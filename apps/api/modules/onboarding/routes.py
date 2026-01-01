"""Onboarding Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.onboarding.services import OnboardingService
from modules.employees.repositories import EmployeeRepository

router = APIRouter()


@router.get("/checklist")
async def get_onboarding_checklist(
    employee_id: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get onboarding checklist"""
    employee_repo = EmployeeRepository(db)
    
    if employee_id:
        import uuid
        try:
            target_employee_id = uuid.UUID(employee_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid employee ID format")
    else:
        # Get current user's employee record
        employee = await employee_repo.get_by_user_id(current_user["id"])
        if not employee:
            raise HTTPException(status_code=404, detail="Employee profile not found")
        target_employee_id = employee.id
    
    onboarding_service = OnboardingService(db)
    checklist = await onboarding_service.get_checklist(target_employee_id)
    return checklist


@router.post("/checklist/{task_id}/complete")
async def complete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Complete an onboarding task"""
    import uuid
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    onboarding_service = OnboardingService(db)
    task = await onboarding_service.complete_task(task_uuid)
    return task
