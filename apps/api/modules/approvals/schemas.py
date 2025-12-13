"""
Approval Workflow Module - Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

from modules.approvals.models import ApprovalStatus, ApprovalType


# Approval Request Schemas
class ApprovalRequestBase(BaseModel):
    request_type: ApprovalType
    request_id: uuid.UUID
    employee_id: uuid.UUID
    approver_id: uuid.UUID
    comments: Optional[str] = None


class ApprovalRequestCreate(BaseModel):
    request_type: ApprovalType
    request_id: uuid.UUID
    employee_id: uuid.UUID
    comments: Optional[str] = None


class ApprovalRequestUpdate(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    id: uuid.UUID
    status: ApprovalStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Approval Delegation Schemas
class ApprovalDelegationBase(BaseModel):
    supervisor_id: uuid.UUID
    delegate_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None


class ApprovalDelegationCreate(ApprovalDelegationBase):
    pass


class ApprovalDelegationUpdate(BaseModel):
    end_date: Optional[datetime] = None
    is_active: Optional[str] = None
    reason: Optional[str] = None


class ApprovalDelegationResponse(ApprovalDelegationBase):
    id: uuid.UUID
    is_active: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dashboard stats
class ApprovalStats(BaseModel):
    total_pending: int
    leave_pending: int
    travel_pending: int
    timesheet_pending: int
    performance_pending: int
