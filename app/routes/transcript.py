"""
API routes for transcript operations.
"""
import logging
import os
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, status, Query, Depends, Form, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Import services and utilities
from app.services.transcript_service import TranscriptService
from app.utils.url_parser import extract_video_id

# Set up logger
logger = logging.getLogger(__name__)

# Create API router
json_api_router = APIRouter(
    prefix="/api",
    tags=["transcript"],
    default_response_class=JSONResponse
)

# Create API router
api_router = APIRouter(
    prefix="/api",
    tags=["transcript"]
)

# Create web router for the HTML interface
web_router = APIRouter()

# Mount static files for the web interface
@web_router.get("/")
async def get_transcript_page(request: Request):
    """Serve the transcript extraction page."""
    if request.headers.get('accept') == 'application/json':
        return JSONResponse(content={"error": "html_only", "message": "This endpoint only serves HTML"})
    return FileResponse("templates/transcript.html")

@json_api_router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify the API is running."""
    return JSONResponse(content={"status": "success", "message": "Test endpoint is working"})

@json_api_router.get("/transcript")
async def get_transcript(
    request: Request,
    url: str = Query(..., description="YouTube video URL or ID"),
    language: str = Query("auto", description="Language code (2 letters) or 'auto' for auto-detection"),
    auto_generated: bool = Query(False, description="Whether to use auto-generated subtitles")
):
    """
    Get transcript for a YouTube video.
    
    Returns:
        JSON response with transcript data or error message
    """
    # Log request start
    logger.info("[REQUEST START] Processing transcript request")
    logger.info(f"[PARAMS] URL: {url}, Language: {language}, Auto-generated: {auto_generated}")
    logger.info(f"[HEADERS] {dict(request.headers)}")
    
    # Check content type
    accept_header = request.headers.get('accept', '')
    logger.info(f"[CONTENT_TYPE] Accept header: {accept_header}")
    
    if 'application/json' not in accept_header:
        error_msg = f"Invalid content type: {accept_header}"
        logger.warning(f"[WARNING] {error_msg}")
        response = JSONResponse(
            status_code=400,
            content={
                "error": "invalid_content_type",
                "message": "This endpoint only accepts JSON requests"
            }
        )
        logger.info(f"[RESPONSE] {response.status_code}: {response.body.decode()}")
        return response
    
    logger.info(f"[PROCESSING] Processing transcript request for URL: {url}")
    
    # Extract video ID from URL
    logger.info("[PROCESSING] Extracting video ID from URL")
    video_id = extract_video_id(url)
    if not video_id:
        logger.error(f"Invalid YouTube URL or ID: {url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL or video ID"
        )
        
    logger.info(f"Extracted video ID: {video_id}")
    
    # Initialize the transcript service
    transcript_service = TranscriptService()
    
    try:
        # Get the transcript
        transcript, detected_lang, _ = await transcript_service.get_transcript(
            video_id=video_id,
            language=language,
            auto_generated=auto_generated
        )
        
        # Prepare response data
        response_data = {
            "status": "success",
            "video_id": video_id,
            "language": detected_lang or language,
            "auto_generated": auto_generated,
            "transcript": transcript,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully retrieved transcript for video {video_id}")
        return JSONResponse(
            content=response_data,
            media_type="application/json"
        )
        
    except HTTPException as he:
        # Get the error details from the exception
        error_details = he.detail
        if isinstance(error_details, dict):
            error_response = error_details
        else:
            error_response = {"error": "transcript_error", "message": str(error_details)}
        
        logger.error(f"HTTP error processing request: {error_response}")
        return JSONResponse(
            status_code=he.status_code,
            content=error_response,
            media_type="application/json"
        )
    except Exception as e:
        logger.exception(f"Unexpected error processing request: {str(e)}")
        error_response = {
            "error": "internal_error",
            "message": str(e),
            "details": {
                "type": type(e).__name__,
                "args": e.args
            }
        }
        return JSONResponse(
            status_code=500,
            content=error_response,
            media_type="application/json"
        )

def _format_success_response(
    transcript: str,
    video_id: str,
    language: str,
    auto_generated: bool,
    response: Response
) -> Dict[str, Any]:
    """Format a successful transcript response with detailed logging."""
    logger.info("Formatting success response")
    logger.debug(f"Input - video_id: {video_id}, language: {language}, auto_generated: {auto_generated}")
    logger.debug(f"Transcript length: {len(transcript) if transcript else 0} characters")
    
    # Clean up the transcript
    try:
        logger.info("Cleaning subtitles...")
        cleaned_transcript = subtitle_service.clean_subtitles(transcript)
        logger.debug(f"Transcript length after cleaning: {len(cleaned_transcript) if cleaned_transcript else 0} characters")
        return cleaned_transcript
    except Exception as e:
        logger.error(f"Error cleaning subtitles: {str(e)}")
        # Fall back to original transcript if cleaning fails
        logger.warning("Using original transcript due to cleaning error")
        return transcript
    
    # Set response headers
    response.headers["X-Transcript-Source"] = "auto-generated" if auto_generated else "manual"
    response.headers["X-Video-ID"] = video_id
    response.headers["X-Language"] = language
    response.headers["X-Auto-Generated"] = str(auto_generated)
    
    logger.debug(f"Set response headers: {dict(response.headers)}")
    
    # Prepare response data
    response_data = TranscriptResponse(
        status="success",
        video_id=video_id,
        language=language,
        auto_generated=auto_generated,
        transcript=cleaned_transcript
    ).dict()
    
    logger.info("Successfully formatted response")
    logger.debug(f"Response data keys: {list(response_data.keys())}")
    
    # Log success (first 100 chars only to avoid log spam)
    preview = cleaned_transcript[:100].replace('\n', ' ').replace('\r', '')
    logger.info(
        "Successfully retrieved %stranscript. Preview: %s...",
        'auto-generated ' if auto_generated else '',
        preview
    )
    
    return response_data
