from typing import List, Optional, Dict
from sqlmodel import Session, select
from fastapi import HTTPException

from app.model.measurement import Measurement, MeasurementType, MeasurementTypeCategory, MeasurementStateTarget
from app.schema.measurement_schema import (
    MeasurementGet, MeasurementTypeGet, MeasurementTypeCategoryGet
)

class MeasurementService:
    def get_measurement_type_categories(self, session: Session) -> List[MeasurementTypeCategoryGet]:
        """Get all measurement type categories."""
        return [MeasurementTypeCategoryGet.from_orm(category) 
                for category in session.exec(select(MeasurementTypeCategory)).all()]

    def get_measurement_type_category_by_id(self, session: Session, category_id: int) -> MeasurementTypeCategoryGet:
        """Get measurement type category by ID."""
        category = session.get(MeasurementTypeCategory, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Measurement type category not found")
        return MeasurementTypeCategoryGet.from_orm(category)

    def get_measurement_types(self, session: Session, category_id: Optional[int] = None) -> List[MeasurementTypeGet]:
        """Get all measurement types, optionally filtered by category."""
        statement = select(MeasurementType)
        
        if category_id is not None:
            statement = statement.where(MeasurementType.measurement_type_category_id_fk == category_id)
            
        types = session.exec(statement).all()
        return [MeasurementTypeGet.from_orm(type) for type in types]

    def get_measurement_type_by_id(self, session: Session, type_id: int) -> MeasurementTypeGet:
        """Get measurement type by ID."""
        measurement_type = session.get(MeasurementType, type_id)
        if not measurement_type:
            raise HTTPException(status_code=404, detail="Measurement type not found")
        return MeasurementTypeGet.from_orm(measurement_type)

    def _get_state_targets(self, session: Session, measurements: List[Measurement]) -> Dict[tuple, float]:
        """
        Helper method to get state targets for measurements.
        Returns a dictionary mapping (measurement_type_id, year) to target value.
        """
        if not measurements:
            return {}
            
        # Extract unique (measurement_type_id, year) pairs
        type_year_pairs = set((m.measurement_type_id_fk, m.year) for m in measurements)
        
        # Query for state targets
        targets = {}
        for type_id, year in type_year_pairs:
            statement = select(MeasurementStateTarget).where(
                MeasurementStateTarget.measurement_type_id_fk == type_id,
                MeasurementStateTarget.year == year
            )
            target = session.exec(statement).first()
            if target:
                targets[(type_id, year)] = target.field
                
        return targets

    def get_measurements(
        self, 
        session: Session, 
        district_id: Optional[int] = None,
        school_id: Optional[int] = None,
        measurement_type_id: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[MeasurementGet]:
        """
        Get measurements with optional filtering by district, school, measurement type, and/or year.
        At least one of district_id or school_id should be provided for meaningful results.
        If a measurement_state_target exists for the measurement_type and year, it will be included.
        """
        statement = select(Measurement)
        
        # Apply filters if provided
        if district_id is not None:
            statement = statement.where(Measurement.district_id_fk == district_id)
        
        if school_id is not None:
            statement = statement.where(Measurement.school_id_fk == school_id)
            
        if measurement_type_id is not None:
            statement = statement.where(Measurement.measurement_type_id_fk == measurement_type_id)
            
        if year is not None:
            statement = statement.where(Measurement.year == year)
            
        measurements = session.exec(statement).all()
        
        # Get state targets for these measurements
        state_targets = self._get_state_targets(session, measurements)
        
        # Convert to response DTOs with state targets
        result = []
        for measurement in measurements:
            measurement_dto = MeasurementGet.from_orm(measurement)
            target_key = (measurement.measurement_type_id_fk, measurement.year)
            if target_key in state_targets:
                measurement_dto.state_target_field = state_targets[target_key]
            result.append(measurement_dto)
            
        return result

    def get_measurement_by_id(self, session: Session, measurement_id: int) -> MeasurementGet:
        """Get measurement by ID."""
        measurement = session.get(Measurement, measurement_id)
        if not measurement:
            raise HTTPException(status_code=404, detail="Measurement not found")
            
        # Check if there's a state target for this measurement
        statement = select(MeasurementStateTarget).where(
            MeasurementStateTarget.measurement_type_id_fk == measurement.measurement_type_id_fk,
            MeasurementStateTarget.year == measurement.year
        )
        target = session.exec(statement).first()
        
        # Convert to DTO and add state target if it exists
        measurement_dto = MeasurementGet.from_orm(measurement)
        if target:
            measurement_dto.state_target_field = target.field
            
        return measurement_dto

    def get_latest_measurements(
        self,
        session: Session,
        district_id: Optional[int] = None,
        school_id: Optional[int] = None
    ) -> List[MeasurementGet]:
        """
        Get the most recent year of measurements for a district or school.
        At least one of district_id or school_id should be provided.
        If a measurement_state_target exists for the measurement_type and year, it will be included.
        """
        from sqlalchemy import func

        # First, find the maximum year for each measurement type
        subquery = (
            select(
                Measurement.measurement_type_id_fk,
                func.max(Measurement.year).label("max_year")
            )
        )
        
        # Apply filters if provided
        if district_id is not None:
            subquery = subquery.where(Measurement.district_id_fk == district_id)
        
        if school_id is not None:
            subquery = subquery.where(Measurement.school_id_fk == school_id)
            
        subquery = subquery.group_by(Measurement.measurement_type_id_fk).subquery()
        
        # Then join with the measurements table to get the actual measurement records
        statement = (
            select(Measurement)
            .join(
                subquery,
                (Measurement.measurement_type_id_fk == subquery.c.measurement_type_id_fk) &
                (Measurement.year == subquery.c.max_year)
            )
        )
        
        # Apply the same filters again to the main query
        if district_id is not None:
            statement = statement.where(Measurement.district_id_fk == district_id)
        
        if school_id is not None:
            statement = statement.where(Measurement.school_id_fk == school_id)
            
        measurements = session.exec(statement).all()
        
        # Get state targets for these measurements
        state_targets = self._get_state_targets(session, measurements)
        
        # Convert to response DTOs with state targets
        result = []
        for measurement in measurements:
            measurement_dto = MeasurementGet.from_orm(measurement)
            target_key = (measurement.measurement_type_id_fk, measurement.year)
            if target_key in state_targets:
                measurement_dto.state_target_field = state_targets[target_key]
            result.append(measurement_dto)
            
        return result

# Create singleton instance
measurement_service = MeasurementService() 