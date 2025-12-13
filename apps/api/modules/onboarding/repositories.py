"""Onboarding - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
class OnboardingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
