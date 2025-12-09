"""
items.py - Items, weapons, and consumables system.

Migrated for web: Removed audio/UI dependencies, returns data instead of printing.
This runs on the Flask backend and maintains item logic.
"""


class Item:
    """
    Base class for all items in the game.
    Represents any object the player can carry/use.
    """
    
    def __init__(self, name, description, effect=None):
        self.name = name
        self.description = description
        self.effect = effect

    def use(self, target):
        """
        Use the item on a target (player or enemy).
        
        Returns:
            dict: Result of item usage
        """
        if self.effect:
            result = self.effect(target)
            return {
                'success': True,
                'message': result if isinstance(result, str) else str(result)
            }
        else:
            return {
                'success': False,
                'message': f"{self.name} has no effect!"
            }
    
    def to_dict(self):
        """Convert item to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description
        }


class Weapon(Item):
    """
    Represents a weapon. Inherits from Item because weapons are also items.
    """
    
    def __init__(self, name, description, attack_range, weapon_type='melee', 
                 ammo_type=None, mag_size=0, sfx_attack=None, sfx_reload=None):
        super().__init__(name, description)
        self.attack_range = attack_range
        self.weapon_type = weapon_type
        self.ammo_type = ammo_type
        self.mag_size = mag_size
        self.current_mag = mag_size if weapon_type == 'gun' else 0
        self.sfx_attack = sfx_attack
        self.sfx_reload = sfx_reload
    
    def to_dict(self):
        """Convert weapon to dictionary for JSON serialization."""
        data = super().to_dict()
        data.update({
            'attack_range': self.attack_range,
            'weapon_type': self.weapon_type
        })
        
        if self.weapon_type == 'gun':
            data.update({
                'ammo_type': self.ammo_type,
                'mag_size': self.mag_size,
                'current_mag': self.current_mag,
                'sfx_attack': self.sfx_attack,
                'sfx_reload': self.sfx_reload
            })
        
        return data


class Consumable(Item):
    """
    Represents consumable items, like potions or ammo.
    Inherits from Item but adds quantity tracking.
    """
    
    def __init__(self, name, description, effect=None, quantity=1, type=None, sfx_name=None):
        super().__init__(name, description, effect)
        self.quantity = quantity
        self.type = type
        self.sfx_name = sfx_name

    def use(self, player):
        """
        Use the consumable on the player.
        
        Returns:
            dict: Result of consumable usage
        """
        if self.quantity > 0:
            self.quantity -= 1
            
            msg = ""
            if self.effect:
                msg = self.effect(player)
            
            return {
                'success': True,
                'message': msg,
                'quantity_remaining': self.quantity,
                'sfx': self.sfx_name
            }
        else:
            return {
                'success': False,
                'message': f"You have no {self.name} left!",
                'quantity_remaining': 0
            }
    
    def to_dict(self):
        """Convert consumable to dictionary for JSON serialization."""
        data = super().to_dict()
        data.update({
            'quantity': self.quantity,
            'type': self.type,
            'sfx': self.sfx_name
        })
        return data


class LoreItem(Item):
    """
    Represents a lore item, like a note or a book.
    """
    
    def __init__(self, name, description, text):
        super().__init__(name, description)
        self.text = text
    
    def display_text(self):
        return self.text

    def use(self, player):
        return {
            'success': True,
            'message': self.display_text(),
            'type': 'lore'
        }


# ==========================================
# INVENTORY MANAGEMENT FUNCTIONS
# ==========================================

def add_weapon_to_inventory(player, weapon_name, current_mag=None):
    """
    Adds a weapon from the weapon library to the player's inventory.
    
    Returns:
        dict: Result of adding weapon
    """
    template = weapon_library.get(weapon_name)
    if not template:
        return {
            'success': False,
            'message': f"Weapon '{weapon_name}' does not exist in the library."
        }
    
    # Create a fresh instance
    new_weapon = Weapon(
        template.name,
        template.description,
        template.attack_range,
        template.weapon_type,
        getattr(template, 'ammo_type', None),
        getattr(template, 'mag_size', 0),
        getattr(template, 'sfx_attack', None),
        getattr(template, 'sfx_reload', None),
    )

    if getattr(new_weapon, 'weapon_type', 'melee') == 'gun':
        if current_mag is None or (isinstance(current_mag, str) and current_mag.lower() == 'full'):
            new_weapon.current_mag = new_weapon.mag_size
        elif isinstance(current_mag, str) and current_mag.lower() == 'empty':
            new_weapon.current_mag = 0
        elif isinstance(current_mag, int):
            new_weapon.current_mag = max(0, min(new_weapon.mag_size, current_mag))
        else:
            new_weapon.current_mag = new_weapon.mag_size
    else:
        new_weapon.current_mag = 0
    
    player.inventory.append(new_weapon)
    
    return {
        'success': True,
        'message': f"You obtained a new weapon: {new_weapon.name}!",
        'weapon': new_weapon.to_dict()
    }


def add_item_to_inventory(player, item_name, amount=1):
    """
    Adds a consumable item to the player's inventory.
    
    Returns:
        dict: Result of adding item
    """
    canonical = next((k for k in consumable_library.keys() if k.lower() == item_name.lower()), None)
    if canonical is None:
        return {
            'success': False,
            'message': f"Item '{item_name}' does not exist in the library."
        }
    
    base_item = consumable_library[canonical]
    
    # Route ammo to ammo pool
    if getattr(base_item, "type", None) and str(getattr(base_item, "type")).lower() == "ammo":
        key = base_item.name
        player.ammo[key] = player.ammo.get(key, 0) + amount
        return {
            'success': True,
            'message': f"You obtained {amount}x {key}! Ammo pool now has {player.ammo[key]}.",
            'ammo_type': key,
            'total_ammo': player.ammo[key]
        }
    
    # Stack consumables in inventory
    for item in player.inventory:
        if isinstance(item, Consumable) and item.name == base_item.name:
            item.quantity += amount
            return {
                'success': True,
                'message': f"You obtained {amount}x {item.name}! You now have: {item.quantity} of these",
                'item': item.to_dict()
            }

    # Create new item
    new_item = Consumable(
        base_item.name,
        base_item.description,
        base_item.effect,
        quantity=amount,
        sfx_name=getattr(base_item, "sfx_name", None),
    )
    player.inventory.append(new_item)
    
    return {
        'success': True,
        'message': f"You obtained {amount}x {new_item.name}!",
        'item': new_item.to_dict()
    }


# ==========================================
# ITEM EFFECTS
# ==========================================

def heal_hp(player, amount):
    """Effect function for Health Potion."""
    player.hp = min(player.max_hp, player.hp + amount)
    return f"You recover {amount} HP!"


def restore_sanity(player, amount):
    """Effect function for Sanity Potion."""
    player.sanity = min(player.max_sanity, player.sanity + amount)
    return f"You recover {amount} sanity!"


# ==========================================
# WEAPON AND CONSUMABLE LIBRARIES
# ==========================================

weapon_library = {
    "Basic dagger": Weapon(
        "Basic dagger", 
        "Quick and light, but low damage", 
        attack_range=(7, 12), 
        weapon_type='melee', 
        sfx_attack="knife_slash"
    ),
    "Sword": Weapon(
        "Ulfberht sword", 
        "high-quality steel sword from the Viking era", 
        attack_range=(10, 20), 
        weapon_type='melee', 
        sfx_attack="sword_slash"
    ),
    "Jack's hammer": Weapon(
        "Jack's hammer", 
        "Jack's beloved hammer of destruction", 
        attack_range=(50, 999), 
        weapon_type='melee'
    ),
    "Old revolver": Weapon(
        "Old revolver", 
        "It has seen better days but seems to still be usable", 
        attack_range=(10, 16), 
        weapon_type='gun', 
        ammo_type='.36 Caliber', 
        mag_size=6, 
        sfx_attack="revolver_shot", 
        sfx_reload="revolver_reload"
    ),
    "MP7": Weapon(
        "MP7", 
        "A German Personal Defense Weapon and submachine gun", 
        attack_range=(10, 20), 
        weapon_type="gun", 
        ammo_type='4.6x30mm', 
        mag_size=20, 
        sfx_attack="submachine_shot", 
        sfx_reload="reload"
    ),
    "AR-15": Weapon(
        "AR-15", 
        "Lightweight semi-automatic rifle", 
        attack_range=(15, 30), 
        weapon_type="gun", 
        ammo_type='5.56x45mm NATO', 
        mag_size=30, 
        sfx_attack="rifle_shot", 
        sfx_reload="reload"
    ),
}

consumable_library = {
    "Small Health Potion": Consumable(
        "Karelian pie", 
        "A warm, comforting pastry that restores your health with each bite.", 
        effect=lambda player: heal_hp(player, 10), 
        quantity=0, 
        sfx_name="Eating"
    ),
    "Large Health Potion": Consumable(
        "Rye Bread", 
        "Hearty slice of Finnish grain. Keeps a man on the road.", 
        effect=lambda player: heal_hp(player, 30), 
        quantity=0, 
        sfx_name="Eating"
    ),
    "Small Sanity Potion": Consumable(
        "Small coffee", 
        "Small soothing container of coffee, this should calm your mind.", 
        effect=lambda player: restore_sanity(player, 10), 
        quantity=0, 
        sfx_name="Drinking"
    ),
    "Large Sanity Potion": Consumable(
        "Large coffee", 
        "Full thermos container of coffee, this should calm your mind a lot.", 
        effect=lambda player: restore_sanity(player, 20), 
        quantity=0, 
        sfx_name="Drinking"
    ),
    "pistol ammo": Consumable(
        ".36 Caliber", 
        "Revolver ammunition.", 
        effect=None, 
        quantity=0, 
        type="ammo"
    ),
    "rifle ammo": Consumable(
        "5.56x45mm NATO", 
        "Rifle ammunition.", 
        effect=None, 
        quantity=0, 
        type="ammo"
    ),
    "submachine ammo": Consumable(
        "4.6x30mm", 
        "Submachine gun ammunition.", 
        effect=None, 
        quantity=0, 
        type="ammo"
    ),
    "Makkara": Consumable(
        "Makkara", 
        "A makkara is a unit of currency in Finland. Wait what?!?", 
        effect=lambda player: heal_hp(player, 100) and restore_sanity(player, 100), 
        quantity=0, 
        sfx_name="Eating"
    ),
}
