"""
writing_effects.py

Utilities for atmospheric text rendering in the terminal for a horror game:
- print_typewriter: character-by-character printing with pauses and random jitter
- dim_text / red_text: color/brightness styling with ANSI (via colorama on Windows if available)
- red_flash: quick red flash effect for jump lines
- flicker_line: simulate failing lights by clearing/reprinting a line
- print_glitch: print a line with occasional glitching characters corrected in-place
- heartbeat_modes: presets for pacing (calm, heartbeat, panic)
- gated_prompt: prompt user to continue between narrative beats

All functions are safe no-ops for styling if ANSI/color support is unavailable.
"""

import sys
import os
import time
import random
import shutil
from game.music import play_sfx

# Detect platform
try:
    import msvcrt  # Windows-only
    def poll_key():
        if msvcrt.kbhit():
            return msvcrt.getwch()
        return None
    HAS_KB = True
except ImportError:
    import termios, tty, select

    def poll_key():
        """Non-blocking single key read on POSIX (macOS, Linux)."""
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None
    HAS_KB = True

# Optional color support on Windows
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    HAS_COLOR = True
except Exception:  # colorama not installed
    HAS_COLOR = False
    class Fore:
        RED = "\033[31m"
        RESET = "\033[39m"
    class Style:
        DIM = "\033[2m"
        RESET_ALL = "\033[0m"

# Fallbacks for environments that strip ANSI
ANSI_DIM = Style.DIM if HAS_COLOR else "\033[2m"
ANSI_RESET = Style.RESET_ALL if HAS_COLOR else "\033[0m"
ANSI_RED = Fore.RED if HAS_COLOR else "\033[31m"


def _term_width(fallback=80):
    return shutil.get_terminal_size(fallback=(fallback, 20)).columns


def dim_text(text):
    return f"{ANSI_DIM}{text}{ANSI_RESET}"


def red_text(text):
    return f"{ANSI_RED}{text}{ANSI_RESET}"


HEARTBEAT_PRESETS = {
    # cps=characters per second baseline, punct_pause extra pause after punctuation
    "calm": dict(cps=35, punct_pause=0.35, jitter=0.012),
    "heartbeat": dict(cps=22, punct_pause=0.55, jitter=0.018),
    "panic": dict(cps=55, punct_pause=0.18, jitter=0.006),
}


def print_typewriter(
    text,
    cps=None,
    jitter=None,
    punct_pause=None,
    mode="calm",
    glitch_probability=0.0,
    sfx=True,
    sfx_channel=7,
    sfx_channel_2=6,
    sfx_key_name="type_key",
    sfx_return_name=None,
    allow_skip=True,
    skip_line_key=" ",
    skip_all_key="\r",
    force_skip_all=False,
):

    last_click_ts = 0.0
    play_every_n = 2          # play every 2nd visible character
    min_click_interval = 0.08 # seconds; 80 ms throttle
    visible_count = 0

    """
    Print text with a typewriter effect.
    - cps/jitter/punct_pause can be overridden, otherwise taken from `mode` preset.
    - mode: one of HEARTBEAT_PRESETS keys: calm, heartbeat, panic
    - glitch_probability: chance per character to briefly display a wrong glyph and correct it
    """
    preset = HEARTBEAT_PRESETS.get(mode, HEARTBEAT_PRESETS["calm"])
    cps = cps if cps is not None else preset["cps"]
    jitter = jitter if jitter is not None else preset["jitter"]
    punct_pause = punct_pause if punct_pause is not None else preset["punct_pause"]

    base_delay = 1.0 / max(int(cps), 1)
    punct_set = ".,!?;:"  # extra pause after these
    glitch_chars = "@#$%&*+=/\\|~^"  # pool for brief glitches

    # skip state
    skip_line = False
    # Allow callers (like a one-off story intro) to begin in skip-all mode
    skip_all = bool(force_skip_all)

    for ch in text:
        # Poll keyboard (non-blocking) to update skip states
        if allow_skip and HAS_KB:
            try:
                k = poll_key()
                if k == skip_all_key:
                    skip_all = True
                    skip_line = False
                elif k == skip_line_key:
                    if not skip_all:
                        skip_line = True
            except Exception:
                pass
        # Optional glitch: briefly show wrong char and correct in-place
        if not skip_all and not skip_line and glitch_probability > 0 and ch not in "\n" and random.random() < glitch_probability:
            wrong = random.choice(glitch_chars)
            sys.stdout.write(wrong)
            sys.stdout.flush()
            time.sleep(base_delay * 0.6)
            # backspace and overwrite with correct char
            sys.stdout.write("\b")
            sys.stdout.flush()

        sys.stdout.write(ch)
        sys.stdout.flush()

        # play key sound for visible characters
        if sfx and ch not in " \t\r\n":
            visible_count += 1
            now = time.time()
            if (visible_count % play_every_n == 0) and (now - last_click_ts >= min_click_interval):
                play_sfx(sfx_key_name, channel_id=sfx_channel)
                last_click_ts = now
        # Timing + pauses    
        if ch == "\n":
            if sfx and sfx_return_name:
                play_sfx(sfx_return_name, channel_id=sfx_channel_2)
            if not skip_all:
                # end of line cancels line fast-forward
                time.sleep(base_delay * 2)
            skip_line = False
            continue
        if ch == " ":
            if not skip_all and not skip_line:
                time.sleep(base_delay * 0.6)
            continue

        if not skip_all and not skip_line:
            delay = base_delay + random.uniform(0, jitter)
            time.sleep(delay)

        if ch in punct_set:
            now = time.time()
            if sfx and (now - last_click_ts >= min_click_interval):
                play_sfx(sfx_key_name, channel_id=sfx_channel)
                last_click_ts = now
            if not skip_all and not skip_line:
                time.sleep(punct_pause)


def red_flash(text, flashes=2, on_time=0.06, off_time=0.06):
    """
    Print a quick red flashing text (e.g., for a jump scare cue).
    """
    clear = "\r" + " " * _term_width() + "\r"
    for i in range(max(1, flashes)):
        sys.stdout.write(red_text(text))
        sys.stdout.flush()
        time.sleep(on_time)
        sys.stdout.write(clear)
        sys.stdout.flush()
        time.sleep(off_time)
    # leave the text visible at the end
    sys.stdout.write(red_text(text) + "\n")
    sys.stdout.flush()


def flicker_line(text, times=2, interval=0.08):
    """
    Simulate failing lights by briefly clearing and reprinting the line.
    """
    clear = "\r" + " " * _term_width() + "\r"
    for _ in range(max(1, times)):
        sys.stdout.write(text)
        sys.stdout.flush()
        time.sleep(interval)
        sys.stdout.write(clear)
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def print_glitch(text, glitch_probability=0.05, mode="heartbeat"):
    """
    Print a full line with occasional glitch characters that are corrected in-place.
    """
    print_typewriter(text + "\n", mode=mode, glitch_probability=glitch_probability)


def gated_prompt(prompt="[Press Enter to continue…]"):
    try:
        input(f"\n{dim_text(prompt)}")
    except KeyboardInterrupt:
        # Gracefully allow skipping
        print()
