"""Compliance & Legal Module - Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


# Policy Schemas
class PolicyBase(BaseModel):
    title: str
    policy_type: str
    version: str
    content: Optional[str] = None
    document_url: Optional[str] = None
    effective_date: date
    expiry_date: Optional[date] = None
    is_active: bool = True
    requires_acknowledgment: bool = True
    applicable_to: str = "all"
    applicable_department_id: Optional[uuid.UUID] = None
    applicable_role: Optional[str] = None


class PolicyCreate(PolicyBase):
    pass


class PolicyResponse(PolicyBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Policy Acknowledgment Schemas
class PolicyAcknowledgmentCreate(BaseModel):
    policy_id: uuid.UUID
    employee_id: uuid.UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class PolicyAcknowledgmentResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    employee_id: uuid.UUID
    acknowledged_date: datetime
    is_acknowledged: bool
    
    class Config:
        from_attributes = True


# Compliance Training Schemas
class ComplianceTrainingBase(BaseModel):
    title: str
    training_type: str
    description: Optional[str] = None
    duration_minutes: Optional[str] = None
    training_url: Optional[str] = None
    is_online: bool = True
    required_for: str = "all"
    frequency: Optional[str] = None
    due_date: Optional[date] = None
    is_active: bool = True


class ComplianceTrainingCreate(ComplianceTrainingBase):
    pass


class ComplianceTrainingResponse(ComplianceTrainingBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Training Completion Schemas
class TrainingCompletionCreate(BaseModel):
    compliance_training_id: uuid.UUID
    employee_id: uuid.UUID
    expiration_date: Optional[datetime] = None
    certificate_url: Optional[str] = None
    score: Optional[str] = None
    passed: Optional[bool] = None


class TrainingCompletionResponse(BaseModel):
    id: uuid.UUID
    compliance_training_id: uuid.UUID
    employee_id: uuid.UUID
    completed_date: datetime
    
    class Config:
        from_attributes = True

