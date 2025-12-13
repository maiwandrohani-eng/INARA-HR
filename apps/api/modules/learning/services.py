"""Learning - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
class LearningService:
    def __init__(self, db: AsyncSession):
        self.db = db
