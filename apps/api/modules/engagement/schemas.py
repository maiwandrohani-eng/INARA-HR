"""Employee Engagement Module - Schemas"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import uuid


# Survey Schemas
class SurveyBase(BaseModel):
    title: str
    survey_type: str
    description: Optional[str] = None
    is_anonymous: bool = True
    is_active: bool = True
    start_date: date
    end_date: date
    target_audience: str = "all"
    target_department_id: Optional[uuid.UUID] = None


class SurveyCreate(SurveyBase):
    pass


class SurveyResponse(BaseModel):
    id: uuid.UUID
    title: str
    survey_type: str
    is_active: bool
    start_date: date
    end_date: date
    response_count: int
    
    class Config:
        from_attributes = True


# Survey Question Schemas
class SurveyQuestionBase(BaseModel):
    survey_id: uuid.UUID
    question_text: str
    question_type: str
    is_required: bool = True
    display_order: int
    options: Optional[str] = None


class SurveyQuestionCreate(SurveyQuestionBase):
    pass


# Survey Response Schemas
class SurveyResponseCreate(BaseModel):
    survey_id: uuid.UUID
    employee_id: Optional[uuid.UUID] = None
    overall_rating: Optional[int] = None


# Recognition Schemas
class RecognitionBase(BaseModel):
    employee_id: uuid.UUID
    recognized_by_id: uuid.UUID
    recognition_type: str
    title: str
    description: str
    recognition_date: date
    is_public: bool = True


class RecognitionCreate(RecognitionBase):
    pass


class RecognitionResponse(RecognitionBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

