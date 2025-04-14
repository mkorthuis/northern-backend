from fastapi import APIRouter, Query
from typing import List, Optional

from app.api.v1.deps import SessionDep
from app.schema.safety_schema import (
    SchoolSafetyTypeGet, SchoolSafetyGet, SchoolTruancyGet,
    DisciplineIncidentTypeGet, SchoolDisciplineIncidentGet,
    DisciplineCountTypeGet, SchoolDisciplineCountGet,
    BullyingTypeGet, SchoolBullyingGet,
    BullyingClassificationTypeGet, SchoolBullyingClassificationGet,
    BullyingImpactTypeGet, SchoolBullyingImpactGet,
    HarassmentClassificationGet, SchoolHarassmentGet,
    SchoolRestraintGet, SchoolSeclusionGet,
    StateSafetyGet, StateTruancyGet,
    StateDisciplineIncidentGet, StateDisciplineCountGet,
    StateBullyingGet, StateBullyingClassificationGet, 
    StateBullyingImpactGet, StateHarassmentGet,
    StateRestraintGet, StateSeclusionGet,
    DistrictSafetyGet, DistrictTruancyGet,
    DistrictDisciplineIncidentGet, DistrictDisciplineCountGet,
    DistrictBullyingGet, DistrictBullyingClassificationGet,
    DistrictBullyingImpactGet, DistrictHarassmentGet,
    DistrictRestraintGet, DistrictSeclusionGet,
    SchoolSafetyEnrollmentGet, DistrictSafetyEnrollmentGet, StateSafetyEnrollmentGet
)
from app.service.public.safety_service import safety_service

router = APIRouter()

@router.get("/school-safety-type",
    response_model=List[SchoolSafetyTypeGet],
    summary="Get all school safety types",
    description="Retrieves a list of all school safety types",
    response_description="List of school safety types")
def get_school_safety_types(session: SessionDep):
    return safety_service.get_safety_types(session=session)

@router.get("/discipline-incident-type",
    response_model=List[DisciplineIncidentTypeGet],
    summary="Get all discipline incident types",
    description="Retrieves a list of all discipline incident types",
    response_description="List of discipline incident types")
def get_discipline_incident_types(session: SessionDep):
    return safety_service.get_discipline_incident_types(session=session)

@router.get("/discipline-count-type",
    response_model=List[DisciplineCountTypeGet],
    summary="Get all discipline count types",
    description="Retrieves a list of all discipline count types",
    response_description="List of discipline count types")
def get_discipline_count_types(session: SessionDep):
    return safety_service.get_discipline_count_types(session=session)

@router.get("/bullying-type",
    response_model=List[BullyingTypeGet],
    summary="Get all bullying types",
    description="Retrieves a list of all bullying types",
    response_description="List of bullying types")
def get_bullying_types(session: SessionDep):
    return safety_service.get_bullying_types(session=session)

@router.get("/bullying-classification-type",
    response_model=List[BullyingClassificationTypeGet],
    summary="Get all bullying classification types",
    description="Retrieves a list of all bullying classification types",
    response_description="List of bullying classification types")
def get_bullying_classification_types(session: SessionDep):
    return safety_service.get_bullying_classification_types(session=session)

@router.get("/bullying-impact-type",
    response_model=List[BullyingImpactTypeGet],
    summary="Get all bullying impact types",
    description="Retrieves a list of all bullying impact types",
    response_description="List of bullying impact types")
def get_bullying_impact_types(session: SessionDep):
    return safety_service.get_bullying_impact_types(session=session)

@router.get("/harassment-classification",
    response_model=List[HarassmentClassificationGet],
    summary="Get all harassment classifications",
    description="Retrieves a list of all harassment classifications",
    response_description="List of harassment classifications")
def get_harassment_classifications(session: SessionDep):
    return safety_service.get_harassment_classifications(session=session)

@router.get("/school/safety",
    response_model=List[SchoolSafetyGet],
    summary="Get school safety data",
    description="Retrieves school safety data with optional filters",
    response_description="List of school safety data")
def get_school_safety(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    safety_type_id: Optional[int] = Query(default=None, description="Filter by safety type ID")
):
    return safety_service.get_school_safety(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        safety_type_id=safety_type_id
    )

@router.get("/school/truancy",
    response_model=List[SchoolTruancyGet],
    summary="Get school truancy data",
    description="Retrieves school truancy data with optional filters",
    response_description="List of school truancy data")
def get_school_truancy(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_school_truancy(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id
    )

@router.get("/school/discipline/incident",
    response_model=List[SchoolDisciplineIncidentGet],
    summary="Get school discipline incident data",
    description="Retrieves school discipline incident data with optional filters",
    response_description="List of school discipline incident data")
def get_school_discipline_incidents(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    discipline_incident_type_id: Optional[int] = Query(default=None, description="Filter by discipline incident type ID")
):
    return safety_service.get_school_discipline_incidents(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        discipline_incident_type_id=discipline_incident_type_id
    )

@router.get("/school/discipline/count",
    response_model=List[SchoolDisciplineCountGet],
    summary="Get school discipline count data",
    description="Retrieves school discipline count data with optional filters",
    response_description="List of school discipline count data")
def get_school_discipline_counts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    discipline_count_type_id: Optional[int] = Query(default=None, description="Filter by discipline count type ID")
):
    return safety_service.get_school_discipline_counts(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        discipline_count_type_id=discipline_count_type_id
    )

@router.get("/school/bullying",
    response_model=List[SchoolBullyingGet],
    summary="Get school bullying data",
    description="Retrieves school bullying data with optional filters",
    response_description="List of school bullying data")
def get_school_bullying(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_type_id: Optional[int] = Query(default=None, description="Filter by bullying type ID")
):
    return safety_service.get_school_bullying(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        bullying_type_id=bullying_type_id
    )

@router.get("/school/bullying/classification",
    response_model=List[SchoolBullyingClassificationGet],
    summary="Get school bullying classification data",
    description="Retrieves school bullying classification data with optional filters",
    response_description="List of school bullying classification data")
def get_school_bullying_classifications(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_classification_type_id: Optional[int] = Query(default=None, description="Filter by bullying classification type ID")
):
    return safety_service.get_school_bullying_classifications(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        bullying_classification_type_id=bullying_classification_type_id
    )

@router.get("/school/bullying/impact",
    response_model=List[SchoolBullyingImpactGet],
    summary="Get school bullying impact data",
    description="Retrieves school bullying impact data with optional filters",
    response_description="List of school bullying impact data")
def get_school_bullying_impacts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_impact_type_id: Optional[int] = Query(default=None, description="Filter by bullying impact type ID")
):
    return safety_service.get_school_bullying_impacts(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        bullying_impact_type_id=bullying_impact_type_id
    )

@router.get("/school/harassment",
    response_model=List[SchoolHarassmentGet],
    summary="Get school harassment data",
    description="Retrieves school harassment data with optional filters",
    response_description="List of school harassment data")
def get_school_harassment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    harassment_classification_id: Optional[int] = Query(default=None, description="Filter by harassment classification ID")
):
    return safety_service.get_school_harassment(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id,
        harassment_classification_id=harassment_classification_id
    )

@router.get("/school/restraint",
    response_model=List[SchoolRestraintGet],
    summary="Get school restraint data",
    description="Retrieves school restraint data with optional filters",
    response_description="List of school restraint data")
def get_school_restraint(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_school_restraint(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id
    )

@router.get("/school/seclusion",
    response_model=List[SchoolSeclusionGet],
    summary="Get school seclusion data",
    description="Retrieves school seclusion data with optional filters",
    response_description="List of school seclusion data")
def get_school_seclusion(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_school_seclusion(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id
    )

@router.get("/school/enrollment",
    response_model=List[SchoolSafetyEnrollmentGet],
    summary="Get school safety enrollment data",
    description="Retrieves school-level safety enrollment data with optional filters",
    response_description="List of school safety enrollment data")
def get_school_safety_enrollment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    school_id: Optional[int] = Query(default=None, description="Filter by school ID"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_school_safety_enrollment(
        session=session,
        year=year,
        school_id=school_id,
        district_id=district_id
    )

@router.get("/state/safety",
    response_model=List[StateSafetyGet],
    summary="Get state safety data",
    description="Retrieves state-level safety data with optional filters",
    response_description="List of state safety data")
def get_state_safety(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    safety_type_id: Optional[int] = Query(default=None, description="Filter by safety type ID")
):
    return safety_service.get_state_safety(
        session=session,
        year=year,
        safety_type_id=safety_type_id
    )

@router.get("/state/truancy",
    response_model=List[StateTruancyGet],
    summary="Get state truancy data",
    description="Retrieves state-level truancy data with optional filters",
    response_description="List of state truancy data")
def get_state_truancy(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year")
):
    return safety_service.get_state_truancy(
        session=session,
        year=year
    )

@router.get("/state/discipline/incident",
    response_model=List[StateDisciplineIncidentGet],
    summary="Get state discipline incident data",
    description="Retrieves state-level discipline incident data with optional filters",
    response_description="List of state discipline incident data")
def get_state_discipline_incidents(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    discipline_incident_type_id: Optional[int] = Query(default=None, description="Filter by discipline incident type ID")
):
    return safety_service.get_state_discipline_incidents(
        session=session,
        year=year,
        discipline_incident_type_id=discipline_incident_type_id
    )

@router.get("/state/discipline/count",
    response_model=List[StateDisciplineCountGet],
    summary="Get state discipline count data",
    description="Retrieves state-level discipline count data with optional filters",
    response_description="List of state discipline count data")
def get_state_discipline_counts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    discipline_count_type_id: Optional[int] = Query(default=None, description="Filter by discipline count type ID")
):
    return safety_service.get_state_discipline_counts(
        session=session,
        year=year,
        discipline_count_type_id=discipline_count_type_id
    )

@router.get("/state/bullying",
    response_model=List[StateBullyingGet],
    summary="Get state bullying data",
    description="Retrieves state-level bullying data with optional filters",
    response_description="List of state bullying data")
def get_state_bullying(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    bullying_type_id: Optional[int] = Query(default=None, description="Filter by bullying type ID")
):
    return safety_service.get_state_bullying(
        session=session,
        year=year,
        bullying_type_id=bullying_type_id
    )

@router.get("/state/bullying/classification",
    response_model=List[StateBullyingClassificationGet],
    summary="Get state bullying classification data",
    description="Retrieves state-level bullying classification data with optional filters",
    response_description="List of state bullying classification data")
def get_state_bullying_classifications(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    bullying_classification_type_id: Optional[int] = Query(default=None, description="Filter by bullying classification type ID")
):
    return safety_service.get_state_bullying_classifications(
        session=session,
        year=year,
        bullying_classification_type_id=bullying_classification_type_id
    )

@router.get("/state/bullying/impact",
    response_model=List[StateBullyingImpactGet],
    summary="Get state bullying impact data",
    description="Retrieves state-level bullying impact data with optional filters",
    response_description="List of state bullying impact data")
def get_state_bullying_impacts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    bullying_impact_type_id: Optional[int] = Query(default=None, description="Filter by bullying impact type ID")
):
    return safety_service.get_state_bullying_impacts(
        session=session,
        year=year,
        bullying_impact_type_id=bullying_impact_type_id
    )

@router.get("/state/harassment",
    response_model=List[StateHarassmentGet],
    summary="Get state harassment data",
    description="Retrieves state-level harassment data with optional filters",
    response_description="List of state harassment data")
def get_state_harassment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    harassment_classification_id: Optional[int] = Query(default=None, description="Filter by harassment classification ID")
):
    return safety_service.get_state_harassment(
        session=session,
        year=year,
        harassment_classification_id=harassment_classification_id
    )

@router.get("/state/restraint",
    response_model=List[StateRestraintGet],
    summary="Get state restraint data",
    description="Retrieves state-level restraint data with optional filters",
    response_description="List of state restraint data")
def get_state_restraint(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year")
):
    return safety_service.get_state_restraint(
        session=session,
        year=year
    )

@router.get("/state/seclusion",
    response_model=List[StateSeclusionGet],
    summary="Get state seclusion data",
    description="Retrieves state-level seclusion data with optional filters",
    response_description="List of state seclusion data")
def get_state_seclusion(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year")
):
    return safety_service.get_state_seclusion(
        session=session,
        year=year
    )

@router.get("/state/enrollment",
    response_model=List[StateSafetyEnrollmentGet],
    summary="Get state enrollment data ONLY for schools we have safety data for ",
    description="Retrieves state-level safety enrollment data with optional filter",
    response_description="List of state safety enrollment data")
def get_state_safety_enrollment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year")
):
    return safety_service.get_state_safety_enrollment(
        session=session,
        year=year
    ) 

@router.get("/district/safety",
    response_model=List[DistrictSafetyGet],
    summary="Get district safety data",
    description="Retrieves district-level safety data with optional filters",
    response_description="List of district safety data")
def get_district_safety(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    safety_type_id: Optional[int] = Query(default=None, description="Filter by safety type ID")
):
    return safety_service.get_district_safety(
        session=session,
        year=year,
        district_id=district_id,
        safety_type_id=safety_type_id
    )

@router.get("/district/truancy",
    response_model=List[DistrictTruancyGet],
    summary="Get district truancy data",
    description="Retrieves district-level truancy data with optional filters",
    response_description="List of district truancy data")
def get_district_truancy(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_district_truancy(
        session=session,
        year=year,
        district_id=district_id
    )

@router.get("/district/discipline/incident",
    response_model=List[DistrictDisciplineIncidentGet],
    summary="Get district discipline incident data",
    description="Retrieves district-level discipline incident data with optional filters",
    response_description="List of district discipline incident data")
def get_district_discipline_incidents(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    discipline_incident_type_id: Optional[int] = Query(default=None, description="Filter by discipline incident type ID")
):
    return safety_service.get_district_discipline_incidents(
        session=session,
        year=year,
        district_id=district_id,
        discipline_incident_type_id=discipline_incident_type_id
    )

@router.get("/district/discipline/count",
    response_model=List[DistrictDisciplineCountGet],
    summary="Get district discipline count data",
    description="Retrieves district-level discipline count data with optional filters",
    response_description="List of district discipline count data")
def get_district_discipline_counts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    discipline_count_type_id: Optional[int] = Query(default=None, description="Filter by discipline count type ID")
):
    return safety_service.get_district_discipline_counts(
        session=session,
        year=year,
        district_id=district_id,
        discipline_count_type_id=discipline_count_type_id
    )

@router.get("/district/bullying",
    response_model=List[DistrictBullyingGet],
    summary="Get district bullying data",
    description="Retrieves district-level bullying data with optional filters",
    response_description="List of district bullying data")
def get_district_bullying(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_type_id: Optional[int] = Query(default=None, description="Filter by bullying type ID")
):
    return safety_service.get_district_bullying(
        session=session,
        year=year,
        district_id=district_id,
        bullying_type_id=bullying_type_id
    )

@router.get("/district/bullying/classification",
    response_model=List[DistrictBullyingClassificationGet],
    summary="Get district bullying classification data",
    description="Retrieves district-level bullying classification data with optional filters",
    response_description="List of district bullying classification data")
def get_district_bullying_classifications(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_classification_type_id: Optional[int] = Query(default=None, description="Filter by bullying classification type ID")
):
    return safety_service.get_district_bullying_classifications(
        session=session,
        year=year,
        district_id=district_id,
        bullying_classification_type_id=bullying_classification_type_id
    )

@router.get("/district/bullying/impact",
    response_model=List[DistrictBullyingImpactGet],
    summary="Get district bullying impact data",
    description="Retrieves district-level bullying impact data with optional filters",
    response_description="List of district bullying impact data")
def get_district_bullying_impacts(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    bullying_impact_type_id: Optional[int] = Query(default=None, description="Filter by bullying impact type ID")
):
    return safety_service.get_district_bullying_impacts(
        session=session,
        year=year,
        district_id=district_id,
        bullying_impact_type_id=bullying_impact_type_id
    )

@router.get("/district/harassment",
    response_model=List[DistrictHarassmentGet],
    summary="Get district harassment data",
    description="Retrieves district-level harassment data with optional filters",
    response_description="List of district harassment data")
def get_district_harassment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    harassment_classification_id: Optional[int] = Query(default=None, description="Filter by harassment classification ID")
):
    return safety_service.get_district_harassment(
        session=session,
        year=year,
        district_id=district_id,
        harassment_classification_id=harassment_classification_id
    )

@router.get("/district/restraint",
    response_model=List[DistrictRestraintGet],
    summary="Get district restraint data",
    description="Retrieves district-level restraint data with optional filters",
    response_description="List of district restraint data")
def get_district_restraint(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_district_restraint(
        session=session,
        year=year,
        district_id=district_id
    )

@router.get("/district/seclusion",
    response_model=List[DistrictSeclusionGet],
    summary="Get district seclusion data",
    description="Retrieves district-level seclusion data with optional filters",
    response_description="List of district seclusion data")
def get_district_seclusion(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_district_seclusion(
        session=session,
        year=year,
        district_id=district_id
    )

@router.get("/district/enrollment",
    response_model=List[DistrictSafetyEnrollmentGet],
    summary="Get district safety enrollment data ONLY for schools we have safety data for",
    description="Retrieves district-level safety enrollment data with optional filters",
    response_description="List of district safety enrollment data")
def get_district_safety_enrollment(
    session: SessionDep,
    year: Optional[int] = Query(default=None, description="Filter by year"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID")
):
    return safety_service.get_district_safety_enrollment(
        session=session,
        year=year,
        district_id=district_id
    )