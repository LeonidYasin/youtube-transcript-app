from fastapi import APIRouter

# Create a router for test endpoints
router = APIRouter(prefix="", tags=["test"])

@router.get("/test-endpoint")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}
