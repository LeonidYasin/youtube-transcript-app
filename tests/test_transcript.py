"""
Tests for the YouTube Transcript API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.youtube import YouTubeService
from app.utils.helpers import extract_video_id, vtt_to_text

client = TestClient(app)


def test_extract_video_id():
    """Test video ID extraction from various YouTube URLs."""
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share", "dQw4w9WgXcQ"),
        ("https://www.example.com", None),
        ("", None),
    ]
    
    for url, expected in test_cases:
        assert extract_video_id(url) == expected


def test_vtt_to_text():
    """Test VTT to text conversion."""
    vtt_content = """
WEBVTT
Kind: captions
Language: en

00:00:01.000 --> 00:00:04.000
This is a test subtitle.

00:00:05.000 --> 00:00:08.000
This is another line.
    """
    
    expected = "This is a test subtitle. This is another line."
    assert vtt_to_text(vtt_content).strip() == expected


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.skip(reason="Requires internet connection")
def test_get_transcript():
    """Test getting a transcript (requires internet connection)."""
    # Test with a known video that has captions
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    # Test with default language (should be 'ru' from settings)
    response = client.get(f"/api/transcript?url={video_url}")
    assert response.status_code in [200, 404]  # 200 if Russian subtitles exist, 404 if not
    
    # Test with explicit English language
    response = client.get(f"/api/transcript?url={video_url}&language=en")
    assert response.status_code == 200
    assert len(response.text) > 0


def test_get_available_languages():
    """Test getting available languages."""
    response = client.get("/api/available-languages")
    assert response.status_code == 200
    languages = response.json()
    assert isinstance(languages, list)
    assert len(languages) > 0
    assert all(["code" in lang and "name" in lang for lang in languages])


class TestYouTubeService:
    """Tests for the YouTubeService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = YouTubeService()
    
    def test_get_video_id(self):
        """Test video ID extraction."""
        assert self.service.get_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    @pytest.mark.skip(reason="Requires internet connection")
    def test_get_subtitles(self):
        """Test getting subtitles (requires internet connection)."""
        # Test with a known video that has captions
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        # Test with English language
        text, error = self.service.get_subtitles(video_id, "en")
        assert error is None
        assert isinstance(text, str)
        assert len(text) > 0
        
        # Test with non-existent language (should fall back to English)
        text, error = self.service.get_subtitles(video_id, "xx")
        assert error is not None or (isinstance(text, str) and len(text) > 0)
