"""Enhanced Exit Management Module - Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


# Exit Interview Schemas
class ExitInterviewBase(BaseModel):
    resignation_id: uuid.UUID
    employee_id: uuid.UUID
    conducted_by_id: uuid.UUID
    interview_date: date
    interview_type: str = "face_to_face"
    q1_reason_for_leaving: Optional[str] = None
    q2_overall_satisfaction: Optional[int] = None
    q3_management_rating: Optional[int] = None
    q4_work_environment_rating: Optional[int] = None
    q5_would_recommend: Optional[bool] = None
    q6_improvement_suggestions: Optional[str] = None
    q7_positive_feedback: Optional[str] = None
    q8_future_plans: Optional[str] = None
    overall_feedback: Optional[str] = None
    feedback_summary: Optional[str] = None
    is_complete: bool = False
    is_confidential: bool = True


class ExitInterviewCreate(ExitInterviewBase):
    pass


class ExitInterviewResponse(ExitInterviewBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Exit Checklist Schemas
class ExitChecklistBase(BaseModel):
    resignation_id: uuid.UUID
    employee_id: uuid.UUID
    checklist_item: str
    category: str
    assigned_to: Optional[uuid.UUID] = None
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    completed_by: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    verification_required: bool = False
    verified_by: Optional[uuid.UUID] = None
    verified_date: Optional[datetime] = None
    is_critical: bool = False
    due_date: Optional[date] = None


class ExitChecklistCreate(ExitChecklistBase):
    pass


class ExitChecklistResponse(ExitChecklistBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True


# Knowledge Transfer Schemas
class KnowledgeTransferBase(BaseModel):
    resignation_id: uuid.UUID
    employee_id: uuid.UUID
    transferred_to_id: Optional[uuid.UUID] = None
    transfer_date: Optional[date] = None
    knowledge_area: str
    description: str
    document_url: Optional[str] = None
    resources: Optional[str] = None
    is_complete: bool = False
    verified_by: Optional[uuid.UUID] = None
    verified_date: Optional[datetime] = None


class KnowledgeTransferCreate(KnowledgeTransferBase):
    pass


class KnowledgeTransferResponse(KnowledgeTransferBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

