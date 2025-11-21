"""
player.py - Defines the Player character and leveling logic.

This file contains the `Player` class. A Player has stats like HP and Sanity,
an inventory, an optional weapon, and a list of unlocked manifestations
(special skills).
"""
# ==========================================
# PLAYER CLASS
# ==========================================

class Player:
    def __init__(self, name, unlocked_manifestations=None):
        """Create a new player with default starting stats.

        Args:
            name (str): Visible name of the player character.
            unlocked_manifestations (list): Optional list of starting skills.
        """
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        self.max_hp = 4000
        self.hp = 4000
        self.max_sanity = 15
        self.sanity = 15
        self.base_attack = (4, 8)            # Fallback damage if no weapon is equipped
        self.weapon = None                   # Equipped Weapon (or None)
        self.inventory = []                  # List of Item/Weapon/Consumable instances
        # Ammo pool keyed by ammo type (e.g., 'bullets', 'rifle', 'shells')
        # Example: {'bullets': 12}
        self.ammo = {}
        self.markka = 0                     # Current currency amount (synced from run state when available)
        self.manifestations = unlocked_manifestations if unlocked_manifestations else []

    def attack_range(self):
        """Return the active attack range tuple depending on the weapon.

        If a weapon is equipped, use its damage range. Otherwise use base.
        """
        if self.weapon:
            return self.weapon.attack_range
        return self.base_attack

    def gain_exp(self, amount):
        """Add EXP and trigger level-ups as needed."""
        self.exp += amount
        # Use UI helper for consistent styling (lazy import avoids circulars)
        try:
            from .ui import ui_print  # type: ignore
            ui_print(f"You gain {amount} EXP!", "blue")
        except Exception:
            # Fallback if UI unavailable
            print(f"You gain {amount} EXP!")
        while self.exp >= self.exp_to_next:
            # Lazy import to avoid any potential circulars at module import time
            from .ui import level_up_display  # type: ignore
            level_up_display(self)

    def level_up(self):
        """Increase player level and improve core stats.

        This resets HP and Sanity to the new maximums and slightly
        increases base attack damage to reflect progression.
        """
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

    # ==========================================
    # EQUIPMENT & ITEM USAGE
    # ==========================================
    def equip_weapon(self,weapon):
        """Equip a weapon from inventory for use in combat."""
        self.weapon = weapon
        try:
            from .ui import ui_print  # type: ignore
            ui_print(f"You equipped {weapon.name}!", "green")
        except Exception:
            print(f"You equipped {weapon.name}!")

    def use_item(self, item):
        """Use an item (or consumable) from the inventory on the player.

        Items can print messages or modify player state depending on their
        effect function. Depleted consumables are removed automatically.
        """
        result = item.use(self)
        if result:
            print(result)
        if hasattr(item, "quantity") and item.quantity <= 0:
            self.inventory.remove(item)

    # ==========================================
    # STATUS DISPLAY
    # ==========================================
    def show_status(self):
        """Print current player status in a compact format."""
        print(f"{self.name} - Level {self.level}")
        print(f"HP: {self.hp}/{self.max_hp} | Sanity: {self.sanity}/{self.max_sanity}")
        print(f"Attack: {self.attack_range()}")
        if self.ammo:
            ammo_str = ", ".join(f"{k}: {v}" for k, v in self.ammo.items())
            print(f"Ammo: {ammo_str}")