"""
enemies.py - Instructions for use in the main game file

1. Import the Enemy class and helper functions:
       from enemies import Enemy, create_enemy, enemy_library

2. Creating a new enemy instance:
       # From the enemy library
       cultist = create_enemy("Cultist")
       # Or manually
       custom_enemy = Enemy("Goblin", difficulty=1, hp=15, attack=(2, 5))

3. Accessing predefined enemies:
       enemy = enemy_library["High Priest"]

4. Handling special attacks:
       # Special attacks are automatically called within take_turn()
       # They return messages suitable for the combat log.

5. Tips:
       - Use create_enemy() when you want a fresh instance with full HP.
       - Always capture the returned messages from take_turn() and print or log them in your combat loop.
"""


import random
# ==========================================
# Enemy Class
# ==========================================

class Enemy:
    """
    Represents an enemy in the game.
    Each enemy has a name, difficulty level, health points (HP),
    attack range, optional special attack, and a description.
    """
    def __init__(self, name, difficulty, hp, attack, special_attack=None, special_attack_chance=0.3, death_effect=None, description="", exp_reward=10):
        self.name = name                    # Enemy's name
        self.difficulty = difficulty        # Difficulty rating (can be used for scaling loot, XP, etc.)
        self.hp = hp                        # Current health
        self.max_hp = hp                    # Maximum health
        self.attack = attack                # Tuple (min_damage, max_damage) for regular attack
        self.special_attack = special_attack  # Optional function for special abilities
        self.special_attack_chance = special_attack_chance  # configurable per enemy
        self.death_effect = death_effect    # Optional function for death effects
        self.description = description      # Description for flavor text
        self.exp_reward = exp_reward  # How much EXP the player gets for defeating this enemy

    def take_turn(self, player, enemies, defending=False):
        """
        Called when the enemy takes its turn in combat.
        Decides whether to use special attack or normal attack.

        Args:
            player: the Player instance to target
            enemies: list of Enemy instances (used by some specials)
            defending (bool): if True, player has chosen Defend this round
                              and will take half damage from normal attacks
        """
        messages = []

        # Roll for special attack first (if one is defined for this enemy)
        if self.special_attack and random.random() < self.special_attack_chance:
            # Standardized signature: special(enemy, player, enemies)
            messages += self.special_attack(self, player, enemies)
        else:
            # Use the basic attack (random damage within the enemy's range)
            dmg = random.randint(*self.attack)
            if defending:
                # If the player chose to defend, reduce damage by half (rounded down)
                dmg //= 2
            player.hp -= dmg
            messages.append(f"{self.name} strikes you for {dmg} damage!")

        messages.append("")
        return messages


# ==========================================
# Special Attacks for Enemies
# ==========================================

def apostle_buff(enemy, player, enemies):
    """
    Special attack for Apostles.
    Heals the enemy a small random amount.
    """
    messages = []
    # Find the ally with the lowest HP that’s still alive
    target = min([e for e in enemies if e.hp > 0], key=lambda e: e.hp)
    heal = random.randint(3, 6)
    target.hp = min(target.max_hp, target.hp + heal)
    messages.append(f"{enemy.name} chants a hymn, healing {target.name} for {heal} HP!")
    return messages

def priest_curse(enemy, player, enemies):
    """
    Special attack for High Priests.
    Reduces the player's sanity.
    """
    messages = []
    dmg = random.randint(4, 8)
    player.sanity = max(0, player.sanity - dmg)
    messages.append(f"{enemy.name} invokes a dark curse!")
    messages.append(f"Your sanity is reduced by {dmg}!")
    return messages

def Rite_of_reclamation(enemy, player, enemies):
    """
    Special attack for Anatomist.
    Does damage to the player and heals itself.
    """
    messages = []
    dmg = random.randint(4, 10)
    player.hp -= dmg
    heal = dmg
    enemy.hp = min(enemy.max_hp, enemy.hp + heal)
    messages.append(f"{enemy.name} strikes you for {dmg} damage!")
    messages.append(f"The Anatomist licks its blade clean and regains {heal} HP!")
    return messages

def unstable_form_death(enemy, player, enemies):
    """
    Special attack for Starborn.
    as it dies it damages the player.
    """
    dmg = random.randint(4, 10)
    player.hp -= dmg
    return f"{enemy.name} collapses, its unstable form tearing itself apart and striking you for {dmg} damage!"
    
def whisperer_psychic(enemy, player, enemies):
    """
    Special attack for Whisperers.
    Deals minor HP and sanity damage.
    """
    messages = []
    dmg = random.randint(5, 10)
    player.hp -= dmg
    player.sanity = max(0, player.sanity - 2)
    messages.append(f"{enemy.name} whispers forbidden truths...")
    messages.append(f"You take {dmg} psychic damage and lose 2 sanity!")
    return messages

def Call_of_the_Hollow(enemy, player, enemies):
    """
    Special attack for Dirge of the Deep.
    - Summons 1 "Drowned fragment" if none exists in the current round list.
    - If a fragment exists (alive or dead) in this round's list, Dirge attacks instead.

    Note: Dead fragments are cleaned up at end-of-round in the combat loop,
    preventing immediate same-round re-summoning after a kill.
    """
    messages = []

    # Block summoning if any fragment (alive or dead) is present this round.
    fragment_exists_this_round = any(e.name == "Drowned fragment" for e in enemies)

    if not fragment_exists_this_round:
        messages.append(f"{enemy.name} whispers forbidden truths...")
        fragment = create_enemy("Drowned fragment")
        enemies.append(fragment)
        messages.append("A Drowned fragment slithers into existence!")
    else:
        # If a fragment already exists this round, Dirge attacks instead of summoning.
        dmg = random.randint(3, 8)
        player.hp -= dmg
        messages.append(f"{enemy.name} lashes out for {dmg} damage!")

    return messages


def abomination_crush(enemy, player, enemies):
    """
    Special attack for Abominations.
    Deals high HP damage.
    """
    messages = []
    dmg = random.randint(8, 14)
    player.hp -= dmg
    messages.append(f"{enemy.name} crushes you with monstrous strength for {dmg} damage!")
    return messages


# ==========================================
# Enemy Library
# ==========================================

# This is a dictionary of all predefined enemies in the game.
# Each entry can be used to spawn a fresh copy of that enemy.
enemy_library = {
    # Difficulty 1: 
    "Tutorial": Enemy("Wounded Cultist", difficulty=1, hp=20, attack=(1, 3), description="Fanatical servant of the cult.", exp_reward=0),
    "Cultist": Enemy("Cultist", difficulty=1, hp=20, attack=(3, 6), description="Fanatical servant of the cult.", exp_reward=10),
    "Drowned fragment": Enemy("Drowned fragment", difficulty=1, hp=10, attack=(1, 5), description="A fragment of the drowned.", exp_reward=5),

    # Difficulty 2: 
    # Apostle: demonstrates an ally-targeting special (heals lowest-HP ally)
    # special_attack_chance=1 means it will always try to use the special each turn
    "Apostle": Enemy("Apostle", difficulty=2, hp=28, attack=(4, 7), special_attack=apostle_buff, 
                     special_attack_chance=0.3, description="Disciple that heals itself with hymns.", exp_reward=20),

    # Difficulty 3: 
    "High Priest": Enemy("High Priest", difficulty=3, hp=35, attack=(5, 9), special_attack=priest_curse,
                         special_attack_chance=0.3, description="Leader who curses your sanity.", exp_reward=30),
    "Anatomist": Enemy("Anatomist", difficulty=3, hp=40, attack=(5, 10), special_attack=Rite_of_reclamation,
                         special_attack_chance=1, description="It works by intuition, hands guided by a voice only it can hear.", exp_reward=30),
    "Starborn": Enemy("Starborn", difficulty=3, hp=12, attack=(4, 10), death_effect=unstable_form_death,
                         description="Once humans, now hollow vessels etched with constellations. Fragile, but every death tears a hole in reality.", exp_reward=30),

    # Difficulty 4:                     
    "Whisperer": Enemy("Whisperer", difficulty=4, hp=30, attack=(4, 10), special_attack=whisperer_psychic,
                       special_attack_chance=0.3, description="Maddening voice that eats away at your mind.", exp_reward=40),
    "Dirge of the Deep": Enemy("Dirge of the Deep", difficulty=4, hp=34, attack=(3, 8), special_attack=Call_of_the_Hollow,
                       special_attack_chance=1, description="A veiled entity that calls the void to your location.", exp_reward=35),

    # Difficulty 5: 
    "Abomination": Enemy("Abomination", difficulty=5, hp=50, attack=(6, 12), special_attack=abomination_crush,
                         special_attack_chance=0.3, description="Horrific mutation of flesh and shadow.", exp_reward=50),
}

# ==========================================
# Helper function to create fresh enemy instances
# ==========================================

def create_enemy(name):
    """
    Creates a new instance of an enemy based on the template in the enemy library.
    This ensures each enemy starts with full HP and default stats.
    """
    template = enemy_library[name]
    return Enemy(
        template.name,
        template.difficulty,
        template.max_hp,  # Reset HP to full
        template.attack,
        special_attack = template.special_attack,
        special_attack_chance= template.special_attack_chance,
        death_effect = template.death_effect,
        description = template.description,
        exp_reward = template.exp_reward
    )