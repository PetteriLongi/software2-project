"""
Combat API blueprint.
Handles all combat-related operations and turn processing.
Implements the 5 combat actions from original game:
1. Attack - Physical attack with equipped weapon
2. Defend - Brace for next hit (halves damage)
3. Manifest - Use manifestation power (costs sanity)
4. Inventory - Use item or equip weapon (doesn't consume turn if you just browse)
5. Reload - Reload equipped firearm
"""
from flask import Blueprint, request, session, jsonify

from game_logic.player import Player
from game_logic.enemies import Enemy, create_enemy
from game_logic.combat_engine import CombatState, process_player_action
from game_logic.doomclock_integration import get_doom_clock_from_session, save_doom_clock_to_session

combat_bp = Blueprint('combat', __name__)


@combat_bp.route('/start', methods=['POST'])
def start_combat():
    """
    Initialize a combat encounter.
    
    Request JSON:
        {
            "enemy_types": ["Cultist", "Apostle"]  # Names from enemy_library
        }
    
    Response:
        {
            "player": {...},
            "enemies": [{name, hp, max_hp, ...}, ...],
            "turn": 1,
            "combat_log": ["Combat begins!"],
            "defending": false
        }
    """
    try:
        data = request.get_json() or {}
        enemy_types = data.get('enemy_types', [])
        
        if not enemy_types:
            return jsonify({'error': 'No enemy_types specified'}), 400
        
        # Get player from session
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game. Call /api/game/start first.'}), 400
        
        player = Player.from_dict(player_data)
        
        # Create combat state
        try:
            combat_state = CombatState(player, enemy_types)
        except (KeyError, ValueError) as e:
            return jsonify({'error': f'Failed to create combat: {str(e)}'}), 400
        
        # Save combat state to session (serialize it)
        session['combat'] = {
            'turn_counter': combat_state.turn_counter,
            'enemies': [e.to_dict() for e in combat_state.enemies],
            'defending': combat_state.defending,
            'combat_active': combat_state.combat_active
        }
        session.modified = True
        
        # Get doom clock for response
        doom_clock = get_doom_clock_from_session(session)
        doom_state = doom_clock.to_dict()
        
        return jsonify({
            'player': player.to_dict(),
            'enemies': [e.to_dict() for e in combat_state.enemies],
            'turn': combat_state.turn_counter,
            'combat_log': [f"--- COMBAT: {', '.join(enemy_types)} APPEARS! ---"],
            'defending': combat_state.defending,
            'available_actions': ['attack', 'defend', 'manifest', 'reload'],
            'doom_clock': doom_state
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@combat_bp.route('/action', methods=['POST'])
def process_combat_action():
    """
    Process a combat action (player turn + enemy turns).
    
    Request JSON:
        {
            "action": "attack|defend|manifest|reload",
            "target_index": 0,           # For attack/manifest - which enemy (0-based index of living enemies)
            "item_index": 0               # For manifest - which manifestation (0-based index)
        }
    
    Response:
        {
            "player": {...},
            "enemies": [...],
            "turn": 2,
            "combat_log": ["You attack...", "Enemy attacks..."],
            "defending": false,
            "turn_consumed": true,
            "combat_over": false,
            "victory": false,
            "player_died": false
        }
    """
    try:
        data = request.get_json() or {}
        action = data.get('action')
        
        if not action:
            return jsonify({'error': 'No action specified'}), 400
        
        # Get state from session
        player_data = session.get('player')
        combat_data = session.get('combat')
        
        if not player_data or not combat_data:
            return jsonify({'error': 'No active combat. Call /api/combat/start first.'}), 400
        
        # Reconstruct game objects
        player = Player.from_dict(player_data)
        
        # Reconstruct combat state from session data
        combat_state = CombatState.from_dict(combat_data)
        
        # Process the action
        result = process_player_action(
            combat_state=combat_state,
            player=player,
            action=action,
            target_index=data.get('target_index'),
            item_index=data.get('item_index')
        )
        
        # Tick down doom clock for turn consumed
        doom_messages = []
        if result['turn_consumed']:
            doom_clock = get_doom_clock_from_session(session)
            doom_result = doom_clock.countdown(
                n=1,
                player=player.to_dict(),
                enemies=[e.to_dict() for e in combat_state.enemies],
                log=doom_messages,
                reason="Combat round"
            )
            save_doom_clock_to_session(session, doom_clock)
            
            # Add doom messages to combat log
            if doom_result['messages']:
                result['messages'].extend(doom_result['messages'])
            
            # Check if doom reached zero
            if doom_result['zero_triggered']:
                result['game_over'] = True
                result['messages'].append("\n💀 DOOM REACHES ZERO. THE WORLD ENDS. 💀")
        
        # Save updated state to session
        session['player'] = player.to_dict()
        session['combat'] = {
            'turn_counter': combat_state.turn_counter,
            'enemies': [e.to_dict() for e in combat_state.enemies],
            'defending': combat_state.defending,
            'combat_active': combat_state.combat_active
        }
        session.modified = True
        
        # Get updated doom clock for response
        doom_clock = get_doom_clock_from_session(session)
        doom_state = doom_clock.to_dict()
        
        response = {
            'player': player.to_dict(),
            'enemies': [e.to_dict() for e in combat_state.enemies if e.hp > 0],
            'turn': combat_state.turn_counter,
            'combat_log': result['messages'],
            'defending': combat_state.defending,
            'turn_consumed': result['turn_consumed'],
            'combat_over': result['combat_ended'],
            'victory': result.get('victory', False),
            'player_died': player.hp <= 0,
            'manifestation_used': result.get('manifestation_used'),  # Pass through manifestation name
            'sfx': result.get('sfx'),  # Pass through sound effect for attacks
            'doom_clock': doom_state  # Include doom clock state in response
        }
        
        # Clear combat and advance story if it's over
        if result['combat_ended']:
            session.pop('combat', None)
            
            # If victory, advance the story to the next node
            if result.get('victory', False):
                game_state = session.get('game_state', {})
                current_node = game_state.get('current_node')
                
                # Get the next node from the story
                if current_node:
                    from game_logic.story_engine import process_story_node
                    from game_logic.items import weapon_library, consumable_library
                    
                    story_result = process_story_node(current_node)
                    next_node = story_result.get('next_node')
                    
                    if next_node:
                        # Update to the post-combat node
                        game_state['current_node'] = next_node
                        if next_node not in game_state.get('visited_nodes', []):
                            game_state.setdefault('visited_nodes', []).append(next_node)
                        session['game_state'] = game_state
                        
                        # Process rewards from the next node
                        next_story = process_story_node(next_node)
                        
                        # Check for manifestation unlocks in the text
                        from game_logic.manifestations import manifestation_library
                        import re
                        
                        text = ' '.join(next_story.get('text', []))
                        # Pattern: [MANIFESTATION UNLOCKED: **Name**] or [MANIFESTATION UNLOCKED: Name]
                        matches = re.findall(r'\[MANIFESTATION UNLOCKED:[\s*]+([A-Za-z]+)[\s*\]]+', text)
                        
                        for match in matches:
                            manif_name = match.strip('* ')
                            if manif_name in manifestation_library:
                                manifestation = manifestation_library[manif_name]
                                if not any(m.name == manifestation.name for m in player.manifestations):
                                    player.manifestations.append(manifestation)
                                    response['combat_log'].append(f"\n✨ Manifestation unlocked: {manif_name}")
                        
                        # Check if this node should close a conduit
                        if next_story.get('conduit_closed'):
                            from blueprints.api.travel import process_conduit_closure_if_needed, init_travel_state
                            
                            if process_conduit_closure_if_needed(session):
                                run_state = init_travel_state()
                                response['combat_log'].append(f"\n✨ Conduit sealed! ({run_state.conduits_closed}/5)")
                        
                        rewards = next_story.get('rewards')
                        
                        if rewards:
                            reward_messages = []
                            
                            # Add weapons
                            if 'weapons' in rewards:
                                for weapon_name in rewards['weapons']:
                                    if weapon_name in weapon_library:
                                        weapon = weapon_library[weapon_name]
                                        # Check if player already has this weapon (by name)
                                        existing = next((item for item in player.inventory 
                                                       if hasattr(item, 'name') and item.name == weapon.name), None)
                                        
                                        if not existing:
                                            player.inventory.append(weapon)
                                            reward_messages.append(f"Found: {weapon.name}")
                                        else:
                                            reward_messages.append(f"Already have: {weapon.name}")
                            
                            # Add consumables
                            if 'consumables' in rewards:
                                from game_logic.items import add_item_to_inventory
                                for item_data in rewards['consumables']:
                                    item_name = item_data['name']  # This is the library key
                                    quantity = item_data.get('quantity', 1)
                                    
                                    # Use add_item_to_inventory which properly routes ammo to ammo pool
                                    result = add_item_to_inventory(player, item_name, quantity)
                                    if result['success']:
                                        reward_messages.append(result['message'])
                            
                            # Update player in session
                            session['player'] = player.to_dict()
                            
                            # Add reward messages to response
                            if reward_messages:
                                response['rewards'] = reward_messages
            
            session.modified = True
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@combat_bp.route('/state', methods=['GET'])
def get_combat_state():
    """
    Get current combat state without taking an action.
    
    Response:
        {
            "in_combat": true,
            "player": {...},
            "enemies": [...],
            "turn": 2,
            "defending": false
        }
    """
    try:
        combat_data = session.get('combat')
        player_data = session.get('player')
        
        if not combat_data:
            return jsonify({
                'in_combat': False,
                'message': 'No active combat'
            }), 200
        
        # Get doom clock for response
        doom_clock = get_doom_clock_from_session(session)
        doom_state = doom_clock.to_dict()
        
        return jsonify({
            'in_combat': True,
            'player': player_data,
            'enemies': combat_data['enemies'],
            'turn': combat_data['turn_counter'],
            'defending': combat_data.get('defending', False),
            'doom_clock': doom_state
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
