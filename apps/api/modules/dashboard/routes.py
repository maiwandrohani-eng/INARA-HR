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
    is_supervisor = await service.check_if_supervisor(current_user["id"])
    
    return {
        "is_supervisor": is_supervisor,
        "user_id": current_user["id"],
        "email": current_user["email"]
    }


@router.get("/employee")
async def get_employee_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get employee personal dashboard data
    """
    service = DashboardService(db)
    dashboard_data = await service.get_employee_dashboard(current_user["id"])
    
    return dashboard_data


@router.get("/supervisor")
async def get_supervisor_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get supervisor dashboard with team data and pending approvals
    """
    service = DashboardService(db)
    
    # Check if user is actually a supervisor
    is_supervisor = await service.check_if_supervisor(current_user["id"])
    if not is_supervisor:
        from core.exceptions import ForbiddenException
        raise ForbiddenException(detail="User is not a supervisor")
    
    dashboard_data = await service.get_supervisor_dashboard(current_user["id"])
    
    return dashboard_data
