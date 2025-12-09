"""
doomclock_examples.py - Real-world usage examples for DoomClock in GameProjectSoftware2

These examples show how to integrate the doom clock into:
1. Combat encounters
2. Story progression
3. Flask API endpoints
4. Game initialization
"""

from typing import Dict, Any, Optional


# ============================================================
# EXAMPLE 1: Combat Endpoint Integration
# ============================================================

def example_combat_endpoint(session, player, combat_state, action: str, **kwargs):
    """
    Example Flask endpoint: POST /api/combat/action
    
    Integrates doom countdown into combat turns.
    Every turn player takes, doom decreases slightly.
    Special actions might decrease doom more.
    """
    from game_logic.doomclock_integration import (
        get_doom_clock_from_session, save_doom_clock_to_session
    )
    
    doom_clock = get_doom_clock_from_session(session)
    messages = []
    
    # Process the player's combat action
    # (assuming combat_engine.process_player_action exists)
    
    # For each round that passes, doom counts down
    doom_result = doom_clock.countdown(
        n=1,
        player=player.to_dict() if hasattr(player, 'to_dict') else {},
        enemies=[e.to_dict() if hasattr(e, 'to_dict') else {} for e in combat_state.enemies],
        log=messages,
        reason="Turn passed in combat"
    )
    
    # Save updated doom state
    save_doom_clock_to_session(session, doom_clock)
    
    # If doom reached zero, end combat immediately
    if doom_result['zero_triggered']:
        return {
            'success': False,
            'status': 'game_over',
            'message': 'The doom has reached zero. Reality collapses.',
            'doom': doom_result['percentage'],
            'messages': messages + doom_result['messages']
        }
    
    # Add milestone messages to response
    if doom_result['triggered_milestones']:
        messages.extend(doom_result['messages'])
    
    return {
        'success': True,
        'status': 'combat_continue',
        'doom': doom_result['percentage'],
        'messages': messages,
        'milestones_hit': doom_result['triggered_milestones']
    }


# ============================================================
# EXAMPLE 2: Story Node Progression
# ============================================================

def example_story_progression(session, player, current_node: str, choice_index: int = None):
    """
    Example: Story nodes can trigger doom countdown.
    
    Some story choices might:
    - Countdown doom (critical decisions)
    - Add time (solving mysteries)
    - Trigger milestones (approaching conduits)
    """
    from game_logic.doomclock_integration import (
        get_doom_clock_from_session, save_doom_clock_to_session
    )
    from game_logic.story_engine import process_story_node
    
    doom_clock = get_doom_clock_from_session(session)
    
    # Process the story node normally
    story_result = process_story_node(current_node, choice_index)
    messages = story_result.get('text', [])
    
    # Some nodes might have doom effects
    doom_effect = None
    if current_node == 'approach_conduit':
        # Approaching a conduit = doom increases by 2
        doom_effect = doom_clock.countdown(
            n=2,
            log=messages,
            reason="Approaching a conduit - reality warps"
        )
    elif current_node == 'solve_mystery':
        # Solving a mystery = gain time
        doom_effect = doom_clock.add_time(
            n=5,
            log=messages,
            reason="Mystery solved - temporal stability restored"
        )
    elif current_node == 'encounter_cultist':
        # Cultist encounter = doom ticks once
        doom_effect = doom_clock.countdown(
            n=1,
            log=messages,
            reason="Cultist ritual detected"
        )
    
    if doom_effect:
        story_result['doom_effect'] = doom_effect
        
        # Check for game over
        if doom_effect.get('zero_triggered'):
            story_result['game_over'] = True
            story_result['text'].append(
                "The final conduit opens. Reality crumbles. Game Over."
            )
    
    # Save doom state
    save_doom_clock_to_session(session, doom_clock)
    
    story_result['doom'] = doom_clock.get_percentage()
    return story_result


# ============================================================
# EXAMPLE 3: Game Initialization
# ============================================================

def example_game_initialization(session, difficulty: str = 'normal'):
    """
    Example: Initialize a new game with doom clock.
    Different difficulties have different starting doom values.
    """
    from game_logic.doomclock import create_default_doom_clock
    from game_logic.doomclock_integration import (
        create_hardcore_doom_clock, create_story_doom_clock
    )
    
    # Choose clock based on difficulty
    if difficulty == 'easy':
        doom_clock = create_default_doom_clock(start=200)
    elif difficulty == 'hard':
        doom_clock = create_default_doom_clock(start=50)
    elif difficulty == 'hardcore':
        doom_clock = create_hardcore_doom_clock(start=75)
    elif difficulty == 'story':
        doom_clock = create_story_doom_clock(start=100)
    else:
        doom_clock = create_default_doom_clock(start=100)
    
    # Store in session
    session['doom_clock_data'] = doom_clock.to_dict()
    session['difficulty'] = difficulty
    session['game_started'] = True
    
    return {
        'status': 'initialized',
        'difficulty': difficulty,
        'doom': doom_clock.get_percentage(),
        'doom_start': doom_clock.start
    }


# ============================================================
# EXAMPLE 4: Custom Milestone Callbacks for Special Events
# ============================================================

def example_custom_milestones(session):
    """
    Example: Create a custom doom clock with special events.
    These callbacks can trigger special story events, music changes, etc.
    """
    from game_logic.doomclock import DoomClock
    
    def at_90_percent(player: dict, enemies: list, log: list):
        """90%: First hint of trouble."""
        log.append("💀 Strange whispers echo in the distance...")
        # Could trigger a story event here
        session['story_event'] = 'whispers'
    
    def at_70_percent(player: dict, enemies: list, log: list):
        """70%: Reality becomes unstable."""
        log.append("⚡ The sky crackles with unnatural energy.")
        # Could change background music
        session['music_track'] = 'ominous'
    
    def at_40_percent(player: dict, enemies: list, log: list):
        """40%: Cultists appear."""
        log.append("🔮 Robed figures materialize from shadow.")
        # Could trigger combat or story branch
        session['story_event'] = 'cultist_encounter'
    
    def at_10_percent(player: dict, enemies: list, log: list):
        """10%: Final warning."""
        log.append(
            "⚠️ THE CONDUITS SCREAM. REALITY TEARS. "
            "YOU HAVE MOMENTS LEFT."
        )
        # Urgent UI notification
        session['ui_alert'] = 'critical'
    
    def at_zero_percent(player: dict, enemies: list, log: list):
        """0%: Game Over."""
        log.append(
            "💀 Darkness consumes all. The Sleeper awakens. "
            "Your world ends."
        )
    
    # Create clock with custom milestones
    doom_clock = DoomClock(
        name="Custom Doom",
        start=100,
        milestones={
            90: at_90_percent,
            70: at_70_percent,
            40: at_40_percent,
            10: at_10_percent
        },
        on_zero=at_zero_percent
    )
    
    session['doom_clock_data'] = doom_clock.to_dict()
    return doom_clock


# ============================================================
# EXAMPLE 5: Reward System
# ============================================================

def example_close_conduit(session, player, conduit_location: str):
    """
    Example: Closing a conduit rewards time back to doom clock.
    
    This demonstrates using add_time() for rewards.
    """
    from game_logic.doomclock_integration import (
        get_doom_clock_from_session, save_doom_clock_to_session
    )
    
    doom_clock = get_doom_clock_from_session(session)
    messages = []
    
    # Sanity cost for closing conduit
    if hasattr(player, 'sanity'):
        player.sanity = max(0, player.sanity - 7)
        messages.append(f"Your mind reels. -7 Sanity (now {player.sanity})")
    
    # Currency reward
    if hasattr(player, 'markka'):
        player.markka += 25
        messages.append(f"Ritual artifacts worth 25 Markka fall at your feet.")
    
    # Time reward (main incentive for closing conduits)
    doom_result = doom_clock.add_time(
        n=5,
        log=messages,
        reason=f"Conduit at {conduit_location} sealed - timeline restored"
    )
    messages.extend(doom_result['messages'])
    
    # Track progress
    if 'closed_conduits' not in session:
        session['closed_conduits'] = []
    session['closed_conduits'].append(conduit_location)
    
    # Save state
    save_doom_clock_to_session(session, doom_clock)
    
    return {
        'success': True,
        'messages': messages,
        'doom': doom_clock.get_percentage(),
        'player_sanity': player.sanity if hasattr(player, 'sanity') else 0,
        'player_markka': player.markka if hasattr(player, 'markka') else 0,
        'conduits_closed': len(session.get('closed_conduits', []))
    }


# ============================================================
# EXAMPLE 6: Status Display for Frontend
# ============================================================

def example_doom_status_display(session) -> Dict[str, Any]:
    """
    Example: Generate doom status for frontend display.
    
    Returns all data needed to display doom meter, warnings, etc.
    """
    from game_logic.doomclock_integration import get_doom_clock_from_session
    
    doom_clock = get_doom_clock_from_session(session)
    percentage = doom_clock.get_percentage()
    
    # Determine warning level
    if percentage > 60:
        level = 'safe'
        color = '#00ff00'  # Green
        icon = '✓'
    elif percentage > 40:
        level = 'caution'
        color = '#ffff00'  # Yellow
        icon = '⚠'
    elif percentage > 20:
        level = 'danger'
        color = '#ff8800'  # Orange
        icon = '⚡'
    else:
        level = 'critical'
        color = '#ff0000'  # Red
        icon = '☠'
    
    return {
        'percentage': round(percentage, 1),
        'ticks': doom_clock.ticks,
        'max_ticks': doom_clock.start,
        'level': level,
        'color': color,
        'icon': icon,
        'warning_text': {
            'safe': 'Reality stable',
            'caution': 'Signs of corruption',
            'danger': 'Reality fractures',
            'critical': 'DOOM APPROACHES'
        }[level],
        'milestones_triggered': list(doom_clock._previous_thresholds)
    }


# ============================================================
# EXAMPLE 7: Conduit Detection at Locations
# ============================================================

def example_check_for_conduits(session, player, location: str) -> Dict[str, Any]:
    """
    Example: Check if a location has a conduit.
    Finding a conduit might trigger doom effects or story events.
    """
    from game_logic.doomclock_integration import (
        get_doom_clock_from_session, save_doom_clock_to_session
    )
    import random
    
    doom_clock = get_doom_clock_from_session(session)
    messages = []
    
    # 30% chance of finding a conduit (customizable)
    has_conduit = random.random() < 0.30
    
    if has_conduit:
        messages.append(f"You sense an unnatural convergence at {location}.")
        messages.append("A conduit manifests before you!")
        
        # Sensing the conduit costs sanity slightly
        if hasattr(player, 'sanity'):
            player.sanity = max(0, player.sanity - 2)
        
        # And triggers doom increment
        doom_result = doom_clock.countdown(
            n=2,
            log=messages,
            reason=f"Conduit detected at {location}"
        )
        messages.extend(doom_result['messages'])
        
        save_doom_clock_to_session(session, doom_clock)
        
        return {
            'location': location,
            'has_conduit': True,
            'messages': messages,
            'doom': doom_clock.get_percentage(),
            'can_attempt_closure': True
        }
    else:
        messages.append(f"Nothing unusual at {location}.")
        return {
            'location': location,
            'has_conduit': False,
            'messages': messages,
            'doom': doom_clock.get_percentage(),
            'can_attempt_closure': False
        }


# ============================================================
# EXAMPLE 8: Testing Helper
# ============================================================

def example_test_doom_clock():
    """
    Example unit tests for doom clock functionality.
    """
    from game_logic.doomclock import create_default_doom_clock
    
    # Test basic countdown
    doom = create_default_doom_clock(start=100)
    result = doom.countdown(25, log=[])
    assert result['ticks'] == 75
    assert result['percentage'] == 75.0
    assert result['zero_triggered'] is False
    print("✓ Basic countdown works")
    
    # Test milestone at 50%
    result = doom.countdown(25, log=[])
    assert result['ticks'] == 50
    assert '50%' in result['triggered_milestones']
    print("✓ Milestone triggering works")
    
    # Test add_time
    result = doom.add_time(10, log=[])
    assert result['ticks'] == 60
    assert result['increased'] is True
    print("✓ Add time works")
    
    # Test zero
    doom.countdown(60, log=[])
    assert doom.ticks == 0
    assert doom.resolved is True
    print("✓ Zero state works")
    
    # Test reset
    doom.reset()
    assert doom.ticks == 100
    assert doom.resolved is False
    print("✓ Reset works")
    
    # Test serialization
    serialized = doom.to_dict()
    assert 'ticks' in serialized
    assert 'start' in serialized
    print("✓ Serialization works")
    
    print("\nAll doom clock tests passed!")


if __name__ == '__main__':
    example_test_doom_clock()
