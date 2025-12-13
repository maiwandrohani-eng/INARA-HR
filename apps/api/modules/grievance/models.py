"""Grievance & Disciplinary Module - Models"""
from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin

class Grievance(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "grievances"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    case_number = Column(String(100), unique=True, nullable=False)
    grievance_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    filed_date = Column(Date, nullable=False)
    status = Column(String(20), default="open")
    resolution = Column(Text, nullable=True)
    resolution_date = Column(Date, nullable=True)

class DisciplinaryAction(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "disciplinary_actions"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # verbal_warning, written_warning, suspension, termination
    reason = Column(Text, nullable=False)
    action_date = Column(Date, nullable=False)
    details = Column(Text, nullable=True)
    document_url = Column(String(500), nullable=True)
