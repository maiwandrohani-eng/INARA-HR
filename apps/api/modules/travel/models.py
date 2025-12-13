"""Travel & Deployment Module - Models"""
from sqlalchemy import Column, String, Date, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin

class TravelRequest(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "travel_requests"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    destination = Column(String(200), nullable=False)
    purpose = Column(Text, nullable=False)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    duration_days = Column(Numeric(5, 1), nullable=True)
    transport_mode = Column(String(50), nullable=True)
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected, completed
    approval_date = Column(Date, nullable=True)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="travel_requests")
    approver = relationship("Employee", foreign_keys=[approver_id])

class VisaRecord(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "visa_records"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    country = Column(String(100), nullable=False)
    visa_type = Column(String(100), nullable=False)
    visa_number = Column(String(100), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")  # active, expired, cancelled
    notes = Column(Text, nullable=True)
