from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.v1.deps import SessionDep
from app.schema.survey_analysis_schema import (
    ChartTypeGet,
    SurveyAnalysisGet, SurveyAnalysisCreate, SurveyAnalysisUpdate,
    SurveyAnalysisQuestionGet, SurveyAnalysisQuestionCreate, SurveyAnalysisQuestionUpdate,
    SurveyQuestionTopicGet, SurveyQuestionTopicCreate, SurveyQuestionTopicUpdate,
    SurveyReportSegmentGet, SurveyReportSegmentCreate, SurveyReportSegmentUpdate,
    SurveyAnalysisFilterGet, SurveyAnalysisFilterCreate, SurveyAnalysisFilterUpdate
)
from app.service.public.survey_analysis_service import survey_analysis_service

router = APIRouter()

# ----- CHART TYPE ENDPOINTS -----

@router.get("/chart-types", 
    response_model=List[ChartTypeGet],
    summary="Get chart types",
    description="Retrieves all available chart types",
    response_description="List of chart types")
def get_chart_types(
    session: SessionDep = SessionDep
):
    """
    Get all available chart types.
    
    Returns a list of chart types that can be used for survey analysis visualizations.
    """
    return survey_analysis_service.get_chart_types(session=session)

@router.get("/chart-types/{chart_type_id}", 
    response_model=ChartTypeGet,
    summary="Get chart type",
    description="Retrieves a specific chart type by ID",
    response_description="Chart type details")
def get_chart_type(
    chart_type_id: int = Path(..., description="The ID of the chart type to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific chart type by its ID.
    
    Parameters:
    - **chart_type_id**: ID of the chart type to retrieve
    
    Returns the chart type details.
    """
    return survey_analysis_service.get_chart_type(
        session=session, 
        chart_type_id=chart_type_id
    )

# ----- SURVEY ANALYSIS ENDPOINTS -----

@router.get("/{survey_id}", 
    response_model=List[SurveyAnalysisGet],
    summary="Get survey analyses",
    description="Retrieves all analyses for a specific survey",
    response_description="List of survey analyses")
def get_survey_analyses(
    survey_id: UUID = Path(..., description="The ID of the survey to get analyses for"),
    session: SessionDep = SessionDep
):
    """
    Get all analyses for a specific survey.
    
    Parameters:
    - **survey_id**: UUID of the survey to get analyses for
    
    Returns a list of survey analyses.
    """
    return survey_analysis_service.get_survey_analyses(
        session=session, 
        survey_id=survey_id
    )

@router.get("/analyses/{analysis_id}", 
    response_model=SurveyAnalysisGet,
    summary="Get survey analysis",
    description="Retrieves a specific survey analysis by ID",
    response_description="Survey analysis details")
def get_survey_analysis(
    analysis_id: UUID = Path(..., description="The ID of the analysis to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey analysis by its ID.
    
    Parameters:
    - **analysis_id**: UUID of the analysis to retrieve
    
    Returns the survey analysis details.
    """
    return survey_analysis_service.get_survey_analysis(
        session=session, 
        analysis_id=analysis_id
    )

@router.post("/analyses", 
    response_model=SurveyAnalysisGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create survey analysis",
    description="Creates a new survey analysis",
    response_description="Newly created survey analysis")
def create_survey_analysis(
    analysis_data: SurveyAnalysisCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey analysis.
    
    The request body should contain the survey ID, title, and optional description.
    
    Returns the newly created survey analysis.
    """
    return survey_analysis_service.create_survey_analysis(
        session=session, 
        analysis_data=analysis_data
    )

@router.put("/analyses/{analysis_id}", 
    response_model=SurveyAnalysisGet,
    summary="Update survey analysis",
    description="Updates an existing survey analysis",
    response_description="Updated survey analysis")
def update_survey_analysis(
    analysis_data: SurveyAnalysisUpdate,
    analysis_id: UUID = Path(..., description="The ID of the analysis to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey analysis.
    
    Parameters:
    - **analysis_id**: UUID of the analysis to update
    
    Returns the updated survey analysis.
    """
    return survey_analysis_service.update_survey_analysis(
        session=session, 
        analysis_id=analysis_id,
        analysis_data=analysis_data
    )

@router.delete("/analyses/{analysis_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete survey analysis",
    description="Deletes a survey analysis and all its related data")
def delete_survey_analysis(
    analysis_id: UUID = Path(..., description="The ID of the analysis to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey analysis and all its related data.
    
    This operation cannot be undone. All analysis questions and associations
    will also be deleted due to cascading deletes.
    
    Parameters:
    - **analysis_id**: UUID of the analysis to delete
    """
    survey_analysis_service.delete_survey_analysis(
        session=session, 
        analysis_id=analysis_id
    )

# ----- SURVEY ANALYSIS QUESTION ENDPOINTS -----

@router.get("/analyses/{analysis_id}/questions", 
    response_model=List[SurveyAnalysisQuestionGet],
    summary="Get analysis questions",
    description="Retrieves all questions for a specific survey analysis",
    response_description="List of analysis questions")
def get_survey_analysis_questions(
    analysis_id: UUID = Path(..., description="The ID of the analysis to get questions for"),
    session: SessionDep = SessionDep
):
    """
    Get all questions for a specific survey analysis.
    
    Parameters:
    - **analysis_id**: UUID of the analysis to get questions for
    
    Returns a list of analysis questions.
    """
    return survey_analysis_service.get_survey_analysis_questions(
        session=session, 
        analysis_id=analysis_id
    )

@router.get("/analysis-questions/{analysis_question_id}", 
    response_model=SurveyAnalysisQuestionGet,
    summary="Get analysis question",
    description="Retrieves a specific survey analysis question by ID",
    response_description="Analysis question details")
def get_survey_analysis_question(
    analysis_question_id: UUID = Path(..., description="The ID of the analysis question to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey analysis question by its ID.
    
    Parameters:
    - **analysis_question_id**: UUID of the analysis question to retrieve
    
    Returns the analysis question details.
    """
    return survey_analysis_service.get_survey_analysis_question(
        session=session, 
        analysis_question_id=analysis_question_id
    )

@router.post("/analysis-questions", 
    response_model=SurveyAnalysisQuestionGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create analysis question",
    description="Creates a new survey analysis question",
    response_description="Newly created analysis question")
def create_survey_analysis_question(
    question_data: SurveyAnalysisQuestionCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey analysis question.
    
    The request body should contain:
    - survey_analysis_id: The ID of the analysis this question belongs to
    - question_id: The ID of the survey question being analyzed
    - chart_type_id: The type of chart to use for visualization
    - sort_by_value: Whether to sort the chart by value (default: false)
    - topic_ids: Optional list of topic IDs to associate with this analysis question
    - report_segment_ids: Optional list of report segment IDs to associate with this analysis question
    
    Returns the newly created analysis question.
    """
    return survey_analysis_service.create_survey_analysis_question(
        session=session, 
        question_data=question_data
    )

@router.put("/analysis-questions/{analysis_question_id}", 
    response_model=SurveyAnalysisQuestionGet,
    summary="Update analysis question",
    description="Updates an existing survey analysis question",
    response_description="Updated analysis question")
def update_survey_analysis_question(
    question_data: SurveyAnalysisQuestionUpdate,
    analysis_question_id: UUID = Path(..., description="The ID of the analysis question to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey analysis question.
    
    Parameters:
    - **analysis_question_id**: UUID of the analysis question to update
    
    Returns the updated analysis question.
    """
    return survey_analysis_service.update_survey_analysis_question(
        session=session, 
        analysis_question_id=analysis_question_id,
        question_data=question_data
    )

@router.delete("/analysis-questions/{analysis_question_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete analysis question",
    description="Deletes a survey analysis question and all its associations")
def delete_survey_analysis_question(
    analysis_question_id: UUID = Path(..., description="The ID of the analysis question to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey analysis question and all its associations.
    
    This operation cannot be undone. All topic and report segment associations
    will also be deleted due to cascading deletes.
    
    Parameters:
    - **analysis_question_id**: UUID of the analysis question to delete
    """
    survey_analysis_service.delete_survey_analysis_question(
        session=session, 
        analysis_question_id=analysis_question_id
    )

# ----- SURVEY QUESTION TOPIC ENDPOINTS -----

@router.get("/{survey_id}/topics", 
    response_model=List[SurveyQuestionTopicGet],
    summary="Get survey question topics",
    description="Retrieves all question topics for a specific survey",
    response_description="List of question topics")
def get_survey_question_topics(
    survey_id: UUID = Path(..., description="The ID of the survey to get topics for"),
    session: SessionDep = SessionDep
):
    """
    Get all question topics for a specific survey.
    
    Parameters:
    - **survey_id**: UUID of the survey to get topics for
    
    Returns a list of question topics.
    """
    return survey_analysis_service.get_survey_question_topics(
        session=session, 
        survey_id=survey_id
    )

@router.get("/topics/{topic_id}", 
    response_model=SurveyQuestionTopicGet,
    summary="Get question topic",
    description="Retrieves a specific survey question topic by ID",
    response_description="Question topic details")
def get_survey_question_topic(
    topic_id: UUID = Path(..., description="The ID of the topic to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey question topic by its ID.
    
    Parameters:
    - **topic_id**: UUID of the topic to retrieve
    
    Returns the question topic details.
    """
    return survey_analysis_service.get_survey_question_topic(
        session=session, 
        topic_id=topic_id
    )

@router.post("/topics", 
    response_model=SurveyQuestionTopicGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create question topic",
    description="Creates a new survey question topic",
    response_description="Newly created question topic")
def create_survey_question_topic(
    topic_data: SurveyQuestionTopicCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey question topic.
    
    The request body should contain:
    - survey_id: The ID of the survey this topic belongs to
    - name: The name of the topic
    
    Returns the newly created question topic.
    """
    return survey_analysis_service.create_survey_question_topic(
        session=session, 
        topic_data=topic_data
    )

@router.put("/topics/{topic_id}", 
    response_model=SurveyQuestionTopicGet,
    summary="Update question topic",
    description="Updates an existing survey question topic",
    response_description="Updated question topic")
def update_survey_question_topic(
    topic_data: SurveyQuestionTopicUpdate,
    topic_id: UUID = Path(..., description="The ID of the topic to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey question topic.
    
    Parameters:
    - **topic_id**: UUID of the topic to update
    
    Returns the updated question topic.
    """
    return survey_analysis_service.update_survey_question_topic(
        session=session, 
        topic_id=topic_id,
        topic_data=topic_data
    )

@router.delete("/topics/{topic_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete question topic",
    description="Deletes a survey question topic and all its associations")
def delete_survey_question_topic(
    topic_id: UUID = Path(..., description="The ID of the topic to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey question topic and all its associations.
    
    This operation cannot be undone. All associations with analysis questions
    will also be deleted due to cascading deletes.
    
    Parameters:
    - **topic_id**: UUID of the topic to delete
    """
    survey_analysis_service.delete_survey_question_topic(
        session=session, 
        topic_id=topic_id
    )

# ----- SURVEY REPORT SEGMENT ENDPOINTS -----

@router.get("/{survey_id}/segments", 
    response_model=List[SurveyReportSegmentGet],
    summary="Get survey report segments",
    description="Retrieves all report segments for a specific survey",
    response_description="List of report segments")
def get_survey_report_segments(
    survey_id: UUID = Path(..., description="The ID of the survey to get segments for"),
    session: SessionDep = SessionDep
):
    """
    Get all report segments for a specific survey.
    
    Parameters:
    - **survey_id**: UUID of the survey to get segments for
    
    Returns a list of report segments.
    """
    return survey_analysis_service.get_survey_report_segments(
        session=session, 
        survey_id=survey_id
    )

@router.get("/segments/{segment_id}", 
    response_model=SurveyReportSegmentGet,
    summary="Get report segment",
    description="Retrieves a specific survey report segment by ID",
    response_description="Report segment details")
def get_survey_report_segment(
    segment_id: UUID = Path(..., description="The ID of the segment to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey report segment by its ID.
    
    Parameters:
    - **segment_id**: UUID of the segment to retrieve
    
    Returns the report segment details.
    """
    return survey_analysis_service.get_survey_report_segment(
        session=session, 
        segment_id=segment_id
    )

@router.post("/segments", 
    response_model=SurveyReportSegmentGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create report segment",
    description="Creates a new survey report segment",
    response_description="Newly created report segment")
def create_survey_report_segment(
    segment_data: SurveyReportSegmentCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey report segment.
    
    The request body should contain:
    - survey_id: The ID of the survey this segment belongs to
    - name: The name of the segment
    
    Returns the newly created report segment.
    """
    return survey_analysis_service.create_survey_report_segment(
        session=session, 
        segment_data=segment_data
    )

@router.put("/segments/{segment_id}", 
    response_model=SurveyReportSegmentGet,
    summary="Update report segment",
    description="Updates an existing survey report segment",
    response_description="Updated report segment")
def update_survey_report_segment(
    segment_data: SurveyReportSegmentUpdate,
    segment_id: UUID = Path(..., description="The ID of the segment to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey report segment.
    
    Parameters:
    - **segment_id**: UUID of the segment to update
    
    Returns the updated report segment.
    """
    return survey_analysis_service.update_survey_report_segment(
        session=session, 
        segment_id=segment_id,
        segment_data=segment_data
    )

@router.delete("/segments/{segment_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete report segment",
    description="Deletes a survey report segment and all its associations")
def delete_survey_report_segment(
    segment_id: UUID = Path(..., description="The ID of the segment to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey report segment and all its associations.
    
    This operation cannot be undone. All associations with analysis questions
    will also be deleted due to cascading deletes.
    
    Parameters:
    - **segment_id**: UUID of the segment to delete
    """
    survey_analysis_service.delete_survey_report_segment(
        session=session, 
        segment_id=segment_id
    )

# ----- SURVEY ANALYSIS FILTER ENDPOINTS -----

@router.get("/analyses/{analysis_id}/filters", 
    response_model=List[SurveyAnalysisFilterGet],
    summary="Get analysis filters",
    description="Retrieves all filters for a specific survey analysis",
    response_description="List of analysis filters")
def get_survey_analysis_filters(
    analysis_id: UUID = Path(..., description="The ID of the analysis to get filters for"),
    session: SessionDep = SessionDep
):
    """
    Get all filters for a specific survey analysis.
    
    Parameters:
    - **analysis_id**: UUID of the analysis to get filters for
    
    Returns a list of analysis filters.
    """
    return survey_analysis_service.get_survey_analysis_filters(
        session=session, 
        analysis_id=analysis_id
    )

@router.get("/filters/{filter_id}", 
    response_model=SurveyAnalysisFilterGet,
    summary="Get analysis filter",
    description="Retrieves a specific survey analysis filter by ID",
    response_description="Analysis filter details")
def get_survey_analysis_filter(
    filter_id: UUID = Path(..., description="The ID of the filter to retrieve"),
    session: SessionDep = SessionDep
):
    """
    Get detailed information about a specific survey analysis filter by its ID.
    
    Parameters:
    - **filter_id**: UUID of the filter to retrieve
    
    Returns the survey analysis filter details.
    """
    return survey_analysis_service.get_survey_analysis_filter(
        session=session, 
        filter_id=filter_id
    )

@router.post("/filters", 
    response_model=SurveyAnalysisFilterGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create analysis filter",
    description="Creates a new survey analysis filter",
    response_description="Newly created analysis filter")
def create_survey_analysis_filter(
    filter_data: SurveyAnalysisFilterCreate,
    session: SessionDep = SessionDep
):
    """
    Create a new survey analysis filter.
    
    The request body should contain the survey analysis ID, question ID, and criteria.
    
    Returns the newly created survey analysis filter.
    """
    return survey_analysis_service.create_survey_analysis_filter(
        session=session, 
        filter_data=filter_data
    )

@router.put("/filters/{filter_id}", 
    response_model=SurveyAnalysisFilterGet,
    summary="Update analysis filter",
    description="Updates an existing survey analysis filter",
    response_description="Updated analysis filter")
def update_survey_analysis_filter(
    filter_data: SurveyAnalysisFilterUpdate,
    filter_id: UUID = Path(..., description="The ID of the filter to update"),
    session: SessionDep = SessionDep
):
    """
    Update an existing survey analysis filter.
    
    Parameters:
    - **filter_id**: UUID of the filter to update
    
    Returns the updated survey analysis filter.
    """
    return survey_analysis_service.update_survey_analysis_filter(
        session=session, 
        filter_id=filter_id,
        filter_data=filter_data
    )

@router.delete("/filters/{filter_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete analysis filter",
    description="Deletes a survey analysis filter and all its criteria")
def delete_survey_analysis_filter(
    filter_id: UUID = Path(..., description="The ID of the filter to delete"),
    session: SessionDep = SessionDep
):
    """
    Delete a survey analysis filter and all its criteria.
    
    This operation cannot be undone. All filter criteria will also be deleted 
    due to cascading deletes.
    
    Parameters:
    - **filter_id**: UUID of the filter to delete
    """
    survey_analysis_service.delete_survey_analysis_filter(
        session=session, 
        filter_id=filter_id
    ) 