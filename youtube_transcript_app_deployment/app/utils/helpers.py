"""
Helper functions for the YouTube Transcript API.
"""

import re
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any, List
import os


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL.
    
    Args:
        url: YouTube video URL or ID
        
    Returns:
        str or None: Video ID if found, None otherwise
    """
    if not url or not isinstance(url, str):
        return None
        
    # Remove any URL parameters that might be after the video ID
    url = url.split('&')[0]
    
    patterns = [
        # Standard YouTube URL
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|live\/)|youtu\.be\/)([\w-]{11})',
        # Just the video ID (11 characters)
        r'^([\w-]{11})$',
        # YouTube URL with additional path
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([\w-]{11})',
        # YouTube URL with additional parameters
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([\w-]{11})',
        # YouTube Shorts URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([\w-]{11})',
        # YouTube Live URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([\w-]{11})',
        # youtu.be URL
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([\w-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match and match.group(1):
            # Validate the video ID (should be 11 characters)
            video_id = match.group(1)
            if len(video_id) == 11 and all(c.isalnum() or c in {'-', '_'} for c in video_id):
                return video_id
    return None


def vtt_to_text(vtt_content: str) -> str:
    """
    Convert VTT content to clean text.
    
    Args:
        vtt_content: VTT formatted content
        
    Returns:
        str: Cleaned text content
    """
    if not vtt_content:
        return ""
    
    # Remove WEBVTT header
    vtt_content = re.sub(r'^WEBVTT.*?\n\n', '', vtt_content, flags=re.DOTALL)
    
    # Remove timestamps and speaker labels
    vtt_content = re.sub(r'\d{2}:\d{2}:\d{2}[\.\,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.\,]\d{3}\n', '', vtt_content)
    vtt_content = re.sub(r'\n\d+\n', '\n', vtt_content)  # Remove cue numbers
    vtt_content = re.sub(r'^<[^>]+>', '', vtt_content, flags=re.MULTILINE)  # Remove speaker labels
    
    # Remove HTML tags and extra whitespace
    vtt_content = re.sub(r'<[^>]+>', '', vtt_content)
    vtt_content = re.sub(r'\s+', ' ', vtt_content).strip()
    
    return vtt_content


def setup_logging(log_file: str = "youtube_transcript.log") -> None:
    """
    Configure logging for the application with UTF-8 encoding support.
    This function is safe to call multiple times and handles reloads properly.
    
    Args:
        log_file: Path to the log file (can be relative or absolute)
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Skip if already configured (prevents duplicate handlers on reload)
    if hasattr(setup_logging, '_configured'):
        return
       
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    
    # Clear existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        try:
            handler.close()
        except Exception as e:
            pass  # Ignore errors when closing handlers
        logger.removeHandler(handler)
    
    # Configure root logger
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler with UTF-8 encoding
    try:
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
    
    # Create console handler only if not in a subprocess
    if not os.environ.get('_UVICORN_WORKER'):
        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception as e:
            print(f"Warning: Could not set up console logging: {e}")
    
    # Configure third-party loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Log the log file location
    logger.info(f"Application logging initialized. Log file: {log_path}")
    
    # Mark as configured
    setup_logging._configured = True
