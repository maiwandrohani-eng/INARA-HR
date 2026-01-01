"""Succession Planning Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from modules.succession.models import KeyPosition, Successor, SuccessionPlan
from modules.succession.schemas import KeyPositionCreate, SuccessorCreate, SuccessionPlanCreate


class KeyPositionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, position_data: KeyPositionCreate, country_code: str) -> KeyPosition:
        position = KeyPosition(**position_data.model_dump(), country_code=country_code)
        self.db.add(position)
        await self.db.flush()
        return position
    
    async def get_all(self) -> List[KeyPosition]:
        result = await self.db.execute(
            select(KeyPosition).where(KeyPosition.is_deleted == False)
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, position_id: uuid.UUID) -> Optional[KeyPosition]:
        result = await self.db.execute(
            select(KeyPosition).where(
                and_(KeyPosition.id == position_id, KeyPosition.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()


class SuccessorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, successor_data: SuccessorCreate, country_code: str) -> Successor:
        successor = Successor(**successor_data.model_dump(), country_code=country_code)
        self.db.add(successor)
        
        # Update key position has_successor flag
        key_position = await self.db.get(KeyPosition, successor_data.key_position_id)
        if key_position:
            key_position.has_successor = True
            key_position.succession_status = "identified"
        
        await self.db.flush()
        return successor
    
    async def get_by_key_position(self, key_position_id: uuid.UUID) -> List[Successor]:
        result = await self.db.execute(
            select(Successor).where(
                and_(
                    Successor.key_position_id == key_position_id,
                    Successor.is_deleted == False,
                    Successor.is_active == True
                )
            )
        )
        return list(result.scalars().all())


class SuccessionPlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, plan_data: SuccessionPlanCreate, country_code: str) -> SuccessionPlan:
        plan = SuccessionPlan(**plan_data.model_dump(), country_code=country_code)
        self.db.add(plan)
        await self.db.flush()
        return plan
    
    async def get_all(self) -> List[SuccessionPlan]:
        result = await self.db.execute(
            select(SuccessionPlan).where(SuccessionPlan.is_deleted == False)
        )
        return list(result.scalars().all())

