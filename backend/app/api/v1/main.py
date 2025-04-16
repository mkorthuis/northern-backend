from fastapi import APIRouter

from app.api.v1.routes import util, survey, survey_analysis

api_router = APIRouter()
api_router.include_router(survey.router, prefix="/survey", tags=["Survey"])
api_router.include_router(survey_analysis.router, prefix="/survey-analysis", tags=["Survey Analysis"])
api_router.include_router(util.router, prefix="/util", tags=["Utilities"])