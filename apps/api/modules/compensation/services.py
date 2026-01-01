"""Compensation Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
import uuid

from modules.compensation.repositories import CompensationRepository
from core.exceptions import NotFoundException


class CompensationService:
    """Service for compensation operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CompensationRepository(db)
    
    async def get_salary_history(self, employee_id: uuid.UUID) -> List[dict]:
        """Get salary history for an employee"""
        history = await self.repo.get_salary_history(employee_id)
        return [{
            "id": str(h.id),
            "effective_date": str(h.effective_date),
            "salary": float(h.salary),
            "currency": h.currency,
            "change_reason": h.change_reason,
            "notes": h.notes
        } for h in history]
    
    async def add_salary_adjustment(
        self,
        employee_id: uuid.UUID,
        salary: float,
        currency: str,
        effective_date: date,
        change_reason: str = None,
        notes: str = None,
        created_by: uuid.UUID = None
    ) -> dict:
        """Add salary adjustment to history"""
        salary_data = {
            "employee_id": employee_id,
            "salary": salary,
            "currency": currency,
            "effective_date": effective_date,
            "change_reason": change_reason,
            "notes": notes
        }
        if created_by:
            salary_data["created_by"] = created_by
        
        history = await self.repo.create_salary_history(salary_data)
        await self.db.commit()
        
        return {
            "id": str(history.id),
            "employee_id": str(history.employee_id),
            "effective_date": str(history.effective_date),
            "salary": float(history.salary),
            "currency": history.currency
        }
