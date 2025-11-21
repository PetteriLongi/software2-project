"""Music and SFX helpers with seamless track transitions.

Highlights:
    • Mixer is initialised lazily on first use (`play_music()` or friends).
    • `play_music()` keeps the current track alive unless a new file is requested,
      fading out the previous loop and fading in the replacement.
    • `stop_music()` clears the cached track so future calls can restart it.
    • Load short sound effects with `load_sfx()` and play them through
      `play_sfx()` (optionally pinning them to reserved channels).
    • Volume helpers exist for both music (`set_volume`) and cached SFX
      (`set_sfx_volume`).

All helpers degrade gracefully when audio cannot be initialised (e.g. no device).
"""

import pygame

_mixer_ready = False
_CURRENT_TRACK: str | None = None
_SFX_CACHE: dict[str, pygame.mixer.Sound] = {}
_SFX_CHANNELS: dict[int, pygame.mixer.Channel] = {}


# ==========================================
# LAZY MIXER INIT (SAFE ON IMPORT)
# ==========================================
def _ensure_mixer() -> bool:
    """Initialise ``pygame.mixer`` on demand. Returns True when ready."""
    global _mixer_ready
    if _mixer_ready:
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _mixer_ready = True
        return True
    except Exception as exc:
        print(f"\033[93m[Audio Disabled]\033[0m Could not initialise audio: {exc}")
        _mixer_ready = False
        return False


def init_audio() -> bool:
    """Explicitly initialise audio. Useful for early failure detection."""
    return _ensure_mixer()


# ==========================================
# MUSIC CONTROLS
# ==========================================
def play_music(
    file_path: str,
    volume: float = 0.5,
    loop: bool = True,
    restart: bool = False,
    fade_ms: int = 800,
) -> None:
    """Play ``file_path`` with optional fade handling.

    If the requested track is already playing, only the volume is updated unless
    ``restart`` is True. When switching to a new track, the previous music fades
    out and the new one fades in using ``fade_ms`` milliseconds.
    """

    global _CURRENT_TRACK

    if not _ensure_mixer():
        return

    busy = pygame.mixer.music.get_busy()
    if busy:
        if not restart and _CURRENT_TRACK == file_path:
            pygame.mixer.music.set_volume(volume)
            return
        try:
            pygame.mixer.music.fadeout(max(0, fade_ms))
        except Exception:
            pygame.mixer.music.stop()

    try:
        pygame.mixer.music.load(file_path)
    except Exception as exc:
        print(f"\033[93m[Audio]\033[0m Failed to load track '{file_path}': {exc}")
        return

    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1 if loop else 0, fade_ms=max(0, fade_ms))
    _CURRENT_TRACK = file_path


def stop_music() -> None:
    """Stop the currently playing music track."""

    global _CURRENT_TRACK

    if not _ensure_mixer():
        return
    pygame.mixer.music.stop()
    _CURRENT_TRACK = None


def set_volume(volume: float) -> None:
    """Adjust music volume while a track is playing."""

    if not _ensure_mixer():
        return
    pygame.mixer.music.set_volume(volume)


# ==========================================
# SFX MANAGEMENT (CACHE + CHANNELS)
# ==========================================
def load_sfx(name: str, path: str, volume: float = 0.15, channel_id: int | None = None) -> pygame.mixer.Sound | None:
    """Load (and cache) a sound effect by ``name``. Returns the ``Sound`` instance."""

    if not _ensure_mixer():
        return None

    snd = _SFX_CACHE.get(name)
    if snd is None:
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(max(0.0, min(1.0, float(volume))))
            _SFX_CACHE[name] = snd
        except Exception as exc:
            print(f"\033[93m[SFX]\033[0m Failed to load '{path}': {exc}")
            return None

    if channel_id is not None and channel_id not in _SFX_CHANNELS:
        try:
            _SFX_CHANNELS[channel_id] = pygame.mixer.Channel(int(channel_id))
        except Exception as exc:
            print(f"\033[93m[SFX]\033[0m Failed to reserve channel {channel_id}: {exc}")

    return snd


def play_sfx(name: str, channel_id: int | None = None) -> None:
    """Play a cached SFX by ``name``."""

    if not _ensure_mixer():
        return

    snd = _SFX_CACHE.get(name)
    if not snd:
        return

    if channel_id is not None and channel_id in _SFX_CHANNELS:
        try:
            _SFX_CHANNELS[channel_id].play(snd)
        except Exception:
            snd.play()
    else:
        snd.play()


def set_sfx_volume(name: str, volume: float) -> None:
    """Adjust the volume of a cached SFX."""

    snd = _SFX_CACHE.get(name)
    if snd:
        try:
            snd.set_volume(max(0.0, min(1.0, float(volume))))
        except Exception:
            pass


def unload_sfx(name: str) -> None:
    """Remove a cached SFX. Does not stop currently playing audio."""

    _SFX_CACHE.pop(name, None)
