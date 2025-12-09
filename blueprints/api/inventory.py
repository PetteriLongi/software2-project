"""
Inventory API blueprint.
Handles inventory operations from the original game:
1. View inventory
2. Use consumable items (potions)
3. Equip weapons
4. Unequip weapons
Note: Does NOT handle in-combat inventory (handled by combat blueprint)
"""
from flask import Blueprint, request, session, jsonify
from game_logic.player import Player
from game_logic.items import Weapon, Consumable
from game_logic.database import RunState

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """
    Get player's current inventory.
    
    Response:
        {
            "inventory": [
                {"name": "Health Potion", "type": "consumable", "quantity": 2, ...},
                {"name": "Dagger", "type": "weapon", ...}
            ],
            "equipped_weapon": {"name": "Dagger", ...} or null,
            "weapons": [...],
            "consumables": [...]
        }
    """
    try:
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game'}), 400
        
        player = Player.from_dict(player_data)
        
        # Get markka from run_state (travel system tracks currency)
        run_state_data = session.get('run_state')
        markka = 0
        if run_state_data:
            run_state = RunState.from_dict(run_state_data)
            markka = run_state.markka
        
        # Separate weapons and consumables (matching original combat_actions.py)
        weapons = []
        consumables = []
        
        for item in player.inventory:
            if isinstance(item, Weapon):
                weapons.append(item.to_dict())
            elif isinstance(item, Consumable):
                # Skip ammo-type consumables (they go to player.ammo dict)
                if not (getattr(item, 'type', None) and str(getattr(item, 'type')).lower() == 'ammo'):
                    consumables.append(item.to_dict())
        
        return jsonify({
            'success': True,
            'inventory': [item.to_dict() for item in player.inventory],
            'equipped_weapon': player.weapon.to_dict() if player.weapon else None,
            'weapons': weapons,
            'consumables': consumables,
            'inventory_size': len(player.inventory),
            'ammo': player.ammo,
            'player_stats': {
                'hp': player.hp,
                'max_hp': player.max_hp,
                'sanity': player.sanity,
                'max_sanity': player.max_sanity,
                'level': player.level,
                'markka': markka
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/use', methods=['POST'])
def use_item():
    """
    Use a consumable item from inventory.
    
    Request JSON:
        {
            "item_index": 0  # Index in player.inventory list
        }
    
    Response:
        {
            "success": true,
            "message": "You used Health Potion. Restored 20 HP!",
            "player": {...},
            "item_consumed": false,  # true if item was depleted and removed
            "quantity_remaining": 1
        }
    """
    try:
        data = request.get_json() or {}
        item_index = data.get('item_index')
        
        if item_index is None:
            return jsonify({'error': 'item_index required'}), 400
        
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game'}), 400
        
        player = Player.from_dict(player_data)
        
        # Validate index
        if item_index < 0 or item_index >= len(player.inventory):
            return jsonify({'error': 'Invalid item index'}), 400
        
        item = player.inventory[item_index]
        
        # Check if item is consumable
        if not isinstance(item, Consumable):
            return jsonify({
                'error': f'{item.name} is not a consumable item. Use /equip for weapons.'
            }), 400
        
        # Use the item (calls original use() method from items.py)
        result = item.use(player)
        
        # Remove if depleted (matching original: if selected.quantity <= 0)
        item_consumed = False
        if item.quantity <= 0:
            player.inventory.remove(item)
            item_consumed = True
        
        # Save updated player
        session['player'] = player.to_dict()
        session.modified = True
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'player': player.to_dict(),
            'item_consumed': item_consumed,
            'quantity_remaining': result.get('quantity_remaining', 0),
            'sfx': result.get('sfx')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/equip', methods=['POST'])
def equip_weapon():
    """
    Equip a weapon from inventory.
    
    Request JSON:
        {
            "item_index": 0  # Index in player.inventory list
        }
    
    Response:
        {
            "success": true,
            "message": "You equipped Basic dagger",
            "player": {...},
            "equipped_weapon": {...}
        }
    """
    try:
        data = request.get_json() or {}
        item_index = data.get('item_index')
        
        if item_index is None:
            return jsonify({'error': 'item_index required'}), 400
        
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game'}), 400
        
        player = Player.from_dict(player_data)
        
        # Validate index
        if item_index < 0 or item_index >= len(player.inventory):
            return jsonify({'error': 'Invalid item index'}), 400
        
        item = player.inventory[item_index]
        
        # Check if item is weapon
        if not isinstance(item, Weapon):
            return jsonify({
                'error': f'{item.name} is not a weapon.'
            }), 400
        
        # Equip weapon (matching original: player.weapon = selected)
        player.weapon = item
        
        # Save updated player
        session['player'] = player.to_dict()
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'You equipped {item.name}',
            'player': player.to_dict(),
            'equipped_weapon': item.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/unequip', methods=['POST'])
def unequip_weapon():
    """
    Unequip currently equipped weapon.
    
    Response:
        {
            "success": true,
            "message": "You unequip your weapon.",
            "player": {...}
        }
    """
    try:
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game'}), 400
        
        player = Player.from_dict(player_data)
        
        # Check if weapon is equipped (matching original)
        if player.weapon is None:
            return jsonify({
                'success': False,
                'message': 'You have no weapon equipped!'
            }), 200
        
        # Unequip weapon (matching original: player.weapon = None)
        player.weapon = None
        
        # Save updated player
        session['player'] = player.to_dict()
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'You unequip your weapon.',
            'player': player.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/reload', methods=['POST'])
def reload_weapon():
    """
    Reload currently equipped weapon (if it's a firearm).
    
    Response:
        {
            "success": true,
            "message": "You reload your weapon.",
            "player": {...},
            "ammo_used": 6,
            "ammo_remaining": 24
        }
    """
    try:
        player_data = session.get('player')
        if not player_data:
            return jsonify({'error': 'No active game'}), 400
        
        player = Player.from_dict(player_data)
        
        # Check if weapon is equipped
        if player.weapon is None:
            return jsonify({
                'success': False,
                'message': 'You have no weapon equipped!'
            }), 200
        
        # Check if weapon is a gun
        if not hasattr(player.weapon, 'weapon_type') or player.weapon.weapon_type != 'gun':
            return jsonify({
                'success': False,
                'message': f'{player.weapon.name} cannot be reloaded!'
            }), 200
        
        # Check if weapon needs reloading
        if player.weapon.current_ammo >= player.weapon.ammo_capacity:
            return jsonify({
                'success': False,
                'message': f'{player.weapon.name} is already fully loaded!'
            }), 200
        
        # Get ammo type
        ammo_type = getattr(player.weapon, 'ammo_type', 'bullets')
        
        # Check if player has ammo
        if ammo_type not in player.ammo or player.ammo[ammo_type] <= 0:
            return jsonify({
                'success': False,
                'message': f'You have no {ammo_type} to reload with!'
            }), 200
        
        # Calculate ammo needed
        ammo_needed = player.weapon.ammo_capacity - player.weapon.current_ammo
        ammo_available = player.ammo[ammo_type]
        ammo_to_use = min(ammo_needed, ammo_available)
        
        # Reload weapon
        player.weapon.current_ammo += ammo_to_use
        player.ammo[ammo_type] -= ammo_to_use
        
        # Save updated player
        session['player'] = player.to_dict()
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'You reload your {player.weapon.name}. Loaded {ammo_to_use} {ammo_type}.',
            'player': player.to_dict(),
            'ammo_used': ammo_to_use,
            'ammo_remaining': player.ammo[ammo_type]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
