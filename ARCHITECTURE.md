# Architecture: AJAX/SPA with Deferred Conduit Closure

## System Overview

Rites of Transit is a **Flask-based AJAX Single-Page Application (SPA)** with Python game logic running on the server. The architecture separates frontend (display) from backend (rules), preventing cheating and maintaining a single source of truth.

```
┌──────────────────────────────────────────────────────────────────┐
│                         WEB BROWSER                               │
│  index.html (single page) + static/js/*.js                        │
│  - Display: Render HTML/CSS                                       │
│  - Events: Handle clicks and user input                           │
│  - API Calls: Send JSON via fetch()                               │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                    AJAX Requests
                   (JSON over HTTP)
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                       FLASK SERVER                                 │
│  app.py + blueprints/api/*.py                                     │
│  - Routing: URLs to handler functions                             │
│  - Session: Store player, run_state, game_state                   │
│  - Validation: Enforce game rules                                 │
│  - Response: Return JSON data (AJAX routes never render HTML)     │
└───────────────────────┬──────────────────────────────────────────┘
                        │
              Game Logic Processing
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                      GAME LOGIC LAYER                              │
│  game_logic/*.py                                                   │
│  - Combat Engine: Calculate damage, effects, AI                   │
│  - Story Engine: Process narrative choices and progression        │
│  - Player System: Track HP, sanity, inventory, manifestations     │
│  - Item System: Weapons, ammo, consumables                        │
│  - Travel System: Airport routing, conduit closure                │
└───────────────────────┬──────────────────────────────────────────┘
                        │
              Data Persistence
                        │
┌───────────────────────▼──────────────────────────────────────────┐
│                    SESSION STORAGE                                 │
│  session['player'], session['run_state'], session['game_state']   │
└──────────────────────────────────────────────────────────────────┘
```

---

## AJAX/SPA Pattern

**AJAX** = Asynchronous JavaScript + XML (really JSON)
**SPA** = Single Page Application (one index.html, all content loaded dynamically)

### Flow:

1. **Browser loads index.html once**
   ```html
   <!DOCTYPE html>
   <html>
   <body>
       <div id="app"></div>
       <script src="static/js/main.js"></script>
   </body>
   </html>
   ```

2. **JavaScript controls what displays**
   ```javascript
   // Load main menu
   const menuHTML = await fetch('/menu').then(r => r.text());
   document.getElementById('app').innerHTML = menuHTML;
   
   // Load story (as JSON)
   const storyData = await fetch('/api/story/node').then(r => r.json());
   UI.renderStory(storyData);
   ```

3. **All updates via API calls that return JSON**
   ```javascript
   // Player makes choice
   const result = await fetch('/api/story/choice', {
       method: 'POST',
       body: JSON.stringify({ choice_id: 3 })
   }).then(r => r.json());
   
   // Backend processed it, returns next story node
   // JavaScript displays it
   ```

### Why AJAX/SPA?

✅ **Responsive**: No full page reloads (feels like desktop app)
✅ **Fast**: Only data transfers over network, not HTML
✅ **Clean**: Clear separation: frontend displays, backend calculates
✅ **Flexible**: Easy to change UI without touching game logic
✅ **Animated**: Smooth transitions between game states

---

## Critical Architecture: Deferred Conduit Closure

The game's conduit closing mechanic uses **deferred closure** for dramatic impact:

### ❌ WRONG (old approach):
```
Button Click: "Defy!" ──> travel.py closes conduit immediately
                              ↓
                         Chapter increments (too early!)
                              ↓
                         Story plays (feels anticlimactic)
```

### ✅ CORRECT (current implementation):
```
Button Click: "Defy!" ──> travel.py stores pending closure
                              ↓
                         Story node plays (full drama)
                              ↓
                         Player reaches "defiance" choice
                              ↓
                         story.py detects conduit_closed flag
                              ↓
                         Conduit actually closes (climactic moment!)
                              ↓
                         Chapter increments (at right time)
```

### Implementation Details:

**Step 1: travel.py stores closure (doesn't execute it)**
```python
@travel_bp.route('/travel', methods=['POST'])
def travel():
    airport_index = request.json['airport_index']
    
    # Store closure for later execution
    session['pending_conduit_closure'] = airport_index
    
    # Use CURRENT count to map to correct story chapter
    current_conduits = session['run_state']['conduits_closed']
    chapter = current_conduits + 1
    node_id = f'{chapter}_conduit_encounter'
    
    # Load the encounter story node
    result = story_engine.process_story_node(node_id, session)
    
    return jsonify(result)  # Don't close yet!
```

**Step 2: story_data.json marks defiance nodes**
```json
{
    "2_conduit_encounter.defiance": {
        "text": "With defiant will, you SLAM the gate shut!",
        "conduit_closed": true,
        "travel": true,
        "next": "post_conduit_escape"
    }
}
```

**Step 3: story.py detects flag and executes closure**
```python
@story_bp.route('/choice', methods=['POST'])
def make_choice():
    choice_id = request.json['choice_id']
    
    # Get next story node
    next_node_id = story_engine.get_next_node(current_node, choice_id)
    next_result = story_engine.process_story_node(next_node_id, session)
    
    # KEY: Check if this node closes a conduit
    if next_result.get('conduit_closed'):
        run_state = deserialize_run_state(session['run_state'])
        airport_index = session.get('pending_conduit_closure')
        
        # Now actually close the conduit
        closure_result = close_conduit_service(run_state, airport_index)
        
        # Clean up pending closure
        session.pop('pending_conduit_closure', None)
        
        # Return closure result, not story node
        return jsonify(closure_result)
    
    # Normal story progression
    session['game_state']['current_node'] = next_node_id
    return jsonify({
        'success': True,
        'text': next_result['text'],
        'choices': next_result['choices'],
        'music': next_result.get('music')
    })
```

**Why This Works:**
- Closure doesn't happen until player makes a choice
- The choice itself triggers the actual gate closing
- Dramatic timing: story flows → choice → climax
- Session state preserved throughout the flow

---

## Module Organization

### blueprints/ (HTTP Routes)
Handles web requests and responses. Never contains game logic.

```
blueprints/
├── main.py                    # Frontend routes: /, /menu
├── api/
│   ├── game.py               # /api/game/* endpoints
│   ├── story.py              # /api/story/* endpoints
│   ├── combat.py             # /api/combat/* endpoints
│   ├── inventory.py          # /api/inventory/* endpoints
│   ├── travel.py             # /api/travel/* endpoints
│   └── audio/
│       └── routes.py         # /api/audio/* endpoints
```

**Responsibility**: Parse JSON requests, call game_logic functions, serialize responses to JSON

**Key Pattern**: Routes never implement game rules—they call game_logic

### game_logic/ (Pure Game Logic)
Business logic with no web dependencies. Can run standalone or in different web frameworks.

```
game_logic/
├── player.py                 # Player class: HP, inventory, manifestations
├── enemies.py                # Enemy definitions and AI
├── combat_engine.py          # Turn-based combat processor
├── items.py                  # Weapons, consumables, effects
├── manifestations.py         # Fear, Hope, Rage, Resentment powers
├── story_engine.py           # Story node processor
├── story_data.json           # 28 nodes × 5 chapters × 4 endings
├── travel_service.py         # Airport routing, conduit system
└── database.py               # SQLite persistence
```

**Responsibility**: Enforce game rules, calculate outcomes, no I/O (no print, no input)

**Key Classes**:
- `Player`: HP, sanity, inventory, manifestations, serialization
- `Enemy`: HP, attacks, AI, death effects
- `CombatEngine`: Turn processor, action validation, outcome calculation
- `StoryEngine`: Node loading, choice processing, narrative flow

### static/js/ (Frontend Application)
JavaScript for display and user interaction.

```
static/js/
├── main.js                   # App initialization
├── game.js                   # Game state management
├── ui.js                     # DOM rendering functions
├── api.js                    # Fetch wrapper for API calls
├── audio.js                  # Music and sound effects
├── story.js                  # Story display and choice handling
├── travel.js                 # Map rendering and plane animation
├── settings.js               # UI preferences
└── combat/
    ├── combat-controller.js  # Action coordination
    └── combat-renderer.js    # Sprite animations, HP bars
```

**Responsibility**: Display data, handle user clicks, manage audio/visuals

**Key Pattern**: Call API endpoints, process JSON responses, update DOM

### static/ (Assets)
CSS, images, and audio files.

```
static/
├── css/
│   ├── style.css            # Global styles
│   ├── combat.css           # Combat UI
│   ├── story.css            # Story display
│   └── settings.css         # Settings menu
├── images/
│   ├── backgrounds/         # Scene backdrops
│   ├── enemies/             # Enemy sprites
│   ├── manifestations/       # Manifestation icons
│   └── player/              # Player sprites
└── audio/
    ├── music/               # BGM tracks
    └── sfx/                 # Sound effects
```

### templates/ (HTML Templates)
Jinja2 templates served by Flask.

```
templates/
├── index.html               # Root page (loaded once)
├── mainMenu.html            # Title screen (loaded via fetch)
├── story.html               # Story UI template
├── combat.html              # Combat UI template
└── travel.html              # Map UI template
```

**Key Difference**: Templates are loaded **via AJAX** and injected by JavaScript, NOT rendered by Jinja2 on each request

---

## Session State Structure

Flask sessions persist game state between requests. Key structure:

```python
session = {
    # Player state (serialized Player object)
    'player': {
        'name': 'Avatar',
        'hp': 78,
        'max_hp': 100,
        'sanity': 54,
        'max_sanity': 100,
        'inventory': [
            {'type': 'weapon', 'name': 'Dagger', 'damage': '2-4'},
            {'type': 'gun', 'name': 'Revolver', 'ammo': 6, 'mag_size': 6},
            {'type': 'consumable', 'name': 'Health Potion', 'qty': 3}
        ],
        'manifestations': {
            'fear': {'level': 2, 'cooldown': 0},
            'hope': {'level': 1, 'cooldown': 0},
            'rage': {'level': 1, 'cooldown': 0},
            'resentment': {'level': 1, 'cooldown': 0}
        }
    },
    
    # Game progression state
    'run_state': {
        'chapter': 3,
        'conduits_closed': 2,
        'doom_clock': 67,
        'current_location': 'Denver'
    },
    
    # Current context (story, combat, etc.)
    'game_state': {
        'current_node': 'chapter_3_ritual',
        'in_combat': False,
        'current_combat': None  # or serialized Combat object
    },
    
    # Deferred conduit closure (set when travel button clicked)
    'pending_conduit_closure': 2  # Airport index
}
```

**Key Values**:
- `player`: Serialized Player object (stats, inventory, powers)
- `run_state`: Game progression (chapter, conduits, doom clock, location)
- `game_state`: Current context (story node ID, combat state)
- `pending_conduit_closure`: Which airport index to close (set by travel.py, used by story.py)

---

## Complete Request/Response Examples

### Story Choice (with potential conduit closure):

**Frontend** (static/js/story.js):
```javascript
async function chooseStoryOption(choiceId) {
    const response = await fetch('/api/story/choice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ choice_id: choiceId })
    });
    
    const result = await response.json();
    
    // Result might be:
    // 1. Next story node (normal progression)
    // 2. Conduit closure result (if choice triggered defiance)
    
    if (result.conduit_closed) {
        // Play conduit closure animation
        UI.showConduitClosure(result.location);
        await Audio.play('conduit_close');
    } else {
        // Display next story node
        UI.renderStory(result);
    }
}
```

**Backend** (blueprints/api/story.py):
```python
@story_bp.route('/choice', methods=['POST'])
def make_choice():
    choice_id = request.json['choice_id']
    current_node = session['game_state']['current_node']
    
    # Get next node based on choice
    next_node_id = story_engine.get_next_node(current_node, choice_id)
    
    # Process that node
    next_result = story_engine.process_story_node(next_node_id, session)
    
    # Check: Does this node close a conduit?
    if next_result.get('conduit_closed'):
        # Execute deferred closure NOW
        run_state = deserialize_run_state(session['run_state'])
        airport_index = session.get('pending_conduit_closure')
        
        result = close_conduit_service(run_state, airport_index)
        
        # Update session
        session['run_state'] = run_state.to_dict()
        session.pop('pending_conduit_closure', None)
        
        # Return closure result (not story node)
        return jsonify({
            'success': True,
            'conduit_closed': True,
            'location': result['location'],
            'chapter': run_state.chapter,
            'next_node': result.get('next_node')
        })
    
    # Normal story progression
    session['game_state']['current_node'] = next_node_id
    
    return jsonify({
        'success': True,
        'text': next_result['text'],
        'choices': next_result['choices'],
        'music': next_result.get('music'),
        'conduit_closed': False
    })
```

### Combat Action:

**Frontend** (static/js/combat/combat-controller.js):
```javascript
async function executeAction(actionType, targetIndex) {
    const response = await fetch('/api/combat/action', {
        method: 'POST',
        body: JSON.stringify({
            action_type: actionType,
            target_index: targetIndex
        })
    });
    
    const result = await response.json();
    
    // Animate player action
    CombatRenderer.playAttackAnimation(
        result.attacker,
        result.target,
        result.damage
    );
    
    // Update enemy HP
    CombatRenderer.updateEnemyHP(result.enemy_hp);
    
    // Check if enemy still alive
    if (result.enemy_alive) {
        // Wait for animation to finish
        await new Promise(r => setTimeout(r, 500));
        
        // Enemy turn
        const enemyResult = await handleEnemyTurn(result.enemy_action);
    } else {
        // Combat over, show victory
        handleVictory(result);
    }
}
```

**Backend** (blueprints/api/combat.py):
```python
@combat_bp.route('/action', methods=['POST'])
def combat_action():
    action_type = request.json['action_type']
    player = deserialize_player(session['player'])
    combat = deserialize_combat(session['game_state']['current_combat'])
    
    # Process player action
    player_result = combat_engine.process_action(
        combat,
        player,
        action_type,
        target_index=request.json.get('target_index')
    )
    
    # Check win condition
    if combat.enemy.hp <= 0:
        # Victory!
        session.pop('current_combat', None)
        victory_rewards = combat_engine.calculate_rewards(player, combat.enemy)
        
        return jsonify({
            'success': True,
            'player_action': player_result,
            'enemy_alive': False,
            'victory': True,
            'rewards': victory_rewards
        })
    
    # Process enemy turn
    enemy_action = combat.enemy.choose_action(combat, player)
    enemy_result = combat_engine.process_action(
        combat,
        combat.enemy,
        enemy_action,
        target=player
    )
    
    # Check loss condition
    if player.hp <= 0:
        return jsonify({
            'success': True,
            'enemy_action': enemy_result,
            'player_alive': False,
            'game_over': True
        })
    
    # Save updated state
    session['player'] = serialize_player(player)
    session['game_state']['current_combat'] = serialize_combat(combat)
    
    # Combat continues
    return jsonify({
        'success': True,
        'player_action': player_result,
        'enemy_action': enemy_result,
        'player_hp': player.hp,
        'enemy_hp': combat.enemy.hp,
        'enemy_alive': True
    })
```

### Travel (Airport):

**Frontend** (static/js/travel.js):
```javascript
async function travelToAirport(airportIndex) {
    const response = await fetch('/api/travel/travel', {
        method: 'POST',
        body: JSON.stringify({ airport_index: airportIndex })
    });
    
    const result = await response.json();
    
    // Animate plane flight
    TravelRenderer.animateFlight(airportIndex, () => {
        // Show story encounter (conduit gate)
        UI.renderStory(result);
    });
}
```

**Backend** (blueprints/api/travel.py):
```python
@travel_bp.route('/travel', methods=['POST'])
def travel():
    airport_index = request.json['airport_index']
    
    # Get current progression
    run_state = deserialize_run_state(session['run_state'])
    chapter = run_state.conduits_closed + 1
    
    # Store pending closure (don't execute yet!)
    session['pending_conduit_closure'] = airport_index
    
    # Load conduit encounter story node
    node_id = f'{chapter}_conduit_encounter'
    result = story_engine.process_story_node(node_id, session)
    
    session['game_state']['current_node'] = node_id
    
    # Return encounter story (not closure result)
    return jsonify({
        'success': True,
        'text': result['text'],
        'choices': result['choices'],
        'music': result.get('music')
    })
```

---

## Story Engine: JSON-Driven Narrative

**story_data.json** contains 28 story nodes forming 5 chapters with 4 possible endings.

### Node Structure:

```json
{
    "chapter_2_encounter": {
        "text": "You arrive at the coordinates given in the letter...",
        "music": "ambient_dread",
        "choices": [
            {
                "text": "Attempt to seal the gate",
                "next": "chapter_2_seal"
            },
            {
                "text": "Defiantly close it",
                "next": "chapter_2_defiance"
            },
            {
                "text": "Investigate further",
                "next": "chapter_2_investigate"
            }
        ]
    },
    
    "chapter_2_defiance": {
        "text": "With defiant fury, you SLAM the ancient gate shut!",
        "conduit_closed": true,
        "travel": true,
        "next": "post_closure_escape"
    },
    
    "chapter_2_combat": {
        "text": "Cultists block your path!",
        "combat": {
            "enemy_type": "Cultist",
            "count": 3,
            "music": "combat_tense"
        },
        "on_victory": "proceed_to_node_3",
        "on_defeat": "captured"
    }
}
```

### Node Fields:

| Field | Purpose |
|-------|---------|
| `text` | Story content displayed to player |
| `choices` | Array of {text, next} for branching |
| `music` | BGM track to play |
| `combat` | Enemy encounter configuration |
| `conduit_closed` | Flag: this node closes a conduit |
| `travel` | Flag: transition to travel phase |
| `doom_ticks` | Sanity loss for this node |
| `on_victory`/`on_defeat` | Next nodes based on combat outcome |

### Processing:

```python
def process_story_node(node_id, session):
    """Load and process a story node"""
    node = STORY_DATA.get(node_id)
    
    if not node:
        return {'error': f'Node {node_id} not found'}
    
    result = {
        'text': node['text'],
        'choices': node.get('choices', []),
        'music': node.get('music'),
        'conduit_closed': node.get('conduit_closed', False),
        'travel': node.get('travel', False)
    }
    
    # Handle combat encounters
    if 'combat' in node:
        enemy = spawn_enemy(node['combat']['enemy_type'])
        session['game_state']['current_combat'] = serialize_combat(enemy)
        result['combat'] = True
        result['combat_enemy'] = enemy.to_dict()
    
    # Update doom clock
    if 'doom_ticks' in node:
        run_state = deserialize_run_state(session['run_state'])
        run_state.doom_clock += node['doom_ticks']
        session['run_state'] = run_state.to_dict()
        result['doom_clock'] = run_state.doom_clock
    
    return result
```

---

## Why This Architecture?

### ✅ Security
- Players cannot modify HP, damage, or outcomes
- All calculations happen server-side
- No cheating via browser DevTools

### ✅ Single Source of Truth
- Game logic in one place (game_logic/ folder)
- No duplication between Python and JavaScript
- Easy to update rules consistently

### ✅ Session Persistence
- Player can refresh browser without losing progress
- Game state survives page reloads
- Session stored server-side (secure)

### ✅ Deferred Actions
- Conduit closure deferred until the right narrative moment
- Actions can be queued and executed at proper time
- Dramatic timing preserved

### ✅ Scalability
- Frontend independent of game logic
- Easy to build different frontends (mobile, CLI, etc.)
- Backend can support multiple players

### ✅ Maintainability
- Game logic stays in Python (familiar, easy to debug)
- Frontend stays in JavaScript (display only)
- Clear separation of concerns

---

## Testing the Architecture

### 1. Start the server
```powershell
python app.py
# Server running on http://localhost:5000
```

### 2. Test API endpoints directly
```powershell
# Start a new game
curl -X POST http://localhost:5000/api/game/start

# Get current story node
curl http://localhost:5000/api/story/node

# Make a choice
curl -X POST http://localhost:5000/api/story/choice `
  -H "Content-Type: application/json" `
  -d '{"choice_id": 1}'

# Travel to airport
curl -X POST http://localhost:5000/api/travel/travel `
  -d '{"airport_index": 0}'
```

### 3. Open browser
```
http://localhost:5000
```

The AJAX architecture will:
1. Load index.html (single page)
2. Fetch mainMenu.html via AJAX
3. Handle all interactions via fetch() API calls
4. Update DOM based on JSON responses
5. Maintain game state in Flask sessions

---

## Key Takeaways

| Concept | Details |
|---------|---------|
| **AJAX/SPA** | Single index.html, all content loaded dynamically via JavaScript |
| **Deferred Closure** | Conduit closed at story node, not at button click |
| **Session State** | Player, run_state, game_state stored in Flask sessions |
| **Module Separation** | blueprints/ (routes), game_logic/ (rules), static/js/ (display) |
| **No Duplication** | Game logic in Python only, JavaScript just displays results |
| **Request/Response** | Fetch JSON, JavaScript renders it, always through session |

This architecture makes Rites of Transit:
- **Secure**: Rules enforced server-side
- **Responsive**: AJAX feels like desktop app
- **Maintainable**: Logic centralized in Python
- **Dramatic**: Actions execute at the right story moment
