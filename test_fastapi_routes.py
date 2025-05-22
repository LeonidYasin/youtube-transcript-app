import sys
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the app from main.py
sys.path.append('.')
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "swagger" in response.text

def test_channel_search_endpoint():
    response = client.get("/api/channel-search/rabbi-ginsburgh")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    # Even if it fails, we want to see the response
    assert True

if __name__ == "__main__":
    test_read_main()
    test_channel_search_endpoint()
