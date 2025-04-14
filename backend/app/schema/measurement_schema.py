from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

class MeasurementTypeCategoryGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class MeasurementTypeGet(BaseModel):
    id: int
    name: str
    measurement_type_category_id_fk: int = Field(alias='measurement_type_category_id')
    
    class Config:
        from_attributes = True
        populate_by_name = True

class MeasurementGet(BaseModel):
    id: int
    school_id_fk: Optional[int] = Field(alias='school_id')
    district_id_fk: Optional[int] = Field(alias='district_id')
    measurement_type_id_fk: int = Field(alias='measurement_type_id')
    year: int
    field: Optional[float]
    state_target_field: Optional[float] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class MeasurementFilter(BaseModel):
    district_id: Optional[int] = None
    measurement_type_id: Optional[int] = None
    year: Optional[int] = None 