from fastapi import APIRouter, Query
from typing import List, Optional
from uuid import UUID

from app.api.v1.deps import SessionDep
from app.schema.location_schema import (
    SAUGet, DistrictGet, RegionGet, SchoolTypeGet, 
    GradeGet, TownGet, SchoolGet
)
from app.service.public.location_service import location_service

router = APIRouter()

@router.get("/sau", 
    response_model=List[SAUGet],
    summary="Get all SAUs",
    description="Retrieves a list of all School Administrative Units (SAUs), with optional filtering by district ID",
    response_description="List of SAUs")
def get_saus(
    session: SessionDep,
    district_id: Optional[int] = Query(None, description="Filter SAUs by district ID")
):
    return location_service.get_saus(session=session, district_id=district_id)

@router.get("/sau/{sau_id}", 
    response_model=SAUGet,
    summary="Get SAU by ID",
    description="Retrieves a specific School Administrative Unit by its ID",
    response_description="SAU details")
def get_sau(sau_id: int, session: SessionDep):
    return location_service.get_sau_by_id(session=session, sau_id=sau_id)

@router.get("/district", 
    response_model=List[DistrictGet],
    summary="Gets districts",
    description="Retrieves a list of all school districts, with optional filtering by public status.",
    response_description="List of districts")
def get_districts(
    session: SessionDep,
    is_public: Optional[bool] = Query(None, description="Filter districts by public status (true/false)"),
    school_id: Optional[int] = Query(None, description="Filter districts by school ID")
):
    """
    Retrieves a list of districts, optionally filtered by public status and/or school ID.
    """
    return location_service.get_districts(session=session, is_public=is_public, school_id=school_id)

@router.get("/district/{district_id}", 
    response_model=DistrictGet,
    summary="Get district by ID",
    description="Retrieves a specific school district by its ID",
    response_description="District details")
def get_district(district_id: int, session: SessionDep):
    return location_service.get_district_by_id(session=session, district_id=district_id)

@router.get("/school", 
    response_model=List[SchoolGet],
    summary="Get schools",
    description="Retrieves a list of all schools, with optional filtering by district ID",
    response_description="List of schools")
def get_schools(
    session: SessionDep,
    district_id: Optional[int] = Query(None, description="Filter schools by district ID")
):
    return location_service.get_schools(session=session, district_id=district_id)

@router.get("/school/{school_id}", 
    response_model=SchoolGet,
    summary="Get school by ID",
    description="Retrieves a specific school by its ID",
    response_description="School details")
def get_school(school_id: int, session: SessionDep):
    return location_service.get_school_by_id(session=session, school_id=school_id)

@router.get("/region", 
    response_model=List[RegionGet],
    summary="Get all regions",
    description="Retrieves a list of all regions",
    response_description="List of regions")
def get_regions(session: SessionDep):
    return location_service.get_regions(session=session)

@router.get("/region/{region_id}", 
    response_model=RegionGet,
    summary="Get region by ID",
    description="Retrieves a specific region by its ID",
    response_description="Region details")
def get_region(region_id: int, session: SessionDep):
    return location_service.get_region_by_id(session=session, region_id=region_id)

@router.get("/school-type", 
    response_model=List[SchoolTypeGet],
    summary="Get all school types",
    description="Retrieves a list of all school types",
    response_description="List of school types")
def get_school_types(session: SessionDep):
    return location_service.get_school_types(session=session)

@router.get("/school-type/{school_type_id}", 
    response_model=SchoolTypeGet,
    summary="Get school type by ID",
    description="Retrieves a specific school type by its ID",
    response_description="School type details")
def get_school_type(school_type_id: int, session: SessionDep):
    return location_service.get_school_type_by_id(session=session, school_type_id=school_type_id)

@router.get("/grade", 
    response_model=List[GradeGet],
    summary="Get all grades",
    description="Retrieves a list of all grades",
    response_description="List of grades")
def get_grades(session: SessionDep):
    return location_service.get_grades(session=session)

@router.get("/grade/{grade_id}", 
    response_model=GradeGet,
    summary="Get grade by ID",
    description="Retrieves a specific grade by its ID",
    response_description="Grade details")
def get_grade(grade_id: int, session: SessionDep):
    return location_service.get_grade_by_id(session=session, grade_id=grade_id)

@router.get("/town", 
    response_model=List[TownGet],
    summary="Get towns",
    description="Retrieves a list of all towns, with optional filtering by district ID",
    response_description="List of towns")
def get_towns(
    session: SessionDep,
    district_id: Optional[int] = Query(None, description="Filter towns by district ID")
):
    return location_service.get_towns(session=session, district_id=district_id)

@router.get("/town/{town_id}", 
    response_model=TownGet,
    summary="Get town by ID",
    description="Retrieves a specific town by its ID",
    response_description="Town details")
def get_town(town_id: int, session: SessionDep):
    return location_service.get_town_by_id(session=session, town_id=town_id) 