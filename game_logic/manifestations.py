"""
manifestations.py - Manifestation (special abilities) system.

Migrated for web: Removed audio dependencies, returns data instead of ANSI-colored strings.
This runs on the Flask backend and maintains manifestation logic.
"""

import random


class Manifestation:
    """
    Represents a summonable entity (like a magical or psychic power)
    that the player can use in combat.
    """
    
    def __init__(self, name, sanity_cost, special_attack, description, target_type="enemy", sfx_manifest=None):
        """
        Initialize a manifestation.
        
        Args:
            name: Name of the manifestation
            sanity_cost: Sanity required to use
            special_attack: Function that processes the manifestation effect
            description: Description for display
            target_type: "enemy" or "self"
            sfx_manifest: Sound effect name (handled by frontend)
        """
        self.name = name
        self.sanity_cost = sanity_cost
        self.special_attack = special_attack
        self.description = description
        self.target_type = target_type
        self.sfx_manifest = sfx_manifest

    def use_skill(self, player, enemy):
        """
        Attempts to use the manifestation's special ability in combat.

        Args:
            player: Player instance using this manifestation
            enemy: Enemy instance to target, or None for self-targeting skills

        Returns:
            dict: Result of manifestation use including messages and effects
        """
        if player.sanity >= self.sanity_cost:
            player.sanity -= self.sanity_cost
            messages = self.special_attack(player, enemy)
            
            return {
                'success': True,
                'sanity_cost': self.sanity_cost,
                'messages': messages if isinstance(messages, list) else [messages],
                'player_sanity': player.sanity,
                'sfx': self.sfx_manifest  # Frontend will play this
            }
        else:
            return {
                'success': False,
                'messages': [f"Not enough sanity to summon {self.name}'s power!"],
                'required_sanity': self.sanity_cost,
                'current_sanity': player.sanity
            }
    
    def to_dict(self):
        """Convert manifestation to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'sanity_cost': self.sanity_cost,
            'description': self.description,
            'target_type': self.target_type,
            'sfx': self.sfx_manifest
        }


# ==========================================
# SPECIAL ATTACK FUNCTIONS
# ==========================================

def fear_special(player, enemy):
    """
    Fear manifestation: Deals strong psychic damage to the enemy.
    """
    dmg = random.randint(14, 24)
    enemy.hp -= dmg
    messages = [
        f"Manifestation of Fear whispers horrors into {enemy.name}!",
        f"It deals {dmg} psychic damage!"
    ]
    return messages


def hope_special(player, enemy=None):
    """
    Hope manifestation: Heals the player.
    """
    heal = random.randint(10, 20)
    player.hp = min(player.max_hp, player.hp + heal)
    messages = [
        "Manifestation of Hope heals you!",
        f"You recover {heal} HP!"
    ]
    return messages


def rage_special(player, enemy):
    """
    Rage manifestation: High damage to enemy but player suffers recoil.
    """
    dmg = random.randint(20, 42)
    enemy.hp -= dmg
    recoil = random.randint(1, 20)
    player.hp -= recoil
    messages = [
        "Manifestation of Rage erupts in violent fury!",
        f"It deals {dmg} damage but you suffer {recoil} recoil."
    ]
    return messages


def resentment_special(player, enemy):
    """
    Resentment manifestation: Damages enemy and heals the player.
    """
    dmg = random.randint(4, 25)
    enemy.hp -= dmg
    heal = dmg // 2
    player.hp = min(player.max_hp, player.hp + heal)
    messages = [
        f"Manifestation of Resentment drains life from {enemy.name}!",
        f"It deals {dmg} damage and heals you for {heal}."
    ]
    return messages


# ==========================================
# MANIFESTATION LIBRARY
# ==========================================

manifestation_library = {
    "Fear": Manifestation(
        "Fear",
        sanity_cost=5,
        special_attack=fear_special,
        description="Strong psychic damage.",
        sfx_manifest="Fear"
    ),
    "Hope": Manifestation(
        "Hope",
        sanity_cost=5,
        special_attack=hope_special,
        description="Fuels the spirit, revitalizing your body.",
        target_type="self",
        sfx_manifest="Hope"
    ),
    "Rage": Manifestation(
        "Rage",
        sanity_cost=6,
        special_attack=rage_special,
        description="High damage but hurts you.",
        sfx_manifest="Rage"
    ),
    "Resentment": Manifestation(
        "Resentment",
        sanity_cost=4,
        special_attack=resentment_special,
        description="Damage + life steal.",
        sfx_manifest="Resentment"
    ),
}
