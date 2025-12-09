"""Audio logic module."""
from .audio_config import (
    AUDIO_LIBRARY,
    EVENT_AUDIO_MAP,
    AudioTrack,
    get_audio_for_event,
    get_all_tracks,
    get_tracks_by_category
)

__all__ = [
    'AUDIO_LIBRARY',
    'EVENT_AUDIO_MAP',
    'AudioTrack',
    'get_audio_for_event',
    'get_all_tracks',
    'get_tracks_by_category'
]
