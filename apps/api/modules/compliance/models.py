"""
Compliance & Legal Module - Models
Policy acknowledgments, training compliance, regulatory tracking
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class Policy(BaseModel, TenantMixin, AuditMixin, Base):
    """Company policies and documents"""
    __tablename__ = "policies"
    
    title = Column(String(200), nullable=False)
    policy_type = Column(String(50), nullable=False)  # hr_policy, code_of_conduct, safety, data_protection, etc.
    version = Column(String(20), nullable=False)
    
    # Content
    content = Column(Text, nullable=True)
    document_url = Column(String(500), nullable=True)
    
    # Effective dates
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    requires_acknowledgment = Column(Boolean, default=True, nullable=False)
    
    # Applicability
    applicable_to = Column(String(50), default="all")  # all, department, role, specific_employees
    applicable_department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    applicable_role = Column(String(50), nullable=True)
    
    # Relationships
    department = relationship("Department", backref="policies")
    acknowledgments = relationship("PolicyAcknowledgment", back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Policy {self.title} v{self.version}>"


class PolicyAcknowledgment(BaseModel, TenantMixin, AuditMixin, Base):
    """Employee policy acknowledgments"""
    __tablename__ = "policy_acknowledgments"
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policies.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Acknowledgment details
    acknowledged_date = Column(DateTime, nullable=False)
    acknowledged_version = Column(String(20), nullable=False)
    
    # Status
    is_acknowledged = Column(Boolean, default=True, nullable=False)
    
    # IP address and device info (for audit)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    policy = relationship("Policy", back_populates="acknowledgments")
    employee = relationship("Employee", backref="policy_acknowledgments")
    
    def __repr__(self):
        return f"<PolicyAcknowledgment {self.policy_id} - {self.employee_id}>"


class ComplianceTraining(BaseModel, TenantMixin, AuditMixin, Base):
    """Compliance training requirements"""
    __tablename__ = "compliance_trainings"
    
    title = Column(String(200), nullable=False)
    training_type = Column(String(50), nullable=False)  # safety, harassment, data_protection, etc.
    description = Column(Text, nullable=True)
    
    # Training details
    duration_minutes = Column(String(20), nullable=True)
    training_url = Column(String(500), nullable=True)
    is_online = Column(Boolean, default=True, nullable=False)
    
    # Requirements
    required_for = Column(String(50), default="all")  # all, new_employees, department, role
    frequency = Column(String(50), nullable=True)  # once, annual, biannual, etc.
    
    # Due dates
    due_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    completions = relationship("TrainingCompletion", back_populates="compliance_training", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ComplianceTraining {self.title}>"


class TrainingCompletion(BaseModel, TenantMixin, AuditMixin, Base):
    """Training completion records"""
    __tablename__ = "training_completions"
    
    compliance_training_id = Column(UUID(as_uuid=True), ForeignKey('compliance_trainings.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Completion details
    completed_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Verification
    certificate_url = Column(String(500), nullable=True)
    score = Column(String(20), nullable=True)  # For tests/quizzes
    passed = Column(Boolean, nullable=True)
    
    # Relationships
    compliance_training = relationship("ComplianceTraining", back_populates="completions")
    employee = relationship("Employee", backref="training_completions")
    
    def __repr__(self):
        return f"<TrainingCompletion {self.compliance_training_id} - {self.employee_id}>"

