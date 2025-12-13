"""Learning - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
class LearningRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
