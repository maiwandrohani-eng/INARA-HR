"""Performance Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession

class PerformanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
