from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EducationFreedomAccountEntryGet(BaseModel):
    """Education Freedom Account entry schema"""
    id: int
    town_id_fk: int = Field(alias='town_id')
    year: int
    education_freedom_account_entry_type_id_fk: int = Field(alias='entry_type_id')
    value: Optional[float] = None
    date_created: datetime
    date_updated: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class EFAEntryTypeGet(BaseModel):
    """Combined Education Freedom Account entry type with its value for a specific year"""
    id: int
    name: str
    description: Optional[str] = None
    year: int
    value: Optional[float] = None
    
    class Config:
        from_attributes = True 