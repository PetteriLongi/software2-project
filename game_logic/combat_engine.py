"""
combat_engine.py - Turn-based combat engine for web version

Migration changes:
- Removed all input()/print() calls
- Combat state stored as dict (can be serialized to session)
- Actions return results as dicts for API responses
- No loops - each API call processes one player action
- Combat state includes turn counter, enemies, player status, logs
"""

import random
from .enemies import Enemy, create_enemy


class CombatState:
    """
    Represents the current state of a combat encounter.
    This is serializable and can be stored in session.
    """
    def __init__(self, player, enemy_names):
        """
        Initialize combat state.
        
        Args:
            player: Player instance
            enemy_names: List of enemy names from enemy_library
        """
        self.turn_counter = 1
        self.enemies = [create_enemy(name) for name in enemy_names]
        self.defending = False
        self.player_log = []
        self.enemy_log = []
        self.combat_active = True
        self.victory = False
        
    def to_dict(self, player):
        """Convert combat state to JSON-serializable dict"""
        return {
            'turn_counter': self.turn_counter,
            'enemies': [e.to_dict() for e in self.enemies],
            'defending': self.defending,
            'player_log': self.player_log,
            'enemy_log': self.enemy_log,
            'combat_active': self.combat_active,
            'victory': self.victory,
            'player_hp': player.hp,
            'player_max_hp': player.max_hp,
            'player_sanity': player.sanity,
            'player_max_sanity': player.max_sanity
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Reconstruct CombatState from serialized session data.
        
        Args:
            data: dict from session['combat']
        
        Returns:
            CombatState: Reconstructed instance with all state restored
        """
        instance = cls.__new__(cls)
        instance.turn_counter = data['turn_counter']
        instance.enemies = [Enemy.from_dict(e) for e in data['enemies']]
        instance.defending = data['defending']
        instance.combat_active = data['combat_active']
        instance.victory = False
        instance.player_log = []
        instance.enemy_log = []
        return instance
    
    def check_combat_end(self, player):
        """
        Check if combat should end (player dead or all enemies dead).
        Updates combat_active and victory flags.
        """
        if player.hp <= 0:
            self.combat_active = False
            self.victory = False
            return True
            
        living_enemies = [e for e in self.enemies if e.hp > 0]
        if not living_enemies:
            self.combat_active = False
            self.victory = True
            return True
            
        return False


def process_player_action(combat_state, player, action, target_index=None, item_index=None):
    """
    Process a single player action and advance combat state.
    
    Args:
        combat_state: CombatState instance
        player: Player instance
        action: str - 'attack', 'defend', 'manifest', 'use_item', 'reload'
        target_index: int - index of enemy in combat_state.enemies (for attacks)
        item_index: int - index in player.manifestations or player.inventory
    
    Returns:
        dict: {
            'success': bool,
            'messages': list of str,
            'turn_consumed': bool,
            'combat_state': dict (serialized CombatState),
            'combat_ended': bool,
            'victory': bool (if combat_ended)
        }
    """
    result = {
        'success': True,
        'messages': [],
        'turn_consumed': False,
        'combat_ended': False,
        'victory': False,
        'sfx': None
    }
    
    # Clear previous logs
    combat_state.player_log = []
    combat_state.enemy_log = []
    
    living_enemies = [e for e in combat_state.enemies if e.hp > 0]
    
    # ========================================
    # ATTACK ACTION
    # ========================================
    if action == 'attack':
        if target_index is None or target_index < 0 or target_index >= len(living_enemies):
            result['success'] = False
            result['messages'].append("Invalid target!")
            return result
            
        target = living_enemies[target_index]
        result['turn_consumed'] = True
        
        # Resolve attack
        weapon = player.weapon
        if weapon:
            weapon_name = weapon.name
            if getattr(weapon, "weapon_type", "melee") == "gun":
                # Gun attack
                if getattr(weapon, "current_mag", 0) > 0:
                    dmg = random.randint(*weapon.attack_range)
                    weapon.current_mag -= 1
                    reserve = player.ammo.get(getattr(weapon, "ammo_type", "bullets"), 0)
                    combat_state.player_log.append(
                        f"You fire {weapon.name}! ({weapon.current_mag}/{weapon.mag_size} in mag, {reserve} in reserve)"
                    )
                    result['sfx'] = getattr(weapon, 'sfx_attack', 'gun_fire')
                else:
                    reserve = player.ammo.get(getattr(weapon, "ammo_type", "bullets"), 0)
                    if reserve > 0:
                        combat_state.player_log.append("Click! Your magazine is empty. Reload first.")
                    else:
                        combat_state.player_log.append("Click! You have no ammo left.")
                    dmg = 0
            else:
                # Melee attack
                dmg = random.randint(*weapon.attack_range)
                result['sfx'] = getattr(weapon, 'sfx_attack', 'melee_swing')
        else:
            # Fists
            dmg = random.randint(*player.base_attack)
            weapon_name = "your fists"
            result['sfx'] = 'punch'
        
        # Apply damage
        if dmg > 0:
            target.hp -= dmg
            combat_state.player_log.append(f"You strike {target.name} with {weapon_name} for {dmg} damage!")
            
            # Check if enemy died
            if target.hp <= 0:
                combat_state.player_log.append(f"{target.name} is defeated!")
                
                # Award XP immediately
                exp_gained = target.exp_reward
                level_result = player.gain_exp(exp_gained)
                combat_state.player_log.append(f"You gained {exp_gained} EXP!")
                
                # Check if player leveled up
                if level_result.get('level_ups'):
                    for level_up in level_result['level_ups']:
                        combat_state.player_log.append(
                            f"You leveled up to level {level_up['new_level']}!"
                        )
                
                # Check for death effect
                death_result = target.apply_death_effect()
                if death_result['has_effect']:
                    player.hp -= death_result['damage']
                    combat_state.player_log.append(death_result['message'])
        
        combat_state.player_log.append("")
    
    # ========================================
    # DEFEND ACTION
    # ========================================
    elif action == 'defend':
        result['turn_consumed'] = True
        combat_state.defending = True
        combat_state.player_log.append("You brace yourself for the next attack...")
        combat_state.player_log.append("")
    
    # ========================================
    # MANIFEST ACTION
    # ========================================
    elif action == 'manifest':
        if item_index is None or item_index < 0 or item_index >= len(player.manifestations):
            result['success'] = False
            result['messages'].append("Invalid manifestation!")
            return result
        
        result['turn_consumed'] = True
        manifestation = player.manifestations[item_index]
        
        # Store manifestation name for audio/animation
        result['manifestation_used'] = manifestation.name
        
        # Check if self-targeting (like Hope)
        if getattr(manifestation, "target_type", "enemy") == "self":
            manifest_result = manifestation.use_skill(player, None)
            combat_state.player_log.extend(manifest_result['messages'])
            player.sanity = manifest_result['player_sanity']
            result['sfx'] = manifest_result.get('sfx')
        else:
            # Enemy targeting
            if target_index is None or target_index < 0 or target_index >= len(living_enemies):
                result['success'] = False
                result['messages'].append("Invalid target for manifestation!")
                return result
            
            target = living_enemies[target_index]
            manifest_result = manifestation.use_skill(player, target)
            
            if manifest_result['success']:
                combat_state.player_log.extend(manifest_result['messages'])
                player.sanity = manifest_result['player_sanity']
                result['sfx'] = manifest_result.get('sfx')
                
                # Check if enemy died
                if target.hp <= 0:
                    combat_state.player_log.append(f"{target.name} is defeated!")
                    
                    # Award XP immediately
                    exp_gained = target.exp_reward
                    level_result = player.gain_exp(exp_gained)
                    combat_state.player_log.append(f"You gained {exp_gained} EXP!")
                    
                    # Check if player leveled up
                    if level_result.get('level_ups'):
                        for level_up in level_result['level_ups']:
                            combat_state.player_log.append(
                                f"You leveled up to level {level_up['new_level']}!"
                            )
            else:
                combat_state.player_log.append("Not enough sanity to use this manifestation!")
        
        combat_state.player_log.append("")
    
    # ========================================
    # RELOAD ACTION
    # ========================================
    elif action == 'reload':
        result['turn_consumed'] = True
        weapon = player.weapon
        
        if not weapon or getattr(weapon, "weapon_type", "melee") != "gun":
            combat_state.player_log.append("You are not wielding a firearm.")
            combat_state.player_log.append("")
        else:
            needed = max(0, weapon.mag_size - weapon.current_mag)
            if needed == 0:
                combat_state.player_log.append(f"{weapon.name}'s magazine is already full.")
                combat_state.player_log.append("")
            else:
                ammo_type = getattr(weapon, 'ammo_type', 'bullets')
                reserve = player.ammo.get(ammo_type, 0)
                
                if reserve <= 0:
                    combat_state.player_log.append(f"No {ammo_type} ammo in reserve to reload!")
                    combat_state.player_log.append("")
                else:
                    to_load = min(needed, reserve)
                    weapon.current_mag += to_load
                    player.ammo[ammo_type] = reserve - to_load
                    
                    combat_state.player_log.append(
                        f"You reload {weapon.name}: +{to_load} rounds ({weapon.current_mag}/{weapon.mag_size})."
                    )
                    combat_state.player_log.append(f"Reserve left: {player.ammo[ammo_type]}")
                    
                    if to_load < needed:
                        combat_state.player_log.append(f"Partial reload: not enough {ammo_type} to fill the magazine.")
                    if player.ammo[ammo_type] == 0:
                        combat_state.player_log.append(f"You're out of {ammo_type} after reloading.")
                    
                    combat_state.player_log.append("")
                    result['sfx'] = getattr(weapon, 'sfx_reload', 'reload')
    
    else:
        result['success'] = False
        result['messages'].append("Unknown action!")
        return result
    
    # ========================================
    # ENEMY TURN (if turn consumed)
    # ========================================
    if result['turn_consumed']:
        living_enemies = [e for e in combat_state.enemies if e.hp > 0]
        
        for enemy in living_enemies:
            enemy_result = enemy.take_turn(player_defending=combat_state.defending)
            
            # Apply damage and sanity loss
            player.hp -= enemy_result['damage']
            player.sanity = max(0, player.sanity - enemy_result['sanity_loss'])
            
            # Handle special enemy effects
            if 'heal_amount' in enemy_result:
                # Ally healing (find lowest HP ally)
                allies = [e for e in living_enemies if e != enemy and e.hp > 0]
                if allies:
                    lowest = min(allies, key=lambda e: e.hp)
                    lowest.hp = min(lowest.max_hp, lowest.hp + enemy_result['heal_amount'])
            
            if 'summon_attempt' in enemy_result:
                # Handle summoning (e.g., Dirge)
                fragment_exists = any(e.name == enemy_result['summon_name'] for e in combat_state.enemies)
                if not fragment_exists:
                    summoned = create_enemy(enemy_result['summon_name'])
                    combat_state.enemies.append(summoned)
                    combat_state.enemy_log.append("A Drowned fragment slithers into existence!")
                else:
                    # Fallback attack
                    player.hp -= enemy_result['fallback_damage']
                    combat_state.enemy_log.append(f"{enemy.name} lashes out for {enemy_result['fallback_damage']} damage!")
            
            combat_state.enemy_log.extend(enemy_result['messages'])
        
        # Reset defending after enemy turn
        combat_state.defending = False
        combat_state.turn_counter += 1
    
    # ========================================
    # CHECK COMBAT END
    # ========================================
    if combat_state.check_combat_end(player):
        result['combat_ended'] = True
        result['victory'] = combat_state.victory
        
        if result['victory']:
            combat_state.player_log.append("Victory! All enemies defeated!")
    
    # Combine logs into messages
    result['messages'] = combat_state.player_log + combat_state.enemy_log
    result['combat_state'] = combat_state.to_dict(player)
    
    return result
