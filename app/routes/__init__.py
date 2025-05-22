"""
API routes package.
"""

from fastapi import APIRouter

# Create a base router for all API routes
api_router = APIRouter()

# Import all route modules here
from . import transcript, languages  # noqa
