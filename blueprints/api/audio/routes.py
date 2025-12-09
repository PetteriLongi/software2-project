"""
Audio API routes.
Serves audio metadata for the frontend.
Static files are served by Flask's static folder.
"""
from flask import Blueprint, jsonify, request
from game_logic.audio import get_audio_for_event, get_all_tracks, get_tracks_by_category

audio_bp = Blueprint('audio', __name__)


@audio_bp.route('/catalog', methods=['GET'])
def get_audio_catalog():
    """
    Get full audio library catalog.
    
    Returns:
        JSON: {
            "success": true,
            "catalog": {
                "track_id": {
                    "id": "track_id",
                    "url": "/static/audio/...",
                    "category": "music|sfx|ambient",
                    "loop": true|false,
                    "volume": 0.0-1.0,
                    "description": "..."
                },
                ...
            }
        }
    """
    tracks = get_all_tracks()
    
    catalog = {
        track_id: {
            'id': track.id,
            'url': f"/static/audio/{track.filename}",
            'category': track.category,
            'loop': track.loop,
            'volume': track.volume,
            'description': track.description
        }
        for track_id, track in tracks.items()
    }
    
    return jsonify({
        'success': True,
        'catalog': catalog,
        'total': len(catalog)
    }), 200


@audio_bp.route('/category/<category>', methods=['GET'])
def get_category_audio(category: str):
    """
    Get all audio tracks in a specific category.
    
    Args:
        category: 'music', 'sfx', or 'ambient'
    
    Returns:
        JSON: List of tracks in the category
    """
    if category not in ['music', 'sfx', 'ambient']:
        return jsonify({
            'success': False,
            'message': 'Invalid category. Must be: music, sfx, or ambient'
        }), 400
    
    tracks = get_tracks_by_category(category)
    
    audio_data = {
        track_id: {
            'id': track.id,
            'url': f"/static/audio/{track.filename}",
            'loop': track.loop,
            'volume': track.volume,
            'description': track.description
        }
        for track_id, track in tracks.items()
    }
    
    return jsonify({
        'success': True,
        'category': category,
        'tracks': audio_data,
        'total': len(audio_data)
    }), 200


@audio_bp.route('/event/<event_name>', methods=['GET'])
def get_event_audio(event_name: str):
    """
    Get audio tracks for a specific game event.
    
    Args:
        event_name: Game event identifier (e.g., 'combat_start', 'attack_rifle')
    
    Returns:
        JSON: {
            "success": true,
            "event": "event_name",
            "audio": [
                {
                    "id": "track_id",
                    "url": "/static/audio/...",
                    "category": "...",
                    "loop": true|false,
                    "volume": 0.0-1.0
                }
            ]
        }
    """
    tracks = get_audio_for_event(event_name)
    
    if not tracks:
        return jsonify({
            'success': False,
            'message': f'No audio configured for event: {event_name}',
            'event': event_name,
            'audio': []
        }), 404
    
    audio_data = [
        {
            'id': track.id,
            'url': f"/static/audio/{track.filename}",
            'category': track.category,
            'loop': track.loop,
            'volume': track.volume,
            'description': track.description
        }
        for track in tracks
    ]
    
    return jsonify({
        'success': True,
        'event': event_name,
        'audio': audio_data
    }), 200


@audio_bp.route('/events', methods=['GET'])
def list_events():
    """
    Get list of all available audio events.
    
    Returns:
        JSON: List of event names
    """
    from game_logic.audio import EVENT_AUDIO_MAP
    
    return jsonify({
        'success': True,
        'events': list(EVENT_AUDIO_MAP.keys()),
        'total': len(EVENT_AUDIO_MAP)
    }), 200
