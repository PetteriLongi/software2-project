"""
Audio configuration and mapping for GameProjectSoftware2.
Maps game events to audio files (independent from old pygame version).
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AudioTrack:
    """Audio file metadata."""
    id: str
    filename: str
    category: str  # 'music', 'sfx', 'ambient'
    loop: bool = False
    volume: float = 1.0
    description: str = ""


# Audio library - all available tracks
AUDIO_LIBRARY: Dict[str, AudioTrack] = {
    # Background Music - Combat
    'music_anxiety': AudioTrack(
        'music_anxiety', 'music/Anxiety.mp3', 'music',
        loop=True, volume=0.5, description='Combat background - tension'
    ),
    'music_behind_you': AudioTrack(
        'music_behind_you', 'music/Behind_you.mp3', 'music',
        loop=True, volume=0.5, description='Combat background - threat'
    ),
    'music_final_battle': AudioTrack(
        'music_final_battle', 'music/Final_battle.mp3', 'music',
        loop=True, volume=0.5, description='Boss combat theme'
    ),
    'music_invocation': AudioTrack(
        'music_invocation', 'music/Invocation.mp3', 'music',
        loop=True, volume=0.5, description='Ritual/manifestation theme'
    ),
    'music_fragments_work': AudioTrack(
        'music_fragments_work', 'music/let_the_fragments_work.mp3', 'music',
        loop=True, volume=0.5, description='Combat background - chaos'
    ),
    'music_your_fear': AudioTrack(
        'music_your_fear', 'music/your_fear.mp3', 'music',
        loop=True, volume=0.5, description='Horror combat theme'
    ),
    
    # Ambient Music
    'ambient_airport_dread': AudioTrack(
        'ambient_airport_dread', 'ambient/Airport_dread.mp3', 'ambient',
        loop=True, volume=0.35, description='Airport exploration ambience'
    ),
    'ambient_chaos_terminal': AudioTrack(
        'ambient_chaos_terminal', 'ambient/Chaos_in_terminal.mp3', 'ambient',
        loop=True, volume=0.35, description='Terminal chaos ambience'
    ),
    'ambient_eclipse': AudioTrack(
        'ambient_eclipse', 'ambient/Eclipse_arrival.mp3', 'ambient',
        loop=True, volume=0.35, description='Eclipse event ambience'
    ),
    'ambient_epilogue': AudioTrack(
        'ambient_epilogue', 'ambient/Epilogue.mp3', 'ambient',
        loop=False, volume=0.5, description='Ending theme'
    ),
    'ambient_piano_suspense': AudioTrack(
        'ambient_piano_suspense', 'ambient/Piano_suspense.mp3', 'ambient',
        loop=True, volume=0.35, description='Story suspense'
    ),
    'ambient_tension_rise': AudioTrack(
        'ambient_tension_rise', 'ambient/Tension_rise.mp3', 'ambient',
        loop=True, volume=0.35, description='Rising tension'
    ),
    'ambient_whispers': AudioTrack(
        'ambient_whispers', 'ambient/Whispers_Beyond_the_Veil.mp3', 'ambient',
        loop=True, volume=0.35, description='Otherworldly whispers'
    ),
    
    # Sound Effects - Weapons
    'sfx_knife_slash': AudioTrack(
        'sfx_knife_slash', 'sfx/knife_slash.wav', 'sfx',
        volume=0.6, description='Knife attack'
    ),
    'sfx_sword_slash': AudioTrack(
        'sfx_sword_slash', 'sfx/sword_slash.wav', 'sfx',
        volume=0.75, description='Sword attack'
    ),
    'sfx_revolver_shot': AudioTrack(
        'sfx_revolver_shot', 'sfx/revolver_shot.wav', 'sfx',
        volume=0.6, description='Revolver gunshot'
    ),
    'sfx_rifle_shot': AudioTrack(
        'sfx_rifle_shot', 'sfx/rifle_shot.wav', 'sfx',
        volume=0.6, description='Rifle gunshot'
    ),
    'sfx_submachine_shot': AudioTrack(
        'sfx_submachine_shot', 'sfx/submachine_shot.wav', 'sfx',
        volume=0.6, description='Submachine gun shot'
    ),
    
    # Sound Effects - Reload
    'sfx_reload': AudioTrack(
        'sfx_reload', 'sfx/reload.wav', 'sfx',
        volume=0.6, description='Generic reload'
    ),
    'sfx_revolver_reload': AudioTrack(
        'sfx_revolver_reload', 'sfx/revolver_reload.wav', 'sfx',
        volume=0.6, description='Revolver reload'
    ),
    
    # Sound Effects - Consumables
    'sfx_eating': AudioTrack(
        'sfx_eating', 'sfx/Eating.wav', 'sfx',
        volume=0.6, description='Eating food'
    ),
    'sfx_drinking': AudioTrack(
        'sfx_drinking', 'sfx/Drinking.wav', 'sfx',
        volume=0.6, description='Drinking potion'
    ),
    
    # Sound Effects - Manifestations
    'sfx_manifestation_fear': AudioTrack(
        'sfx_manifestation_fear', 'sfx/Fear.wav', 'sfx',
        volume=0.6, description='Fear manifestation cast'
    ),
    'sfx_manifestation_hope': AudioTrack(
        'sfx_manifestation_hope', 'sfx/Hope.wav', 'sfx',
        volume=0.6, description='Hope manifestation cast'
    ),
    'sfx_manifestation_rage': AudioTrack(
        'sfx_manifestation_rage', 'sfx/Rage.wav', 'sfx',
        volume=0.6, description='Rage manifestation cast'
    ),
    'sfx_manifestation_resentment': AudioTrack(
        'sfx_manifestation_resentment', 'sfx/Resentment.wav', 'sfx',
        volume=0.6, description='Resentment manifestation cast'
    ),
    
    # Sound Effects - UI
    'sfx_level_up': AudioTrack(
        'sfx_level_up', 'sfx/level_up.wav', 'sfx',
        volume=0.6, description='Level up notification'
    ),
    'sfx_type_key': AudioTrack(
        'sfx_type_key', 'sfx/type_key.wav', 'sfx',
        volume=0.5, description='Typing key press'
    ),
    'sfx_type_return': AudioTrack(
        'sfx_type_return', 'sfx/type_return.wav', 'sfx',
        volume=0.5, description='Typing return key'
    ),
}


# Event → Audio mapping
# Maps game events to one or more audio tracks
EVENT_AUDIO_MAP: Dict[str, List[str]] = {
    # Combat events
    'combat_start': ['music_anxiety'],
    'combat_start_boss': ['music_final_battle'],
    'combat_end': ['ambient_airport_dread'],
    
    # Weapon actions
    'attack_knife': ['sfx_knife_slash'],
    'attack_sword': ['sfx_sword_slash'],
    'attack_revolver': ['sfx_revolver_shot'],
    'attack_rifle': ['sfx_rifle_shot'],
    'attack_submachine': ['sfx_submachine_shot'],
    'reload_gun': ['sfx_reload'],
    'reload_revolver': ['sfx_revolver_reload'],
    
    # Manifestation casts
    'manifestation_fear': ['sfx_manifestation_fear'],
    'manifestation_hope': ['sfx_manifestation_hope'],
    'manifestation_rage': ['sfx_manifestation_rage'],
    'manifestation_resentment': ['sfx_manifestation_resentment'],
    
    # Consumables
    'consume_food': ['sfx_eating'],
    'consume_potion': ['sfx_drinking'],
    
    # Story events
    'story_suspense': ['ambient_piano_suspense'],
    'story_tension': ['ambient_tension_rise'],
    'story_eclipse': ['ambient_eclipse'],
    'story_ending': ['ambient_epilogue'],
    
    # Travel/exploration
    'travel_airport': ['ambient_airport_dread'],
    'explore_terminal': ['ambient_chaos_terminal'],
    'location_change': ['ambient_airport_dread'],
    'conduit_discovered': ['ambient_whispers'],
    'conduit_closed': ['ambient_tension_rise'],
    'rest_start': ['ambient_piano_suspense'],
    'menu_open': ['ambient_airport_dread'],
    
    # UI events
    'level_up': ['sfx_level_up'],
    'ui_typing': ['sfx_type_key'],
}


def get_audio_for_event(event: str) -> List[AudioTrack]:
    """Get audio tracks for a game event."""
    track_ids = EVENT_AUDIO_MAP.get(event, [])
    return [AUDIO_LIBRARY[tid] for tid in track_ids if tid in AUDIO_LIBRARY]


def get_all_tracks() -> Dict[str, AudioTrack]:
    """Get the full audio library."""
    return AUDIO_LIBRARY.copy()


def get_tracks_by_category(category: str) -> Dict[str, AudioTrack]:
    """Get all tracks in a specific category."""
    return {
        track_id: track 
        for track_id, track in AUDIO_LIBRARY.items() 
        if track.category == category
    }
