"""
story_engine.py - Story progression system for web version

Migration changes:
- Story data loaded from JSON file instead of Python dict
- No input()/print() - returns dicts for API responses
- Processes one node at a time per API call
- Returns structured data: text, choices, combat specs, music specs
- Maintains story state (current node key) in session
"""

import json
import os


# Cache for loaded story data
_STORY_DATA = None


def load_story_data():
    """
    Load story data from JSON file.
    Caches result for subsequent calls.
    
    Returns:
        dict: Story map with all nodes
    """
    global _STORY_DATA
    
    if _STORY_DATA is not None:
        return _STORY_DATA
    
    # Get path relative to this file
    json_path = os.path.join(os.path.dirname(__file__), 'story_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        _STORY_DATA = json.load(f)
    
    # Remove comment keys (starting with _)
    _STORY_DATA = {k: v for k, v in _STORY_DATA.items() if not k.startswith('_')}
    
    return _STORY_DATA


def get_node(node_key):
    """
    Get a specific story node by key.
    
    Args:
        node_key: str - Key of the node to retrieve
    
    Returns:
        dict: Node data, or None if not found
    """
    story_data = load_story_data()
    return story_data.get(node_key)


def process_story_node(node_key, choice_index=None, include_next=False):
    """
    Process a story node and return structured data for API response.
    
    Args:
        node_key: str - Current node to process
        choice_index: int - If node has choices, which one was selected (0-indexed)
        include_next: bool - If True, also return processed next_node data (avoids double-processing)
    
    Returns:
        dict: {
            'success': bool,
            'node_key': str (current node),
            'text': list of str (text lines to display),
            'music': dict or None (music change spec),
            'combat': dict or None (combat encounter spec),
            'doom_tick': int or None,
            'doom_reason': str or None,
            'choices': list of dict or None (available choices),
            'wait': bool (whether to wait for user acknowledgment),
            'next_node': str or None (auto-navigation to next node),
            'next_node_data': dict or None (only if include_next=True; processed next node),
            'is_ending': bool (whether this node ends the story),
            'quit_game': bool (whether game should quit)
        }
    """
    node = get_node(node_key)
    
    if not node:
        return {
            'success': False,
            'error': f'Story node not found: {node_key}',
            'node_key': node_key
        }
    
    result = {
        'success': True,
        'node_key': node_key,
        'text': [],
        'music': None,
        'combat': None,
        'doom_tick': None,
        'doom_reason': None,
        'choices': None,
        'wait': node.get('wait', True),
        'next_node': None,
        'next_node_data': None,
        'is_ending': node.get('end', False),
        'quit_game': node.get('quit', False),
        'travel': node.get('travel', False),  # Added travel flag
        'rewards': node.get('rewards'),  # Add rewards field
        'conduit_closed': node.get('conduit_closed', False)  # Add conduit_closed flag
    }
    
    # Extract text
    text = node.get('text', [])
    if isinstance(text, str):
        text = [text]
    result['text'] = text
    
    # Extract music
    music = node.get('music')
    if music:
        # Handle array of music specs (like fadeout then play)
        if isinstance(music, list):
            result['music'] = music
        else:
            result['music'] = music
    
    # Extract combat
    combat = node.get('combat')
    if combat:
        result['combat'] = combat
    
    # Extract doom clock
    if 'doom_tick' in node:
        result['doom_tick'] = node['doom_tick']
        result['doom_reason'] = node.get('doom_reason', 'The veil grows thinner...')
    
    # Extract choices
    choices = node.get('choices')
    if choices:
        result['choices'] = choices
        
        # If a choice was made, determine next node
        if choice_index is not None:
            if 0 <= choice_index < len(choices):
                result['next_node'] = choices[choice_index].get('next')
            else:
                result['success'] = False
                result['error'] = f'Invalid choice index: {choice_index}'
    else:
        # No choices - check for auto-navigation
        result['next_node'] = node.get('goto') or node.get('next')
    
    # Optionally process next node in single call to avoid double-processing
    if include_next and result['next_node'] and result['success']:
        next_data = process_story_node(result['next_node'], choice_index=None, include_next=False)
        if next_data['success']:
            result['next_node_data'] = next_data
    
    return result


def get_starting_nodes():
    """
    Get list of available starting nodes (chapters).
    
    Returns:
        list of dict: [{'key': str, 'title': str}, ...]
    """
    story_data = load_story_data()
    
    # Extract chapter nodes (those with "Chapter" in text)
    chapters = []
    for key, node in story_data.items():
        text = node.get('text', [])
        if isinstance(text, list) and len(text) > 0:
            first_line = text[0]
            if 'Chapter' in first_line or 'Chapter' in first_line:
                # Extract chapter title
                title = first_line.strip().split('\n')[0]
                chapters.append({
                    'key': key,
                    'title': title
                })
    
    return chapters


def validate_story_data():
    """
    Validate story data for broken links and missing nodes.
    
    Returns:
        dict: {
            'valid': bool,
            'errors': list of str,
            'warnings': list of str
        }
    """
    story_data = load_story_data()
    errors = []
    warnings = []
    
    # Check all referenced nodes exist
    all_keys = set(story_data.keys())
    
    for node_key, node in story_data.items():
        # Check goto/next references
        for ref_key in ['goto', 'next']:
            ref = node.get(ref_key)
            if ref and ref not in all_keys:
                errors.append(f"Node '{node_key}' references missing node '{ref}' in '{ref_key}'")
        
        # Check choice references
        choices = node.get('choices', [])
        for i, choice in enumerate(choices):
            next_node = choice.get('next')
            if next_node and next_node not in all_keys:
                errors.append(f"Node '{node_key}' choice {i} references missing node '{next_node}'")
        
        # Check combat enemy names
        combat = node.get('combat')
        if combat:
            enemies = combat.get('enemies', [])
            if not enemies:
                warnings.append(f"Node '{node_key}' has combat but no enemies specified")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def get_story_progress(visited_nodes):
    """
    Calculate story progress based on visited nodes.
    
    Args:
        visited_nodes: list of str - Keys of nodes already visited
    
    Returns:
        dict: {
            'chapter': int (1-5),
            'completion_percent': float,
            'endings_seen': list of str
        }
    """
    story_data = load_story_data()
    
    # Determine current chapter based on visited nodes
    chapter = 1
    if any('3_' in n for n in visited_nodes):
        chapter = 3
    elif any('2_' in n for n in visited_nodes):
        chapter = 2
    if any('4_' in n for n in visited_nodes):
        chapter = 4
    if any('5_' in n for n in visited_nodes):
        chapter = 5
    
    # Find endings
    endings_seen = []
    for node_key in visited_nodes:
        node = story_data.get(node_key, {})
        if node.get('quit'):
            # Extract ending name from text
            text = ' '.join(node.get('text', []))
            if 'ENDING:' in text:
                ending = text.split('ENDING:')[1].split(']')[0].strip()
                endings_seen.append(ending)
    
    # Calculate rough completion (5 chapters)
    completion_percent = (chapter / 5.0) * 100
    
    return {
        'chapter': chapter,
        'completion_percent': completion_percent,
        'endings_seen': endings_seen
    }
