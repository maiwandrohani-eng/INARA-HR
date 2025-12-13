"""
Leave & Attendance Module - Service Layer with Approval Workflow Integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import uuid

from modules.leave.repositories import (
    LeavePolicyRepository, LeaveBalanceRepository,
    LeaveRequestRepository, AttendanceRepository
)
from modules.leave.schemas import (
    LeavePolicyCreate, LeavePolicyResponse,
    LeaveBalanceCreate, LeaveBalanceResponse,
    LeaveRequestCreate, LeaveRequestResponse,
    AttendanceRecordCreate, AttendanceRecordResponse
)
from modules.approvals.services import ApprovalService
from modules.approvals.schemas import ApprovalRequestCreate
from modules.approvals.models import ApprovalType
from modules.employees.models import Employee
from core.exceptions import NotFoundException, BadRequestException
from core.email import email_service


class LeaveService:
    """Service for leave and attendance operations with approval workflow"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy_repo = LeavePolicyRepository(db)
        self.balance_repo = LeaveBalanceRepository(db)
        self.request_repo = LeaveRequestRepository(db)
        self.attendance_repo = AttendanceRepository(db)
        self.approval_service = ApprovalService(db)
    
    # Leave Policy methods
    async def create_policy(self, policy_data: LeavePolicyCreate) -> LeavePolicyResponse:
        """Create a new leave policy"""
        policy = await self.policy_repo.create(policy_data)
        return LeavePolicyResponse.model_validate(policy)
    
    async def get_policies(self) -> List[LeavePolicyResponse]:
        """Get all leave policies"""
        policies = await self.policy_repo.get_all()
        return [LeavePolicyResponse.model_validate(p) for p in policies]
    
    # Leave Balance methods
    async def get_employee_balances(
        self,
        employee_id: uuid.UUID,
        year: Optional[str] = None
    ) -> List[LeaveBalanceResponse]:
        """Get leave balances for an employee"""
        if not year:
            year = str(datetime.now().year)
        
        balances = await self.balance_repo.get_by_employee_and_year(employee_id, year)
        return [LeaveBalanceResponse.model_validate(b) for b in balances]
    
    # Leave Request methods
    async def submit_leave_request(
        self,
        request_data: LeaveRequestCreate,
        current_employee_id: uuid.UUID
    ) -> LeaveRequestResponse:
        """Submit a new leave request with automatic approval routing"""
        # Set employee_id if not provided
        if not request_data.employee_id:
            request_data.employee_id = current_employee_id
        
        # Get employee to find supervisor
        result = await self.db.execute(
            select(Employee).where(Employee.id == request_data.employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise NotFoundException("Employee not found")
        
        if not employee.manager_id:
            raise BadRequestException("Employee has no supervisor assigned. Cannot route for approval.")
        
        # Calculate total days
        total_days = Decimal((request_data.end_date - request_data.start_date).days + 1)
        
        # Check leave balance
        year = str(request_data.start_date.year)
        balance = await self.balance_repo.get_by_employee_type_year(
            request_data.employee_id,
            request_data.leave_type,
            year
        )
        
        if balance and balance.available_days < total_days:
            raise BadRequestException(
                f"Insufficient leave balance. Available: {balance.available_days}, Requested: {total_days}"
            )
        
        # Create leave request
        leave_request = await self.request_repo.create(request_data, total_days)
        leave_request.approver_id = employee.manager_id
        await self.db.commit()
        await self.db.refresh(leave_request)
        
        # Create approval request
        approval_data = ApprovalRequestCreate(
            request_type=ApprovalType.LEAVE,
            request_id=leave_request.id,
            employee_id=request_data.employee_id,
            comments=request_data.reason
        )
        
        await self.approval_service.create_approval_request(
            approval_data,
            employee.manager_id
        )
        
        # Send email notification to supervisor
        supervisor_result = await self.db.execute(
            select(Employee).where(Employee.id == employee.manager_id)
        )
        supervisor = supervisor_result.scalar_one_or_none()
        
        if supervisor and supervisor.email:
            await email_service.send_approval_request_notification(
                to_email=supervisor.email,
                employee_name=f"{employee.first_name} {employee.last_name}",
                request_type="leave",
                request_details={
                    "Type": request_data.leave_type,
                    "Start Date": request_data.start_date.strftime("%Y-%m-%d"),
                    "End Date": request_data.end_date.strftime("%Y-%m-%d"),
                    "Days": str(total_days),
                    "Reason": request_data.reason or "N/A"
                }
            )
        
        # Update leave balance (add to pending)
        if balance:
            new_pending = balance.pending_days + total_days
            await self.balance_repo.update_balance(balance.id, pending_days=new_pending)
        
        return LeaveRequestResponse.model_validate(leave_request)
    
    async def get_employee_leave_requests(
        self,
        employee_id: uuid.UUID
    ) -> List[LeaveRequestResponse]:
        """Get all leave requests for an employee"""
        requests = await self.request_repo.get_by_employee(employee_id)
        return [LeaveRequestResponse.model_validate(r) for r in requests]
    
    async def get_leave_request(self, request_id: uuid.UUID) -> LeaveRequestResponse:
        """Get a specific leave request"""
        leave_request = await self.request_repo.get_by_id(request_id)
        if not leave_request:
            raise NotFoundException("Leave request not found")
        return LeaveRequestResponse.model_validate(leave_request)
    
    async def approve_leave_request(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        comments: Optional[str] = None
    ) -> LeaveRequestResponse:
        """Approve a leave request (called after approval workflow approves)"""
        leave_request = await self.request_repo.approve(request_id, approver_id)
        if not leave_request:
            raise NotFoundException("Leave request not found")
        
        # Send email notification to employee
        employee_result = await self.db.execute(
            select(Employee).where(Employee.id == leave_request.employee_id)
        )
        employee = employee_result.scalar_one_or_none()
        
        if employee and employee.email:
            await email_service.send_approval_status_notification(
                to_email=employee.email,
                request_type="leave",
                status="approved",
                comments=comments
            )
        
        # Update leave balance (move from pending to used)
        year = str(leave_request.start_date.year)
        balance = await self.balance_repo.get_by_employee_type_year(
            leave_request.employee_id,
            leave_request.leave_type,
            year
        )
        
        if balance:
            new_pending = balance.pending_days - leave_request.total_days
            new_used = balance.used_days + leave_request.total_days
            await self.balance_repo.update_balance(
                balance.id,
                used_days=new_used,
                pending_days=new_pending
            )
        
        return LeaveRequestResponse.model_validate(leave_request)
    
    async def reject_leave_request(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        reason: str
    ) -> LeaveRequestResponse:
        """Reject a leave request (called after approval workflow rejects)"""
        leave_request = await self.request_repo.reject(request_id, approver_id, reason)
        if not leave_request:
            raise NotFoundException("Leave request not found")
        
        # Send email notification to employee
        employee_result = await self.db.execute(
            select(Employee).where(Employee.id == leave_request.employee_id)
        )
        employee = employee_result.scalar_one_or_none()
        
        if employee and employee.email:
            await email_service.send_approval_status_notification(
                to_email=employee.email,
                request_type="leave",
                status="rejected",
                comments=reason
            )
        
        # Update leave balance (remove from pending)
        year = str(leave_request.start_date.year)
        balance = await self.balance_repo.get_by_employee_type_year(
            leave_request.employee_id,
            leave_request.leave_type,
            year
        )
        
        if balance:
            new_pending = balance.pending_days - leave_request.total_days
            await self.balance_repo.update_balance(balance.id, pending_days=new_pending)
        
        return LeaveRequestResponse.model_validate(leave_request)
    
    # Attendance methods
    async def record_attendance(
        self,
        attendance_data: AttendanceRecordCreate
    ) -> AttendanceRecordResponse:
        """Record attendance for an employee"""
        # Check if record already exists
        existing = await self.attendance_repo.get_by_employee_and_date(
            attendance_data.employee_id,
            attendance_data.date
        )
        
        if existing:
            raise BadRequestException("Attendance already recorded for this date")
        
        record = await self.attendance_repo.create(attendance_data)
        return AttendanceRecordResponse.model_validate(record)
    
    async def get_monthly_attendance(
        self,
        employee_id: uuid.UUID,
        year: int,
        month: int
    ) -> List[AttendanceRecordResponse]:
        """Get attendance records for a month"""
        records = await self.attendance_repo.get_by_employee_and_month(employee_id, year, month)
        return [AttendanceRecordResponse.model_validate(r) for r in records]
