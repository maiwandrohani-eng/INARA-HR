"""
Safeguarding & Misconduct Module - Models
Case management for safeguarding issues and misconduct
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class SafeguardingCase(BaseModel, TenantMixin, AuditMixin, Base):
    """Safeguarding and misconduct cases"""
    __tablename__ = "safeguarding_cases"
    
    case_number = Column(String(100), unique=True, nullable=False)
    
    # Case Details
    case_type = Column(String(50), nullable=False)  # safeguarding, misconduct, harassment, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    reported_date = Column(Date, nullable=False)
    incident_date = Column(Date, nullable=True)
    
    # Parties Involved (anonymized for sensitivity)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)  # Person accused
    
    # Case Information
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    
    # Investigation
    investigator_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    investigation_status = Column(String(20), default="pending")  # pending, ongoing, completed
    investigation_findings = Column(Text, nullable=True)
    
    # Resolution
    status = Column(String(20), default="open")  # open, investigating, resolved, closed
    resolution_date = Column(Date, nullable=True)
    actions_taken = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    
    # Confidentiality
    confidentiality_level = Column(String(20), default="high")  # low, medium, high
    
    # Documents
    supporting_documents = Column(Text, nullable=True)  # JSON array of URLs
