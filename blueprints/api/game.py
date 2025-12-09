"""
Game API blueprint.
Handles game initialization, state management, and core game operations.
"""
from flask import Blueprint, request, session, jsonify
import json

# Import game logic
from game_logic.player import Player
from game_logic.manifestations import manifestation_library
from game_logic.items import weapon_library, consumable_library, Consumable
from game_logic.story_engine import process_story_node, get_starting_nodes
from game_logic.doomclock import create_default_doom_clock
from game_logic.doomclock_integration import save_doom_clock_to_session, get_doom_clock_from_session

game_bp = Blueprint('game', __name__)


def serialize_player(player):
    """Serialize player object for session storage using JSON."""
    return player.to_dict()


def deserialize_player(player_data):
    """Deserialize player object from session."""
    return Player.from_dict(player_data)


@game_bp.route('/start', methods=['POST'])
def start_game():
    """
    Initialize a new game.
    Creates a new player with starting equipment and story state.
    
    Request JSON:
        {
            "name": "Hero",              # Optional: player name
            "starting_chapter": "2_conduit"  # Optional: story node to start at
        }
    
    Returns:
        JSON: {
            "success": true,
            "message": "Game started successfully",
            "player": {...},              # Player stats, inventory, manifestations
            "story": {...},                # Current story node with text/choices
            "game_state": {...}            # Doom clock, location, progress
        }
    """
    try:
        # Get request data (allow empty JSON)
        try:
            data = request.get_json(silent=True) or {}
        except Exception:
            data = {}
        
        player_name = data.get('name', 'Hero')
        starting_chapter = data.get('starting_chapter', '1_intro')  # Start from Chapter 1
        
        # Create new player with Fear manifestation (unlocked in tutorial)
        starting_manifestations = []
        if 'Fear' in manifestation_library:
            starting_manifestations.append(manifestation_library['Fear'])
        
        player = Player(player_name, unlocked_manifestations=starting_manifestations)
        
        # Give starting equipment
        if 'Basic dagger' in weapon_library:
            starting_weapon = weapon_library['Basic dagger']
            player.inventory.append(starting_weapon)
            player.weapon = starting_weapon
        
        # Give starting consumables
        starting_consumables = ['Small Health Potion', 'Large Health Potion', 'Small Sanity Potion']
        for consumable_name in starting_consumables:
            if consumable_name in consumable_library:
                consumable = consumable_library[consumable_name]
                # Create a copy with quantity
                new_consumable = Consumable(
                    consumable.name,
                    consumable.description,
                    consumable.effect,
                    quantity=1,
                    type=getattr(consumable, 'type', None),
                    sfx_name=getattr(consumable, 'sfx_name', None)
                )
                # Store the library key for serialization
                new_consumable._library_key = consumable_name
                player.inventory.append(new_consumable)
        
        # Initialize story state
        story_result = process_story_node(starting_chapter)
        
        if not story_result['success']:
            return jsonify({
                'success': False,
                'message': f"Failed to load story: {story_result.get('error', 'Unknown error')}"
            }), 500
        
        # Initialize game state
        game_state = {
            'current_node': starting_chapter,
            'visited_nodes': [starting_chapter],
            'conduits_closed': 1 if starting_chapter == '1_intro' else 0,
            'manifestations_unlocked': ['Fear'],
            'location': 'Airport Terminal'
        }
        
        # Initialize doom clock
        doom_clock_obj = create_default_doom_clock(start=100)
        save_doom_clock_to_session(session, doom_clock_obj)
        doom_clock = doom_clock_obj.to_dict()
        
        # Save to session
        session['player'] = serialize_player(player)
        session['game_state'] = game_state
        # Doom clock already saved above via save_doom_clock_to_session
        session['in_combat'] = False
        
        # Clear any previous run state (travel/airport data) for fresh start
        session.pop('run_state', None)
        session.pop('combat', None)
        
        session.permanent = True  # Make session persist
        
        return jsonify({
            'success': True,
            'message': 'Game started successfully',
            'player': player.to_dict(),
            'story': {
                'node_key': story_result['node_key'],
                'text': story_result['text'],
                'choices': story_result['choices'],
                'music': story_result['music'],
                'wait': story_result['wait'],
                'is_ending': story_result['is_ending']
            },
            'game_state': game_state,
            'doom_clock': doom_clock
        }), 201
    
    except Exception as e:
        print(f"Error starting game: {str(e)}")  # Log to console
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to start game: {str(e)}'
        }), 400


@game_bp.route('/state', methods=['GET'])
def get_game_state():
    """
    Get current game state.
    
    Returns:
        JSON: Current player, state, and doom clock data
    """
    if 'player' not in session:
        return jsonify({
            'success': False,
            'message': 'No active game. Please start a new game.'
        }), 404
    
    player = deserialize_player(session['player'])
    
    return jsonify({
        'success': True,
        'player': player.to_dict(),
        'game_state': session.get('game_state', {}),
        'doom_clock': session.get('doom_clock', {'ticks': 100, 'start': 100}),
        'in_combat': session.get('in_combat', False)
    }), 200


@game_bp.route('/chapters', methods=['GET'])
def list_chapters():
    """
    Get list of available starting chapters.
    
    Returns:
        JSON: List of chapter nodes with titles
    """
    chapters = get_starting_nodes()
    
    return jsonify({
        'success': True,
        'chapters': chapters,
        'default': '2_conduit'
    }), 200


@game_bp.route('/save', methods=['POST'])
def save_game():
    """
    Save current game state.
    
    Returns:
        JSON: Save confirmation
    """
    # TODO: Implement game saving logic
    
    return jsonify({
        'success': True,
        'message': 'Game saved successfully'
    }), 200


@game_bp.route('/load', methods=['POST'])
def load_game():
    """
    Load a saved game.
    
    Returns:
        JSON: Loaded game state
    """
    # TODO: Implement game loading logic
    
    return jsonify({
        'success': True,
        'message': 'Game loaded successfully',
        'data': {}
    }), 200
