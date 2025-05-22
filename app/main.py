"""
Main FastAPI application module.
"""

import os
import sys
import io
import logging
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
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
from .routes.transcript import router as transcript_router
from .routes.languages import router as languages_router
from .routes.channel import router as channel_router
from .routes.channel_search import router as channel_search_router
from .routes.test import router as test_router

# Set up logging
setup_logging(settings.LOG_FILE)
logger = logging.getLogger(__name__)
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
# Each router is included with its specific prefix
app.include_router(transcript_router, prefix="/api", tags=["transcript"])
app.include_router(languages_router, prefix="/api/languages", tags=["languages"])
app.include_router(channel_router, prefix="/api/channel", tags=["channel"])
app.include_router(channel_search_router, prefix="/api/channel-search", tags=["channel-search"])
app.include_router(test_router, prefix="/api/test", tags=["test"])

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
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
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
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
