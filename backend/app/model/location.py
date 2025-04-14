from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .base import BaseMixin

if TYPE_CHECKING:
    from .finance import DistrictCostPerPupil
    from .education_freedom_account import EducationFreedomAccountEntry

# First define ALL link tables
class DistrictGradeLink(BaseMixin, table=True):
    __tablename__ = "district_grade_xref"
    district_id_fk: int = Field(foreign_key="district.id")
    grade_id_fk: int = Field(foreign_key="grades.id")

class SchoolGradeLink(BaseMixin, table=True):
    __tablename__ = "school_grade_xref"
    school_id_fk: int = Field(foreign_key="school.id")
    grade_id_fk: int = Field(foreign_key="grades.id")

class TownServedLink(BaseMixin, table=True):
    __tablename__ = "town_served_xref"
    school_id_fk: int = Field(foreign_key="school.id")
    town_id_fk: int = Field(foreign_key="town.id")

class TownDistrictLink(BaseMixin, table=True):
    __tablename__ = "town_district_xref"
    town_id_fk: int = Field(foreign_key="town.id")
    district_id_fk: int = Field(foreign_key="district.id")

# Then define the main models
class SAU(BaseMixin, table=True):
    __tablename__ = "sau"
    name: str = Field(max_length=255)
    address1: Optional[str] = Field(max_length=255, default=None)
    address2: Optional[str] = Field(max_length=255, default=None)
    town: Optional[str] = Field(max_length=255, default=None)
    state: Optional[str] = Field(max_length=50, default=None)
    zip: Optional[str] = Field(max_length=20, default=None)
    phone: Optional[str] = Field(max_length=50, default=None)
    fax: Optional[str] = Field(max_length=50, default=None)
    webpage: Optional[str] = Field(max_length=255, default=None)
    town_id_fk: Optional[int] = Field(foreign_key="town.id", default=None)

    districts: List["District"] = Relationship(back_populates="sau")
    schools: List["School"] = Relationship(back_populates="sau")
    staff: List["SAUStaff"] = Relationship(back_populates="sau")
    town_obj: Optional["Town"] = Relationship(sa_relationship_kwargs={"foreign_keys": "SAU.town_id_fk"})

class SAUStaff(BaseMixin, table=True):
    __tablename__ = "sau_staff"
    sau_id_fk: int = Field(foreign_key="sau.id")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    title: Optional[str] = Field(max_length=255, default=None)
    admin_type: str = Field(max_length=50)  # Based on migration default 'SUP'
    email: Optional[str] = Field(max_length=255, default=None)

    sau: "SAU" = Relationship(back_populates="staff")

class District(BaseMixin, table=True):
    __tablename__ = "district"
    name: str = Field(max_length=255)
    sau_id_fk: Optional[int] = Field(foreign_key="sau.id")
    sau: Optional["SAU"] = Relationship(back_populates="districts")
    is_public: bool = Field(default=True)
    schools: List["School"] = Relationship(back_populates="district")
    towns: List["Town"] = Relationship(back_populates="districts", link_model=TownDistrictLink)
    grades: List["Grade"] = Relationship(back_populates="districts", link_model=DistrictGradeLink)
    cost_per_pupil: List["DistrictCostPerPupil"] = Relationship(back_populates="district")

class Region(BaseMixin, table=True):
    __tablename__ = "region"
    name: str = Field(max_length=255)
    schools: List["School"] = Relationship(back_populates="region")

class SchoolType(BaseMixin, table=True):
    __tablename__ = "school_type"
    name: str = Field(max_length=255)
    schools: List["School"] = Relationship(back_populates="school_type")

class Grade(BaseMixin, table=True):
    __tablename__ = "grades"
    name: str = Field(max_length=50)
    schools: List["School"] = Relationship(back_populates="grades", link_model=SchoolGradeLink)
    districts: List["District"] = Relationship(back_populates="grades", link_model=DistrictGradeLink)

class Town(BaseMixin, table=True):
    __tablename__ = "town"
    name: str = Field(max_length=255)
    districts: List["District"] = Relationship(back_populates="towns", link_model=TownDistrictLink)
    schools_served: List["School"] = Relationship(back_populates="towns_served", link_model=TownServedLink)
    education_freedom_account_entries: List["EducationFreedomAccountEntry"] = Relationship(back_populates="town")

class School(BaseMixin, table=True):
    __tablename__ = "school"
    
    name: str = Field(max_length=255)
    sau_id_fk: Optional[int] = Field(foreign_key="sau.id")
    district_id_fk: Optional[int] = Field(foreign_key="district.id")
    region_id_fk: Optional[int] = Field(foreign_key="region.id")
    school_type_id_fk: Optional[int] = Field(foreign_key="school_type.id")
    town_id_fk: Optional[int] = Field(foreign_key="town.id")
    
    principal_first_name: Optional[str] = Field(max_length=100)
    principal_last_name: Optional[str] = Field(max_length=100)
    address1: Optional[str] = Field(max_length=255)
    address2: Optional[str] = Field(max_length=255)
    city: Optional[str] = Field(max_length=255)
    state: Optional[str] = Field(max_length=50)
    zip: Optional[str] = Field(max_length=20)
    phone: Optional[str] = Field(max_length=50)
    fax: Optional[str] = Field(max_length=50)
    email: Optional[str] = Field(max_length=255)
    county: Optional[str] = Field(max_length=100)
    webpage: Optional[str] = Field(max_length=255)
    
    sau: Optional["SAU"] = Relationship(back_populates="schools")
    district: Optional["District"] = Relationship(back_populates="schools")
    region: Optional["Region"] = Relationship(back_populates="schools")
    school_type: Optional["SchoolType"] = Relationship(back_populates="schools")
    town: Optional["Town"] = Relationship(sa_relationship_kwargs={"foreign_keys": "School.town_id_fk"})
    grades: List["Grade"] = Relationship(back_populates="schools", link_model=SchoolGradeLink)
    towns_served: List["Town"] = Relationship(back_populates="schools_served", link_model=TownServedLink) 