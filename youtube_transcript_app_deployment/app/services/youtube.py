"""
YouTube service for handling video and transcript operations.
"""

import logging
import pkg_resources
import json
import tempfile
import os
from typing import Optional, Tuple, List, Dict, Any

# Try to import youtube-transcript-api
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("youtube-transcript-api not available. Only yt-dlp will be used.")

# Try to import yt-dlp
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("yt-dlp not available. Some features may be limited.")

from ..utils.helpers import extract_video_id

logger = logging.getLogger(__name__)

def get_youtube_transcript_api_version() -> str:
    """Get the installed version of youtube-transcript-api."""
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        return "not_installed"
    try:
        return pkg_resources.get_distribution("youtube-transcript-api").version
    except Exception as e:
        logger.warning(f"Could not determine youtube-transcript-api version: {e}")
        return "unknown"

class YouTubeService:
    """Service for interacting with YouTube videos and transcripts."""
    
    def __init__(self):
        self.api_version = get_youtube_transcript_api_version() if YOUTUBE_TRANSCRIPT_AVAILABLE else "not_installed"
        logger.info(f"Using youtube-transcript-api version: {self.api_version}")
        logger.info(f"Using yt-dlp: {'available' if YT_DLP_AVAILABLE else 'not available'}")
    
    def get_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL."""
        return extract_video_id(url)
    
    def _handle_old_api(self, video_id: str, lang: str = "ru") -> Tuple[Optional[str], Optional[str]]:
        """Handle transcript retrieval for older versions of the API (<=0.6.1)."""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            return None, "youtube-transcript-api not available"
            
        try:
            # First try with the requested language
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, 
                    languages=[lang],
                    preserve_formatting=True
                )
                if transcript:
                    formatter = TextFormatter()
                    transcript_text = formatter.format_transcript(transcript)
                    return transcript_text, lang
            except Exception as e:
                # If that fails, try to get any available transcript
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(
                        video_id,
                        preserve_formatting=True
                    )
                    if transcript:
                        # We don't know the actual language with the old API, just return what we found
                        formatter = TextFormatter()
                        transcript_text = formatter.format_transcript(transcript)
                        return transcript_text, "unknown"
                except Exception as e2:
                    pass  # We'll handle the error below
            
            # If we get here, both attempts failed
            error_msg = str(e).lower()
            if "no transcript found" in error_msg:
                return None, f"No {'auto-generated ' if lang == 'en' else ''}transcript available in {lang}"
            return None, f"Error retrieving transcript (old API): {str(e)}"
            
        except Exception as e:
            error_msg = str(e).lower()
            if "no transcript found" in error_msg:
                return None, f"No {'auto-generated ' if lang == 'en' else ''}transcript available in {lang}"
            return None, f"Error retrieving transcript (old API): {str(e)}"
    
    def _handle_new_api(self, video_id: str, lang: str = "ru", auto_generated: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """Handle transcript retrieval for newer versions of the API (>0.6.1)."""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            return None, "youtube-transcript-api not available"
            
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find the requested transcript
            try:
                if auto_generated:
                    transcript = transcript_list.find_generated_transcript([lang])
                else:
                    transcript = transcript_list.find_manually_created_transcript([lang])
                
                transcript_pieces = transcript.fetch()
                formatter = TextFormatter()
                return formatter.format_transcript(transcript_pieces), None
                
            except Exception as e:
                # If we couldn't find the exact match, try to find any transcript in the requested language
                try:
                    transcript = transcript_list.find_transcript([lang])
                    transcript_pieces = transcript.fetch()
                    formatter = TextFormatter()
                    return formatter.format_transcript(transcript_pieces), None
                except Exception as e2:
                    # If we still can't find it, try to find any transcript at all
                    try:
                        # Get the first available transcript
                        transcript = next(iter(transcript_list))
                        found_lang = transcript.language_code
                        transcript_pieces = transcript.fetch()
                        formatter = TextFormatter()
                        return formatter.format_transcript(transcript_pieces), found_lang
                    except Exception as e3:
                        # If all else fails, return the original error
                        error_msg = str(e).lower()
                        if "no transcript found" in error_msg or "could not find a transcript" in error_msg:
                            return None, f"No transcript found in {lang}"
                        return None, f"Error retrieving transcript (new API): {str(e)}"
            
        except Exception as e:
            error_msg = str(e).lower()
            if "no transcript found" in error_msg or "could not find a transcript" in error_msg:
                return None, f"No transcript found in {lang}"
            return None, f"Error retrieving transcript (new API): {str(e)}"
    
    def _get_subtitles_with_ytdlp(self, video_id: str, lang: str = "ru") -> Tuple[Optional[str], Optional[str]]:
        """Get subtitles using yt-dlp as a fallback."""
        if not YT_DLP_AVAILABLE:
            return None, "yt-dlp is not available"
            
        try:
            # Create a temporary directory for the subtitles
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': [lang],
                    'quiet': True,
                    'no_warnings': True,
                    'outtmpl': os.path.join(temp_dir, '%(id)s'),
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract info to get available subtitles
                    info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                    
                    # Check if subtitles are available
                    if not info.get('automatic_captions') and not info.get('subtitles'):
                        return None, "No subtitles available for this video"
                    
                    # Download the subtitles
                    ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
                    
                    # Look for the downloaded subtitle file
                    sub_file = os.path.join(temp_dir, f"{video_id}.{lang}.vtt")
                    if not os.path.exists(sub_file):
                        # Try with auto-generated subtitles
                        sub_file = os.path.join(temp_dir, f"{video_id}.{lang}.vtt")
                        if not os.path.exists(sub_file):
                            return None, "Could not find downloaded subtitles"
                    
                    # Read and return the subtitle content
                    with open(sub_file, 'r', encoding='utf-8') as f:
                        return f.read(), None
                        
        except Exception as e:
            return None, f"Error retrieving transcript with yt-dlp: {str(e)}"
    
    def get_subtitles(self, video_id: str, lang: str = None, auto_generated: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        Get subtitles for a YouTube video, trying multiple methods.
        
        Args:
            video_id: YouTube video ID
            lang: Language code (e.g., 'en', 'ru', 'he'). If None, will try to get native language subtitles.
            auto_generated: Whether to prefer auto-generated subtitles
            
        Returns:
            Tuple of (transcript_text, language_or_error) where language_or_error is either the language code
            of the found transcript or an error message if no transcript was found
        """
        errors = []
        
        # Try youtube-transcript-api first if available
        if YOUTUBE_TRANSCRIPT_AVAILABLE:
            try:
                # If no language specified, try to get native language subtitles
                if lang is None:
                    logger.info("No language specified, trying to get native language subtitles")
                    try:
                        # First try to get the video's native language
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        native_lang = transcript_list.video_language_code
                        logger.info(f"Found video's native language: {native_lang}")
                        
                        # Try to get manual subtitles in native language
                        try:
                            transcript = transcript_list.find_manually_created_transcript([native_lang])
                            transcript_pieces = transcript.fetch()
                            formatter = TextFormatter()
                            return formatter.format_transcript(transcript_pieces), native_lang
                        except Exception as e:
                            logger.info(f"No manual subtitles in native language, trying auto-generated: {str(e)}")
                            # If no manual subtitles, try auto-generated in native language
                            try:
                                transcript = transcript_list.find_generated_transcript([native_lang])
                                transcript_pieces = transcript.fetch()
                                formatter = TextFormatter()
                                return formatter.format_transcript(transcript_pieces), f"{native_lang} (auto-generated)"
                            except Exception as e2:
                                logger.info(f"No auto-generated subtitles in native language: {str(e2)}")
                    except Exception as e:
                        logger.warning(f"Could not determine native language: {str(e)}")
                        pass  # Continue with the rest of the logic
                
                # If we get here, either a specific language was requested or we couldn't determine native language
                logger.info(f"Trying to get subtitles for language: {lang if lang else 'any'}")
                
                # Try with the new API first if available
                if pkg_resources.parse_version(self.api_version) > pkg_resources.parse_version("0.6.1"):
                    result = self._handle_new_api(video_id, lang, auto_generated)
                    if result[0] is not None:
                        logger.info(f"Successfully retrieved transcript using new API in language: {result[1]}")
                        return result
                    errors.append(f"New API: {result[1] if len(result) > 1 else 'Unknown error'}")
                
                # Fall back to old API if new API fails or is not available
                result = self._handle_old_api(video_id, lang if lang else 'en')
                if result[0] is not None:
                    logger.info(f"Successfully retrieved transcript using old API in language: {result[1]}")
                    return result
                errors.append(f"Old API: {result[1] if len(result) > 1 else 'Unknown error'}")
                        
            except Exception as e:
                error_msg = str(e).lower()
                if any(term in error_msg for term in ["video unavailable", "not found", "does not exist"]):
                    return None, "Video is not available (may have been removed)"
                elif "private" in error_msg or "members only" in error_msg:
                    return None, "Video is private or requires sign-in"
                elif "disabled" in error_msg:
                    return None, "Subtitles are disabled for this video"
                errors.append(f"youtube-transcript-api error: {str(e)}")
        else:
            errors.append("youtube-transcript-api not installed")
        
        # If we get here, youtube-transcript-api failed or is not available, try yt-dlp
        if YT_DLP_AVAILABLE:
            logger.info(f"Trying to get subtitles with yt-dlp for language: {lang}")
            result = self._get_subtitles_with_ytdlp(video_id, lang)
            if result[0] is not None:
                logger.info("Successfully retrieved transcript using yt-dlp")
                return result
            else:
                errors.append(f"yt-dlp: {result[1] if result[1] else 'Unknown error'}")
        else:
            errors.append("yt-dlp not installed")
        
        # If we get here, all methods failed
        return None, "Could not retrieve transcript. Errors: " + "; ".join(errors)
