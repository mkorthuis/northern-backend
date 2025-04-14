from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from .base import BaseMixin

if TYPE_CHECKING:
    from .location import Town
else:
    # Need to use a string type hint at runtime
    Town = "Town"

class EducationFreedomAccountEntryType(BaseMixin, table=True):
    """Education Freedom Account entry type model"""
    __tablename__ = "education_freedom_account_entry_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    entry_type_values: List["EducationFreedomAccountEntryTypeValue"] = Relationship(
        back_populates="entry_type",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    entries: List["EducationFreedomAccountEntry"] = Relationship(
        back_populates="entry_type",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class EducationFreedomAccountEntryTypeValue(BaseMixin, table=True):
    """Education Freedom Account entry type value model"""
    __tablename__ = "education_freedom_account_entry_type_value"
    
    education_freedom_account_entry_type_id_fk: int = Field(
        foreign_key="education_freedom_account_entry_type.id"
    )
    year: int
    value: Optional[float] = None
    
    # Relationships
    entry_type: EducationFreedomAccountEntryType = Relationship(back_populates="entry_type_values")

class EducationFreedomAccountEntry(BaseMixin, table=True):
    """Education Freedom Account entry model"""
    __tablename__ = "education_freedom_account_entry"
    
    town_id_fk: int = Field(foreign_key="town.id")
    year: int
    education_freedom_account_entry_type_id_fk: int = Field(
        foreign_key="education_freedom_account_entry_type.id"
    )
    value: Optional[float] = None
    
    # Relationships
    town: Town = Relationship(back_populates="education_freedom_account_entries")
    entry_type: EducationFreedomAccountEntryType = Relationship(back_populates="entries") 