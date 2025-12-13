"""Timesheets Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession

class TimesheetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
