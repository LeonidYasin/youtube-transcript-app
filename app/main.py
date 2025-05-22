"""
Main FastAPI application module.
"""

import os
import sys
import io
import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import List, Any, Dict, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')
    # Also set the console output code page to UTF-8
    os.system('chcp 65001 > nul')
    os.environ["PYTHONIOENCODING"] = "utf-8"

from .config import settings
from .utils.helpers import setup_logging
# Import routers
from .routes.transcript import json_api_router, web_router as transcript_web_router
from .routes.languages import router as languages_router
from .routes.channel import router as channel_router
from .routes.channel_search import router as channel_search_router
from .routes.test import router as test_router

# Set up logging
setup_logging("youtube_transcript.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting YouTube Transcript API...")

# Create FastAPI app
app = FastAPI(
    title="YouTube Transcript API",
    description="API for extracting and processing YouTube video transcripts",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with proper prefixes
# Note: The JSON API router already has /api prefix defined
app.include_router(json_api_router, tags=["transcript"])  # JSON API routes
app.include_router(transcript_web_router)  # Web interface routes
app.include_router(languages_router, prefix="/languages", tags=["languages"])
app.include_router(channel_router, prefix="/channel", tags=["channel"])
app.include_router(channel_search_router, prefix="/channel-search", tags=["channel-search"])
app.include_router(test_router, prefix="/test", tags=["test"])

# Mount static files (if any)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve the test web interface
@app.get("/test", response_class=HTMLResponse)
async def test_web_interface():
    test_html_path = os.path.join(os.path.dirname(__file__), "..", "test_web.html")
    with open(test_html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Add startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting YouTube Transcript API...")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down YouTube Transcript API...")

# Add middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    start_time = time.time()
    
    # Get request info
    client_host = request.client.host if request.client else "unknown"
    request_info = {
        "method": request.method,
        "path": request.url.path,
        "client": client_host,
        "headers": dict(request.headers)
    }
    
    # Log request
    logger.info(f"Request received: {request_info}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Get response info
        response_info = {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", "unknown"),
            "headers": dict(response.headers)
        }
        
        # Log response
        logger.info(f"Response sent: {response_info}")
        
        # Add processing time to response headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Handle content type
        if request.url.path.startswith('/api/') and request.headers.get('accept') == 'application/json':
            logger.info(f"Checking response type for API endpoint: {request.url.path}")
            logger.info(f"Response content type: {response.headers.get('content-type')}")
            
            if isinstance(response, HTMLResponse):
                logger.warning(f"HTML response detected for API endpoint: {request.url.path}")
                logger.warning(f"Response headers: {dict(response.headers)}")
                
                # Try to get the response body
                try:
                    body = await response.body()
                    logger.warning(f"Response body: {body[:500]}...")
                except Exception as e:
                    logger.warning(f"Could not read response body: {str(e)}")
                
                return Response(content='{"error": "html_response", "message": "API endpoint expected JSON response"}',
                               media_type="application/json",
                               status_code=400)
        
        return response
    except Exception as e:
        # Log exception
        logger.exception(f"Request failed: {request_info}")
        raise

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Root endpoint redirects to the API docs
@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/api/docs")

# This allows running with uvicorn directly: `uvicorn app.main:app`
if __name__ == "__main__":
    import uvicorn
    
    # Set up logging
    setup_logging()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
