"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class TranscriptResponse(BaseModel):
    """Response model for transcript endpoint."""
    text: str = Field(..., description="The transcript text")
    language: str = Field(..., description="Language code of the transcript")
    video_id: str = Field(..., description="YouTube video ID")


class ErrorResponse(BaseModel):
    """Generic error response model."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


class LanguageInfo(BaseModel):
    """Language information model."""
    code: str = Field(..., description="Language code (e.g., 'ru', 'en')")
    name: str = Field(..., description="Language name in English")
