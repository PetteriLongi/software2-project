# conduit_game/ui/menu.py
from Database.config import RunState
from Database.services import travel_to_index, rest
from Database.services import TravelResult
from Database.menu_ui.travel_board import show_travel_options
from game.music import play_music
from game.ui import colouring, ui_print
from Database.FetchDB import coords, distance_km
from rich.console import Console
from rich.table import Table
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
from game.combat import handle_inventory
from game.player import Player
from Doomclock.doomclock import doom_clock
import shutil, sys
#from ..repository import create_bloody_note, fetch_random_airports_excl_hel
console = Console()


def show_commands():
    play_music("Music/ambience/Whispers_Beyond_the_Veil.mp3", volume=0.12, loop=True)
    ui_print("Choose: [1] Travel  [2] Inventory  [3] Rest  [H] Help  [Q] Quit", "bold cyan")

def show_help():
    ui_print("""
HELP

Game Menu
  [1] Travel      - opens the terminal board (choose 1..10)
  [2] Inventory   - shows markka, bullets, levels, doomclock counter, weapons, consumables, magazine states.
  [3] Rest        - fully restore HP and Sanity and reloads all magazines
  [H] Help        - this help
  [Q] Quit        - quits the game
  [Space bar]     - Skip current line. The rest of that line prints instantly, then normal speed resumes on the next line.
  [Enter]         - Print the rest of the entire text instantly.

Combat Menu
  [1] Attack      - physical strike
  [2] Defend      - reduce next damage
  [3] Manifest    - use a special skill at the cost of sanity
  [4] Inventory   - shows markka, bullets, levels, doomclock counter, weapons, consumables, magazine states.
  [5] Reload      - for firearms. reloads the current magazine
  [H] Help        - this help

Notes
  • Start at HEL; HEL is not among the 10 options; you cannot return to HEL.
  • 10 random airports; 5 are secret conduits.
  • You may revisit an airport only if a conduit there is still open.
  • Travel cost depends on distance.
""", "purple")

@dataclass
class MenuEvent:
    event_type: str
    travel_result: Optional[TravelResult] = None
    conduits_found: int = 0
    conduits_closed: int = 0


def game_loop(player: Player, state: RunState) -> Optional[MenuEvent]:
    while True:
        # Keep player currency in sync with the run state before showing options
        try:
            player.markka = state.markka
        except AttributeError:
            # Player may not have markka attribute in legacy saves; ignore silently
            pass
        show_commands()
        cmd = input("> ").strip().lower()

        if cmd == "q":
            ui_print("The world darkens. Farewell.", "purple")
            return MenuEvent(event_type="quit")

        if cmd == "h":
            show_help()
            continue

        if cmd == "3":
            ui_print(rest(state, player))
            setattr(player, "markka", state.markka)
            continue

        if cmd == "2":
            setattr(player, "markka", state.markka)
            handle_inventory(player)
            continue

        if cmd == "1":
            show_travel_options(state)
            sel = input("Go to (1-10): ").strip()
            if sel.isdigit():
                idx = int(sel)
                result = travel_to_index(state, idx)
                setattr(player, "markka", state.markka)
                ui_print(result.message)
                if result.conduit_found:
                    ui_print("A conduit has been discovered here. The story deepens.", "yellow")
                if result.conduit_closed:
                    ui_print("The conduit is sealed. A new chapter awaits.", "green")
                if result.conduit_found or result.conduit_closed:
                    setattr(player, "markka", state.markka)
                    return MenuEvent(
                        event_type="conduit_closed" if result.conduit_closed else "conduit_found",
                        travel_result=result,
                        conduits_found=state.conduits_found,
                        conduits_closed=state.conduits_closed,
                    )
            else:
                ui_print("Please enter a number between 1 and 10.", "red")
            continue

        ui_print("Unknown command. Use 1,2,3,H, or Q.", "red")

# --- Inventory ---

def show_inventory(state: RunState):
    print("\n=== INVENTORY ===")
    print(f"Markka: {state.markka}")
    print(f"HP: {state.hp} | Sanity: {state.sanity}")

    # Display the bloody note if it exists in inventory
    if state.inventory:
        console.print("\n[bold red]BLOODY NOTE:[/bold red]")
        console.print(state.inventory[0])

    cur = coords(state.current_lat, state.current_lon)

#==================
# --- MAIN MENU ---
#==================
def main_menu(on_start_game):
    # Get terminal dimensions
    term_width = shutil.get_terminal_size(fallback=(80, 24)).columns

    def center_text(text):
        """Center text within terminal width"""
        if len(text) >= term_width:
            return text
        padding = (term_width - len(text)) // 2
        return " " * padding + text

    while True:
        # Create the banner
        banner_lines = [
            " ",
            " ██▀███   ██▓▄▄▄█████▓▓█████   ██████     ▒█████    █████▒   ▄▄▄█████▓ ██▀███   ▄▄▄       ███▄    █   ██████  ██▓▄▄▄█████▓",
            "▓██ ▒ ██▒▓██▒▓  ██▒ ▓▒▓█   ▀ ▒██    ▒    ▒██▒  ██▒▓██   ▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄     ██ ▀█   █ ▒██    ▒ ▓██▒▓  ██▒ ▓▒",
            "▓██ ░▄█ ▒▒██▒▒ ▓██░ ▒░▒███   ░ ▓██▄      ▒██░  ██▒▒████ ░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ▓██  ▀█ ██▒░ ▓██▄   ▒██▒▒ ▓██░ ▒░",
            "▒██▀▀█▄  ░██░░ ▓██▓ ░ ▒▓█  ▄   ▒   ██▒   ▒██   ██░░▓█▒  ░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██ ▓██▒  ▐▌██▒  ▒   ██▒░██░░ ▓██▓ ░ ",
            "░██▓ ▒██▒░██░  ▒██▒ ░ ░▒████▒▒██████▒▒   ░ ████▓▒░░▒█░         ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒██░   ▓██░▒██████▒▒░██░  ▒██▒ ░ ",
            "░ ▒▓ ░▒▓░░▓    ▒ ░░   ░░ ▒░ ░▒ ▒▓▒ ▒ ░   ░ ▒░▒░▒░  ▒ ░         ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░▓    ▒ ░░   ",
            "  ░▒ ░ ▒░ ▒ ░    ░     ░ ░  ░░ ░▒  ░ ░     ░ ▒ ▒░  ░             ░      ░▒ ░ ▒░  ▒   ▒▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░ ▒ ░    ░    ",
            "  ░░   ░  ▒ ░  ░         ░   ░  ░  ░     ░ ░ ░ ▒   ░ ░         ░        ░░   ░   ░   ▒      ░   ░ ░ ░  ░  ░   ▒ ░  ░      ",
            "   ░      ░              ░  ░      ░         ░ ░                         ░           ░  ░         ░       ░   ░           ",
            " ",
        ]
        for line in banner_lines:
            ui_print(center_text(line), "purple")

        # Print centered separator and options
        separator = "=" * min(60, term_width - 4)  # Don't exceed terminal width
        ui_print(center_text(separator), "purple")

        menu_options = [
            " [1] Descend into the Unknown (New Game)",
            " [2] Whispers of Guidance (Help)",
            " [3] Escape the Void (Exit)"
        ]

        for option in menu_options:
            ui_print(center_text(option))

        ui_print(center_text(separator), "purple")

        # Center the input prompt (without centering the actual input)
        prompt = "Choose your fate (1-3): "
        choice = input(center_text(prompt) + " ")

        if choice == "1":
            on_start_game()
            break

        elif choice == "2":
            show_help()

        elif choice == "3":
            ui_print(center_text("\nThe void consumes you... Farewell.\n"), "purple")
            sys.exit()

        else:
            ui_print(center_text("The cosmos does not understand your choice... Try again."), "red")