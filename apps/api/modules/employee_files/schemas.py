"""
Pydantic schemas for employee files module
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from .models import DocumentCategory, ContractStatus, ExtensionStatus, ResignationStatus


# ============= Document Schemas =============

class DocumentBase(BaseModel):
    category: DocumentCategory
    title: str
    description: Optional[str] = None
    is_confidential: bool = False
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class DocumentCreate(DocumentBase):
    employee_id: UUID
    file_name: str
    file_size: int
    mime_type: str


class DocumentResponse(DocumentBase):
    id: UUID
    employee_id: UUID
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_by: UUID
    uploaded_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# ============= Contract Schemas =============

class ContractBase(BaseModel):
    contract_number: str
    position_title: str
    location: str
    contract_type: str
    start_date: date
    end_date: date
    monthly_salary: float
    currency: str = "USD"
    notice_period_days: int = 30
    signed_date: Optional[date] = None


class ContractCreate(ContractBase):
    employee_id: UUID
    document_id: Optional[UUID] = None


class ContractUpdate(BaseModel):
    position_title: Optional[str] = None
    location: Optional[str] = None
    monthly_salary: Optional[float] = None
    end_date: Optional[date] = None
    june_review_date: Optional[date] = None
    december_review_date: Optional[date] = None
    june_review_outcome: Optional[str] = None
    december_review_outcome: Optional[str] = None
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None


class ContractResponse(ContractBase):
    id: UUID
    employee_id: UUID
    status: ContractStatus
    document_id: Optional[UUID] = None
    june_review_date: Optional[date] = None
    december_review_date: Optional[date] = None
    june_review_outcome: Optional[str] = None
    december_review_outcome: Optional[str] = None
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    contracts: List[ContractResponse]
    total: int


# ============= Extension Schemas =============

class ExtensionBase(BaseModel):
    new_start_date: date
    new_end_date: date
    new_monthly_salary: Optional[float] = None
    salary_change_reason: Optional[str] = None
    new_position_title: Optional[str] = None
    new_location: Optional[str] = None
    terms_changes: Optional[str] = None


class ExtensionCreate(ExtensionBase):
    contract_id: UUID
    employee_id: UUID
    document_id: Optional[UUID] = None


class ExtensionAccept(BaseModel):
    employee_signature_ip: str


class ExtensionResponse(ExtensionBase):
    id: UUID
    contract_id: UUID
    employee_id: UUID
    extension_number: int
    status: ExtensionStatus
    document_id: Optional[UUID] = None
    employee_accepted_at: Optional[datetime] = None
    employee_signature_ip: Optional[str] = None
    notified_at: Optional[datetime] = None
    reminder_sent_at: Optional[datetime] = None
    expires_at: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExtensionListResponse(BaseModel):
    extensions: List[ExtensionResponse]
    total: int


# ============= Resignation Schemas =============

class ResignationBase(BaseModel):
    resignation_date: date
    intended_last_working_day: date
    reason: str
    notice_period_days: int = 30


class ResignationCreate(ResignationBase):
    employee_id: UUID
    supervisor_id: Optional[UUID] = None
    document_id: Optional[UUID] = None


class ResignationApprove(BaseModel):
    comments: Optional[str] = None


class ResignationCEOApprove(ResignationApprove):
    approved_last_working_day: date


class ResignationComplete(BaseModel):
    exit_interview_date: Optional[date] = None


class ResignationResponse(ResignationBase):
    id: UUID
    employee_id: UUID
    resignation_number: str
    supervisor_id: Optional[UUID] = None
    status: ResignationStatus
    
    # Supervisor approval
    supervisor_accepted_at: Optional[datetime] = None
    supervisor_comments: Optional[str] = None
    
    # HR approval
    hr_accepted_by: Optional[UUID] = None
    hr_accepted_at: Optional[datetime] = None
    hr_comments: Optional[str] = None
    
    # CEO approval
    ceo_accepted_by: Optional[UUID] = None
    ceo_accepted_at: Optional[datetime] = None
    ceo_comments: Optional[str] = None
    approved_last_working_day: Optional[date] = None
    
    # Exit process
    exit_interview_completed: bool = False
    exit_interview_date: Optional[date] = None
    
    document_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResignationListResponse(BaseModel):
    resignations: List[ResignationResponse]
    total: int


# ============= Personal File Summary =============

class PersonalFileSummary(BaseModel):
    """Summary of an employee's personal file"""
    employee_id: UUID
    employee_name: str
    employee_number: str
    
    # Counts
    total_documents: int
    active_contracts: int
    pending_extensions: int
    total_resignations: int
    
    # Current status
    current_contract: Optional[ContractResponse] = None
    current_contract_end_date: Optional[date] = None
    days_until_contract_end: Optional[int] = None
    
    # Recent activity
    recent_documents: List[DocumentResponse] = []
    pending_actions: List[str] = []
    
    class Config:
        from_attributes = True


# ============= Notification Schemas =============

class PendingExtensionNotification(BaseModel):
    """Notification for pending contract extension"""
    extension_id: UUID
    employee_id: UUID
    employee_name: str
    new_start_date: date
    new_end_date: date
    expires_at: Optional[date] = None
    days_until_expiry: Optional[int] = None
    new_monthly_salary: Optional[float] = None
    salary_change_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class PendingResignationNotification(BaseModel):
    """Notification for pending resignation approval"""
    resignation_id: UUID
    employee_id: UUID
    employee_name: str
    resignation_date: date
    intended_last_working_day: date
    status: ResignationStatus
    days_since_submission: int
    pending_with: str  # "Supervisor", "HR", "CEO"
    
    class Config:
        from_attributes = True
