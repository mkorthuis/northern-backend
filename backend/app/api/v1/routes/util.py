from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.service.internal.jelly_donut_service import JellyDonutService

router = APIRouter()

@router.get("/health-check",
    summary="Health check endpoint",
    description="Simple endpoint to verify API is running",
    response_description="Status indicating API health")
async def health_check():
    return {"status": "ok"}

@router.get("/jelly-donut",
    summary="Jelly donut endpoint",
    description="Endpoint that returns a response from LLM using the provided message or default to 'I am a jelly donut'",
    response_description="LLM response to the provided prompt")
async def jelly_donut(message: Optional[str] = Query(None, description="Custom message to send to the LLM")):
    try:
        response = await JellyDonutService.get_jelly_donut_response(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing jelly donut request: {str(e)}")