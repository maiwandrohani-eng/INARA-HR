"""
Timesheets Module - Models
Time tracking with donor/project allocation
"""

from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class Project(BaseModel, TenantMixin, Base):
    """Projects for time allocation"""
    __tablename__ = "projects"
    
    project_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    donor = Column(String(200), nullable=True)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    budget = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    status = Column(String(20), default="active")  # active, completed, on-hold
    description = Column(Text, nullable=True)


class Timesheet(BaseModel, TenantMixin, AuditMixin, Base):
    """Employee timesheets"""
    __tablename__ = "timesheets"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    total_hours = Column(Numeric(6, 2), default=0, nullable=False)
    
    status = Column(String(20), default="draft")  # draft, submitted, approved, rejected
    submitted_date = Column(Date, nullable=True)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="timesheets")
    approver = relationship("Employee", foreign_keys=[approver_id])
    entries = relationship("TimesheetEntry", back_populates="timesheet")


class TimesheetEntry(BaseModel, TenantMixin, Base):
    """Individual timesheet entries"""
    __tablename__ = "timesheet_entries"
    
    timesheet_id = Column(UUID(as_uuid=True), ForeignKey('timesheets.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    date = Column(Date, nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    
    activity_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    timesheet = relationship("Timesheet", back_populates="entries")
    project = relationship("Project")
