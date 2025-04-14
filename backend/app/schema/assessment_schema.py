from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AssessmentException(str, Enum):
    TOO_FEW_SAMPLES = "TOO_FEW_SAMPLES"
    SCORE_UNDER_10 = "SCORE_UNDER_10"
    SCORE_OVER_90 = "SCORE_OVER_90"


class AssessmentSubgroupGet(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class AssessmentSubjectGet(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class AssessmentGet(BaseModel):
    id: int
    year: int
    district_id: Optional[int] = None
    school_id: Optional[int] = None
    assessment_subgroup_id: int
    assessment_subject_id: int
    grade_id: Optional[int] = None
    total_fay_students_low: Optional[int] = None
    total_fay_students_high: Optional[int] = None
    level_1_percentage: Optional[float] = None
    level_1_percentage_exception: Optional[AssessmentException] = None
    level_2_percentage: Optional[float] = None
    level_2_percentage_exception: Optional[AssessmentException] = None
    level_3_percentage: Optional[float] = None
    level_3_percentage_exception: Optional[AssessmentException] = None
    level_4_percentage: Optional[float] = None
    level_4_percentage_exception: Optional[AssessmentException] = None
    above_proficient_percentage: Optional[float] = None
    above_proficient_percentage_exception: Optional[AssessmentException] = None
    participate_percentage: Optional[float] = None
    mean_sgp: Optional[float] = None
    average_score: Optional[float] = None
    district_name: Optional[str] = None
    school_name: Optional[str] = None