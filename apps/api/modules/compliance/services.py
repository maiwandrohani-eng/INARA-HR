"""Compliance & Legal Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from modules.compliance.repositories import (
    PolicyRepository, PolicyAcknowledgmentRepository,
    ComplianceTrainingRepository, TrainingCompletionRepository
)
from modules.compliance.schemas import (
    PolicyCreate, PolicyAcknowledgmentCreate,
    ComplianceTrainingCreate, TrainingCompletionCreate
)


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.acknowledgment_repo = PolicyAcknowledgmentRepository(db)
        self.training_repo = ComplianceTrainingRepository(db)
        self.completion_repo = TrainingCompletionRepository(db)
    
    async def create_policy(self, policy_data: PolicyCreate, country_code: str = "US") -> dict:
        policy = await self.policy_repo.create(policy_data, country_code)
        await self.db.commit()
        return {"id": str(policy.id), "title": policy.title}
    
    async def acknowledge_policy(self, acknowledgment_data: PolicyAcknowledgmentCreate, country_code: str = "US") -> dict:
        acknowledgment = await self.acknowledgment_repo.create(acknowledgment_data, country_code)
        await self.db.commit()
        return {"id": str(acknowledgment.id), "policy_id": str(acknowledgment.policy_id)}
    
    async def create_training(self, training_data: ComplianceTrainingCreate, country_code: str = "US") -> dict:
        training = await self.training_repo.create(training_data, country_code)
        await self.db.commit()
        return {"id": str(training.id), "title": training.title}
    
    async def record_completion(self, completion_data: TrainingCompletionCreate, country_code: str = "US") -> dict:
        completion = await self.completion_repo.create(completion_data, country_code)
        await self.db.commit()
        return {"id": str(completion.id), "compliance_training_id": str(completion.compliance_training_id)}

