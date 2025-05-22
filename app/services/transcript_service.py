"""
Core service for handling transcript-related operations.
"""
import logging
import time
from typing import Tuple, Optional, Dict, Any

from fastapi import HTTPException, status

from app.schemas.transcript import ErrorResponse
from app.services.youtube import YouTubeService
from app.services import subtitle_service

logger = logging.getLogger(__name__)

class TranscriptService:
    """Service for handling transcript-related operations."""

    def __init__(self):
        """Initialize the TranscriptService with required services."""
        self.youtube_service = YouTubeService()

    async def get_transcript(
        self,
        video_id: str,
        language: str = "auto",
        auto_generated: bool = False
    ) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """
        Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language: Language code or 'auto' for auto-detection
            auto_generated: Whether to use auto-generated subtitles
            
        Returns:
            Tuple of (transcript, detected_language, metadata)
        """
        logger.info("[TRANSCRIPT] Starting transcript retrieval")
        logger.info(f"[TRANSCRIPT] Video ID: {video_id}")
        logger.info(f"[TRANSCRIPT] Language: {language if language != 'auto' else 'auto (will detect)'}")
        logger.info(f"[TRANSCRIPT] Auto-generated: {auto_generated}")
        
        try:
            start_time = time.time()
            
            # Get subtitles from YouTube
            logger.info("[TRANSCRIPT] Fetching subtitles from YouTube API")
            try:
                logger.info(f"[TRANSCRIPT] Calling YouTubeService.get_subtitles with params: video_id={video_id}, lang={language if language != 'auto' else None}, auto_generated={auto_generated}")
                transcript, detected_lang = await self.youtube_service.get_subtitles(
                    video_id,
                    lang=language if language != 'auto' else None,
                    auto_generated=auto_generated
                )
                logger.info(f"[TRANSCRIPT] YouTubeService.get_subtitles returned: transcript={bool(transcript)}, detected_lang={detected_lang}")
                logger.info(f"[TRANSCRIPT] Successfully retrieved subtitles")
                if detected_lang:
                    logger.info(f"[TRANSCRIPT] Detected language: {detected_lang}")
            except Exception as e:
                error_msg = f"Error fetching subtitles: {str(e)}"
                logger.error(f"[TRANSCRIPT] {error_msg}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ErrorResponse(
                        error="youtube_api_error",
                        message=error_msg
                    ).dict()
                )
            
            request_duration = time.time() - start_time
            logger.info(f"[TRANSCRIPT] Subtitle retrieval completed in {request_duration:.2f} seconds")
            
            if not transcript:
                # If the error message is a dictionary, use it directly
                if isinstance(detected_lang, dict):
                    error_response = detected_lang
                else:
                    error_response = {
                        "error": "no_subtitles",
                        "message": f"No subtitles found for video {video_id}",
                        "details": {
                            "video_id": video_id,
                            "language": language,
                            "auto_generated": auto_generated
                        }
                    }
                
                logger.error(f"[TRANSCRIPT] {error_response}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response
                )
            
            # Clean the transcript
            logger.info("[TRANSCRIPT] Cleaning subtitles")
            try:
                cleaned_transcript = subtitle_service.clean_subtitles(transcript)
                logger.info(f"[TRANSCRIPT] Subtitles cleaned. Original length: {len(transcript)}, Cleaned length: {len(cleaned_transcript)}")
            except Exception as e:
                error_msg = f"Error cleaning subtitles: {str(e)}"
                logger.error(f"[TRANSCRIPT] {error_msg}", exc_info=True)
                # Fallback to original transcript if cleaning fails
                cleaned_transcript = transcript
            
            # Prepare metadata
            metadata = {
                "processing_time": request_duration,
                "original_length": len(transcript),
                "cleaned_length": len(cleaned_transcript),
                "language_detected": detected_lang or language,
                "auto_generated": auto_generated
            }
            
            logger.info(f"[TRANSCRIPT] Transcript processing completed successfully")
            return cleaned_transcript, detected_lang, metadata
            
        except HTTPException as he:
            logger.error(f"[TRANSCRIPT] HTTP Error: {str(he.detail) if hasattr(he, 'detail') else str(he)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error retrieving subtitles: {str(e)}"
            logger.error(f"[TRANSCRIPT] {error_msg}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error="internal_error",
                    message=error_msg
                ).dict()
            )

    @staticmethod
    def validate_language(language: str) -> None:
        """
        Validate language code format.
        
        Args:
            language: Language code to validate
            
        Raises:
            HTTPException: If language code is invalid
        """
        if language != "auto" and (not isinstance(language, str) or len(language) != 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error="invalid_language",
                    message="Use a 2-letter language code or 'auto'"
                ).dict()
            )
