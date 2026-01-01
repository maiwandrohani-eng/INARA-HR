"""Workforce Planning Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from modules.workforce.repositories import WorkforcePlanRepository, PositionRequisitionRepository, HeadcountForecastRepository
from modules.workforce.schemas import WorkforcePlanCreate, PositionRequisitionCreate, HeadcountForecastCreate


class WorkforceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_repo = WorkforcePlanRepository(db)
        self.requisition_repo = PositionRequisitionRepository(db)
        self.forecast_repo = HeadcountForecastRepository(db)
    
    async def create_workforce_plan(self, plan_data: WorkforcePlanCreate, country_code: str = "US") -> dict:
        plan = await self.plan_repo.create(plan_data, country_code)
        await self.db.commit()
        return {"id": str(plan.id), "plan_name": plan.plan_name}
    
    async def create_requisition(self, requisition_data: PositionRequisitionCreate, current_user: dict, country_code: str = "US") -> dict:
        # If requested_by is not provided, try to get from current user's employee
        requisition_dict = requisition_data.model_dump(exclude_none=True)
        
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        from core.role_helpers import get_ceo
        from modules.approvals.services import ApprovalService
        from modules.approvals.schemas import ApprovalRequestCreate
        from modules.approvals.models import ApprovalType
        from sqlalchemy import select
        
        requested_by_employee_id = None
        if not requisition_dict.get("requested_by"):
            from modules.auth.repositories import UserRepository
            user_repo = UserRepository(self.db)
            user = await user_repo.get_by_id(uuid.UUID(current_user["id"]))
            if user and hasattr(user, 'employee') and user.employee:
                requisition_dict["requested_by"] = user.employee.id
                requested_by_employee_id = user.employee.id
        
        # Get country_code from employee if not provided
        if not country_code and requested_by_employee_id:
            employee_repo = EmployeeRepository(self.db)
            employee = await employee_repo.get_by_id(requested_by_employee_id)
            if employee:
                country_code = employee.country_code or 'US'
        
        # Create a new schema instance with updated requested_by if available
        updated_data = PositionRequisitionCreate(**requisition_dict)
        
        requisition = await self.requisition_repo.create(updated_data, country_code)
        await self.db.flush()
        
        # Create approval request for CEO
        if requested_by_employee_id:
            ceo = await get_ceo(self.db, country_code)
            if ceo:
                approval_service = ApprovalService(self.db)
                approval_data = ApprovalRequestCreate(
                    request_type=ApprovalType.WORKFORCE,
                    request_id=requisition.id,
                    employee_id=requested_by_employee_id,
                    comments=f"Position Requisition: {requisition.job_title} - {requisition.justification[:100]}"
                )
                
                await approval_service.create_approval_request(
                    approval_data,
                    ceo.id,
                    country_code=country_code,
                    approval_level=1,
                    is_final_approval=True  # CEO approval is final
                )
        
        await self.db.commit()
        return {"id": str(requisition.id), "requisition_number": requisition.requisition_number}
    
    async def get_workforce_plans(self, status: Optional[str] = None) -> List[dict]:
        plans = await self.plan_repo.get_all(status=status)
        return [{
            "id": str(p.id),
            "plan_name": p.plan_name,
            "plan_year": p.plan_year,
            "plan_start_date": p.plan_start_date.isoformat() if p.plan_start_date else None,
            "plan_end_date": p.plan_end_date.isoformat() if p.plan_end_date else None,
            "status": p.status,
            "total_budget": str(p.total_budget) if p.total_budget else None,
            "currency": p.currency,
        } for p in plans]
    
    async def get_requisitions(self, status: Optional[str] = None) -> List[dict]:
        requisitions = await self.requisition_repo.get_all(status=status)
        return [{
            "id": str(r.id),
            "requisition_number": r.requisition_number,
            "job_title": r.job_title,
            "status": r.status,
            "department_id": str(r.department_id) if r.department_id else None
        } for r in requisitions]

