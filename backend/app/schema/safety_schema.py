from pydantic import BaseModel, Field
from typing import Optional, List


class SchoolSafetyTypeGet(BaseModel):
    id: int
    name: str


class DisciplineIncidentTypeGet(BaseModel):
    id: int
    name: str


class DisciplineCountTypeGet(BaseModel):
    id: int
    name: str


class BullyingTypeGet(BaseModel):
    id: int
    name: str


class BullyingClassificationTypeGet(BaseModel):
    id: int
    name: str


class BullyingImpactTypeGet(BaseModel):
    id: int
    name: str


class HarassmentClassificationGet(BaseModel):
    id: int
    name: str


class SchoolSafetyGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None
    safety_type: Optional[SchoolSafetyTypeGet] = None


class SchoolTruancyGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None


class SchoolDisciplineIncidentGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None
    incident_type: Optional[DisciplineIncidentTypeGet] = None


class SchoolDisciplineCountGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None
    count_type: Optional[DisciplineCountTypeGet] = None


class SchoolBullyingGet(BaseModel):
    id: int
    school_id: int
    year: int
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    bullying_type: Optional[BullyingTypeGet] = None


class SchoolBullyingClassificationGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None
    classification_type: Optional[BullyingClassificationTypeGet] = None


class SchoolBullyingImpactGet(BaseModel):
    id: int
    school_id: int
    year: int
    count: Optional[int] = None
    impact_type: Optional[BullyingImpactTypeGet] = None


class SchoolHarassmentGet(BaseModel):
    id: int
    school_id: int
    year: int
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    classification: Optional[HarassmentClassificationGet] = None


class SchoolRestraintGet(BaseModel):
    id: int
    school_id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None


class SchoolSeclusionGet(BaseModel):
    id: int
    school_id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None


class StateSafetyGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None
    safety_type: Optional[SchoolSafetyTypeGet] = None


class StateTruancyGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None


class StateDisciplineIncidentGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None
    incident_type: Optional[DisciplineIncidentTypeGet] = None


class StateDisciplineCountGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None
    count_type: Optional[DisciplineCountTypeGet] = None


class StateBullyingGet(BaseModel):
    id: int
    year: int
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    bullying_type: Optional[BullyingTypeGet] = None


class StateBullyingClassificationGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None
    classification_type: Optional[BullyingClassificationTypeGet] = None


class StateBullyingImpactGet(BaseModel):
    id: int
    year: int
    count: Optional[int] = None
    impact_type: Optional[BullyingImpactTypeGet] = None


class StateHarassmentGet(BaseModel):
    id: int
    year: int
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    classification: Optional[HarassmentClassificationGet] = None


class StateRestraintGet(BaseModel):
    id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None


class StateSeclusionGet(BaseModel):
    id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None


class DistrictSafetyGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None
    safety_type: Optional[SchoolSafetyTypeGet] = None


class DistrictTruancyGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None


class DistrictDisciplineIncidentGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None
    incident_type: Optional[DisciplineIncidentTypeGet] = None


class DistrictDisciplineCountGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None
    count_type: Optional[DisciplineCountTypeGet] = None


class DistrictBullyingGet(BaseModel):
    id: int
    district_id: int
    year: int
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    bullying_type: Optional[BullyingTypeGet] = None


class DistrictBullyingClassificationGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None
    classification_type: Optional[BullyingClassificationTypeGet] = None


class DistrictBullyingImpactGet(BaseModel):
    id: int
    district_id: int
    year: int
    count: Optional[int] = None
    impact_type: Optional[BullyingImpactTypeGet] = None


class DistrictHarassmentGet(BaseModel):
    id: int
    district_id: int
    year: int
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    classification: Optional[HarassmentClassificationGet] = None


class DistrictRestraintGet(BaseModel):
    id: int
    district_id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None


class DistrictSeclusionGet(BaseModel):
    id: int
    district_id: int
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None


TruancyGet = SchoolTruancyGet
DisciplineIncidentGet = SchoolDisciplineIncidentGet
DisciplineCountGet = SchoolDisciplineCountGet
BullyingGet = SchoolBullyingGet
BullyingClassificationGet = SchoolBullyingClassificationGet
BullyingImpactGet = SchoolBullyingImpactGet
HarassmentGet = SchoolHarassmentGet
RestraintGet = SchoolRestraintGet
SeclusionGet = SchoolSeclusionGet


class SchoolSafetyEnrollmentGet(BaseModel):
    school_id: int
    year: int
    total_enrollment: Optional[int] = None


class DistrictSafetyEnrollmentGet(BaseModel):
    district_id: int
    year: int
    total_enrollment: Optional[int] = None


class StateSafetyEnrollmentGet(BaseModel):
    year: int
    total_enrollment: Optional[int] = None
