"""
Approval Workflow Module - Repository Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid

from modules.approvals.models import ApprovalRequest, ApprovalDelegation, ApprovalStatus, ApprovalType
from modules.approvals.schemas import (
    ApprovalRequestCreate, ApprovalRequestUpdate,
    ApprovalDelegationCreate, ApprovalDelegationUpdate
)


class ApprovalRequestRepository:
    """Repository for approval request operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, approval_data: ApprovalRequestCreate, approver_id: uuid.UUID) -> ApprovalRequest:
        """Create a new approval request"""
        approval = ApprovalRequest(
            **approval_data.model_dump(),
            approver_id=approver_id
        )
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
    
    async def get_by_id(self, approval_id: uuid.UUID) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        result = await self.db.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.employee),
                selectinload(ApprovalRequest.approver)
            )
            .where(ApprovalRequest.id == approval_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_request(self, request_type: ApprovalType, request_id: uuid.UUID) -> Optional[ApprovalRequest]:
        """Get approval request by related entity"""
        result = await self.db.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.employee),
                selectinload(ApprovalRequest.approver)
            )
            .where(
                and_(
                    ApprovalRequest.request_type == request_type,
                    ApprovalRequest.request_id == request_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_pending_for_approver(self, approver_id: uuid.UUID) -> List[ApprovalRequest]:
        """Get all pending approval requests for an approver"""
        result = await self.db.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.employee),
                selectinload(ApprovalRequest.approver)
            )
            .where(
                and_(
                    ApprovalRequest.approver_id == approver_id,
                    ApprovalRequest.status == ApprovalStatus.PENDING
                )
            )
            .order_by(ApprovalRequest.submitted_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[ApprovalRequest]:
        """Get all approval requests submitted by an employee"""
        result = await self.db.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.employee),
                selectinload(ApprovalRequest.approver)
            )
            .where(ApprovalRequest.employee_id == employee_id)
            .order_by(ApprovalRequest.submitted_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, approval_id: uuid.UUID, update_data: ApprovalRequestUpdate) -> Optional[ApprovalRequest]:
        """Update approval request (approve/reject)"""
        approval = await self.get_by_id(approval_id)
        if not approval:
            return None
        
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(approval, key, value)
        
        if update_data.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            approval.reviewed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
    
    async def get_stats_for_approver(self, approver_id: uuid.UUID) -> dict:
        """Get approval statistics for an approver"""
        # Total pending
        total_result = await self.db.execute(
            select(func.count(ApprovalRequest.id))
            .where(
                and_(
                    ApprovalRequest.approver_id == approver_id,
                    ApprovalRequest.status == ApprovalStatus.PENDING
                )
            )
        )
        total_pending = total_result.scalar() or 0
        
        # Pending by type
        stats = {"total_pending": total_pending}
        
        for approval_type in ApprovalType:
            type_result = await self.db.execute(
                select(func.count(ApprovalRequest.id))
                .where(
                    and_(
                        ApprovalRequest.approver_id == approver_id,
                        ApprovalRequest.status == ApprovalStatus.PENDING,
                        ApprovalRequest.request_type == approval_type
                    )
                )
            )
            count = type_result.scalar() or 0
            stats[f"{approval_type.value}_pending"] = count
        
        return stats


class ApprovalDelegationRepository:
    """Repository for approval delegation operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, delegation_data: ApprovalDelegationCreate) -> ApprovalDelegation:
        """Create a new delegation"""
        delegation = ApprovalDelegation(**delegation_data.model_dump())
        self.db.add(delegation)
        await self.db.commit()
        await self.db.refresh(delegation)
        return delegation
    
    async def get_by_id(self, delegation_id: uuid.UUID) -> Optional[ApprovalDelegation]:
        """Get delegation by ID"""
        result = await self.db.execute(
            select(ApprovalDelegation)
            .options(
                selectinload(ApprovalDelegation.supervisor),
                selectinload(ApprovalDelegation.delegate)
            )
            .where(ApprovalDelegation.id == delegation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_for_supervisor(self, supervisor_id: uuid.UUID) -> List[ApprovalDelegation]:
        """Get active delegations for a supervisor"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(ApprovalDelegation)
            .options(
                selectinload(ApprovalDelegation.supervisor),
                selectinload(ApprovalDelegation.delegate)
            )
            .where(
                and_(
                    ApprovalDelegation.supervisor_id == supervisor_id,
                    ApprovalDelegation.is_active == "true",
                    ApprovalDelegation.start_date <= now,
                    ApprovalDelegation.end_date >= now
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_active_delegate(self, supervisor_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Get the currently active delegate for a supervisor"""
        delegations = await self.get_active_for_supervisor(supervisor_id)
        if delegations:
            return delegations[0].delegate_id
        return None
    
    async def get_by_supervisor(self, supervisor_id: uuid.UUID) -> List[ApprovalDelegation]:
        """Get all delegations for a supervisor"""
        result = await self.db.execute(
            select(ApprovalDelegation)
            .options(
                selectinload(ApprovalDelegation.supervisor),
                selectinload(ApprovalDelegation.delegate)
            )
            .where(ApprovalDelegation.supervisor_id == supervisor_id)
            .order_by(ApprovalDelegation.start_date.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, delegation_id: uuid.UUID, update_data: ApprovalDelegationUpdate) -> Optional[ApprovalDelegation]:
        """Update delegation"""
        delegation = await self.get_by_id(delegation_id)
        if not delegation:
            return None
        
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(delegation, key, value)
        
        await self.db.commit()
        await self.db.refresh(delegation)
        return delegation
    
    async def deactivate(self, delegation_id: uuid.UUID) -> Optional[ApprovalDelegation]:
        """Deactivate a delegation"""
        return await self.update(delegation_id, ApprovalDelegationUpdate(is_active="false"))
