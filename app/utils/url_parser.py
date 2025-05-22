"""
URL parsing utilities for extracting video IDs from YouTube URLs.
"""
from typing import Optional

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats.
    
    Args:
        url: YouTube URL or video ID
        
    Returns:
        Extracted video ID or None if invalid
    """
    if not url:
        return None
    
    # Handle youtu.be links
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0].split('/')[0]
    
    # Handle youtube.com/live/ URLs
    if 'youtube.com/live/' in url:
        return url.split('youtube.com/live/')[1].split('?')[0].split('/')[0]
    
    # Handle regular YouTube URLs
    if 'youtube.com/watch' in url and '?' in url:
        params = url.split('?')[1].split('&')
        for param in params:
            if param.startswith('v='):
                return param[2:].split('&')[0]
    
    # If no match found, check if it's already a video ID
    if _is_valid_video_id(url):
        return url
    
    return None

def _is_valid_video_id(video_id: str) -> bool:
    """
    Check if a string is a valid YouTube video ID.
    
    Args:
        video_id: String to validate
        
    Returns:
        bool: True if valid YouTube video ID, False otherwise
    """
    if not video_id or len(video_id) != 11:
        return False
    
    # YouTube video IDs can contain alphanumeric characters, dashes, and underscores
    valid_chars = (
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789-_'
    )
    
    return all(c in valid_chars for c in video_id)
