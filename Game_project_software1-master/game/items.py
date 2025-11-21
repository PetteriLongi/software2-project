"""
items.py - Instructions for use in the main game file

1. Import the relevant classes and functions:
       from items import Item, Weapon, Consumable
       from items import add_weapon_to_inventory, add_item_to_inventory
       from items import weapon_library, consumable_library

2. Adding items or weapons to the player's inventory:
       add_weapon_to_inventory(player, "Basic dagger")
       add_item_to_inventory(player, "Health Potion", amount=2)

3. Creating custom items or weapons:
       potion = Consumable("Custom Potion", "Restores 20 HP", effect=custom_effect, quantity=1)
       dagger = Weapon("Steel Dagger", "Sharp and fast", attack_range=(8, 14), weapon_type='melee')

4. All item effects return strings suitable for printing to the combat log.
"""
# Import audio helper for item SFX
from .music import play_sfx
from .ui import ui_print

# ==========================================
# Classes for Items, Weapons, and Consumables
# ==========================================

class Item:
    """
    Base class for all items in the game.
    Represents any object the player can carry/use.
    """
    def __init__(self, name, description, effect=None):
        self.name = name                # Name of the item
        self.description = description  # Short description of the item
        self.effect = effect            # Optional function applied when the item is used

    def use(self, target):
        """
        Use the item on a target (player or enemy).
        If it has an effect function, apply it and return its result as a string.
        """
        if self.effect:
            return self.effect(target)
        else:
            return f"{self.name} has no effect!"

class Weapon(Item):
    """
    Represents a weapon. Inherits from Item because weapons are also items.
    """
    def __init__(self, name, description, attack_range, weapon_type='melee', ammo_type=None, mag_size=0, sfx_attack=None, sfx_reload=None):
        super().__init__(name, description)  # Initialize Item attributes
        self.attack_range = attack_range     # Tuple (min_attack, max_attack) for damage
        self.weapon_type = weapon_type       # 'melee' or 'gun'
        # Gun-specific fields
        self.ammo_type = ammo_type           # e.g., 'bullets', 'rifle'
        self.mag_size = mag_size             # magazine capacity
        self.current_mag = mag_size if weapon_type == 'gun' else 0  # start loaded for guns
        # Optional SFX key to play on attack (loaded in main.py)
        self.sfx_attack = sfx_attack
        self.sfx_reload = sfx_reload

class Consumable(Item):
    """
    Represents consumable items, like potions or ammo.
    Inherits from Item but adds quantity tracking.
    If 'type' is provided (e.g., 'ammo'), it will be used for routing logic.
    """
    def __init__(self, name, description, effect=None, quantity=1, type=None, sfx_name=None):
        super().__init__(name, description, effect)
        self.quantity = quantity  # How many of this item the player has
        # Optional semantic type label, e.g., 'ammo'.
        # Note: using the parameter name 'type' to match existing library entries.
        self.type = type
        # Optional sound effect to play when this consumable is used (loaded via main)
        self.sfx_name = sfx_name

    def use(self, player):
        """
        Use the consumable on the player.
        Reduces quantity, applies effect, and returns a message for display.
        """
        if self.quantity > 0:
            self.quantity -= 1
            # Play item-specific SFX if configured
            if getattr(self, "sfx_name", None):
                try:
                    play_sfx(self.sfx_name)
                except Exception:
                    # Fail silently if audio unavailable
                    pass
            msg = ""
            if self.effect:
                msg = self.effect(player)   # Call the effect function
            return msg
        else:
            return f"\033[91mYou have no {self.name} left!\033[0m"

class LoreItem(Item):
    """
    Represents a lore item, like a note or a book.
    Inherits from Item but adds quantity tracking.
    """
    def __init__(self, name, description, text):
        super().__init__(name, description)
        self.text = text
    
    def display_text(self):
        return self.text

    def use(self, player):
        return self.display_text()


# ==========================================
# Functions to add items or weapons to inventory
# ==========================================


def add_weapon_to_inventory(player, weapon_name, current_mag=None):
    """
    Adds a weapon from the weapon library to the player's inventory.

    current_mag behavior for firearms:
      - None (default): full magazine (existing behavior)
      - "empty": magazine starts at 0
      - int: magazine starts partially loaded (clamped to [0, mag_size])

    Notes:
      - Melee weapons ignore current_mag and always have current_mag = 0.
      - This function does not pull rounds from player.ammo; it only sets the
        starting magazine on the newly acquired weapon.
    """
    template = weapon_library.get(weapon_name)
    if template:
        # Create a fresh instance so magazine state isn't shared
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
            if current_mag is None or (isinstance(current_mag, str) and  current_mag.lower() == 'full'):
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
        ui_print(f"\nYou obtained a new weapon: {new_weapon.name}!", "cyan")
    else:
        ui_print(f"Weapon '{weapon_name}' does not exist in the library.", "red")


def add_item_to_inventory(player, item_name, amount=1):
    """
    Adds a consumable item to the player's inventory.
    If the item already exists, increases the quantity.
    """
    # Resolve to canonical library key (case-insensitive)
    canonical = next((k for k in consumable_library.keys() if k.lower() == item_name.lower()), None)
    if canonical is not None:
        base_item = consumable_library[canonical]
        # Route ANY consumable explicitly marked as ammo into the ammo pool
        if getattr(base_item, "type", None) and str(getattr(base_item, "type")).lower() == "ammo":
            # Use the consumable's display name as the canonical ammo key.
            # This should match Weapon.ammo_type (e.g., "5.56x45mm NATO").
            key = base_item.name
            player.ammo[key] = player.ammo.get(key, 0) + amount
            ui_print(f"You obtained {amount}x {key}! Ammo pool now has {player.ammo[key]}.", "yellow")
            return
        # Otherwise, stack consumables in inventory
        for item in player.inventory:
            if isinstance(item, Consumable) and item.name == base_item.name:
                    item.quantity += amount
                    ui_print(f"You obtained {amount}x {item.name}! You now have: {item.quantity} of these", "yellow")
                    return

        # Otherwise, create a new item and add it
        new_item = Consumable(
            base_item.name,
            base_item.description,
            base_item.effect,
            quantity=amount,
            sfx_name=getattr(base_item, "sfx_name", None),
        )
        player.inventory.append(new_item)
        ui_print(f"You obtained {amount}x {new_item.name}!", "green")
    else:
        ui_print(f"Item '{item_name}' does not exist in the library.", "red")

"""ITEM EFFECTS START HERE"""


# ==========================================
# Effects for consumable items
# ==========================================

def heal_hp(player, amount):
    """
    Effect function for Health Potion.
    Restores HP, but not above the player's max HP.
    Returns a formatted string to display in combat.
    """
    player.hp = min(player.max_hp, player.hp + amount)
    return f"\033[92mYou recover {amount} HP!\033[0m"

def restore_sanity(player, amount):
    """
    Effect function for Sanity Potion.
    Restores sanity points.
    Returns a formatted string to display in combat.
    """
    player.sanity = min(player.max_sanity, player.sanity + amount)
    return f"\033[94mYou recover {amount} sanity!\033[0m"



"""WEAPON AND CONSUMABLE LIBRARIES START HERE"""

# ==========================================
# Weapon and consumable libraries
# ==========================================

# Dictionary of all weapons in the game
weapon_library = {
    "Basic dagger" : Weapon("Basic dagger", "Quick and light, but low damage", attack_range=(7,12), weapon_type='melee', sfx_attack="knife_slash"),
    "Sword" : Weapon("Ulfberht sword", "high-quality steel sword from the Viking era", attack_range=(10,20), weapon_type='melee', sfx_attack="sword_slash"),
    "Jack's hammer" : Weapon("Jack's hammer", "Jack's beloved hammer of destruction", attack_range=(50,999), weapon_type='melee'),
    "Old revolver" : Weapon("Old revolver", "It has seen better days but seems to still be usable", attack_range=(10,16), weapon_type='gun', ammo_type='.36 Caliber', mag_size=6, sfx_attack="revolver_shot", sfx_reload="revolver_reload"),
    "MP7" : Weapon("MP7", "A German Personal Defense Weapon and submachine gun", attack_range=(10, 20), weapon_type="gun", ammo_type='4.6x30mm', mag_size=20, sfx_attack="submachine_shot", sfx_reload="reload"),
    "AR-15" : Weapon("AR-15", "Lightweight semi-automatic rifle", attack_range=(15, 30), weapon_type="gun", ammo_type='5.56x45mm NATO', mag_size=30, sfx_attack="rifle_shot", sfx_reload="reload"),
    # Additional weapons can be added here
}

# Dictionary of all consumable items in the game
consumable_library = {
    "Small Health Potion": Consumable("Karelian pie", "A warm, comforting pastry that restores your health with each bite.", effect=lambda player: heal_hp(player, 10), quantity=0, sfx_name="Eating"),
    "Large Health Potion": Consumable("Rye Bread", "Hearty slice of Finnish grain. Keeps a man on the road.", effect=lambda player: heal_hp(player, 30), quantity=0, sfx_name="Eating"),
    "Small Sanity Potion": Consumable("Small coffee", "Small soothing container of coffee, this should calm your mind.", effect=lambda player: restore_sanity(player, 10), quantity=0, sfx_name="Drinking"),
    "Large Sanity Potion": Consumable("Large coffee", "Full thermos container of coffee, this should calm your mind a lot.", effect=lambda player: restore_sanity(player, 20), quantity=0, sfx_name="Drinking"),
    "pistol ammo": Consumable(".36 Caliber", "Revolver ammunition.", effect=None, quantity=0, type="ammo"),
    "rifle ammo": Consumable("5.56x45mm NATO", "Rifle ammunition.", effect=None, quantity=0, type="ammo"),
    "submachine ammo": Consumable("4.6x30mm", "Submachine gun ammunition.", effect=None, quantity=0, type="ammo"),
    "Makkara": Consumable("Makkara", "A makkara is a unit of currency in Finland. Wait what?!?", effect=lambda player: heal_hp(player, 100) + restore_sanity(player, 100), quantity=0, sfx_name="Eating"),
    # Additional items like antidotes, elixirs, etc., can be added here
}