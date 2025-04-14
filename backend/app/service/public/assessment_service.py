from sqlalchemy.orm import Session, selectinload
from sqlmodel import select, col, or_, and_
from typing import List, Optional, Dict, Any, Union
from fastapi import HTTPException
import logging

from app.schema.assessment_schema import AssessmentGet, AssessmentSubgroupGet, AssessmentSubjectGet
from app.model.assessment import AssessmentSubject, AssessmentSubgroup, AssessmentDistrict, AssessmentSchool, AssessmentState
from app.model.location import District, School, Grade

logger = logging.getLogger(__name__)

class AssessmentService:
    def get_assessment_subgroups(self, session: Session) -> List[AssessmentSubgroupGet]:
        """Get all assessment subgroups"""
        try:
            result = session.exec(select(AssessmentSubgroup).order_by(AssessmentSubgroup.name)).all()
            return [AssessmentSubgroupGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching assessment subgroups: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch assessment subgroups")
    
    def get_assessment_subjects(self, session: Session) -> List[AssessmentSubjectGet]:
        """Get all assessment subjects"""
        try:
            result = session.exec(select(AssessmentSubject).order_by(AssessmentSubject.name)).all()
            return [AssessmentSubjectGet.model_validate(r.dict()) for r in result]
        except Exception as e:
            logger.error(f"Error fetching assessment subjects: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch assessment subjects")
    
    def _apply_common_filters(self, statement, model, year=None, assessment_subgroup_id=None, 
                             assessment_subject_id=None, grade_id=None):
        """Apply common filters to assessment queries"""
        if year is not None:
            statement = statement.where(model.year == year)
            
        if assessment_subgroup_id is not None:
            statement = statement.where(model.assessment_subgroup_id_fk == assessment_subgroup_id)
            
        if assessment_subject_id is not None:
            statement = statement.where(model.assessment_subject_id_fk == assessment_subject_id)
            
        if grade_id is not None:
            if grade_id == 999:
                # Special case: grade_id 999 searches for NULL grade_id_fk
                statement = statement.where(model.grade_id_fk.is_(None))
            else:
                statement = statement.where(model.grade_id_fk == grade_id)
            
        return statement
    
    def _create_assessment_data(self, 
                               assessment_model: Union[AssessmentState, AssessmentDistrict, AssessmentSchool],
                               district_name: Optional[str] = None,
                               school_name: Optional[str] = None,
                               district_id: Optional[int] = None,
                               school_id: Optional[int] = None) -> Dict[str, Any]:
        """Create assessment data dictionary from assessment model"""
        return {
            "id": assessment_model.id,
            "year": assessment_model.year,
            "district_id": district_id,
            "school_id": school_id,
            "assessment_subgroup_id": assessment_model.assessment_subgroup_id_fk,
            "assessment_subject_id": assessment_model.assessment_subject_id_fk,
            "grade_id": assessment_model.grade_id_fk,
            "total_fay_students_low": assessment_model.total_fay_students_low,
            "total_fay_students_high": assessment_model.total_fay_students_high,
            "level_1_percentage": assessment_model.level_1_percentage,
            "level_1_percentage_exception": assessment_model.level_1_percentage_exception,
            "level_2_percentage": assessment_model.level_2_percentage,
            "level_2_percentage_exception": assessment_model.level_2_percentage_exception,
            "level_3_percentage": assessment_model.level_3_percentage,
            "level_3_percentage_exception": assessment_model.level_3_percentage_exception,
            "level_4_percentage": assessment_model.level_4_percentage,
            "level_4_percentage_exception": assessment_model.level_4_percentage_exception,
            "above_proficient_percentage": assessment_model.above_proficient_percentage,
            "above_proficient_percentage_exception": assessment_model.above_proficient_percentage_exception,
            "participate_percentage": assessment_model.participate_percentage,
            "mean_sgp": assessment_model.mean_sgp,
            "average_score": assessment_model.average_score,
            "district_name": district_name,
            "school_name": school_name
        }
    
    def get_state_assessments(
        self, 
        session: Session, 
        year: Optional[int] = None,
        assessment_subgroup_id: Optional[int] = None,
        assessment_subject_id: Optional[int] = None,
        grade_id: Optional[int] = None
    ) -> List[AssessmentGet]:
        """Get state level assessment data with optional filters"""
        try:
            # Create a query selecting the models
            statement = select(AssessmentState)
            
            # Apply common filters
            statement = self._apply_common_filters(
                statement, 
                AssessmentState, 
                year, 
                assessment_subgroup_id, 
                assessment_subject_id, 
                grade_id
            )
            
            result = session.exec(statement)
            
            assessments = []
            for state in result:
                assessment_data = self._create_assessment_data(state)
                assessments.append(AssessmentGet.model_validate(assessment_data))
                
            return assessments
        except Exception as e:
            logger.error(f"Error fetching state assessments: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch state assessment data")
    
    def get_district_assessments(
        self, 
        session: Session, 
        district_id: Optional[int] = None,
        year: Optional[int] = None,
        assessment_subgroup_id: Optional[int] = None,
        assessment_subject_id: Optional[int] = None,
        grade_id: Optional[int] = None
    ) -> List[AssessmentGet]:
        """Get district level assessment data with optional filters"""
        try:
            # Create a query selecting the models
            statement = select(
                AssessmentDistrict,
                District,
            ).join(
                District, 
                AssessmentDistrict.district_id_fk == District.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(
                statement, 
                AssessmentDistrict, 
                year, 
                assessment_subgroup_id, 
                assessment_subject_id, 
                grade_id
            )
            
            # Add district-specific filter
            if district_id is not None:
                statement = statement.where(AssessmentDistrict.district_id_fk == district_id)
            
            result = session.exec(statement)
            
            assessments = []
            for district_assmt, district in result:
                assessment_data = self._create_assessment_data(
                    district_assmt,
                    district_name=district.name,
                    district_id=district_assmt.district_id_fk
                )
                assessments.append(AssessmentGet.model_validate(assessment_data))
                
            return assessments
        except Exception as e:
            logger.error(f"Error fetching district assessments: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch district assessment data")
    
    def get_school_assessments(
        self, 
        session: Session, 
        school_id: Optional[int] = None,
        district_id: Optional[int] = None,
        year: Optional[int] = None,
        assessment_subgroup_id: Optional[int] = None,
        assessment_subject_id: Optional[int] = None,
        grade_id: Optional[int] = None
    ) -> List[AssessmentGet]:
        """Get school level assessment data with optional filters"""
        try:
            # Create a query selecting the models
            statement = select(
                AssessmentSchool,
                School,
                District
            ).join(
                School, 
                AssessmentSchool.school_id_fk == School.id
            ).join(
                District,
                School.district_id_fk == District.id
            )
            
            # Apply common filters
            statement = self._apply_common_filters(
                statement, 
                AssessmentSchool, 
                year, 
                assessment_subgroup_id, 
                assessment_subject_id, 
                grade_id
            )
            
            # Add school-specific filters
            if school_id is not None:
                statement = statement.where(AssessmentSchool.school_id_fk == school_id)
                
            if district_id is not None:
                # Filter by district through the School model
                statement = statement.where(School.district_id_fk == district_id)
            
            # Execute the query
            result = session.exec(statement)
            
            assessments = []
            for school_assmt, school, district in result:
                assessment_data = self._create_assessment_data(
                    school_assmt,
                    district_name=district.name,
                    school_name=school.name,
                    district_id=school.district_id_fk,
                    school_id=school_assmt.school_id_fk
                )
                assessments.append(AssessmentGet.model_validate(assessment_data))
                
            return assessments
        except Exception as e:
            logger.error(f"Error fetching school assessments: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch school assessment data")

assessment_service = AssessmentService() 