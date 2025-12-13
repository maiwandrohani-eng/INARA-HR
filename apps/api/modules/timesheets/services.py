"""Timesheets Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date
from decimal import Decimal
import uuid

from modules.timesheets.models import Timesheet, TimesheetEntry
from modules.employees.models import Employee
from modules.approvals.services import ApprovalService
from modules.approvals.schemas import ApprovalRequestCreate
from modules.approvals.models import ApprovalType
from core.exceptions import NotFoundException, BadRequestException

class TimesheetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_service = ApprovalService(db)
    
    async def submit_timesheet(
        self,
        employee_id: uuid.UUID,
        period_start: date,
        period_end: date,
        entries: List[dict]
    ) -> dict:
        """Submit monthly timesheet for approval"""
        # Get employee to find supervisor
        result = await self.db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise NotFoundException("Employee not found")
        
        if not employee.manager_id:
            raise BadRequestException("Employee has no supervisor assigned")
        
        # Calculate total hours
        total_hours = sum(Decimal(str(entry.get('hours', 0))) for entry in entries)
        
        # Create timesheet
        timesheet = Timesheet(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end,
            total_hours=total_hours,
            status="submitted",
            submitted_date=date.today(),
            approver_id=employee.manager_id
        )
        
        self.db.add(timesheet)
        await self.db.commit()
        await self.db.refresh(timesheet)
        
        # Create approval request
        approval_data = ApprovalRequestCreate(
            request_type=ApprovalType.TIMESHEET,
            request_id=timesheet.id,
            employee_id=employee_id,
            comments=f"Timesheet for {period_start} to {period_end}"
        )
        
        await self.approval_service.create_approval_request(
            approval_data,
            employee.manager_id
        )
        
        return {
            "id": str(timesheet.id),
            "status": timesheet.status,
            "total_hours": float(timesheet.total_hours)
        }
    
    async def approve_timesheet(
        self,
        timesheet_id: uuid.UUID,
        approver_id: uuid.UUID
    ) -> dict:
        """Approve a timesheet"""
        result = await self.db.execute(
            select(Timesheet).where(Timesheet.id == timesheet_id)
        )
        timesheet = result.scalar_one_or_none()
        
        if not timesheet:
            raise NotFoundException("Timesheet not found")
        
        timesheet.status = "approved"
        timesheet.approver_id = approver_id
        timesheet.approved_date = date.today()
        
        await self.db.commit()
        
        return {"id": str(timesheet.id), "status": "approved"}
    
    async def reject_timesheet(
        self,
        timesheet_id: uuid.UUID,
        approver_id: uuid.UUID
    ) -> dict:
        """Reject a timesheet"""
        result = await self.db.execute(
            select(Timesheet).where(Timesheet.id == timesheet_id)
        )
        timesheet = result.scalar_one_or_none()
        
        if not timesheet:
            raise NotFoundException("Timesheet not found")
        
        timesheet.status = "rejected"
        timesheet.approver_id = approver_id
        
        await self.db.commit()
        
        return {"id": str(timesheet.id), "status": "rejected"}
