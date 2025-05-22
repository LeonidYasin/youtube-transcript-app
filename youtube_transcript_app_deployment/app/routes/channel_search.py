from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.services.youtube_search import YouTubeSearcher

# Create a router for channel search functionality
router = APIRouter(prefix="", tags=["channel-search"])

@router.get("/search")
async def search_channels(
    query: str = Query(..., description="Search query for YouTube channels"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum number of results (1-20)")
) -> Dict[str, Any]:
    """
    Search for YouTube channels by query
    """
    result = YouTubeSearcher.search_channels(query, max_results)
    
    if result['status'] != 'success':
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Failed to search for channels: {result.get('message')}",
                "error_type": result.get('error_type')
            }
        )
    
    return result

@router.get("/rabbi-ginsburgh")
async def get_rabbi_ginsburgh_channel() -> Dict[str, Any]:
    """
    Get Rabbi Yitzchak Ginsburgh's official YouTube channel
    """
    channel = YouTubeSearcher.find_rabbi_ginsburgh_channel()
    
    if not channel:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Rabbi Yitzchak Ginsburgh's channel not found"
            }
        )
    
    return {
        "status": "success",
        "channel": channel
    }
