"""
Pydantic models for transcript API responses and requests.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LogData(BaseModel):
    """Log data model for API requests."""
    level: str
    message: str
    timestamp: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""
    status: str = "error"
    error: str
    message: str


class TranscriptResponse(BaseModel):
    """Successful transcript response model."""
    status: str = "success"
    video_id: str
    language: str
    auto_generated: bool
    transcript: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TranscriptRequest(BaseModel):
    """Transcript request model for API validation."""
    url: str
    language: str = "auto"
    auto_generated: bool = False
