"""Recruitment Module - Schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
import uuid

class JobPostingCreate(BaseModel):
    title: str
    description: str
    employment_type: str
    country_code: str

class ApplicationCreate(BaseModel):
    job_posting_id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

class InterviewSchedule(BaseModel):
    application_id: uuid.UUID
    interview_type: str
    scheduled_date: date
