"""
Main blueprint for serving the frontend application.
Handles root routes and static page serving.
"""
from flask import Blueprint, render_template, send_from_directory, session, redirect, url_for
import json

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the main game page."""
    return render_template('index.html')


@main_bp.route('/menu')
def menu():
    """Serve the main menu template."""
    return render_template('mainMenu.html')


@main_bp.route('/combat')
def combat():
    """
    Serve the combat page with initial combat state.
    If no combat is active, redirects to main game.
    """
    # Check if there's an active combat session
    combat_data = session.get('combat')
    player_data = session.get('player')
    
    if not combat_data or not player_data:
        # No active combat, redirect to main game
        return redirect(url_for('main.index'))
    
    # Reconstruct combat state for initial render
    from game_logic.player import Player
    from game_logic.enemies import Enemy
    
    player = Player.from_dict(player_data)
    enemies = [Enemy.from_dict(e) for e in combat_data.get('enemies', [])]
    
    # Prepare initial combat data for JavaScript
    initial_data = {
        'player': player.to_dict(),
        'enemies': [e.to_dict() for e in enemies if e.hp > 0],
        'turn': combat_data.get('turn_counter', 1),
        'defending': combat_data.get('defending', False),
        'chapter': session.get('game_state', {}).get('current_chapter', 1),
        'doom_clock': session.get('doom_clock', {'ticks': 100, 'start': 100})
    }
    
    # Convert to JSON for embedding in template
    combat_json = json.dumps(initial_data)
    
    return render_template('combat.html', combat_data=combat_json)


@main_bp.route('/combat/test')
def combat_test():
    """
    Test combat page with sample data.
    Useful for frontend development and testing.
    """
    from game_logic.player import Player
    from game_logic.combat_engine import CombatState
    
    # Create a test player
    test_player = Player("Test Hero")
    test_player.hp = 80
    test_player.max_hp = 100
    test_player.sanity = 12
    test_player.max_sanity = 15
    test_player.xp = 150
    
    # Add test weapon
    from game_logic.items import weapon_library
    if 'Basic dagger' in weapon_library:
        test_player.weapon = weapon_library['Basic dagger']
        test_player.inventory.append(weapon_library['Basic dagger'])
    
    # Add test manifestation
    from game_logic.manifestations import manifestation_library
    if 'Fear' in manifestation_library:
        test_player.manifestations.append(manifestation_library['Fear'])
    
    # Create test combat with enemies
    try:
        combat_state = CombatState(test_player, ['Apostle', 'Cultist'])
        
        # Prepare initial combat data
        initial_data = {
            'player': test_player.to_dict(),
            'enemies': [e.to_dict() for e in combat_state.enemies],
            'turn': 1,
            'defending': False,
            'chapter': 1,
            'doom_clock': {'ticks': 100, 'start': 100}
        }
        
        # Save to session for testing API calls
        session['player'] = test_player.to_dict()
        session['combat'] = {
            'turn_counter': 1,
            'enemies': [e.to_dict() for e in combat_state.enemies],
            'defending': False,
            'combat_active': True
        }
        session['game_state'] = {'current_chapter': 1}
        session['doom_clock'] = {'ticks': 100, 'start': 100}
        
        combat_json = json.dumps(initial_data)
        return render_template('combat.html', combat_data=combat_json)
        
    except Exception as e:
        return f"Error creating test combat: {str(e)}", 500


@main_bp.route('/story')
def story():
    """
    Serve the story page with typewriter effect.
    """
    # Check if there's an active game session
    game_state = session.get('game_state')
    player_data = session.get('player')
    
    if not game_state or not player_data:
        # No active game, redirect to main page
        return redirect(url_for('main.index'))
    
    return render_template('story.html')


@main_bp.route('/travel')
def travel():
    """
    Serve the travel/airport board page.
    """
    # Check if there's an active game session
    player_data = session.get('player')
    
    if not player_data:
        # No active game, redirect to main page
        return redirect(url_for('main.index'))
    
    return render_template('travel.html')


@main_bp.route('/inventory')
def inventory():
    """
    Serve the inventory management page.
    """
    from flask import request
    
    # Check if there's an active game session
    player_data = session.get('player')
    
    if not player_data:
        # No active game, redirect to main page
        return redirect(url_for('main.index'))
    
    # Get referrer to know where to return to
    referrer = request.args.get('from', 'story')
    
    return render_template('inventory.html', referrer=referrer)


@main_bp.route('/help_modal')
def help_modal():
    """Serve the shared help modal fragment for dynamic loading."""
    return render_template('help_modal.html')


@main_bp.route('/story/test')
def story_test():
    """
    Test story page with sample data.
    Useful for frontend development and testing.
    """
    from game_logic.player import Player
    
    # Create test player and session
    test_player = Player("Test Hero")
    session['player'] = test_player.to_dict()
    session['game_state'] = {
        'current_chapter': 1,
        'current_node': '1_intro',
        'visited_nodes': []
    }
    session['doom_clock'] = {
        'ticks': 100,
        'start': 100,
        'warnings': []
    }
    
    return render_template('story.html')


@main_bp.route('/travel/test')
def travel_test():
    """
    Test travel/animation page with sample data.
    Useful for frontend development and testing.
    """
    from game_logic.player import Player
    from game_logic.travel_service import start_new_run
    
    # Create test player and session
    test_player = Player("Test Hero")
    session['player'] = test_player.to_dict()
    
    # Initialize a new run for testing
    run_state = start_new_run()
    session['run_state'] = run_state.to_dict()
    
    return render_template('travel.html')


@main_bp.route('/audio/test')
def audio_test():
    """
    Audio system test page.
    Interactive interface for testing all audio features.
    """
    return render_template('audio_test.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return {'status': 'ok', 'message': 'Server is running'}, 200

