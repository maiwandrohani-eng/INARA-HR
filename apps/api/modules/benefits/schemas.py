"""
Benefits Management Module - Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
import uuid


# Benefit Plan Schemas
class BenefitPlanBase(BaseModel):
    name: str
    benefit_type: str  # health_insurance, retirement, life_insurance, etc.
    provider: Optional[str] = None
    description: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None
    eligibility_criteria: Optional[str] = None
    is_active: bool = True
    employer_contribution_percentage: Optional[float] = None
    employer_contribution_amount: Optional[float] = None
    employee_cost_per_pay_period: Optional[float] = None
    currency: str = "USD"


class BenefitPlanCreate(BenefitPlanBase):
    pass


class BenefitPlanUpdate(BaseModel):
    name: Optional[str] = None
    benefit_type: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None
    eligibility_criteria: Optional[str] = None
    is_active: Optional[bool] = None
    employer_contribution_percentage: Optional[float] = None
    employer_contribution_amount: Optional[float] = None
    employee_cost_per_pay_period: Optional[float] = None
    currency: Optional[str] = None


class BenefitPlanResponse(BenefitPlanBase):
    id: uuid.UUID
    created_at: Optional[date] = None
    
    class Config:
        from_attributes = True


# Benefit Enrollment Schemas
class BenefitEnrollmentBase(BaseModel):
    employee_id: uuid.UUID
    benefit_plan_id: uuid.UUID
    enrollment_date: date
    effective_date: date
    end_date: Optional[date] = None
    coverage_level: Optional[str] = None
    status: str = "active"
    dependents_count: int = 0
    employee_contribution_amount: Optional[float] = None
    notes: Optional[str] = None


class BenefitEnrollmentCreate(BenefitEnrollmentBase):
    pass


class BenefitEnrollmentUpdate(BaseModel):
    end_date: Optional[date] = None
    status: Optional[str] = None
    coverage_level: Optional[str] = None
    dependents_count: Optional[int] = None
    employee_contribution_amount: Optional[float] = None
    notes: Optional[str] = None


class BenefitEnrollmentResponse(BenefitEnrollmentBase):
    id: uuid.UUID
    created_at: Optional[date] = None
    
    class Config:
        from_attributes = True


# Dependent Schemas
class BenefitDependentBase(BaseModel):
    enrollment_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    dependent_relationship: str
    ssn: Optional[str] = None
    is_active: bool = True
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None


class BenefitDependentCreate(BenefitDependentBase):
    pass


class BenefitDependentResponse(BenefitDependentBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Open Enrollment Period Schemas
class OpenEnrollmentPeriodBase(BaseModel):
    name: str
    year: int
    start_date: date
    end_date: date
    is_active: bool = False
    applicable_benefit_types: Optional[str] = None
    description: Optional[str] = None


class OpenEnrollmentPeriodCreate(OpenEnrollmentPeriodBase):
    pass


class OpenEnrollmentPeriodResponse(OpenEnrollmentPeriodBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

