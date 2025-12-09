"""
player.py - Defines the Player character and leveling logic.

Migrated for web: Removed console UI dependencies, returns data instead of printing.
This runs on the Flask backend and maintains authoritative player state.
"""


class Player:
    """
    Represents the player character with stats, inventory, and progression.
    """
    
    def __init__(self, name, unlocked_manifestations=None):
        """Create a new player with default starting stats.

        Args:
            name (str): Visible name of the player character.
            unlocked_manifestations (list): Optional list of starting Manifestation instances.
        """
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        self.max_hp = 100
        self.hp = 100
        self.max_sanity = 15
        self.sanity = 15
        self.base_attack = (4, 8)            # Fallback damage if no weapon is equipped
        self.weapon = None                   # Equipped Weapon (or None)
        self.inventory = []                  # List of Item/Weapon/Consumable instances
        self.ammo = {}                       # Ammo pool keyed by ammo type
        self.markka = 0                      # Current currency amount
        self.manifestations = unlocked_manifestations if unlocked_manifestations else []

    def unlock_manifestation(self, manifestation):
        """
        Add a new manifestation to the player's available list.
        
        Args:
            manifestation: Manifestation instance to unlock
            
        Returns:
            bool: True if unlocked, False if already known
        """
        # Check if already unlocked
        if any(m.name == manifestation.name for m in self.manifestations):
            return False
        
        self.manifestations.append(manifestation)
        return True

    def attack_range(self):
        """Return the active attack range tuple depending on the weapon.

        If a weapon is equipped, use its damage range. Otherwise use base.
        """
        if self.weapon:
            return self.weapon.attack_range
        return self.base_attack

    def gain_exp(self, amount):
        """
        Add EXP and trigger level-ups as needed.
        
        Returns:
            dict: Contains messages and level-up information
        """
        messages = []
        self.exp += amount
        messages.append(f"You gain {amount} EXP!")
        
        level_ups = []
        while self.exp >= self.exp_to_next:
            level_up_data = self.level_up()
            level_ups.append(level_up_data)
            
        return {
            'exp_gained': amount,
            'current_exp': self.exp,
            'exp_to_next': self.exp_to_next,
            'messages': messages,
            'level_ups': level_ups
        }

    def level_up(self):
        """
        Increase player level and improve core stats.
        
        Returns:
            dict: Level up information for display
        """
        old_level = self.level
        old_max_hp = self.max_hp
        old_max_sanity = self.max_sanity
        old_attack = self.base_attack
        
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)

        hp_gain = 10
        sanity_gain = 2
        attack_gain = 1

        self.max_hp += hp_gain
        self.hp = self.max_hp
        self.max_sanity += sanity_gain
        self.sanity = self.max_sanity
        self.base_attack = (self.base_attack[0] + attack_gain, self.base_attack[1] + attack_gain)
        
        return {
            'new_level': self.level,
            'hp_gain': hp_gain,
            'sanity_gain': sanity_gain,
            'attack_gain': attack_gain,
            'new_max_hp': self.max_hp,
            'new_max_sanity': self.max_sanity,
            'new_base_attack': self.base_attack
        }

    # ==========================================
    # EQUIPMENT & ITEM USAGE
    # ==========================================
    def equip_weapon(self, weapon):
        """
        Equip a weapon from inventory for use in combat.
        
        Returns:
            dict: Result of equipping
        """
        self.weapon = weapon
        return {
            'success': True,
            'message': f"You equipped {weapon.name}!",
            'weapon': self.weapon_to_dict()
        }

    def unequip_weapon(self):
        """
        Unequip current weapon.
        
        Returns:
            dict: Result of unequipping
        """
        if self.weapon:
            weapon_name = self.weapon.name
            self.weapon = None
            return {
                'success': True,
                'message': f"You unequipped {weapon_name}."
            }
        return {
            'success': False,
            'message': "No weapon equipped."
        }

    def use_item(self, item):
        """
        Use an item (or consumable) from the inventory on the player.
        
        Returns:
            dict: Result of item usage
        """
        result = item.use(self)
        
        # Remove depleted consumables
        if hasattr(item, "quantity") and item.quantity <= 0:
            self.inventory.remove(item)
            
        return result

    # ==========================================
    # SERIALIZATION FOR API
    # ==========================================
    def to_dict(self):
        """
        Convert player state to dictionary for JSON serialization.
        
        Returns:
            dict: Complete player state
        """
        return {
            'name': self.name,
            'level': self.level,
            'exp': self.exp,
            'exp_to_next': self.exp_to_next,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'sanity': self.sanity,
            'max_sanity': self.max_sanity,
            'base_attack': self.base_attack,
            'weapon': self.weapon_to_dict(),
            'inventory': [self._item_to_dict(item) for item in self.inventory],
            'ammo': self.ammo,
            'markka': self.markka,
            'manifestations': [self._manifestation_to_dict(m) for m in self.manifestations]
        }
    
    def weapon_to_dict(self):
        """Convert equipped weapon to dict."""
        if not self.weapon:
            return None
        return self._item_to_dict(self.weapon)
    
    def _item_to_dict(self, item):
        """Convert an item to dictionary."""
        data = {
            'name': item.name,
            'description': item.description
        }
        
        # Add type-specific fields for weapons
        if hasattr(item, 'attack_range'):
            data['attack_range'] = item.attack_range
            data['weapon_type'] = getattr(item, 'weapon_type', 'melee')
            if data['weapon_type'] == 'gun':
                data['current_mag'] = getattr(item, 'current_mag', 0)
                data['mag_size'] = getattr(item, 'mag_size', 0)
                data['ammo_type'] = getattr(item, 'ammo_type', 'bullets')
        
        # Add type-specific fields for consumables
        if hasattr(item, 'quantity'):
            data['quantity'] = item.quantity
            data['type'] = getattr(item, 'type', None)
            data['sfx_name'] = getattr(item, 'sfx_name', None)
            # Store the library key so we can look it up later
            data['library_key'] = getattr(item, '_library_key', item.name)
            
        return data
    
    def _manifestation_to_dict(self, manifestation):
        """Convert a manifestation to dictionary."""
        return {
            'name': manifestation.name,
            'description': manifestation.description,
            'sanity_cost': manifestation.sanity_cost,
            'target_type': getattr(manifestation, 'target_type', 'enemy')
        }
    
    @classmethod
    def from_dict(cls, data, item_library=None, manifestation_library=None):
        """
        Reconstruct a Player instance from dictionary data.
        
        Args:
            data: Dictionary from to_dict()
            item_library: Reference to items/weapons for reconstruction
            manifestation_library: Reference to manifestations for reconstruction
            
        Returns:
            Player: Reconstructed player instance
        """
        # Import libraries if not provided
        if item_library is None:
            from .items import weapon_library, consumable_library
            item_library = {**weapon_library, **consumable_library}
        
        if manifestation_library is None:
            from .manifestations import manifestation_library as manif_lib
            manifestation_library = manif_lib
        
        # Create player with basic data
        player = cls(data['name'])
        player.level = data['level']
        player.exp = data['exp']
        player.exp_to_next = data['exp_to_next']
        player.hp = data['hp']
        player.max_hp = data['max_hp']
        player.sanity = data['sanity']
        player.max_sanity = data['max_sanity']
        player.base_attack = tuple(data['base_attack'])
        player.ammo = data.get('ammo', {})
        player.markka = data['markka']
        
        # Reconstruct weapon
        if data.get('weapon'):
            weapon_name = data['weapon']['name']
            if weapon_name in item_library:
                base_weapon = item_library[weapon_name]
                # For guns, create a new instance to preserve state
                if data['weapon'].get('weapon_type') == 'gun':
                    from .items import Weapon
                    player.weapon = Weapon(
                        base_weapon.name,
                        base_weapon.description,
                        base_weapon.attack_range,
                        base_weapon.weapon_type,
                        ammo_type=base_weapon.ammo_type,
                        mag_size=base_weapon.mag_size,
                        sfx_attack=base_weapon.sfx_attack,
                        sfx_reload=getattr(base_weapon, 'sfx_reload', None)
                    )
                    player.weapon.current_mag = data['weapon'].get('current_mag', 0)
                else:
                    # For melee weapons, use library reference
                    player.weapon = base_weapon
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data.get('inventory', []):
            # Try to use library_key first, then fall back to name
            item_key = item_data.get('library_key', item_data.get('name'))
            item_name = item_data['name']
            
            if item_key in item_library:
                base_item = item_library[item_key]
                # For consumables, create a new instance with the quantity
                if hasattr(base_item, 'quantity'):
                    from .items import Consumable
                    item = Consumable(
                        base_item.name,
                        base_item.description,
                        base_item.effect,
                        quantity=item_data.get('quantity', 1),
                        sfx_name=item_data.get('sfx_name'),
                        type=item_data.get('type')
                    )
                    # Store the library key for future serialization
                    item._library_key = item_key
                    player.inventory.append(item)
                else:
                    # For weapons, create new instances for guns to preserve state
                    if item_data.get('weapon_type') == 'gun':
                        from .items import Weapon
                        weapon = Weapon(
                            base_item.name,
                            base_item.description,
                            base_item.attack_range,
                            base_item.weapon_type,
                            ammo_type=base_item.ammo_type,
                            mag_size=base_item.mag_size,
                            sfx_attack=base_item.sfx_attack,
                            sfx_reload=getattr(base_item, 'sfx_reload', None)
                        )
                        weapon.current_mag = item_data.get('current_mag', 0)
                        player.inventory.append(weapon)
                    else:
                        # For melee weapons, use library reference
                        player.inventory.append(base_item)
        
        # Reconstruct manifestations
        player.manifestations = []
        for manif_data in data.get('manifestations', []):
            manif_name = manif_data['name']
            if manif_name in manifestation_library:
                player.manifestations.append(manifestation_library[manif_name])
        
        return player
