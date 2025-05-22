import sys
import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

# Import the app from main.py
sys.path.append('.')
from app.main import app
from app.services.youtube_search import YouTubeSearcher

# Test the YouTubeSearcher directly
def test_get_channel_videos():
    print("Testing direct YouTubeSearcher.get_channel_videos...")
    channel_id = "UCKadAPtEb8TTfPrQY3qwKpQ"  # Rabbi Ginsburgh's channel
    result = YouTubeSearcher.get_channel_videos(channel_id, max_results=5)
    
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"Found {len(result.get('videos', []))} videos:")
        for idx, video in enumerate(result.get('videos', [])[:3], 1):
            print(f"{idx}. {video.get('title')} - {video.get('published_time')}")
    else:
        print(f"Error: {result.get('message')}")

# Test the FastAPI endpoint
def test_endpoint():
    print("\nTesting FastAPI endpoint...")
    client = TestClient(app)
    
    # First, check if the endpoint is registered
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"{route.path} - {route.name}")
    
    # Test the channel videos endpoint
    channel_id = "UCKadAPtEb8TTfPrQY3qwKpQ"
    response = client.get(f"/api/channel-search/{channel_id}/videos")
    
    print(f"\nResponse status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result.get('videos', []))} videos")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_get_channel_videos()
    test_endpoint()
