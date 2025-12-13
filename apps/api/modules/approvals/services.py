"""
Approval Workflow Module - Service Layer
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from modules.approvals.repositories import ApprovalRequestRepository, ApprovalDelegationRepository
from modules.approvals.schemas import (
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalRequestResponse,
    ApprovalDelegationCreate, ApprovalDelegationUpdate, ApprovalDelegationResponse,
    ApprovalStats
)
from modules.approvals.models import ApprovalStatus, ApprovalType
from core.exceptions import NotFoundException, BadRequestException


class ApprovalService:
    """Service for approval workflow operations"""
    
    def __init__(self, db: AsyncSession):
        self.approval_repo = ApprovalRequestRepository(db)
        self.delegation_repo = ApprovalDelegationRepository(db)
    
    async def create_approval_request(
        self,
        request_data: ApprovalRequestCreate,
        supervisor_id: uuid.UUID
    ) -> ApprovalRequestResponse:
        """Create a new approval request"""
        # Check if there's an active delegation
        delegate_id = await self.delegation_repo.get_active_delegate(supervisor_id)
        approver_id = delegate_id if delegate_id else supervisor_id
        
        approval = await self.approval_repo.create(request_data, approver_id)
        return ApprovalRequestResponse.model_validate(approval)
    
    async def get_approval_request(self, approval_id: uuid.UUID) -> ApprovalRequestResponse:
        """Get approval request by ID"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        return ApprovalRequestResponse.model_validate(approval)
    
    async def get_approval_by_request(
        self,
        request_type: ApprovalType,
        request_id: uuid.UUID
    ) -> Optional[ApprovalRequestResponse]:
        """Get approval request by related entity"""
        approval = await self.approval_repo.get_by_request(request_type, request_id)
        if approval:
            return ApprovalRequestResponse.model_validate(approval)
        return None
    
    async def get_pending_approvals(self, approver_id: uuid.UUID) -> List[ApprovalRequestResponse]:
        """Get all pending approvals for an approver"""
        approvals = await self.approval_repo.get_pending_for_approver(approver_id)
        return [ApprovalRequestResponse.model_validate(a) for a in approvals]
    
    async def get_employee_requests(self, employee_id: uuid.UUID) -> List[ApprovalRequestResponse]:
        """Get all approval requests submitted by an employee"""
        approvals = await self.approval_repo.get_by_employee(employee_id)
        return [ApprovalRequestResponse.model_validate(a) for a in approvals]
    
    async def approve_request(
        self,
        approval_id: uuid.UUID,
        approver_id: uuid.UUID,
        comments: Optional[str] = None,
        is_hr_override: bool = False
    ) -> ApprovalRequestResponse:
        """Approve a request"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        # Allow HR admin override (permission check should be done at route level)
        if not is_hr_override and approval.approver_id != approver_id:
            raise BadRequestException("You are not authorized to approve this request")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("This request has already been reviewed")
        
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.APPROVED, comments=comments)
        updated = await self.approval_repo.update(approval_id, update_data)
        return ApprovalRequestResponse.model_validate(updated)
    
    async def reject_request(
        self,
        approval_id: uuid.UUID,
        approver_id: uuid.UUID,
        comments: Optional[str] = None,
        is_hr_override: bool = False
    ) -> ApprovalRequestResponse:
        """Reject a request"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        # Allow HR admin override (permission check should be done at route level)
        if not is_hr_override and approval.approver_id != approver_id:
            raise BadRequestException("You are not authorized to reject this request")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("This request has already been reviewed")
        
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.REJECTED, comments=comments)
        updated = await self.approval_repo.update(approval_id, update_data)
        return ApprovalRequestResponse.model_validate(updated)
    
    async def cancel_request(self, approval_id: uuid.UUID, employee_id: uuid.UUID) -> ApprovalRequestResponse:
        """Cancel a pending request (by employee who submitted it)"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        if approval.employee_id != employee_id:
            raise BadRequestException("You can only cancel your own requests")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("Only pending requests can be cancelled")
        
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.CANCELLED)
        updated = await self.approval_repo.update(approval_id, update_data)
        return ApprovalRequestResponse.model_validate(updated)
    
    async def get_approval_stats(self, approver_id: uuid.UUID) -> ApprovalStats:
        """Get approval statistics for dashboard"""
        stats = await self.approval_repo.get_stats_for_approver(approver_id)
        return ApprovalStats(**stats)
    
    # Delegation methods
    async def create_delegation(self, delegation_data: ApprovalDelegationCreate) -> ApprovalDelegationResponse:
        """Create a new delegation"""
        if delegation_data.start_date >= delegation_data.end_date:
            raise BadRequestException("End date must be after start date")
        
        delegation = await self.delegation_repo.create(delegation_data)
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def get_delegation(self, delegation_id: uuid.UUID) -> ApprovalDelegationResponse:
        """Get delegation by ID"""
        delegation = await self.delegation_repo.get_by_id(delegation_id)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def get_supervisor_delegations(self, supervisor_id: uuid.UUID) -> List[ApprovalDelegationResponse]:
        """Get all delegations for a supervisor"""
        delegations = await self.delegation_repo.get_by_supervisor(supervisor_id)
        return [ApprovalDelegationResponse.model_validate(d) for d in delegations]
    
    async def update_delegation(
        self,
        delegation_id: uuid.UUID,
        update_data: ApprovalDelegationUpdate
    ) -> ApprovalDelegationResponse:
        """Update delegation"""
        delegation = await self.delegation_repo.update(delegation_id, update_data)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def deactivate_delegation(self, delegation_id: uuid.UUID) -> ApprovalDelegationResponse:
        """Deactivate a delegation"""
        delegation = await self.delegation_repo.deactivate(delegation_id)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
