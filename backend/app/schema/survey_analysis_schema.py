from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schema.survey_schema import QuestionGet

class ChartTypeGet(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class SurveyQuestionTopicGet(BaseModel):
    id: UUID
    name: str
    
    class Config:
        from_attributes = True

class SurveyReportSegmentGet(BaseModel):
    id: UUID
    name: str
    
    class Config:
        from_attributes = True

class SurveyAnalysisQuestionGet(BaseModel):
    id: UUID
    question_id: UUID
    chart_type_id: int
    sort_by_value: bool = False
    chart_type: ChartTypeGet
    question: QuestionGet
    topics: List[SurveyQuestionTopicGet] = []
    report_segments: List[SurveyReportSegmentGet] = []
    
    class Config:
        from_attributes = True

class SurveyAnalysisGet(BaseModel):
    id: UUID
    survey_id: UUID
    title: str
    description: Optional[str] = None
    date_created: datetime
    date_updated: datetime
    analysis_questions: List[SurveyAnalysisQuestionGet] = []
    
    class Config:
        from_attributes = True

# Survey Analysis schemas
class SurveyAnalysisCreate(BaseModel):
    survey_id: UUID
    title: str
    description: Optional[str] = None

class SurveyAnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class SurveyAnalysisQuestionCreate(BaseModel):
    survey_analysis_id: UUID
    question_id: UUID
    chart_type_id: int
    sort_by_value: bool = False
    topic_ids: Optional[List[UUID]] = None
    report_segment_ids: Optional[List[UUID]] = None

class SurveyAnalysisQuestionUpdate(BaseModel):
    chart_type_id: Optional[int] = None
    sort_by_value: Optional[bool] = None
    topic_ids: Optional[List[UUID]] = None
    report_segment_ids: Optional[List[UUID]] = None

class SurveyQuestionTopicCreate(BaseModel):
    survey_id: UUID
    name: str

class SurveyQuestionTopicUpdate(BaseModel):
    name: Optional[str] = None

class SurveyReportSegmentCreate(BaseModel):
    survey_id: UUID
    name: str

class SurveyReportSegmentUpdate(BaseModel):
    name: Optional[str] = None 