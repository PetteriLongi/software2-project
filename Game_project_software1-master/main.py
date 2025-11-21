"""
main.py - Demo entry point for the Lovecraft-inspired terminal RPG.

Instructions:
1. Run this file to play the demo encounters.
2. The script sets up the player, prints a short narrative intro, gives starter gear,
   and runs two combat encounters using helpers from the `game/` package.
"""

import shutil
import pygame
import sys


# ==========================================
# LOCAL IMPORTS
# ==========================================
from game import (
    combat, reload_gun,
    Player,
    manifestation_library,
    create_enemy,
    add_weapon_to_inventory, add_item_to_inventory,
    play_music, stop_music,
    print_typewriter,
    ui_print, display_hud, LoreItem,
    intro,
    run_story, STORY_MAP, make_choice, wait_for_input
)
from Doomclock.doomclock import doom_clock
from Database.menu_ui.menu import game_loop, main_menu
from Database.services import start_new_run
# UI capability flag (for hinting Rich availability to the user)
from game.ui import RICH_AVAILABLE
# Getting all the sound files from sfx_loader and registering them
from game.sfx_loader import register_all_sfx

#print("Manifestations available:", list(manifestation_library.keys()))

def start_story():
    # ==========================================
    # PLAYER SETUP
    # ==========================================
    # Create our player character.
    unlocked_manifestations = []
    player = Player("Hero", unlocked_manifestations)
    # Attach DoomClock to player for easy access
    player.doom_clock = doom_clock
    # Determine terminal width for nicer wrapping (fallback to 80)
    term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
    wrap_width = max(50, min(100, term_width))

    # Hint Rich availability (so users understand UI mode)
    if not RICH_AVAILABLE:
        print("\nNote: Rich not detected. Using ASCII UI. Install 'rich' for enhanced inventory and status visuals.")
    else:
        print("\nRich UI enabled. Enjoy enhanced inventory and status visuals.\n")

    # ==========================================
    # NARRATIVE 
    # ==========================================
    add_weapon_to_inventory(player, "AR-15", current_mag=13)
    add_weapon_to_inventory(player, "MP7", current_mag=14)
    add_weapon_to_inventory(player, "Basic dagger")
    add_item_to_inventory(player, "rifle ammo", 10)   
    add_item_to_inventory(player, "submachine ammo", 54)
    add_item_to_inventory(player, "pistol ammo", 13)
    play_music("Music/ambience/Piano_suspense.mp3", volume=0.12, loop=True)

    # ==========================================
    # INTRO
    # ==========================================
    player.manifestations.append(manifestation_library["Fear"])
    intro()
    state = start_new_run()
    player.markka = getattr(state, "markka", 0)

    display_hud(player, doom_clock)
    player.gain_exp(50)
    stop_music()

    def play_chapter_two():
        run_story("2_conduit", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    # Here we can give rewards afther the combat encounter

        run_story("2_conduit.aftermath", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
        player.manifestations.append(manifestation_library["Hope"])

    def play_chapter_three():
        run_story("3_conduit", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    #Here we can give combat rewards

        run_story("3_first_encounter.aftermath", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    #Here we should add the manifestation unlocked here
        player.manifestations.append(manifestation_library["Resentment"])

        run_story("defiance_anatomist.combat", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    # Here we can give rewards the story cuts after the bossfight and below it continues after it 

        run_story("anatomist.aftermath", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)

    def play_chapter_four():
        run_story("4_conduit", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    #Here we can give combat rewards

        run_story("4_conduit.encounter", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    # Here we should add the manifestation unlocked here
        player.manifestations.append(manifestation_library["Rage"])

        run_story("4_conduit.defy", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    # Here we can give rewards the story cuts after the bossfight and below it continues after it 

        run_story("4_conduit.aftermath", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)

    def play_chapter_five():
        run_story("5_conduit", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)

    chapter_scripts = [
        (1, play_chapter_two),
        (2, play_chapter_three),
        (3, play_chapter_four),
        (4, play_chapter_five),
    ]

    next_chapter_index = 0

    while True:
        event = game_loop(player, state)
        if event is None:
            continue
        if event.event_type == "quit":
            return

        while next_chapter_index < len(chapter_scripts):
            required_conduits, chapter_fn = chapter_scripts[next_chapter_index]
            if state.conduits_found >= required_conduits:
                chapter_fn()
                next_chapter_index += 1
            else:
                break



if __name__ == "__main__":
    play_music("Music/ambience/Whispers_Beyond_the_Veil.mp3", volume=0.12, loop=True)
    register_all_sfx()
    main_menu(start_story)
    sys.exit(0)


    

    # ==========================================
    # IMPORTANT: EVERYTHING UNDER THIS COMMENT IS JUST TO SHOW HOW TO CALL THESE FUNCTIONS
    #            AND FOR TESTING PURPOSES
    #            NEEDS TO BE REWRITTEN COMPLETELY LATER TO BUILD THE GAME PROPERLY
    # ==========================================
    # ==========================================
    # STARTING GEAR (FEEL FREE TO TWEAK)
    # ==========================================
    # Give the player some starting gear and items to try out in combat.
    # You can add more here to experiment.

    add_weapon_to_inventory(player, "Basic dagger")
    add_weapon_to_inventory(player, "Sword")
    add_item_to_inventory(player, "Small Health Potion")
    add_item_to_inventory(player, "Large Health Potion")
    add_item_to_inventory(player, "Small Sanity Potion")
    add_item_to_inventory(player, "Large Sanity Potion")
    add_item_to_inventory(player, "pistol ammo", 10)               # AR-15 ammo reserve
    add_item_to_inventory(player, "rifle ammo", 10)
    add_item_to_inventory(player, "submachine ammo", 10)
    add_weapon_to_inventory(player, "AR-15", current_mag=13)        # Starts with a full magazine
    add_weapon_to_inventory(player, "MP7", current_mag=14)

    run_story("2_conduit", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)
    player.manifestations.append(manifestation_library["Hope"])
    add_item_to_inventory(player, "Large Health Potion", 2)
    run_story("whispering_conduit.defiance", player, STORY_MAP, print_typewriter, wait_for_input, make_choice)

    # Pause so the player can read the setup text above (optional)
    #pygame.mixer.music.fadeout(2000) #this causes a 2, second delay before the combat starts
    input("\nPress enter to continue...")
   
    # ==========================================
    # ENCOUNTER 1
    # ==========================================
    # Prepare the first combat encounter (you can add up to 3 enemies in this list)
    enemies1 = [create_enemy("Anatomist")]
    # Start combat with background music for atmosphere
    play_music("Music/combat/Anxiety.mp3", volume=0.12)
    combat(player, enemies1)
    # Fade out the music a bit after combat ends
    pygame.mixer.music.fadeout(2000)
    #stop_music()

    # ==========================================
    # ENCOUNTER 2
    # ==========================================
    # Second encounter setup
    print("\nIt seems you have found something")
    add_weapon_to_inventory(player, "Old revolver")  # Comes with a full magazine
    ui_print('oh no there are even more guys', 'red')

    reload_gun(player, consume_turn=False) # A way to reload equipped gun outside of combat by calling this function

    input("\nPress enter to continue...")

    enemies2 = [create_enemy('Apostle'), create_enemy('High Priest'), create_enemy('Cultist')]
    play_music("Music/combat/Behind_you.mp3", volume=0.12)
    combat(player, enemies2)
    pygame.mixer.music.fadeout(2000)

