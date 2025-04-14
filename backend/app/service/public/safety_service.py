from sqlalchemy.orm import Session, selectinload
from sqlmodel import select, col, or_, and_
from typing import List, Optional, Dict, Any, Union
from fastapi import HTTPException
import logging

from app.model.safety import (
    SafetySafetyType, SchoolSafety, SchoolTruancy,
    SafetyDisciplineIncidentType, SchoolDisciplineIncident,
    SafetyDisciplineCountType, SchoolDisciplineCount,
    SafetyBullyingType, SchoolBullying,
    SafetyBullyingClassificationType, SchoolBullyingClassification,
    SafetyBullyingImpactType, SchoolBullyingImpact,
    SafetyHarassmentClassification, SchoolHarassment,
    SchoolRestraint, SchoolSeclusion,
    # Add State models
    StateSafety, StateTruancy,
    StateDisciplineIncident, StateDisciplineCount,
    StateBullying, StateBullyingClassification,
    StateBullyingImpact, StateHarassment,
    StateRestraint, StateSeclusion,
    # Add District models
    DistrictSafety, DistrictTruancy,
    DistrictDisciplineIncident, DistrictDisciplineCount,
    DistrictBullying, DistrictBullyingClassification,
    DistrictBullyingImpact, DistrictHarassment,
    DistrictRestraint, DistrictSeclusion,
    # Add Enrollment models
    SchoolSafetyEnrollment, StateSafetyEnrollment, DistrictSafetyEnrollment
)
from app.model.location import School, District
from app.schema.safety_schema import (
    SchoolSafetyTypeGet, SchoolSafetyGet, SchoolTruancyGet,
    DisciplineIncidentTypeGet, SchoolDisciplineIncidentGet,
    DisciplineCountTypeGet, SchoolDisciplineCountGet,
    BullyingTypeGet, SchoolBullyingGet,
    BullyingClassificationTypeGet, SchoolBullyingClassificationGet,
    BullyingImpactTypeGet, SchoolBullyingImpactGet,
    HarassmentClassificationGet, SchoolHarassmentGet,
    SchoolRestraintGet, SchoolSeclusionGet,
    # Add State schemas
    StateSafetyGet, StateTruancyGet,
    StateDisciplineIncidentGet, StateDisciplineCountGet,
    StateBullyingGet, StateBullyingClassificationGet, 
    StateBullyingImpactGet, StateHarassmentGet,
    StateRestraintGet, StateSeclusionGet,
    # Add District schemas
    DistrictSafetyGet, DistrictTruancyGet,
    DistrictDisciplineIncidentGet, DistrictDisciplineCountGet,
    DistrictBullyingGet, DistrictBullyingClassificationGet,
    DistrictBullyingImpactGet, DistrictHarassmentGet,
    DistrictRestraintGet, DistrictSeclusionGet,
    # Add Enrollment schemas
    SchoolSafetyEnrollmentGet, StateSafetyEnrollmentGet, DistrictSafetyEnrollmentGet
)

logger = logging.getLogger(__name__)

class SafetyService:
    def get_safety_types(self, session: Session) -> List[SchoolSafetyTypeGet]:
        """Get all safety types"""
        try:
            result = session.exec(select(SafetySafetyType).order_by(SafetySafetyType.name)).all()
            return [SchoolSafetyTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching safety types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch safety types")
            
    def get_discipline_incident_types(self, session: Session) -> List[DisciplineIncidentTypeGet]:
        """Get all discipline incident types"""
        try:
            result = session.exec(select(SafetyDisciplineIncidentType).order_by(SafetyDisciplineIncidentType.name)).all()
            return [DisciplineIncidentTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching discipline incident types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch discipline incident types")
            
    def get_discipline_count_types(self, session: Session) -> List[DisciplineCountTypeGet]:
        """Get all discipline count types"""
        try:
            result = session.exec(select(SafetyDisciplineCountType).order_by(SafetyDisciplineCountType.name)).all()
            return [DisciplineCountTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching discipline count types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch discipline count types")
            
    def get_bullying_types(self, session: Session) -> List[BullyingTypeGet]:
        """Get all bullying types"""
        try:
            result = session.exec(select(SafetyBullyingType).order_by(SafetyBullyingType.name)).all()
            return [BullyingTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching bullying types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying types")
            
    def get_bullying_classification_types(self, session: Session) -> List[BullyingClassificationTypeGet]:
        """Get all bullying classification types"""
        try:
            result = session.exec(select(SafetyBullyingClassificationType).order_by(SafetyBullyingClassificationType.name)).all()
            return [BullyingClassificationTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching bullying classification types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying classification types")
            
    def get_bullying_impact_types(self, session: Session) -> List[BullyingImpactTypeGet]:
        """Get all bullying impact types"""
        try:
            result = session.exec(select(SafetyBullyingImpactType).order_by(SafetyBullyingImpactType.name)).all()
            return [BullyingImpactTypeGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching bullying impact types: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying impact types")
            
    def get_harassment_classifications(self, session: Session) -> List[HarassmentClassificationGet]:
        """Get all harassment classifications"""
        try:
            result = session.exec(select(SafetyHarassmentClassification).order_by(SafetyHarassmentClassification.name)).all()
            return [HarassmentClassificationGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching harassment classifications: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch harassment classifications")
    
    def _apply_common_filters(self, statement, model, year=None, school_id=None, district_id=None):
        """Apply common filters for safety-related queries"""
        if year is not None:
            statement = statement.where(model.year == year)
            
        if school_id is not None:
            statement = statement.where(model.school_id_fk == school_id)
            
        if district_id is not None:
            statement = statement.where(School.district_id_fk == district_id)
            
        return statement
    
    def get_school_safety(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        safety_type_id: Optional[int] = None
    ) -> List[SchoolSafetyGet]:
        """Get school safety data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolSafety,
                SafetySafetyType
            ).join(
                School,
                SchoolSafety.school_id_fk == School.id
            ).join(
                SafetySafetyType,
                SchoolSafety.school_safety_type_id_fk == SafetySafetyType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolSafety, year, school_id, district_id)
            
            # Apply specific filter
            if safety_type_id is not None:
                statement = statement.where(SchoolSafety.school_safety_type_id_fk == safety_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            safety_data = []
            for safety, safety_type in result:
                safety_type_data = safety_type.dict()
                
                data = {
                    "id": safety.id,
                    "school_id": safety.school_id_fk,
                    "year": safety.year,
                    "count": safety.count,
                    "safety_type": SchoolSafetyTypeGet.model_validate(safety_type_data)
                }
                safety_data.append(SchoolSafetyGet.model_validate(data))
                
            return safety_data
        except Exception as e:
            logger.error(f"Error fetching school safety data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch school safety data")
    
    def get_school_truancy(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[SchoolTruancyGet]:
        """Get school truancy data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolTruancy
            ).join(
                School,
                SchoolTruancy.school_id_fk == School.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolTruancy, year, school_id, district_id)
                
            # Execute query
            result = session.exec(statement)
            
            truancy_data = []
            for truancy in result:
                data = {
                    "id": truancy.id,
                    "school_id": truancy.school_id_fk,
                    "year": truancy.year,
                    "count": truancy.count
                }
                truancy_data.append(SchoolTruancyGet.model_validate(data))
                
            return truancy_data
        except Exception as e:
            logger.error(f"Error fetching truancy data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch truancy data")
    
    def get_school_discipline_incidents(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        discipline_incident_type_id: Optional[int] = None
    ) -> List[SchoolDisciplineIncidentGet]:
        """Get school discipline incident data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolDisciplineIncident,
                SafetyDisciplineIncidentType
            ).join(
                School,
                SchoolDisciplineIncident.school_id_fk == School.id
            ).join(
                SafetyDisciplineIncidentType,
                SchoolDisciplineIncident.school_discipline_incident_type_id_fk == SafetyDisciplineIncidentType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolDisciplineIncident, year, school_id, district_id)
            
            # Apply specific filter
            if discipline_incident_type_id is not None:
                statement = statement.where(SchoolDisciplineIncident.school_discipline_incident_type_id_fk == discipline_incident_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            incident_data = []
            for incident, incident_type in result:
                incident_type_data = incident_type.dict()
                
                data = {
                    "id": incident.id,
                    "school_id": incident.school_id_fk,
                    "year": incident.year,
                    "count": incident.count,
                    "incident_type": DisciplineIncidentTypeGet.model_validate(incident_type_data)
                }
                incident_data.append(SchoolDisciplineIncidentGet.model_validate(data))
                
            return incident_data
        except Exception as e:
            logger.error(f"Error fetching discipline incident data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch discipline incident data")
    
    def get_school_discipline_counts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        discipline_count_type_id: Optional[int] = None
    ) -> List[SchoolDisciplineCountGet]:
        """Get school discipline count data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolDisciplineCount,
                SafetyDisciplineCountType
            ).join(
                School,
                SchoolDisciplineCount.school_id_fk == School.id
            ).join(
                SafetyDisciplineCountType,
                SchoolDisciplineCount.school_discipline_count_type_id_fk == SafetyDisciplineCountType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolDisciplineCount, year, school_id, district_id)
            
            # Apply specific filter
            if discipline_count_type_id is not None:
                statement = statement.where(SchoolDisciplineCount.school_discipline_count_type_id_fk == discipline_count_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            count_data = []
            for count, count_type in result:
                count_type_data = count_type.dict()
                
                data = {
                    "id": count.id,
                    "school_id": count.school_id_fk,
                    "year": count.year,
                    "count": count.count,
                    "count_type": DisciplineCountTypeGet.model_validate(count_type_data)
                }
                count_data.append(SchoolDisciplineCountGet.model_validate(data))
                
            return count_data
        except Exception as e:
            logger.error(f"Error fetching discipline count data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch discipline count data")
    
    def get_school_bullying(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_type_id: Optional[int] = None
    ) -> List[SchoolBullyingGet]:
        """Get school bullying data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolBullying,
                SafetyBullyingType
            ).join(
                School,
                SchoolBullying.school_id_fk == School.id
            ).join(
                SafetyBullyingType,
                SchoolBullying.school_bullying_type_id_fk == SafetyBullyingType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolBullying, year, school_id, district_id)
            
            # Apply specific filter
            if bullying_type_id is not None:
                statement = statement.where(SchoolBullying.school_bullying_type_id_fk == bullying_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            bullying_data = []
            for bullying, bullying_type in result:
                bullying_type_data = bullying_type.dict()
                
                data = {
                    "id": bullying.id,
                    "school_id": bullying.school_id_fk,
                    "year": bullying.year,
                    "reported": bullying.reported,
                    "investigated_actual": bullying.investigated_actual,
                    "bullying_type": BullyingTypeGet.model_validate(bullying_type_data)
                }
                bullying_data.append(SchoolBullyingGet.model_validate(data))
                
            return bullying_data
        except Exception as e:
            logger.error(f"Error fetching bullying data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying data")
    
    def get_school_bullying_classifications(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_classification_type_id: Optional[int] = None
    ) -> List[SchoolBullyingClassificationGet]:
        """Get school bullying classification data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolBullyingClassification,
                SafetyBullyingClassificationType
            ).join(
                School,
                SchoolBullyingClassification.school_id_fk == School.id
            ).join(
                SafetyBullyingClassificationType,
                SchoolBullyingClassification.school_bullying_classification_type_id_fk == SafetyBullyingClassificationType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolBullyingClassification, year, school_id, district_id)
            
            # Apply specific filter
            if bullying_classification_type_id is not None:
                statement = statement.where(SchoolBullyingClassification.school_bullying_classification_type_id_fk == bullying_classification_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            classification_data = []
            for classification, classification_type in result:
                classification_type_data = classification_type.dict()
                
                data = {
                    "id": classification.id,
                    "school_id": classification.school_id_fk,
                    "year": classification.year,
                    "count": classification.count,
                    "classification_type": BullyingClassificationTypeGet.model_validate(classification_type_data)
                }
                classification_data.append(SchoolBullyingClassificationGet.model_validate(data))
                
            return classification_data
        except Exception as e:
            logger.error(f"Error fetching bullying classification data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying classification data")
    
    def get_school_bullying_impacts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_impact_type_id: Optional[int] = None
    ) -> List[SchoolBullyingImpactGet]:
        """Get school bullying impact data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolBullyingImpact,
                SafetyBullyingImpactType
            ).join(
                School,
                SchoolBullyingImpact.school_id_fk == School.id
            ).join(
                SafetyBullyingImpactType,
                SchoolBullyingImpact.school_bullying_impact_type_id_fk == SafetyBullyingImpactType.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolBullyingImpact, year, school_id, district_id)
            
            # Apply specific filter
            if bullying_impact_type_id is not None:
                statement = statement.where(SchoolBullyingImpact.school_bullying_impact_type_id_fk == bullying_impact_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            impact_data = []
            for impact, impact_type in result:
                impact_type_data = impact_type.dict()
                
                data = {
                    "id": impact.id,
                    "school_id": impact.school_id_fk,
                    "year": impact.year,
                    "count": impact.count,
                    "impact_type": BullyingImpactTypeGet.model_validate(impact_type_data)
                }
                impact_data.append(SchoolBullyingImpactGet.model_validate(data))
                
            return impact_data
        except Exception as e:
            logger.error(f"Error fetching bullying impact data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch bullying impact data")
    
    def get_school_harassment(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        harassment_classification_id: Optional[int] = None
    ) -> List[SchoolHarassmentGet]:
        """Get school harassment data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolHarassment,
                SafetyHarassmentClassification
            ).join(
                School,
                SchoolHarassment.school_id_fk == School.id
            ).join(
                SafetyHarassmentClassification,
                SchoolHarassment.school_harassment_classification_id_fk == SafetyHarassmentClassification.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolHarassment, year, school_id, district_id)
            
            # Apply specific filter
            if harassment_classification_id is not None:
                statement = statement.where(SchoolHarassment.school_harassment_classification_id_fk == harassment_classification_id)
                
            # Execute query
            result = session.exec(statement)
            
            harassment_data = []
            for harassment, classification in result:
                classification_data = classification.dict()
                
                data = {
                    "id": harassment.id,
                    "school_id": harassment.school_id_fk,
                    "year": harassment.year,
                    "incident_count": harassment.incident_count,
                    "student_impact_count": harassment.student_impact_count,
                    "student_engaged_count": harassment.student_engaged_count,
                    "classification": HarassmentClassificationGet.model_validate(classification_data)
                }
                harassment_data.append(SchoolHarassmentGet.model_validate(data))
                
            return harassment_data
        except Exception as e:
            logger.error(f"Error fetching harassment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch harassment data")
    
    def get_school_restraint(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[SchoolRestraintGet]:
        """Get school restraint data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolRestraint
            ).join(
                School,
                SchoolRestraint.school_id_fk == School.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolRestraint, year, school_id, district_id)
                
            # Execute query
            result = session.exec(statement)
            
            restraint_data = []
            for restraint in result:
                data = {
                    "id": restraint.id,
                    "school_id": restraint.school_id_fk,
                    "year": restraint.year,
                    "generated": restraint.generated,
                    "active_investigation": restraint.active_investigation,
                    "closed_investigation": restraint.closed_investigation,
                    "bodily_injury": restraint.bodily_injury,
                    "serious_injury": restraint.serious_injury
                }
                restraint_data.append(SchoolRestraintGet.model_validate(data))
                
            return restraint_data
        except Exception as e:
            logger.error(f"Error fetching restraint data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch restraint data")
    
    def get_school_seclusion(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[SchoolSeclusionGet]:
        """Get school seclusion data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolSeclusion
            ).join(
                School,
                SchoolSeclusion.school_id_fk == School.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(statement, SchoolSeclusion, year, school_id, district_id)
                
            # Execute query
            result = session.exec(statement)
            
            seclusion_data = []
            for seclusion in result:
                data = {
                    "id": seclusion.id,
                    "school_id": seclusion.school_id_fk,
                    "year": seclusion.year,
                    "generated": seclusion.generated,
                    "active_investigation": seclusion.active_investigation,
                    "closed_investigation": seclusion.closed_investigation
                }
                seclusion_data.append(SchoolSeclusionGet.model_validate(data))
                
            return seclusion_data
        except Exception as e:
            logger.error(f"Error fetching seclusion data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch seclusion data")


    # Backward compatibility methods
    def get_truancy(self, session: Session, year=None, school_id=None, district_id=None) -> List[SchoolTruancyGet]:
        """Backward compatibility method for get_school_truancy"""
        return self.get_school_truancy(session, year, school_id, district_id)
        
    def get_discipline_incidents(self, session: Session, year=None, school_id=None, district_id=None, discipline_incident_type_id=None) -> List[SchoolDisciplineIncidentGet]:
        """Backward compatibility method for get_school_discipline_incidents"""
        return self.get_school_discipline_incidents(session, year, school_id, district_id, discipline_incident_type_id)
        
    def get_discipline_counts(self, session: Session, year=None, school_id=None, district_id=None, discipline_count_type_id=None) -> List[SchoolDisciplineCountGet]:
        """Backward compatibility method for get_school_discipline_counts"""
        return self.get_school_discipline_counts(session, year, school_id, district_id, discipline_count_type_id)
        
    def get_bullying(self, session: Session, year=None, school_id=None, district_id=None, bullying_type_id=None) -> List[SchoolBullyingGet]:
        """Backward compatibility method for get_school_bullying"""
        return self.get_school_bullying(session, year, school_id, district_id, bullying_type_id)
        
    def get_bullying_classifications(self, session: Session, year=None, school_id=None, district_id=None, bullying_classification_type_id=None) -> List[SchoolBullyingClassificationGet]:
        """Backward compatibility method for get_school_bullying_classifications"""
        return self.get_school_bullying_classifications(session, year, school_id, district_id, bullying_classification_type_id)
        
    def get_bullying_impacts(self, session: Session, year=None, school_id=None, district_id=None, bullying_impact_type_id=None) -> List[SchoolBullyingImpactGet]:
        """Backward compatibility method for get_school_bullying_impacts"""
        return self.get_school_bullying_impacts(session, year, school_id, district_id, bullying_impact_type_id)
        
    def get_harassment(self, session: Session, year=None, school_id=None, district_id=None, harassment_classification_id=None) -> List[SchoolHarassmentGet]:
        """Backward compatibility method for get_school_harassment"""
        return self.get_school_harassment(session, year, school_id, district_id, harassment_classification_id)
        
    def get_restraint(self, session: Session, year=None, school_id=None, district_id=None) -> List[SchoolRestraintGet]:
        """Backward compatibility method for get_school_restraint"""
        return self.get_school_restraint(session, year, school_id, district_id)
        
    def get_seclusion(self, session: Session, year=None, school_id=None, district_id=None) -> List[SchoolSeclusionGet]:
        """Backward compatibility method for get_school_seclusion"""
        return self.get_school_seclusion(session, year, school_id, district_id)

    # State-level methods
    def get_state_safety(
        self, 
        session: Session, 
        year: Optional[int] = None,
        safety_type_id: Optional[int] = None
    ) -> List[StateSafetyGet]:
        """Get state safety data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateSafety,
                SafetySafetyType
            ).join(
                SafetySafetyType,
                StateSafety.school_safety_type_id_fk == SafetySafetyType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateSafety.year == year)
                
            if safety_type_id is not None:
                statement = statement.where(StateSafety.school_safety_type_id_fk == safety_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            safety_data = []
            for safety, safety_type in result:
                safety_type_data = safety_type.dict()
                
                data = {
                    "id": safety.id,
                    "year": safety.year,
                    "count": safety.count,
                    "safety_type": SchoolSafetyTypeGet.model_validate(safety_type_data)
                }
                safety_data.append(StateSafetyGet.model_validate(data))
                
            return safety_data
        except Exception as e:
            logger.error(f"Error fetching state safety data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state safety data")

    def get_state_truancy(
        self, 
        session: Session, 
        year: Optional[int] = None
    ) -> List[StateTruancyGet]:
        """Get state truancy data with optional filters"""
        try:
            # Create base query
            statement = select(StateTruancy)
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateTruancy.year == year)
                
            # Execute query
            result = session.exec(statement)
            
            truancy_data = []
            for truancy in result:
                data = {
                    "id": truancy.id,
                    "year": truancy.year,
                    "count": truancy.count
                }
                truancy_data.append(StateTruancyGet.model_validate(data))
                
            return truancy_data
        except Exception as e:
            logger.error(f"Error fetching state truancy data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state truancy data")
    
    def get_state_discipline_incidents(
        self, 
        session: Session, 
        year: Optional[int] = None,
        discipline_incident_type_id: Optional[int] = None
    ) -> List[StateDisciplineIncidentGet]:
        """Get state discipline incident data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateDisciplineIncident,
                SafetyDisciplineIncidentType
            ).join(
                SafetyDisciplineIncidentType,
                StateDisciplineIncident.school_discipline_incident_type_id_fk == SafetyDisciplineIncidentType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateDisciplineIncident.year == year)
                
            if discipline_incident_type_id is not None:
                statement = statement.where(StateDisciplineIncident.school_discipline_incident_type_id_fk == discipline_incident_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            incident_data = []
            for incident, incident_type in result:
                incident_type_data = incident_type.dict()
                
                data = {
                    "id": incident.id,
                    "year": incident.year,
                    "count": incident.count,
                    "incident_type": DisciplineIncidentTypeGet.model_validate(incident_type_data)
                }
                incident_data.append(StateDisciplineIncidentGet.model_validate(data))
                
            return incident_data
        except Exception as e:
            logger.error(f"Error fetching state discipline incident data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state discipline incident data")
    
    def get_state_discipline_counts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        discipline_count_type_id: Optional[int] = None
    ) -> List[StateDisciplineCountGet]:
        """Get state discipline count data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateDisciplineCount,
                SafetyDisciplineCountType
            ).join(
                SafetyDisciplineCountType,
                StateDisciplineCount.school_discipline_count_type_id_fk == SafetyDisciplineCountType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateDisciplineCount.year == year)
                
            if discipline_count_type_id is not None:
                statement = statement.where(StateDisciplineCount.school_discipline_count_type_id_fk == discipline_count_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            count_data = []
            for count, count_type in result:
                count_type_data = count_type.dict()
                
                data = {
                    "id": count.id,
                    "year": count.year,
                    "count": count.count,
                    "count_type": DisciplineCountTypeGet.model_validate(count_type_data)
                }
                count_data.append(StateDisciplineCountGet.model_validate(data))
                
            return count_data
        except Exception as e:
            logger.error(f"Error fetching state discipline count data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state discipline count data")
    
    def get_state_bullying(
        self, 
        session: Session, 
        year: Optional[int] = None,
        bullying_type_id: Optional[int] = None
    ) -> List[StateBullyingGet]:
        """Get state bullying data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateBullying,
                SafetyBullyingType
            ).join(
                SafetyBullyingType,
                StateBullying.school_bullying_type_id_fk == SafetyBullyingType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateBullying.year == year)
                
            if bullying_type_id is not None:
                statement = statement.where(StateBullying.school_bullying_type_id_fk == bullying_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            bullying_data = []
            for bullying, bullying_type in result:
                bullying_type_data = bullying_type.dict()
                
                data = {
                    "id": bullying.id,
                    "year": bullying.year,
                    "reported": bullying.reported,
                    "investigated_actual": bullying.investigated_actual,
                    "bullying_type": BullyingTypeGet.model_validate(bullying_type_data)
                }
                bullying_data.append(StateBullyingGet.model_validate(data))
                
            return bullying_data
        except Exception as e:
            logger.error(f"Error fetching state bullying data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state bullying data")
    
    def get_state_bullying_classifications(
        self, 
        session: Session, 
        year: Optional[int] = None,
        bullying_classification_type_id: Optional[int] = None
    ) -> List[StateBullyingClassificationGet]:
        """Get state bullying classification data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateBullyingClassification,
                SafetyBullyingClassificationType
            ).join(
                SafetyBullyingClassificationType,
                StateBullyingClassification.school_bullying_classification_type_id_fk == SafetyBullyingClassificationType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateBullyingClassification.year == year)
                
            if bullying_classification_type_id is not None:
                statement = statement.where(StateBullyingClassification.school_bullying_classification_type_id_fk == bullying_classification_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            classification_data = []
            for classification, classification_type in result:
                classification_type_data = classification_type.dict()
                
                data = {
                    "id": classification.id,
                    "year": classification.year,
                    "count": classification.count,
                    "classification_type": BullyingClassificationTypeGet.model_validate(classification_type_data)
                }
                classification_data.append(StateBullyingClassificationGet.model_validate(data))
                
            return classification_data
        except Exception as e:
            logger.error(f"Error fetching state bullying classification data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state bullying classification data")
    
    def get_state_bullying_impacts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        bullying_impact_type_id: Optional[int] = None
    ) -> List[StateBullyingImpactGet]:
        """Get state bullying impact data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateBullyingImpact,
                SafetyBullyingImpactType
            ).join(
                SafetyBullyingImpactType,
                StateBullyingImpact.school_bullying_impact_type_id_fk == SafetyBullyingImpactType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateBullyingImpact.year == year)
                
            if bullying_impact_type_id is not None:
                statement = statement.where(StateBullyingImpact.school_bullying_impact_type_id_fk == bullying_impact_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            impact_data = []
            for impact, impact_type in result:
                impact_type_data = impact_type.dict()
                
                data = {
                    "id": impact.id,
                    "year": impact.year,
                    "count": impact.count,
                    "impact_type": BullyingImpactTypeGet.model_validate(impact_type_data)
                }
                impact_data.append(StateBullyingImpactGet.model_validate(data))
                
            return impact_data
        except Exception as e:
            logger.error(f"Error fetching state bullying impact data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state bullying impact data")
    
    def get_state_harassment(
        self, 
        session: Session, 
        year: Optional[int] = None,
        harassment_classification_id: Optional[int] = None
    ) -> List[StateHarassmentGet]:
        """Get state harassment data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateHarassment,
                SafetyHarassmentClassification
            ).join(
                SafetyHarassmentClassification,
                StateHarassment.school_harassment_classification_id_fk == SafetyHarassmentClassification.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateHarassment.year == year)
                
            if harassment_classification_id is not None:
                statement = statement.where(StateHarassment.school_harassment_classification_id_fk == harassment_classification_id)
                
            # Execute query
            result = session.exec(statement)
            
            harassment_data = []
            for harassment, classification in result:
                classification_data = classification.dict()
                
                data = {
                    "id": harassment.id,
                    "year": harassment.year,
                    "incident_count": harassment.incident_count,
                    "student_impact_count": harassment.student_impact_count,
                    "student_engaged_count": harassment.student_engaged_count,
                    "classification": HarassmentClassificationGet.model_validate(classification_data)
                }
                harassment_data.append(StateHarassmentGet.model_validate(data))
                
            return harassment_data
        except Exception as e:
            logger.error(f"Error fetching state harassment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state harassment data")
    
    def get_state_restraint(
        self, 
        session: Session, 
        year: Optional[int] = None
    ) -> List[StateRestraintGet]:
        """Get state restraint data with optional filters"""
        try:
            # Create base query
            statement = select(StateRestraint)
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateRestraint.year == year)
                
            # Execute query
            result = session.exec(statement)
            
            restraint_data = []
            for restraint in result:
                data = {
                    "id": restraint.id,
                    "year": restraint.year,
                    "generated": restraint.generated,
                    "active_investigation": restraint.active_investigation,
                    "closed_investigation": restraint.closed_investigation,
                    "bodily_injury": restraint.bodily_injury,
                    "serious_injury": restraint.serious_injury
                }
                restraint_data.append(StateRestraintGet.model_validate(data))
                
            return restraint_data
        except Exception as e:
            logger.error(f"Error fetching state restraint data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state restraint data")
    
    def get_state_seclusion(
        self, 
        session: Session, 
        year: Optional[int] = None
    ) -> List[StateSeclusionGet]:
        """Get state seclusion data with optional filters"""
        try:
            # Create base query
            statement = select(StateSeclusion)
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateSeclusion.year == year)
                
            # Execute query
            result = session.exec(statement)
            
            seclusion_data = []
            for seclusion in result:
                data = {
                    "id": seclusion.id,
                    "year": seclusion.year,
                    "generated": seclusion.generated,
                    "active_investigation": seclusion.active_investigation,
                    "closed_investigation": seclusion.closed_investigation
                }
                seclusion_data.append(StateSeclusionGet.model_validate(data))
                
            return seclusion_data
        except Exception as e:
            logger.error(f"Error fetching state seclusion data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state seclusion data")

    # District-level methods
    def get_district_safety(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        safety_type_id: Optional[int] = None
    ) -> List[DistrictSafetyGet]:
        """Get district safety data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictSafety,
                SafetySafetyType
            ).join(
                District,
                DistrictSafety.district_id_fk == District.id
            ).join(
                SafetySafetyType,
                DistrictSafety.school_safety_type_id_fk == SafetySafetyType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictSafety.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictSafety.district_id_fk == district_id)
                
            if safety_type_id is not None:
                statement = statement.where(DistrictSafety.school_safety_type_id_fk == safety_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            safety_data = []
            for safety, safety_type in result:
                safety_type_data = safety_type.dict()
                
                data = {
                    "id": safety.id,
                    "district_id": safety.district_id_fk,
                    "year": safety.year,
                    "count": safety.count,
                    "safety_type": SchoolSafetyTypeGet.model_validate(safety_type_data)
                }
                safety_data.append(DistrictSafetyGet.model_validate(data))
                
            return safety_data
        except Exception as e:
            logger.error(f"Error fetching district safety data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district safety data")

    def get_district_truancy(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[DistrictTruancyGet]:
        """Get district truancy data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictTruancy
            ).join(
                District,
                DistrictTruancy.district_id_fk == District.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictTruancy.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictTruancy.district_id_fk == district_id)
                
            # Execute query
            result = session.exec(statement)
            
            truancy_data = []
            for truancy in result:
                data = {
                    "id": truancy.id,
                    "district_id": truancy.district_id_fk,
                    "year": truancy.year,
                    "count": truancy.count
                }
                truancy_data.append(DistrictTruancyGet.model_validate(data))
                
            return truancy_data
        except Exception as e:
            logger.error(f"Error fetching district truancy data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district truancy data")
    
    def get_district_discipline_incidents(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        discipline_incident_type_id: Optional[int] = None
    ) -> List[DistrictDisciplineIncidentGet]:
        """Get district discipline incident data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictDisciplineIncident,
                SafetyDisciplineIncidentType
            ).join(
                District,
                DistrictDisciplineIncident.district_id_fk == District.id
            ).join(
                SafetyDisciplineIncidentType,
                DistrictDisciplineIncident.school_discipline_incident_type_id_fk == SafetyDisciplineIncidentType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictDisciplineIncident.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictDisciplineIncident.district_id_fk == district_id)
                
            if discipline_incident_type_id is not None:
                statement = statement.where(DistrictDisciplineIncident.school_discipline_incident_type_id_fk == discipline_incident_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            incident_data = []
            for incident, incident_type in result:
                incident_type_data = incident_type.dict()
                
                data = {
                    "id": incident.id,
                    "district_id": incident.district_id_fk,
                    "year": incident.year,
                    "count": incident.count,
                    "incident_type": DisciplineIncidentTypeGet.model_validate(incident_type_data)
                }
                incident_data.append(DistrictDisciplineIncidentGet.model_validate(data))
                
            return incident_data
        except Exception as e:
            logger.error(f"Error fetching district discipline incident data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district discipline incident data")
    
    def get_district_discipline_counts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        discipline_count_type_id: Optional[int] = None
    ) -> List[DistrictDisciplineCountGet]:
        """Get district discipline count data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictDisciplineCount,
                SafetyDisciplineCountType
            ).join(
                District,
                DistrictDisciplineCount.district_id_fk == District.id
            ).join(
                SafetyDisciplineCountType,
                DistrictDisciplineCount.school_discipline_count_type_id_fk == SafetyDisciplineCountType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictDisciplineCount.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictDisciplineCount.district_id_fk == district_id)
                
            if discipline_count_type_id is not None:
                statement = statement.where(DistrictDisciplineCount.school_discipline_count_type_id_fk == discipline_count_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            count_data = []
            for count, count_type in result:
                count_type_data = count_type.dict()
                
                data = {
                    "id": count.id,
                    "district_id": count.district_id_fk,
                    "year": count.year,
                    "count": count.count,
                    "count_type": DisciplineCountTypeGet.model_validate(count_type_data)
                }
                count_data.append(DistrictDisciplineCountGet.model_validate(data))
                
            return count_data
        except Exception as e:
            logger.error(f"Error fetching district discipline count data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district discipline count data")
    
    def get_district_bullying(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_type_id: Optional[int] = None
    ) -> List[DistrictBullyingGet]:
        """Get district bullying data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictBullying,
                SafetyBullyingType
            ).join(
                District,
                DistrictBullying.district_id_fk == District.id
            ).join(
                SafetyBullyingType,
                DistrictBullying.school_bullying_type_id_fk == SafetyBullyingType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictBullying.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictBullying.district_id_fk == district_id)
                
            if bullying_type_id is not None:
                statement = statement.where(DistrictBullying.school_bullying_type_id_fk == bullying_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            bullying_data = []
            for bullying, bullying_type in result:
                bullying_type_data = bullying_type.dict()
                
                data = {
                    "id": bullying.id,
                    "district_id": bullying.district_id_fk,
                    "year": bullying.year,
                    "reported": bullying.reported,
                    "investigated_actual": bullying.investigated_actual,
                    "bullying_type": BullyingTypeGet.model_validate(bullying_type_data)
                }
                bullying_data.append(DistrictBullyingGet.model_validate(data))
                
            return bullying_data
        except Exception as e:
            logger.error(f"Error fetching district bullying data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district bullying data")
    
    def get_district_bullying_classifications(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_classification_type_id: Optional[int] = None
    ) -> List[DistrictBullyingClassificationGet]:
        """Get district bullying classification data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictBullyingClassification,
                SafetyBullyingClassificationType
            ).join(
                District,
                DistrictBullyingClassification.district_id_fk == District.id
            ).join(
                SafetyBullyingClassificationType,
                DistrictBullyingClassification.school_bullying_classification_type_id_fk == SafetyBullyingClassificationType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictBullyingClassification.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictBullyingClassification.district_id_fk == district_id)
                
            if bullying_classification_type_id is not None:
                statement = statement.where(DistrictBullyingClassification.school_bullying_classification_type_id_fk == bullying_classification_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            classification_data = []
            for classification, classification_type in result:
                classification_type_data = classification_type.dict()
                
                data = {
                    "id": classification.id,
                    "district_id": classification.district_id_fk,
                    "year": classification.year,
                    "count": classification.count,
                    "classification_type": BullyingClassificationTypeGet.model_validate(classification_type_data)
                }
                classification_data.append(DistrictBullyingClassificationGet.model_validate(data))
                
            return classification_data
        except Exception as e:
            logger.error(f"Error fetching district bullying classification data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district bullying classification data")
    
    def get_district_bullying_impacts(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        bullying_impact_type_id: Optional[int] = None
    ) -> List[DistrictBullyingImpactGet]:
        """Get district bullying impact data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictBullyingImpact,
                SafetyBullyingImpactType
            ).join(
                District,
                DistrictBullyingImpact.district_id_fk == District.id
            ).join(
                SafetyBullyingImpactType,
                DistrictBullyingImpact.school_bullying_impact_type_id_fk == SafetyBullyingImpactType.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictBullyingImpact.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictBullyingImpact.district_id_fk == district_id)
                
            if bullying_impact_type_id is not None:
                statement = statement.where(DistrictBullyingImpact.school_bullying_impact_type_id_fk == bullying_impact_type_id)
                
            # Execute query
            result = session.exec(statement)
            
            impact_data = []
            for impact, impact_type in result:
                impact_type_data = impact_type.dict()
                
                data = {
                    "id": impact.id,
                    "district_id": impact.district_id_fk,
                    "year": impact.year,
                    "count": impact.count,
                    "impact_type": BullyingImpactTypeGet.model_validate(impact_type_data)
                }
                impact_data.append(DistrictBullyingImpactGet.model_validate(data))
                
            return impact_data
        except Exception as e:
            logger.error(f"Error fetching district bullying impact data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district bullying impact data")
    
    def get_district_harassment(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        harassment_classification_id: Optional[int] = None
    ) -> List[DistrictHarassmentGet]:
        """Get district harassment data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictHarassment,
                SafetyHarassmentClassification
            ).join(
                District,
                DistrictHarassment.district_id_fk == District.id
            ).join(
                SafetyHarassmentClassification,
                DistrictHarassment.school_harassment_classification_id_fk == SafetyHarassmentClassification.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictHarassment.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictHarassment.district_id_fk == district_id)
                
            if harassment_classification_id is not None:
                statement = statement.where(DistrictHarassment.school_harassment_classification_id_fk == harassment_classification_id)
                
            # Execute query
            result = session.exec(statement)
            
            harassment_data = []
            for harassment, classification in result:
                classification_data = classification.dict()
                
                data = {
                    "id": harassment.id,
                    "district_id": harassment.district_id_fk,
                    "year": harassment.year,
                    "incident_count": harassment.incident_count,
                    "student_impact_count": harassment.student_impact_count,
                    "student_engaged_count": harassment.student_engaged_count,
                    "classification": HarassmentClassificationGet.model_validate(classification_data)
                }
                harassment_data.append(DistrictHarassmentGet.model_validate(data))
                
            return harassment_data
        except Exception as e:
            logger.error(f"Error fetching district harassment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district harassment data")
    
    def get_district_restraint(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[DistrictRestraintGet]:
        """Get district restraint data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictRestraint
            ).join(
                District,
                DistrictRestraint.district_id_fk == District.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictRestraint.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictRestraint.district_id_fk == district_id)
                
            # Execute query
            result = session.exec(statement)
            
            restraint_data = []
            for restraint in result:
                data = {
                    "id": restraint.id,
                    "district_id": restraint.district_id_fk,
                    "year": restraint.year,
                    "generated": restraint.generated,
                    "active_investigation": restraint.active_investigation,
                    "closed_investigation": restraint.closed_investigation,
                    "bodily_injury": restraint.bodily_injury,
                    "serious_injury": restraint.serious_injury
                }
                restraint_data.append(DistrictRestraintGet.model_validate(data))
                
            return restraint_data
        except Exception as e:
            logger.error(f"Error fetching district restraint data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district restraint data")
    
    def get_district_seclusion(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[DistrictSeclusionGet]:
        """Get district seclusion data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictSeclusion
            ).join(
                District,
                DistrictSeclusion.district_id_fk == District.id
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictSeclusion.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictSeclusion.district_id_fk == district_id)
                
            # Execute query
            result = session.exec(statement)
            
            seclusion_data = []
            for seclusion in result:
                data = {
                    "id": seclusion.id,
                    "district_id": seclusion.district_id_fk,
                    "year": seclusion.year,
                    "generated": seclusion.generated,
                    "active_investigation": seclusion.active_investigation,
                    "closed_investigation": seclusion.closed_investigation
                }
                seclusion_data.append(DistrictSeclusionGet.model_validate(data))
                
            return seclusion_data
        except Exception as e:
            logger.error(f"Error fetching district seclusion data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district seclusion data")

    # Enrollment methods
    def get_school_safety_enrollment(
        self, 
        session: Session, 
        year: Optional[int] = None,
        school_id: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[SchoolSafetyEnrollmentGet]:
        """Get school safety enrollment data with optional filters"""
        try:
            # Create base query
            statement = select(
                SchoolSafetyEnrollment
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(SchoolSafetyEnrollment.year == year)
                
            if school_id is not None:
                statement = statement.where(SchoolSafetyEnrollment.school_id_fk == school_id)
                
            # If district_id is provided, we need to join to the School table
            if district_id is not None:
                statement = (
                    select(SchoolSafetyEnrollment)
                    .join(School, SchoolSafetyEnrollment.school_id_fk == School.id)
                    .where(School.district_id_fk == district_id)
                )
                
                # Re-apply the other filters if they were provided
                if year is not None:
                    statement = statement.where(SchoolSafetyEnrollment.year == year)
                
                if school_id is not None:
                    statement = statement.where(SchoolSafetyEnrollment.school_id_fk == school_id)
                
            # Execute query
            result = session.exec(statement)
            
            enrollment_data = []
            for enrollment in result:
                data = {
                    "school_id": enrollment.school_id_fk,
                    "year": enrollment.year,
                    "total_enrollment": enrollment.total_enrollment
                }
                enrollment_data.append(SchoolSafetyEnrollmentGet.model_validate(data))
                
            return enrollment_data
        except Exception as e:
            logger.error(f"Error fetching school safety enrollment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch school safety enrollment data")
            
    def get_district_safety_enrollment(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None
    ) -> List[DistrictSafetyEnrollmentGet]:
        """Get district safety enrollment data with optional filters"""
        try:
            # Create base query
            statement = select(
                DistrictSafetyEnrollment
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(DistrictSafetyEnrollment.year == year)
                
            if district_id is not None:
                statement = statement.where(DistrictSafetyEnrollment.district_id_fk == district_id)
                
            # Execute query
            result = session.exec(statement)
            
            enrollment_data = []
            for enrollment in result:
                data = {
                    "district_id": enrollment.district_id_fk,
                    "year": enrollment.year,
                    "total_enrollment": enrollment.total_enrollment
                }
                enrollment_data.append(DistrictSafetyEnrollmentGet.model_validate(data))
                
            return enrollment_data
        except Exception as e:
            logger.error(f"Error fetching district safety enrollment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district safety enrollment data")
            
    def get_state_safety_enrollment(
        self, 
        session: Session, 
        year: Optional[int] = None
    ) -> List[StateSafetyEnrollmentGet]:
        """Get state safety enrollment data with optional filters"""
        try:
            # Create base query
            statement = select(
                StateSafetyEnrollment
            )
            
            # Apply filters
            if year is not None:
                statement = statement.where(StateSafetyEnrollment.year == year)
                
            # Execute query
            result = session.exec(statement)
            
            enrollment_data = []
            for enrollment in result:
                data = {
                    "year": enrollment.year,
                    "total_enrollment": enrollment.total_enrollment
                }
                enrollment_data.append(StateSafetyEnrollmentGet.model_validate(data))
                
            return enrollment_data
        except Exception as e:
            logger.error(f"Error fetching state safety enrollment data: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state safety enrollment data")


safety_service = SafetyService() 