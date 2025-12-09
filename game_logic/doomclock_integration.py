"""
doomclock_integration.py - Flask session integration for DoomClock

Essential integration functions for saving/loading doom clock state.
"""

from game_logic.doomclock import DoomClock, create_default_doom_clock


def initialize_game_session(session, player_name: str, start_doom: int = 100):
    """
    Initialize a new game session with a doom clock.
    
    Args:
        session: Flask session object
        player_name: Name of player
        start_doom: Starting doom value (default 100)
    """
    doom_clock = create_default_doom_clock(start=start_doom)
    
    session['doom_clock_data'] = doom_clock.to_dict()
    session['doom_milestones_triggered'] = []
    session['player_name'] = player_name
    
    return doom_clock


def get_doom_clock_from_session(session) -> DoomClock:
    """
    Restore DoomClock from session.
    
    Args:
        session: Flask session object
    
    Returns:
        DoomClock: Restored instance
    """
    doom_data = session.get('doom_clock_data')
    
    if not doom_data:
        return create_default_doom_clock()
    
    return DoomClock.from_dict(doom_data)


def save_doom_clock_to_session(session, doom_clock: DoomClock):
    """
    Save DoomClock state to session.
    
    Args:
        session: Flask session object
        doom_clock: DoomClock instance
    """
    session['doom_clock_data'] = doom_clock.to_dict()
    session.modified = True
