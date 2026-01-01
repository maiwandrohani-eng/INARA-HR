"""Grievance - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, datetime
import uuid
from .models import Grievance
from .schemas import GrievanceCreate
from typing import List, Optional

class GrievanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_grievance(self, grievance_data: GrievanceCreate, created_by: uuid.UUID) -> Grievance:
        """Create a new grievance and create approval requests for HR Manager and CEO"""
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        from core.role_helpers import get_hr_manager, get_ceo
        from modules.approvals.services import ApprovalService
        from modules.approvals.schemas import ApprovalRequestCreate
        from modules.approvals.models import ApprovalType
        from sqlalchemy import select
        
        # Get employee to find country_code
        employee_repo = EmployeeRepository(self.db)
        employee_result = await self.db.execute(
            select(Employee).where(Employee.id == uuid.UUID(grievance_data.employee_id))
        )
        employee = employee_result.scalar_one_or_none()
        if not employee:
            raise Exception("Employee not found")
        
        country_code = employee.country_code or 'US'
        
        # Generate case number
        case_number = await self._generate_case_number()
        
        grievance = Grievance(
            employee_id=uuid.UUID(grievance_data.employee_id),
            case_number=case_number,
            grievance_type=grievance_data.grievance_type,
            description=grievance_data.description,
            filed_date=date.today(),
            status=grievance_data.status,
            created_by=created_by,
            country_code=country_code
        )
        
        self.db.add(grievance)
        await self.db.flush()
        
        # Create approval requests for HR Manager and CEO (both can review)
        hr_manager = await get_hr_manager(self.db, country_code)
        ceo = await get_ceo(self.db, country_code)
        
        if hr_manager or ceo:
            approval_service = ApprovalService(self.db)
            approval_data = ApprovalRequestCreate(
                request_type=ApprovalType.GRIEVANCE,
                request_id=grievance.id,
                employee_id=employee.id,
                comments=f"Grievance case: {case_number} - {grievance_data.grievance_type}"
            )
            
            # Create approval for HR Manager (if exists)
            if hr_manager:
                await approval_service.create_approval_request(
                    approval_data,
                    hr_manager.id,
                    country_code=country_code,
                    approval_level=1,
                    is_final_approval=False
                )
            
            # Create approval for CEO (if exists) - can review independently
            if ceo:
                await approval_service.create_approval_request(
                    approval_data,
                    ceo.id,
                    country_code=country_code,
                    approval_level=1,
                    is_final_approval=True  # CEO can finalize
                )
        
        await self.db.commit()
        await self.db.refresh(grievance)
        
        return grievance
    
    async def get_all_grievances(self) -> List[Grievance]:
        """Get all grievances"""
        result = await self.db.execute(
            select(Grievance)
            .where(Grievance.is_deleted == False)
            .order_by(Grievance.filed_date.desc())
        )
        return result.scalars().all()
    
    async def update_grievance(self, grievance_id: uuid.UUID, update_data: dict, updated_by: uuid.UUID) -> Optional[Grievance]:
        """Update an existing grievance"""
        result = await self.db.execute(
            select(Grievance).where(Grievance.id == grievance_id, Grievance.is_deleted == False)
        )
        grievance = result.scalars().first()
        
        if not grievance:
            return None
        
        # Update fields
        if 'status' in update_data and update_data['status']:
            grievance.status = update_data['status']
        if 'resolution' in update_data and update_data['resolution']:
            grievance.resolution = update_data['resolution']
        if 'resolution_date' in update_data and update_data['resolution_date']:
            grievance.resolution_date = datetime.fromisoformat(update_data['resolution_date']).date()
        
        grievance.updated_by = updated_by
        
        await self.db.commit()
        await self.db.refresh(grievance)
        
        return grievance
    
    async def _generate_case_number(self) -> str:
        """Generate unique case number in format GR-YYYY-####"""
        year = datetime.now().year
        
        # Get the latest case number for this year
        result = await self.db.execute(
            select(Grievance)
            .where(Grievance.case_number.like(f'GR-{year}-%'))
            .order_by(Grievance.case_number.desc())
        )
        latest = result.scalars().first()
        
        if latest:
            # Extract number and increment
            last_num = int(latest.case_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'GR-{year}-{new_num:04d}'
