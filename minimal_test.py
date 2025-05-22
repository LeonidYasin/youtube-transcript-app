from fastapi import FastAPI, APIRouter
import uvicorn

# Create FastAPI app
app = FastAPI()

# Create a router with a prefix
router = APIRouter(prefix="/test")

@router.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

# Include the router with a prefix
app.include_router(router, prefix="/api")

# Print all routes
print("\nRegistered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

if __name__ == "__main__":
    uvicorn.run("minimal_test:app", host="0.0.0.0", port=8000, reload=True)
