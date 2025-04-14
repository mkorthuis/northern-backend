from typing import List, Optional, Dict
from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.core.context import UserContext
from app.model.location import SAU, District, Region, SchoolType, Grade, Town, School
from app.model.enrollment import SchoolEnrollment
from app.schema.location_schema import (
    SAUGet, DistrictGet, RegionGet, SchoolTypeGet, 
    GradeGet, TownGet, SchoolGet
)

class LocationService:
    def get_saus(
        self, 
        session: Session,
        district_id: Optional[int] = None
    ) -> List[SAUGet]:
        """Get all SAUs, optionally filtering by district ID."""
        if district_id is not None:
            # Get the district first to check if it exists
            district = session.get(District, district_id)
            if not district:
                raise HTTPException(status_code=404, detail="District not found")
            
            # If the district has an SAU, return only that SAU
            if district.sau_id_fk is not None:
                sau = session.get(SAU, district.sau_id_fk)
                return [SAUGet.from_orm(sau)] if sau else []
            return []
        
        # If no district_id filter, return all SAUs
        return [SAUGet.from_orm(sau) for sau in session.exec(select(SAU)).all()]

    def get_sau_by_id(self, session: Session, sau_id: int) -> SAUGet:
        """Get SAU by ID."""
        sau = session.get(SAU, sau_id)
        if not sau:
            raise HTTPException(status_code=404, detail="SAU not found")
        return SAUGet.from_orm(sau)

    def get_districts(
        self, 
        session: Session, 
        is_public: Optional[bool] = None,
        school_id: Optional[int] = None
    ) -> List[DistrictGet]:
        """Get districts, optionally filtering by public status and/or school ID."""
        
        statement = select(District)
        
        # Apply filters
        if is_public is not None:
            statement = statement.where(District.is_public == is_public)
        
        if school_id is not None:
            school = session.get(School, school_id)
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            statement = statement.where(District.id == school.district_id_fk)
        
        districts = session.exec(statement).all()
        result = []
        
        for district in districts:
            # Create a temporary copy of the district data
            district_dict = {
                "id": district.id,
                "name": district.name,
                "sau_id_fk": district.sau_id_fk,
                "is_public": district.is_public
            }
            
            # Add town IDs list instead of town objects
            district_dict["towns"] = [town.id for town in district.towns] if district.towns else []
            
            # Create DistrictGet object from dictionary using Pydantic v2 method
            result.append(DistrictGet.model_validate(district_dict))
            
        return result

    def get_district_by_id(self, session: Session, district_id: int) -> DistrictGet:
        """Get district by ID."""
        district = session.get(District, district_id)
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
        
        # Create a temporary copy of the district data
        district_dict = {
            "id": district.id,
            "name": district.name,
            "sau_id_fk": district.sau_id_fk,
            "is_public": district.is_public
        }
        
        # Add town IDs list instead of town objects
        district_dict["towns"] = [town.id for town in district.towns] if district.towns else []
        
        # Create DistrictGet object from dictionary using Pydantic v2 method
        return DistrictGet.model_validate(district_dict)

    def get_schools(
        self, 
        session: Session,
        district_id: Optional[int] = None
    ) -> List[SchoolGet]:
        """Get all schools, optionally filtering by district ID."""
        statement = select(School)
        
        if district_id is not None:
            statement = statement.where(School.district_id_fk == district_id)
            
        schools = session.exec(statement).all()
        result = []
        
        for school in schools:
            school_data = SchoolGet.from_orm(school)
            self._add_latest_enrollment_data(session, school_data)
            result.append(school_data)
            
        return result

    def get_school_by_id(self, session: Session, school_id: int) -> SchoolGet:
        """Get school by ID."""
        school = session.get(School, school_id)
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        school_data = SchoolGet.from_orm(school)
        self._add_latest_enrollment_data(session, school_data)
        return school_data

    def _add_latest_enrollment_data(self, session: Session, school_data: SchoolGet) -> None:
        """Add latest enrollment data to school information."""
        # Get all enrollment data for this school in a single query
        statement = select(SchoolEnrollment, Grade).join(
            Grade, SchoolEnrollment.grade_id_fk == Grade.id
        ).where(
            SchoolEnrollment.school_id_fk == school_data.id
        )
        
        enrollments = session.exec(statement).all()
        
        if not enrollments:
            school_data.latest_enrollment = {}
            school_data.enrollment = {}
            return
        
        # Determine the latest year in memory
        latest_year = max(enrollment.year for enrollment, _ in enrollments)
        
        # Filter to only include the latest year's enrollments
        latest_enrollments = [(enrollment, grade) for enrollment, grade in enrollments if enrollment.year == latest_year]
        
        # Create a dictionary of grade ID to enrollment
        enrollment_by_id = {}
        # Create a dictionary of grade name to enrollment
        enrollment_by_name = {}
        total_enrollment = 0
        
        for enrollment, grade in latest_enrollments:
            enrollment_by_id[grade.id] = enrollment.enrollment
            enrollment_by_name[grade.name] = enrollment.enrollment
            total_enrollment += enrollment.enrollment
        
        # Add total enrollment
        enrollment_by_name['total'] = total_enrollment
        
        school_data.enrollment = enrollment_by_id
        school_data.latest_enrollment = enrollment_by_name

    def get_regions(self, session: Session) -> List[RegionGet]:
        """Get all regions."""
        return [RegionGet.from_orm(region) for region in session.exec(select(Region)).all()]

    def get_region_by_id(self, session: Session, region_id: int) -> RegionGet:
        """Get region by ID."""
        region = session.get(Region, region_id)
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        return RegionGet.from_orm(region)

    def get_school_types(self, session: Session) -> List[SchoolTypeGet]:
        """Get all school types."""
        return [SchoolTypeGet.from_orm(st) for st in session.exec(select(SchoolType)).all()]

    def get_school_type_by_id(self, session: Session, school_type_id: int) -> SchoolTypeGet:
        """Get school type by ID."""
        school_type = session.get(SchoolType, school_type_id)
        if not school_type:
            raise HTTPException(status_code=404, detail="School type not found")
        return SchoolTypeGet.from_orm(school_type)

    def get_grades(self, session: Session) -> List[GradeGet]:
        """Get all grades."""
        return [GradeGet.from_orm(grade) for grade in session.exec(select(Grade)).all()]

    def get_grade_by_id(self, session: Session, grade_id: int) -> GradeGet:
        """Get grade by ID."""
        grade = session.get(Grade, grade_id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade not found")
        return GradeGet.from_orm(grade)

    def get_towns(
        self, 
        session: Session,
        district_id: Optional[int] = None
    ) -> List[TownGet]:
        """Get all towns, optionally filtering by district ID."""
        
        if district_id is not None:
            # For filtering by district_id, we need to query through the link table
            # Since it's a many-to-many relationship
            from app.model.location import TownDistrictLink
            
            # Get town IDs linked to this district
            statement = select(TownDistrictLink.town_id_fk).where(
                TownDistrictLink.district_id_fk == district_id
            )
            # When selecting a single column, SQLModel returns the values directly (not as tuples)
            town_ids = session.exec(statement).all()
            
            # Then get the towns with those IDs
            if town_ids:
                statement = select(Town).where(Town.id.in_(town_ids))
                towns = session.exec(statement).all()
            else:
                towns = []
        else:
            # If no district_id filter, get all towns
            towns = session.exec(select(Town)).all()
        
        result = []
        
        for town in towns:
            # Create a temporary copy of the town data
            town_dict = {
                "id": town.id,
                "name": town.name
            }
            
            # Add district IDs list instead of district objects
            town_dict["district_ids"] = [district.id for district in town.districts] if town.districts else []
            
            # Create TownGet object from dictionary using Pydantic v2 method
            result.append(TownGet.model_validate(town_dict))
            
        return result

    def get_town_by_id(self, session: Session, town_id: int) -> TownGet:
        """Get town by ID."""
        town = session.get(Town, town_id)
        if not town:
            raise HTTPException(status_code=404, detail="Town not found")
        
        # Create a temporary copy of the town data
        town_dict = {
            "id": town.id,
            "name": town.name
        }
        
        # Add district IDs list instead of district objects
        town_dict["district_ids"] = [district.id for district in town.districts] if town.districts else []
        
        # Create TownGet object from dictionary using Pydantic v2 method
        return TownGet.model_validate(town_dict)

location_service = LocationService() 