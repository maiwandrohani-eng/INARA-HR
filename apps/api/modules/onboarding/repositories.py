"""Onboarding Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from modules.onboarding.models import OnboardingChecklist


class OnboardingRepository:
    """Repository for onboarding operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_checklist(self, employee_id: uuid.UUID) -> List[OnboardingChecklist]:
        """Get onboarding checklist for an employee"""
        result = await self.db.execute(
            select(OnboardingChecklist).where(
                and_(
                    OnboardingChecklist.employee_id == employee_id,
                    OnboardingChecklist.is_deleted == False
                )
            ).order_by(OnboardingChecklist.created_at)
        )
        return result.scalars().all()
    
    async def get_task_by_id(self, task_id: uuid.UUID) -> Optional[OnboardingChecklist]:
        """Get task by ID"""
        result = await self.db.execute(
            select(OnboardingChecklist).where(
                and_(OnboardingChecklist.id == task_id, OnboardingChecklist.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def complete_task(self, task_id: uuid.UUID) -> Optional[OnboardingChecklist]:
        """Mark task as completed"""
        task = await self.get_task_by_id(task_id)
        if not task:
            return None
        
        from datetime import date
        task.completed = True
        task.completed_date = date.today()
        await self.db.flush()
        return task
    
    async def create_task(self, task_data: dict) -> OnboardingChecklist:
        """Create onboarding task"""
        task = OnboardingChecklist(**task_data)
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task
