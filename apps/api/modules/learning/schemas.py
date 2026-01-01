"""Learning Module - Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid


class CourseCreate(BaseModel):
    """Training course creation schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration_hours: Optional[int] = None
    provider: Optional[str] = None
    category: Optional[str] = None


class CourseResponse(BaseModel):
    """Training course response schema"""
    id: uuid.UUID
    title: str
    description: Optional[str]
    duration_hours: Optional[int]
    provider: Optional[str]
    category: Optional[str]
    
    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    """Training enrollment creation schema"""
    course_id: uuid.UUID


class EnrollmentResponse(BaseModel):
    """Training enrollment response schema"""
    id: uuid.UUID
    employee_id: uuid.UUID
    course_id: uuid.UUID
    enrollment_date: date
    completion_date: Optional[date]
    status: str
    certificate_url: Optional[str]
    
    class Config:
        from_attributes = True


class EnrollmentStatusUpdate(BaseModel):
    """Enrollment status update schema"""
    status: str = Field(..., pattern="^(enrolled|in_progress|completed|dropped)$")
    completion_date: Optional[date] = None
