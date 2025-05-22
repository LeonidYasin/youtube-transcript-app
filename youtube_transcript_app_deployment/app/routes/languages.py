"""
API routes for language-related operations.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Dict, Any, Optional

from app.services import youtube_service
from app.models.schemas import LanguageInfo

# Create a router for language endpoints
router = APIRouter(prefix="", tags=["languages"])


@router.get("/available-languages", response_model=List[LanguageInfo])
async def get_available_languages() -> List[Dict[str, str]]:
    """
    Get list of available languages for subtitles.
    
    Returns:
        List of available languages with codes and names
    """
    try:
        return youtube_service.get_available_languages()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available languages: {str(e)}"
        )


@router.get("/available-languages/{video_id}", response_model=List[LanguageInfo])
async def get_available_languages_for_video(video_id: str) -> List[Dict[str, str]]:
    """
    Get list of available languages for a specific video.
    
    Note: This is a placeholder. In a real implementation, you would check
    the actual available languages for the video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of available languages with codes and names
    """
    try:
        # In a real implementation, we would check the available languages for this video
        # For now, we'll just return the common languages
        return youtube_service.get_available_languages()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available languages for video: {str(e)}"
        )
