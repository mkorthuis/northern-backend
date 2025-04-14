from fastapi import APIRouter, Query
from typing import List, Optional

from app.api.v1.deps import SessionDep
from app.schema.assessment_schema import AssessmentGet, AssessmentSubgroupGet, AssessmentSubjectGet
from app.service.public.assessment_service import assessment_service

router = APIRouter()

@router.get("/subgroup",
    response_model=List[AssessmentSubgroupGet],
    summary="Get all assessment subgroups",
    description="Retrieves a list of all assessment subgroups",
    response_description="List of assessment subgroups")
def get_assessment_subgroups(session: SessionDep):
    return assessment_service.get_assessment_subgroups(session=session)

@router.get("/subject",
    response_model=List[AssessmentSubjectGet],
    summary="Get all assessment subjects",
    description="Retrieves a list of all assessment subjects",
    response_description="List of assessment subjects")
def get_assessment_subjects(session: SessionDep):
    return assessment_service.get_assessment_subjects(session=session)

@router.get("/state",
    response_model=List[AssessmentGet],
    summary="Get state assessment data",
    description="Retrieves state level assessment data with optional filters",
    response_description="List of state assessment data")
def get_state_assessments(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    assessment_subgroup_id: Optional[int] = Query(default=None, description="Filter by assessment subgroup ID"),
    assessment_subject_id: Optional[int] = Query(default=None, description="Filter by assessment subject ID"),
    grade_id: Optional[int] = Query(default=None, description="Filter by grade ID.  If you pass in 999, it returnes the summed values of all grades (grade_id is NULL)")
):
    return assessment_service.get_state_assessments(
        session=session,
        year=year,
        assessment_subgroup_id=assessment_subgroup_id,
        assessment_subject_id=assessment_subject_id,
        grade_id=grade_id
    )

@router.get("/district",
    response_model=List[AssessmentGet],
    summary="Get district assessment data",
    description="Retrieves district level assessment data with optional filters",
    response_description="List of district assessment data")
def get_district_assessments(
    session: SessionDep,
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    year: Optional[int] = Query(default=None, description="Filter by year"),
    assessment_subgroup_id: Optional[int] = Query(default=None, description="Filter by assessment subgroup ID"),
    assessment_subject_id: Optional[int] = Query(default=None, description="Filter by assessment subject ID"),
    grade_id: Optional[int] = Query(default=None, description="Filter by grade ID.  If you pass in 999, it returnes the summed values of all grades (grade_id is NULL)")
):
    return assessment_service.get_district_assessments(
        session=session,
        district_id=district_id,
        year=year,
        assessment_subgroup_id=assessment_subgroup_id,
        assessment_subject_id=assessment_subject_id,
        grade_id=grade_id
    )

@router.get("/school",
    response_model=List[AssessmentGet],
    summary="Get school assessment data",
    description="Retrieves school level assessment data with optional filters",
    response_description="List of school assessment data")
def get_school_assessments(
    session: SessionDep,
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    year: Optional[int] = Query(default=None, description="Filter by year"),
    assessment_subgroup_id: Optional[int] = Query(default=None, description="Filter by assessment subgroup ID"),
    assessment_subject_id: Optional[int] = Query(default=None, description="Filter by assessment subject ID"),
    grade_id: Optional[int] = Query(default=None, description="Filter by grade ID.  If you pass in 999, it returnes the summed values of all grades (grade_id is NULL)")
):
    return assessment_service.get_school_assessments(
        session=session,
        school_id=school_id,
        district_id=district_id,
        year=year,
        assessment_subgroup_id=assessment_subgroup_id,
        assessment_subject_id=assessment_subject_id,
        grade_id=grade_id
    ) 