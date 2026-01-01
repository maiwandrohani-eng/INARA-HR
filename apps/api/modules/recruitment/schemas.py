"""Recruitment Module - Schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
import uuid


class JobPostingCreate(BaseModel):
    """Job posting creation schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    employment_type: str
    location: Optional[str] = None
    salary_range_min: Optional[str] = None
    salary_range_max: Optional[str] = None
    currency: str = "USD"
    closing_date: Optional[date] = None


class JobPostingResponse(BaseModel):
    """Job posting response schema"""
    id: uuid.UUID
    title: str
    description: str
    employment_type: str
    location: Optional[str]
    status: str
    posted_date: Optional[date]
    
    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    """Application creation schema"""
    job_posting_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    source: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Application response schema"""
    id: uuid.UUID
    job_posting_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    status: str
    applied_date: date
    
    class Config:
        from_attributes = True


class InterviewSchedule(BaseModel):
    """Interview scheduling schema"""
    application_id: uuid.UUID
    interview_type: str = Field(..., pattern="^(phone|video|in-person|panel)$")
    scheduled_date: date
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    interviewer_ids: List[uuid.UUID] = []


class InterviewResponse(BaseModel):
    """Interview response schema"""
    id: uuid.UUID
    application_id: uuid.UUID
    interview_type: str
    scheduled_date: date
    status: str
    rating: Optional[int] = None
    
    class Config:
        from_attributes = True


class InterviewFeedback(BaseModel):
    """Interview feedback schema"""
    feedback: str
    rating: Optional[int] = Field(None, ge=1, le=5)


class OfferLetterCreate(BaseModel):
    """Offer letter creation schema"""
    application_id: uuid.UUID
    position_title: str
    salary: str
    currency: str = "USD"
    start_date: date
    offer_letter_url: Optional[str] = None


class OfferLetterResponse(BaseModel):
    """Offer letter response schema"""
    id: uuid.UUID
    application_id: uuid.UUID
    position_title: str
    salary: str
    status: str
    sent_date: Optional[date] = None
    
    class Config:
        from_attributes = True
