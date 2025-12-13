"""Compensation - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
class CompensationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
