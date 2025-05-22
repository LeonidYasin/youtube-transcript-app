from fastapi import FastAPI, APIRouter
import uvicorn

# Create a new FastAPI app
app = FastAPI()

# Create a test router
test_router = APIRouter()

@test_router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}

# Include the router with a prefix
app.include_router(test_router, prefix="/api")

# Print all routes
print("\nRegistered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

if __name__ == "__main__":
    print("\nStarting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
