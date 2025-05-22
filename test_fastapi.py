import uvicorn
from fastapi import FastAPI, Response
import json

# Create a minimal FastAPI app for testing
app = FastAPI()

@app.get("/test-route")
async def test_route():
    return {"message": "Test route is working!"}

@app.get("/test-params/{test_id}")
async def test_params(test_id: str):
    return {"test_id": test_id, "message": f"Received test_id: {test_id}"}

if __name__ == "__main__":
    # Print all registered routes for debugging
    print("\nRegistered routes:")
    for route in app.routes:
        print(f"- {route.path} ({', '.join(route.methods)})")
    
    # Run the test server
    uvicorn.run("test_fastapi:app", host="0.0.0.0", port=8001, reload=False)
