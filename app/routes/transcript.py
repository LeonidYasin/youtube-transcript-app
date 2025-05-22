"""
API routes for transcript operations.
"""
import logging
import os
from fastapi import APIRouter, Query, Request, Response, status, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any, Tuple, Union, List
from pydantic import BaseModel
from datetime import datetime

# Import services
from app.services import youtube_service, subtitle_service

# Set up logger
logger = logging.getLogger(__name__)

# Create a router for transcript endpoints
router = APIRouter(prefix="/transcript", tags=["transcript"])

# Set up templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

# Mount static files
router.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")), name="static")

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
        // Add debug logging function
        function logToServer(level, message, data = {}) {
            console[level](`[${level.toUpperCase()}] ${message}`, data);
            // Send log to server
            fetch('/api/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    level: level,
                    message: message,
                    data: data,
                    timestamp: new Date().toISOString()
                })
            }).catch(err => console.error('Failed to send log:', err));
        }

        document.addEventListener('DOMContentLoaded', function() {
            logToServer('info', 'Page loaded', {
                url: window.location.href,
                userAgent: navigator.userAgent
            });

            // Function to simulate button click
            function simulateButtonClick() {
                console.log('Simulating button click...');
                const button = document.querySelector('button[type="submit"]');
                if (button) {
                    console.log('Button found, clicking...');
                    button.click();
                } else {
                    console.error('Submit button not found!');
                }
            }

            // First make a test request to ensure backend is working
            console.log('Making initial test request to backend...');
            fetch('/api/transcript/test')
                .then(response => response.json())
                .then(data => {
                    console.log('Test request successful, proceeding with form submission...');
                    logToServer('info', 'Test request successful', data);
                    
                    // Fill the form with test data if fields are empty
                    const videoUrlInput = document.getElementById('videoUrl');
                    if (videoUrlInput && !videoUrlInput.value) {
                        videoUrlInput.value = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
                    }
                    
                    // Simulate button click after a short delay
                    setTimeout(simulateButtonClick, 1000);
                })
                .catch(error => {
                    console.error('Test request failed:', error);
                    logToServer('error', 'Test request failed', { error: error.toString() });
                });
            
            const form = document.getElementById('transcriptForm');
            const videoUrlInput = document.getElementById('videoUrl');
            const languageSelect = document.getElementById('language');
            const submitBtn = document.getElementById('submitBtn');
            const loadingDiv = document.getElementById('loading');
            const resultDiv = document.getElementById('result');

            form.addEventListener('submit', async function(e) {
                console.log('=== FORM SUBMIT EVENT TRIGGERED ===');
                console.log('Event type:', e.type);
                
                // Prevent default form submission
                e.preventDefault();
                console.log('Default form submission prevented');
                
                // Show loading state
                setLoading(true);
                resultDiv.innerHTML = '';
                
                const videoUrl = videoUrlInput.value.trim();
                const language = languageSelect.value;
                
                // Log to server
                logToServer('info', 'Form submission started', {
                    videoUrl,
                    language,
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent
                });
                
                console.log('Starting form processing...');
                
                if (!videoUrl) {
                    const errorMsg = 'Please enter a YouTube URL';
                    logToServer('error', errorMsg);
                    showError(errorMsg);
                    setLoading(false);
                    return;
                }
                
                console.log('Extracting video ID from URL:', videoUrl);
                const videoId = extractVideoId(videoUrl);
                console.log('Extracted video ID:', videoId);
                
                logToServer('debug', 'Extracted video ID', { 
                    videoId, 
                    videoUrl,
                    timestamp: new Date().toISOString()
                });
                
                if (!videoId) {
                    const errorMsg = 'Invalid YouTube URL';
                    console.error('Failed to extract video ID from URL:', videoUrl);
                    logToServer('error', errorMsg, { 
                        videoUrl,
                        timestamp: new Date().toISOString()
                    });
                    showError(errorMsg + '. Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ');
                    setLoading(false);
                    return;
                }
                
                try {
                    console.log('Sending request to server...');
                    const response = await fetch(`/api/transcript?url=${encodeURIComponent(videoId)}&language=${encodeURIComponent(language)}`);
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.message || 'Failed to fetch transcript');
                    }
                    
                    console.log('Received response from server:', data);
                    logToServer('info', 'Transcript received', { 
                        videoId,
                        language: data.language,
                        autoGenerated: data.auto_generated,
                        transcriptLength: data.transcript ? data.transcript.length : 0
                    });
                    
                    showTranscript(data);
                } catch (error) {
                    console.error('Error fetching transcript:', error);
                    logToServer('error', 'Error in form submission', { 
                        error: error.message,
                        stack: error.stack
                    });
                    showError(error.message || 'An error occurred while fetching the transcript');
                } finally {
                    setLoading(false);
                }
async def get_transcript_page(request: Request):
    """Serve the transcript extraction page."""
    return templates.TemplateResponse("index.html", {"request": request})

# ... rest of your code remains the same ...
    # Log request details
    logger.info("=== NEW TRANSCRIPT REQUEST ===")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Client: {request.client}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Query params: url={url}, language={language}, auto_generated={auto_generated}")
    logger.debug(f"Full request: {request}")
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
        logger.error(f"Invalid URL or video ID: {url}")
        logger.info(f"Returning error response: {error_response.dict()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response.dict()
        )
        
    logger.info(f"Processing request for video: {video_id}")
    
    try:
        # Try to get subtitles
        logger.info(f"Attempting to get subtitles for video {video_id}")
        logger.info(f"Language: {language if language != 'auto' else 'auto (will detect)'}")
        logger.info(f"Auto-generated: {auto_generated}")
        
        start_time = time.time()
        transcript, detected_lang = await youtube_service.get_subtitles(
            video_id, 
            lang=language if language != "auto" else None,
            auto_generated=auto_generated
        )
        request_duration = time.time() - start_time
        
        logger.info(f"Subtitle retrieval completed in {request_duration:.2f} seconds")
        logger.debug(f"Detected language: {detected_lang}")
        logger.debug(f"Transcript length: {len(transcript) if transcript else 0} characters")
        
        if not transcript:
            error_msg = f"No subtitles found for video {video_id}"
            logger.error(error_msg)
            error_response = ErrorResponse(
                status="error",
                error="no_subtitles",
                message=error_msg
            )
            logger.info(f"Returning error response: {error_response.dict()}")
            return JSONResponse(status_code=404, content=error_response.dict())
            
        logger.info(f"Successfully retrieved subtitles for video {video_id}")
        
        # Format the response
        logger.info("Formatting success response")
        response_data = _format_success_response(
            transcript=transcript,
            video_id=video_id,
            language=detected_lang or language,
            auto_generated=auto_generated,
            response=response
        )
        logger.info(f"Response prepared. Status: {response.status_code}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        error_msg = f"Error retrieving subtitles: {str(e)}"
        logger.exception(error_msg)
        error_response = ErrorResponse(
            status="error",
            error="internal_error",
            message="An error occurred while processing your request"
        )
        logger.error(f"Returning 500 error: {error_response.dict()}")
        return JSONResponse(status_code=500, content=error_response.dict())

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
    logger.debug(f"Transcript length before cleaning: {len(transcript) if transcript else 0} characters")
    
    # Clean up the transcript
    try:
        logger.info("Cleaning subtitles...")
        cleaned_transcript = subtitle_service.clean_subtitles(transcript)
        logger.debug(f"Transcript length after cleaning: {len(cleaned_transcript) if cleaned_transcript else 0} characters")
    except Exception as e:
        logger.error(f"Error cleaning subtitles: {str(e)}")
        # Fall back to original transcript if cleaning fails
        cleaned_transcript = transcript
        logger.warning("Using original transcript due to cleaning error")
    
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
    # Return response that matches the TranscriptResponse model
    return TranscriptResponse(
        status="success",
        video_id=video_id,
        language=language,
        auto_generated=auto_generated,
        transcript=cleaned_text
    ).dict()
