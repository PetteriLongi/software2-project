"""
manifestations.py - Instructions for use in the main game file

1. Import manifestations:
       from manifestations import Manifestation, manifestation_library

2. Access a manifestation:
       fear = manifestation_library["Fear"]
       rage = manifestation_library["Rage"]
       despair = manifestation_library["Despair"]

3. Assign manifestations to the player:
       player["manifestations"] = [fear, rage]  # list of Manifestation objects

4. Using a manifestation in combat:
       # Choose a target enemy instance (from enemies.py)
       result_messages = fear.use_skill(player, enemy)

       # result_messages is a list of formatted strings describing the effect
       # You can display them using:
       for msg in result_messages:
           print(msg)

5. Notes:
       - The player's "sanity" must be >= the manifestation's sanity_cost to use it.
       - Each manifestation has a description (for menus) and a special_attack function defining its effect.
       - You can extend the library by adding new Manifestation objects:
           manifestation_library["NewPower"] = Manifestation("NewPower", sanity_cost=5, special_attack=my_func, description="...")

"""

import random
from .music import play_sfx

# ==========================================
# CLASS DEFINITION: MANIFESTATION
# ==========================================

class Manifestation:
    """
    Represents a summonable entity (like a magical or psychic power)
    that the player can use in combat.
    """
    def __init__(self, name, sanity_cost, special_attack, description, target_type="enemy", sfx_manifest=None):
        self.name = name                        # Name of the manifestation
        self.sanity_cost = sanity_cost          # How much sanity (mana) it costs to use
        self.special_attack = special_attack    # Function that runs when used
        self.description = description          # Description shown in menu
        self.target_type = target_type          # "enemy" (default) or "self"
        self.sfx_manifest = sfx_manifest        # Optional sound effect to play when this manifestation is used (loaded via main)

    # Method to use the manifestation's skill in combat
    def use_skill(self, player, enemy):
        """
        Attempts to use the manifestation's special ability in combat.

        Args:
            player: Player instance (game.player.Player) using this manifestation.
            enemy: Enemy instance to target, or None for self-targeting skills.

        Returns:
            List[str] of log messages describing the outcome, or a one-line
            message indicating insufficient sanity.
        """
        if player.sanity >= self.sanity_cost:                     # Check if player has enough sanity
            player.sanity -= self.sanity_cost                     # Reduce sanity cost
            if getattr(self, "sfx_manifest", None):
                try:
                    play_sfx(self.sfx_manifest)
                except Exception:
                    # Fail silently if audio unavailable
                    pass
            messages = self.special_attack(player, enemy)
            return messages                                          # Call its special attack function
        else:
            return [f"\033[95mNot enough sanity to summon {self.name}'s power!\033[0m"]


# ==========================================
# SPECIAL ATTACK FUNCTIONS
# ==========================================

def fear_special(player, enemy):
    """
    Fear manifestation: Deals strong psychic damage to the enemy.
    """
    dmg = random.randint(14, 24)         # Damage range for Fear
    enemy.hp -= dmg                      # Apply damage
    messages = [
        f"\033[95mManifestation of Fear whispers horrors into {enemy.name}!\033[0m",
        f"\033[95mIt deals {dmg} psychic damage!\033[0m"
    ]
    return messages

#Hope special attack heals the player
def hope_special(player, enemy=None):
    """
    Hope manifestation: Heals the player.
    """
    heal = random.randint(10, 20)
    player.hp = min(player.max_hp, player.hp + heal)
    messages = [
        f"\033[95mManifestation of Hope heals you!\033[0m",
        f"\033[95mYou recover {heal} HP!\033[0m"
    ]
    return messages

#Rages special attack
def rage_special(player, enemy):
    """
    Rage manifestation: High damage to enemy but player suffers recoil.
    """
    dmg = random.randint(20, 42)        # Low - High damage
    enemy.hp -= dmg
    recoil = random.randint(1, 20)      # Player also takes recoil damage
    player.hp -= recoil
    messages = [
        f"\033[95mManifestation of Rage erupts in violent fury!\033[0m",
        f"\033[95mIt deals {dmg} damage but you suffer {recoil} recoil.\033[0m"
    ]
    return messages

#despairs special attack steals HP from the enemy
def resentment_special(player, enemy):
    """
    Resentment manifestation: Damages enemy and heals the player.
    """
    dmg = random.randint(4, 25)
    enemy.hp -= dmg
    heal = dmg // 2
    player.hp = min(player.max_hp, player.hp + heal)
    messages = [
        f"\033[95mManifestation of Resentment drains life from {enemy.name}!\033[0m",
        f"\033[95mIt deals {dmg} damage and heals you for {heal}.\033[0m"
    ]
    return messages

# ==========================================
# ==========================================

# This dictionary stores all available manifestations for easy access
manifestation_library = {
    "Fear": Manifestation("Fear", sanity_cost=5, special_attack=fear_special, description="Strong psychic damage.", sfx_manifest="Fear"),
    "Hope": Manifestation("Hope", sanity_cost=5, special_attack=hope_special, description="Fuels the spirit, revitalizing your body.", target_type="self", sfx_manifest="Hope"),
    "Rage": Manifestation("Rage", sanity_cost=6, special_attack=rage_special, description="High damage but hurts you.", sfx_manifest="Rage"),
    "Resentment": Manifestation("Resentment", sanity_cost=4, special_attack=resentment_special, description="Damage + life steal.", sfx_manifest="Resentment"),
}