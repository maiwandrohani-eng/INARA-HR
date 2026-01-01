"""Asset/Equipment Management Module - Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.assets.services import AssetService
from modules.assets.schemas import AssetCreate, AssetAssignmentCreate, AssetMaintenanceCreate

router = APIRouter()


@router.post("/assets", status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new asset"""
    asset_service = AssetService(db)
    asset = await asset_service.create_asset(asset_data, country_code="US")
    return asset


@router.get("/assets")
async def list_assets(
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all assets"""
    asset_service = AssetService(db)
    assets = await asset_service.get_assets(status=status, asset_type=asset_type)
    return assets


@router.post("/assignments", status_code=201)
async def assign_asset(
    assignment_data: AssetAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Assign asset to employee"""
    asset_service = AssetService(db)
    assignment = await asset_service.assign_asset(assignment_data)
    return assignment


@router.post("/assignments/{assignment_id}/return")
async def return_asset(
    assignment_id: str,
    return_date: Optional[date] = None,
    condition: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Return an assigned asset"""
    try:
        assignment_uuid = uuid.UUID(assignment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assignment ID format")
    
    asset_service = AssetService(db)
    result = await asset_service.return_asset(assignment_uuid, return_date, condition)
    return result


@router.post("/maintenance", status_code=201)
async def schedule_maintenance(
    maintenance_data: AssetMaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Schedule asset maintenance"""
    asset_service = AssetService(db)
    maintenance = await asset_service.schedule_maintenance(maintenance_data)
    return maintenance

