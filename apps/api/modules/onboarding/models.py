"""Onboarding Module - Models"""
from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin

class OnboardingChecklist(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "onboarding_checklists"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    task_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean, default=False)
    completed_date = Column(Date, nullable=True)
