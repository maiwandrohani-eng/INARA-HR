"""
Workforce Planning Module - Models
Headcount forecasting, budget planning, position requisitions
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class WorkforcePlan(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Workforce planning documents"""
    __tablename__ = "workforce_plans"
    
    plan_name = Column(String(200), nullable=False)
    plan_year = Column(Integer, nullable=False)
    
    # Plan period
    plan_start_date = Column(Date, nullable=False)
    plan_end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(String(20), default="draft")  # draft, approved, active, archived
    
    # Budget
    total_budget = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Relationships
    approver = relationship("Employee", foreign_keys=[approved_by])
    requisitions = relationship("PositionRequisition", back_populates="workforce_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkforcePlan {self.plan_name} {self.plan_year}>"


class PositionRequisition(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Position requisition requests"""
    __tablename__ = "position_requisitions"
    
    workforce_plan_id = Column(UUID(as_uuid=True), ForeignKey('workforce_plans.id'), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id'), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)
    
    # Requisition details
    requisition_number = Column(String(100), unique=True, nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    employment_type = Column(String(50), nullable=False)  # full_time, part_time, contract
    
    # Justification
    justification = Column(Text, nullable=False)
    business_case = Column(Text, nullable=True)
    
    # Budget
    budgeted_salary_min = Column(Numeric(10, 2), nullable=True)
    budgeted_salary_max = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Timeline
    requested_start_date = Column(Date, nullable=True)
    urgency = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Status and workflow
    status = Column(String(20), default="draft")  # draft, pending_approval, approved, rejected, on_hold, filled
    
    # Approval chain
    requested_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    workforce_plan = relationship("WorkforcePlan", back_populates="requisitions")
    position = relationship("Position", backref="requisitions")
    department = relationship("Department", backref="position_requisitions")
    requester = relationship("Employee", foreign_keys=[requested_by], backref="requested_requisitions")
    approver = relationship("Employee", foreign_keys=[approved_by], backref="approved_requisitions")
    
    def __repr__(self):
        return f"<PositionRequisition {self.requisition_number}>"


class HeadcountForecast(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Headcount forecasts by department/position"""
    __tablename__ = "headcount_forecasts"
    
    workforce_plan_id = Column(UUID(as_uuid=True), ForeignKey('workforce_plans.id'), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id'), nullable=True)
    
    # Forecast period
    forecast_month = Column(Integer, nullable=False)  # 1-12
    forecast_year = Column(Integer, nullable=False)
    
    # Forecast numbers
    current_headcount = Column(Integer, nullable=False)
    planned_headcount = Column(Integer, nullable=False)
    budgeted_headcount = Column(Integer, nullable=False)
    
    # Variance
    headcount_variance = Column(Integer, nullable=True)  # planned - current
    cost_impact = Column(Numeric(15, 2), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    workforce_plan = relationship("WorkforcePlan", backref="headcount_forecasts")
    department = relationship("Department", backref="headcount_forecasts")
    position = relationship("Position", backref="headcount_forecasts")
    
    def __repr__(self):
        return f"<HeadcountForecast {self.forecast_year}-{self.forecast_month}>"

