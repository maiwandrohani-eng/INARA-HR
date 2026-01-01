"""Compensation Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from modules.compensation.models import SalaryHistory


class CompensationRepository:
    """Repository for compensation operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_salary_history(self, salary_data: dict) -> SalaryHistory:
        """Create salary history record"""
        history = SalaryHistory(**salary_data)
        self.db.add(history)
        await self.db.flush()
        await self.db.refresh(history)
        return history
    
    async def get_salary_history(self, employee_id: uuid.UUID) -> List[SalaryHistory]:
        """Get salary history for an employee"""
        result = await self.db.execute(
            select(SalaryHistory).where(
                and_(
                    SalaryHistory.employee_id == employee_id,
                    SalaryHistory.is_deleted == False
                )
            ).order_by(SalaryHistory.effective_date.desc())
        )
        return result.scalars().all()
    
    async def get_current_salary(self, employee_id: uuid.UUID) -> Optional[SalaryHistory]:
        """Get current salary for an employee"""
        result = await self.db.execute(
            select(SalaryHistory).where(
                and_(
                    SalaryHistory.employee_id == employee_id,
                    SalaryHistory.is_deleted == False
                )
            ).order_by(SalaryHistory.effective_date.desc()).limit(1)
        )
        return result.scalar_one_or_none()
