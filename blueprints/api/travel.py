"""
travel.py - Travel and location management API endpoints

Handles airport destinations, travel actions, and conduit management.
"""
import traceback
from flask import Blueprint, jsonify, request, session
from game_logic.travel_service import (
    start_new_run, travel_to_index, rest, close_conduit as close_conduit_service,
    get_travel_options
)
from game_logic.database import RunState
from game_logic.player import Player
from game_logic.doomclock_integration import get_doom_clock_from_session, save_doom_clock_to_session

travel_bp = Blueprint('travel', __name__)


def init_travel_state():
    """Initialize travel state if not present in session."""
    if 'run_state' not in session:
        run_state = start_new_run()
        
        # Get conduits_closed from game_state if available
        game_state = session.get('game_state', {})
        if 'conduits_closed' in game_state:
            run_state.conduits_closed = game_state['conduits_closed']
        
        session['run_state'] = run_state.to_dict()
        return run_state
    return RunState.from_dict(session['run_state'])


def process_conduit_closure_if_needed(session):
    """
    Handle conduit closure logic if pending.
    
    This is called from story/combat endpoints when a node has conduit_closed=True.
    Centralizes the logic to avoid duplication across multiple endpoints.
    
    Args:
        session: Flask session object
        
    Returns:
        bool: True if conduit was closed successfully, False otherwise
    """
    run_state = init_travel_state()
    pending_airport_index = session.get('pending_conduit_closure')
    
    # Fallback: if pending index missing, try current location conduit
    if pending_airport_index is None:
        for idx, airport in enumerate(run_state.airports):
            if airport.conduit and airport.iata == run_state.current_iata and not airport.conduit_closed:
                pending_airport_index = idx
                break
    
    if pending_airport_index is not None:
        result = close_conduit_service(run_state, int(pending_airport_index))
        
        if result['success']:
            session['run_state'] = run_state.to_dict()
            game_state = session.get('game_state', {})
            game_state['conduits_closed'] = run_state.conduits_closed
            session['game_state'] = game_state
            
            # Clear pending closure
            session.pop('pending_conduit_closure', None)
            return True
    
    return False


@travel_bp.route('/destinations', methods=['GET'])
def get_destinations():
    """
    Get available travel destinations from current location.
    
    Returns list of airports with distances and costs.
    """
    try:
        run_state = init_travel_state()
        options = get_travel_options(run_state)
        
        # Get doom clock for response
        doom_clock = get_doom_clock_from_session(session)
        
        return jsonify({
            'success': True,
            'current_location': {
                'name': run_state.current_name,
                'iata': run_state.current_iata,
                'country': run_state.current_country,
                'lat': run_state.current_lat,
                'lon': run_state.current_lon
            },
            'markka': run_state.markka,
            'destinations': options,
            'conduits_found': run_state.conduits_found,
            'conduits_closed': run_state.conduits_closed,
            'doom_clock': doom_clock.to_dict()
        }), 200
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in get_destinations: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500


@travel_bp.route('/to', methods=['POST'])
def travel_to_destination():
    """
    Travel to a chosen destination.
    
    Expects JSON: {'airport_index': int}
    
    Updates player location and deducts travel cost.
    """
    try:
        data = request.get_json()
        airport_index = data.get('airport_index')
        
        if airport_index is None:
            return jsonify({
                'success': False,
                'error': 'airport_index is required'
            }), 400
        
        # Get current state
        run_state = init_travel_state()
        
        # Get player for doom clock integration
        player_data = session.get('player')
        if not player_data:
            return jsonify({
                'success': False,
                'error': 'No active player session'
            }), 400
        
        player = Player.from_dict(player_data)
        
        # Perform travel
        result = travel_to_index(run_state, int(airport_index))
        
        # Apply doom ticks from travel if successful
        if result['success']:
            doom_clock = get_doom_clock_from_session(session)
            doom_ticks = result.get('doom_ticks', 0)
            
            if doom_ticks > 0:
                doom_result = doom_clock.countdown(n=doom_ticks, reason=f"Traveled {result['distance']:.0f}km")
                result['game_over'] = doom_result['zero_triggered']
                result['doom_clock'] = doom_clock.to_dict()
            else:
                result['doom_clock'] = doom_clock.to_dict()
            
            save_doom_clock_to_session(session, doom_clock)
        
        # Save updated state
        session['run_state'] = run_state.to_dict()
        session['player'] = player.to_dict()
        
        # Add current location to result
        if result['success']:
            result['current_location'] = {
                'name': run_state.current_name,
                'iata': run_state.current_iata,
                'country': run_state.current_country
            }
            result['markka'] = run_state.markka
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@travel_bp.route('/rest', methods=['POST'])
def rest():
    """
    Rest at current location to restore HP/sanity.
    
    Costs doom ticks but restores player stats.
    """
    try:
        # Get current state
        run_state = init_travel_state()
        
        player_data = session.get('player')
        if not player_data:
            return jsonify({
                'success': False,
                'error': 'No active player session'
            }), 400
        
        player = Player.from_dict(player_data)
        
        # Perform rest
        from game_logic.travel_service import rest as rest_service
        result = rest_service(run_state, player)
        
        # Apply doom tick from rest
        if result['success']:
            doom_clock = get_doom_clock_from_session(session)
            doom_result = doom_clock.countdown(n=1, reason="Rested at airport")
            result['game_over'] = doom_result['zero_triggered']
            result['doom_clock'] = doom_clock.to_dict()
            save_doom_clock_to_session(session, doom_clock)
        
        # Save updated state
        session['run_state'] = run_state.to_dict()
        session['player'] = player.to_dict()
        
        # Add updated stats to result
        result['hp'] = player.hp
        result['sanity'] = player.sanity
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@travel_bp.route('/conduit/close', methods=['POST'])
def close_conduit():
    """
    Close a conduit at the current location.
    
    Expects JSON: {'airport_index': int}
    
    Awards markka, updates progression, and triggers story node.
    """
    try:
        from game_logic.story_engine import process_story_node
        
        data = request.get_json()
        airport_index = data.get('airport_index')
        
        if airport_index is None:
            return jsonify({
                'success': False,
                'error': 'airport_index is required'
            }), 400
        
        # Get current state
        run_state = init_travel_state()
        
        # Store pending conduit closure - do NOT mark closed yet
        # The story will mark it closed when player chooses defiance
        session['pending_conduit_closure'] = int(airport_index)
        
        # Determine which chapter to trigger based on CURRENT conduits closed
        # (before increment - we want the right chapter for current progress)
        conduits_closed = run_state.conduits_closed
        
        # Map conduits closed to story chapters
        # After closing N conduits, show the (N+1)th conduit encounter
        chapter_map = {
            1: '2_conduit',  # After closing 1st conduit, encounter 2nd
            2: '3_conduit',  # After closing 2nd conduit, encounter 3rd
            3: '4_conduit',  # After closing 3rd conduit, encounter 4th
            4: '5_conduit'   # After closing 4th conduit, encounter 5th (final)
        }
        
        story_node = chapter_map.get(conduits_closed, '2_conduit')
        
        # Prepare result without actually closing the conduit yet
        result = {
            'success': True,
            'markka': run_state.markka,
            'conduits_closed': run_state.conduits_closed
        }
        
        # Update game state
        game_state = session.get('game_state', {})
        game_state['conduits_closed'] = run_state.conduits_closed
        
        game_state['current_node'] = story_node
        game_state['visited_nodes'] = game_state.get('visited_nodes', [])
        if story_node not in game_state['visited_nodes']:
            game_state['visited_nodes'].append(story_node)
        session['game_state'] = game_state
        
        # Trigger the conduit story node
        story_result = process_story_node(story_node)
        if story_result['success']:
            result['story'] = {
                'node_key': story_result['node_key'],
                'text': story_result['text'],
                'choices': story_result['choices'],
                'combat': story_result['combat'],
                'music': story_result['music'],
                'wait': story_result['wait']
            }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

