"""
Employee Management Module - Service Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from modules.employees.repositories import EmployeeRepository
from modules.employees.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Service for employee operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
    
    async def get_employee(self, employee_id: uuid.UUID):
        """Get employee by ID"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        return employee
    
    async def list_employees(self, skip: int = 0, limit: int = 100):
        """List all employees"""
        return await self.employee_repo.get_all(skip=skip, limit=limit)
    
    async def create_employee(self, employee_data: EmployeeCreate):
        """Create new employee"""
        # Auto-generate employee number if not provided
        employee_dict = employee_data.model_dump()
        
        if not employee_dict.get('employee_number'):
            # Get all employee numbers matching pattern
            from sqlalchemy import select
            from modules.employees.models import Employee
            
            result = await self.db.execute(
                select(Employee.employee_number)
                .where(Employee.employee_number.like('EMP-%'))
                .where(Employee.is_deleted == False)
            )
            employee_numbers = result.scalars().all()
            
            if employee_numbers:
                # Extract all numbers and find the maximum
                max_num = 0
                for emp_num in employee_numbers:
                    try:
                        num = int(emp_num.split('-')[1])
                        if num > max_num:
                            max_num = num
                    except (IndexError, ValueError):
                        continue
                employee_dict['employee_number'] = f'EMP-{max_num + 1:03d}'
            else:
                employee_dict['employee_number'] = 'EMP-001'
        
        # TODO: Create associated user account
        employee = await self.employee_repo.create(employee_dict)
        await self.db.commit()
        return employee
    
    async def update_employee(self, employee_id: uuid.UUID, employee_data: EmployeeUpdate):
        """Update employee"""
        employee = await self.employee_repo.update(
            employee_id,
            employee_data.model_dump(exclude_unset=True)
        )
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        await self.db.commit()
        return employee
    
    async def delete_employee(self, employee_id: uuid.UUID):
        """Delete employee (soft delete)"""
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.is_deleted = True
        await self.db.commit()
        return None
    
    async def activate_employee(self, employee_id: uuid.UUID):
        """Activate employee - set status to ACTIVE"""
        from modules.employees.models import Employee
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.manager)
            )
            .where(Employee.id == employee_id)
            .where(Employee.is_deleted == False)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.status = 'ACTIVE'
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
    
    async def deactivate_employee(self, employee_id: uuid.UUID):
        """Deactivate employee - set status to TERMINATED"""
        from modules.employees.models import Employee
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.department),
                selectinload(Employee.position),
                selectinload(Employee.manager)
            )
            .where(Employee.id == employee_id)
            .where(Employee.is_deleted == False)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            from core.exceptions import NotFoundException
            raise NotFoundException(resource="Employee")
        
        employee.status = 'TERMINATED'
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
