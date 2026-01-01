"""Safeguarding Module - Schemas"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
from uuid import UUID

class SafeguardingCaseCreate(BaseModel):
    # Accept both frontend field names and standard field names
    reporter_name: Optional[str] = None
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    incident_type: Optional[str] = None  # Frontend uses this
    case_type: Optional[str] = None      # Standard field
    severity: str = Field(..., description="Severity: low, medium, high, critical")
    incident_date: Optional[date] = Field(None, description="Date when incident occurred")
    incident_location: Optional[str] = None  # Frontend uses this
    location: Optional[str] = None           # Standard field
    description: str = Field(..., description="Detailed description of the incident")
    involved_persons: Optional[str] = None
    witnesses: Optional[str] = None
    action_taken: Optional[str] = None
    subject_id: Optional[str] = Field(None, description="ID of person accused (if applicable)")
    is_anonymous: bool = Field(default=False, description="Whether report is anonymous")
    status: Optional[str] = None  # Frontend sends this
    
    @field_validator('case_type', mode='before')
    def set_case_type(cls, v, info):
        # Use incident_type if case_type is not provided
        if not v and info.data.get('incident_type'):
            return info.data['incident_type']
        return v or 'safeguarding'
    
    @field_validator('location', mode='before')
    def set_location(cls, v, info):
        # Use incident_location if location is not provided
        if not v and info.data.get('incident_location'):
            return info.data['incident_location']
        return v

class SafeguardingCaseUpdate(BaseModel):
    investigator_id: Optional[str] = None
    investigation_status: Optional[str] = None
    investigation_findings: Optional[str] = None
    status: Optional[str] = None
    actions_taken: Optional[str] = None
    outcome: Optional[str] = None

class SafeguardingCaseResponse(BaseModel):
    id: UUID
    case_number: str
    case_type: str
    severity: str
    reported_date: date
    incident_date: Optional[date]
    description: str
    location: Optional[str]
    reporter_id: Optional[UUID]
    subject_id: Optional[UUID]
    investigator_id: Optional[UUID]
    investigation_status: str
    investigation_findings: Optional[str]
    status: str
    resolution_date: Optional[date]
    actions_taken: Optional[str]
    outcome: Optional[str]
    
    class Config:
        from_attributes = True
