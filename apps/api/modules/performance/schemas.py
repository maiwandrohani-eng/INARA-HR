"""
Performance Management Module - Pydantic Schemas
360-degree performance reviews
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
import uuid

from modules.performance.models import ReviewerType


# Performance Review Cycle Schemas
class PerformanceReviewCycleBase(BaseModel):
    employee_id: uuid.UUID
    review_period_start: date
    review_period_end: date
    review_type: str  # annual, quarterly, probation


class PerformanceReviewCycleCreate(PerformanceReviewCycleBase):
    # Optionally specify evaluators
    supervisor_id: Optional[uuid.UUID] = None
    peer_ids: Optional[List[uuid.UUID]] = None
    subordinate_ids: Optional[List[uuid.UUID]] = None


class PerformanceReviewCycleUpdate(BaseModel):
    status: Optional[str] = None
    final_rating: Optional[int] = None
    final_strengths: Optional[str] = None
    final_areas_for_improvement: Optional[str] = None
    final_development_plan: Optional[str] = None
    employee_comments: Optional[str] = None


class PerformanceReviewCycleResponse(PerformanceReviewCycleBase):
    id: uuid.UUID
    status: str
    final_rating: Optional[int] = None
    final_strengths: Optional[str] = None
    final_areas_for_improvement: Optional[str] = None
    final_development_plan: Optional[str] = None
    employee_comments: Optional[str] = None
    acknowledged_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Performance Evaluation Schemas
class PerformanceEvaluationBase(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    achievements: Optional[str] = None
    recommendations: Optional[str] = None
    technical_skills: Optional[int] = Field(None, ge=1, le=5)
    communication: Optional[int] = Field(None, ge=1, le=5)
    teamwork: Optional[int] = Field(None, ge=1, le=5)
    leadership: Optional[int] = Field(None, ge=1, le=5)
    problem_solving: Optional[int] = Field(None, ge=1, le=5)


class PerformanceEvaluationSubmit(PerformanceEvaluationBase):
    """Schema for submitting an evaluation"""
    pass


class PerformanceEvaluationResponse(PerformanceEvaluationBase):
    id: uuid.UUID
    review_cycle_id: uuid.UUID
    evaluator_id: uuid.UUID
    evaluator_type: str
    status: str
    submitted_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# 360-degree Review Summary
class Review360Summary(BaseModel):
    review_cycle_id: uuid.UUID
    employee_id: uuid.UUID
    employee_name: str
    review_period: str
    status: str
    
    # Evaluation status
    total_evaluations: int
    completed_evaluations: int
    pending_evaluations: int
    
    # Evaluations by type
    supervisor_evaluation: Optional[PerformanceEvaluationResponse] = None
    peer_evaluations: List[PerformanceEvaluationResponse] = []
    subordinate_evaluations: List[PerformanceEvaluationResponse] = []
    self_evaluation: Optional[PerformanceEvaluationResponse] = None
    
    # Aggregated ratings
    average_rating: Optional[float] = None
    supervisor_rating: Optional[int] = None
    peer_average_rating: Optional[float] = None
    subordinate_average_rating: Optional[float] = None
    self_rating: Optional[int] = None
    
    # Final results
    final_rating: Optional[int] = None
    final_strengths: Optional[str] = None
    final_areas_for_improvement: Optional[str] = None
    final_development_plan: Optional[str] = None


# Performance Goal Schemas (for backwards compatibility)
class GoalCreate(BaseModel):
    title: str
    description: str
    target_date: date


class PerformanceGoalBase(BaseModel):
    employee_id: uuid.UUID
    title: str
    description: str
    category: Optional[str] = None
    start_date: date
    target_date: date


class PerformanceGoalCreate(PerformanceGoalBase):
    pass


class PerformanceGoalResponse(PerformanceGoalBase):
    id: uuid.UUID
    status: str
    progress_percentage: int
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Review Create (for backwards compatibility)
class ReviewCreate(BaseModel):
    employee_id: uuid.UUID
    review_period_start: date
    review_period_end: date
    review_type: str
