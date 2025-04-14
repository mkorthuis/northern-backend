from typing import Optional, List
from sqlmodel import Field, Relationship
from .base import BaseMixin
from .location import School, District

class MeasurementTypeCategory(BaseMixin, table=True):
    __tablename__ = "measurement_type_category"
    
    name: str = Field(max_length=255)
    measurement_types: List["MeasurementType"] = Relationship(back_populates="category")

class MeasurementType(BaseMixin, table=True):
    __tablename__ = "measurement_type"
    
    name: str = Field(max_length=255)
    measurement_type_category_id_fk: int = Field(foreign_key="measurement_type_category.id")
    category: MeasurementTypeCategory = Relationship(back_populates="measurement_types")
    measurements: List["Measurement"] = Relationship(back_populates="measurement_type")
    state_targets: List["MeasurementStateTarget"] = Relationship(back_populates="measurement_type")

class Measurement(BaseMixin, table=True):
    __tablename__ = "measurement"
    
    school_id_fk: Optional[int] = Field(foreign_key="school.id")
    district_id_fk: Optional[int] = Field(foreign_key="district.id")
    measurement_type_id_fk: int = Field(foreign_key="measurement_type.id")
    year: int
    field: Optional[float]
    
    school: Optional[School] = Relationship()
    district: Optional[District] = Relationship()
    measurement_type: MeasurementType = Relationship(back_populates="measurements")

class MeasurementStateTarget(BaseMixin, table=True):
    __tablename__ = "measurement_state_target"
    
    measurement_type_id_fk: int = Field(foreign_key="measurement_type.id")
    year: int
    field: Optional[float]
    
    measurement_type: MeasurementType = Relationship(back_populates="state_targets") 