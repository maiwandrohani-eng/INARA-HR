"""Onboarding - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
class OnboardingService:
    def __init__(self, db: AsyncSession):
        self.db = db
