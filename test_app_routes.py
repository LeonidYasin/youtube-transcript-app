import sys
import os
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the FastAPI app
from app.main import app

# Create a test client
client = TestClient(app)

# Test the root endpoint
print("Testing root endpoint:")
response = client.get("/")
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

# Test the test endpoint
print("\nTesting test endpoint:")
response = client.get("/api/test-endpoint")
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

# List all registered routes
print("\nAll registered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

# Test the channel search endpoint
print("\nTesting channel search endpoint:")
response = client.get("/api/channel-search/UCKadAPtEb8TTfPrQY3qwKpQ/videos?max_results=3")
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")
