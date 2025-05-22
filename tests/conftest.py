"""
Pytest configuration and fixtures.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.config import settings


@pytest.fixture(scope="session")
def test_client() -> Generator:
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def vtt_sample() -> str:
    """
    Sample VTT content for testing.
    """
    return """
WEBVTT
Kind: captions
Language: en

00:00:01.000 --> 00:00:04.000
This is a test subtitle.

00:00:05.000 --> 00:00:08.000
This is another line.
    """


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment.
    """
    # Create test directory if it doesn't exist
    test_dir = Path("tests/test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Set up test environment variables
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FILE"] = str(test_dir / "test.log")
    
    yield
    
    # Clean up after tests if needed
    # (e.g., remove test files, reset environment variables)
