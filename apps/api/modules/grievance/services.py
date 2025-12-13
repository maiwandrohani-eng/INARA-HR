"""Grievance - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
class GrievanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
