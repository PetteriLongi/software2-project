# Rites of Transit - A Lovecraftian Horror RPG

A web-based Lovecraftian horror RPG built with Flask backend and vanilla JavaScript frontend. Players navigate a dark world of conduits and cosmic horrors, make choices that affect their sanity, manage resources, engage in tactical combat, and uncover an eldritch mystery across multiple chapters.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Architecture](#architecture)
4. [Core Systems](#core-systems)
5. [Setup Instructions](#setup-instructions)
6. [API Reference](#api-reference)
7. [Game Flow](#game-flow)
8. [Development Guide](#development-guide)

---

## Overview

**Rites of Transit** is a narrative-driven horror RPG featuring:

- **5 Chapters** of progressive story with branching narrative choices
- **Interactive Map** with Leaflet.js showing real-world airports
- **Turn-Based Combat** with enemy targeting and tactical choices
- **Doom Clock System** tracking player sanity decline (0-100 ticks)
- **Item & Inventory System** with weapons, ammo, and consumables
- **Conduit Closing Mechanic** - Close 5 conduits (gates to the cosmic) to win
- **Dynamic Audio** with atmospheric music and sound effects
- **Persistent Game State** using Flask sessions

### Core Mechanics

- **Doom Clock**: Decrements as player encounters horrors. When it reaches 0, game over
- **Manifestations**: Unlocked entities that follow the player (Hope, Resentment, etc.)
- **Conduits**: Supernatural structures that must be closed by defying cosmic voices
- **Markka**: Currency for trading and resource management

---

## Project Structure

```
GameProjectSoftware2/
├── app.py                              # Flask application factory
├── config.py                           # Configuration constants
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
│
├── blueprints/                         # Modular Flask blueprints
│   ├── main.py                        # Frontend routes (/, /menu, /combat, /story, /travel)
│   └── api/
│       ├── game.py                   # Game init, state, save/load
│       ├── combat.py                 # Combat logic, actions, rewards
│       ├── travel.py                 # Travel board, airport selection, conduit closing
│       ├── inventory.py              # Item management, equipment
│       ├── story.py                  # Story node processing, choices
│       └── audio/
│           ├── routes.py             # Audio file serving
│           └── __init__.py
│
├── game_logic/                         # Core game systems
│   ├── database.py                   # Database initialization
│   ├── player.py                     # Player data model
│   ├── combat_engine.py              # Combat calculations, turn logic
│   ├── story_engine.py               # Story node processing
│   ├── story_data.json               # Complete story content (3+ chapters)
│   ├── travel_service.py             # Airport generation, travel logic
│   ├── items.py                      # Weapon/consumable definitions
│   ├── enemies.py                    # Enemy definitions and encounters
│   ├── manifestations.py             # Manifestation mechanics
│   ├── audio/
│   │   ├── audio_config.py          # Audio file mappings
│   │   └── __init__.py
│   └── __pycache__/
│
├── static/                             # Frontend assets
│   ├── css/
│   │   ├── style.css                # Main stylesheet
│   │   ├── combat.css               # Combat-specific styles
│   │   ├── story.css                # Story screen styles
│   │   ├── settings.css             # Settings panel styles
│   │   └── travel.css               # Travel board styles
│   │
│   ├── js/
│   │   ├── main.js                  # Application entry point
│   │   ├── game.js                  # Game state manager
│   │   ├── api.js                   # API communication layer
│   │   ├── ui.js                    # UI rendering utilities
│   │   ├── audio.js                 # Audio management
│   │   ├── settings.js              # Settings panel logic
│   │   ├── combat/
│   │   │   ├── combat-controller.js # Combat flow control
│   │   │   └── combat-renderer.js   # Combat UI rendering
│   │   ├── story.js                 # Story screen logic
│   │   └── travel.js                # Travel map controller
│   │
│   ├── images/
│   │   ├── player/                 # Player sprites (chapter-based)
│   │   ├── enemies/                # Enemy sprites
│   │   ├── backgrounds/            # Screen backgrounds
│   │   ├── manifestations/         # Manifestation images
│   │   └── props/                  # Environmental props
│   │
│   └── audio/
│       ├── music/                  # Ambient and combat music
│       ├── sfx/                    # Sound effects
│       └── ambience/               # Atmospheric sounds
│
├── templates/                          # HTML templates
│   ├── index.html                  # Main SPA container (minimal Jinja2 for asset refs)
│   ├── mainMenu.html               # Menu template (injected via AJAX)
│   ├── story.html                  # Story template (injected via AJAX)
│   ├── combat.html                 # Combat template (injected via AJAX)
│   ├── travel.html                 # Travel template (injected via AJAX)
│   ├── help_modal.html             # Shared help modal fragment (loaded dynamically)
│   └── audio_test.html             # Audio debugging template
│
├── Data/
│   └── flightgame.sql              # Database schema (legacy)
│
└── [Documentation files - DOOMCLOCK_*, PHASE2_COMPLETE, etc.]
```

---

## Architecture

### Technology Stack

**Backend:**
- Python 3.x with Flask web framework
- Flask-CORS for cross-origin requests
- Session-based game state management
- JSON for configuration and story data
- Minimal Jinja2 templating (only for asset URLs)

**Frontend:**
- Vanilla JavaScript (no frameworks) - Single Page Application (SPA)
- HTML5 and CSS3
- AJAX/fetch for all dynamic content loading
- Leaflet.js v1.9.4 for interactive maps
- OpenStreetMap tiles for map display

**Architecture Pattern:**
- Index.html serves as the main SPA container
- All screens (menu, story, combat, travel) are templates injected via AJAX
- No server-side page renders - all navigation is client-side
- API endpoints return JSON only

**Assets:**
- PNG sprites for characters and environments
- MP3 audio files for music and effects
- CSS3 animations and transitions

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (JavaScript)                   │
│  main.js → ui.js → game.js → api.js → [fetch requests]     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/JSON
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend                            │
│  app.py → blueprints → [game_logic] → session management   │
└──────────────────────┬──────────────────────────────────────┘
                       │ Session Storage
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Game State (Flask Sessions)                     │
│  player, run_state, game_state, doom_clock                 │
└─────────────────────────────────────────────────────────────┘
```

### Game State Structure

```python
Session Storage:
{
    'player': {
        'name': str,
        'hp': int,
        'max_hp': int,
        'inventory': {...},
        'weapons': {...}
    },
    'run_state': {
        'conduits_closed': int,
        'markka': int,
        'current_location': str
    },
    'game_state': {
        'current_node': str,
        'visited_nodes': [],
        'conduits_closed': int
    },
    'doom_clock': {
        'ticks': int (0-100),
        'start': int (100),
        'warnings': []
    }
}
```

---

## Core Systems

### Shared Help Modal

- Centralized HTML lives in `templates/help_modal.html`
- Dynamically fetched via the `/help_modal` route
- Injected and styled by `UI.initializeHelpModal()` in `static/js/ui.js`
- Available on main menu, inventory, and travel screens via the `?` / "Whispers of Guidance" buttons

### 1. Story Engine (`game_logic/story_engine.py`)

**Purpose:** Process narrative nodes and manage story progression

**Key Functions:**
- `process_story_node(node_key, choice_index)` - Load and process story nodes
- Supports text arrays, music changes, combat encounters, choices, rewards
- Tracks visited nodes for replay prevention
- Handles manifestation unlocks

**Story Structure (story_data.json):**
```json
{
  "node_key": {
    "text": ["Line 1", "Line 2"],
    "music": {"action": "play", "track": "path", "volume": 0.12},
    "combat": {"enemies": ["Cultist"], "music": "path"},
    "choices": [
      {"label": "Option A", "next": "next_node"},
      {"label": "Option B", "next": "other_node"}
    ],
    "doom_tick": 1,
    "rewards": {"weapons": ["AR-15"], "consumables": [...]},
    "conduit_closed": true,
    "travel": true
  }
}
```

### 2. Combat System (`game_logic/combat_engine.py`)

**Purpose:** Handle turn-based tactical combat

**Key Components:**
- Enemy selection with click targeting
- Turn-based action system (Attack, Defend, Use Item)
- Damage calculation with randomization
- Enemy targeting with sprite visual feedback
- Hurt animations on damage taken

**Combat Flow:**
1. Combat starts → enemies rendered with sprite animations
2. Player chooses target and action
3. Turn processes: Player action → Enemy counter-attack
4. Damage calculated and displayed
5. Victory/Defeat determined
6. Rewards distributed (items, markka)

### 3. Travel System (`game_logic/travel_service.py`)

**Purpose:** Generate airports and manage travel between locations

**Key Features:**
- Generates 10 random airports from real-world database
- Calculates routes with Leaflet.js screen-space interpolation
- Animated plane icon follows flight path with rotation
- Conduit closing at each airport location
- Dark map overlay (brightness 0.5, contrast 1.2, saturation 0.8)

**Map Integration:**
- Uses Leaflet.js v1.9.4 with OpenStreetMap tiles
- LeafletMapManager handles animation and controls
- Plane sprite rotates to face flight direction
- Real geographic coordinates for airports

### 4. Inventory System (`game_logic/items.py`)

**Weapons:**
- AR-15 (15-30 damage, 5.56x45mm NATO, 30-round magazine)
- Various support weapons

**Consumables:**
- Potions (healing items)
- Ammunition (tracked by type)

### 5. Doom Clock System

**Purpose:** Track player mental state and create urgency

**Mechanics:**
- Starts at 100 ticks
- Decrements 1 tick per conduit closure
- Additional ticks lost on story events
- Game over when reaches 0
- Visual indicator and warnings as it approaches 0

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Git
- PowerShell or Command Prompt

### 1. Clone/Navigate to Project

```powershell
cd c:\Users\petel\PycharmProjects\software2-project\GameProjectSoftware2
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
copy .env.example .env
# Edit .env with any custom settings
```

### 5. Run Application

```powershell
python app.py
```

**Application URL:** `http://localhost:5000`

---

## API Reference

### Game Management (`/api/game/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/game/start` | Initialize new game, set up player and doom clock |
| GET | `/api/game/state` | Retrieve current game state |
| POST | `/api/game/save` | Save game to file/database |
| POST | `/api/game/load` | Load saved game |

### Combat System (`/api/combat/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/combat/action` | Execute combat action (attack, defend, use item) |
| GET | `/api/combat/state` | Get current combat state and enemy status |
| POST | `/api/combat/target/<index>` | Select target enemy |

### Travel System (`/api/travel/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/travel/airports` | Get list of 10 available airports |
| POST | `/api/travel/travel` | Travel to selected airport |
| POST | `/api/travel/close_conduit` | Close conduit at location, trigger story |

**Close Conduit Request:**
```json
{
  "airport_index": 0
}
```

**Response:**
```json
{
  "success": true,
  "markka": 5000000,
  "conduits_closed": 1,
  "story": {
    "node_key": "2_conduit",
    "text": ["Story text..."],
    "choices": [...],
    "combat": {...}
  }
}
```

### Story System (`/api/story/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/story/current` | Get current story node |
| POST | `/api/story/choice` | Process player story choice |
| POST | `/api/story/continue` | Continue to next story node |
| GET | `/api/story/node/<key>` | Fetch specific story node |

**Choice Request:**
```json
{
  "choice_index": 0
}
```

### Inventory (`/api/inventory/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory` | Get inventory contents |
| POST | `/api/inventory/use` | Use consumable item |
| POST | `/api/inventory/equip` | Equip weapon |

---

## Game Flow

### Chapter Progression

```
Start (Intro Chapter)
  ↓ Intro closes first conduit
Chapter 2 (Apostle encounter)
  ↓ Close 1st conduit (2nd total) + Choose Defiance
Chapter 3 (Anatomist encounter)
  ↓ Close 2nd conduit (3rd total) + Choose Defiance
Chapter 4 (Fractured Sky)
  ↓ Close 3rd conduit (4th total) + Choose Defiance
Chapter 5+ (Final confrontation)
  ↓ Close remaining conduits
Victory/Ending
```

### Conduit Closing Flow (Fixed in Latest Build)

1. **Button Press** → Store pending conduit closure (don't close yet)
2. **Story Plays** → Show chapter content based on CURRENT conduit count
3. **Combat** → Battle manifestation/enemy
4. **Aftermath** → Get item rewards
5. **Story Choice** → Player chooses Acceptance (ending) or **Defiance**
6. **Defiance Path** → Node marked with `"conduit_closed": true`
7. **Close Conduit** → Increment counter, unlock next chapter
8. **Return to Travel** → See updated conduit counter (X/5 Sealed)

### Defiance Nodes

Special story nodes that mark conduit closure:
- `whispering_conduit.defiance` (Chapter 2)
- `3_conduit_encounter.defy` (Chapter 3)
- etc.

These nodes have:
```json
{
  "conduit_closed": true,
  "travel": true,
  "doom_tick": 1
}
```

---

## Development Guide

### Adding New Story Content

1. **Add node to `story_data.json`:**
```json
"new_chapter.intro": {
  "text": ["Story text"],
  "music": {"action": "play", "track": "path"},
  "choices": [
    {"label": "Option A", "next": "new_chapter.path_a"},
    {"label": "Option B", "next": "new_chapter.path_b"}
  ]
}
```

2. **Link from previous node:**
```json
"previous_node": {
  "next": "new_chapter.intro"
}
```

### Adding New Enemies

1. **Define in `game_logic/enemies.py`:**
```python
"Chapter": Enemy(
    "Enemy Name",
    difficulty=2,
    hp=50,
    attack=(5, 15),
    min_loot=1000,
    max_loot=2000
)
```

2. **Add sprite to `static/images/enemies/`:**
- `enemyname.png` - Normal sprite
- `enemynameHurt.png` - Hurt animation sprite

3. **Map in combat renderer if needed:**
```javascript
const nameMapping = {
    'Enemy Name': 'enemyname'
};

const hurtSpriteMapping = {
    'Enemy Name': 'enemynameHurt'
};
```

### Adding New Items

**Weapons:**
```python
'Weapon Name': {
    'name': 'Weapon Name',
    'type': 'weapon',
    'damage_min': 10,
    'damage_max': 20,
    'ammo_type': '5.56x45mm NATO',
    'mag_size': 30,
    'description': 'Description'
}
```

**Consumables:**
```python
'Potion': {
    'name': 'Potion',
    'type': 'consumable',
    'effect': 'heal',
    'amount': 20,
    'description': 'Description'
}
```

### Modifying Doom Clock

Adjust in story nodes:
```json
"node_key": {
  "doom_tick": 2,
  "doom_reason": "Reason for sanity loss"
}
```

### Audio Management

Audio files organized in `static/audio/`:
- `music/` - Background music tracks
- `sfx/` - Sound effects
- `ambience/` - Atmospheric sounds

Map in `game_logic/audio/audio_config.py`:
```python
AUDIO_MAP = {
    'event_name': {
        'track': 'Music/path/to/file.mp3',
        'volume': 0.12,
        'loop': True
    }
}
```

---

## Deployment Notes

### Production Considerations

- Set `DEBUG = False` in `config.py`
- Use production WSGI server (Gunicorn, etc.)
- Enable HTTPS
- Configure CORS for specific domains
- Implement proper database for save persistence
- Add rate limiting to API endpoints
- Implement user authentication system
- Serve the help modal via the `/help_modal` route (already wired) and keep `/` as the primary entry point for the main menu

### Performance Optimization

- Minify CSS/JS
- Compress audio files
- Cache static assets
- Lazy-load images
- Optimize map tile loading

---

## Credits & Contributors

**Original Game Design:** Petteri, Jack, Derej, Pathirage

**Web Migration & Development:** Petteri, Daniel, Derej, Pathirage

**Special Thanks:** All playttesters and contributors

---
