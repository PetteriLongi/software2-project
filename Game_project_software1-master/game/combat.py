"""
combat.py - Turn-based combat loop and menus

Usage:
    from game.combat import combat

Quick start:
    from game.player import Player
    from game.enemies import create_enemy
    from Doomclock.doomclock import doom_clock

    player = Player("Hero", unlocked_manifestations=[])
    enemies = [create_enemy("Cultist"), create_enemy("Apostle")]
    combat(player, enemies, doom_clock)

What this module does:
- Runs the round-based combat loop
- Presents the action menu each turn:
  1) Attack   2) Defend   3) Manifest   4) Inventory   5) Reload
- Resolves enemy turns and special attacks
- Tracks HP/Sanity and prints a colorized turn log

Rendering (UI):
- Status bars, inventory menus, and HUD widgets are delegated to `game/ui.py`.
  - If Rich is available, the game uses the eldritch Rich layouts.
  - Otherwise, ASCII fallback utilities from `game/ui_elements/` provide output.

End conditions:
- Combat ends when all enemies are defeated (victory) or the player HP reaches 0 (defeat).
"""
import sys
import random

from game.writing_effects import red_flash

from .items import Weapon, Item, Consumable
from .ui import exp_hint, colouring
from .ui import draw_status_bars_ascii
from .ui import RICH_AVAILABLE, draw_status_bars_rich
from .combat_actions import select_target, resolve_attack, handle_manifestations, handle_inventory, reload_gun
from .ui import display_hud
from Doomclock.doomclock import doom_clock
from Database.menu_ui.menu import show_help

# ==========================================
# MAIN COMBAT LOOP
# ==========================================
# The combat loop runs in rounds (turns). Each round, the player can choose an action.
# After certain actions (Attack/Defend/Manifest/Reload), enemies take their turns.
# Just opening the Inventory and backing out does NOT spend a turn.

def combat(player, enemies_list, doom_clock):
    """
    Handles turn-based combat between the player and a list of enemies.

    Features:
        - Player actions: Attack, Defend, Manifest, Inventory
        - Enemy actions and special attacks
        - Turn log display
        - HP/Sanity tracking
    """
    defending = False   # When True, the next enemy hit does half damage
    max_name_length = max(len(e.name) for e in enemies_list)
    turn_counter = 1

    print(f"\n\033[95m--- COMBAT: {', '.join([e.name for e in enemies_list])} APPEARS! ---\033[0m")

    while player.hp > 0 and any(e.hp > 0 for e in enemies_list):
        # These logs gather all messages for this round and are printed at the end
        player_log = []
        enemy_log = []
        # If False, we skip enemy actions and do not advance the round counter
        turn_consumed = False

        # --- Turn Header ---
        print(f"\n\033[96m--- Turn {turn_counter} ---\033[0m")

        # --- Display status bars for player and enemies ---
        if RICH_AVAILABLE and draw_status_bars_rich:
            draw_status_bars_rich(player, enemies_list)
        else:
            # Delegate ASCII status bar rendering to UI module
            draw_status_bars_ascii(player, enemies_list)

        # At the start of a turn, remove defeated enemies.
        # This ensures summoners (like Dirge) cannot immediately re-summon in
        # the same round a minion was killed.
        enemies_list[:] = [e for e in enemies_list if e.hp > 0]

        # --- Action menu ---
        # Type the number and press Enter to perform an action
        print("\nChoose your action:")
        print("1. Attack")
        print("2. Defend")
        print("3. Manifest")
        print("4. Inventory")
        print("5. Reload")
        print("\nH. Help")
        print("Write: escape to quit")
        choice = input("> ")

        # ========================================
        # PLAYER TURN: ATTACK
        # ========================================

        if choice == "1":
            # Physical attack against a selected enemy target
            turn_consumed = True
            target = select_target(enemies_list, player_log)
            if target:
                resolve_attack(player, target, player_log)


        # ========================================
        # PLAYER TURN: DEFEND
        # ========================================

        elif choice == "2":
            # Reduce damage from the next enemy hit in this round
            turn_consumed = True
            defending = True
            player_log.append(colouring(
                "You brace yourself for the next attack...",
                "blue"
            ))
            player_log.append("")



        # ========================================
        # PLAYER TURN: MANIFEST
        # ========================================

        elif choice == "3":  # Use a Manifestation (special ability)
            turn_consumed = handle_manifestations(player, enemies_list, player_log)


        # ========================================
        # PLAYER TURN: INVENTORY
        # ========================================

        elif choice == "4":
            turn_consumed, msgs = handle_inventory(player)
            player_log.extend(msgs)


        # ========================================
        # PLAYER TURN: RELOAD
        # ========================================

        elif choice == "5":
            # Reload the currently equipped firearm (if any)
            turn_consumed, msgs = reload_gun(player, consume_turn=True)
            player_log.extend(msgs)


        # ========================================
        # PLAYER TURN: HELP
        # ========================================
        elif choice.lower() == "h":
            show_help()
            continue
        
        # ========================================
        # PLAYER TURN: QUIT
        # ========================================
        elif choice.lower() == "escape":
            print("You ran away from the enemies and got stabbed in the back, coward.")
            sys.exit()
        
        # ========================================
        # ENEMY TURNS (only if player action consumed the turn)
        # ========================================

        if turn_consumed:
            for enemy in enemies_list:
                if enemy.hp <= 0:
                    # Call the death effect if it exists
                    if getattr(enemy, "death_effect", None) and not getattr(enemy, "death_effect_called", False):
                        try:
                            msgs = enemy.death_effect(enemy, player, enemies_list)
                            if msgs:
                                if isinstance(msgs, list):
                                    for m in msgs:
                                        player_log.append(m)
                                else:
                                    player_log.append(str(msgs))
                                player_log.append("")
                        except Exception:
                            pass
                        setattr(enemy, "death_effect_called", True)
                        
                    if not getattr(enemy, "exp_awarded", False):
                        player.gain_exp(enemy.exp_reward)
                        enemy.exp_awarded = True
                    continue

                enemy_log.append(colouring(f"{enemy.name} prepares to act!", "red"))
                msgs = enemy.take_turn(player, enemies_list, defending)
                match msgs:
                    case str():
                        enemy_log.append(msgs)
                    case list():
                        enemy_log.extend(msgs)
                    case _ if msgs:
                        enemy_log.append(str(msgs))
                enemy_log.append("")
                defending = False

        # ========================================
        # AMBIENT EXP HINT (WHISPER)
        # ========================================
        try:
            ratio = player.exp / max(getattr(player, "exp_to_next", 1), 1)
        except Exception:
            ratio = 0.0

        # The closer to level up, the more frequent the whisper
        # Base 12% chance + up to 20% as ratio approaches 1.0
        if random.random() < 0.15 + 0.50 * max(0.0, min(1.0, ratio)):
            player_log.append("") #spacer
            player_log.append(colouring(f"[Whisper] {exp_hint(ratio)}", "magenta"))
        

        # ========================================
        # DISPLAY TURN LOG
        # ========================================
        turn_log = player_log + [""] + enemy_log
        print(colouring("\n" + "=" * 50, "magenta"))
        for entry in turn_log:
            print(entry)
        print(colouring("=" * 50, "magenta"))


        # ========================================
        # CHECK WIN / LOSS
        # ========================================
        if turn_consumed and all(e.hp <= 0 for e in enemies_list):
            print(colouring("\nAll enemies have been defeated! Victory is yours!", "green"))
            if doom_clock is not None:
                doom_clock.countdown(1, player=None, enemies=None, log=None)
                try:
                    display_hud(player, doom_clock)
                except Exception:
                    pass
            return True

        if turn_consumed:
            turn_counter += 1

    # Player has been defeated
    if player.hp <= 0:
        print(colouring("\nYour body collapses... The cult claims another victim.\n", "red"))
        red_flash("It seems this is all you amounted to in the end...", flashes=10, on_time=0.5, off_time=0.5)
        return sys.exit()
