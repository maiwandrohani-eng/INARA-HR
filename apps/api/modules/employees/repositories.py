"""
Employee Management Module - Repository Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
import uuid

from modules.employees.models import Employee, Department, Position, Contract


class EmployeeRepository:
    """Repository for Employee operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, employee_id: uuid.UUID) -> Optional[Employee]:
        """Get employee by ID"""
        result = await self.db.execute(
            select(Employee).where(and_(Employee.id == employee_id, Employee.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees"""
        result = await self.db.execute(
            select(Employee)
            .where(Employee.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, employee_data: dict) -> Employee:
        """Create new employee"""
        employee = Employee(**employee_data)
        self.db.add(employee)
        await self.db.flush()
        await self.db.refresh(employee)
        return employee
    
    async def update(self, employee_id: uuid.UUID, employee_data: dict) -> Optional[Employee]:
        """Update employee"""
        employee = await self.get_by_id(employee_id)
        if not employee:
            return None
        
        for key, value in employee_data.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        
        await self.db.flush()
        return employee
    
    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Employee]:
        """Get employee by user ID"""
        result = await self.db.execute(
            select(Employee).where(
                and_(
                    Employee.user_id == user_id,
                    Employee.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()


# Similar repositories for Department, Position, Contract...
