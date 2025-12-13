"""Travel - Schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid

class TravelRequestCreate(BaseModel):
    destination: str
    purpose: str
    departure_date: date
    return_date: date
    employee_id: Optional[uuid.UUID] = None

class TravelRequestResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    destination: str
    purpose: str
    departure_date: date
    return_date: date
    status: str
    approval_date: Optional[date] = None
    approver_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
