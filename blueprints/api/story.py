"""
Story API blueprint.
Handles story progression, narrative choices, and chapter management.
Uses original story from story_data.json without modifications.
"""
from flask import Blueprint, request, session, jsonify
from game_logic.story_engine import process_story_node, get_node, get_starting_nodes

story_bp = Blueprint('story', __name__)


@story_bp.route('/current', methods=['GET'])
def get_current_story():
    """
    Get current story node.
    
    Returns:
        JSON: Current story node data including text and choices
    """
    try:
        game_state = session.get('game_state')
        if not game_state:
            return jsonify({
                'success': False,
                'error': 'No active game'
            }), 400
        
        current_node = game_state.get('current_node', '1_intro')
        story_result = process_story_node(current_node)
        
        if not story_result['success']:
            return jsonify(story_result), 404
        
        return jsonify({
            'success': True,
            'node_key': story_result['node_key'],
            'text': story_result['text'],
            'choices': story_result['choices'],
            'combat': story_result['combat'],
            'music': story_result['music'],
            'wait': story_result['wait'],
            'is_ending': story_result['is_ending'],
            'quit_game': story_result['quit_game'],
            'travel': story_result.get('travel', False)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@story_bp.route('/choice', methods=['POST'])
def make_story_choice():
    """
    Make a story choice and progress to the next node.
    
    Request JSON:
        {
            "choice_index": 0  # Index of the choice selected (0-indexed)
        }
    
    Response:
        {
            "success": true,
            "node_key": "1_where_shadows_bled",
            "text": [...],
            "choices": [...] or null,
            "combat": {...} or null,
            "music": {...} or null,
            "doom_tick": int or null,
            "doom_reason": str or null,
            "wait": bool,
            "is_ending": bool,
            "quit_game": bool,
            "game_state": {...},
            "doom_clock": {...}
        }
    """
    try:
        data = request.get_json() or {}
        choice_index = data.get('choice_index')
        
        # Get current game state
        game_state = session.get('game_state')
        if not game_state:
            return jsonify({
                'success': False,
                'error': 'No active game'
            }), 400
        
        current_node = game_state.get('current_node', '1_intro')
        
        # Process the story choice
        story_result = process_story_node(current_node, choice_index=choice_index)
        
        if not story_result['success']:
            return jsonify(story_result), 400
        
        # Update to next node if available
        next_node = story_result.get('next_node')
        if next_node:
            # Process the next node to get its content
            next_result = process_story_node(next_node)
            
            if next_result['success']:
                # Update game state
                game_state['current_node'] = next_node
                if next_node not in game_state.get('visited_nodes', []):
                    game_state['visited_nodes'].append(next_node)
                
                # Check for manifestation unlocks in the text
                from game_logic.manifestations import manifestation_library
                from game_logic.player import Player
                import re
                
                player_data = session.get('player')
                if player_data:
                    player = Player.from_dict(player_data)
                    
                    # Parse text for manifestation unlocks
                    text = ' '.join(next_result.get('text', []))
                    # Pattern: [MANIFESTATION UNLOCKED: **Name**] or [MANIFESTATION UNLOCKED: Name]
                    matches = re.findall(r'\[MANIFESTATION UNLOCKED:[\s*]+([A-Za-z]+)[\s*\]]+', text)
                    
                    for match in matches:
                        manif_name = match.strip('* ')
                        if manif_name in manifestation_library:
                            manifestation = manifestation_library[manif_name]
                            if not any(m.name == manifestation.name for m in player.manifestations):
                                player.manifestations.append(manifestation)
                    
                    session['player'] = player.to_dict()
                
                # Update doom clock if specified
                doom_clock = session.get('doom_clock', {'ticks': 100, 'start': 100, 'warnings': []})
                if next_result.get('doom_tick'):
                    doom_clock['ticks'] = max(0, doom_clock['ticks'] - next_result['doom_tick'])
                    if next_result.get('doom_reason'):
                        doom_clock['warnings'].append(next_result['doom_reason'])
                
                # Check if this node should actually close the conduit (defiance path)
                if next_result.get('conduit_closed'):
                    from blueprints.api.travel import init_travel_state, close_conduit_service
                    
                    run_state = init_travel_state()
                    pending_airport_index = session.get('pending_conduit_closure')

                    # Fallback: if pending index missing, try current location conduit
                    if pending_airport_index is None:
                        for idx, airport in enumerate(run_state.airports):
                            if airport.conduit and airport.iata == run_state.current_iata and not airport.conduit_closed:
                                pending_airport_index = idx
                                break
                    
                    if pending_airport_index is not None:
                        # Now actually close the conduit
                        result = close_conduit_service(run_state, int(pending_airport_index))
                        
                        if result['success']:
                            session['run_state'] = run_state.to_dict()
                            game_state['conduits_closed'] = run_state.conduits_closed
                            
                            # Clear pending closure
                            session.pop('pending_conduit_closure', None)
                
                session['game_state'] = game_state
                session['doom_clock'] = doom_clock
                session.modified = True
                
                # Return the next node's content
                return jsonify({
                    'success': True,
                    'node_key': next_result['node_key'],
                    'text': next_result['text'],
                    'choices': next_result['choices'],
                    'combat': next_result['combat'],
                    'music': next_result['music'],
                    'doom_tick': next_result.get('doom_tick'),
                    'doom_reason': next_result.get('doom_reason'),
                    'wait': next_result['wait'],
                    'is_ending': next_result['is_ending'],
                    'quit_game': next_result['quit_game'],
                    'travel': next_result.get('travel', False),
                    'game_state': game_state,
                    'doom_clock': doom_clock
                }), 200
            else:
                return jsonify(next_result), 404
        else:
            # No next node - might be waiting for user input or ending
            return jsonify({
                'success': True,
                'message': 'Story paused - awaiting next action',
                'node_key': current_node,
                'game_state': game_state
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@story_bp.route('/continue', methods=['POST'])
def continue_story():
    """
    Continue story from current node (for nodes with no choices).
    Useful for "press any key to continue" type nodes.
    
    Response:
        Same as /choice endpoint
    """
    try:
        game_state = session.get('game_state')
        if not game_state:
            return jsonify({
                'success': False,
                'error': 'No active game'
            }), 400
        
        current_node = game_state.get('current_node', '1_intro')
        
        # Process current node to get next
        story_result = process_story_node(current_node)
        
        if not story_result['success']:
            return jsonify(story_result), 400
        
        next_node = story_result.get('next_node')
        if not next_node:
            return jsonify({
                'success': False,
                'error': 'No next node available. This node requires a choice.'
            }), 400
        
        # Process the next node
        next_result = process_story_node(next_node)
        
        if next_result['success']:
            # Update game state
            game_state['current_node'] = next_node
            if next_node not in game_state.get('visited_nodes', []):
                game_state['visited_nodes'].append(next_node)
            
            # Check for manifestation unlocks in the text
            from game_logic.manifestations import manifestation_library
            from game_logic.player import Player
            import re
            
            player_data = session.get('player')
            if player_data:
                player = Player.from_dict(player_data)
                
                # Parse text for manifestation unlocks
                text = ' '.join(next_result.get('text', []))
                # Pattern: [MANIFESTATION UNLOCKED: **Name**] or [MANIFESTATION UNLOCKED: Name]
                matches = re.findall(r'\[MANIFESTATION UNLOCKED:[\s*]+([A-Za-z]+)[\s*\]]+', text)
                
                for match in matches:
                    manif_name = match.strip('* ')
                    if manif_name in manifestation_library:
                        manifestation = manifestation_library[manif_name]
                        if not any(m.name == manifestation.name for m in player.manifestations):
                            player.manifestations.append(manifestation)
                
                session['player'] = player.to_dict()
            
            # Update doom clock if specified
            doom_clock = session.get('doom_clock', {'ticks': 100, 'start': 100, 'warnings': []})
            if next_result.get('doom_tick'):
                doom_clock['ticks'] = max(0, doom_clock['ticks'] - next_result['doom_tick'])
                if next_result.get('doom_reason'):
                    doom_clock['warnings'].append(next_result['doom_reason'])

            # Close conduit if this node marks it as sealed (e.g., defiance path aftermath)
            if next_result.get('conduit_closed'):
                from blueprints.api.travel import init_travel_state, close_conduit_service

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
                        game_state['conduits_closed'] = run_state.conduits_closed

                        # Clear pending closure now that it's applied
                        session.pop('pending_conduit_closure', None)
            
            session['game_state'] = game_state
            session['doom_clock'] = doom_clock
            session.modified = True
            
            return jsonify({
                'success': True,
                'node_key': next_result['node_key'],
                'text': next_result['text'],
                'choices': next_result['choices'],
                'combat': next_result['combat'],
                'music': next_result['music'],
                'doom_tick': next_result.get('doom_tick'),
                'doom_reason': next_result.get('doom_reason'),
                'wait': next_result['wait'],
                'is_ending': next_result['is_ending'],
                'quit_game': next_result['quit_game'],
                'travel': next_result.get('travel', False),
                'game_state': game_state,
                'doom_clock': doom_clock
            }), 200
        else:
            return jsonify(next_result), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@story_bp.route('/node/<node_key>', methods=['GET'])
def get_story_node(node_key):
    """
    Get a specific story node by key.
    Useful for debugging or jumping to specific story points.
    
    Args:
        node_key: Story node key (e.g., "1_intro", "2_conduit")
    
    Response:
        Story node data
    """
    try:
        story_result = process_story_node(node_key)
        
        if not story_result['success']:
            return jsonify(story_result), 404
        
        return jsonify({
            'success': True,
            'node_key': story_result['node_key'],
            'text': story_result['text'],
            'choices': story_result['choices'],
            'combat': story_result['combat'],
            'music': story_result['music'],
            'doom_tick': story_result.get('doom_tick'),
            'doom_reason': story_result.get('doom_reason'),
            'wait': story_result['wait'],
            'is_ending': story_result['is_ending'],
            'quit_game': story_result['quit_game']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@story_bp.route('/chapters', methods=['GET'])
def list_chapters():
    """
    Get list of available chapter starting nodes.
    
    Response:
        {
            "success": true,
            "chapters": [{"key": "1_intro", "title": "Chapter I: Crimson Veil"}, ...]
        }
    """
    try:
        chapters = get_starting_nodes()
        
        return jsonify({
            'success': True,
            'chapters': chapters
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
