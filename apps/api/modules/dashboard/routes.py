"""
Dashboard Module - API Routes
Endpoints for employee and supervisor dashboards
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.dashboard.services import DashboardService

router = APIRouter()


@router.get("/role")
async def get_user_role(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Check if user is a supervisor (has direct reports)
    """
    service = DashboardService(db)
    import uuid
    is_supervisor = await service.check_if_supervisor(uuid.UUID(current_user["id"]))
    
    return {
        "is_supervisor": is_supervisor,
        "user_id": current_user["id"],
        "email": current_user["email"]
    }


@router.get("/is-supervisor-of/{employee_id}")
async def is_supervisor_of(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Check if current user is supervisor of a specific employee
    """
    from modules.employees.repositories import EmployeeRepository
    from sqlalchemy import select
    import uuid
    
    employee_repo = EmployeeRepository(db)
    current_employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not current_employee:
        return {"is_supervisor": False, "reason": "Current user has no employee record"}
    
    target_employee = await employee_repo.get_by_id(uuid.UUID(employee_id))
    if not target_employee:
        return {"is_supervisor": False, "reason": "Target employee not found"}
    
    is_supervisor = target_employee.manager_id == current_employee.id
    
    return {
        "is_supervisor": is_supervisor,
        "current_employee_id": str(current_employee.id),
        "target_employee_id": employee_id,
        "target_manager_id": str(target_employee.manager_id) if target_employee.manager_id else None
    }


@router.get("/employee")
async def get_employee_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get employee personal dashboard data
    """
    import uuid
    service = DashboardService(db)
    user_id = uuid.UUID(current_user["id"])
    dashboard_data = await service.get_employee_dashboard(user_id)
    
    return dashboard_data


@router.get("/supervisor")
async def get_supervisor_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get supervisor dashboard with team data and pending approvals
    """
    import uuid
    service = DashboardService(db)
    user_id = uuid.UUID(current_user["id"])
    
    # Check if user is actually a supervisor
    is_supervisor = await service.check_if_supervisor(user_id)
    if not is_supervisor:
        from core.exceptions import ForbiddenException
        raise ForbiddenException(detail="User is not a supervisor")
    
    dashboard_data = await service.get_supervisor_dashboard(user_id)
    
    return dashboard_data
