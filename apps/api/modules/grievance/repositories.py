"""Grievance Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from modules.grievance.models import DisciplinaryAction


class DisciplinaryActionRepository:
    """Repository for disciplinary action operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, action_data: dict) -> DisciplinaryAction:
        """Create disciplinary action"""
        action = DisciplinaryAction(**action_data)
        self.db.add(action)
        await self.db.flush()
        await self.db.refresh(action)
        return action
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[DisciplinaryAction]:
        """Get all disciplinary actions for an employee"""
        result = await self.db.execute(
            select(DisciplinaryAction).where(
                and_(
                    DisciplinaryAction.employee_id == employee_id,
                    DisciplinaryAction.is_deleted == False
                )
            ).order_by(DisciplinaryAction.action_date.desc())
        )
        return result.scalars().all()
    
    async def get_by_id(self, action_id: uuid.UUID) -> Optional[DisciplinaryAction]:
        """Get disciplinary action by ID"""
        result = await self.db.execute(
            select(DisciplinaryAction).where(
                and_(DisciplinaryAction.id == action_id, DisciplinaryAction.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
