"""Safeguarding Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession

class SafeguardingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
