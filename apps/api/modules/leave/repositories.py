"""
Leave & Attendance Module - Repository Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import uuid

from modules.leave.models import LeavePolicy, LeaveBalance, LeaveRequest, AttendanceRecord
from modules.leave.schemas import (
    LeavePolicyCreate, LeaveBalanceCreate, LeaveRequestCreate,
    LeaveRequestUpdate, AttendanceRecordCreate
)


class LeavePolicyRepository:
    """Repository for leave policy operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, policy_data: LeavePolicyCreate) -> LeavePolicy:
        """Create a new leave policy"""
        policy = LeavePolicy(**policy_data.model_dump())
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy
    
    async def get_by_id(self, policy_id: uuid.UUID) -> Optional[LeavePolicy]:
        """Get policy by ID"""
        result = await self.db.execute(
            select(LeavePolicy).where(LeavePolicy.id == policy_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[LeavePolicy]:
        """Get all leave policies"""
        result = await self.db.execute(select(LeavePolicy))
        return list(result.scalars().all())
    
    async def get_by_type(self, leave_type: str) -> Optional[LeavePolicy]:
        """Get policy by leave type"""
        result = await self.db.execute(
            select(LeavePolicy).where(LeavePolicy.leave_type == leave_type)
        )
        return result.scalar_one_or_none()


class LeaveBalanceRepository:
    """Repository for leave balance operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, balance_data: LeaveBalanceCreate) -> LeaveBalance:
        """Create a new leave balance"""
        balance = LeaveBalance(**balance_data.model_dump())
        self.db.add(balance)
        await self.db.commit()
        await self.db.refresh(balance)
        return balance
    
    async def get_by_employee_and_year(
        self,
        employee_id: uuid.UUID,
        year: str
    ) -> List[LeaveBalance]:
        """Get all leave balances for an employee in a year"""
        result = await self.db.execute(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.year == year
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_by_employee_type_year(
        self,
        employee_id: uuid.UUID,
        leave_type: str,
        year: str
    ) -> Optional[LeaveBalance]:
        """Get specific leave balance"""
        result = await self.db.execute(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type == leave_type,
                    LeaveBalance.year == year
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_balance(
        self,
        balance_id: uuid.UUID,
        used_days: Optional[Decimal] = None,
        pending_days: Optional[Decimal] = None
    ) -> Optional[LeaveBalance]:
        """Update leave balance"""
        balance = await self.db.get(LeaveBalance, balance_id)
        if not balance:
            return None
        
        if used_days is not None:
            balance.used_days = used_days
        if pending_days is not None:
            balance.pending_days = pending_days
        
        balance.available_days = balance.total_days - balance.used_days - balance.pending_days
        
        await self.db.commit()
        await self.db.refresh(balance)
        return balance


class LeaveRequestRepository:
    """Repository for leave request operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, request_data: LeaveRequestCreate, total_days: Decimal) -> LeaveRequest:
        """Create a new leave request"""
        leave_request = LeaveRequest(
            **request_data.model_dump(),
            total_days=total_days,
            status="pending"
        )
        self.db.add(leave_request)
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request
    
    async def get_by_id(self, request_id: uuid.UUID) -> Optional[LeaveRequest]:
        """Get leave request by ID"""
        result = await self.db.execute(
            select(LeaveRequest).where(LeaveRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[LeaveRequest]:
        """Get all leave requests for an employee"""
        result = await self.db.execute(
            select(LeaveRequest)
            .where(LeaveRequest.employee_id == employee_id)
            .order_by(LeaveRequest.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_pending_by_approver(self, approver_id: uuid.UUID) -> List[LeaveRequest]:
        """Get pending leave requests for an approver"""
        result = await self.db.execute(
            select(LeaveRequest)
            .where(
                and_(
                    LeaveRequest.approver_id == approver_id,
                    LeaveRequest.status == "pending"
                )
            )
            .order_by(LeaveRequest.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(
        self,
        request_id: uuid.UUID,
        update_data: LeaveRequestUpdate
    ) -> Optional[LeaveRequest]:
        """Update leave request"""
        leave_request = await self.get_by_id(request_id)
        if not leave_request:
            return None
        
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(leave_request, key, value)
        
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request
    
    async def approve(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID
    ) -> Optional[LeaveRequest]:
        """Approve a leave request"""
        leave_request = await self.get_by_id(request_id)
        if not leave_request:
            return None
        
        leave_request.status = "approved"
        leave_request.approver_id = approver_id
        leave_request.approved_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request
    
    async def reject(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        reason: str
    ) -> Optional[LeaveRequest]:
        """Reject a leave request"""
        leave_request = await self.get_by_id(request_id)
        if not leave_request:
            return None
        
        leave_request.status = "rejected"
        leave_request.approver_id = approver_id
        leave_request.approved_date = date.today()
        leave_request.rejection_reason = reason
        
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request


class AttendanceRepository:
    """Repository for attendance operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, attendance_data: AttendanceRecordCreate) -> AttendanceRecord:
        """Create attendance record"""
        record = AttendanceRecord(**attendance_data.model_dump())
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
    
    async def get_by_employee_and_date(
        self,
        employee_id: uuid.UUID,
        date: date
    ) -> Optional[AttendanceRecord]:
        """Get attendance record for employee on specific date"""
        result = await self.db.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.employee_id == employee_id,
                    AttendanceRecord.date == date
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee_and_month(
        self,
        employee_id: uuid.UUID,
        year: int,
        month: int
    ) -> List[AttendanceRecord]:
        """Get all attendance records for employee in a month"""
        result = await self.db.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.employee_id == employee_id,
                    extract('year', AttendanceRecord.date) == year,
                    extract('month', AttendanceRecord.date) == month
                )
            ).order_by(AttendanceRecord.date)
        )
        return list(result.scalars().all())
