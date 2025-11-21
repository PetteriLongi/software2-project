"""
sfx_loader.py - Centralized registration of all short sound effects (SFX).

Usage from main.py:

    from game.sfx_loader import register_all_sfx
    register_all_sfx()

This keeps main.py clean and provides a single place to manage SFX.
"""

from .music import load_sfx

# List all SFX here. Each entry: (key, path, volume, channel_id)
SFX_CATALOG = [
    # Typing / ambience
    ("type_key", "Music/SFX/type_key.wav", 0.12, 7),
    ("type_return", "Music/ambience/Piano_suspense.mp3", 0.12, 6),

    # Weapons - reloads
    ("revolver_reload", "Music/SFX/revolver_reload.wav", 0.12, 5),
    ("reload", "Music/SFX/reload.wav", 0.12, 5),

    # Weapons - attacks
    ("knife_slash", "Music/SFX/knife_slash.wav", 0.12, 5),
    ("sword_slash", "Music/SFX/sword_slash.wav", 0.75, 5),
    ("revolver_shot", "Music/SFX/revolver_shot.wav", 0.08, 5),
    ("rifle_shot", "Music/SFX/rifle_shot.wav", 0.12, 5),
    ("submachine_shot", "Music/SFX/submachine_shot.wav", 0.12, 5),

    # Consumables
    ("Eating", "Music/SFX/Eating.wav", 0.52, 5),
    ("Drinking", "Music/SFX/Drinking.wav", 0.52, 5),

    # Level up
    ("level_up", "Music/SFX/level_up.wav", 0.12, 5),

    # Manifestations
    ("Fear", "Music/SFX/Manifestation/Fear.wav", 0.12, 5),
    ("Hope", "Music/SFX/Manifestation/Hope.wav", 0.12, 5),
    ("Rage", "Music/SFX/Manifestation/Rage.wav", 0.12, 5),
    ("Resentment", "Music/SFX/Manifestation/Resentment.wav", 0.12, 5),
]


def register_all_sfx():
    """Register all SFX defined in SFX_CATALOG.

    Safe to call multiple times; underlying mixer will just reassign the same keys.
    """
    for key, path, volume, channel_id in SFX_CATALOG:
        try:
            load_sfx(key, path, volume=volume, channel_id=channel_id)
        except Exception:
            # Keep the game running even if an asset is missing on the filesystem
            pass


# Optional: expose the keys for validation or debugging
SFX_KEYS = {key for key, *_ in SFX_CATALOG}

