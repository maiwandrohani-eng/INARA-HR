"""
Employee Files Module - Database Models
Personal file management, contracts, documents, extensions, resignations
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class DocumentCategory(str, enum.Enum):
    """Document category types"""
    CONTRACT = "contract"
    CONTRACT_EXTENSION = "contract_extension"
    EDUCATIONAL = "educational"
    REFERENCE_CHECK = "reference_check"
    INTERVIEW_RECORD = "interview_record"
    BACKGROUND_CHECK = "background_check"
    ID_DOCUMENT = "id_document"
    BANK_DETAILS = "bank_details"
    EMERGENCY_CONTACT = "emergency_contact"
    RESIGNATION = "resignation"
    TERMINATION = "termination"
    PERFORMANCE_REVIEW = "performance_review"
    DISCIPLINARY = "disciplinary"
    TRAINING_CERTIFICATE = "training_certificate"
    OTHER = "other"


class ContractStatus(str, enum.Enum):
    """Employment contract status"""
    DRAFT = "draft"
    ACTIVE = "active"
    EXTENDED = "extended"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class ExtensionStatus(str, enum.Enum):
    """Contract extension status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ResignationStatus(str, enum.Enum):
    """Resignation status"""
    SUBMITTED = "submitted"
    ACCEPTED_BY_SUPERVISOR = "accepted_by_supervisor"
    ACCEPTED_BY_HR = "accepted_by_hr"
    ACCEPTED_BY_CEO = "accepted_by_ceo"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class PersonalFileDocument(Base):
    """Employee personal file documents"""
    __tablename__ = "personal_file_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    category = Column(SQLEnum(DocumentCategory), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)  # Path to stored file
    file_name = Column(String(255), nullable=False)
    file_size = Column(Numeric)  # Size in bytes
    mime_type = Column(String(100))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_confidential = Column(Boolean, default=True)
    expiry_date = Column(Date)  # For documents like visas, certifications
    notes = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Multi-tenancy
    country_code = Column(String(2), index=True)
    
    # Relationships - Note: using foreign_keys only, not back_populates to avoid conflict with Employee.documents
    employee = relationship("Employee", foreign_keys=[employee_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])


class EmploymentContract(Base):
    """Employment contracts and their history"""
    __tablename__ = "employment_contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    contract_number = Column(String(50), unique=True, nullable=False)
    
    # Contract details from the agreement template
    position_title = Column(String(255), nullable=False)
    location = Column(String(255))
    contract_type = Column(String(100))  # Annual, Fixed-term, etc.
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    signed_date = Column(Date)
    
    # Compensation
    monthly_salary = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)
    
    # Performance reviews
    june_review_date = Column(Date)
    december_review_date = Column(Date)
    june_review_outcome = Column(String(50))
    december_review_outcome = Column(String(50))
    
    # Termination
    termination_date = Column(Date)
    termination_reason = Column(Text)
    notice_period_days = Column(Numeric, default=30)
    
    # Document reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("personal_file_documents.id"))
    
    # Tracking
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Multi-tenancy
    country_code = Column(String(2), index=True)
    
    # Relationships - Note: Employee.contracts already exists, check if it points here or the old Contract model
    employee = relationship("Employee", foreign_keys=[employee_id])
    document = relationship("PersonalFileDocument")
    creator = relationship("User", foreign_keys=[created_by])
    extensions = relationship("ContractExtension", back_populates="contract")


class ContractExtension(Base):
    """Contract extensions/amendments"""
    __tablename__ = "contract_extensions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("employment_contracts.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    # Extension details
    extension_number = Column(String(50), unique=True, nullable=False)
    new_start_date = Column(Date, nullable=False)
    new_end_date = Column(Date, nullable=False)
    
    # Salary changes (if any)
    new_monthly_salary = Column(Numeric(12, 2))
    salary_change_reason = Column(Text)
    
    # Other changes
    new_position_title = Column(String(255))
    new_location = Column(String(255))
    terms_changes = Column(Text)  # Description of any terms changes
    
    # Status and signatures
    status = Column(SQLEnum(ExtensionStatus), default=ExtensionStatus.PENDING)
    employee_accepted_at = Column(DateTime)
    employee_signature_ip = Column(String(45))  # Track IP for audit
    
    # Notifications
    notified_at = Column(DateTime)
    reminder_sent_at = Column(DateTime)
    expires_at = Column(DateTime)  # When the acceptance offer expires
    
    # Document
    document_id = Column(UUID(as_uuid=True), ForeignKey("personal_file_documents.id"))
    
    # Tracking
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Multi-tenancy
    country_code = Column(String(2), index=True)
    
    # Relationships
    contract = relationship("EmploymentContract", back_populates="extensions")
    employee = relationship("Employee", foreign_keys=[employee_id])
    creator = relationship("User", foreign_keys=[created_by])
    document = relationship("PersonalFileDocument")


class Resignation(Base):
    """Employee resignations"""
    __tablename__ = "resignations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    resignation_number = Column(String(50), unique=True, nullable=False)
    
    # Resignation details
    resignation_date = Column(Date, nullable=False)  # Date of submission
    intended_last_working_day = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    notice_period_days = Column(Numeric, default=30)
    
    # Status workflow
    status = Column(SQLEnum(ResignationStatus), default=ResignationStatus.SUBMITTED)
    
    # Approvals
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    supervisor_accepted_at = Column(DateTime)
    supervisor_comments = Column(Text)
    
    hr_accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    hr_accepted_at = Column(DateTime)
    hr_comments = Column(Text)
    
    ceo_accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    ceo_accepted_at = Column(DateTime)
    ceo_comments = Column(Text)
    
    # Final details
    approved_last_working_day = Column(Date)
    exit_interview_completed = Column(Boolean, default=False)
    exit_interview_date = Column(Date)
    
    # Document
    document_id = Column(UUID(as_uuid=True), ForeignKey("personal_file_documents.id"))
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft delete (in case of withdrawal)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Multi-tenancy
    country_code = Column(String(2), index=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="resignations")
    supervisor = relationship("Employee", foreign_keys=[supervisor_id])
    hr_user = relationship("User", foreign_keys=[hr_accepted_by])
    ceo_user = relationship("User", foreign_keys=[ceo_accepted_by])
    document = relationship("PersonalFileDocument")
