# ==========================================
# IMPORTS: BRINGING IN OTHER MODULES
# ==========================================

# Combat
from .combat import combat
from .combat_actions import select_target, resolve_attack, handle_manifestations, handle_inventory, reload_gun

# Player
from .player import Player

# SFX
from .music import load_sfx, play_sfx

# Manifestations
from .manifestations import manifestation_library, Manifestation

# Enemies
from .enemies import enemy_library, create_enemy

# Items
from .items import weapon_library, consumable_library, add_item_to_inventory, add_weapon_to_inventory, LoreItem

# Music
from .music import play_music, stop_music, set_volume

# UI
from .ui import render_inventory, draw_status_bars_rich, draw_status_bars_ascii, ui_print, level_up_display, colouring
from .ui import display_hud

# Writing Effects
from .writing_effects import print_typewriter, flicker_line, dim_text, red_flash, print_glitch

# SFX Loader
from .sfx_loader import load_sfx

# Story
from .story import intro, dark_hallway, encounter_with_man, conduit, awakening, shadows_stir, ezekiels_warning, combat_scene, aftermath, final_words
from .story import run_story, STORY_MAP, make_choice, wait_for_input, print_typewriter

# Doom Clock
from Doomclock.doomclock import DoomClock
