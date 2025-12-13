"""
Approval Workflow Module - Database Models
"""

from sqlalchemy import Column, String, Enum as SQLEnum, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from datetime import datetime

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalType(str, enum.Enum):
    """Type of approval request"""
    LEAVE = "leave"
    TRAVEL = "travel"
    TIMESHEET = "timesheet"
    PERFORMANCE = "performance"
    EXPENSE = "expense"


class ApprovalRequest(BaseModel, TenantMixin, AuditMixin, Base):
    """Generic approval request tracking"""
    __tablename__ = "approval_requests"
    
    # Request details
    request_type = Column(SQLEnum(ApprovalType), nullable=False)
    request_id = Column(UUID(as_uuid=True), nullable=False)  # ID of the related entity (leave, travel, etc.)
    
    # Employee who submitted the request
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Supervisor/approver
    approver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Approval status and details
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    comments = Column(Text, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="approval_requests_submitted")
    approver = relationship("Employee", foreign_keys=[approver_id], backref="approval_requests_to_review")
    
    def __repr__(self):
        return f"<ApprovalRequest {self.request_type} - {self.status}>"


class ApprovalDelegation(BaseModel, TenantMixin, AuditMixin, Base):
    """Approval delegation for supervisor absences"""
    __tablename__ = "approval_delegations"
    
    # Supervisor delegating their approval authority
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Employee receiving delegation
    delegate_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Delegation period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Active status
    is_active = Column(String(10), default="true", nullable=False)
    
    # Reason for delegation
    reason = Column(Text, nullable=True)
    
    # Relationships
    supervisor = relationship("Employee", foreign_keys=[supervisor_id], backref="delegations_given")
    delegate = relationship("Employee", foreign_keys=[delegate_id], backref="delegations_received")
    
    def __repr__(self):
        return f"<ApprovalDelegation {self.supervisor_id} -> {self.delegate_id}>"
