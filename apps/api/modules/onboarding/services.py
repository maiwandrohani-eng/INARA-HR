"""Onboarding Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
import uuid

from modules.onboarding.repositories import OnboardingRepository
from core.exceptions import NotFoundException


class OnboardingService:
    """Service for onboarding operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OnboardingRepository(db)
    
    async def get_checklist(self, employee_id: uuid.UUID) -> List[dict]:
        """Get onboarding checklist"""
        tasks = await self.repo.get_checklist(employee_id)
        return [{
            "id": str(t.id),
            "task_name": t.task_name,
            "description": t.description,
            "due_date": str(t.due_date) if t.due_date else None,
            "completed": t.completed,
            "completed_date": str(t.completed_date) if t.completed_date else None
        } for t in tasks]
    
    async def complete_task(self, task_id: uuid.UUID) -> dict:
        """Complete an onboarding task"""
        task = await self.repo.complete_task(task_id)
        if not task:
            raise NotFoundException(resource="Onboarding task")
        
        await self.db.commit()
        return {
            "id": str(task.id),
            "task_name": task.task_name,
            "completed": task.completed,
            "completed_date": str(task.completed_date)
        }
