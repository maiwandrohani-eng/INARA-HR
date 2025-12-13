"""Safeguarding Module - Schemas"""
from pydantic import BaseModel
from datetime import date

class SafeguardingCaseCreate(BaseModel):
    case_type: str
    severity: str
    incident_date: date
    description: str
