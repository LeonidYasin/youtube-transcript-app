"""
Subtitle processing service.
"""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SubtitleService:
    """Service for processing and cleaning subtitles."""
    
    def clean_subtitles(self, text: str) -> str:
        """
        Clean and format subtitle text with proper handling of special characters.
        
        Args:
            text: Raw subtitle text
            
        Returns:
            str: Cleaned text with proper encoding
        """
        if not text:
            return ""
        
        try:
            # Normalize line endings and remove any BOM characters
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            text = text.strip('\ufeff')
            
            # Remove timestamps and metadata
            text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}.*?(\n|$)', '', text)
            
            # Remove speaker labels and other annotations
            text = re.sub(r'^\s*[A-Z\s]+:', '', text, flags=re.MULTILINE)
            
            # Remove any remaining HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Remove text in square and round brackets (often used for sound effects or notes)
            text = re.sub(r'\[[^\]]+\]|\([^)]+\)', '', text)
            
            # Handle common special characters and normalize whitespace
            text = re.sub(r'[�]', '', text)  # Remove replacement characters
            text = re.sub(r'[\u200b-\u200f]', '', text)  # Remove zero-width spaces
            text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)  # Remove control characters
            
            # Normalize quotation marks and other common special characters
            text = text.replace('\"', '"').replace('\'', "'")
            text = text.replace('–', '-').replace('—', '-')  # Different types of dashes
            text = text.replace('…', '...')  # Ellipsis
            
            # Preserve musical notes and other special characters but normalize them
            text = text.replace('♪', '♫').replace('♩', '♫')  # Standardize musical notes
            
            # Normalize whitespace and clean up
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Ensure proper line breaks between paragraphs
            text = re.sub(r'([.!?])\s+', r'\1\n\n', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove empty lines
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning subtitle text: {str(e)}")
            # Return the original text if cleaning fails
            return text
    
    def format_transcript(self, text: str, language: str, video_id: str) -> Dict[str, Any]:
        """
        Format transcript into a structured response.
        
        Args:
            text: Transcript text
            language: Language code
            video_id: YouTube video ID
            
        Returns:
            dict: Formatted transcript response
        """
        return {
            "text": text,
            "language": language,
            "video_id": video_id
        }
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get the display name for a language code.
        
        Args:
            lang_code: Language code (e.g., 'ru', 'en')
            
        Returns:
            str: Language display name
        """
        language_map = {
            'ru': 'Русский',
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ja': '日本語',
            'ko': '한국어',
            'zh-Hans': '中文(简体)',
            'zh-Hant': '中文(繁體)',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'bn': 'বাংলা',
            'pa': 'ਪੰਜਾਬੀ',
            'te': 'తెలుగు',
            'mr': 'मराठी',
            'ta': 'தமிழ்',
            'ur': 'اردو',
            'gu': 'ગુજરાતી',
            'kn': 'ಕನ್ನಡ',
            'or': 'ଓଡ଼ିଆ',
            'ml': 'മലയാളം'
        }
        
        return language_map.get(lang_code, lang_code)
