"""Benefits Management Module - Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.benefits.services import BenefitService
from modules.benefits.schemas import (
    BenefitPlanCreate, BenefitEnrollmentCreate, BenefitDependentCreate,
    BenefitPlanUpdate, BenefitEnrollmentUpdate
)

router = APIRouter()


@router.post("/plans", status_code=201)
async def create_benefit_plan(
    plan_data: BenefitPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new benefit plan (admin only)"""
    benefit_service = BenefitService(db)
    plan = await benefit_service.create_plan(plan_data)
    return plan


@router.get("/plans")
async def list_benefit_plans(
    benefit_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all benefit plans"""
    benefit_service = BenefitService(db)
    plans = await benefit_service.get_plans(benefit_type=benefit_type, is_active=is_active)
    return plans


@router.post("/enrollments", status_code=201)
async def enroll_employee(
    enrollment_data: BenefitEnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Enroll employee in a benefit plan"""
    benefit_service = BenefitService(db)
    enrollment = await benefit_service.enroll_employee(enrollment_data)
    return enrollment


@router.get("/enrollments/employee/{employee_id}")
async def get_employee_enrollments(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all enrollments for an employee"""
    try:
        employee_uuid = uuid.UUID(employee_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid employee ID format")
    
    benefit_service = BenefitService(db)
    enrollments = await benefit_service.get_employee_enrollments(employee_uuid)
    return enrollments


@router.post("/enrollments/{enrollment_id}/cancel")
async def cancel_enrollment(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Cancel an enrollment"""
    try:
        enrollment_uuid = uuid.UUID(enrollment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid enrollment ID format")
    
    benefit_service = BenefitService(db)
    result = await benefit_service.cancel_enrollment(enrollment_uuid)
    return result


@router.post("/dependents", status_code=201)
async def add_dependent(
    dependent_data: BenefitDependentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Add a dependent to an enrollment"""
    benefit_service = BenefitService(db)
    dependent = await benefit_service.add_dependent(dependent_data)
    return dependent

