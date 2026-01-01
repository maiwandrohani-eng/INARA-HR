"""Succession Planning Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from modules.succession.repositories import KeyPositionRepository, SuccessorRepository, SuccessionPlanRepository
from modules.succession.schemas import KeyPositionCreate, SuccessorCreate, SuccessionPlanCreate


class SuccessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.key_position_repo = KeyPositionRepository(db)
        self.successor_repo = SuccessorRepository(db)
        self.plan_repo = SuccessionPlanRepository(db)
    
    async def create_key_position(self, position_data: KeyPositionCreate, country_code: str = "US") -> dict:
        position = await self.key_position_repo.create(position_data, country_code)
        await self.db.commit()
        return {"id": str(position.id), "position_id": str(position.position_id)}
    
    async def add_successor(self, successor_data: SuccessorCreate, country_code: str = "US") -> dict:
        successor = await self.successor_repo.create(successor_data, country_code)
        await self.db.commit()
        return {"id": str(successor.id), "employee_id": str(successor.employee_id)}
    
    async def create_succession_plan(self, plan_data: SuccessionPlanCreate, country_code: str = "US") -> dict:
        plan = await self.plan_repo.create(plan_data, country_code)
        await self.db.commit()
        return {"id": str(plan.id), "plan_name": plan.plan_name}
    
    async def get_key_positions(self) -> List[dict]:
        positions = await self.key_position_repo.get_all()
        return [{
            "id": str(p.id),
            "position_id": str(p.position_id),
            "criticality_level": p.criticality_level,
            "has_successor": p.has_successor,
            "succession_status": p.succession_status
        } for p in positions]
    
    async def get_succession_plans(self) -> List[dict]:
        plans = await self.plan_repo.get_all()
        return [{
            "id": str(p.id),
            "key_position_id": str(p.key_position_id),
            "plan_name": p.plan_name,
            "plan_date": p.plan_date.isoformat() if p.plan_date else None,
            "review_date": p.review_date.isoformat() if p.review_date else None,
            "status": p.status,
            "expected_transition_date": p.expected_transition_date.isoformat() if p.expected_transition_date else None,
        } for p in plans]

