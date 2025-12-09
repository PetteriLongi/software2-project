"""
Game logic package.
Contains all core game mechanics migrated from the console version.

This logic runs on the Flask backend and maintains authoritative game state.
"""

from .player import Player
from .items import Item, Weapon, Consumable, weapon_library, consumable_library, add_weapon_to_inventory, add_item_to_inventory
from .manifestations import Manifestation, manifestation_library
from .enemies import Enemy, enemy_library, create_enemy
from .combat_engine import CombatState, process_player_action
from .story_engine import (
    load_story_data, 
    get_node, 
    process_story_node, 
    get_starting_nodes,
    validate_story_data,
    get_story_progress
)

__all__ = [
    'Player',
    'Item', 'Weapon', 'Consumable', 'weapon_library', 'consumable_library',
    'add_weapon_to_inventory', 'add_item_to_inventory',
    'Manifestation', 'manifestation_library',
    'Enemy', 'enemy_library', 'create_enemy',
    'CombatState', 'process_player_action',
    'load_story_data', 'get_node', 'process_story_node', 
    'get_starting_nodes', 'validate_story_data', 'get_story_progress'
]
