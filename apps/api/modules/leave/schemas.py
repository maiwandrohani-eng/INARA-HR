"""
Leave & Attendance Module - Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
import uuid


# Leave Policy Schemas
class LeavePolicyBase(BaseModel):
    name: str
    leave_type: str
    days_per_year: Decimal
    accrual_rate: Optional[str] = None
    max_carryover: Optional[Decimal] = None
    requires_approval: bool = True
    description: Optional[str] = None


class LeavePolicyCreate(LeavePolicyBase):
    pass


class LeavePolicyResponse(LeavePolicyBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Leave Balance Schemas
class LeaveBalanceBase(BaseModel):
    employee_id: uuid.UUID
    leave_type: str
    year: str
    total_days: Decimal
    used_days: Decimal = Decimal("0")
    pending_days: Decimal = Decimal("0")
    available_days: Decimal


class LeaveBalanceCreate(LeaveBalanceBase):
    pass


class LeaveBalanceResponse(LeaveBalanceBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Leave Request Schemas
class LeaveRequestBase(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    notes: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    employee_id: Optional[uuid.UUID] = None  # Will be set from current user if not provided


class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None
    rejection_reason: Optional[str] = None


class LeaveRequestResponse(LeaveRequestBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    total_days: Decimal
    status: str
    approver_id: Optional[uuid.UUID] = None
    approved_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    supporting_document_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceRecordBase(BaseModel):
    employee_id: uuid.UUID
    date: date
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    status: str = "present"
    work_hours: Optional[Decimal] = None
    notes: Optional[str] = None


class AttendanceRecordCreate(AttendanceRecordBase):
    pass


class AttendanceRecordResponse(AttendanceRecordBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
