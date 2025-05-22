import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_channels():
    """Test searching for channels"""
    response = client.get("/api/channel/search", params={"query": "рав гинзбург"})
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "status" in data
    assert data["status"] == "success"
    assert "results" in data
    assert "count" in data
    
    # If there are results, check their structure
    if data["results"]:
        channel = data["results"][0]
        assert "channel_id" in channel
        assert "title" in channel
        assert "subscribers" in channel
        assert "video_count" in channel

def test_search_channels_with_limit():
    """Test searching with a limit on the number of results"""
    limit = 3
    response = client.get(
        "/api/channel/search", 
        params={"query": "рав гинзбург", "max_results": limit}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= limit

def test_search_channels_empty_query():
    """Test searching with an empty query"""
    response = client.get("/api/channel/search", params={"query": ""})
    assert response.status_code == 400  # Expecting a validation error

def test_get_channel_videos():
    """Test getting videos from a channel"""
    # First, get a channel ID from the search
    search_response = client.get("/api/channel/search", params={"query": "рав гинзбург"})
    if search_response.status_code == 200 and search_response.json()["results"]:
        channel_id = search_response.json()["results"][0]["channel_id"]
        
        # Now get videos for this channel
        response = client.get(f"/api/channel/{channel_id}/videos")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert data["status"] == "success"
        assert "videos" in data
        assert "count" in data
        
        # If there are videos, check their structure
        if data["videos"]:
            video = data["videos"][0]
            assert "video_id" in video
            assert "title" in video
            assert "duration" in video
            assert "view_count" in video

if __name__ == "__main__":
    # Run tests with detailed output
    import sys
    import pytest
    sys.exit(pytest.main(["-v", "-s", __file__]))
