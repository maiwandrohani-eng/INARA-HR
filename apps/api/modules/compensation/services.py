"""Compensation - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
class CompensationService:
    def __init__(self, db: AsyncSession):
        self.db = db
