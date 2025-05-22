from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.testclient import TestClient
import uvicorn

# Create a new FastAPI app
app = FastAPI()

# Create a test router
test_router = APIRouter()

@test_router.get("/test-endpoint")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}

# Include the router with a prefix
app.include_router(test_router, prefix="/api/test")

# Add a direct endpoint
@app.get("/api/direct-endpoint")
async def direct_endpoint():
    return {"message": "Direct endpoint is working!"}

# Print all routes
print("\nRegistered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

# Create a test client
client = TestClient(app)

# Test the endpoints
print("\nTesting endpoints:")
try:
    # Test the test endpoint
    print("\nTesting /api/test/test-endpoint:")
    response = client.get("/api/test/test-endpoint")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test the direct endpoint
    print("\nTesting /api/direct-endpoint:")
    response = client.get("/api/direct-endpoint")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")

# Run the app directly for testing
if __name__ == "__main__":
    print("\nStarting server...")
    uvicorn.run("direct_test:app", host="0.0.0.0", port=8000, reload=True)
