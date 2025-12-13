"""Travel - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date
import uuid

from modules.travel.models import TravelRequest
from modules.travel.schemas import TravelRequestCreate, TravelRequestResponse
from modules.employees.models import Employee
from modules.approvals.services import ApprovalService
from modules.approvals.schemas import ApprovalRequestCreate
from modules.approvals.models import ApprovalType
from core.exceptions import NotFoundException, BadRequestException

class TravelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_service = ApprovalService(db)
    
    async def create_travel_request(
        self,
        request_data: TravelRequestCreate,
        current_employee_id: uuid.UUID
    ) -> TravelRequestResponse:
        """Create travel request with approval workflow"""
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
            raise BadRequestException("Employee has no supervisor assigned")
        
        # Create travel request
        travel_request = TravelRequest(
            employee_id=request_data.employee_id,
            destination=request_data.destination,
            purpose=request_data.purpose,
            departure_date=request_data.departure_date,
            return_date=request_data.return_date,
            status="pending",
            approver_id=employee.manager_id
        )
        
        self.db.add(travel_request)
        await self.db.commit()
        await self.db.refresh(travel_request)
        
        # Create approval request
        approval_data = ApprovalRequestCreate(
            request_type=ApprovalType.TRAVEL,
            request_id=travel_request.id,
            employee_id=request_data.employee_id,
            comments=request_data.purpose
        )
        
        await self.approval_service.create_approval_request(
            approval_data,
            employee.manager_id
        )
        
        return TravelRequestResponse.model_validate(travel_request)
    
    async def get_employee_travel_requests(
        self,
        employee_id: uuid.UUID
    ) -> List[TravelRequestResponse]:
        """Get all travel requests for an employee"""
        result = await self.db.execute(
            select(TravelRequest)
            .where(TravelRequest.employee_id == employee_id)
            .order_by(TravelRequest.created_at.desc())
        )
        requests = result.scalars().all()
        return [TravelRequestResponse.model_validate(r) for r in requests]
    
    async def approve_travel_request(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID
    ) -> TravelRequestResponse:
        """Approve a travel request"""
        result = await self.db.execute(
            select(TravelRequest).where(TravelRequest.id == request_id)
        )
        travel_request = result.scalar_one_or_none()
        
        if not travel_request:
            raise NotFoundException("Travel request not found")
        
        travel_request.status = "approved"
        travel_request.approver_id = approver_id
        travel_request.approval_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(travel_request)
        
        return TravelRequestResponse.model_validate(travel_request)
    
    async def reject_travel_request(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID
    ) -> TravelRequestResponse:
        """Reject a travel request"""
        result = await self.db.execute(
            select(TravelRequest).where(TravelRequest.id == request_id)
        )
        travel_request = result.scalar_one_or_none()
        
        if not travel_request:
            raise NotFoundException("Travel request not found")
        
        travel_request.status = "rejected"
        travel_request.approver_id = approver_id
        travel_request.approval_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(travel_request)
        
        return TravelRequestResponse.model_validate(travel_request)
