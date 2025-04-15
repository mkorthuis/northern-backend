from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from uuid import UUID, uuid4
from .base import UUIDBaseMixin
import sqlalchemy

class SurveyRespondent(UUIDBaseMixin, table=True):
    __tablename__ = "survey_respondent"
    
    email: str = Field(max_length=255, unique=True)
    username: str = Field(max_length=100, unique=True)
    
    # Relationships
    responses: List["SurveyResponse"] = Relationship(back_populates="respondent")


class Survey(UUIDBaseMixin, table=True):
    __tablename__ = "survey"
    
    title: str = Field(max_length=255)
    description: Optional[str] = None
    survey_start: Optional[datetime] = None
    survey_end: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    # Relationships
    sections: List["SurveySection"] = Relationship(back_populates="survey")
    questions: List["Question"] = Relationship(back_populates="survey")
    responses: List["SurveyResponse"] = Relationship(back_populates="survey")


class SurveySection(UUIDBaseMixin, table=True):
    __tablename__ = "survey_section"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    title: str = Field(max_length=255)
    description: Optional[str] = None
    order_index: int
    
    # Relationships
    survey: Survey = Relationship(back_populates="sections")
    questions: List["Question"] = Relationship(back_populates="section")


class QuestionType(SQLModel, table=True):
    __tablename__ = "question_type"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = None
    date_created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    date_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relationships
    questions: List["Question"] = Relationship(back_populates="type")


class Question(UUIDBaseMixin, table=True):
    __tablename__ = "question"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    section_id: Optional[UUID] = Field(default=None, foreign_key="survey_section.id")
    type_id: int = Field(foreign_key="question_type.id")
    title: str
    description: Optional[str] = None
    is_required: bool = Field(default=False)
    order_index: int
    validation_rules: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    display_logic: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    allow_multiple: bool = Field(default=False)
    max_answers: Optional[int] = None
    
    # Relationships
    survey: Survey = Relationship(back_populates="questions")
    section: Optional[SurveySection] = Relationship(back_populates="questions")
    type: QuestionType = Relationship(back_populates="questions")
    options: List["QuestionOption"] = Relationship(back_populates="question")
    answers: List["Answer"] = Relationship(back_populates="question")


class QuestionOption(UUIDBaseMixin, table=True):
    __tablename__ = "question_option"
    
    question_id: UUID = Field(foreign_key="question.id")
    text: str
    order_index: int
    is_other_option: bool = Field(default=False)
    score: Optional[float] = None
    row_label: Optional[str] = Field(default=None, max_length=255)
    column_label: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    question: Question = Relationship(back_populates="options")
    answer_items: List["AnswerItem"] = Relationship(back_populates="option")


class SurveyResponse(UUIDBaseMixin, table=True):
    __tablename__ = "survey_response"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    respondent_id: Optional[UUID] = Field(default=None, foreign_key="survey_respondent.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = None
    is_complete: bool = Field(default=False)
    response_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column("metadata", JSON))
    
    # Relationships
    survey: Survey = Relationship(back_populates="responses")
    respondent: Optional[SurveyRespondent] = Relationship(back_populates="responses")
    answers: List["Answer"] = Relationship(back_populates="response")


class Answer(UUIDBaseMixin, table=True):
    __tablename__ = "answer"
    
    response_id: UUID = Field(foreign_key="survey_response.id")
    question_id: UUID = Field(foreign_key="question.id")
    value: Optional[str] = None
    selected_options: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    file_path: Optional[str] = Field(default=None, max_length=255)
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    response: SurveyResponse = Relationship(back_populates="answers")
    question: Question = Relationship(back_populates="answers")
    items: List["AnswerItem"] = Relationship(back_populates="answer")


class AnswerItem(UUIDBaseMixin, table=True):
    __tablename__ = "answer_item"
    
    answer_id: UUID = Field(foreign_key="answer.id")
    item_index: int
    value: Optional[str] = None
    option_id: Optional[UUID] = Field(default=None, foreign_key="question_option.id")
    row_identifier: Optional[str] = Field(default=None, max_length=100)
    column_identifier: Optional[str] = Field(default=None, max_length=100)
    
    # Relationships
    answer: Answer = Relationship(back_populates="items")
    option: Optional[QuestionOption] = Relationship(back_populates="answer_items") 