import sys
from typing import List, Dict, Callable, Optional

try:  # Prefer unified UI output when available
    from game.ui_elements.colours import ui_print
except Exception:  # pragma: no cover - fallback for early bootstrap
    def ui_print(text: str, colour: Optional[str] = None) -> None:
        print(text)

# ------------------------------------------------------------
# Doom Clock (100 → 0)
# ------------------------------------------------------------
Log = List[str]
MilestoneFn = Callable[[dict, list, Log], None]
OnZeroFn = Callable[[dict, list, Log], None]


def _emit_messages(messages: Log) -> None:
    for message in messages:
        if message:
            ui_print(message)

class DoomClock:
    """
    Countdown Doom Clock.
    Starts at 'start' (default 100) and decreases each turn until 0.
    Milestones trigger when thresholds are crossed.
    """

    def __init__(self, name: str = "Doom ⏳", start: int = 100,
                 milestones: Optional[Dict[int, MilestoneFn]] = None,
                 on_zero: Optional[OnZeroFn] = None):
        self.name = name
        self.start = int(start)
        self.ticks = int(start)
        self.milestones = milestones or {}
        self._hit = set()
        self.on_zero = on_zero
        self.resolved = False

    def countdown(self, n: int = 1, player: Optional[dict] = None,
                  enemies: Optional[list] = None, log: Optional[Log] = None,
                  reason: Optional[str] = None) -> bool:
        prev = self.ticks
        self.ticks = max(0, self.ticks - int(n))

        target_log: Log = log if log is not None else []
        zero_triggered = False

        if reason:
            target_log.append(f"\033[95m[Doom -{n}] {reason}\033[0m")

        # Fire milestones crossed this tick (e.g., crossing 75 from 76→74)
        for threshold in sorted(self.milestones.keys(), reverse=True):
            if prev >= threshold > self.ticks and threshold not in self._hit:
                self._hit.add(threshold)
                cb = self.milestones[threshold]
                if callable(cb):
                    cb(player or {}, enemies or [], target_log)

        if not self.resolved and self.ticks == 0:
            self.resolved = True
            if callable(self.on_zero):
                self.on_zero(player or {}, enemies or [], target_log)
            zero_triggered = True

        if log is None and target_log:
            _emit_messages(target_log)

        if zero_triggered:
            sys.exit()
        return zero_triggered

    def add_time(self, n: int = 1, log: Optional[Log] = None, reason: Optional[str] = None):
        self.ticks = min(self.start, self.ticks + int(n))
        target_log: Log = log if log is not None else []
        if reason:
            target_log.append(f"\033[94m[Doom +{n}] {reason}\033[0m")
        if log is None and target_log:
            _emit_messages(target_log)

    def reset(self):
        self.ticks = self.start
        self._hit.clear()
        self.resolved = False
#====================
# Doom Clock Milestones
#====================
def on_zero(player, enemies, log):
    log.append(
        "\033[91mTime expires. The conduits yawn wide, tearing the fabric of reality.\n"
        "The world succumbs to an eternal slumber.\033[0m"
    )
def at_75(player, enemies, log):
    log.append("\033[95m[75] The chanting grows louder; reality shudders.\033[0m")

def at_50(player, enemies, log):
    log.append("\033[95m[50] Sigils flare; enemies feel stronger.\033[0m")


def at_25(player, enemies, log):
    log.append("\033[95m[25] The veil thins; your mind frays.\033[0m")


doom_clock = DoomClock(
    start=100,
    milestones={75: at_75, 50: at_50, 25: at_25},
    on_zero=on_zero
)

# …then call: combat(player, enemies, doom_clock=doom_clock)
# make it so that it takes the at25 and so on from the % of the amount in doom clock *
#for example if the doom clock was 100: 75% would be 75 or if it was 1000 then 25% would be 250 for the event to trigger
#this makes the code much more reliable and robust
# EVENTS / CONDUITS (stubs you can flesh out)
# ==========================================

#def travel_event(gs: GameState):
#    """
#    Random simple event per spec: fight / check / flavour.
#    Keep it deterministic-by-choice for the prototype.
#    """
#    roll = random.random()
#    if roll < 0.33:
#        # Cultists at Gate — choice
#       print("[A] Confront  [S] Slip past")
#        ch = input("> ").strip().lower()
#        if ch == "a":
#            gs.sanity = max(0, gs.sanity - 3)
#            gs.markka += 5
#            gs.log("\033[92mYou confront them, scattering the cultists. -3 Sanity, +5 Markka.\033[0m")
#        else:
#            gs.sanity = max(0, gs.sanity - 1)
#            gs.log("\033[94mYou slip past in the crowd. -1 Sanity.\033[0m")

#    elif roll < 0.66:
#        # Static Interference — a skill check gate
#        print("\nEvent: Static Interference.")
#        print("[F] Focus (requires Eldritch Sense)  [W] Wait")
#        ch = input("> ").strip().lower()
#        if ch == "f" and "Eldritch Sense" in gs.powers:
#            gs.log("\033[96mYou pierce the noise. A whisper hints at a nearby conduit.\033[0m")
#        else:
#            gs.log("\033[90mYou wait. Nothing changes.\033[0m")
#    else:
#        # Flavour
#        gs.log("\033[90mA cold draft curls through the terminal. Someone hums an old hymn.\033[0m")

#def conduit_check(gs: GameState, airport: Airport):
#    """
#    30% generic chance OR 100% if the airport is on the Note and not yet cleared.
#    """
#    guaranteed = (airport.code in gs.note_airports) and (not airport.conduit_closed)
#    if guaranteed:
#        airport.has_conduit = True
#        return

    # otherwise 30% generic
#    if not airport.conduit_closed and random.random() < 0.30:
#        airport.has_conduit = True
#    else:
#        airport.has_conduit = False

#def attempt_closure(gs: GameState, airport: Airport):
#    """
#    Prototype closure: deterministic success (you can add a mini-check).
#    Effects per spec: -Sanity, +Markka, Doom -1, Gain Power (story beat).
#    """
#    print("\nConduit hums with alien geometry.")
#    print("[1] Attempt Closure  [2] Leave")
#    ch = input("> ").strip()
#    if ch != "1":
#        gs.log("\033[93mYou turn away. The conduit remains.\033[0m")
#        return

#    # Closure resolves
#    airport.conduit_closed = True
#    gs.closed_conduits += 1
#    gs.sanity = max(0, gs.sanity - 5)
#    gs.markka += 10
#    gs.doom.countdown(1, None, None, gs.turn_log, reason="Conduit closure ripples time.")
#    # grant next power (placeholder)
#    new_power = f"Manifestation #{gs.closed_conduits}"
#    gs.powers.append(new_power)
#    gs.log(f"\033[92mConduit sealed! -5 Sanity, +10 Markka, new Power: {new_power}\033[0m")
