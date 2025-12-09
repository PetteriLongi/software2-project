"""
enemies.py - Enemy class and combat AI for web version

Migration changes:
- Removed all direct player.hp/sanity modifications (return damage instead)
- Changed take_turn() to return structured dict with damage/sanity_loss/messages
- Special attacks return dicts instead of modifying player directly
- Added to_dict() method for JSON serialization
- Death effects return dict with damage information
"""

import random


class Enemy:
    """
    Represents an enemy in the game.
    Each enemy has a name, difficulty level, health points (HP),
    attack range, optional special attack, and a description.
    """
    def __init__(self, name, difficulty, hp, attack, special_attack=None, 
                 special_attack_chance=0.3, death_effect=None, description="", exp_reward=10):
        self.name = name
        self.difficulty = difficulty
        self.hp = hp
        self.max_hp = hp
        self.attack = attack  # Tuple (min_damage, max_damage)
        self.special_attack = special_attack
        self.special_attack_chance = special_attack_chance
        self.death_effect = death_effect
        self.description = description
        self.exp_reward = exp_reward

    def take_turn(self, player_defending=False):
        """
        Called when the enemy takes its turn in combat.
        Returns a dict with turn results instead of modifying player directly.

        Args:
            player_defending (bool): if True, player has chosen Defend this round

        Returns:
            dict: {
                'type': 'normal' or 'special',
                'damage': int (HP damage to player),
                'sanity_loss': int (sanity damage to player),
                'messages': list of str (combat log messages),
                'special_name': str (only for special attacks),
                'healed_enemy': {'name': str, 'hp': int, 'heal_amount': int} (for ally heals)
            }
        """
        result = {
            'type': 'normal',
            'damage': 0,
            'sanity_loss': 0,
            'messages': [],
            'healed_enemy': None,
            'summoned_enemy': None
        }

        # Roll for special attack
        if self.special_attack and random.random() < self.special_attack_chance:
            result['type'] = 'special'
            special_result = self.special_attack(self)
            result.update(special_result)
        else:
            # Basic attack
            dmg = random.randint(*self.attack)
            if player_defending:
                dmg //= 2
            result['damage'] = dmg
            result['messages'].append(f"{self.name} strikes you for {dmg} damage!")

        result['messages'].append("")
        return result

    def apply_death_effect(self):
        """
        Called when enemy dies. Returns damage to player if death effect exists.

        Returns:
            dict: {
                'has_effect': bool,
                'damage': int,
                'message': str
            }
        """
        if not self.death_effect:
            return {'has_effect': False, 'damage': 0, 'message': ''}
        
        return self.death_effect(self)

    def to_dict(self):
        """Convert enemy to JSON-serializable dict"""
        return {
            'name': self.name,
            'type': self.name,
            'difficulty': self.difficulty,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'description': self.description,
            'exp_reward': self.exp_reward,
            'special_attack_chance': self.special_attack_chance,
            'has_special_attack': self.special_attack is not None,
            'has_death_effect': self.death_effect is not None
        }
    
    @staticmethod
    def from_dict(data):
        """
        Reconstruct Enemy from dict.
        Re-creates enemy with correct special attacks and death effects from enemy_library.
        """
        # Use enemy_type if available (library key), otherwise try to find by display name
        enemy_key = data.get('enemy_type')
        
        if not enemy_key:
            # Try to find enemy by display name (for backwards compatibility)
            display_name = data['name']
            enemy_key = None
            for key, template in enemy_library.items():
                if template.name == display_name:
                    enemy_key = key
                    break
            
            if not enemy_key:
                # Fallback to using the display name as key
                enemy_key = display_name
        
        # Use create_enemy to get proper enemy with all methods
        enemy = create_enemy(enemy_key)
        # Restore serialized state
        enemy.hp = data['hp']
        enemy.max_hp = data['max_hp']
        return enemy


# ==========================================
# Special Attacks for Enemies
# ==========================================

def apostle_buff(enemy):
    """
    Special attack for Apostles.
    Returns healing information for lowest HP ally.
    Note: Ally selection logic must be handled by combat engine.
    """
    heal = random.randint(3, 6)
    return {
        'special_name': 'Hymn of Restoration',
        'damage': 0,
        'sanity_loss': 0,
        'heal_amount': heal,
        'messages': [f"{enemy.name} chants a hymn, healing an ally for {heal} HP!"]
    }


def priest_curse(enemy):
    """
    Special attack for High Priests.
    Reduces the player's sanity.
    """
    sanity_dmg = random.randint(4, 8)
    return {
        'special_name': 'Dark Curse',
        'damage': 0,
        'sanity_loss': sanity_dmg,
        'messages': [
            f"{enemy.name} invokes a dark curse!",
            f"Your sanity is reduced by {sanity_dmg}!"
        ]
    }


def rite_of_reclamation(enemy):
    """
    Special attack for Anatomist.
    Does damage to the player and heals itself.
    """
    dmg = random.randint(4, 10)
    heal = dmg
    # Self-heal applied directly since it affects the enemy itself
    enemy.hp = min(enemy.max_hp, enemy.hp + heal)
    
    return {
        'special_name': 'Rite of Reclamation',
        'damage': dmg,
        'sanity_loss': 0,
        'self_heal': heal,
        'messages': [
            f"{enemy.name} strikes you for {dmg} damage!",
            f"The Anatomist licks its blade clean and regains {heal} HP!"
        ]
    }


def unstable_form_death(enemy):
    """
    Death effect for Starborn.
    Returns damage dealt as it collapses.
    """
    dmg = random.randint(4, 10)
    return {
        'has_effect': True,
        'damage': dmg,
        'message': f"{enemy.name} collapses, its unstable form tearing itself apart and striking you for {dmg} damage!"
    }


def whisperer_psychic(enemy):
    """
    Special attack for Whisperers.
    Deals minor HP and sanity damage.
    """
    dmg = random.randint(5, 10)
    sanity_dmg = 2
    
    return {
        'special_name': 'Forbidden Truths',
        'damage': dmg,
        'sanity_loss': sanity_dmg,
        'messages': [
            f"{enemy.name} whispers forbidden truths...",
            f"You take {dmg} psychic damage and lose {sanity_dmg} sanity!"
        ]
    }


def call_of_the_hollow(enemy):
    """
    Special attack for Dirge of the Deep.
    Returns information about summoning or attacking.
    Note: Summoning logic must be handled by combat engine.
    """
    # Combat engine will check if fragment already exists
    # For now, return both possibilities and let combat engine decide
    return {
        'special_name': 'Call of the Hollow',
        'summon_attempt': True,
        'summon_name': 'Drowned fragment',
        'fallback_damage': random.randint(3, 8),
        'messages': [f"{enemy.name} whispers forbidden truths..."]
    }


def abomination_crush(enemy):
    """
    Special attack for Abominations.
    Deals high HP damage.
    """
    dmg = random.randint(8, 14)
    
    return {
        'special_name': 'Monstrous Crush',
        'damage': dmg,
        'sanity_loss': 0,
        'messages': [f"{enemy.name} crushes you with monstrous strength for {dmg} damage!"]
    }


# ==========================================
# Enemy Library
# ==========================================

enemy_library = {
    # Difficulty 1
    "Tutorial": Enemy("Wounded Cultist", difficulty=1, hp=20, attack=(1, 3), 
                     description="Fanatical servant of the cult.", exp_reward=0),
    "Cultist": Enemy("Cultist", difficulty=1, hp=20, attack=(3, 6), 
                    description="Fanatical servant of the cult.", exp_reward=10),
    "Drowned fragment": Enemy("Drowned fragment", difficulty=1, hp=10, attack=(1, 5), 
                             description="A fragment of the drowned.", exp_reward=5),

    # Difficulty 2
    "Apostle": Enemy("Apostle", difficulty=2, hp=28, attack=(4, 7), 
                    special_attack=apostle_buff, special_attack_chance=0.3,
                    description="Disciple that heals itself and others with hymns.", exp_reward=20),

    # Difficulty 3
    "High Priest": Enemy("High Priest", difficulty=3, hp=35, attack=(5, 9), 
                        special_attack=priest_curse, special_attack_chance=0.3,
                        description="Leader who curses your sanity.", exp_reward=30),
    "Anatomist": Enemy("Anatomist", difficulty=3, hp=40, attack=(5, 10), 
                      special_attack=rite_of_reclamation, special_attack_chance=1,
                      description="It works by intuition, hands guided by a voice only it can hear.", 
                      exp_reward=30),
    "Starborn": Enemy("Starborn", difficulty=3, hp=12, attack=(4, 10), 
                     death_effect=unstable_form_death,
                     description="Once humans, now hollow vessels etched with constellations. Fragile, but every death tears a hole in reality.", 
                     exp_reward=30),

    # Difficulty 4
    "Whisperer": Enemy("Whisperer", difficulty=4, hp=30, attack=(4, 10), 
                      special_attack=whisperer_psychic, special_attack_chance=0.3,
                      description="Maddening voice that eats away at your mind.", exp_reward=40),
    "Dirge of the Deep": Enemy("Dirge of the Deep", difficulty=4, hp=34, attack=(3, 8), 
                              special_attack=call_of_the_hollow, special_attack_chance=1,
                              description="A veiled entity that calls the void to your location.", 
                              exp_reward=35),

    # Difficulty 5
    "Abomination": Enemy("Abomination", difficulty=5, hp=50, attack=(6, 12), 
                        special_attack=abomination_crush, special_attack_chance=0.3,
                        description="Horrific mutation of flesh and shadow.", exp_reward=50),
}


def create_enemy(name):
    """
    Creates a new instance of an enemy based on the template in the enemy library.
    This ensures each enemy starts with full HP and default stats.
    """
    template = enemy_library[name]
    enemy = Enemy(
        template.name,
        template.difficulty,
        template.max_hp,  # Reset HP to full
        template.attack,
        special_attack=template.special_attack,
        special_attack_chance=template.special_attack_chance,
        death_effect=template.death_effect,
        description=template.description,
        exp_reward=template.exp_reward
    )
    # Store the enemy type key for reconstruction
    enemy._enemy_type = name
    return enemy
