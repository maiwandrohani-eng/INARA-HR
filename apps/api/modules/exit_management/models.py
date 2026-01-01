"""
Enhanced Exit Management Module - Models
Exit interviews, exit checklists, knowledge transfer
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin, NoteMixin


class ExitInterview(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Exit interview records"""
    __tablename__ = "exit_interviews"
    
    resignation_id = Column(UUID(as_uuid=True), ForeignKey('resignations.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    conducted_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Interview details
    interview_date = Column(Date, nullable=False)
    interview_type = Column(String(50), default="face_to_face")  # face_to_face, phone, video, online_survey
    
    # Questions and responses
    q1_reason_for_leaving = Column(Text, nullable=True)
    q2_overall_satisfaction = Column(Integer, nullable=True)  # 1-10 scale
    q3_management_rating = Column(Integer, nullable=True)  # 1-10 scale
    q4_work_environment_rating = Column(Integer, nullable=True)  # 1-10 scale
    q5_would_recommend = Column(Boolean, nullable=True)
    q6_improvement_suggestions = Column(Text, nullable=True)
    q7_positive_feedback = Column(Text, nullable=True)
    q8_future_plans = Column(Text, nullable=True)
    
    # Overall feedback
    overall_feedback = Column(Text, nullable=True)
    feedback_summary = Column(Text, nullable=True)  # HR summary
    
    # Status
    is_complete = Column(Boolean, default=False, nullable=False)
    is_confidential = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    resignation = relationship("Resignation", backref="exit_interview")
    employee = relationship("Employee", foreign_keys=[employee_id], backref="exit_interviews")
    conducted_by = relationship("Employee", foreign_keys=[conducted_by_id])
    
    def __repr__(self):
        return f"<ExitInterview {self.employee_id} - {self.interview_date}>"


class ExitChecklist(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Exit checklist items and completion tracking"""
    __tablename__ = "exit_checklists"
    
    resignation_id = Column(UUID(as_uuid=True), ForeignKey('resignations.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Checklist item details
    checklist_item = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # it, hr, finance, security, knowledge_transfer, etc.
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Details (notes provided by NoteMixin)
    verification_required = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    
    # Priority
    is_critical = Column(Boolean, default=False, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Relationships
    resignation = relationship("Resignation", backref="exit_checklist_items")
    employee = relationship("Employee", foreign_keys=[employee_id], backref="exit_checklists")
    assignee = relationship("Employee", foreign_keys=[assigned_to])
    completer = relationship("Employee", foreign_keys=[completed_by])
    verifier = relationship("Employee", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<ExitChecklist {self.checklist_item} - {self.is_completed}>"


class KnowledgeTransfer(BaseModel, TenantMixin, AuditMixin, NoteMixin, Base):
    """Knowledge transfer documentation"""
    __tablename__ = "knowledge_transfers"
    
    resignation_id = Column(UUID(as_uuid=True), ForeignKey('resignations.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    transferred_to_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Knowledge transfer details
    transfer_date = Column(Date, nullable=True)
    knowledge_area = Column(String(200), nullable=False)  # project, process, client, system, etc.
    description = Column(Text, nullable=False)
    
    # Documents and resources
    document_url = Column(String(500), nullable=True)
    resources = Column(Text, nullable=True)  # JSON array of resources
    
    # Status
    is_complete = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    
    # Relationships
    resignation = relationship("Resignation", backref="knowledge_transfers")
    employee = relationship("Employee", foreign_keys=[employee_id], backref="knowledge_transfers_given")
    transferred_to = relationship("Employee", foreign_keys=[transferred_to_id], backref="knowledge_transfers_received")
    verifier = relationship("Employee", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<KnowledgeTransfer {self.knowledge_area}>"

