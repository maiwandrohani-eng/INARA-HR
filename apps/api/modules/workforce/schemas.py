"""Workforce Planning Module - Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid


# Workforce Plan Schemas
class WorkforcePlanBase(BaseModel):
    plan_name: str
    plan_year: int
    plan_start_date: date
    plan_end_date: date
    status: str = "draft"
    total_budget: Optional[float] = None
    currency: str = "USD"
    approved_by: Optional[uuid.UUID] = None
    approved_date: Optional[date] = None


class WorkforcePlanCreate(WorkforcePlanBase):
    pass


class WorkforcePlanResponse(WorkforcePlanBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Position Requisition Schemas
class PositionRequisitionBase(BaseModel):
    workforce_plan_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    department_id: uuid.UUID
    job_title: str
    employment_type: str
    justification: str
    business_case: Optional[str] = None
    budgeted_salary_min: Optional[float] = None
    budgeted_salary_max: Optional[float] = None
    currency: str = "USD"
    requested_start_date: Optional[date] = None
    urgency: str = "normal"
    status: str = "draft"
    requested_by: Optional[uuid.UUID] = None


class PositionRequisitionCreate(PositionRequisitionBase):
    pass


class PositionRequisitionResponse(PositionRequisitionBase):
    id: uuid.UUID
    requisition_number: str
    
    class Config:
        from_attributes = True


# Headcount Forecast Schemas
class HeadcountForecastBase(BaseModel):
    workforce_plan_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    forecast_month: int
    forecast_year: int
    current_headcount: int
    planned_headcount: int
    budgeted_headcount: int
    headcount_variance: Optional[int] = None
    cost_impact: Optional[float] = None


class HeadcountForecastCreate(HeadcountForecastBase):
    pass


class HeadcountForecastResponse(HeadcountForecastBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

