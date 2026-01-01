"""Succession Planning Module - Routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.succession.services import SuccessionService
from modules.succession.schemas import KeyPositionCreate, SuccessorCreate, SuccessionPlanCreate

router = APIRouter()


@router.post("/key-positions", status_code=201)
async def create_key_position(
    position_data: KeyPositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a key position"""
    service = SuccessionService(db)
    return await service.create_key_position(position_data)


@router.get("/key-positions")
async def get_key_positions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all key positions"""
    service = SuccessionService(db)
    return await service.get_key_positions()


@router.post("/successors", status_code=201)
async def add_successor(
    successor_data: SuccessorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Add a successor candidate"""
    service = SuccessionService(db)
    return await service.add_successor(successor_data)


@router.post("/succession-plans", status_code=201)
async def create_succession_plan(
    plan_data: SuccessionPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a succession plan"""
    service = SuccessionService(db)
    return await service.create_succession_plan(plan_data)


@router.get("/succession-plans")
async def get_succession_plans(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all succession plans"""
    service = SuccessionService(db)
    return await service.get_succession_plans()

