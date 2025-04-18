from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from uuid import UUID, uuid4
from .base import UUIDBaseMixin
from .survey import Survey, Question

class ChartType(SQLModel, table=True):
    __tablename__ = "chart_type"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True)
    date_created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    date_updated: datetime = Field(default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Relationships
    analysis_questions: List["SurveyAnalysisQuestion"] = Relationship(back_populates="chart_type")


class SurveyAnalysis(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    title: str = Field(max_length=255)
    description: Optional[str] = None
    
    # Relationships
    survey: Survey = Relationship(back_populates="analyses")
    analysis_questions: List["SurveyAnalysisQuestion"] = Relationship(back_populates="survey_analysis")
    filters: List["SurveyAnalysisFilter"] = Relationship(
        back_populates="survey_analysis",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class SurveyAnalysisQuestion(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_question"
    
    survey_analysis_id: UUID = Field(foreign_key="survey_analysis.id")
    question_id: UUID = Field(foreign_key="question.id")
    chart_type_id: int = Field(foreign_key="chart_type.id")
    sort_by_value: bool = Field(default=False)
    is_demographic: bool = Field(default=False)
    
    # Relationships
    survey_analysis: SurveyAnalysis = Relationship(back_populates="analysis_questions")
    question: Question = Relationship(back_populates="analysis_questions")
    chart_type: ChartType = Relationship(back_populates="analysis_questions")
    topic_xrefs: List["SurveyAnalysisQuestionTopicXref"] = Relationship(
        back_populates="survey_analysis_question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    segment_xrefs: List["SurveyAnalysisReportSegmentXref"] = Relationship(
        back_populates="survey_analysis_question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    answer_transforms: List["SurveyAnalysisAnswerTransform"] = Relationship(
        back_populates="survey_analysis_question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    filters: List["SurveyAnalysisFilter"] = Relationship(
        back_populates="survey_analysis_question",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    @property
    def topics(self) -> List["SurveyQuestionTopic"]:
        """Get the topics associated with this analysis question."""
        return [xref.survey_question_topic for xref in self.topic_xrefs]

    @property
    def report_segments(self) -> List["SurveyReportSegment"]:
        """Get the report segments associated with this analysis question."""
        return [xref.survey_report_segment for xref in self.segment_xrefs]


class SurveyAnalysisAnswerTransform(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_answer_transform"
    
    survey_analysis_question_id: UUID = Field(foreign_key="survey_analysis_question.id")
    original_answer: str
    new_answer: str
    new_order_id: int
    
    # Relationships
    survey_analysis_question: SurveyAnalysisQuestion = Relationship(back_populates="answer_transforms")


class SurveyAnalysisFilter(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_filter"
    
    survey_analysis_id: UUID = Field(foreign_key="survey_analysis.id")
    survey_analysis_question_id: UUID = Field(foreign_key="survey_analysis_question.id")
    
    # Relationships
    survey_analysis: SurveyAnalysis = Relationship(back_populates="filters")
    survey_analysis_question: SurveyAnalysisQuestion = Relationship(back_populates="filters")
    criteria: List["SurveyAnalysisFilterCriteria"] = Relationship(
        back_populates="survey_analysis_filter",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class SurveyAnalysisFilterCriteria(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_filter_criteria"
    
    survey_analysis_filter_id: UUID = Field(foreign_key="survey_analysis_filter.id")
    value: str
    
    # Relationships
    survey_analysis_filter: SurveyAnalysisFilter = Relationship(back_populates="criteria")


class SurveyQuestionTopic(UUIDBaseMixin, table=True):
    __tablename__ = "survey_question_topic"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    name: str = Field(max_length=255)
    
    # Relationships
    survey: Survey = Relationship(back_populates="topics")
    topic_xrefs: List["SurveyAnalysisQuestionTopicXref"] = Relationship(back_populates="survey_question_topic")


class SurveyAnalysisQuestionTopicXref(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_question_topic_xref"
    
    survey_question_topic_id: UUID = Field(foreign_key="survey_question_topic.id")
    survey_analysis_question_id: UUID = Field(foreign_key="survey_analysis_question.id")
    
    # Relationships
    survey_question_topic: SurveyQuestionTopic = Relationship(back_populates="topic_xrefs")
    survey_analysis_question: SurveyAnalysisQuestion = Relationship(back_populates="topic_xrefs")


class SurveyReportSegment(UUIDBaseMixin, table=True):
    __tablename__ = "survey_report_segment"
    
    survey_id: UUID = Field(foreign_key="survey.id")
    name: str = Field(max_length=255)
    
    # Relationships
    survey: Survey = Relationship(back_populates="report_segments")
    segment_xrefs: List["SurveyAnalysisReportSegmentXref"] = Relationship(back_populates="survey_report_segment")


class SurveyAnalysisReportSegmentXref(UUIDBaseMixin, table=True):
    __tablename__ = "survey_analysis_report_segment_xref"
    
    survey_report_segment_id: UUID = Field(foreign_key="survey_report_segment.id")
    survey_analysis_question_id: UUID = Field(foreign_key="survey_analysis_question.id")
    
    # Relationships
    survey_report_segment: SurveyReportSegment = Relationship(back_populates="segment_xrefs")
    survey_analysis_question: SurveyAnalysisQuestion = Relationship(back_populates="segment_xrefs") 