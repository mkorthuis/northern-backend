from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class QuestionOptionGet(BaseModel):
    id: UUID
    text: str
    order_index: int
    is_other_option: bool = False
    score: Optional[float] = None
    row_label: Optional[str] = None
    column_label: Optional[str] = None
    
    class Config:
        from_attributes = True

class QuestionTypeGet(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class QuestionGet(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    is_required: bool = False
    order_index: int
    validation_rules: Optional[Dict[str, Any]] = None
    display_logic: Optional[Dict[str, Any]] = None
    allow_multiple: bool = False
    max_answers: Optional[int] = None
    type: QuestionTypeGet
    options: List[QuestionOptionGet] = []
    
    class Config:
        from_attributes = True

class SurveySectionGet(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    order_index: int
    questions: List[QuestionGet] = []
    
    class Config:
        from_attributes = True

class SurveyRespondentGet(BaseModel):
    id: UUID
    email: str
    username: str
    
    class Config:
        from_attributes = True

class SurveyGet(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    date_created: datetime
    date_updated: datetime
    survey_start: Optional[datetime] = None
    survey_end: Optional[datetime] = None
    is_active: bool = True
    created_by: UUID
    sections: List[SurveySectionGet] = []
    questions: List[QuestionGet] = []
    
    class Config:
        from_attributes = True

class AnswerItemGet(BaseModel):
    id: UUID
    item_index: int
    value: Optional[str] = None
    option_id: Optional[UUID] = None
    row_identifier: Optional[str] = None
    column_identifier: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnswerGet(BaseModel):
    id: UUID
    question_id: UUID
    value: Optional[str] = None
    selected_options: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    answered_at: datetime
    question: QuestionGet
    items: List[AnswerItemGet] = []
    
    class Config:
        from_attributes = True

class SurveyResponseGet(BaseModel):
    id: UUID
    survey_id: UUID
    respondent_id: Optional[UUID] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_complete: bool = False
    answers: List[AnswerGet] = []
    
    class Config:
        from_attributes = True

# ----- CREATE/UPDATE MODELS -----

class QuestionOptionCreate(BaseModel):
    text: str
    order_index: int
    is_other_option: bool = False
    score: Optional[float] = None
    row_label: Optional[str] = None
    column_label: Optional[str] = None

class QuestionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_required: bool = False
    order_index: int
    type_id: int
    section_id: Optional[UUID] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_logic: Optional[Dict[str, Any]] = None
    allow_multiple: bool = False
    max_answers: Optional[int] = None
    options: List[QuestionOptionCreate] = []

class SurveySectionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    questions: List[QuestionCreate] = []

class SurveyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    survey_start: Optional[datetime] = None
    survey_end: Optional[datetime] = None
    is_active: bool = True
    created_by: UUID
    sections: List[SurveySectionCreate] = []
    questions: List[QuestionCreate] = []

class SurveyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    survey_start: Optional[datetime] = None
    survey_end: Optional[datetime] = None
    is_active: Optional[bool] = None

class AnswerItemCreate(BaseModel):
    item_index: int
    value: Optional[str] = None
    option_id: Optional[UUID] = None
    row_identifier: Optional[str] = None
    column_identifier: Optional[str] = None

class AnswerCreate(BaseModel):
    question_id: UUID
    value: Optional[str] = None
    selected_options: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    items: List[AnswerItemCreate] = []

class SurveyResponseCreate(BaseModel):
    survey_id: UUID
    respondent_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_metadata: Optional[Dict[str, Any]] = None
    answers: List[AnswerCreate] = []

class SurveyResponseUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    is_complete: Optional[bool] = None
    answers: Optional[List[AnswerCreate]] = None 