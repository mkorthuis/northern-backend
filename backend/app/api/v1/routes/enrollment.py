from fastapi import APIRouter, Query
from typing import List, Optional

from app.api.v1.deps import SessionDep
from app.schema.enrollment_schema import SchoolEnrollmentGet, StateEnrollmentGet
from app.service.public.enrollment_service import enrollment_service

router = APIRouter()

@router.get("/school/{school_id}", 
    response_model=List[SchoolEnrollmentGet],
    summary="Get school enrollments",
    description="Retrieves enrollment data for a specific school, with optional filtering by year",
    response_description="List of school enrollments")
def get_school_enrollments(
    school_id: int, 
    session: SessionDep,
    year: Optional[int] = Query(None, description="Filter enrollments by year")
):
    """
    Get enrollment data for a specific school, optionally filtered by year.
    
    Parameters:
    - **school_id**: The ID of the school to get enrollments for
    - **year**: Optional year to filter enrollments by
    
    Returns a list of enrollment records with grade information.
    """
    return enrollment_service.get_school_enrollments(
        session=session, 
        school_id=school_id, 
        year=year
    )

@router.get("/school/{school_id}/latest", 
    response_model=List[SchoolEnrollmentGet],
    summary="Get latest school enrollments",
    description="Retrieves the most recent enrollment data available for a specific school",
    response_description="List of latest school enrollments")
def get_latest_school_enrollments(
    school_id: int, 
    session: SessionDep
):
    """
    Get the most recent enrollment data available for a specific school.
    
    This endpoint automatically finds the latest year for which enrollment data
    is available and returns all enrollment records for that year.
    
    Parameters:
    - **school_id**: The ID of the school to get enrollments for
    
    Returns a list of the most recent enrollment records with grade information.
    """
    return enrollment_service.get_latest_school_enrollments(
        session=session, 
        school_id=school_id
    )

@router.get("/state", 
    response_model=List[StateEnrollmentGet],
    summary="Get state-level enrollments",
    description="Retrieves state-level enrollment data, with optional filtering by year",
    response_description="List of state enrollment records")
def get_state_enrollments(
    session: SessionDep,
    year: Optional[int] = Query(None, description="Filter enrollments by year")
):
    """
    Get state-level enrollment data, optionally filtered by year.
    
    Parameters:
    - **year**: Optional year to filter enrollments by
    
    Returns a list of state enrollment records with elementary, middle, high, and total enrollment figures.
    """
    return enrollment_service.get_state_enrollments(
        session=session, 
        year=year
    )
