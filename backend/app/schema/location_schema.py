from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class SAUStaffGet(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: Optional[str]
    admin_type: str
    email: Optional[str]

    class Config:
        from_attributes = True
        populate_by_name = True

class SAUGet(BaseModel):
    id: int
    name: str
    address1: Optional[str]
    address2: Optional[str]
    town: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    webpage: Optional[str]
    town_id_fk: Optional[int] = Field(alias='town_id')
    staff: List[SAUStaffGet] = []

    class Config:
        from_attributes = True
        populate_by_name = True

class DistrictGet(BaseModel):
    id: int
    name: str
    sau_id_fk: Optional[int] = Field(alias='sau_id')
    is_public: bool
    towns: Optional[List[int]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class RegionGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SchoolTypeGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class GradeGet(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class TownGet(BaseModel):
    id: int
    name: str
    district_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class SchoolGet(BaseModel):
    """
    Schema for returning school information.
    
    The latest_enrollment field is a dictionary where:
    - Keys are grade names (e.g., "K", "1", "2", etc.)
    - Values are the number of students enrolled in that grade
    - A special "total" key contains the total enrollment across all grades
    - If no enrollment data exists, this will be an empty dictionary
    """
    id: int
    name: str
    sau_id_fk: Optional[int] = Field(alias='sau_id')
    district_id_fk: Optional[int] = Field(alias='district_id')
    region_id_fk: Optional[int] = Field(alias='region_id')
    school_type_id_fk: Optional[int] = Field(alias='school_type_id')
    town_id_fk: Optional[int] = Field(alias='town_id')
    principal_first_name: Optional[str]
    principal_last_name: Optional[str]
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    county: Optional[str]
    webpage: Optional[str]
    school_type: Optional[SchoolTypeGet] = None
    grades: List[GradeGet] = []
    enrollment: Optional[Dict[int, int]] = None
    latest_enrollment: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True
        populate_by_name = True 