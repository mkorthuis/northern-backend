from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from .base import BaseMixin

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .location import District, School, Grade


class AssessmentException(str, Enum):
    TOO_FEW_SAMPLES = "TOO_FEW_SAMPLES"
    SCORE_UNDER_10 = "SCORE_UNDER_10"
    SCORE_OVER_90 = "SCORE_OVER_90"


class AssessmentSubject(BaseMixin, table=True):
    __tablename__ = "assessment_subject"
    
    name: str = Field(max_length=100)
    description: Optional[str] = Field(max_length=255, default=None)
    
    # Relationships
    district_assessments: List["AssessmentDistrict"] = Relationship(back_populates="subject")
    school_assessments: List["AssessmentSchool"] = Relationship(back_populates="subject")
    state_assessments: List["AssessmentState"] = Relationship(back_populates="subject")


class AssessmentSubgroup(BaseMixin, table=True):
    __tablename__ = "assessment_subgroup"
    
    name: str = Field(max_length=100)
    description: Optional[str] = Field(max_length=255, default=None)
    
    # Relationships
    district_assessments: List["AssessmentDistrict"] = Relationship(back_populates="subgroup")
    school_assessments: List["AssessmentSchool"] = Relationship(back_populates="subgroup")
    state_assessments: List["AssessmentState"] = Relationship(back_populates="subgroup")


class AssessmentDistrict(BaseMixin, table=True):
    __tablename__ = "assessment_district"
    
    district_id_fk: int = Field(foreign_key="district.id")
    assessment_subject_id_fk: int = Field(foreign_key="assessment_subject.id")
    year: int
    grade_id_fk: Optional[int] = Field(foreign_key="grades.id", default=None)
    assessment_subgroup_id_fk: int = Field(foreign_key="assessment_subgroup.id")
    
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
    
    # Relationships
    subject: AssessmentSubject = Relationship(back_populates="district_assessments", 
                                               sa_relationship_kwargs={"foreign_keys": "AssessmentDistrict.assessment_subject_id_fk"})
    subgroup: AssessmentSubgroup = Relationship(back_populates="district_assessments",
                                                 sa_relationship_kwargs={"foreign_keys": "AssessmentDistrict.assessment_subgroup_id_fk"})
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(sa_relationship_kwargs={"foreign_keys": "AssessmentDistrict.district_id_fk", "viewonly": True})


class AssessmentSchool(BaseMixin, table=True):
    __tablename__ = "assessment_school"
    
    school_id_fk: int = Field(foreign_key="school.id")
    assessment_subject_id_fk: int = Field(foreign_key="assessment_subject.id")
    year: int
    grade_id_fk: Optional[int] = Field(foreign_key="grades.id", default=None)
    assessment_subgroup_id_fk: int = Field(foreign_key="assessment_subgroup.id")
    
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
    
    # Relationships
    subject: AssessmentSubject = Relationship(back_populates="school_assessments",
                                               sa_relationship_kwargs={"foreign_keys": "AssessmentSchool.assessment_subject_id_fk"})
    subgroup: AssessmentSubgroup = Relationship(back_populates="school_assessments",
                                                 sa_relationship_kwargs={"foreign_keys": "AssessmentSchool.assessment_subgroup_id_fk"})
    # One-way relationships - no inverse relationships
    school: "School" = Relationship(sa_relationship_kwargs={"foreign_keys": "AssessmentSchool.school_id_fk", "viewonly": True})
    # Get district through school relationship instead of directly


class AssessmentState(BaseMixin, table=True):
    __tablename__ = "assessment_state"
    
    assessment_subject_id_fk: int = Field(foreign_key="assessment_subject.id")
    year: int
    grade_id_fk: Optional[int] = Field(foreign_key="grades.id", default=None)
    assessment_subgroup_id_fk: int = Field(foreign_key="assessment_subgroup.id")
    
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
    
    # Relationships
    subject: AssessmentSubject = Relationship(back_populates="state_assessments",
                                               sa_relationship_kwargs={"foreign_keys": "AssessmentState.assessment_subject_id_fk"})
    subgroup: AssessmentSubgroup = Relationship(back_populates="state_assessments",
                                                 sa_relationship_kwargs={"foreign_keys": "AssessmentState.assessment_subgroup_id_fk"})
    # Add grade relationship with viewonly=True to prevent bidirectional navigation
    grade: "Grade" = Relationship(sa_relationship_kwargs={"foreign_keys": "AssessmentState.grade_id_fk", "viewonly": True}) 