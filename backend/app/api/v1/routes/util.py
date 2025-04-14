from fastapi import APIRouter

router = APIRouter()

@router.get("/health-check",
    summary="Health check endpoint",
    description="Simple endpoint to verify API is running",
    response_description="Status indicating API health")
async def health_check():
    return {"status": "ok"}