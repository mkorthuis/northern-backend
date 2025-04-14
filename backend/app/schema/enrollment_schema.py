from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schema.location_schema import GradeGet, SchoolGet
from datetime import datetime

class SchoolEnrollmentGet(BaseModel):
    id: int
    school_id_fk: int = Field(alias='school_id')
    grade_id_fk: int = Field(alias='grade_id')
    year: int
    enrollment: int
    grade: Optional[GradeGet] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class StateEnrollmentGet(BaseModel):
    """State-level enrollment data by year and grade level"""
    id: int
    year: int
    elementary: Optional[float] = None
    middle: Optional[float] = None
    high: Optional[float] = None
    total: Optional[float] = None
    date_created: datetime
    date_updated: datetime

    class Config:
        from_attributes = True
