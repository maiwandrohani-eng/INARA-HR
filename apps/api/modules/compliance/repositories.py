"""Compliance & Legal Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
import uuid

from modules.compliance.models import Policy, PolicyAcknowledgment, ComplianceTraining, TrainingCompletion
from modules.compliance.schemas import PolicyCreate, PolicyAcknowledgmentCreate, ComplianceTrainingCreate, TrainingCompletionCreate


class PolicyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, policy_data: PolicyCreate, country_code: str) -> Policy:
        policy = Policy(**policy_data.model_dump(), country_code=country_code)
        self.db.add(policy)
        await self.db.flush()
        return policy
    
    async def get_all(self, is_active: Optional[bool] = None) -> List[Policy]:
        query = select(Policy).where(Policy.is_deleted == False)
        if is_active is not None:
            query = query.where(Policy.is_active == is_active)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class PolicyAcknowledgmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, acknowledgment_data: PolicyAcknowledgmentCreate, country_code: str) -> PolicyAcknowledgment:
        policy = await self.db.get(Policy, acknowledgment_data.policy_id)
        acknowledgment_dict = acknowledgment_data.model_dump()
        acknowledgment_dict["acknowledged_date"] = datetime.utcnow()
        acknowledgment_dict["acknowledged_version"] = policy.version if policy else "1.0"
        acknowledgment_dict["country_code"] = country_code
        acknowledgment = PolicyAcknowledgment(**acknowledgment_dict)
        self.db.add(acknowledgment)
        await self.db.flush()
        return acknowledgment


class ComplianceTrainingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, training_data: ComplianceTrainingCreate, country_code: str) -> ComplianceTraining:
        training = ComplianceTraining(**training_data.model_dump(), country_code=country_code)
        self.db.add(training)
        await self.db.flush()
        return training
    
    async def get_all(self) -> List[ComplianceTraining]:
        result = await self.db.execute(
            select(ComplianceTraining).where(ComplianceTraining.is_deleted == False)
        )
        return list(result.scalars().all())


class TrainingCompletionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, completion_data: TrainingCompletionCreate, country_code: str) -> TrainingCompletion:
        completion_dict = completion_data.model_dump()
        completion_dict["completed_date"] = datetime.utcnow()
        completion_dict["country_code"] = country_code
        completion = TrainingCompletion(**completion_dict)
        self.db.add(completion)
        await self.db.flush()
        return completion

