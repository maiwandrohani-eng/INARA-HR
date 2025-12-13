"""Compensation Module - Models"""
from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin

class SalaryHistory(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "salary_history"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    effective_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    change_reason = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
