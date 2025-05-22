from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.youtube_service import YouTubeService

# Create a router for channel endpoints
router = APIRouter(prefix="", tags=["channel"])
youtube_service = YouTubeService()

@router.get("/search")
async def search_channels(
    query: str,
    max_results: int = Query(10, ge=1, le=50, description="Максимальное количество результатов (1-50)")
):
    """
    Поиск каналов на YouTube по ключевому слову
    
    - **query**: Поисковый запрос (название канала или ключевые слова)
    - **max_results**: Максимальное количество возвращаемых результатов
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Поисковый запрос не может быть пустым")
            
        channels = await youtube_service.search_channels(query, max_results)
        return {
            "status": "success",
            "results": channels,
            "count": len(channels)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{channel_id}/videos")
async def get_channel_videos(
    channel_id: str,
    max_results: int = Query(10, ge=1, le=50, description="Максимальное количество видео (1-50)")
):
    """
    Получение списка видео канала
    
    - **channel_id**: ID канала
    - **max_results**: Максимальное количество возвращаемых видео
    """
    try:
        videos = await youtube_service.get_channel_videos(channel_id, max_results)
        return {
            "status": "success",
            "channel_id": channel_id,
            "videos": videos,
            "count": len(videos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
