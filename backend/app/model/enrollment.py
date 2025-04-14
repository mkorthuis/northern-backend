from sqlmodel import Field, Relationship
from .base import BaseMixin
from .location import School, Grade
from typing import Optional

class SchoolEnrollment(BaseMixin, table=True):
    __tablename__ = "school_enrollment"
    
    school_id_fk: int = Field(foreign_key="school.id")
    grade_id_fk: int = Field(foreign_key="grades.id")
    year: int
    enrollment: int
    
    school: School = Relationship()
    grade: Grade = Relationship() 

class StateEnrollment(BaseMixin, table=True):
    """State-level enrollment data by year and grade level"""
    __tablename__ = "state_enrollment"
    
    year: int = Field(index=True)
    elementary: Optional[float] = Field(default=None)
    middle: Optional[float] = Field(default=None)
    high: Optional[float] = Field(default=None)
    total: Optional[float] = Field(default=None) 