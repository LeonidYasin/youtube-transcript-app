"""
Services package - contains business logic for the application.
"""

from .youtube import YouTubeService
from .subtitles import SubtitleService

# Initialize services
youtube_service = YouTubeService()
subtitle_service = SubtitleService()
