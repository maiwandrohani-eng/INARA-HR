"""
Approval Workflow Module - API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, get_current_user, require_hr_admin
from core.exceptions import NotFoundException, BadRequestException
from modules.auth.models import User
from modules.approvals.services import ApprovalService
from modules.approvals.schemas import (
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalRequestResponse,
    ApprovalDelegationCreate, ApprovalDelegationUpdate, ApprovalDelegationResponse,
    ApprovalStats
)
from modules.approvals.models import ApprovalType

router = APIRouter(prefix="/approvals", tags=["Approvals"])


# Approval Request endpoints
@router.post("/requests", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_request(
    request_data: ApprovalRequestCreate,
    supervisor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new approval request"""
    service = ApprovalService(db)
    try:
        return await service.create_approval_request(request_data, supervisor_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/requests/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval request by ID"""
    service = ApprovalService(db)
    try:
        return await service.get_approval_request(approval_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/requests/type/{request_type}/{request_id}", response_model=ApprovalRequestResponse)
async def get_approval_by_request(
    request_type: ApprovalType,
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval request by related entity"""
    service = ApprovalService(db)
    result = await service.get_approval_by_request(request_type, request_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return result


@router.get("/pending", response_model=List[ApprovalRequestResponse])
async def get_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending approvals for current user (as approver)"""
    service = ApprovalService(db)
    # Assuming current_user has employee relationship
    if not current_user.employee:
        return []
    return await service.get_pending_approvals(current_user.employee.id)


@router.get("/my-requests", response_model=List[ApprovalRequestResponse])
async def get_my_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all approval requests submitted by current user"""
    service = ApprovalService(db)
    if not current_user.employee:
        return []
    return await service.get_employee_requests(current_user.employee.id)


@router.post("/requests/{approval_id}/approve", response_model=ApprovalRequestResponse)
async def approve_request(
    approval_id: uuid.UUID,
    comments: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a request"""
    service = ApprovalService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    try:
        return await service.approve_request(approval_id, current_user.employee.id, comments)
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/requests/{approval_id}/reject", response_model=ApprovalRequestResponse)
async def reject_request(
    approval_id: uuid.UUID,
    comments: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a request"""
    service = ApprovalService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    try:
        return await service.reject_request(approval_id, current_user.employee.id, comments)
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/requests/{approval_id}/cancel", response_model=ApprovalRequestResponse)
async def cancel_request(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a pending request"""
    service = ApprovalService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    try:
        return await service.cancel_request(approval_id, current_user.employee.id)
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stats", response_model=ApprovalStats)
async def get_approval_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval statistics for dashboard"""
    service = ApprovalService(db)
    if not current_user.employee:
        return ApprovalStats(
            total_pending=0,
            leave_pending=0,
            travel_pending=0,
            timesheet_pending=0,
            performance_pending=0
        )
    return await service.get_approval_stats(current_user.employee.id)


# Delegation endpoints
@router.post("/delegations", response_model=ApprovalDelegationResponse, status_code=status.HTTP_201_CREATED)
async def create_delegation(
    delegation_data: ApprovalDelegationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new delegation"""
    service = ApprovalService(db)
    try:
        return await service.create_delegation(delegation_data)
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/delegations/{delegation_id}", response_model=ApprovalDelegationResponse)
async def get_delegation(
    delegation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delegation by ID"""
    service = ApprovalService(db)
    try:
        return await service.get_delegation(delegation_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/delegations", response_model=List[ApprovalDelegationResponse])
async def get_my_delegations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all delegations for current user"""
    service = ApprovalService(db)
    if not current_user.employee:
        return []
    return await service.get_supervisor_delegations(current_user.employee.id)


@router.patch("/delegations/{delegation_id}", response_model=ApprovalDelegationResponse)
async def update_delegation(
    delegation_id: uuid.UUID,
    update_data: ApprovalDelegationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update delegation"""
    service = ApprovalService(db)
    try:
        return await service.update_delegation(delegation_id, update_data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/requests/{approval_id}/deactivate", response_model=ApprovalDelegationResponse)
async def deactivate_delegation(
    delegation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate a delegation"""
    service = ApprovalService(db)
    try:
        return await service.deactivate_delegation(delegation_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# HR Admin Override Endpoints
@router.post("/admin/requests/{approval_id}/approve", response_model=ApprovalRequestResponse)
async def hr_override_approve(
    approval_id: uuid.UUID,
    comments: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    HR Admin override - Approve any request regardless of approver assignment
    Requires hr:admin permission
    """
    service = ApprovalService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    try:
        override_comments = f"[HR OVERRIDE] {comments if comments else 'Approved by HR Admin'}"
        return await service.approve_request(
            approval_id, 
            current_user.employee.id, 
            override_comments,
            is_hr_override=True
        )
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/admin/requests/{approval_id}/reject", response_model=ApprovalRequestResponse)
async def hr_override_reject(
    approval_id: uuid.UUID,
    comments: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    HR Admin override - Reject any request regardless of approver assignment
    Requires hr:admin permission
    """
    service = ApprovalService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    try:
        override_comments = f"[HR OVERRIDE] {comments if comments else 'Rejected by HR Admin'}"
        return await service.reject_request(
            approval_id, 
            current_user.employee.id, 
            override_comments,
            is_hr_override=True
        )
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
