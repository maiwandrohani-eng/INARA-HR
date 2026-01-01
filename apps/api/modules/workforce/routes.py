"""Workforce Planning Module - Routes"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.workforce.services import WorkforceService
from modules.workforce.schemas import WorkforcePlanCreate, PositionRequisitionCreate, HeadcountForecastCreate

router = APIRouter()


@router.post("/plans", status_code=201)
async def create_workforce_plan(
    plan_data: WorkforcePlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a workforce plan"""
    service = WorkforceService(db)
    return await service.create_workforce_plan(plan_data)


@router.get("/plans")
async def get_workforce_plans(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get workforce plans"""
    service = WorkforceService(db)
    return await service.get_workforce_plans(status=status)


@router.post("/requisitions", status_code=201)
async def create_requisition(
    requisition_data: PositionRequisitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a position requisition"""
    service = WorkforceService(db)
    return await service.create_requisition(requisition_data, current_user)


@router.get("/requisitions")
async def get_requisitions(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get position requisitions"""
    service = WorkforceService(db)
    return await service.get_requisitions(status=status)

