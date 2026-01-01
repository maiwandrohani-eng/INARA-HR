"""Compliance & Legal Module - Routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.compliance.services import ComplianceService
from modules.compliance.schemas import PolicyCreate, PolicyAcknowledgmentCreate, ComplianceTrainingCreate, TrainingCompletionCreate

router = APIRouter()


@router.post("/policies", status_code=201)
async def create_policy(
    policy_data: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new policy"""
    service = ComplianceService(db)
    return await service.create_policy(policy_data)


@router.post("/acknowledgments", status_code=201)
async def acknowledge_policy(
    acknowledgment_data: PolicyAcknowledgmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Acknowledge a policy"""
    service = ComplianceService(db)
    return await service.acknowledge_policy(acknowledgment_data)


@router.post("/trainings", status_code=201)
async def create_training(
    training_data: ComplianceTrainingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create compliance training"""
    service = ComplianceService(db)
    return await service.create_training(training_data)


@router.post("/completions", status_code=201)
async def record_completion(
    completion_data: TrainingCompletionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Record training completion"""
    service = ComplianceService(db)
    return await service.record_completion(completion_data)

