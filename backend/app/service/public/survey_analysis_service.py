from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, delete
from fastapi import HTTPException
from uuid import UUID
import datetime
import sqlalchemy

from app.model.survey import Survey, Question
from app.model.survey_analysis import (
    ChartType, SurveyAnalysis, SurveyAnalysisQuestion,
    SurveyQuestionTopic, SurveyAnalysisQuestionTopicXref,
    SurveyReportSegment, SurveyAnalysisReportSegmentXref,
    SurveyAnalysisFilter, SurveyAnalysisFilterCriteria
)
from app.schema.survey_analysis_schema import (
    SurveyAnalysisGet, SurveyAnalysisCreate, SurveyAnalysisUpdate,
    SurveyAnalysisQuestionGet, SurveyAnalysisQuestionCreate, SurveyAnalysisQuestionUpdate,
    SurveyQuestionTopicGet, SurveyQuestionTopicCreate, SurveyQuestionTopicUpdate,
    SurveyReportSegmentGet, SurveyReportSegmentCreate, SurveyReportSegmentUpdate,
    ChartTypeGet, SurveyAnalysisFilterGet, SurveyAnalysisFilterCreate, 
    SurveyAnalysisFilterUpdate, SurveyAnalysisFilterCriteriaGet, SurveyAnalysisFilterCriteriaCreate
)

class SurveyAnalysisService:
    # --- CHART TYPE OPERATIONS ---
    def get_chart_types(
        self,
        session: Session
    ) -> List[ChartTypeGet]:
        """
        Get all available chart types.
        
        Args:
            session: Database session
            
        Returns:
            List of all chart types
        """
        statement = select(ChartType).order_by(ChartType.id)
        chart_types = session.exec(statement).all()
        return [ChartTypeGet.from_orm(chart_type) for chart_type in chart_types]
    
    def get_chart_type(
        self,
        session: Session,
        chart_type_id: int
    ) -> ChartTypeGet:
        """
        Get a specific chart type by ID.
        
        Args:
            session: Database session
            chart_type_id: ID of the chart type
            
        Returns:
            Chart type details
            
        Raises:
            HTTPException: If the chart type is not found
        """
        statement = select(ChartType).where(ChartType.id == chart_type_id)
        chart_type = session.exec(statement).first()
        
        if not chart_type:
            raise HTTPException(status_code=404, detail=f"Chart type with ID {chart_type_id} not found")
            
        return ChartTypeGet.from_orm(chart_type)

    # --- SURVEY ANALYSIS OPERATIONS ---
    def get_survey_analyses(
        self,
        session: Session,
        survey_id: UUID
    ) -> List[SurveyAnalysisGet]:
        """
        Get all analyses for a specific survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey
            
        Returns:
            List of survey analyses
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        statement = select(SurveyAnalysis).where(SurveyAnalysis.survey_id == survey_id)
        analyses = session.exec(statement).all()
        
        return [SurveyAnalysisGet.from_orm(analysis) for analysis in analyses]
    
    def get_survey_analysis(
        self,
        session: Session,
        analysis_id: UUID
    ) -> SurveyAnalysisGet:
        """
        Get a specific survey analysis by ID.
        
        Args:
            session: Database session
            analysis_id: ID of the analysis
            
        Returns:
            Survey analysis details
            
        Raises:
            HTTPException: If the analysis is not found
        """
        statement = select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_id)
        analysis = session.exec(statement).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Survey analysis with ID {analysis_id} not found")
            
        return SurveyAnalysisGet.from_orm(analysis)
    
    def create_survey_analysis(
        self,
        session: Session,
        analysis_data: SurveyAnalysisCreate
    ) -> SurveyAnalysisGet:
        """
        Create a new survey analysis.
        
        Args:
            session: Database session
            analysis_data: Data for creating the analysis
            
        Returns:
            Newly created survey analysis
            
        Raises:
            HTTPException: If the survey is not found
        """
        # Verify survey exists
        survey = session.exec(select(Survey).where(Survey.id == analysis_data.survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {analysis_data.survey_id} not found")
        
        # Create the analysis
        analysis = SurveyAnalysis(
            survey_id=analysis_data.survey_id,
            title=analysis_data.title,
            description=analysis_data.description
        )
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        
        return SurveyAnalysisGet.from_orm(analysis)
    
    def update_survey_analysis(
        self,
        session: Session,
        analysis_id: UUID,
        analysis_data: SurveyAnalysisUpdate
    ) -> SurveyAnalysisGet:
        """
        Update an existing survey analysis.
        
        Args:
            session: Database session
            analysis_id: ID of the analysis to update
            analysis_data: Data for updating the analysis
            
        Returns:
            Updated survey analysis
            
        Raises:
            HTTPException: If the analysis is not found
        """
        analysis = session.exec(select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_id)).first()
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Survey analysis with ID {analysis_id} not found")
        
        # Update fields if provided
        if analysis_data.title is not None:
            analysis.title = analysis_data.title
        if analysis_data.description is not None:
            analysis.description = analysis_data.description
        
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        
        return SurveyAnalysisGet.from_orm(analysis)
    
    def delete_survey_analysis(
        self,
        session: Session,
        analysis_id: UUID
    ) -> bool:
        """
        Delete a survey analysis.
        
        Args:
            session: Database session
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the analysis is not found
        """
        analysis = session.exec(select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_id)).first()
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Survey analysis with ID {analysis_id} not found")
        
        # Get all SurveyAnalysisQuestion records associated with this analysis
        analysis_questions = session.exec(
            select(SurveyAnalysisQuestion).where(SurveyAnalysisQuestion.survey_analysis_id == analysis_id)
        ).all()
        
        # For each analysis question, first delete all cross-reference records
        for question in analysis_questions:
            # Delete topic cross-references
            topic_xrefs = session.exec(
                select(SurveyAnalysisQuestionTopicXref).where(
                    SurveyAnalysisQuestionTopicXref.survey_analysis_question_id == question.id
                )
            ).all()
            
            for topic_xref in topic_xrefs:
                session.delete(topic_xref)
            
            # Delete segment cross-references
            segment_xrefs = session.exec(
                select(SurveyAnalysisReportSegmentXref).where(
                    SurveyAnalysisReportSegmentXref.survey_analysis_question_id == question.id
                )
            ).all()
            
            for segment_xref in segment_xrefs:
                session.delete(segment_xref)
        
        # Flush to ensure cross-references are deleted
        session.flush()
        
        # Now delete the analysis questions
        for question in analysis_questions:
            session.delete(question)
        
        # Flush to ensure questions are deleted before deleting the analysis itself
        session.flush()
        
        # Now delete the analysis
        session.delete(analysis)
        session.commit()
        
        return True

    # --- SURVEY ANALYSIS QUESTION OPERATIONS ---
    def get_survey_analysis_questions(
        self,
        session: Session,
        analysis_id: UUID
    ) -> List[SurveyAnalysisQuestionGet]:
        """
        Get all analysis questions for a specific analysis.
        
        Args:
            session: Database session
            analysis_id: ID of the analysis
            
        Returns:
            List of survey analysis questions
            
        Raises:
            HTTPException: If the analysis is not found
        """
        # First verify the analysis exists
        analysis_exists = session.exec(select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_id)).first()
        if not analysis_exists:
            raise HTTPException(status_code=404, detail=f"Survey analysis with ID {analysis_id} not found")
        
        statement = select(SurveyAnalysisQuestion).where(SurveyAnalysisQuestion.survey_analysis_id == analysis_id)
        analysis_questions = session.exec(statement).all()
        
        return [SurveyAnalysisQuestionGet.from_orm(q) for q in analysis_questions]
    
    def get_survey_analysis_question(
        self,
        session: Session,
        analysis_question_id: UUID
    ) -> SurveyAnalysisQuestionGet:
        """
        Get a specific survey analysis question by ID.
        
        Args:
            session: Database session
            analysis_question_id: ID of the analysis question
            
        Returns:
            Survey analysis question details
            
        Raises:
            HTTPException: If the analysis question is not found
        """
        statement = select(SurveyAnalysisQuestion).where(SurveyAnalysisQuestion.id == analysis_question_id)
        analysis_question = session.exec(statement).first()
        
        if not analysis_question:
            raise HTTPException(status_code=404, 
                               detail=f"Survey analysis question with ID {analysis_question_id} not found")
            
        return SurveyAnalysisQuestionGet.from_orm(analysis_question)
    
    def create_survey_analysis_question(
        self,
        session: Session,
        question_data: SurveyAnalysisQuestionCreate
    ) -> SurveyAnalysisQuestionGet:
        """
        Create a new survey analysis question.
        
        Args:
            session: Database session
            question_data: Data for creating the analysis question
            
        Returns:
            Newly created survey analysis question
            
        Raises:
            HTTPException: If the analysis, question, or chart type is not found
        """
        # Verify analysis exists
        analysis = session.exec(
            select(SurveyAnalysis).where(SurveyAnalysis.id == question_data.survey_analysis_id)
        ).first()
        if not analysis:
            raise HTTPException(
                status_code=404, 
                detail=f"Survey analysis with ID {question_data.survey_analysis_id} not found"
            )
        
        # Verify question exists
        question = session.exec(select(Question).where(Question.id == question_data.question_id)).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_data.question_id} not found")
        
        # Verify question belongs to the same survey as the analysis
        if question.survey_id != analysis.survey_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Question {question_data.question_id} does not belong to the same survey as the analysis"
            )
        
        # Verify chart type exists
        chart_type = session.exec(select(ChartType).where(ChartType.id == question_data.chart_type_id)).first()
        if not chart_type:
            raise HTTPException(
                status_code=404, 
                detail=f"Chart type with ID {question_data.chart_type_id} not found"
            )
        
        # Create the analysis question
        analysis_question = SurveyAnalysisQuestion(
            survey_analysis_id=question_data.survey_analysis_id,
            question_id=question_data.question_id,
            chart_type_id=question_data.chart_type_id,
            sort_by_value=question_data.sort_by_value,
            is_demographic=question_data.is_demographic
        )
        session.add(analysis_question)
        session.flush()  # Flush to get the ID
        
        # Add topic associations if provided
        if question_data.topic_ids:
            for topic_id in question_data.topic_ids:
                # Verify topic exists and belongs to the same survey
                topic = session.exec(
                    select(SurveyQuestionTopic).where(
                        SurveyQuestionTopic.id == topic_id,
                        SurveyQuestionTopic.survey_id == analysis.survey_id
                    )
                ).first()
                
                if not topic:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Topic with ID {topic_id} not found or not part of the same survey"
                    )
                
                topic_xref = SurveyAnalysisQuestionTopicXref(
                    survey_question_topic_id=topic_id,
                    survey_analysis_question_id=analysis_question.id
                )
                session.add(topic_xref)
        
        # Add report segment associations if provided
        if question_data.report_segment_ids:
            for segment_id in question_data.report_segment_ids:
                # Verify segment exists and belongs to the same survey
                segment = session.exec(
                    select(SurveyReportSegment).where(
                        SurveyReportSegment.id == segment_id,
                        SurveyReportSegment.survey_id == analysis.survey_id
                    )
                ).first()
                
                if not segment:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Report segment with ID {segment_id} not found or not part of the same survey"
                    )
                
                segment_xref = SurveyAnalysisReportSegmentXref(
                    survey_report_segment_id=segment_id,
                    survey_analysis_question_id=analysis_question.id
                )
                session.add(segment_xref)
        
        session.commit()
        session.refresh(analysis_question)
        
        return SurveyAnalysisQuestionGet.from_orm(analysis_question)
    
    def update_survey_analysis_question(
        self,
        session: Session,
        analysis_question_id: UUID,
        question_data: SurveyAnalysisQuestionUpdate
    ) -> SurveyAnalysisQuestionGet:
        """
        Update an existing survey analysis question.
        
        Args:
            session: Database session
            analysis_question_id: ID of the analysis question to update
            question_data: Data for updating the analysis question
            
        Returns:
            Updated survey analysis question
            
        Raises:
            HTTPException: If the analysis question, chart type, topic, or segment is not found
        """
        def load_analysis_question():
            """Load analysis question with all necessary relationships."""
            statement = (
                select(SurveyAnalysisQuestion)
                .where(SurveyAnalysisQuestion.id == analysis_question_id)
                .options(
                    sqlalchemy.orm.joinedload(SurveyAnalysisQuestion.chart_type),
                    sqlalchemy.orm.joinedload(SurveyAnalysisQuestion.question),
                    sqlalchemy.orm.joinedload(SurveyAnalysisQuestion.topic_xrefs)
                    .joinedload(SurveyAnalysisQuestionTopicXref.survey_question_topic),
                    sqlalchemy.orm.joinedload(SurveyAnalysisQuestion.segment_xrefs)
                    .joinedload(SurveyAnalysisReportSegmentXref.survey_report_segment)
                )
            )
            return session.exec(statement).first()
        
        # Load the analysis question
        analysis_question = load_analysis_question()
        if not analysis_question:
            raise HTTPException(
                status_code=404, 
                detail=f"Survey analysis question with ID {analysis_question_id} not found"
            )
        
        # Get the analysis to check survey_id for relationships
        analysis = session.exec(
            select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_question.survey_analysis_id)
        ).first()
        
        # Update basic fields
        if question_data.chart_type_id is not None:
            chart_type = session.exec(select(ChartType).where(ChartType.id == question_data.chart_type_id)).first()
            if not chart_type:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Chart type with ID {question_data.chart_type_id} not found"
                )
            analysis_question.chart_type_id = question_data.chart_type_id
        
        if question_data.sort_by_value is not None:
            analysis_question.sort_by_value = question_data.sort_by_value
            
        if question_data.is_demographic is not None:
            analysis_question.is_demographic = question_data.is_demographic
        
        # Update relationships
        def update_xref_relationships(
            xref_type: type,
            entity_type: type,
            xref_field: str,
            id_list: Optional[List[UUID]],
            entity_id_field: str
        ):
            """Generic function to update cross-reference relationships."""
            # Delete existing xrefs
            session.exec(
                delete(xref_type).where(
                    getattr(xref_type, "survey_analysis_question_id") == analysis_question_id
                )
            )
            session.commit()

            # Clear relationship list
            setattr(analysis_question, xref_field, [])

            # Add new relationships if provided
            if id_list is not None:
                for entity_id in id_list:
                    # Verify entity exists and belongs to the same survey
                    entity = session.exec(
                        select(entity_type).where(
                            getattr(entity_type, "id") == entity_id,
                            entity_type.survey_id == analysis.survey_id
                        )
                    ).first()

                    if not entity:
                        raise HTTPException(
                            status_code=404,
                            detail=f"{entity_type.__name__} with ID {entity_id} not found or not part of the same survey"
                        )

                    # Create and add new xref
                    xref = xref_type(
                        **{
                            entity_id_field: entity_id,
                            "survey_analysis_question_id": analysis_question.id
                        }
                    )
                    getattr(analysis_question, xref_field).append(xref)
        
        # Update topics
        update_xref_relationships(
            xref_type=SurveyAnalysisQuestionTopicXref,
            entity_type=SurveyQuestionTopic,
            xref_field="topic_xrefs",
            id_list=question_data.topic_ids,
            entity_id_field="survey_question_topic_id"
        )
        
        # Update segments
        update_xref_relationships(
            xref_type=SurveyAnalysisReportSegmentXref,
            entity_type=SurveyReportSegment,
            xref_field="segment_xrefs",
            id_list=question_data.report_segment_ids,
            entity_id_field="survey_report_segment_id"
        )
        
        # Save changes
        session.add(analysis_question)
        session.commit()
        
        # Return refreshed question
        return SurveyAnalysisQuestionGet.from_orm(load_analysis_question())
    
    def delete_survey_analysis_question(
        self,
        session: Session,
        analysis_question_id: UUID
    ) -> bool:
        """
        Delete a survey analysis question.
        
        Args:
            session: Database session
            analysis_question_id: ID of the analysis question to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the analysis question is not found
        """
        analysis_question = session.exec(
            select(SurveyAnalysisQuestion).where(SurveyAnalysisQuestion.id == analysis_question_id)
        ).first()
        
        if not analysis_question:
            raise HTTPException(
                status_code=404, 
                detail=f"Survey analysis question with ID {analysis_question_id} not found"
            )
        
        # This will cascade to delete all xrefs due to DB constraints
        session.delete(analysis_question)
        session.commit()
        
        return True

    # --- SURVEY QUESTION TOPIC OPERATIONS ---
    def get_survey_question_topics(
        self,
        session: Session,
        survey_id: UUID
    ) -> List[SurveyQuestionTopicGet]:
        """
        Get all question topics for a specific survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey
            
        Returns:
            List of survey question topics
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        statement = select(SurveyQuestionTopic).where(SurveyQuestionTopic.survey_id == survey_id)
        topics = session.exec(statement).all()
        
        return [SurveyQuestionTopicGet.from_orm(topic) for topic in topics]
    
    def get_survey_question_topic(
        self,
        session: Session,
        topic_id: UUID
    ) -> SurveyQuestionTopicGet:
        """
        Get a specific survey question topic by ID.
        
        Args:
            session: Database session
            topic_id: ID of the topic
            
        Returns:
            Survey question topic details
            
        Raises:
            HTTPException: If the topic is not found
        """
        statement = select(SurveyQuestionTopic).where(SurveyQuestionTopic.id == topic_id)
        topic = session.exec(statement).first()
        
        if not topic:
            raise HTTPException(status_code=404, detail=f"Survey question topic with ID {topic_id} not found")
            
        return SurveyQuestionTopicGet.from_orm(topic)
    
    def create_survey_question_topic(
        self,
        session: Session,
        topic_data: SurveyQuestionTopicCreate
    ) -> SurveyQuestionTopicGet:
        """
        Create a new survey question topic.
        
        Args:
            session: Database session
            topic_data: Data for creating the topic
            
        Returns:
            Newly created survey question topic
            
        Raises:
            HTTPException: If the survey is not found
        """
        # Verify survey exists
        survey = session.exec(select(Survey).where(Survey.id == topic_data.survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {topic_data.survey_id} not found")
        
        # Create the topic
        topic = SurveyQuestionTopic(
            survey_id=topic_data.survey_id,
            name=topic_data.name
        )
        session.add(topic)
        session.commit()
        session.refresh(topic)
        
        return SurveyQuestionTopicGet.from_orm(topic)
    
    def update_survey_question_topic(
        self,
        session: Session,
        topic_id: UUID,
        topic_data: SurveyQuestionTopicUpdate
    ) -> SurveyQuestionTopicGet:
        """
        Update an existing survey question topic.
        
        Args:
            session: Database session
            topic_id: ID of the topic to update
            topic_data: Data for updating the topic
            
        Returns:
            Updated survey question topic
            
        Raises:
            HTTPException: If the topic is not found
        """
        topic = session.exec(select(SurveyQuestionTopic).where(SurveyQuestionTopic.id == topic_id)).first()
        if not topic:
            raise HTTPException(status_code=404, detail=f"Survey question topic with ID {topic_id} not found")
        
        # Update fields if provided
        if topic_data.name is not None:
            topic.name = topic_data.name
        
        session.add(topic)
        session.commit()
        session.refresh(topic)
        
        return SurveyQuestionTopicGet.from_orm(topic)
    
    def delete_survey_question_topic(
        self,
        session: Session,
        topic_id: UUID
    ) -> bool:
        """
        Delete a survey question topic.
        
        Args:
            session: Database session
            topic_id: ID of the topic to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the topic is not found
        """
        topic = session.exec(select(SurveyQuestionTopic).where(SurveyQuestionTopic.id == topic_id)).first()
        if not topic:
            raise HTTPException(status_code=404, detail=f"Survey question topic with ID {topic_id} not found")
        
        # This will cascade to delete all xrefs due to DB constraints
        session.delete(topic)
        session.commit()
        
        return True
    
    # --- SURVEY REPORT SEGMENT OPERATIONS ---
    def get_survey_report_segments(
        self,
        session: Session,
        survey_id: UUID
    ) -> List[SurveyReportSegmentGet]:
        """
        Get all report segments for a specific survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey
            
        Returns:
            List of survey report segments
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        statement = select(SurveyReportSegment).where(SurveyReportSegment.survey_id == survey_id)
        segments = session.exec(statement).all()
        
        return [SurveyReportSegmentGet.from_orm(segment) for segment in segments]
    
    def get_survey_report_segment(
        self,
        session: Session,
        segment_id: UUID
    ) -> SurveyReportSegmentGet:
        """
        Get a specific survey report segment by ID.
        
        Args:
            session: Database session
            segment_id: ID of the segment
            
        Returns:
            Survey report segment details
            
        Raises:
            HTTPException: If the segment is not found
        """
        statement = select(SurveyReportSegment).where(SurveyReportSegment.id == segment_id)
        segment = session.exec(statement).first()
        
        if not segment:
            raise HTTPException(status_code=404, detail=f"Survey report segment with ID {segment_id} not found")
            
        return SurveyReportSegmentGet.from_orm(segment)
    
    def create_survey_report_segment(
        self,
        session: Session,
        segment_data: SurveyReportSegmentCreate
    ) -> SurveyReportSegmentGet:
        """
        Create a new survey report segment.
        
        Args:
            session: Database session
            segment_data: Data for creating the segment
            
        Returns:
            Newly created survey report segment
            
        Raises:
            HTTPException: If the survey is not found
        """
        # Verify survey exists
        survey = session.exec(select(Survey).where(Survey.id == segment_data.survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {segment_data.survey_id} not found")
        
        # Create the segment
        segment = SurveyReportSegment(
            survey_id=segment_data.survey_id,
            name=segment_data.name
        )
        session.add(segment)
        session.commit()
        session.refresh(segment)
        
        return SurveyReportSegmentGet.from_orm(segment)
    
    def update_survey_report_segment(
        self,
        session: Session,
        segment_id: UUID,
        segment_data: SurveyReportSegmentUpdate
    ) -> SurveyReportSegmentGet:
        """
        Update an existing survey report segment.
        
        Args:
            session: Database session
            segment_id: ID of the segment to update
            segment_data: Data for updating the segment
            
        Returns:
            Updated survey report segment
            
        Raises:
            HTTPException: If the segment is not found
        """
        segment = session.exec(select(SurveyReportSegment).where(SurveyReportSegment.id == segment_id)).first()
        if not segment:
            raise HTTPException(status_code=404, detail=f"Survey report segment with ID {segment_id} not found")
        
        # Update fields if provided
        if segment_data.name is not None:
            segment.name = segment_data.name
        
        session.add(segment)
        session.commit()
        session.refresh(segment)
        
        return SurveyReportSegmentGet.from_orm(segment)
    
    def delete_survey_report_segment(
        self,
        session: Session,
        segment_id: UUID
    ) -> bool:
        """
        Delete a survey report segment.
        
        Args:
            session: Database session
            segment_id: ID of the segment to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the segment is not found
        """
        segment = session.exec(select(SurveyReportSegment).where(SurveyReportSegment.id == segment_id)).first()
        if not segment:
            raise HTTPException(status_code=404, detail=f"Survey report segment with ID {segment_id} not found")
        
        # This will cascade to delete all xrefs due to DB constraints
        session.delete(segment)
        session.commit()
        
        return True

    # --- SURVEY ANALYSIS FILTER OPERATIONS ---
    def get_survey_analysis_filters(
        self,
        session: Session,
        analysis_id: UUID
    ) -> List[SurveyAnalysisFilterGet]:
        """
        Get all filters for a specific survey analysis.
        
        Args:
            session: Database session
            analysis_id: ID of the survey analysis
            
        Returns:
            List of survey analysis filters
            
        Raises:
            HTTPException: If the survey analysis is not found
        """
        # First verify the analysis exists
        analysis_exists = session.exec(select(SurveyAnalysis).where(SurveyAnalysis.id == analysis_id)).first()
        if not analysis_exists:
            raise HTTPException(status_code=404, detail=f"Survey analysis with ID {analysis_id} not found")
        
        statement = select(SurveyAnalysisFilter).where(SurveyAnalysisFilter.survey_analysis_id == analysis_id)
        filters = session.exec(statement).all()
        
        return [SurveyAnalysisFilterGet.from_orm(f) for f in filters]
    
    def get_survey_analysis_filter(
        self,
        session: Session,
        filter_id: UUID
    ) -> SurveyAnalysisFilterGet:
        """
        Get a specific survey analysis filter by ID.
        
        Args:
            session: Database session
            filter_id: ID of the filter
            
        Returns:
            Survey analysis filter details
            
        Raises:
            HTTPException: If the filter is not found
        """
        statement = select(SurveyAnalysisFilter).where(SurveyAnalysisFilter.id == filter_id)
        filter_obj = session.exec(statement).first()
        
        if not filter_obj:
            raise HTTPException(status_code=404, detail=f"Survey analysis filter with ID {filter_id} not found")
            
        return SurveyAnalysisFilterGet.from_orm(filter_obj)
    
    def create_survey_analysis_filter(
        self,
        session: Session,
        filter_data: SurveyAnalysisFilterCreate
    ) -> SurveyAnalysisFilterGet:
        """
        Create a new survey analysis filter.
        
        Args:
            session: Database session
            filter_data: Data for creating the filter
            
        Returns:
            Newly created survey analysis filter
            
        Raises:
            HTTPException: If the analysis or question is not found
        """
        # Verify analysis exists
        analysis = session.exec(
            select(SurveyAnalysis).where(SurveyAnalysis.id == filter_data.survey_analysis_id)
        ).first()
        if not analysis:
            raise HTTPException(
                status_code=404, 
                detail=f"Survey analysis with ID {filter_data.survey_analysis_id} not found"
            )
        
        # Verify analysis question exists and belongs to the same analysis
        analysis_question = session.exec(
            select(SurveyAnalysisQuestion).where(
                SurveyAnalysisQuestion.id == filter_data.survey_analysis_question_id,
                SurveyAnalysisQuestion.survey_analysis_id == filter_data.survey_analysis_id
            )
        ).first()
        if not analysis_question:
            raise HTTPException(
                status_code=404, 
                detail=f"Analysis question with ID {filter_data.survey_analysis_question_id} not found or not part of this analysis"
            )
        
        # Create the filter
        filter_obj = SurveyAnalysisFilter(
            survey_analysis_id=filter_data.survey_analysis_id,
            survey_analysis_question_id=filter_data.survey_analysis_question_id
        )
        session.add(filter_obj)
        session.flush()  # Flush to get the ID
        
        # Add criteria if provided
        if filter_data.criteria:
            for criterion_data in filter_data.criteria:
                criterion = SurveyAnalysisFilterCriteria(
                    survey_analysis_filter_id=filter_obj.id,
                    value=criterion_data.value
                )
                session.add(criterion)
        
        session.commit()
        session.refresh(filter_obj)
        
        return SurveyAnalysisFilterGet.from_orm(filter_obj)
    
    def update_survey_analysis_filter(
        self,
        session: Session,
        filter_id: UUID,
        filter_data: SurveyAnalysisFilterUpdate
    ) -> SurveyAnalysisFilterGet:
        """
        Update an existing survey analysis filter.
        
        Args:
            session: Database session
            filter_id: ID of the filter to update
            filter_data: Data for updating the filter
            
        Returns:
            Updated survey analysis filter
            
        Raises:
            HTTPException: If the filter is not found
        """
        filter_obj = session.exec(select(SurveyAnalysisFilter).where(SurveyAnalysisFilter.id == filter_id)).first()
        if not filter_obj:
            raise HTTPException(status_code=404, detail=f"Survey analysis filter with ID {filter_id} not found")
        
        # Update criteria if provided
        if filter_data.criteria is not None:
            # Delete existing criteria
            session.exec(
                delete(SurveyAnalysisFilterCriteria).where(
                    SurveyAnalysisFilterCriteria.survey_analysis_filter_id == filter_id
                )
            )
            
            # Add new criteria
            for criterion_data in filter_data.criteria:
                criterion = SurveyAnalysisFilterCriteria(
                    survey_analysis_filter_id=filter_id,
                    value=criterion_data.value
                )
                session.add(criterion)
        
        session.commit()
        session.refresh(filter_obj)
        
        return SurveyAnalysisFilterGet.from_orm(filter_obj)
    
    def delete_survey_analysis_filter(
        self,
        session: Session,
        filter_id: UUID
    ) -> bool:
        """
        Delete a survey analysis filter.
        
        Args:
            session: Database session
            filter_id: ID of the filter to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the filter is not found
        """
        filter_obj = session.exec(select(SurveyAnalysisFilter).where(SurveyAnalysisFilter.id == filter_id)).first()
        if not filter_obj:
            raise HTTPException(status_code=404, detail=f"Survey analysis filter with ID {filter_id} not found")
        
        # This will cascade to delete all criteria due to DB constraints
        session.delete(filter_obj)
        session.commit()
        
        return True

survey_analysis_service = SurveyAnalysisService() 