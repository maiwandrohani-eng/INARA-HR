"""Safeguarding Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession

class SafeguardingService:
    def __init__(self, db: AsyncSession):
        self.db = db
