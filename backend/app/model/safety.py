from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .base import BaseMixin

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .location import School, District


# -------------------- Type/Classification Models --------------------

class SafetySafetyType(BaseMixin, table=True):
    __tablename__ = "safety_safety_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    school_safety_records: List["SchoolSafety"] = Relationship(back_populates="safety_type")
    state_safety_records: List["StateSafety"] = Relationship(back_populates="safety_type")
    district_safety_records: List["DistrictSafety"] = Relationship(back_populates="safety_type")


class SafetyDisciplineIncidentType(BaseMixin, table=True):
    __tablename__ = "safety_discipline_incident_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    discipline_incidents: List["SchoolDisciplineIncident"] = Relationship(back_populates="incident_type")
    state_discipline_incidents: List["StateDisciplineIncident"] = Relationship(back_populates="incident_type")
    district_discipline_incidents: List["DistrictDisciplineIncident"] = Relationship(back_populates="incident_type")


class SafetyDisciplineCountType(BaseMixin, table=True):
    __tablename__ = "safety_discipline_count_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    discipline_counts: List["SchoolDisciplineCount"] = Relationship(back_populates="count_type")
    state_discipline_counts: List["StateDisciplineCount"] = Relationship(back_populates="count_type")
    district_discipline_counts: List["DistrictDisciplineCount"] = Relationship(back_populates="count_type")


class SafetyBullyingType(BaseMixin, table=True):
    __tablename__ = "safety_bullying_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    bullying_records: List["SchoolBullying"] = Relationship(back_populates="bullying_type")
    state_bullying_records: List["StateBullying"] = Relationship(back_populates="bullying_type")
    district_bullying_records: List["DistrictBullying"] = Relationship(back_populates="bullying_type")


class SafetyBullyingClassificationType(BaseMixin, table=True):
    __tablename__ = "safety_bullying_classification_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    bullying_classifications: List["SchoolBullyingClassification"] = Relationship(back_populates="classification_type")
    state_bullying_classifications: List["StateBullyingClassification"] = Relationship(back_populates="classification_type")
    district_bullying_classifications: List["DistrictBullyingClassification"] = Relationship(back_populates="classification_type")


class SafetyBullyingImpactType(BaseMixin, table=True):
    __tablename__ = "safety_bullying_impact_type"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    bullying_impacts: List["SchoolBullyingImpact"] = Relationship(back_populates="impact_type")
    state_bullying_impacts: List["StateBullyingImpact"] = Relationship(back_populates="impact_type")
    district_bullying_impacts: List["DistrictBullyingImpact"] = Relationship(back_populates="impact_type")


class SafetyHarassmentClassification(BaseMixin, table=True):
    __tablename__ = "safety_harassment_classification"
    
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    harassment_records: List["SchoolHarassment"] = Relationship(back_populates="classification")
    state_harassment_records: List["StateHarassment"] = Relationship(back_populates="classification")
    district_harassment_records: List["DistrictHarassment"] = Relationship(back_populates="classification")

# -------------------- School-level Models --------------------

class SchoolSafety(BaseMixin, table=True):
    __tablename__ = "school_safety"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_safety_type_id_fk: int = Field(foreign_key="safety_safety_type.id")
    count: Optional[int] = None
    
    # Relationships
    safety_type: SafetySafetyType = Relationship(
        back_populates="school_safety_records",
        sa_relationship_kwargs={"foreign_keys": "SchoolSafety.school_safety_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolSafety.school_id_fk", "viewonly": True}
    )


class SchoolTruancy(BaseMixin, table=True):
    __tablename__ = "school_truancy"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    count: Optional[int] = None
    
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolTruancy.school_id_fk", "viewonly": True}
    )


class SchoolDisciplineIncident(BaseMixin, table=True):
    __tablename__ = "school_discipline_incident"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_discipline_incident_type_id_fk: int = Field(foreign_key="safety_discipline_incident_type.id")
    count: Optional[int] = None
    
    # Relationships
    incident_type: SafetyDisciplineIncidentType = Relationship(
        back_populates="discipline_incidents",
        sa_relationship_kwargs={"foreign_keys": "SchoolDisciplineIncident.school_discipline_incident_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolDisciplineIncident.school_id_fk", "viewonly": True}
    )


class SchoolDisciplineCount(BaseMixin, table=True):
    __tablename__ = "school_discipline_count"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_discipline_count_type_id_fk: int = Field(foreign_key="safety_discipline_count_type.id")
    count: Optional[int] = None
    
    # Relationships
    count_type: SafetyDisciplineCountType = Relationship(
        back_populates="discipline_counts",
        sa_relationship_kwargs={"foreign_keys": "SchoolDisciplineCount.school_discipline_count_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolDisciplineCount.school_id_fk", "viewonly": True}
    )


class SchoolBullying(BaseMixin, table=True):
    __tablename__ = "school_bullying"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_bullying_type_id_fk: int = Field(foreign_key="safety_bullying_type.id")
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    
    # Relationships
    bullying_type: SafetyBullyingType = Relationship(
        back_populates="bullying_records",
        sa_relationship_kwargs={"foreign_keys": "SchoolBullying.school_bullying_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolBullying.school_id_fk", "viewonly": True}
    )


class SchoolBullyingClassification(BaseMixin, table=True):
    __tablename__ = "school_bullying_classification"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_bullying_classification_type_id_fk: int = Field(foreign_key="safety_bullying_classification_type.id")
    count: Optional[int] = None
    
    # Relationships
    classification_type: SafetyBullyingClassificationType = Relationship(
        back_populates="bullying_classifications",
        sa_relationship_kwargs={"foreign_keys": "SchoolBullyingClassification.school_bullying_classification_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolBullyingClassification.school_id_fk", "viewonly": True}
    )


class SchoolBullyingImpact(BaseMixin, table=True):
    __tablename__ = "school_bullying_impact"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_bullying_impact_type_id_fk: int = Field(foreign_key="safety_bullying_impact_type.id")
    count: Optional[int] = None
    
    # Relationships
    impact_type: SafetyBullyingImpactType = Relationship(
        back_populates="bullying_impacts",
        sa_relationship_kwargs={"foreign_keys": "SchoolBullyingImpact.school_bullying_impact_type_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolBullyingImpact.school_id_fk", "viewonly": True}
    )


class SchoolHarassment(BaseMixin, table=True):
    __tablename__ = "school_harassment"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    school_harassment_classification_id_fk: int = Field(foreign_key="safety_harassment_classification.id")
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    
    # Relationships
    classification: SafetyHarassmentClassification = Relationship(
        back_populates="harassment_records",
        sa_relationship_kwargs={"foreign_keys": "SchoolHarassment.school_harassment_classification_id_fk"}
    )
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolHarassment.school_id_fk", "viewonly": True}
    )


class SchoolRestraint(BaseMixin, table=True):
    __tablename__ = "school_restraint"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None
    
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolRestraint.school_id_fk", "viewonly": True}
    )


class SchoolSeclusion(BaseMixin, table=True):
    __tablename__ = "school_seclusion"
    
    school_id_fk: int = Field(foreign_key="school.id")
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SchoolSeclusion.school_id_fk", "viewonly": True}
    )


# -------------------- State-level Models --------------------

class StateTruancy(BaseMixin, table=True):
    __tablename__ = "state_truancy"
    
    year: int
    count: Optional[int] = None


class StateSafety(BaseMixin, table=True):
    __tablename__ = "state_safety"
    
    year: int
    school_safety_type_id_fk: int = Field(foreign_key="safety_safety_type.id")
    count: Optional[int] = None
    
    # Relationships
    safety_type: SafetySafetyType = Relationship(
        back_populates="state_safety_records",
        sa_relationship_kwargs={"foreign_keys": "StateSafety.school_safety_type_id_fk"}
    )


class StateDisciplineIncident(BaseMixin, table=True):
    __tablename__ = "state_discipline_incident"
    
    year: int
    school_discipline_incident_type_id_fk: int = Field(foreign_key="safety_discipline_incident_type.id")
    count: Optional[int] = None
    
    # Relationships
    incident_type: SafetyDisciplineIncidentType = Relationship(
        back_populates="state_discipline_incidents",
        sa_relationship_kwargs={"foreign_keys": "StateDisciplineIncident.school_discipline_incident_type_id_fk"}
    )


class StateDisciplineCount(BaseMixin, table=True):
    __tablename__ = "state_discipline_count"
    
    year: int
    school_discipline_count_type_id_fk: int = Field(foreign_key="safety_discipline_count_type.id")
    count: Optional[int] = None
    
    # Relationships
    count_type: SafetyDisciplineCountType = Relationship(
        back_populates="state_discipline_counts",
        sa_relationship_kwargs={"foreign_keys": "StateDisciplineCount.school_discipline_count_type_id_fk"}
    )


class StateBullying(BaseMixin, table=True):
    __tablename__ = "state_bullying"
    
    year: int
    school_bullying_type_id_fk: int = Field(foreign_key="safety_bullying_type.id")
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    
    # Relationships
    bullying_type: SafetyBullyingType = Relationship(
        back_populates="state_bullying_records",
        sa_relationship_kwargs={"foreign_keys": "StateBullying.school_bullying_type_id_fk"}
    )


class StateBullyingClassification(BaseMixin, table=True):
    __tablename__ = "state_bullying_classification"
    
    year: int
    school_bullying_classification_type_id_fk: int = Field(foreign_key="safety_bullying_classification_type.id")
    count: Optional[int] = None
    
    # Relationships
    classification_type: SafetyBullyingClassificationType = Relationship(
        back_populates="state_bullying_classifications",
        sa_relationship_kwargs={"foreign_keys": "StateBullyingClassification.school_bullying_classification_type_id_fk"}
    )


class StateBullyingImpact(BaseMixin, table=True):
    __tablename__ = "state_bullying_impact"
    
    year: int
    school_bullying_impact_type_id_fk: int = Field(foreign_key="safety_bullying_impact_type.id")
    count: Optional[int] = None
    
    # Relationships
    impact_type: SafetyBullyingImpactType = Relationship(
        back_populates="state_bullying_impacts",
        sa_relationship_kwargs={"foreign_keys": "StateBullyingImpact.school_bullying_impact_type_id_fk"}
    )


class StateHarassment(BaseMixin, table=True):
    __tablename__ = "state_harassment"
    
    year: int
    school_harassment_classification_id_fk: int = Field(foreign_key="safety_harassment_classification.id")
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    
    # Relationships
    classification: SafetyHarassmentClassification = Relationship(
        back_populates="state_harassment_records",
        sa_relationship_kwargs={"foreign_keys": "StateHarassment.school_harassment_classification_id_fk"}
    )


class StateRestraint(BaseMixin, table=True):
    __tablename__ = "state_restraint"
    
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None


class StateSeclusion(BaseMixin, table=True):
    __tablename__ = "state_seclusion"
    
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None


# -------------------- District-level Models --------------------

class DistrictTruancy(BaseMixin, table=True):
    __tablename__ = "district_truancy"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    count: Optional[int] = None
    
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictTruancy.district_id_fk", "viewonly": True}
    )


class DistrictSafety(BaseMixin, table=True):
    __tablename__ = "district_safety"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_safety_type_id_fk: int = Field(foreign_key="safety_safety_type.id")
    count: Optional[int] = None
    
    # Relationships
    safety_type: SafetySafetyType = Relationship(
        back_populates="district_safety_records",
        sa_relationship_kwargs={"foreign_keys": "DistrictSafety.school_safety_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictSafety.district_id_fk", "viewonly": True}
    )


class DistrictDisciplineIncident(BaseMixin, table=True):
    __tablename__ = "district_discipline_incident"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_discipline_incident_type_id_fk: int = Field(foreign_key="safety_discipline_incident_type.id")
    count: Optional[int] = None
    
    # Relationships
    incident_type: SafetyDisciplineIncidentType = Relationship(
        back_populates="district_discipline_incidents",
        sa_relationship_kwargs={"foreign_keys": "DistrictDisciplineIncident.school_discipline_incident_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictDisciplineIncident.district_id_fk", "viewonly": True}
    )


class DistrictDisciplineCount(BaseMixin, table=True):
    __tablename__ = "district_discipline_count"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_discipline_count_type_id_fk: int = Field(foreign_key="safety_discipline_count_type.id")
    count: Optional[int] = None
    
    # Relationships
    count_type: SafetyDisciplineCountType = Relationship(
        back_populates="district_discipline_counts",
        sa_relationship_kwargs={"foreign_keys": "DistrictDisciplineCount.school_discipline_count_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictDisciplineCount.district_id_fk", "viewonly": True}
    )


class DistrictBullying(BaseMixin, table=True):
    __tablename__ = "district_bullying"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_bullying_type_id_fk: int = Field(foreign_key="safety_bullying_type.id")
    reported: Optional[int] = None
    investigated_actual: Optional[int] = None
    
    # Relationships
    bullying_type: SafetyBullyingType = Relationship(
        back_populates="district_bullying_records",
        sa_relationship_kwargs={"foreign_keys": "DistrictBullying.school_bullying_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictBullying.district_id_fk", "viewonly": True}
    )


class DistrictBullyingClassification(BaseMixin, table=True):
    __tablename__ = "district_bullying_classification"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_bullying_classification_type_id_fk: int = Field(foreign_key="safety_bullying_classification_type.id")
    count: Optional[int] = None
    
    # Relationships
    classification_type: SafetyBullyingClassificationType = Relationship(
        back_populates="district_bullying_classifications",
        sa_relationship_kwargs={"foreign_keys": "DistrictBullyingClassification.school_bullying_classification_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictBullyingClassification.district_id_fk", "viewonly": True}
    )


class DistrictBullyingImpact(BaseMixin, table=True):
    __tablename__ = "district_bullying_impact"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_bullying_impact_type_id_fk: int = Field(foreign_key="safety_bullying_impact_type.id")
    count: Optional[int] = None
    
    # Relationships
    impact_type: SafetyBullyingImpactType = Relationship(
        back_populates="district_bullying_impacts",
        sa_relationship_kwargs={"foreign_keys": "DistrictBullyingImpact.school_bullying_impact_type_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictBullyingImpact.district_id_fk", "viewonly": True}
    )


class DistrictHarassment(BaseMixin, table=True):
    __tablename__ = "district_harassment"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    school_harassment_classification_id_fk: int = Field(foreign_key="safety_harassment_classification.id")
    incident_count: Optional[int] = None
    student_impact_count: Optional[int] = None
    student_engaged_count: Optional[int] = None
    
    # Relationships
    classification: SafetyHarassmentClassification = Relationship(
        back_populates="district_harassment_records",
        sa_relationship_kwargs={"foreign_keys": "DistrictHarassment.school_harassment_classification_id_fk"}
    )
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictHarassment.district_id_fk", "viewonly": True}
    )


class DistrictRestraint(BaseMixin, table=True):
    __tablename__ = "district_restraint"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    bodily_injury: Optional[int] = None
    serious_injury: Optional[int] = None
    
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictRestraint.district_id_fk", "viewonly": True}
    )


class DistrictSeclusion(BaseMixin, table=True):
    __tablename__ = "district_seclusion"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    generated: Optional[int] = None
    active_investigation: Optional[int] = None
    closed_investigation: Optional[int] = None
    
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DistrictSeclusion.district_id_fk", "viewonly": True}
    )


# -------------------- Materialized View Models --------------------

class SchoolSafetyEnrollment(SQLModel, table=True):
    """Materialized view for school safety enrollment data."""
    __tablename__ = "school_safety_enrollment"
    
    # This is a materialized view, so we need to define primary key
    school_id_fk: int = Field(primary_key=True)
    year: int = Field(primary_key=True)
    total_enrollment: Optional[int] = None
    
    # One-way relationship to School - no inverse relationship
    school: "School" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "SchoolSafetyEnrollment.school_id_fk", 
            "primaryjoin": "SchoolSafetyEnrollment.school_id_fk == School.id",
            "viewonly": True
        }
    )


class StateSafetyEnrollment(SQLModel, table=True):
    """Materialized view for state safety enrollment data."""
    __tablename__ = "state_safety_enrollment"
    
    # This is a materialized view, so we need to define primary key
    year: int = Field(primary_key=True)
    total_enrollment: Optional[int] = None


class DistrictSafetyEnrollment(SQLModel, table=True):
    """Materialized view for district safety enrollment data."""
    __tablename__ = "district_safety_enrollment"
    
    # This is a materialized view, so we need to define primary key
    district_id_fk: int = Field(primary_key=True)
    year: int = Field(primary_key=True)
    total_enrollment: Optional[int] = None
    
    # One-way relationship to District - no inverse relationship
    district: "District" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "DistrictSafetyEnrollment.district_id_fk", 
            "primaryjoin": "DistrictSafetyEnrollment.district_id_fk == District.id",
            "viewonly": True
        }
    ) 