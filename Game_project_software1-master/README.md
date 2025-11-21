Lovecraft-inspired, terminal-based, turn-based RPG (Python)

Battle cultists and abominations using melee weapons, firearms with magazines and ammo reserves, and eldritch manifestations that consume Sanity. 
Travel around the world with a enviromentally friendly Electric airplane!

**Database prerequisite (MariaDB)**

This game requires a local MariaDB database for the travel/airport/conduit data.
You’ll install MariaDB, create a schema, import the dataset, and set credentials the game will use.

Database Setup (MariaDB) — Required
**1) Install MariaDB and a GUI client**

MariaDB Server (local) – default port 3306
https://mariadb.org/download/

HeidiSQL (Windows GUI) – optional but recommended
https://www.heidisql.com/download.php

You can use any MySQL/MariaDB client; HeidiSQL instructions are below.

2) Create a database & user (with HeidiSQL)

Open HeidiSQL → create a New session → host: 127.0.0.1, user: your root user (or an admin), connect.

Right-click the server → Create new → Database…

Name it (e.g.) flightgame

Collation: utf8mb4_general_ci (or utf8mb4_0900_ai_ci if available)

With the server selected, open Users tab → Add:

User: conduit_user

Host: localhost

Password: set a password (e.g. conduit_pass)

Database-specific privileges: grant ALL on flightgame (or at least SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX)

Save.

**3) Import the dataset**

In the repo you’ll find something like Data/flightgame.sql (or similarly named SQL dump).

In HeidiSQL: select the flightgame database → File → Run SQL file… → pick the .sql → Execute.

You should now see tables populated (airports, conduits, etc.).

**4) Tell the game how to connect**
The game reads DB credentials from config constants (these are typical, adjust to your tree):
conduit_game/utils/config.py

**Set the following constants to match your local setup:**

DB_USER = "conduit_user"
DB_PASSWORD = "conduit_pass"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "flightgame"

**The code uses mariadb:**
pip install mariadb

If you hit build errors on Windows, install the MariaDB Connector/C from MariaDB’s site, then retry pip install mariadb.

Troubleshooting

Access denied: confirm user, password, host = localhost, and that you granted the privileges on flightgame.

Can’t connect: ensure MariaDB service is running; confirm port 3306 isn’t in use; check firewall.

Unicode issues: ensure DB and tables use utf8mb4 collations.

Driver missing: install mariadb (or switch code to mysql-connector-python and install that).

------------------------------------------------------------------------------------------------------------------------


## Features
- **Narrative-driven gameplay** with chapter-based story progression and player choices
- Turn-based combat with a clear, colorized combat log
- Player progression: levels, EXP, HP and Sanity scaling
- Inventory management with equip/use functionality
- **Weapons and Items system***
  - Melee and firearms with distinct characteristics
  - Firearms have magazine sizes and use named ammo types
  - Spawn guns with full, empty, or partial magazines
- **Manifestations (skills)** that consume Sanity
  - Fear, Hope, Rage, and Resentment manifestations available
  - Each with unique effects and sound effects
- **Enemy roster** with special attacks and EXP rewards
  - Multiple difficulty levels and unique abilities
- **Background music and SFX** via Pygame (lazy-initialized, safe on machines without audio)
- **Rich-based UI** for inventory and status bars with ASCII fallback
  - Unified Inventory table (aligned columns: `# | Name | Mag | Qty | Description`)
  - Inventory header now includes Markka, ammo reserves, and a dedicated vitals panel (HP/Sanity) rendered beside Level and Doom Clock when Rich is available
  - Ambient cryptic EXP "whispers" appear in the turn log as you near level-up
- **Travel loop with narrative feedback**
  - Menu-driven airport hopping, Markka costs, and conduit discovery/closure
  - Arrival messages now render as stylized blocks highlighting destination details and Doom Clock shifts
  - Doom Clock countdown logs inform the player when the clock hits zero, describing the world collapsing into eternal slumber
- **Rest system refresh**
  - Resting now draws HP/Sanity directly from `game/player.py:Player` stats and automatically reloads every firearm you own using current ammo reserves
  - Doom Clock still advances while resting, reinforcing the time pressure loop
- **Sound effects integration** for weapons, manifestations, and consumables
- **Typewriter text effects** for immersive storytelling

## Quick Start
### Requirements
- Python 3.10+
- pygame
- rich (recommended for enhanced UI; without it, the game uses an ASCII UI for inventory and status bars)
- Run through a real terminal for best visuals (Run/Debug consoles often mangle ANSI/Rich output)

Install dependencies:
```bash
pip install pygame rich geopy
```

py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
pip install pygame rich  # 'rich' is optional but recommended

If running scripts is disabled, run this:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

### Run the game
From the project root (real terminal recommended):
```bash
python main.py
```

## Project Structure
```
Game_project_software1/
├─ main.py                       # Entry point with story progression and demo encounters
├─ Music/                        # Music & SFX assets (case-sensitive on some systems)
├─ Database/
│  ├─ services.py                # Travel, conduit resolution, and arrival/Doom Clock messaging
│  ├─ menu_ui/                   # Hub loop, travel board, and menu screens
│  └─ Data/                      # SQL datasets for airports/conduits
└─ game/
   ├─ __init__.py                # Package API (re-exports: combat, Player, items, enemies, manifestations, music, UI helpers)
   ├─ combat.py                  # Turn-based combat loop and menus (orchestrates actions)
   ├─ combat_actions.py          # Combat helper functions: attack/manifest/inventory, reload_gun, target selection
   ├─ enemies.py                 # Enemy class, specials, library
   ├─ items.py                   # Item/Weapon/Consumable classes, libraries, inventory helpers
   ├─ manifestations.py          # Manifestation class and library
   ├─ music.py                   # Music helpers (play/stop/set volume, lazy init)
   ├─ player.py                  # Player class and leveling
   ├─ sfx_loader.py              # Sound effects registration and management
   ├─ story.py                   # Narrative system and story progression logic
   ├─ ui.py                      # Rich-first UI orchestration importing shared helpers from `ui_elements/`
   ├─ ui_elements/
   │  ├─ ASCII_fallback.py       # Inventory, combat bars, and HUD renderers for non-Rich terminals
   │  └─ colours.py              # Colour helpers, Rich detection, unified `ui_print`
   └─ writing_effects.py         # Typewriter/glitch/etc. text helpers
```

## Core Systems
### Player
- Class: `game/player.py` -> `Player`
- Stats: HP, Sanity, Base Attack, Leveling / EXP
- Inventory: list of `Item` objects
- Ammo pool: dictionary on player: `player.ammo = {".36 Caliber": 12, "5.56 Caliber": 30, ...}`
 - Level-up flow:
   - EXP is granted via `Player.gain_exp(amount)`.
   - While EXP ≥ threshold, `level_up_display(player)` (in `game/ui.py`) is called to level and show a Rich panel (ASCII fallback) with gains and an SFX. Music pauses briefly during the panel.

### Items & Weapons
- File: `game/items.py`
- Classes: `Item`, `Weapon`, `Consumable`
- Firearms include:
  - `ammo_type` (e.g., `.36 Caliber`, `5.56x45mm NATO`, `4.6x30mm`)
  - `mag_size` (e.g., 6, 30)
  - `current_mag` (auto-filled when acquired)
- Libraries:
  - `weapon_library`: Basic dagger, Sword, Jack's hammer, Old revolver, MP7, AR-15
  - `consumable_library`: Karelian pie, Rye Bread, Small coffee, Large coffee, .36 Caliber, 5.56x45mm NATO, 4.6x30mm, Markka, Makkara
- Inventory helpers:
  - `add_weapon_to_inventory(player, name)` (clones a fresh weapon)
  - `add_item_to_inventory(player, name, amount=1)` (routes ammo items into `player.ammo`)
 - SFX fields:
   - Consumables: `sfx_name` (e.g., Eating for healing, Drinking for sanity).
   - Weapons: `sfx_attack`, `sfx_reload`.
   - These are defined in the libraries and cloned onto instances; sounds are triggered at use-time (not at construction).
 - Inventory behavior:
   - Ammo-type consumables are routed to `player.ammo` pools (keyed by the consumable's display name to match `Weapon.ammo_type`).
   - Stacking compares by display name (e.g., `"Small coffee"`), ensuring SFX metadata is preserved.

### Combat
- Files: `game/combat.py`, `game/combat_actions.py`
- Actions per turn:
  1. Attack
  2. Defend
  3. Manifest
  4. Inventory
  5. Reload (for firearms)
- Turn usage rules:
  - Attack/Defend/Manifest/Reload consume the player turn
  - Opening Inventory and picking `0` (Back) does NOT consume the turn
  - Using an item or equipping a weapon from Inventory DOES consume the turn (configurable)
- Firearms:
  - Firing decrements `weapon.current_mag`
  - If the mag is empty, Reload to move rounds from `player.ammo[weapon.ammo_type]` into the mag
  - Combat log shows both mag state and reserve ammo
 - Implementation notes:
   - The main loop lives in `game/combat.py`.
   - Action handlers (`resolve_attack`, `handle_inventory`, `handle_manifestations`, `reload_gun`, `select_target`) live in `game/combat_actions.py` and are imported by the loop.
    - Attack SFX are played during the attack resolution using `weapon.sfx_attack`.
    - Reload SFX are played in `reload_gun()` using `weapon.sfx_reload` when a reload occurs.
    - Cleanup timing: defeated enemies are removed at the start of each new player turn so the `[ DEFEATED ]` state is visible for the rest of the round they died.

### Manifestations
- File: `game/manifestations.py`
- Available manifestations: Fear, Hope, Rage, and Resentment (with different costs and effects)
- SFX field: `sfx_manifest` can be set per manifestation; played when used.

### Enemies
- File: `game/enemies.py`
- Each enemy has a difficulty, HP, attack range, optional special attack, and EXP reward.
- Cleanup timing: Defeated enemies are removed at the start of each new player turn. This keeps the "[ DEFEATED ]" state visible for clarity during the remainder of the round in which they died.

### Music
- File: `game/music.py`
- Simple wrappers: `play_music`, `stop_music`, `set_volume`, `init_audio`
- Mixer is initialized lazily on first use (or explicitly via `init_audio()`), so import never crashes on machines without audio.
- Included assets (paths are case-sensitive on some systems):
  - `Music/ambience/Piano_suspense.mp3`
  - `Music/combat/Anxiety.mp3`
  - `Music/combat/Behind_you.mp3`
  - `Music/SFX/*.wav` (slash, shots, reloads, typing)

### SFX Registration
- File: `game/sfx_loader.py`
- Call `register_all_sfx()` from `main.py` to load all SFX keys/paths/volumes at startup.
- Gameplay code triggers sounds via `play_sfx(key)`.

### Terminal UI (Rich + ASCII fallback)
- Files: `game/ui.py`, `game/ui_elements/ASCII_fallback.py`, `game/ui_elements/colours.py`
- Inventory renders as dual-pane layout: Rich mode shows Inventory, Vitals, Level, and Doom Clock panels side-by-side; ASCII mode mirrors the original text layout.
- Shared `ui_print()` automatically routes to Rich or plain ANSI output based on runtime detection (`RICH_AVAILABLE`).
- Colour helpers (`colouring`, `colorize`) and ASCII HUD/status bars live in the `ui_elements/` package for reuse outside combat.

### Travel & Overworld
- Files: `Database/menu_ui/menu.py`, `Database/services.py`
- Hub loop for choosing travel, inventory, or rest; integrates with combat inventory handling.
- `travel_to_index()` deducts Markka, advances Doom Clock proportional to distance, and prints emphasized arrival/Doom updates.
- Conduit prompts reward Markka on closure and track global progress to unlock new story beats.
- `rest()` synchronizes with the active `Player` instance, restoring HP/Sanity and refilling firearm magazines from the player's ammo pools.

## Demo Flow (`main.py`)
- Creates a player character with starting manifestations and equipment
- Runs through a narrative-driven story progression system with multiple chapters ("conduits")
- Each story segment may unlock new manifestations, equipment, and trigger combat encounters
- Features typewriter text effects for immersive storytelling
- Includes multiple combat encounters integrated into the narrative flow
- Demonstrates the complete game loop: story → combat → progression → story
- Prints a hint at startup indicating whether Rich UI is enabled or ASCII fallback is in use.

## Story System (`game/story.py`)
- Manages narrative progression through chapter-based storytelling
- Implements player choice mechanics and branching narratives
- Integrates combat encounters seamlessly into the story flow
- Uses typewriter effects and timing for dramatic presentation
- Handles player progression and manifestation unlocks

## Controls & Tips
- Choose actions via number keys in combat
- In Inventory:
  - Pick an index to equip a weapon or use a consumable
  - Pick `0` to go back without using a turn
- Guns start with a full magazine when obtained
- Watch the log for reload hints and remaining reserve

Tip: For best visuals, install Rich:
```bash
pip install rich
```

## Adding Content
- Add new weapons to `weapon_library` with appropriate `ammo_type` and `mag_size`
- Add new ammo items to `consumable_library` and update `add_item_to_inventory` routing if needed
- Create new manifestations by defining a function and adding to `manifestation_library`
- Add enemies to `enemy_library` and special attacks as standalone functions

## Known Ideas / TODO
- More firearms and ammo types (e.g., shotguns, special rounds)
- Status effects (poison, bleed, fear) 
- Save/Load system
- Sanity Effects (Example: Combat log text gets scrambled when Sanity is low.)
- Randomly trigger audio “glitches” — distorted whispers, reversed sounds, sudden volume spikes.
- critical hits
- Enemies call for reinforcements mid-fight. (Maybe a specific enemy type)
- Some cultists summon eldritch horrors if not killed quickly.
- Boss fights
- Tension meter (tracking looming horror.(tension meter full maybe a secret boss; 
  looming horror appears) The longer you go without resting, the more “strange events” happen.)
- A store you can visit to buy items and weapons
- standardize the UI to use ui_print() 
- Graceful Defeat handling  (now it just brute forces a sys.exit)
- Finish fallbacks and safe guards

## Implemented Safeguards and Fallbacks
This is mainly meant for the teacher to see and review. 
During this project I tried to learn how to make code robust enough to handle different environments, and to make it as safe as possible.

### Audio System Safeguards
- **Lazy Audio Initialization**: Pygame mixer is initialized only when first needed, preventing crashes on systems without audio support
- **Graceful Audio Degradation**: Level-up SFX and music playback include proper checks for mixer initialization
- **Music State Preservation**: Background music is properly paused during level-up effects and resumed afterward
- **Silent Audio Failures**: When audio components fail, the game continues without crashing

### UI System Fallbacks
- **Rich Library Detection**: The `RICH_AVAILABLE` flag safely detects Rich library presence without crashing
- **Dual Rendering System**:
  - Rich-enhanced UI for better visual experience when available
  - ASCII fallback system for terminals without Rich support
- **Consistent Output**: `ui_print()` function routes output through Rich or ASCII based on availability

### Cross-Platform Compatibility
- **Terminal Width Detection**: Uses `shutil.get_terminal_size()` with fallback dimensions for different terminal environments
- **Case-Sensitive Path Handling**: Music assets use case-insensitive loading where possible
- **Import Error Handling**: Optional dependencies are imported safely with try-except blocks

### Combat & UI Stability
- **Defensive Programming**: Enemy cleanup and state validation prevent crashes from invalid game states
- **Input Validation**: Combat actions include bounds checking and error handling
- **Memory Management**: Proper cleanup of defeated enemies and temporary objects
- **UI Modularization**: Rich/ASCII presenters are isolated in `game/ui_elements/` to keep fallbacks consistent across menus and combat

## Remaining Work and Future Improvements

**Note**: Due to time constraints in the development cycle, several improvements and safeguards were planned but require completion in future iterations:

### Critical Safeguards Still Needed
- **Complete Audio Safeguards**: Extend level-up audio protection to all UI audio calls throughout the codebase
- **Standardize UI Output**: Replace remaining direct `print()` calls with the safe `ui_print()` function
- **Graceful Defeat Handling**: Replace `sys.exit()` with proper game over screen and restart options
- **Error Recovery**: Add retry mechanisms for failed audio/music loading

### Planned Features
- **Save/Load System**: Basic framework exists but needs full implementation and data validation
- **Rest System**: HP/Sanity recovery mechanics between combats (partially designed)
- **Status Effects Framework**: Poison, bleed, and fear mechanics (design work done)
- **Boss Fight System**: Special enemy types and multi-phase encounters
- **Tension Meter**: Tracks looming horror and triggers secret boss encounters
- **Audio Glitches**: Randomly trigger audio “glitches” — distorted whispers, reversed sounds, sudden volume spikes.
- **Critical Hits**: A chance for a critical hit that deals double damage.
- **Trader/Economy**: A trader that sells items and weapons.
- **Armor system**: Armor that reduces damage taken. 

### Content Expansion Opportunities
- **Additional Weapons**: Shotguns, special ammunition types, and exotic weapons
- **Enemy Variety**: More enemy types with unique abilities and behaviors
- **Manifestation Balance**: Additional manifestations and rebalancing of existing ones
- **Narrative Depth**: Expanded story branches and consequence systems

### Technical Debt
- **Code Standardization**: Migrate remaining modules to use consistent error handling patterns
- **Testing Coverage**: Add unit tests for critical systems and edge cases
- **Performance Optimization**: Reduce redundant operations in combat and UI rendering
- **Documentation Updates**: Keep inline documentation synchronized with implemented features


## Requirements File
If you prefer a requirements.txt:
```
pygame>=2.0.0
rich>=13.0.0
geopy>=2.4.1
```

## Credits
- Audio assets under `Music/` are not created by us. 
- Credits for the music goes to: Pixabay and fesliyanstudios

## License
This project is for educational purposes. Add a LICENSE file if you plan to distribute.

---
