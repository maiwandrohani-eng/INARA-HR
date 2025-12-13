"""
Leave & Attendance Module - Models
Leave requests, balances, policies, attendance tracking
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class LeavePolicy(BaseModel, TenantMixin, Base):
    """Leave policy configuration per country/type"""
    __tablename__ = "leave_policies"
    
    name = Column(String(100), nullable=False)
    leave_type = Column(String(50), nullable=False)  # annual, sick, maternity, paternity, etc.
    days_per_year = Column(Numeric(5, 2), nullable=False)
    accrual_rate = Column(String(20), nullable=True)  # monthly, quarterly, yearly
    max_carryover = Column(Numeric(5, 2), nullable=True)
    requires_approval = Column(Boolean, default=True)
    description = Column(Text, nullable=True)


class LeaveBalance(BaseModel, TenantMixin, Base):
    """Employee leave balances"""
    __tablename__ = "leave_balances"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    leave_type = Column(String(50), nullable=False)
    year = Column(String(10), nullable=False)
    
    total_days = Column(Numeric(5, 2), nullable=False)
    used_days = Column(Numeric(5, 2), default=0, nullable=False)
    pending_days = Column(Numeric(5, 2), default=0, nullable=False)
    available_days = Column(Numeric(5, 2), nullable=False)


class LeaveRequest(BaseModel, TenantMixin, AuditMixin, Base):
    """Employee leave requests"""
    __tablename__ = "leave_requests"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    leave_type = Column(String(50), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    status = Column(String(20), default="pending")  # pending, approved, rejected, cancelled
    approver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    supporting_document_url = Column(String(500), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="leave_requests")
    approver = relationship("Employee", foreign_keys=[approver_id])


class AttendanceRecord(BaseModel, TenantMixin, Base):
    """Daily attendance tracking"""
    __tablename__ = "attendance_records"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    
    check_in_time = Column(String(20), nullable=True)
    check_out_time = Column(String(20), nullable=True)
    
    status = Column(String(20), default="present")  # present, absent, late, half-day
    work_hours = Column(Numeric(5, 2), nullable=True)
    
    notes = Column(Text, nullable=True)
