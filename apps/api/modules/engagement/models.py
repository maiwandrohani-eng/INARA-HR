"""
Employee Engagement Module - Models
Surveys, recognition, feedback, satisfaction tracking
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean, Integer, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class Survey(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Employee engagement surveys"""
    __tablename__ = "surveys"
    
    title = Column(String(200), nullable=False)
    survey_type = Column(String(50), nullable=False)  # pulse, annual, onboarding, exit, custom
    description = Column(Text, nullable=True)
    
    # Survey configuration
    is_anonymous = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Targeting
    target_audience = Column(String(50), default="all")  # all, department, role
    target_department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    
    # Results
    response_count = Column(Integer, default=0, nullable=False)
    average_rating = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    department = relationship("Department", backref="surveys")
    questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Survey {self.title}>"


class SurveyQuestion(BaseModel, TenantMixin, AuditMixin, Base):
    """Survey questions"""
    __tablename__ = "survey_questions"
    
    survey_id = Column(UUID(as_uuid=True), ForeignKey('surveys.id'), nullable=False)
    
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # rating, multiple_choice, text, yes_no
    is_required = Column(Boolean, default=True, nullable=False)
    
    # Ordering
    display_order = Column(Integer, nullable=False)
    
    # Options for multiple choice
    options = Column(Text, nullable=True)  # JSON array of options
    
    # Relationships
    survey = relationship("Survey", back_populates="questions")
    
    def __repr__(self):
        return f"<SurveyQuestion {self.question_text[:50]}>"


class SurveyResponse(BaseModel, TenantMixin, AuditMixin, Base):
    """Individual survey responses"""
    __tablename__ = "survey_responses"
    
    survey_id = Column(UUID(as_uuid=True), ForeignKey('surveys.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)  # Null if anonymous
    
    # Response details
    submitted_date = Column(DateTime, nullable=False)
    
    # Overall rating (if applicable)
    overall_rating = Column(Integer, nullable=True)  # 1-10 scale
    
    # Response status
    is_complete = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    survey = relationship("Survey", back_populates="responses")
    employee = relationship("Employee", backref="survey_responses")
    answers = relationship("SurveyAnswer", back_populates="response", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SurveyResponse {self.survey_id} - {self.employee_id}>"


class SurveyAnswer(BaseModel, TenantMixin, Base):
    """Individual question answers"""
    __tablename__ = "survey_answers"
    
    response_id = Column(UUID(as_uuid=True), ForeignKey('survey_responses.id'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('survey_questions.id'), nullable=False)
    
    # Answer
    answer_text = Column(Text, nullable=True)
    answer_value = Column(String(200), nullable=True)  # For ratings, multiple choice
    
    # Relationships
    response = relationship("SurveyResponse", back_populates="answers")
    question = relationship("SurveyQuestion")
    
    def __repr__(self):
        return f"<SurveyAnswer {self.question_id}>"


class Recognition(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Employee recognition and awards"""
    __tablename__ = "recognitions"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    recognized_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Recognition details
    recognition_type = Column(String(50), nullable=False)  # achievement, milestone, excellence, peer_recognition
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Dates
    recognition_date = Column(Date, nullable=False)
    
    # Visibility
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="received_recognitions")
    recognized_by = relationship("Employee", foreign_keys=[recognized_by_id], backref="given_recognitions")
    
    def __repr__(self):
        return f"<Recognition {self.title} - {self.employee_id}>"

