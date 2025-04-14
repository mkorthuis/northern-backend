from fastapi import APIRouter

from app.api.v1.routes import util, location, measurement, enrollment, finance, assessment, education_freedom_account, safety

api_router = APIRouter()
api_router.include_router(assessment.router, prefix="/assessment", tags=["Assessment"])
api_router.include_router(education_freedom_account.router, prefix="/education-freedom-account", tags=["Education Freedom Account"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["Enrollment"])
api_router.include_router(finance.router, prefix="/finance", tags=["Finance"])
api_router.include_router(location.router, prefix="/location", tags=["Location"])
api_router.include_router(measurement.router, prefix="/measurement", tags=["Measurement"])
api_router.include_router(safety.router, prefix="/safety", tags=["Safety"])
api_router.include_router(util.router, prefix="/util", tags=["Utilities"])