import sys
import time
from game.writing_effects import print_typewriter, flicker_line
from .combat import combat as run_combat
from .enemies import create_enemy
from .player import Player
from .manifestations import manifestation_library
from .items import add_weapon_to_inventory, add_item_to_inventory
from .music import play_music
from .ui import display_hud
from Doomclock.doomclock import doom_clock


# Utility Functions
def slow_print(text):
#    """Print text slowly for immersion."""
    print_typewriter(text + "\n")
#    for char in text:
#        sys.stdout.write(char)
#        sys.stdout.flush()
#        time.sleep(delay)
#    print()

def wait_for_input():
    """Wait for player to press Enter."""
    input("\n[Press Enter to continue...]")

def make_choice(options):
    """Display numbered options and return player’s choice."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        choice = input("Choose: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice. Try again.")

# Story Functions
def intro():
    slow_print("""=== Chapter I: Crimson Veil ===\n
    Arrival at Helsinki Airport...
    The plane lands with a shudder that rattles your molars...
    You step into Helsinki Airport, your footsteps echoing against marble where a hundred others should drown them out...

    The digital departure board flickers,
    numbers dissolving into static before reassembling.

    A janitor's cart sits abandoned mid-corridor, mop water gone still as glass.
    Ceiling lights buzz and dim in sequence.
    Casting your shadow in three directions at once.
    A child's forgotten teddy bear watches you from a bench with eyes that seem to follow.""")
    wait_for_input()
    dark_hallway()

def dark_hallway():
    slow_print("""    A corridor stretches ahead, marked 'Terminal' in faded letters...

    Your footsteps echo against tile, then suddenly stop—sound swallowed mid-step.
    Thirteen meters in, the fluorescent lights end abruptly, leaving a wall of black.
    You squint, but can't make out even the outline of walls beyond—just absence where substance should continue.""")
    wait_for_input()
    hallway_decision()

def hallway_decision():
    while True:
        choice = make_choice([
            "Step inside and investigate",
            "Leave it alone"
        ])
        if choice == 1:
            where_shadows_bled()
            break
        else:
            slow_print("Fate loops you back — you cannot escape this path.")

def where_shadows_bled():
    slow_print("""    You step into the black hallway.
    The temperature plummets ten degrees.
    Your lungs strain against air thick as oil.

    Thirteen paces in, your shoe squelches in something wet
    dark liquid pooling around a crumpled form.
    Then your eyes adjust.

    Bodies. Dozens of them.
    Robes torn, faces twisted, their blood soaking the tiles in black-red rivers.
    Some still clutch ritual knives, others lie broken at unnatural angles, their expressions frozen in silent hymns cut short.
    Too many to count.
    Too many for one man to face.

    And yet, amid the ruin, one still breathes.""")
    wait_for_input()
    encounter_with_man()            

def encounter_with_man():
    slow_print("""    A hand shoots out, fingers trembling, smearing crimson across your wrist.
    Beneath a torn cassock, chest wounds bubble with each labored breath.
    Yellowed eyes, bloodshot and dilated, find yours with unsettling precision.

    The grip tightens—impossibly strong for someone losing so much blood.
    \"I… am Ezekiel,\" escapes through teeth stained red.
    \"Warden of the Threshold… protector of this world…\"""")
    wait_for_input()
    conduit()

def conduit():
    slow_print("""    Beside the Warden you see it.
    Not a machine. Not a sculpture.
    A wound in geometry itself,
    its angles folding inward and outward at once.
       
    It hums with a resonance that bypasses your ears,
    vibrating directly in your bones.
    Light and shadow pulse across its surface,
    alive in ways your mind refuses to parse.
       
    Ezekiel coughs, blood spattering across your sleeve.
    on His grip your wrist is iron.
    \"You must… shut it down. Touch it… before it opens fully...\"""")
    wait_for_input()
    first_conduit_decision()

def first_conduit_decision():
    while True:
        choice = make_choice([
            "Touch the conduit",
            "Refuse the man"
        ])
        if choice == 1:
            awakening()
            break
        else:
            slow_print('Ezekiel gasps: "You MUST close it... or all is lost!"')

def awakening():
    slow_print("""    Your palm meets the surface....
    It is not solid. It is not liquid.
    It is wrong.
    
    Agony detonates behind your eyes.
    Visions of stars that should not exist burn themselves into your sight.
    Something vast, something ancient, swivels its awareness toward you.
    
    The conduit collapses in on itself,
    a scream of light imploding into silence.
    
    You fall to your knees
    Lungs full of knives
    vision narrowed to a tunnel of shadows and pulse.

    It's not pain. It's not death. It's the knowing.
    That it's too much.
    That you were never meant to carry this.
    That some things were never meant to be seen.

    Then, like a cord snapping inside your chest, it happens.
    Something flees you.
    Not bravery. Not strength.
    Fear.

    The trembling you buried beneath decisions,
    the dread you swallowed to keep moving, rips loose.
    Not forced but freed, as if your mind could no longer hold the weight of its silence.
    It does not vanish. It recoils.

    The air folds around the absence like shivering cloth,
    and from it emerges a shape, twitching, angular, impossible to watch directly.
    It watches everything. It breathes in hesitation. it pulses with retreat.
    It waits.

    Not to defend you, but to outlive what breaks you.
    [MANIFESTATION UNLOCKED: **Fear**]
    It does not protect. It does not empower.
    But it will follow until your shadow forgets the sun.

    And in this place...
    That is enough to shape reality.""")
    doom_clock.countdown(1, player=None, enemies=None, log=None, reason="Conduit closure ripples time.")
    wait_for_input()
    shadows_stir()

def shadows_stir():
    slow_print("""    Ezekiel’s head lolls back,")
    but a faint smile clings to his ruined face.
    
    \"Good... you succeeded...\"
    
    His voice trembles on the edge of nothing.
    
    The air shifts.
    Where the conduit’s radiance once screamed,
    the shadows now stretch unnaturally long,
    sliding into cracks and corners where no light should reach.
    For the first time in hours, maybe days 
    daylight filters faintly into the hallway.
    
    But peace does not follow.
    
    A figure bursts from the broken light.
    Cloth robes of black and tattered crimson drape across its frame,
    etched with curling sigils that writhe like living things.
    Chains dangle from its sleeves, rattling in rhythm
    to the low hum of a hymn that never passes its lips.
    The hood slips back, revealing a face locked in rage — veins bulging, eyes fever-bright,
    mouth twisted as if reciting verses too terrible for sound.
    
    A cultist of the Hymn of the Old Ones.
    
    It sees you. And it moves.""")
    wait_for_input()
    ezekiels_warning()

def ezekiels_warning():
    slow_print("""    Before the zealot can close the distance, Ezekiel rasps,
    a sudden force behind his fading voice:
    "You must endure yet another hurdle. But fear not… I will guide you."
    
    His bloodied hand trembles as he points at your chest.
    
    \"The conduit marked you. You carry within you.... manifestations.\"
    \"Powers pulled from knowledge that no mind should touch.\"
    \"I cannot see what gift has taken root first\"
    \"but know this: each manifestation draws on your sanity.\"
    \"Spend too much, and you will lose yourself.\"
    \"Spend wisely, and you will survive.\"
    
    His words linger, as though pressed into your skull itself.""")
    wait_for_input()
    combat_scene()

def combat_scene():
    slow_print("""    ⚔ Combat Tutorial ⚔")
    Ezekiel's voice steadies you: \"This one is weak. Learn quickly.\"
    I'll show you how to act in battle: Attack, Defend, Manifest, Inventory, and Reload.""")

    tutorial_player = Player("You", unlocked_manifestations=[manifestation_library["Fear"]])
    
    # Starter gear and items so the menus make sense
    add_weapon_to_inventory(tutorial_player, "Basic dagger")
    add_item_to_inventory(tutorial_player, "Small Health Potion")

    slow_print("""    Ezekiel: \"First, equip a weapon from your inventory.\"
    \"Then try a simple Attack. Choose a target and strike.\"
    \"You can also Defend to halve the next hit, or open Inventory to use a potion.\"
    \"And the power within you — Manifest — spends sanity for stronger effects.\"
    \"Reload is only relevant if you're using a firearm.\"""")
    wait_for_input()

    # Spawn a simple enemy for practice
    enemies = [create_enemy("Tutorial")]

    # Run the real combat loop
    run_combat(tutorial_player, enemies, doom_clock)

    slow_print("\"Good. You grasp the rhythm — act, endure, and press on.\"")
    wait_for_input()
    aftermath()

def aftermath():
    slow_print("""    The cultist crumples to the ground, robes pooling like spilled ink...
    The hymn dies in its throat, leaving only the sound of your heartbeat and Ezekiel’s wheezing breath.
    
    The corridor is quiet again,
    but your hands tremble — from exertion, from power,
    \"from something you can no longer deny is inside you.\"
    
    Ezekiel watches, weak eyes gleaming faintly.
    \"Yes… you see now. You have survived.\"
    \"But survival is only the beginning.\"""")
    wait_for_input()
    final_words()

def final_words():
    slow_print("""    His body convulses with another cough, crimson flecking his lips.
    Still, he forces the words out, urgent and deliberate:
    
    \"You must continue my work.\"
    \"The conduits… they are at airports across the world.\"
    \"Only you can close them now....\"

    He presses a crumpled, blood-stained note into your palm.
    Scribbled names of airports, written in haste, blur beneath smears of red.

    His grip slackens.
    With a final ragged breath,
    Ezekiel collapses into silence.

    The hallway feels colder without his voice.
    And in your hand, the note feels heavier than paper has any right to be.""")
    wait_for_input()
    #end_game()

#def end_game():
#    slow_print("GAME OVER – or perhaps just the beginning...")
#    slow_print("   ")
#    slow_print("............STORY STUFF............")
#    slow_print("  ")
#    print(f"\nFinal Sanity: {player['sanity']} | Powers: {player['power']}")


## Pete addendum
_CURRENT_TRACK = None
def set_music(spec):
    # Apply music at node or line level
    from .music import play_music, stop_music
    global _CURRENT_TRACK
    if not spec:
        return
    
    action = spec.get("action", "play")
    if action == "play":
        track = spec.get("track")
        if not track:
            return
        if _CURRENT_TRACK != track:
            play_music(track, volume=spec.get("volume", 0.12), loop=spec.get("loop", False))
            _CURRENT_TRACK = track
        else:
            # Allow volume changes while continuing the same track
            from .music import set_volume
            if "volume" in spec:
                set_volume(spec["volume"])
            # If the same track is requested but nothing is playing (e.g., after a fadeout), restart it
            try:
                import pygame
                if not pygame.mixer.music.get_busy():
                    play_music(track, volume=spec.get("volume", 0.12), loop=spec.get("loop", False))
                    _CURRENT_TRACK = track
            except Exception:
                pass
    
    elif action == "fadeout":
        import pygame
        pygame.mixer.music.fadeout(int(spec.get("fade_ms", 1200)))
        # Mark current track as cleared so a subsequent play of the same track restarts properly
        _CURRENT_TRACK = None
    
    elif action == "stop":
        stop_music()
        _CURRENT_TRACK = None
    
def run_combat_spec(spec, player):
    if not spec: return
    from .music import play_music
    from .enemies import create_enemy
    from .combat import combat as run_combat
    if track := spec.get("music"):
        try: play_music(track, volume=0.12)
        except Exception: pass
    enemies = [create_enemy(n) for n in spec.get("enemies", [])]
    # Pass a provided doom_clock if present in spec, otherwise fall back to the module-level doom_clock
    run_combat(player, enemies, spec.get("doom_clock") or doom_clock)

def run_story(start_key, player, story_map, print_line, wait_for_input, make_choice_func):
    key = start_key
    while key:
        node = story_map.get(key)
        if not node:
            print_line(f"[Story node not found: {key}]")
            return
        
        # Node music change before text
        set_music(node.get("music"))

        # 1) Text
        text = node.get("text", [])
        if isinstance(text, str):
            text = [text]
        for entry in text:
            if isinstance(entry, dict):
                # on the fly changes for music
                set_music(entry.get("music"))
                line = entry.get("line", "")
                if line:
                    print_line(line)
            else:
                print_line(entry)
                
        if node.get("wait", True):
            wait_for_input()
        # 2) Combat (optional)
        run_combat_spec(node.get("combat"), player)

        # 3) Doom Clock
        if "doom_tick" in node:
            doom_clock.countdown(
                node["doom_tick"],
                reason=node.get("doom_reason", "As the conduit closes so does time..."),
            )
            display_hud(player, doom_clock)

        # 4) Choices (optional)
        choices = node.get("choices")
        if choices:
            labels = [c.get("label", "...") for c in choices]
            sel = make_choice_func(labels)
            # clamp selection just in case
            idx = max(1, min(sel, len(choices))) - 1
            key = choices[idx].get("next")
            continue
        # 5) Goto / end
        next_key = node.get("goto") or node.get("next")
        if node.get("quit"):
            print_line("[The story concludes. Exciting...]")
            sys.exit()
        if node.get("end") or not next_key:
            return
        key = next_key
    
STORY_MAP = {
# === SECOND CONDUIT STORY START ===
    "2_conduit": {
        "music": {"action": "play", "track": "Music/ambience/Tension_rise.mp3", "volume": 0.12, "loop": True},
        "text": [
            """\n=== Chapter II: Echoes of the Abyss ===\n\n
    The journey leaves you hollow. Another airport.
    Another silence where life should be.
    But this time it isn’t empty.

    Figures linger ahead, robes shifting like shadow and blood.
    Their chants rise and fall, a hymn that claws at your skin.

    Most you recognize, the same cultists who fell in Helsinki.
    But one stands apart.
    A heavy tome rests in his hands,
    its pages breathing with symbols that squirm like insects across the paper.

    When he speaks the air itself seems to recoil.

    \"I am an Apostle of the Hymn\"

    His eyes narrow, fixing you with disbelief.

    \"What business does a stray civilian have here?\"
    \"How did you breach the veil?\"\n""",
        ],
        "wait": True,
        "choices": [
            {
                "label": "Bluff your way past",
                "next": "second_conduit.doubt"
            },
            {
                "label": "Attack",
                "next": "second_conduit.attack"
            }
        ]
    },
# === SECOND CONDUIT DOUBT ===
    "second_conduit.doubt": {
        "text": [
            """    You steady your breath and speak not with certainty,
    but with something stranger: conviction borrowed from the terror behind your eyes.

    \"The Hymn called to me,\" you say.

    The Apostle flinches, almost imperceptibly.
    Behind him, the cultists falter in their chant, their rhythm bending like warped vinyl.
    The air thickens.
    You step forward.

    \"I dreamed the ink before I saw the page.

    I heard the name that hides between syllables.

    I walked the corridors that pulse beneath waking thought.\"

    The Apostle watches. Measuring.
    Somewhere behind his gaze, a calculus unfolds — ancient, inhuman, suspicious.
    Then, slowly, he lowers the tome.

    \"If that were true… then the Hymn has changed its key.\""

    A pause.

    \"Perish knave.\""""
        ],
        "wait": True,
        "next": "second_conduit.attack"
    },
    "second_conduit.attack": {
        "text": [
            "You charge forward, your heart pounding in your chest."
        ],
# === SECOND CONDUIT COMBAT ===
        "wait": False,
        "combat": {
            "enemies": ["Apostle", "Cultist", "Cultist"],
            "music": "Music/combat/Behind_you.mp3"
        },
        "end": True
    },
# === SECOND CONDUIT AFTERMATH ===
    "2_conduit.aftermath": {
        "music": {"action": "fadeout", "fade_ms": 1500},
        "text": [
            """\nAt last,
the chanting dies.
The Apostle falls silent,
his book closing with a sound like bone breaking.            
            """
        ],
        "wait": True,
        "next": "whispering_conduit"
    },
# === WHISPERING CONDUIT ===
    "whispering_conduit": {
        "music": {"action": "play", "track": "Music/ambience/Tension_rise.mp3", "volume": 0.12, "loop": True},
        "text": [
            """=== The Whispering Conduit ===
    You draw closer to the conduit.  
    The air thickens.  
    Each step drags against unseen weight.  
    Whispers.  
    Not sound, but intrusion.  
    A pressure that seeps into the marrow,  
    curling around thought and dream alike.  
    They flood your skull in a tongue not meant for man
    and yet, you *understand*.  

    A presence. Vast. Ancient.  
    It does not speak *to* you, but *around* you,  
    as though idly acknowledging a gnat that landed in its shadow.  

    \"...a hand that should not reach, reaches.\"  
    \"...an eye that should not open, blinks.\"  

    The tone is neither threat nor greeting.  
    It is amusement.  

    \"You scurry, little one.  
    You paw at threads unseen.  
    For that… I will leave you a morsel.\"  

    A pull gnaws at your chest,  
    offering warmth, a whisper of clarity,  
    The promise of an easier path,  
    less hunger in the nights to come,  
    the veil of fear thinned for your tiny mind.  
    All you must do…  
    is step away.  
    Leave the wound unhealed.  
    Forget you saw it.  

    The presence stirs,  
    like a tide withdrawing,  
    already forgetting your shape.\n"""  
        ],
        "wait": True,
        "choices": [
            {
# === WHISPERING CONDUIT CHOICES ===
                "label": "Accept the \"gift\" and leave the conduit intact",
                "next": "whispering_conduit.acceptance"
            },
            {
                "label": "Defy the voice — close the conduit",
                "next": "whispering_conduit.defiance"
            }
        ]
    },
# === WHISPERING CONDUIT ACCEPTANCE ===
    "whispering_conduit.acceptance": {
        "text": [
            """=== Acceptance: The Dream of Normalcy ===
    You stop.  
    The whispers seep deeper, curling like smoke through every corner of thought.  
    And in that moment, you realize:  
    you don’t want this fight.  
    You never wanted it.  
    Not blood.  
    Not terror.  
    Not shadow‑cloaked wars with gods you cannot fathom.  
    Just peace.  
    Just normalcy.  

    You bow your head.  
    A wordless assent leaves your lips,  
    a contract signed in silence.  
    Something tears.  
    Not flesh. Not bone.  
    Something within you.  
    A sliver of self unspools and drifts away, claimed by the unseen hand.  
    Darkness folds around you.  
    Consciousness unravels.  
    And then  

    \"Wake up already, you’re going to be late!\"  

    Your eyes snap open.  
    Sunlight filters through cheap blinds.  
    The hum of morning traffic bleeds through the walls.  
    You stumble upright, heart hammering.  
    No cultists.  
    No conduits.  
    No blood.  
    Just the familiar clutter of your dorm room.  
    It’s 9:15.  
    You’re late for class.  

    You rush through the motions,  
    pulling on jeans, slinging your bag over your shoulder.  
    Something nags at you.  
    Why did you jolt awake like that?  
    Like a soldier out of a dream of battle.  
    Like a hero torn from an action reel.  

    But the thought slips away.  
    Whatever it was, it doesn’t matter now.  
    Everything feels… easier.  
    The walk across campus.  
    The chatter of classmates.  
    The words of the professor flowing like water.  

    Was it always like this?  
    Or is something new humming just beneath the surface?  
    The question lingers,  
    a splinter your mind refuses to touch.  

    You laugh softly to yourself.  
    What a dumb thought.  
    This isn’t a game.  
    This isn’t a story.  
    This is real life.  
    And life has never been better.  


[ENDING: Blissful Ignorance]"""
        ],
        "wait": True,
        "end": True,  # marks this as an ending
        "quit": True
    },
# === WHISPERING CONDUIT DEFIENCE ===
    "whispering_conduit.defiance": {
        "text": [
            """=== Defiance ===
    Your hand presses against the conduit.  
    The whispers falter.  
    Then sharpen.  
    The amusement rots into something colder,  
    a ripple of disdain.  

    Agony rips through your body  
    as the structure convulses,  
    imploding into itself with a scream  
    that no throat could ever make —  
    screaming silently into absence.  

    You fall, trembling, lungs ragged.  
    Alive but not unmarked.  

    For a moment, you are sure this is the end.  
    Not death.  
    Defeat.  
    The quiet, smothering certainty that nothing will ever change.  
    That no action matters.  
    That you are too small,  
    too late,  
    too alone.  

    And in that moment,  
    something inside you breaks.  
    Not comfort. Not salvation.  

    Hope.  

    The fragile light you clung to in the dark,
    the quiet belief that it could still matter,
    slips from your grasp, not torn, but surrendered,
    as if even your soul had grown too tired to hold it.

    it does not vanish.
    it lets go.

    it rises not in brilliance,
    but in stillness.
    Pale light, gentle and unearned,
    folding into shape like a prayer long forgotten.

    It watches you,
    not with judgment,
    but with grief.

    a hollowed reflection of what you once needed to believe.
    not to survive but to endure.

    [MANIFESTATION UNLOCKED: **Hope**]  

    It does not bring comfort.  
    It does not restore what was lost.  
    But it will linger until the void swallows you whole.  

    And in this place,  
    that is enough to shape reality.  

    Before the presence withdraws,  
    a thought lingers in the hollow of your mind:  

    "You gnawed the hand that brushed you.  
    I will remember."  

    And then…  
    silence.  

    The conduit is gone.  
    But the weight of its notice remains.  
    And within the vacuum left behind,  
    Hope flickers.  
    No longer yours.  
    Now something else entirely."""
        ], 
        "doom_tick": 1,
        "doom_reason": "As the conduit closes so does time...",
        "wait": True,
        "end": True  # also an ending, or chain to another node
    
# === THIRD CONDUIT STORY START ===

    },
    "3_conduit": {
        "music": {
            "action": "play",
            "track": "Music/ambience/Airport_dread.mp3",  # Change to your actual track
            "volume": 0.12,
            "loop": True
        },
        "text": [
            "\n=== Chapter III: Withering Flame ===\n\n",
            """    The plane screeches into the station, brakes screaming like metal in agony.  
    You step onto the platform, suitcase wheels abandoned long ago.  

    The airport yawns ahead.  
    Not bustling. Not alive.  
    A hollow carcass of glass and steel.  

    Departure screens flicker with flights that do not exist,  
    destinations that shift too quickly for the eye to follow.  

    Luggage belts churn with no cargo.  
    Only empty suitcases circle endlessly, their tags smeared with ink that looks like veins.  

    And there at the far end of the hall,  
    Yet another conduit.  
    Yet another promise of nothing but ruin.  

    You walk, though each step feels heavier than the last."""
        ],
        "wait": True,
        "next": "3_first_encounter"
    },
    "3_first_encounter": {
# === THIRD CONDUIT FIRST ENCOUNTER ===
        "text": [
            "\n=== First Encounter ===\n",
            """    The glow intensifies.  
    But you are not alone this time.  

    Figures step from the shadows.  
    Three, then six, then a dozen.  
    Robes of the cult, black and crimson, blades in hand.  

    And at their front — a man draped in heavy vestments, embroidered with spiraling sigils.  
    A High Priest.  
    His eyes gleam with fevered ecstasy.  

    \"So the Order sends another pawn,\"  

    his voice echoes, half sermon, half condemnation.  

    \"You think yourself savior, but you only tighten the chains of this world.\"  

    He raises his hands.  
    The cultists chant.  
    And the air shudders like a drumskin."""
        ],
# === THIRD CONDUIT COMBAT ===
        "wait": False,
        "combat": {
            "enemies": ["Cultist", "Cultist", "Cultist", "Apostle", "High Priest"],
            "music": "Music/combat/Invocation.mp3"
        },
        "end": True
    },
# === THIRD CONDUIT AFTERMATH ===
    "3_first_encounter.aftermath": {
        "music": {
            "action": "fadeout",
            "fade_ms": 1500
        },
        "text": [
            "\nThe chanting ends with a final gurgled breath.\n",
            "The High Priest collapses,\n",
            "his vestments darkening with spreading blood.\n",
            "The air still hums with the weight of their ritual, but for now, it is over.\n",
        ],
        "wait": True,
        "next": "3_conduit_encounter"
    },
    "3_conduit_encounter": {
        "music": {
            "action": "play",
            "track": "Music/ambience/Airport_dread.mp3",
            "volume": 0.12,
            "loop": True
        },
        "text": [
# === THIRD CONDUIT ENCOUNTER ===
            "=== The Conduit ===\n",
            """    Bloodied, gasping, you press onward.  
    The cultists lie broken, their hymn silenced  
    but the glow has grown louder than any chorus.  

    The conduit looms.  
    Angles that do not meet, geometry that sneers at Euclid.  
    A wound in the world.  

    The whispers begin again.  
    No. Stronger this time.  
    They do not seep.  
    They *hammer*.  

    A chorus of voices, overlapping, endless.  
    Language unspoken, yet every word burns meaning into your skull.  

    *We see you.*  
    *We know you.*  
    *Little flame crawling where fire does not belong.*  

    Your head throbs.  
    Your vision fractures.  

    And then, like a serpent coiling close, one voice cuts through the cacophony.  
    Silken, amused.  

    *You bleed. You break. For what?*  
    *Close this gate, and another will open. And another. And another.*  
    *What you destroy today, we will birth tomorrow.*  

    *Take ease, child. You may rest. You may live. We will grant you dreams unspoiled by terror.*\n"""
        ],
# === THIRD CONDUIT ENCOUNTER CHOICES ===
        "wait": False,
        "choices": [
            {
                "label": "Accept the deal",
                "next": "3_conduit_encounter.accept"
            },
            {
                "label": "Defy the voice and close the conduit",
                "next": "3_conduit_encounter.defy"
            }
        ]
    },
# === THIRD CONDUIT ACCEPTANCE ===
    "3_conduit_encounter.accept": {
        "text": [
            "=== Acceptance: The Dream of Triumph ===\n",
            """    Your hand falls away from the conduit.  
    The whispers curl closer, warm and cold at once.  
    A voice like velvet, like oil, like nothing human at all slides beneath your ribs.  

    *So small, yet so stubborn. But even ants may dream.*  

    And then the airport melts.  
    Glass and tile dissolve into gold and light.  

    You are standing on a stage.  
    Thousands of faces blur together, shouting your name.  
    Flashbulbs explode like stars.  

    You are brilliant.  
    Famous.  
    Powerful.  
    Whatever you ever wanted to be, you are.  
    Awards, lovers, riches, influence  
    each one is placed in your hands like an offering.  

    Days become weeks.  
    Weeks become years.  

    Your image glows from billboards.  
    You sign books you don’t remember writing.  
    You accept accolades for deeds you don’t recall performing.  
    Everyone smiles when they see you.  
    Everyone knows your name.  

    And yet…  

    Every cheer sounds the same.  
    Every face, in every crowd, has the same fixed smile.  
    Every night the champagne tastes like dust.  
    Every morning the mirror shows someone a little less real than the day before.  

    Sometimes, in the space between dreams,  
    you remember something.  
    Airports.  
    Whispers.  
    Blood.  
    A man dying, reaching for you.  

    But the memory dissolves before you can hold it.  
    A voice you cannot name purrs against your skull:  

    *Sleep. Shine. Smile.*  
    *It is all we ask.*  

    You nod without realizing.  
    And the dream swallows you whole.  

[ENDING: False Glory]"""
        ],
        "wait": True,
        "end": True,
        "quit": True
    },
# === THIRD CONDUIT DEFY ===
    "3_conduit_encounter.defy": {
        "text": [
            "=== Defiance: The Anatomist ===\n",
            """    You scream into the conduit’s light.  
    Your hand strikes its surface.  
    Agony rips through you  
    not like fire, but like pages torn from a book.  

    You collapse, choking on the taste of iron.  
    The world swims red at the edges.  
    And in the hollow between your heartbeat,  
    you feel it happen.  

    Something leaves you.  
    Not justice.  
    Not truth.  

    Resentment.  

    The festering kernel of every slight,  
    every wound endured,  
    every injustice that lodged itself inside you  
    and never found release.  

    It does not vanish.  
    It remembers.  

    Sloughing away from your psyche like rotted skin,  
    but hardening, coiling,  
    taking form in the world.  

    It glares at you with your own bitterness.  
    It breathes with your own hate.  
    And it smiles with the knowledge  
    that to hurt others is to heal itself.  

    [MANIFESTATION UNLOCKED: Resentment]  

    It will not console you.  
    It will not make you whole.  
    But it will cling until nothing remains but hunger.  

    And in this place,  
    that is enough to shape reality.  

    The conduit collapses, its geometry snapping inward with a final shriek.  
    But silence does not follow.  

    From the ruin, a scraping sound.  
    Metal against tile.  
    Slow. Heavy.  
    Deliberate.  

    A shadow emerges.  
    Tall.  
    Too tall.  

    Tattered surgical cloth hangs from its frame,  
    splashed with stains long since dried black.  
    Its face is hidden behind cracked glass and twisted steel,  
    a surgeon’s mask fused into flesh.  
    In one hand, it drags a scalpel as long as your arm,  
    its edge chipped, pitted, yet impossibly sharp.  

    Its voice is the screech of rust and the hum of bone saws:  
    \"The whispers spoke true.  
    At last, a specimen worthy of study.\"  

    It raises the scalpel, twitching in anticipation.  
    \"You will show me how much can be carved away before the soul expires.\"  

    It takes steps closer in increasing tempo.  
    The scalpel sings across the floor.  
    And you realize  
    you are not facing a foe.  
    You are facing an experiment. \n"""
        ],
        "doom_tick": 1,
        "doom_reason": "As the conduit closes so does time...",
        "wait": True,
        "end": True
    },

    "defiance_anatomist.combat": {
        "wait": False,
        "combat": {
            "enemies": ["Anatomist"],
            "music": "Music/combat/Invocation.mp3"
        },
        "end": True
    },
# === ANATOMIST AFTERMATH ===
    "anatomist.aftermath": {
        "music": {
            "action": "play",
            "track": "Music/ambience/Airport_dread.mp3",
            "volume": 0.12,
            "loop": True
        },
        "text": [
            "=== Aftermath ===\n",
            """    The Anatomist crumples, scalpel clanging against the floor,  
    its final rattle echoing through the empty concourse.  

    You stagger, body broken, mind splintered.  
    But alive.  

    For now.  

    The silence that follows is not complete.  
    In the edges of your hearing, a thousand murmurs stir  
    not angry.  
    Not disappointed.  
    *Amused.*  

    You know now:  
    the cult is not the true danger.  
    They are tools. Pawns. Distractions.  

    Each conduit closed draws more attention.  
    Each act of defiance makes the abyss lean closer.  

    And the Anatomist was not alone.  
    Others wait.  
    Others watch.  
    And each one is *for you*.  

    You press onward.  
    Because you must.  
    Because there is no other choice.\n"""
        ],
        "wait": True,
        "end": True,
    },
# === FOURTH CONDUIT STORY START ===
"4_conduit": {
    "music": {
        "action": "play",
        "track": "Music/ambience/Chaos_in_terminal.mp3",
        "volume": 0.12,
        "loop": True
    },
    "text": [
        "\n=== Chapter IV: The Fractured Sky ===\n\n",
        """    The airport doors part with a hiss,  
    but the air that greets you is not air.  
    It is heavy. Grainy.  
    Every breath scratches down your throat like sandpaper.  

    The terminal is not quiet, yet no sound belongs.  
    Screens flicker between flights and visions,  
    departure times woven with sigils that pulse like veins.  
    A child’s laughter echoes from nowhere,  
    then cuts into a scream that never finishes.  

    Reality is crying out.  
    The veil tears with every heartbeat,  
    its seams stretched thin against what presses from the other side.  

    For a moment, doubt claws at you.  
    Ezekiel’s words echo, but so do theirs.  
    They called you dust.  
    An insect.  
    Something to be brushed aside by inevitability.  

    Your hand trembles.  
    But you remember Ezekiel’s conviction,  
    his eyes in that last moment,  
    and you force steel into your spine.  

    This cannot be the wrong path.\n""",
    ],
    "wait": True,
    "next": "4_greeting"
},

# === FOURTH CONDUIT GREETING ===
"4_greeting": {
    "text": [
        "\n=== The Greeting ===\n\n",
        """    The cult is waiting.  
    Not hiding.  
    Waiting.  

    Their robes catch no wind,  
    but sway as if submerged in water.  
    Eyes gleam from shadowed hoods,  
    some with hatred, some with a flicker of fear.  
    They know you now.  
    They speak your name in hushed whispers, half-curse, half-prayer.  

    But the fear dies quickly.  
    A new voice threads through the silence,  
    not from their mouths, but from the air itself.  

    Whispers.  
    Low, constant, maddening.  
    The same chorus that stalks your sleep, that gnaws the corners of your waking hours.  

    And then her.  

    One among them does not cease her chant when your gaze finds her.  
    Her lips move, spilling words not meant for this world,  
    but her eyes hold yours.  
    Cold. Measured.  
    Not rage. Not zeal.  
    Intent.  

    Your skull throbs with pressure.  
    Your teeth ache.  
    Her voice is not in your ears,  
    but in your marrow.  

    To them, you are not an enemy to defeat.  
    You are an obstacle to be erased."""
    ],
    "wait": False,
    "combat": {
        "enemies": ["Cultist", "Cultist", "Apostle", "High Priest"],
        "music": "Music/combat/your_fear.mp3"
    },
    "end": True
},

# === FOURTH CONDUIT ENCOUNTER ===
"4_conduit.encounter": {
    "music": {
        "action": "play",
        "track": "Music/ambience/Chaos_in_terminal.mp3",
        "volume": 0.12,
        "loop": True
    },
    "text": [
        "\n=== The Conduit ===\n\n",
        """    You stagger forward,  
    breath hitching,  
    toward the glow that stains the far end of the hall.  

    It is larger this time.  
    Hungrier.  
    The geometry buckles,  
    walls and floor warping in its radius,  
    as if reality itself recoils from the wound.  

    The whispers crescendo.  
    Not background.  
    Not distant.  
    They are here.  
    They are with you.  

    *You feel it, don’t you?*
    *The futility. The unraveling.*  
    *Already the air shreds. Already the skin of this world thins.*  

    Their voices coil like serpents through your thoughts.  
    Not desperate.  
    Not hurried.  
    Amused.  

    *You have entertained us, little flicker.*  
    *Defied us, clawed against the tide.*  
    *Dust should not burn so brightly.*  

    A pause, almost tender.  

    *One last deal, then.*  
    *Not for our need,*  
    *for our delight.*\n"""
    ],
    "wait": True,
    "choices": [
        {
            "label": "Accept the \"gift\" and leave the conduit intact",
            "next": "4_conduit.accept"
        },
        {
            "label": "Defy the voice — close the conduit",
            "end": True
        }
    ]
},

# === FOURTH CONDUIT ACCEPTANCE ===
"4_conduit.accept": {
    "text": [
        "\n=== Acceptance: The Crown of Nothing ===\n\n",
        """    You let the whispers in.  
    Not just into your mind, into your blood, your very name.  
    The conduit does not collapse this time.  
    It blossoms.  

    And so do you.  

    You awaken to thunderous applause.  
    No longer a terminal.  
    No longer dust.  

    You sit upon a throne carved from marble that remembers no quarry.  
    Banners drape from vaulted ceilings, each one bearing your sigil, your face, your victories, your will.  
    Before you stretch oceans of people, their heads bowed, their chants your name alone.  

    Power hums in your veins, no longer stolen, no longer borrowed.  
    It is yours.  
    Nations bend at your command.  
    Armies march where you point.  
    Even kings, even prophets, kneel at your feet.  

    You are not part of the machine.  
    You *are* the machine.  
    Every cog spins for you, every gear grinds to your design.  
    The world’s breath is your breath.  
    Its heart, your heart.  

    And yet  
    when the cheers fade,  
    when the banners ripple in silence,  
    you hear it.  

    The hollow echo.  
    The space between each praise,  
    the emptiness beneath every oath of loyalty.  
    Their eyes never meet yours.  
    Their mouths move, but their smiles are painted, stretched too wide.  

    You try to speak  
    but your words vanish before leaving your lips,  
    absorbed into the silence like stones into water.  

    A crown weighs heavy on your head.  
    Too heavy.  
    Crushing.  

    And in the quiet between breaths, you realize  
    you are not their ruler.  
    You are their entertainment.  
    Their puppet.  

    A monarch seated on a stage,  
    adored by phantoms,  
    caged in a fantasy that is not yours.  

    Still, you wear the crown.  
    You wave to the masses.  
    You sit upon the throne of Nothing.  

    And you never wake again.  

[ENDING: The Crown of Nothing]"""
    ],
    "wait": True,
    "end": True,
    "quit": True
},

# === FOURTH CONDUIT DEFIANCE ===
"4_conduit.defy": {
    "text": [
        "\n=== Defiance ===\n\n",
        """    Your hand meets the conduit.  
    Agony.  
    Always agony.  

    But this time, the whispers do not recoil.  
    They converge.  
    A chorus not of promises, but of hunger  
    a tide pressing against the walls of your skull.  

    You stagger, doubled over, chest heaving with fire.  
    The world swims red, your veins screaming, your heart pounding too fast,  
    too loud.  

    And then it happens.  

    Something inside you tears free.  
    Not righteous.  
    Not heroic.  

    **Rage.**  

    The seething ember you buried for so long,  
    the raw defiance that carried you here,  
    splinters away, ripped out as though your soul itself could no longer contain it.  

    It does not vanish.  
    It ignites.  

    Heat coils in the air before you, black smoke bleeding from nothing,  
    shaping itself into a figure: towering, sharpened,  
    a mirror of your fury.  

    Its eyes burn like coals, its stance unyielding,  
    its every breath a snarl at existence itself.  

    [MANIFESTATION UNLOCKED: **Rage**]  

    It does not soothe.  
    It does not forgive.  
    But it will remain until your light burns out.  

    And in this place,  
    that is enough to shape reality.  

    The conduit collapses, shrieking,  
    its geometry unraveling like a noose pulled tight.  
    Shadows snap back into the corners,  
    but the air does not lighten.  

    No.  
    Something remains.  
    Something answers.  

    From the rippling dark steps a figure  
    veiled in funeral wrappings damp with brine,  
    robes dragging wet across the tiles,  
    leaving puddles where no water should be.  

    Chains of barnacle-eaten iron hang from its arms,  
    clinking like bells rung underwater.  

    It does not look at you.  
    Not at first.  
    Its head tilts back,  
    the veil trembling as it begins to sing.  

    The sound is not sound.  
    It is pressure.  
    A dirge pressed into the marrow of your bones.  
    Each note pulls something from the air  
    from the deep.  

    The tiles crack. The air ripples.
    Forms slither through, faceless and half-formed,
    fragments of drowned psyches dragged screaming from the void.
    They trash without mouths, claw without fingers,
    ravenous for flesh, for a host.slow_print

    The Dirge lowers its head now.
    and it looks at you. Through you.

    You realize, too late, it has been singing for you all along."""
        ],
        "doom_tick": 1,
        "doom_reason": "As the conduit closes so does time...",
        "wait": True,
        "combat": {
            "enemies": ["Dirge of the Deep"],
            "music": "Music/combat/Let_the_fragments_work.mp3"
        },
        "end": True,
    },
# === FOURTH CONDUIT AFTERMATH ===
    "4_conduit.aftermath": {
        "music": {
            "action": "fadeout",
            "fade_ms": 1500,
        },
        "music": {
            "action": "play",
            "track": "Music/ambience/Airport_dread.mp3",
            "volume": 0.12,
            "loop": True
        },
        "text": [
            """\n=== Aftermath ===\n\n
    The last fragment crumbles into nothing,
    its borrowed flesh unraveling like smoke in water.
    You stand alone in the corridor
    or so you think.

    The Dirge still lingers.
    Shattered, wounded,
    its veil torn open by your strikes.
    Beneath the dripping cloth,
    you glimpse not a face,
    but a cavity.
    A hollow where features should be,
    echoing with the resonance of drowned hymns.

    It reaches out, hand trembling,
    not toward you,
    but toward the void you cannot see.
    Its song falters
    one final note breaking,
    dissolving into a wet cough that shakes the walls.

    The fragments that had clawed at you recoil,
    sucked screaming back into the unseen deep.
    The Dirge shudders once more,
    then collapses,
    its body falling apart into slick rags and seawater
    that seep between the tiles.

    Silence.

    Not relief.
    Not safety.
    Only silence
    as if the airport itself holds its breath.

    Your chest heaves.
    Sanity frays at the edges,
    but you endure.

    And yet, as the stillness stretches,
    you realize something unshakable:
    the Dirge was not destroyed.
    It was cut off.
    Dragged back to wherever it called from,
    forced into retreat.

    Its hymn is not gone.
    It is only waiting.

    Your hand shakes as you steady yourself against the wall.
    The world wavers,
    like a picture about to tear through its own canvas.
    The air reeks of salt.
    And for the first time,
    you feel the conduit’s destruction has not weakened the Old Ones’ reach—
    but provoked them.

    One battle won.
    A war deepening.

    And the path to the next conduit feels heavier than ever before.\n"""
        ],
        "wait": True,
        "end": True
    },
     # === CHAPTER V: THE LAST ECLIPSE ===
    "5_conduit": {
        "music": {"action": "play", "track": "Music/ambience/Eclipse_arrival.mp3", "volume": 0.12, "loop": True},
        "text": [
            """\n=== Chapter V: The Last Eclipse ===\n\n
    The sky no longer behaves.

    It ripples like a mirage,
    bleeds like an open wound,
    shifts like something waking from a dream.

    From the plane window you watch reality buckle,
    Stars glimmer at noon.
    Shadows crawl without bodies.
    You see shapes moving between seconds,
    each too enormous to belong to your world.

    When the wheels screech to the tarmac,
    you know this is no arrival.
    This is an intrusion.

    The airport is a ruin of flickering light and bending glass.
    Reality here no longer fits.
    Girders stretch like wax.
    Hallways coil into themselves.
    And through every crack in the veil, something vast presses close.

    You step out.
    The air smells like salt and ash.
    Gravity stutters under your feet.

    Air shimmers with the passage of forms too colossal to name.
    They move not above, not below, but through.
    The veil is no longer holding.
    Time is no longer holding.

    This is not an airport anymore.
    It is a threshold.
    A mouth.
    And you are already inside.
    """
        ],
        "wait": True,
        "choices": [
            {
                "label": "Enter the chaos",
                "next": "5_conduit.chaos"
            }
        ]
    },
    
    "5_conduit.chaos": {
        "text": [
            """\n=== Chaos in the Terminal ===\n\n
    Cultists scatter through the concourse,
    their fervor broken into panic.

    Some claw their own faces bloody,
    shrieking at the visions that bloom before them.

    Others kneel, unblinking,
    their mouths hanging open to drink what drips through the cracks of reality.

    And some — the true believers —
    have begun to change.

    Spines twisting like wet rope.
    Eyes bloom like ulcers across their skin.
    Veins glowing with constellations not found on any map.
    Teeth sprouting in patterns that no god designed.

    The Starborn rise among the masses —
    the final reward for their devotion.
    Reaching for you with hands that remember being human.
    """
        ],
        "wait": True,
        "combat": {
            "enemies": ["Starborn", "Starborn", "Cultist"],
        },
        "next": "5_conduit.conduit"
    },
    "5_conduit.conduit": {
        "text": [
            """\n=== The Conduit ===\n\n
    You wade through ruin.
    What was once an airport is now a mausoleum of geometry,
    stained by blood and shadow alike.

    At last, the conduit reveals itself.
    It is no gate now.
    No wound.
    It is an eye.

    It opens in the air before you,
    a lidless pupil vast and depthless,
    gazing outward from a place where no gaze should reach.

    When it looks at you,
    every thought you’ve ever had shatters like glass.
    You are stripped to your essence,
    your struggles laid bare,
    your soul weighed and mocked.

    And then the voices.

    Not whispers.
    Not temptation.
    Resonances older than time,
    vibrations that ripple through the marrow of existence itself.

    "We warned you, ant.
    You scurry across the board, striking pieces, flipping tables.
    But the board remains. The game remains. The players remain."

    "Close this eye, and another will open.
    You may wound us. You may even delay us. But our gaze bends the seconds.
    Our thought drags stars in chains.
    We will outlast all."

    Each syllable is impossible, yet undeniable.
    it is not speech, it is a force.
    Presence older than stars, pressing against your mind,
    a reminder that your defiance is measured against eternity itself.
    """
        ],
        "wait": True,
        "choices": [
            {
                "label": "Close the eye",
                "next": "5_conduit.final_battle"
            }
        ]
    },
    "5_conduit.final_battle": {
        "text": [
            """\n=== Final Battle: The Abomination ===\n\n
    You step closer to the eye and as you touch it,
    you know, as you did in Helsinki that your touch can change the impossible.

    The eye convulses.
    The world convulses.

    Standing at the threshold Ezekiel once stood at,
    decades compressed into a single pulse of terror.

    Something tears through.

    It is not seen.
    It is not describable.
    It is only felt.

    Skin crawls with shapes your mind cannot keep.
    Your bones ache with frequencies that should not exist.
    Your very name sloughs away like wet paper.

    And yet it stands before you.
    The Abomination.

    A thing reality does not want,
    does not understand,
    yet cannot deny.

    The air screams as it takes form.
    Your body screams as you resist.
    """
        ],
        "wait": False,
        "combat": {
            "enemies": ["Abomination"],
            "music": "Music/combat/Final_battle.mp3"
        },
        "music" : {"action": "fadeout", "fade_ms": 1500},
        "next": "5_conduit.aftermath"
    },

    "5_conduit.aftermath": {
    "music": {
        "action": "play",
        "track": "Music/ambience/Epilogue.mp3",
        "volume": 0.12,
        "loop": True
    },
        "text": [
            """\n    The Abomination falls.
    It does not die.
    It cannot die.

    But you have weakened it.
    And the world itself rejects its presence.
    The abomination writhes, collapsing inward,
    and is sucked screaming back into the fracture.

    The eye shudders.
    Closes.
    And is gone.

    You fall to your knees, victorious.
    And empty.

    No agony comes this time.
    No ripping, no tearing.
    Only silence.

    Like a mirror cracking in perfect stillness,
    your mind fractures.
    Not into pain.
    Not into sorrow.
    But into nothing.

    Your thoughts fade.
    Your name fades.
    Your being fades.

    Were you ever here?
    Did any of this matter?
    The world you saved will rise tomorrow
    as if it had never been threatened.

    Tomorrow the flights will run again.
    Passengers will walk through spotless halls.
    Children will laugh at glass windows that look out on endless skies.
    And no one will remember that the sky once fractured.
    That the abyss once leaned close.

    And you, the ant who defied gods, will be gone.
    Not celebrated.
    Not mourned.
    Not even forgotten.

    Erased.
    """
        ],
        "wait": True,
        "next": "5_conduit.epilogue"
    },

    "5_conduit.epilogue": {
        "text": [
            """\n=== Epilogue ===\n\n
    The airport hums with its usual rhythm.  
    Rolling luggage.  
    Footsteps on tile.  
    Voices blending into a low, unbroken murmur.  

    On the departure board, flights click and shuffle.  
    Nothing strange.  
    Nothing out of place.  

    And yet—  
    the air feels lighter somehow.  
    Or heavier.  
    No one can decide.  

    A clerk behind the counter pauses,  
    pen hovering over paper,  
    unsure why her chest aches.  

    A pilot looks out at the clouds,  
    squinting as though trying to remember  
    what it was he just forgot.  

    A child clutches their parent’s hand,  
    eyes wide on nothing at all,  
    and whispers,  
    "I think I had a dream."  

    The parent hushes them gently,  
    and the crowd flows on.  

    No announcement is made.  
    No moment is marked.  

    Just a silence,  
    thin as paper,  
    threaded through the day.  

    And then life continues,  
    as it always has.  
    As it always will.  
"""
        ],
        "wait": True,
        "next": "5_conduit.ending"
    },

    "5_conduit.ending": {
        "text": [
            """    \n[The abyss murmurs] \n
    Written & Designed by:\n
    Petteri\n
    Jack\n
    Derej\n
    Pathirage\n

    [The void turns its gaze]

    Special thanks to you, the player,  
    the final witness,  
    the one who dared the conduit’s light.  

    Your steps are erased,  
    your name forgotten,  
    but the echo of your defiance  
    lingers in the dark.  

    THE END
    """
        ],
        "wait": True,
        "end": True,
        "quit": True
    },
}

