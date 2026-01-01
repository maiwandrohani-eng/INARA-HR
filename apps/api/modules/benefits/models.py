"""
Benefits Management Module - Models
Health insurance, retirement plans, FSA/HSA, life insurance, etc.
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Numeric, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import date

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class BenefitPlan(BaseModel, TenantMixin, AuditMixin, Base):
    """Benefit plan catalog (health insurance, retirement, etc.)"""
    __tablename__ = "benefit_plans"
    
    name = Column(String(200), nullable=False)
    benefit_type = Column(String(50), nullable=False)  # health_insurance, retirement, life_insurance, dental, vision, fsa, hsa, disability, etc.
    provider = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Coverage details
    coverage_start_date = Column(Date, nullable=True)
    coverage_end_date = Column(Date, nullable=True)
    
    # Eligibility
    eligibility_criteria = Column(Text, nullable=True)  # JSON: employment_type, tenure, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Costs
    employer_contribution_percentage = Column(Numeric(5, 2), nullable=True)
    employer_contribution_amount = Column(Numeric(10, 2), nullable=True)
    employee_cost_per_pay_period = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Relationships
    enrollments = relationship("BenefitEnrollment", back_populates="plan")
    
    def __repr__(self):
        return f"<BenefitPlan {self.name} - {self.benefit_type}>"


class BenefitEnrollment(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Employee benefit enrollment records"""
    __tablename__ = "benefit_enrollments"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    benefit_plan_id = Column(UUID(as_uuid=True), ForeignKey('benefit_plans.id'), nullable=False)
    
    # Enrollment details
    enrollment_date = Column(Date, nullable=False)
    effective_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # For terminations/changes
    
    # Coverage level
    coverage_level = Column(String(50), nullable=True)  # individual, employee_spouse, employee_children, family
    
    # Status
    status = Column(String(20), default="active")  # active, cancelled, terminated, pending
    
    # Dependents covered
    dependents_count = Column(Integer, default=0, nullable=False)
    
    # Employee contribution
    employee_contribution_amount = Column(Numeric(10, 2), nullable=True)
    
    # Notes provided by NoteMixin
    
    # Relationships
    employee = relationship("Employee", backref="benefit_enrollments")
    plan = relationship("BenefitPlan", back_populates="enrollments")
    dependents = relationship("BenefitDependent", back_populates="enrollment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BenefitEnrollment {self.employee_id} - {self.benefit_plan_id}>"


class BenefitDependent(BaseModel, TenantMixin, AuditMixin, Base):
    """Dependents covered under benefit enrollments"""
    __tablename__ = "benefit_dependents"
    
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey('benefit_enrollments.id'), nullable=False)
    
    # Dependent information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    dependent_relationship = Column(String(50), nullable=False)  # spouse, child, domestic_partner, etc.
    ssn = Column(String(20), nullable=True)  # Social Security Number (encrypted in production)
    
    # Coverage status
    is_active = Column(Boolean, default=True, nullable=False)
    coverage_start_date = Column(Date, nullable=True)
    coverage_end_date = Column(Date, nullable=True)
    
    # Relationships
    enrollment = relationship("BenefitEnrollment", back_populates="dependents")
    
    def __repr__(self):
        return f"<BenefitDependent {self.first_name} {self.last_name}>"


class OpenEnrollmentPeriod(BaseModel, TenantMixin, AuditMixin, Base):
    """Open enrollment periods for benefits"""
    __tablename__ = "open_enrollment_periods"
    
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Period dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=False, nullable=False)
    
    # Applicable benefit types
    applicable_benefit_types = Column(Text, nullable=True)  # JSON array of benefit types
    
    # Description
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<OpenEnrollmentPeriod {self.name} {self.year}>"

