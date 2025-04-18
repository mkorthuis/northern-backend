from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.v1.deps import SessionDep
from app.schema.survey_schema import (
    SurveyGet, SurveyResponseGet, SurveyCreate, SurveyUpdate,
    SurveyResponseCreate, SurveyResponseUpdate,
    QuestionGet, QuestionCreate, QuestionUpdate,
    BulkSurveyResponseCreate, PaginationParams, SurveyResponseFilter,
    PaginatedSurveyResponses
)
from app.service.public.survey_service import survey_service

router = APIRouter()

# ----- SURVEY ENDPOINTS -----

@router.post("/", 
    response_model=SurveyGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create survey",
    description="Creates a new survey with sections and questions",
    response_description="Newly created survey")
def create_survey(
    survey_data: SurveyCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey with sections and questions.
    
    The request body should contain all necessary information for creating the survey.
    
    Returns the newly created survey with all relationships.
    """
    return survey_service.create_survey(
        session=session, 
        survey_data=survey_data
    )

@router.get("/{survey_id}", 
    response_model=SurveyGet,
    summary="Get survey details",
    description="Retrieves a survey by its ID, including sections and questions",
    response_description="Survey details")
def get_survey(
    survey_id: UUID = Path(..., description="The ID of the survey to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey by its ID.
    
    The response includes all survey information including sections and questions.
    
    Parameters:
    - **survey_id**: UUID of the survey to retrieve
    
    Returns the survey details including sections and questions.
    """
    return survey_service.get_survey(
        session=session, 
        survey_id=survey_id
    )

@router.get("/", 
    response_model=List[SurveyGet],
    summary="Get surveys",
    description="Retrieves a list of surveys, optionally filtered to active surveys only",
    response_description="List of surveys")
def get_surveys(
    session: SessionDep = SessionDep,
    active_only: bool = Query(False, description="If true, only return active surveys")
):
    """
    Get a list of surveys, optionally filtered to active surveys only.
    
    Parameters:
    - **active_only**: Optional flag to only return active surveys
    
    Returns a list of surveys ordered by creation date (newest first).
    """
    return survey_service.get_surveys(
        session=session, 
        active_only=active_only
    )

@router.put("/{survey_id}", 
    response_model=SurveyGet,
    summary="Update survey",
    description="Updates an existing survey's basic properties",
    response_description="Updated survey")
def update_survey(
    survey_data: SurveyUpdate,
    survey_id: UUID = Path(..., description="The ID of the survey to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey's basic properties.
    
    Note that this endpoint only updates the survey's main properties,
    not its sections or questions.
    
    Parameters:
    - **survey_id**: UUID of the survey to update
    
    Returns the updated survey.
    """
    return survey_service.update_survey(
        session=session, 
        survey_id=survey_id,
        survey_data=survey_data
    )

@router.delete("/{survey_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete survey",
    description="Deletes a survey and all its related data")
def delete_survey(
    survey_id: UUID = Path(..., description="The ID of the survey to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey and all its related data.
    
    This operation cannot be undone. All sections, questions, and responses
    associated with this survey will also be deleted due to cascading deletes.
    
    Parameters:
    - **survey_id**: UUID of the survey to delete
    """
    survey_service.delete_survey(
        session=session, 
        survey_id=survey_id
    )

# ----- SURVEY RESPONSE ENDPOINTS -----

@router.post("/response", 
    response_model=SurveyResponseGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create survey response",
    description="Creates a new response to a survey",
    response_description="Newly created survey response")
def create_survey_response(
    response_data: SurveyResponseCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new response to a survey.
    
    The request body should contain the survey ID, optional respondent information,
    and any initial answers to questions.
    
    Returns the newly created survey response.
    """
    return survey_service.create_survey_response(
        session=session, 
        response_data=response_data
    )

@router.get("/response/{response_id}", 
    response_model=SurveyResponseGet,
    summary="Get survey response",
    description="Retrieves a survey response by its ID, including all answers",
    response_description="Survey response details")
def get_survey_response(
    response_id: UUID = Path(..., description="The ID of the survey response to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey response by its ID.
    
    The response includes all answer data.
    
    Parameters:
    - **response_id**: UUID of the survey response to retrieve
    
    Returns the survey response details including all answers.
    """
    return survey_service.get_survey_response(
        session=session, 
        response_id=response_id
    )

@router.put("/response/{response_id}", 
    response_model=SurveyResponseGet,
    summary="Update survey response",
    description="Updates an existing survey response, adding or modifying answers",
    response_description="Updated survey response")
def update_survey_response(
    response_data: SurveyResponseUpdate,
    response_id: UUID = Path(..., description="The ID of the survey response to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey response, adding or modifying answers.
    
    This can be used to:
    - Mark a response as complete
    - Add new answers
    - Update existing answers (by providing new answers for the same questions)
    
    Parameters:
    - **response_id**: UUID of the survey response to update
    
    Returns the updated survey response with all answers.
    """
    return survey_service.update_survey_response(
        session=session, 
        response_id=response_id,
        response_data=response_data
    )

@router.delete("/response/{response_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete survey response",
    description="Deletes a survey response and all its answers")
def delete_survey_response(
    response_id: UUID = Path(..., description="The ID of the survey response to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey response and all its answers.
    
    This operation cannot be undone. All answers associated with this response
    will also be deleted due to cascading deletes.
    
    Parameters:
    - **response_id**: UUID of the survey response to delete
    """
    survey_service.delete_survey_response(
        session=session, 
        response_id=response_id
    )

@router.delete("/{survey_id}/responses", 
    status_code=status.HTTP_200_OK,
    summary="Delete all survey responses",
    description="Deletes all responses for a specific survey",
    response_description="Count of deleted responses")
def delete_all_survey_responses(
    survey_id: UUID = Path(..., description="The ID of the survey to delete all responses for"),
    session: SessionDep = SessionDep
):
    """
    Delete all responses for a specific survey.
    
    This operation cannot be undone. All responses and their associated answers
    will be deleted due to cascading deletes.
    
    Parameters:
    - **survey_id**: UUID of the survey to delete responses for
    
    Returns a count of how many responses were deleted.
    """
    return survey_service.delete_all_survey_responses(
        session=session, 
        survey_id=survey_id
    )

@router.get("/{survey_id}/responses", 
    response_model=PaginatedSurveyResponses,
    summary="Get survey responses",
    description="Retrieves all responses for a specific survey with pagination and filtering options",
    response_description="Paginated list of survey responses")
def get_survey_responses(
    survey_id: UUID = Path(..., description="The ID of the survey to get responses for"),
    session: SessionDep = SessionDep,
    pagination: PaginationParams = Depends(),
    filters: SurveyResponseFilter = Depends()
):
    """
    Get responses for a specific survey with pagination and filtering options.
    
    Parameters:
    - **survey_id**: UUID of the survey to get responses for
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100000)
    - **completed_only**: If true, only return completed responses
    - **started_after**: Filter responses started after this datetime
    - **started_before**: Filter responses started before this datetime
    - **respondent_id**: Filter by specific respondent
    - **search_term**: Search in response metadata
    
    Returns a paginated list of survey responses ordered by start time (newest first).
    """
    return survey_service.get_survey_responses(
        session=session, 
        survey_id=survey_id,
        page=pagination.page,
        page_size=pagination.page_size,
        filter_params=filters
    )

@router.post("/response/bulk", 
    response_model=List[SurveyResponseGet],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create survey responses",
    description="Creates multiple responses to a survey in a single request",
    response_description="List of newly created survey responses")
def create_bulk_survey_responses(
    bulk_data: BulkSurveyResponseCreate,
    session: SessionDep = SessionDep
):
    """
    Create multiple responses to a survey in a single request.
    
    This endpoint allows for efficiently uploading multiple survey responses at once.
    All responses must be for the same survey (specified by survey_id).
    
    The request body should contain:
    - survey_id: The ID of the survey these responses are for
    - responses: A list of response objects with their answers
    - batch_metadata: Optional metadata for the entire batch
    
    Returns a list of the newly created survey responses.
    """
    return survey_service.create_bulk_survey_responses(
        session=session, 
        bulk_data=bulk_data
    )

# ----- QUESTION ENDPOINTS -----

@router.post("/{survey_id}/questions", 
    response_model=QuestionGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create question",
    description="Creates a new question for a survey",
    response_description="Newly created question")
def create_question(
    question_data: QuestionCreate,
    survey_id: UUID = Path(..., description="The ID of the survey to add the question to"),
    session: SessionDep = SessionDep
):
    """
    Create a new question for a survey.
    
    The request body should contain all necessary information for creating the question,
    including options if applicable.
    
    Parameters:
    - **survey_id**: UUID of the survey to add the question to
    
    Returns the newly created question with all relationships.
    """
    return survey_service.create_question(
        session=session, 
        survey_id=survey_id,
        question_data=question_data
    )

@router.get("/questions/{question_id}", 
    response_model=QuestionGet,
    summary="Get question details",
    description="Retrieves a question by its ID, including options",
    response_description="Question details")
def get_question(
    question_id: UUID = Path(..., description="The ID of the question to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific question by its ID.
    
    The response includes all question information including options.
    
    Parameters:
    - **question_id**: UUID of the question to retrieve
    
    Returns the question details including options.
    """
    return survey_service.get_question(
        session=session, 
        question_id=question_id
    )

@router.get("/{survey_id}/questions", 
    response_model=List[QuestionGet],
    summary="Get survey questions",
    description="Retrieves all questions for a specific survey",
    response_description="List of questions")
def get_survey_questions(
    survey_id: UUID = Path(..., description="The ID of the survey to get questions for"),
    session: SessionDep = SessionDep
):
    """
    Get all questions for a specific survey.
    
    Parameters:
    - **survey_id**: UUID of the survey to get questions for
    
    Returns a list of questions ordered by their order index.
    """
    return survey_service.get_survey_questions(
        session=session, 
        survey_id=survey_id
    )

@router.put("/questions/{question_id}", 
    response_model=QuestionGet,
    summary="Update question",
    description="Updates an existing question's properties and options",
    response_description="Updated question")
def update_question(
    question_data: QuestionUpdate,
    question_id: UUID = Path(..., description="The ID of the question to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing question's properties and options.
    
    The request body should contain the information you want to update.
    All fields are optional.
    
    Parameters:
    - **question_id**: UUID of the question to update
    
    Returns the updated question with all relationships.
    """
    return survey_service.update_question(
        session=session, 
        question_id=question_id,
        question_data=question_data
    )

@router.delete("/questions/{question_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete question",
    description="Deletes a question and all its options")
def delete_question(
    question_id: UUID = Path(..., description="The ID of the question to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a question and all its options.
    
    This operation cannot be undone. All options and answers associated with this
    question will also be deleted due to cascading deletes.
    
    Parameters:
    - **question_id**: UUID of the question to delete
    """
    survey_service.delete_question(
        session=session, 
        question_id=question_id
    ) 