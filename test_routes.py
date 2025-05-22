import uvicorn
import requests
from fastapi import FastAPI, APIRouter

# Create a test FastAPI app
test_app = FastAPI()

# Create a test router
test_router = APIRouter(prefix="/test-prefix")

@test_router.get("/test-endpoint")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}

# Include the router with a prefix
test_app.include_router(test_router, prefix="/api")

# Print all routes
print("\nRegistered routes:")
for route in test_app.routes:
    print(f"{route.path} - {route.name}")

# Test the endpoint
try:
    response = requests.get("http://127.0.0.1:8000/api/test-prefix/test-endpoint")
    print(f"\nResponse status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"\nError: {e}")

print("\nTo test the endpoint, run:")
print("uvicorn test_routes:test_app --reload")
print("Then open: http://127.0.0.1:8000/api/test-prefix/test-endpoint")
