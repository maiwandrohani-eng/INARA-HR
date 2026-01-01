"""Analytics Module - Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_active_user, require_hr_read
from modules.analytics.services import AnalyticsService

router = APIRouter()


@router.get("/dashboard")
async def get_hr_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get HR dashboard metrics"""
    analytics_service = AnalyticsService(db)
    metrics = await analytics_service.get_dashboard_metrics()
    return metrics


@router.get("/headcount")
async def get_headcount_report(
    group_by: str = "department",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get headcount by department/location"""
    analytics_service = AnalyticsService(db)
    report = await analytics_service.get_headcount_report(group_by=group_by)
    return report


@router.get("/turnover")
async def get_turnover_rate(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get employee turnover rate"""
    analytics_service = AnalyticsService(db)
    turnover = await analytics_service.get_turnover_rate(year=year)
    return turnover


@router.get("/leave-utilization")
async def get_leave_utilization(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_read)
):
    """Get leave utilization statistics"""
    analytics_service = AnalyticsService(db)
    utilization = await analytics_service.get_leave_utilization(year=year)
    return utilization
