"""
Succession Planning Module - Models
Key position identification, successor planning, readiness assessment
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class KeyPosition(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Critical/key positions in the organization"""
    __tablename__ = "key_positions"
    
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id'), nullable=False)
    
    # Position criticality
    criticality_level = Column(String(20), nullable=False)  # critical, high, medium
    business_impact = Column(Text, nullable=True)
    
    # Risk assessment
    vacancy_risk = Column(String(20), nullable=True)  # low, medium, high, critical
    current_incumbent_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Succession status
    has_successor = Column(Boolean, default=False, nullable=False)
    succession_status = Column(String(20), default="not_planned")  # not_planned, identified, developing, ready
    
    # Relationships
    position = relationship("Position", backref="key_position")
    current_incumbent = relationship("Employee", foreign_keys=[current_incumbent_id], backref="key_positions_held")
    successors = relationship("Successor", back_populates="key_position", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KeyPosition {self.position_id} - {self.criticality_level}>"


class Successor(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Successor candidates for key positions"""
    __tablename__ = "successors"
    
    key_position_id = Column(UUID(as_uuid=True), ForeignKey('key_positions.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Successor details
    successor_type = Column(String(20), nullable=False)  # primary, secondary, backup
    readiness_level = Column(String(20), nullable=False)  # ready_now, ready_1yr, ready_2yr, needs_development
    
    # Assessment
    readiness_score = Column(Integer, nullable=True)  # 1-100
    skills_gap_analysis = Column(Text, nullable=True)
    development_needs = Column(Text, nullable=True)
    
    # Development plan
    development_plan_created = Column(Boolean, default=False, nullable=False)
    development_plan_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    key_position = relationship("KeyPosition", back_populates="successors")
    employee = relationship("Employee", backref="successor_positions")
    
    def __repr__(self):
        return f"<Successor {self.employee_id} for {self.key_position_id}>"


class SuccessionPlan(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Formal succession plan document"""
    __tablename__ = "succession_plans"
    
    key_position_id = Column(UUID(as_uuid=True), ForeignKey('key_positions.id'), nullable=False)
    
    # Plan details
    plan_name = Column(String(200), nullable=False)
    plan_date = Column(Date, nullable=False)
    review_date = Column(Date, nullable=True)
    
    # Plan status
    status = Column(String(20), default="draft")  # draft, active, archived
    
    # Succession timeline
    expected_transition_date = Column(Date, nullable=True)
    
    # Risk mitigation
    risk_mitigation_strategies = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Relationships
    key_position = relationship("KeyPosition", backref="succession_plans")
    approver = relationship("Employee", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<SuccessionPlan {self.plan_name}>"

