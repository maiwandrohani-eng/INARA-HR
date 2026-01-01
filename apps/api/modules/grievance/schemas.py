"""Grievance - Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid

class GrievanceCreate(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    grievance_type: str
    related_person: Optional[str] = None
    relationship_to_complainant: Optional[str] = None
    incident_date: Optional[str] = None
    description: str
    previous_attempts: Optional[str] = None
    desired_resolution: Optional[str] = None
    witnesses: Optional[str] = None
    is_confidential: bool = False
    status: str = 'pending'

class GrievanceUpdate(BaseModel):
    status: Optional[str] = None
    resolution: Optional[str] = None
    resolution_date: Optional[str] = None

class GrievanceResponse(BaseModel):
    id: str
    employee_id: str
    case_number: str
    grievance_type: str
    description: str
    filed_date: date
    status: str
    resolution: Optional[str] = None
    resolution_date: Optional[date] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True
