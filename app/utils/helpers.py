"""
Helper functions for the YouTube Transcript API.
"""

import re
import sys
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
    
    Args:
        log_file: Name of the log file
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set up console logging by default
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)-8s - %(name)-25s - %(message)s [%(filename)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to root logger
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    
    # Try to set up file logging
    try:
        # Get the base directory (3 levels up from this file)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.path.join(base_dir, 'logs')
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        log_path = os.path.join(log_dir, log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Add file handler to root logger
        logger.addHandler(file_handler)
        
        logger.info(f"File logging initialized. Log file: {log_path}")
    except Exception as e:
        # If file logging fails, log to stderr
        import traceback
        print(f"ERROR: Failed to set up file logging: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        
        # Fall back to console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.error(f"Failed to set up file logging: {e}")
    
    # Always add console handler for errors and above
    try:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only INFO and above to console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug("Console logging initialized")
    except Exception as e:
        print(f"ERROR: Failed to set up console logging: {e}", file=sys.stderr)
    
    # Configure third-party loggers - keep these at WARNING to reduce noise
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log the log file location
    logger.info(f"Application logging initialized. Log file: {log_path}")
    logger.debug("Debug logging is enabled")
    
    # Log environment information
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Running on: {sys.platform}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    # Mark as configured
    setup_logging._configured = True
    logger.debug("Logging configuration complete")
