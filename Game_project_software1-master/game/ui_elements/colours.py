"""Colour utilities shared between Rich and ASCII UI layers."""

from __future__ import annotations

from Database.config import USE_ANSI, COLOR_RESET

try:  # Detect Rich availability
    from rich.console import Console
    from rich.text import Text

    console = Console(force_terminal=True)
    RICH_AVAILABLE = True
except Exception:  # pragma: no cover - rich missing
    Console = None  # type: ignore[assignment]
    Text = None  # type: ignore[assignment]
    console = None
    RICH_AVAILABLE = False


# ========================================
# COLOUR HANDLING
# ========================================

COLOURS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "magenta": "\033[95m",
    "violet": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
}


def colouring(text: str, colour: str | None = None, style: str | None = None) -> str:
    colour_code = COLOURS.get(colour, "")
    style_code = COLOURS.get(style, "")
    return f"{style_code}{colour_code}{text}{COLOURS['reset']}"


def ui_print(text: str, colour: str | None = None) -> None:
    if RICH_AVAILABLE and console is not None and Text is not None:
        payload = str(text)
        if colour:
            console.print(Text(payload, style=colour))
        elif "\033[" in payload:
            console.print(Text.from_ansi(payload))
        else:
            console.print(payload)
    else:
        if colour:
            print(colouring(str(text), colour))
        else:
            print(str(text))


def colorize(text: str, color: str | None, strike: bool = False) -> str:
    if not USE_ANSI:
        return text
    prefix = ""
    if color:
        prefix += color
    if strike:
        prefix += "\033[9m"  # strikethrough
    return f"{prefix}{text}{COLOR_RESET}"