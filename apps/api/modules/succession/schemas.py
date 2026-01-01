"""Succession Planning Module - Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid


# Key Position Schemas
class KeyPositionBase(BaseModel):
    position_id: uuid.UUID
    criticality_level: str
    business_impact: Optional[str] = None
    vacancy_risk: Optional[str] = None
    current_incumbent_id: Optional[uuid.UUID] = None
    has_successor: bool = False
    succession_status: str = "not_planned"


class KeyPositionCreate(KeyPositionBase):
    pass


class KeyPositionResponse(KeyPositionBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Successor Schemas
class SuccessorBase(BaseModel):
    key_position_id: uuid.UUID
    employee_id: uuid.UUID
    successor_type: str
    readiness_level: str
    readiness_score: Optional[int] = None
    skills_gap_analysis: Optional[str] = None
    development_needs: Optional[str] = None
    development_plan_created: bool = False
    development_plan_url: Optional[str] = None
    is_active: bool = True


class SuccessorCreate(SuccessorBase):
    pass


class SuccessorResponse(SuccessorBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Succession Plan Schemas
class SuccessionPlanBase(BaseModel):
    key_position_id: uuid.UUID
    plan_name: str
    plan_date: date
    review_date: Optional[date] = None
    status: str = "draft"
    expected_transition_date: Optional[date] = None
    risk_mitigation_strategies: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    approved_date: Optional[date] = None


class SuccessionPlanCreate(SuccessionPlanBase):
    pass


class SuccessionPlanResponse(SuccessionPlanBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

