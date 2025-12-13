"""Travel - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
class TravelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
