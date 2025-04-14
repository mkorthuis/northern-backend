from fastapi import APIRouter, Query
from typing import List, Optional
from uuid import UUID

from app.api.v1.deps import SessionDep
from app.schema.measurement_schema import (
    MeasurementGet, MeasurementTypeGet, MeasurementTypeCategoryGet
)
from app.service.public.measurement_service import measurement_service

router = APIRouter()

@router.get("/category", 
    response_model=List[MeasurementTypeCategoryGet],
    summary="Get all measurement categories",
    description="Retrieves a list of all measurement type categories",
    response_description="List of measurement categories")
def get_measurement_categories(session: SessionDep):
    return measurement_service.get_measurement_type_categories(session=session)

@router.get("/category/{category_id}", 
    response_model=MeasurementTypeCategoryGet,
    summary="Get measurement category by ID",
    description="Retrieves a specific measurement type category by its ID",
    response_description="Measurement category details")
def get_measurement_category(category_id: int, session: SessionDep):
    return measurement_service.get_measurement_type_category_by_id(session=session, category_id=category_id)

@router.get("/type", 
    response_model=List[MeasurementTypeGet],
    summary="Get measurement types",
    description="Retrieves a list of measurement types, optionally filtered by category",
    response_description="List of measurement types")
def get_measurement_types(
    session: SessionDep,
    category_id: Optional[int] = Query(None, description="Filter by category ID")
):
    return measurement_service.get_measurement_types(session=session, category_id=category_id)

@router.get("/type/{type_id}", 
    response_model=MeasurementTypeGet,
    summary="Get measurement type by ID",
    description="Retrieves a specific measurement type by its ID",
    response_description="Measurement type details")
def get_measurement_type(type_id: int, session: SessionDep):
    return measurement_service.get_measurement_type_by_id(session=session, type_id=type_id)

@router.get("", 
    response_model=List[MeasurementGet],
    summary="Get measurements",
    description="Retrieves a list of measurements with optional filtering by district, school, type, and year",
    response_description="List of measurements")
def get_measurements(
    session: SessionDep,
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    measurement_type_id: Optional[int] = Query(default=None, description="Filter by measurement type ID"),
    year: Optional[int] = Query(default=None, description="Filter by year")
):
    return measurement_service.get_measurements(
        session=session,
        district_id=district_id,
        school_id=school_id,
        measurement_type_id=measurement_type_id,
        year=year
    )

@router.get("/latest", 
    response_model=List[MeasurementGet],
    summary="Get latest measurements",
    description="Retrieves the most recent year of measurements for a district or school",
    response_description="List of latest measurements")
def get_latest_measurements(
    session: SessionDep,
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID")
):
    return measurement_service.get_latest_measurements(
        session=session,
        district_id=district_id,
        school_id=school_id
    )

@router.get("/{measurement_id}", 
    response_model=MeasurementGet,
    summary="Get measurement by ID",
    description="Retrieves a specific measurement by its ID",
    response_description="Measurement details")
def get_measurement(measurement_id: int, session: SessionDep):
    return measurement_service.get_measurement_by_id(session=session, measurement_id=measurement_id) 