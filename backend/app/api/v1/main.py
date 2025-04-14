from fastapi import APIRouter

from app.api.v1.routes import util, survey

api_router = APIRouter()
api_router.include_router(survey.router, prefix="/survey", tags=["Survey"])
api_router.include_router(util.router, prefix="/util", tags=["Utilities"])