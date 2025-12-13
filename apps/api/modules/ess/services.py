"""ESS - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
class ESSService:
    def __init__(self, db: AsyncSession):
        self.db = db
