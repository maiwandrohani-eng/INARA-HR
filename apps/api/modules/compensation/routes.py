"""Compensation Module - Routes"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user, require_hr_admin
from core.exceptions import NotFoundException
from modules.admin.schemas import (
    SalaryBandCreate,
    SalaryBandUpdate,
    SalaryBandResponse,
)
from modules.admin.repositories import SalaryBandRepository

router = APIRouter()


# Salary Bands Endpoints
@router.get("/salary-bands", response_model=List[SalaryBandResponse])
async def list_salary_bands(
    country_code: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all salary bands"""
    repo = SalaryBandRepository(db)
    bands = await repo.get_all(country_code=country_code)
    return bands


@router.post("/salary-bands", response_model=SalaryBandResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_band(
    data: SalaryBandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """Create a new salary band"""
    repo = SalaryBandRepository(db)
    band = await repo.create(data.model_dump())
    await db.commit()
    return band


@router.put("/salary-bands/{band_id}", response_model=SalaryBandResponse)
async def update_salary_band(
    band_id: uuid.UUID,
    data: SalaryBandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """Update a salary band"""
    repo = SalaryBandRepository(db)
    band = await repo.get_by_id(band_id)
    
    if not band:
        raise NotFoundException(resource="Salary band")
    
    updated_band = await repo.update(band, data.model_dump(exclude_unset=True))
    await db.commit()
    return updated_band


@router.delete("/salary-bands/{band_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_band(
    band_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """Delete a salary band"""
    repo = SalaryBandRepository(db)
    band = await repo.get_by_id(band_id)
    
    if not band:
        raise NotFoundException(resource="Salary band")
    
    await repo.delete(band)
    await db.commit()


# Legacy Endpoints
@router.get("/salary-history/{employee_id}")
async def get_salary_history(employee_id: str, db = Depends(get_db), current_user = Depends(require_hr_admin)):
    return {"message": f"Get salary history for {employee_id} - TODO"}


@router.post("/salary-adjustment")
async def add_salary_adjustment(db = Depends(get_db), current_user = Depends(require_hr_admin)):
    return {"message": "Add salary adjustment - TODO"}
