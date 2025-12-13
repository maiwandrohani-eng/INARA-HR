"""
Performance Management Module - Models
Goals, reviews, PIPs (Performance Improvement Plans)
360-degree performance reviews
"""

from sqlalchemy import Column, String, Date, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class ReviewerType(str, enum.Enum):
    """Type of reviewer in 360-degree review"""
    SUPERVISOR = "supervisor"
    PEER = "peer"
    SUBORDINATE = "subordinate"
    SELF = "self"


class PerformanceGoal(BaseModel, TenantMixin, AuditMixin, Base):
    """Employee performance goals"""
    __tablename__ = "performance_goals"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # Individual, Team, Organizational
    
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    
    status = Column(String(20), default="in_progress")  # in_progress, achieved, not_achieved, cancelled
    progress_percentage = Column(Integer, default=0)
    
    notes = Column(Text, nullable=True)


class PerformanceReviewCycle(BaseModel, TenantMixin, AuditMixin, Base):
    """360-degree performance review cycle"""
    __tablename__ = "performance_review_cycles"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    
    review_type = Column(String(50), nullable=False)  # annual, quarterly, probation
    
    # 360-degree review status
    status = Column(String(20), default="in_progress")  # in_progress, completed, acknowledged
    
    # Aggregated results
    final_rating = Column(Integer, nullable=True)  # 1-5 scale (average of all evaluations)
    final_strengths = Column(Text, nullable=True)
    final_areas_for_improvement = Column(Text, nullable=True)
    final_development_plan = Column(Text, nullable=True)
    
    # Employee acknowledgment
    employee_comments = Column(Text, nullable=True)
    acknowledged_date = Column(Date, nullable=True)
    
    # Relationships
    evaluations = relationship("PerformanceEvaluation", back_populates="review_cycle", cascade="all, delete-orphan")


class PerformanceEvaluation(BaseModel, TenantMixin, AuditMixin, Base):
    """Individual evaluation within a 360-degree review"""
    __tablename__ = "performance_evaluations"
    
    review_cycle_id = Column(UUID(as_uuid=True), ForeignKey('performance_review_cycles.id'), nullable=False)
    
    # Who is evaluating
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    evaluator_type = Column(SQLEnum(ReviewerType), nullable=False)
    
    # Evaluation content
    rating = Column(Integer, nullable=True)  # 1-5 scale
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Competency ratings (can be expanded)
    technical_skills = Column(Integer, nullable=True)  # 1-5
    communication = Column(Integer, nullable=True)  # 1-5
    teamwork = Column(Integer, nullable=True)  # 1-5
    leadership = Column(Integer, nullable=True)  # 1-5
    problem_solving = Column(Integer, nullable=True)  # 1-5
    
    # Status
    status = Column(String(20), default="pending")  # pending, submitted, approved
    submitted_date = Column(Date, nullable=True)
    
    # Relationships
    review_cycle = relationship("PerformanceReviewCycle", back_populates="evaluations")
    
    # For backwards compatibility, keep this alias
    __table_args__ = (
        {'extend_existing': True}
    )


# Alias for backwards compatibility
PerformanceReview = PerformanceReviewCycle


class PerformanceImprovementPlan(BaseModel, TenantMixin, AuditMixin, Base):
    """PIP - Performance Improvement Plan"""
    __tablename__ = "performance_improvement_plans"
    
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    concerns = Column(Text, nullable=False)
    expected_improvements = Column(Text, nullable=False)
    support_provided = Column(Text, nullable=True)
    
    status = Column(String(20), default="active")  # active, successful, unsuccessful, cancelled
    outcome = Column(Text, nullable=True)
    completion_date = Column(Date, nullable=True)
