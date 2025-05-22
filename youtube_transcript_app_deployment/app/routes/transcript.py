"""
API routes for transcript operations.
"""
import logging
from fastapi import APIRouter, Query, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, Tuple, Union
from pydantic import BaseModel

# Import services
from app.services import youtube_service, subtitle_service

# Set up logger
logger = logging.getLogger(__name__)

# Create a router for transcript endpoints
router = APIRouter(prefix="/transcript", tags=["transcript"])

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    if not url:
        return None
    
    # Handle youtu.be links
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0].split('/')[0]
    
    # Handle youtube.com/live/ URLs
    if 'youtube.com/live/' in url:
        return url.split('youtube.com/live/')[1].split('?')[0].split('/')[0]
    
    # Handle regular YouTube URLs
    if 'youtube.com/watch' in url and '?' in url:
        params = url.split('?')[1].split('&')
        for param in params:
            if param.startswith('v='):
                return param[2:].split('&')[0]
    
    # If no match found, assume the input is already a video ID
    return url if len(url) == 11 and all(c.isalnum() or c in ('-', '_') for c in url) else None

# HTML form for testing
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Transcript Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            background: #f9f9f9;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #444;
        }
        input[type="text"],
        select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background: #ff0000;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: background 0.3s;
        }
        button:hover {
            background: #cc0000;
        }
        button:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
        #result {
            margin-top: 25px;
            padding: 20px;
            background: white;
            border-radius: 4px;
            border: 1px solid #eee;
            min-height: 100px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
            line-height: 1.5;
        }
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .loading {
            text-align: center;
            padding: 15px;
            color: #666;
            display: none;
        }
        .success {
            color: #388e3c;
        }
        .transcript-info {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .transcript-content {
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Transcript Extractor</h1>
        <form id="transcriptForm">
            <div class="form-group">
                <label for="videoUrl">YouTube Video URL:</label>
                <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=..." required>
            </div>
            <div class="form-group">
                <label for="language">Language:</label>
                <select id="language">
                    <option value="auto">Auto-detect</option>
                    <option value="en">English</option>
                    <option value="ru">Русский</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="it">Italiano</option>
                    <option value="pt">Português</option>
                    <option value="zh-Hans">中文 (简体)</option>
                    <option value="zh-Hant">中文 (繁體)</option>
                    <option value="ja">日本語</option>
                    <option value="ko">한국어</option>
                    <option value="ar">العربية</option>
                    <option value="he">עברית</option>
                </select>
            </div>
            <button type="submit" id="submitBtn">Get Transcript</button>
        </form>
        <div id="loading" class="loading">
            Loading transcript...
        </div>
        <div id="result"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded');
            
            const form = document.getElementById('transcriptForm');
            const videoUrlInput = document.getElementById('videoUrl');
            const languageSelect = document.getElementById('language');
            const submitBtn = document.getElementById('submitBtn');
            const loadingDiv = document.getElementById('loading');
            const resultDiv = document.getElementById('result');

            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('Form submitted');
                
                const videoUrl = videoUrlInput.value.trim();
                const language = languageSelect.value;
                
                if (!videoUrl) {
                    showError('Please enter a YouTube URL');
                    return;
                }
                
                const videoId = extractVideoId(videoUrl);
                if (!videoId) {
                    showError('Invalid YouTube URL. Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ');
                    return;
                }
                
                // Show loading, clear previous results
                setLoading(true);
                resultDiv.innerHTML = '';
                
                try {
                    const response = await fetch(`/api/transcript?url=${encodeURIComponent(videoId)}&language=${encodeURIComponent(language)}`);
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to fetch transcript');
                    }
                    
                    // Display the result
                    if (data.status === 'success') {
                        showTranscript(data);
                    } else {
                        throw new Error(data.message || 'Unknown error occurred');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showError(error.message || 'An error occurred while fetching the transcript');
                } finally {
                    setLoading(false);
                }
            });
            
            function extractVideoId(url) {
                
                // Handle youtu.be links
                if (url.includes('youtu.be/')) {
                    return url.split('youtu.be/')[1].split(/[?&#]/)[0];
                }
                
                // Handle youtube.com/live/
                const liveMatch = url.match(/youtube\.com\/live\/([a-zA-Z0-9_-]+)/);
                if (liveMatch) return liveMatch[1];
                
                // Handle regular URLs
                const match = url.match(/[?&]v=([^&#]+)/) || url.match(/\/([a-zA-Z0-9_-]{11})/);
                return match ? match[1] : null;
            }
            
            function showTranscript(data) {
                const languageNames = {
                    'en': 'English',
                    'ru': 'Русский',
                    'es': 'Español',
                    'fr': 'Français',
                    'de': 'Deutsch',
                    'it': 'Italiano',
                    'pt': 'Português',
                    'zh-Hans': '中文 (简体)',
                    'zh-Hant': '中文 (繁體)',
                    'ja': '日本語',
                    'ko': '한국어',
                    'ar': 'العربية',
                    'he': 'עברית'
                };
                
                const langName = languageNames[data.language] || data.language;
                const isAuto = data.language === 'auto';
                const isAutoGenerated = data.auto_generated ? ' (Auto-generated)' : '';
                
                resultDiv.innerHTML = `
                    <div class="success">
                        <p><strong>Language:</strong> ${langName}${isAutoGenerated}${isAuto ? ' (Auto-detected)' : ''}</p>
                    </div>
                    <div class="transcript">
                        ${data.transcript.replace(/\n/g, '<br>')}
                    </div>
                `;
            }
            
            function showError(message) {
                resultDiv.innerHTML = `<div class="error">${message}</div>`;
            }
            
            function setLoading(isLoading) {
                if (isLoading) {
                    submitBtn.disabled = true;
                    loadingDiv.style.display = 'block';
                } else {
                    submitBtn.disabled = false;
                    loadingDiv.style.display = 'none';
                }
            }
        });
    </script>
</html>
"""

@router.get("/page", response_class=HTMLResponse)
async def get_transcript_page():
    """Serve the transcript extraction page."""
    return HTMLResponse(content=HTML_FORM, status_code=200)

@router.get("/test")
async def test_transcript_endpoint():
    return {"message": "Transcript endpoint test successful"}

# Response model for successful transcript response
class TranscriptResponse(BaseModel):
    status: str
    video_id: str
    language: str
    auto_generated: bool
    transcript: str

# Response model for error response
class ErrorResponse(BaseModel):
    status: str
    error: str
    message: str

@router.get("/", 
          response_model=Union[TranscriptResponse, ErrorResponse],
          responses={
              200: {"model": TranscriptResponse, "description": "Successfully retrieved transcript"},
              400: {"model": ErrorResponse, "description": "Invalid request parameters"},
              404: {"model": ErrorResponse, "description": "Transcript not found"},
              500: {"model": ErrorResponse, "description": "Internal server error"}
          })
async def get_transcript(
    request: Request,
    response: Response,
    url: str = Query(..., description="YouTube video URL or ID"),
    language: str = Query("auto", description="Language code (e.g., 'en', 'ru', 'es')"),
    auto_generated: bool = Query(False, description="Whether to use auto-generated subtitles")
) -> Union[Dict[str, Any], JSONResponse]:
    """
    Get transcript for a YouTube video.
    
    Args:
        url: YouTube video URL or ID
        language: Language code for subtitles (default: 'auto')
        auto_generated: Whether to use auto-generated subtitles (default: False)
        
    Returns:
        JSON response with transcript data or error message
    """
    logger.info("=== NEW TRANSCRIPT REQUEST ===")
    logger.info("Headers: %s", dict(request.headers))
    logger.info("Query params: %s", dict(request.query_params))
    logger.info("URL: %s", url)

    # Default to auto if language not provided
    if language is None:
        language = "auto"
        
    # Validate language code if provided
    if language != "auto" and (not isinstance(language, str) or len(language) != 2):
        error_response = ErrorResponse(
            status="error",
            error=f"Invalid language code: {language}",
            message="Use a 2-letter language code or 'auto'"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.dict()
        )
        
    # Extract video ID from URL
    video_id = extract_video_id(url)
    if not video_id:
        error_response = ErrorResponse(
            status="error",
            error="Invalid YouTube URL or video ID",
            message="Please provide a valid YouTube URL or video ID"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.dict()
        )
        
    logger.info("Processing request for video: %s", url)
    
    try:
        # First try with the requested language and auto_generated setting
        result = youtube_service.get_subtitles(video_id, language, auto_generated)
        
        # Check if the result is None or not a tuple
        if result is None:
            error_msg = "No data returned from YouTube service"
            logger.error(error_msg)
            error_response = ErrorResponse(
                status="error",
                error=error_msg,
                message="The YouTube service did not return any data"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response.dict()
            )
            
        transcript, lang_or_error = result
        
        # Log the result for debugging
        logger.info("Got response from youtube_service.get_subtitles(): transcript=%s, lang_or_error=%s", 
                   transcript is not None, lang_or_error)
        
        # If we have a transcript, return it
        if transcript is not None:
            return _format_success_response(
                transcript=transcript,
                video_id=video_id,
                language=lang_or_error if (isinstance(lang_or_error, str) and len(lang_or_error) == 2) else "unknown",
                auto_generated=auto_generated,
                response=response
            )
        
        # If we get here, we don't have a transcript but might have an error message
        error = lang_or_error if isinstance(lang_or_error, str) else "Unknown error"
        logger.warning("Failed to get subtitles: %s", error)
        
        # If auto_generated is False, try with auto_generated=True
        if not auto_generated:
            logger.info("Trying with auto-generated subtitles for video ID: %s", video_id)
            result = youtube_service.get_subtitles(video_id, language, auto_generated=True)
            
            # Check if we got a valid result
            if result and isinstance(result, tuple) and len(result) == 2 and result[0]:
                transcript, lang_or_error = result
                return _format_success_response(
                    transcript=transcript,
                    video_id=video_id,
                    language=lang_or_error if (isinstance(lang_or_error, str) and len(lang_or_error) == 2) else "unknown",
                    auto_generated=True,
                    response=response
                )
        
        # If we get here, we've tried both with and without auto-generated subtitles and failed
        error_msg = f"Failed to retrieve transcript: {error}"
        logger.error(error_msg)
        error_response = ErrorResponse(
            status="error",
            error=str(error),
            message=error_msg
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response.dict()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.exception("Unexpected error processing request")
        error_response = ErrorResponse(
            status="error",
            error="Internal server error",
            message="An unexpected error occurred while processing your request"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )

def _format_success_response(
    transcript: str,
    video_id: str,
    language: str,
    auto_generated: bool,
    response: Response
) -> Dict[str, Any]:
    """Format a successful transcript response."""
    # Clean and format the transcript
    cleaned_text = subtitle_service.clean_subtitles(transcript)
    
    # Add metadata to response headers
    response.headers["X-Transcript-Source"] = "auto-generated" if auto_generated else "manual"
    
    # Log success (first 100 chars only to avoid log spam)
    preview = cleaned_text[:100].replace('\n', ' ').replace('\r', '')
    logger.info(
        "Successfully retrieved %stranscript. Preview: %s...",
        'auto-generated ' if auto_generated else '',
        preview
    )
    
    # Return response that matches the TranscriptResponse model
    return TranscriptResponse(
        status="success",
        video_id=video_id,
        language=language,
        auto_generated=auto_generated,
        transcript=cleaned_text
    ).dict()
