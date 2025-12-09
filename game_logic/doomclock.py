"""
doomclock.py - Doom Clock system for GameProjectSoftware2

A countdown timer (100 → 0) that tracks the progression of reality corruption.
Milestones trigger at percentage thresholds (75%, 50%, 25%, 0%).
Completely independent implementation for web-based game.

Key differences from original:
- Milestones computed from percentages (% of max) rather than fixed values
- All callbacks return data dicts instead of printing
- No sys.exit() calls - returns game state to caller
- Stateless milestone checking (no _hit tracking needed)
- Integrates with Flask session/API flow
"""

from typing import List, Dict, Callable, Optional


# Type aliases
Log = List[str]
MilestoneFn = Callable[[dict, list, Log], None]
OnZeroFn = Callable[[dict, list, Log], None]


class DoomClock:
    """
    Countdown Doom Clock.
    Starts at 'start' (default 100) and decreases each turn until 0.
    Milestones trigger when percentage thresholds are crossed.
    """

    def __init__(self, name: str = "Doom ⏳", start: int = 100,
                 milestones: Optional[Dict[int, MilestoneFn]] = None,
                 on_zero: Optional[OnZeroFn] = None):
        """
        Initialize the Doom Clock.
        
        Args:
            name: Display name for the clock
            start: Starting value (default 100)
            milestones: Dict mapping percentage thresholds (75, 50, 25) to callback functions
            on_zero: Callback function when clock reaches 0
        """
        self.name = name
        self.start = int(start)
        self.ticks = int(start)
        self.milestones = milestones or {}
        self._previous_thresholds = set()  # Track which thresholds have fired
        self.on_zero = on_zero
        self.resolved = False

    def get_percentage(self) -> float:
        """
        Get current clock percentage (0-100).
        
        Returns:
            float: Current percentage
        """
        if self.start == 0:
            return 0.0
        return (self.ticks / self.start) * 100.0

    def _get_active_thresholds(self) -> set:
        """
        Get which percentage thresholds should be active at current percentage.
        
        Returns:
            set: Set of threshold percentages currently crossed
        """
        current_pct = self.get_percentage()
        active = set()
        
        for threshold in self.milestones.keys():
            # Threshold is "active" if current percentage is below it
            if current_pct < threshold:
                active.add(threshold)
        
        return active

    def countdown(self, n: int = 1, player: Optional[dict] = None,
                  enemies: Optional[list] = None, log: Optional[Log] = None,
                  reason: Optional[str] = None) -> Dict:
        """
        Decrease the clock by n ticks.
        Triggers milestones when crossing percentage thresholds.
        
        Args:
            n: Amount to decrease (default 1)
            player: Player state dict
            enemies: List of enemy states
            log: Message log to append to
            reason: Human-readable reason for countdown
        
        Returns:
            dict: {
                'ticks': int (remaining ticks),
                'percentage': float (0-100),
                'triggered_milestones': list of str (milestone names),
                'zero_triggered': bool,
                'messages': list of str (generated messages)
            }
        """
        prev_ticks = self.ticks
        prev_pct = self.get_percentage()
        
        # Decrease ticks
        self.ticks = max(0, self.ticks - int(n))
        current_pct = self.get_percentage()
        
        target_log: Log = log if log is not None else []
        triggered_milestones: List[str] = []
        zero_triggered = False
        
        # Log the countdown reason
        if reason:
            target_log.append(f"[Doom -{n}] {reason}")
        
        # Check which thresholds were crossed going from prev_pct → current_pct
        # A threshold is crossed when we go from >= threshold to <= threshold (inclusive)
        for threshold in sorted(self.milestones.keys(), reverse=True):
            # Check if threshold was just crossed or reached
            if prev_pct >= threshold and current_pct <= threshold and threshold not in self._previous_thresholds:
                self._previous_thresholds.add(threshold)
                cb = self.milestones[threshold]
                if callable(cb):
                    cb(player or {}, enemies or [], target_log)
                    triggered_milestones.append(f"{threshold}%")
        
        # Check if zero is reached
        if not self.resolved and self.ticks == 0:
            self.resolved = True
            if callable(self.on_zero):
                self.on_zero(player or {}, enemies or [], target_log)
            zero_triggered = True
            triggered_milestones.append("ZERO")
        
        result = {
            'ticks': self.ticks,
            'percentage': current_pct,
            'triggered_milestones': triggered_milestones,
            'zero_triggered': zero_triggered,
            'messages': target_log
        }
        
        return result

    def add_time(self, n: int = 1, log: Optional[Log] = None, 
                 reason: Optional[str] = None) -> Dict:
        """
        Increase the clock by n ticks (up to start value).
        
        Args:
            n: Amount to increase (default 1)
            log: Message log to append to
            reason: Human-readable reason for increase
        
        Returns:
            dict: {
                'ticks': int (current ticks),
                'percentage': float (0-100),
                'messages': list of str
            }
        """
        prev_ticks = self.ticks
        self.ticks = min(self.start, self.ticks + int(n))
        
        target_log: Log = log if log is not None else []
        if reason:
            target_log.append(f"[Doom +{n}] {reason}")
        
        return {
            'ticks': self.ticks,
            'percentage': self.get_percentage(),
            'messages': target_log,
            'increased': self.ticks > prev_ticks
        }

    def reset(self):
        """Reset clock to initial state."""
        self.ticks = self.start
        self._previous_thresholds.clear()
        self.resolved = False

    def to_dict(self) -> Dict:
        """
        Serialize clock state for session/API responses.
        
        Returns:
            dict: Serializable state
        """
        return {
            'name': self.name,
            'start': self.start,
            'ticks': self.ticks,
            'percentage': self.get_percentage(),
            'resolved': self.resolved,
            'previous_thresholds': list(self._previous_thresholds)
        }

    @classmethod
    def from_dict(cls, data: Dict, milestones: Optional[Dict[int, MilestoneFn]] = None,
                  on_zero: Optional[OnZeroFn] = None) -> 'DoomClock':
        """
        Reconstruct a DoomClock from serialized state.
        Useful for restoring from session.
        
        Args:
            data: Dict from to_dict()
            milestones: Milestone callbacks (must be provided)
            on_zero: On-zero callback (must be provided)
        
        Returns:
            DoomClock: Reconstructed instance
        """
        instance = cls(name=data['name'], start=data['start'],
                      milestones=milestones, on_zero=on_zero)
        instance.ticks = data['ticks']
        instance.resolved = data['resolved']
        instance._previous_thresholds = set(data.get('previous_thresholds', []))
        return instance


# ============================================================
# Default Milestones & Callbacks
# ============================================================

def default_at_75(player: dict, enemies: list, log: Log) -> None:
    """75% threshold: Reality begins to shudder."""
    log.append("[75%] The chanting grows louder; reality shudders.")


def default_at_50(player: dict, enemies: list, log: Log) -> None:
    """50% threshold: Enemies grow stronger."""
    log.append("[50%] Sigils flare; enemies feel stronger.")


def default_at_25(player: dict, enemies: list, log: Log) -> None:
    """25% threshold: Mind fraying."""
    log.append("[25%] The veil thins; your mind frays.")


def default_on_zero(player: dict, enemies: list, log: Log) -> None:
    """0% threshold: Game over."""
    log.append(
        "Time expires. The conduits yawn wide, tearing the fabric of reality.\n"
        "The world succumbs to an eternal slumber."
    )


def create_default_doom_clock(start: int = 100) -> DoomClock:
    """
    Create a doom clock with default milestones.
    
    Args:
        start: Starting value (default 100)
    
    Returns:
        DoomClock: Configured clock
    """
    return DoomClock(
        name="Doom ⏳",
        start=start,
        milestones={
            75: default_at_75,
            50: default_at_50,
            25: default_at_25
        },
        on_zero=default_on_zero
    )
