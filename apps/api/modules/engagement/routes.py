"""Employee Engagement Module - Routes"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.engagement.services import EngagementService
from modules.engagement.schemas import SurveyCreate, RecognitionCreate

router = APIRouter()


@router.post("/surveys", status_code=201)
async def create_survey(
    survey_data: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new survey"""
    service = EngagementService(db)
    return await service.create_survey(survey_data)


@router.get("/surveys")
async def get_surveys(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all surveys"""
    service = EngagementService(db)
    return await service.get_surveys(is_active=is_active)


@router.post("/recognitions", status_code=201)
async def create_recognition(
    recognition_data: RecognitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create employee recognition"""
    service = EngagementService(db)
    return await service.create_recognition(recognition_data)


@router.get("/recognitions")
async def get_recognitions(
    employee_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get recognitions"""
    service = EngagementService(db)
    emp_id = uuid.UUID(employee_id) if employee_id else None
    return await service.get_recognitions(employee_id=emp_id)

