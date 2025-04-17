from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, delete
from fastapi import HTTPException
from uuid import UUID
import datetime
import sqlalchemy

from app.model.survey import (
    Survey, SurveyResponse, Answer, SurveySection, 
    Question, QuestionOption, AnswerItem
)
from app.model.survey_analysis import (
    SurveyAnalysis, SurveyAnalysisQuestion, 
    SurveyAnalysisQuestionTopicXref, SurveyAnalysisReportSegmentXref,
    SurveyQuestionTopic, SurveyReportSegment
)
from app.schema.survey_schema import (
    SurveyGet, SurveyResponseGet, SurveyCreate, SurveyUpdate,
    SurveyResponseCreate, SurveyResponseUpdate, QuestionGet, QuestionCreate, QuestionUpdate
)

class SurveyService:
    # --- READ OPERATIONS ---
    def get_survey(
        self,
        session: Session,
        survey_id: UUID
    ) -> SurveyGet:
        """
        Get a survey by ID.
        
        Args:
            session: Database session
            survey_id: ID of the survey to retrieve
            
        Returns:
            Survey details including sections and questions
        
        Raises:
            HTTPException: If the survey is not found
        """
        statement = select(Survey).where(Survey.id == survey_id)
        survey = session.exec(statement).first()
        
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
            
        return SurveyGet.from_orm(survey)
    
    def get_surveys(
        self,
        session: Session,
        active_only: bool = False
    ) -> List[SurveyGet]:
        """
        Get all surveys, optionally filtering to active surveys only.
        
        Args:
            session: Database session
            active_only: If True, only return active surveys
            
        Returns:
            List of surveys
        """
        statement = select(Survey)
        
        if active_only:
            statement = statement.where(Survey.is_active == True)
            
        # Order by creation date, newest first
        statement = statement.order_by(Survey.date_created.desc())
            
        surveys = session.exec(statement).all()
        return [SurveyGet.from_orm(survey) for survey in surveys]
    
    def get_survey_response(
        self,
        session: Session,
        response_id: UUID
    ) -> SurveyResponseGet:
        """
        Get a survey response by ID.
        
        Args:
            session: Database session
            response_id: ID of the survey response to retrieve
            
        Returns:
            Survey response details including answers
            
        Raises:
            HTTPException: If the survey response is not found
        """
        statement = select(SurveyResponse).where(SurveyResponse.id == response_id)
        response = session.exec(statement).first()
        
        if not response:
            raise HTTPException(status_code=404, detail=f"Survey response with ID {response_id} not found")
            
        return SurveyResponseGet.from_orm(response)
    
    def get_survey_responses(
        self,
        session: Session,
        survey_id: UUID,
        page: int = 1,
        page_size: int = 50,
        filter_params: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Get all responses for a specific survey with pagination and filtering.
        
        Args:
            session: Database session
            survey_id: ID of the survey to get responses for
            page: Page number (1-indexed)
            page_size: Number of items per page
            filter_params: Optional filter parameters
            
        Returns:
            Paginated list of survey responses
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        # Build the base query
        statement = select(SurveyResponse).where(SurveyResponse.survey_id == survey_id)
        
        # Apply filters if provided
        if filter_params:
            if filter_params.completed_only:
                statement = statement.where(SurveyResponse.is_complete == True)
            
            if filter_params.started_after:
                statement = statement.where(SurveyResponse.started_at >= filter_params.started_after)
                
            if filter_params.started_before:
                statement = statement.where(SurveyResponse.started_at <= filter_params.started_before)
                
            if filter_params.respondent_id:
                statement = statement.where(SurveyResponse.respondent_id == filter_params.respondent_id)
                
            if filter_params.search_term:
                # Search in metadata using JSONB containment
                # This assumes the metadata might contain the search term as a value
                # For more advanced text search, consider using PostgreSQL's full-text search capabilities
                search_term = f"%{filter_params.search_term}%"
                search_condition = sqlalchemy.text("metadata::text ILIKE :search_term").bindparams(search_term=search_term)
                statement = statement.where(search_condition)
        
        # Count total items for pagination
        count_statement = select(sqlalchemy.func.count()).select_from(statement.subquery())
        total_items = session.exec(count_statement).one()
        
        # Calculate pagination values
        total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        offset = (page - 1) * page_size
        
        # Order by start time, newest first and apply pagination
        statement = statement.order_by(SurveyResponse.started_at.desc())
        statement = statement.offset(offset).limit(page_size)
        
        # Execute query
        responses = session.exec(statement).all()
        
        # Convert to schema objects
        response_items = [SurveyResponseGet.from_orm(response) for response in responses]
        
        # Build the paginated response
        result = {
            "items": response_items,
            "total": total_items,
            "page": page,
            "page_size": page_size,
            "pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages
        }
        
        return result

    def get_question(
        self,
        session: Session,
        question_id: UUID
    ) -> QuestionGet:
        """
        Get a question by ID.
        
        Args:
            session: Database session
            question_id: ID of the question to retrieve
            
        Returns:
            Question details including options
        
        Raises:
            HTTPException: If the question is not found
        """
        statement = select(Question).where(Question.id == question_id)
        question = session.exec(statement).first()
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
            
        return QuestionGet.from_orm(question)
    
    def get_survey_questions(
        self,
        session: Session,
        survey_id: UUID
    ) -> List[QuestionGet]:
        """
        Get all questions for a specific survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey to get questions for
            
        Returns:
            List of questions
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        statement = select(Question).where(Question.survey_id == survey_id).order_by(Question.order_index)
        questions = session.exec(statement).all()
        
        return [QuestionGet.from_orm(question) for question in questions]

    # --- CREATE OPERATIONS ---
    def create_survey(
        self,
        session: Session,
        survey_data: SurveyCreate
    ) -> SurveyGet:
        """
        Create a new survey.
        
        Args:
            session: Database session
            survey_data: Data for creating the survey
            
        Returns:
            Newly created survey
        """
        # Create the survey
        survey = Survey(
            title=survey_data.title,
            description=survey_data.description,
            survey_start=survey_data.survey_start,
            survey_end=survey_data.survey_end,
            is_active=survey_data.is_active
        )
        session.add(survey)
        session.flush()  # Flush to get the ID
        
        # Create sections if provided
        if survey_data.sections:
            for section_data in survey_data.sections:
                section = SurveySection(
                    survey_id=survey.id,
                    title=section_data.title,
                    description=section_data.description,
                    order_index=section_data.order_index
                )
                session.add(section)
                session.flush()  # Flush to get the ID
                
                # Create questions for this section
                if section_data.questions:
                    for question_data in section_data.questions:
                        question = self._create_question(
                            session=session,
                            survey_id=survey.id,
                            section_id=section.id,
                            question_data=question_data
                        )
        
        # Create standalone questions if provided
        if survey_data.questions:
            for question_data in survey_data.questions:
                question = self._create_question(
                    session=session,
                    survey_id=survey.id,
                    section_id=None,
                    question_data=question_data
                )
        
        session.commit()
        
        # Refresh to get all relationships
        statement = select(Survey).where(Survey.id == survey.id)
        created_survey = session.exec(statement).first()
        
        return SurveyGet.from_orm(created_survey)
    
    def _create_question(
        self,
        session: Session,
        survey_id: UUID,
        section_id: Optional[UUID],
        question_data: Any
    ) -> Question:
        """
        Helper method to create a question and its options.
        
        Args:
            session: Database session
            survey_id: ID of the survey
            section_id: Optional ID of the section
            question_data: Question data
            
        Returns:
            Created question
        """
        question = Question(
            survey_id=survey_id,
            section_id=section_id or question_data.section_id,
            type_id=question_data.type_id,
            title=question_data.title,
            description=question_data.description,
            is_required=question_data.is_required,
            order_index=question_data.order_index,
            external_question_id=question_data.external_question_id,
            validation_rules=question_data.validation_rules,
            display_logic=question_data.display_logic,
            allow_multiple=question_data.allow_multiple,
            max_answers=question_data.max_answers
        )
        session.add(question)
        session.flush()  # Flush to get the ID
        
        # Create options if provided
        if question_data.options:
            for option_data in question_data.options:
                option = QuestionOption(
                    question_id=question.id,
                    text=option_data.text,
                    order_index=option_data.order_index,
                    is_other_option=option_data.is_other_option,
                    score=option_data.score,
                    row_label=option_data.row_label,
                    column_label=option_data.column_label
                )
                session.add(option)
        
        return question
    
    def create_survey_response(
        self,
        session: Session,
        response_data: SurveyResponseCreate
    ) -> SurveyResponseGet:
        """
        Create a new survey response.
        
        Args:
            session: Database session
            response_data: Data for creating the survey response
            
        Returns:
            Newly created survey response
            
        Raises:
            HTTPException: If the survey is not found
        """
        # Verify survey exists
        survey = session.exec(select(Survey).where(Survey.id == response_data.survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {response_data.survey_id} not found")
        
        # Create the response
        response = SurveyResponse(
            survey_id=response_data.survey_id,
            respondent_id=response_data.respondent_id,
            ip_address=response_data.ip_address,
            user_agent=response_data.user_agent,
            response_metadata=response_data.response_metadata,
            is_complete=False  # Always start as incomplete
        )
        session.add(response)
        session.flush()  # Flush to get the ID
        
        # Create answers if provided
        if response_data.answers:
            for answer_data in response_data.answers:
                answer = self._create_answer(
                    session=session, 
                    response_id=response.id,
                    answer_data=answer_data
                )
        
        session.commit()
        
        # Refresh to get all relationships
        statement = select(SurveyResponse).where(SurveyResponse.id == response.id)
        created_response = session.exec(statement).first()
        
        return SurveyResponseGet.from_orm(created_response)
    
    def _create_answer(
        self,
        session: Session,
        response_id: UUID,
        answer_data: Any
    ) -> Answer:
        """
        Helper method to create an answer and its items.
        
        Args:
            session: Database session
            response_id: ID of the response
            answer_data: Answer data
            
        Returns:
            Created answer
            
        Raises:
            HTTPException: If the question is not found
        """
        # Verify question exists
        question = session.exec(select(Question).where(Question.id == answer_data.question_id)).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {answer_data.question_id} not found")
        
        answer = Answer(
            response_id=response_id,
            question_id=answer_data.question_id,
            value=answer_data.value,
            selected_options=answer_data.selected_options,
            file_path=answer_data.file_path,
            answered_at=datetime.datetime.utcnow()
        )
        session.add(answer)
        session.flush()  # Flush to get the ID
        
        # Create items if provided
        if answer_data.items:
            for item_data in answer_data.items:
                # Verify option exists if provided
                if item_data.option_id:
                    option = session.exec(select(QuestionOption).where(QuestionOption.id == item_data.option_id)).first()
                    if not option:
                        raise HTTPException(status_code=404, detail=f"Option with ID {item_data.option_id} not found")
                
                item = AnswerItem(
                    answer_id=answer.id,
                    item_index=item_data.item_index,
                    value=item_data.value,
                    option_id=item_data.option_id,
                    row_identifier=item_data.row_identifier,
                    column_identifier=item_data.column_identifier
                )
                session.add(item)
        
        return answer

    def create_question(
        self,
        session: Session,
        survey_id: UUID,
        question_data: QuestionCreate
    ) -> QuestionGet:
        """
        Create a new question for a survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey to add the question to
            question_data: Data for creating the question
            
        Returns:
            Newly created question
            
        Raises:
            HTTPException: If the survey is not found
        """
        # First verify the survey exists
        survey_exists = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey_exists:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        # If section_id is provided, verify it exists and belongs to the survey
        if question_data.section_id:
            section = session.exec(
                select(SurveySection).where(
                    SurveySection.id == question_data.section_id,
                    SurveySection.survey_id == survey_id
                )
            ).first()
            
            if not section:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Section with ID {question_data.section_id} not found in survey {survey_id}"
                )
        
        # Create the question
        question = self._create_question(
            session=session,
            survey_id=survey_id,
            section_id=question_data.section_id,
            question_data=question_data
        )
        
        session.commit()
        
        # Refresh to get all relationships
        statement = select(Question).where(Question.id == question.id)
        created_question = session.exec(statement).first()
        
        return QuestionGet.from_orm(created_question)

    # --- UPDATE OPERATIONS ---
    def update_survey(
        self,
        session: Session,
        survey_id: UUID,
        survey_data: SurveyUpdate
    ) -> SurveyGet:
        """
        Update an existing survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey to update
            survey_data: Data for updating the survey
            
        Returns:
            Updated survey
            
        Raises:
            HTTPException: If the survey is not found
        """
        survey = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        # Update fields if provided
        if survey_data.title is not None:
            survey.title = survey_data.title
        if survey_data.description is not None:
            survey.description = survey_data.description
        if survey_data.survey_start is not None:
            survey.survey_start = survey_data.survey_start
        if survey_data.survey_end is not None:
            survey.survey_end = survey_data.survey_end
        if survey_data.is_active is not None:
            survey.is_active = survey_data.is_active
        
        session.add(survey)
        session.commit()
        
        # Refresh to get updated data
        session.refresh(survey)
        
        return SurveyGet.from_orm(survey)
    
    def update_survey_response(
        self,
        session: Session,
        response_id: UUID,
        response_data: SurveyResponseUpdate
    ) -> SurveyResponseGet:
        """
        Update an existing survey response.
        
        Args:
            session: Database session
            response_id: ID of the response to update
            response_data: Data for updating the response
            
        Returns:
            Updated survey response
            
        Raises:
            HTTPException: If the survey response is not found
        """
        response = session.exec(select(SurveyResponse).where(SurveyResponse.id == response_id)).first()
        if not response:
            raise HTTPException(status_code=404, detail=f"Survey response with ID {response_id} not found")
        
        # Update fields if provided
        if response_data.completed_at is not None:
            response.completed_at = response_data.completed_at
        if response_data.is_complete is not None:
            response.is_complete = response_data.is_complete
        
        # Add new answers if provided
        if response_data.answers:
            for answer_data in response_data.answers:
                # Check if answer already exists for this question
                existing_answer = session.exec(
                    select(Answer).where(
                        Answer.response_id == response_id,
                        Answer.question_id == answer_data.question_id
                    )
                ).first()
                
                if existing_answer:
                    # Delete the existing answer and its items
                    session.exec(delete(AnswerItem).where(AnswerItem.answer_id == existing_answer.id))
                    session.exec(delete(Answer).where(Answer.id == existing_answer.id))
                
                # Create a new answer
                self._create_answer(
                    session=session,
                    response_id=response_id,
                    answer_data=answer_data
                )
        
        session.add(response)
        session.commit()
        
        # Refresh to get updated data with relationships
        statement = select(SurveyResponse).where(SurveyResponse.id == response_id)
        updated_response = session.exec(statement).first()
        
        return SurveyResponseGet.from_orm(updated_response)

    def update_question(
        self,
        session: Session,
        question_id: UUID,
        question_data: QuestionUpdate
    ) -> QuestionGet:
        """
        Update an existing question.
        
        Args:
            session: Database session
            question_id: ID of the question to update
            question_data: Data for updating the question
            
        Returns:
            Updated question
            
        Raises:
            HTTPException: If the question is not found
        """
        # Verify question exists
        question = session.exec(select(Question).where(Question.id == question_id)).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        
        # Update question attributes (only if provided)
        if question_data.title is not None:
            question.title = question_data.title
        if question_data.description is not None:
            question.description = question_data.description
        if question_data.is_required is not None:
            question.is_required = question_data.is_required
        if question_data.order_index is not None:
            question.order_index = question_data.order_index
        if question_data.type_id is not None:
            question.type_id = question_data.type_id
        if question_data.external_question_id is not None:
            question.external_question_id = question_data.external_question_id
        if question_data.validation_rules is not None:
            question.validation_rules = question_data.validation_rules
        if question_data.display_logic is not None:
            question.display_logic = question_data.display_logic
        if question_data.allow_multiple is not None:
            question.allow_multiple = question_data.allow_multiple
        if question_data.max_answers is not None:
            question.max_answers = question_data.max_answers
        
        # If section_id is provided, verify it exists and belongs to the survey
        if question_data.section_id is not None:
            if question_data.section_id:  # Not None and not empty UUID
                section = session.exec(
                    select(SurveySection).where(
                        SurveySection.id == question_data.section_id,
                        SurveySection.survey_id == question.survey_id
                    )
                ).first()
                
                if not section:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Section with ID {question_data.section_id} not found in survey {question.survey_id}"
                    )
                
            question.section_id = question_data.section_id
        
        # Update options if provided
        if question_data.options is not None:
            # Delete existing options
            session.exec(delete(QuestionOption).where(QuestionOption.question_id == question_id))
            
            # Create new options
            for option_data in question_data.options:
                option = QuestionOption(
                    question_id=question.id,
                    text=option_data.text,
                    order_index=option_data.order_index,
                    is_other_option=option_data.is_other_option,
                    score=option_data.score,
                    row_label=option_data.row_label,
                    column_label=option_data.column_label
                )
                session.add(option)
        
        session.add(question)
        session.commit()
        
        # Refresh to get updated relationships
        session.refresh(question)
        
        return QuestionGet.from_orm(question)

    # --- DELETE OPERATIONS ---
    def delete_survey(
        self,
        session: Session,
        survey_id: UUID
    ) -> bool:
        """
        Delete a survey.
        
        Args:
            session: Database session
            survey_id: ID of the survey to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the survey is not found
        """
        survey = session.exec(select(Survey).where(Survey.id == survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
        
        # First, get all questions for this survey
        questions = session.exec(select(Question).where(Question.survey_id == survey_id)).all()
        question_ids = [q.id for q in questions]
        
        # Get all survey analyses for this survey
        analyses = session.exec(select(SurveyAnalysis).where(SurveyAnalysis.survey_id == survey_id)).all()
        
        # For each analysis, delete its questions and cross-references
        for analysis in analyses:
            # Get analysis questions for this analysis
            analysis_questions = session.exec(
                select(SurveyAnalysisQuestion).where(
                    SurveyAnalysisQuestion.survey_analysis_id == analysis.id
                )
            ).all()
            
            # For each analysis question, delete cross-references
            for analysis_question in analysis_questions:
                # Delete topic cross-references
                topic_xrefs = session.exec(
                    select(SurveyAnalysisQuestionTopicXref).where(
                        SurveyAnalysisQuestionTopicXref.survey_analysis_question_id == analysis_question.id
                    )
                ).all()
                for topic_xref in topic_xrefs:
                    session.delete(topic_xref)
                
                # Delete segment cross-references
                segment_xrefs = session.exec(
                    select(SurveyAnalysisReportSegmentXref).where(
                        SurveyAnalysisReportSegmentXref.survey_analysis_question_id == analysis_question.id
                    )
                ).all()
                for segment_xref in segment_xrefs:
                    session.delete(segment_xref)
            
            # Flush to ensure cross-references are deleted
            session.flush()
            
            # Delete analysis questions
            for analysis_question in analysis_questions:
                session.delete(analysis_question)
            
            # Flush to ensure analysis questions are deleted
            session.flush()
            
            # Delete the analysis itself
            session.delete(analysis)
            
        # Flush to ensure analyses are deleted
        session.flush()
        
        # Delete any remaining analysis questions that reference these questions
        analysis_questions = session.exec(
            select(SurveyAnalysisQuestion).where(
                SurveyAnalysisQuestion.question_id.in_(question_ids)
            )
        ).all()
        
        # For each analysis question, first delete all cross-reference records
        for analysis_question in analysis_questions:
            # Delete topic cross-references
            topic_xrefs = session.exec(
                select(SurveyAnalysisQuestionTopicXref).where(
                    SurveyAnalysisQuestionTopicXref.survey_analysis_question_id == analysis_question.id
                )
            ).all()
            for topic_xref in topic_xrefs:
                session.delete(topic_xref)
            
            # Delete segment cross-references
            segment_xrefs = session.exec(
                select(SurveyAnalysisReportSegmentXref).where(
                    SurveyAnalysisReportSegmentXref.survey_analysis_question_id == analysis_question.id
                )
            ).all()
            for segment_xref in segment_xrefs:
                session.delete(segment_xref)
        
        # Flush to ensure cross-references are deleted
        session.flush()
        
        # Now delete the analysis questions
        for analysis_question in analysis_questions:
            session.delete(analysis_question)
        
        # Flush to ensure analysis questions are deleted
        session.flush()
        
        # Delete topics and report segments for this survey
        topics = session.exec(select(SurveyQuestionTopic).where(SurveyQuestionTopic.survey_id == survey_id)).all()
        for topic in topics:
            session.delete(topic)
            
        segments = session.exec(select(SurveyReportSegment).where(SurveyReportSegment.survey_id == survey_id)).all()
        for segment in segments:
            session.delete(segment)
            
        # Flush to ensure topics and segments are deleted
        session.flush()
        
        # For each question, delete its options
        for question in questions:
            # Delete the question's options first
            options = session.exec(select(QuestionOption).where(QuestionOption.question_id == question.id)).all()
            for option in options:
                session.delete(option)
            
            # Flush to ensure options are deleted
            session.flush()
            
            # Now delete the question
            session.delete(question)
        
        # Flush to ensure questions are deleted
        session.flush()
        
        # Now delete the survey (will cascade to sections and responses)
        session.delete(survey)
        session.commit()
        
        return True
    
    def delete_survey_response(
        self,
        session: Session,
        response_id: UUID
    ) -> bool:
        """
        Delete a survey response.
        
        Args:
            session: Database session
            response_id: ID of the response to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the survey response is not found
        """
        response = session.exec(select(SurveyResponse).where(SurveyResponse.id == response_id)).first()
        if not response:
            raise HTTPException(status_code=404, detail=f"Survey response with ID {response_id} not found")
        
        # Delete the response (cascades to answers, etc. due to DB constraints)
        session.delete(response)
        session.commit()
        
        return True

    def delete_question(
        self,
        session: Session,
        question_id: UUID
    ) -> bool:
        """
        Delete a question.
        
        Args:
            session: Database session
            question_id: ID of the question to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            HTTPException: If the question is not found
        """
        question = session.exec(select(Question).where(Question.id == question_id)).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found")
        
        # First delete any survey analysis questions that reference this question
        analysis_questions = session.exec(
            select(SurveyAnalysisQuestion).where(SurveyAnalysisQuestion.question_id == question_id)
        ).all()
        
        # For each analysis question, first delete all cross-reference records
        for analysis_question in analysis_questions:
            # Delete topic cross-references
            topic_xrefs = session.exec(
                select(SurveyAnalysisQuestionTopicXref).where(
                    SurveyAnalysisQuestionTopicXref.survey_analysis_question_id == analysis_question.id
                )
            ).all()
            
            for topic_xref in topic_xrefs:
                session.delete(topic_xref)
            
            # Delete segment cross-references
            segment_xrefs = session.exec(
                select(SurveyAnalysisReportSegmentXref).where(
                    SurveyAnalysisReportSegmentXref.survey_analysis_question_id == analysis_question.id
                )
            ).all()
            
            for segment_xref in segment_xrefs:
                session.delete(segment_xref)
        
        # Flush to ensure cross-references are deleted
        session.flush()
        
        # Now delete the analysis questions
        for analysis_question in analysis_questions:
            session.delete(analysis_question)
        
        # Flush to ensure analysis questions are deleted
        session.flush()
        
        # Now delete all options for this question
        options = session.exec(select(QuestionOption).where(QuestionOption.question_id == question_id)).all()
        for option in options:
            session.delete(option)
        
        # Flush to ensure options are deleted
        session.flush()
        
        # Now delete the question
        session.delete(question)
        session.commit()
        
        return True

    # --- BULK OPERATIONS ---
    def create_bulk_survey_responses(
        self,
        session: Session,
        bulk_data: Any
    ) -> List[SurveyResponseGet]:
        """
        Create multiple survey responses in a single transaction.
        
        Args:
            session: Database session
            bulk_data: Data containing survey_id and list of responses to create
            
        Returns:
            List of newly created survey responses
            
        Raises:
            HTTPException: If the survey is not found or validation fails
        """
        # Verify survey exists
        survey = session.exec(select(Survey).where(Survey.id == bulk_data.survey_id)).first()
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey with ID {bulk_data.survey_id} not found")
        
        # Collect the created responses
        created_responses = []
        
        # Process each response in the bulk upload
        for response_data in bulk_data.responses:
            # Ensure the survey_id is consistent
            if response_data.survey_id != bulk_data.survey_id:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Survey ID mismatch. Expected {bulk_data.survey_id}, got {response_data.survey_id}"
                )
            
            # Create response
            response = SurveyResponse(
                survey_id=response_data.survey_id,
                respondent_id=response_data.respondent_id,
                ip_address=response_data.ip_address,
                user_agent=response_data.user_agent,
                response_metadata=response_data.response_metadata,
                is_complete=response_data.is_complete,
                completed_at=response_data.completed_at
            )
            session.add(response)
            session.flush()  # Flush to get the ID
            
            # Create answers if provided
            if response_data.answers:
                for answer_data in response_data.answers:
                    self._create_answer(
                        session=session, 
                        response_id=response.id,
                        answer_data=answer_data
                    )
            
            # Add to our collection
            created_responses.append(response)
        
        # Commit all changes at once
        session.commit()
        
        # Return formatted response objects
        return [SurveyResponseGet.from_orm(response) for response in created_responses]

survey_service = SurveyService() 