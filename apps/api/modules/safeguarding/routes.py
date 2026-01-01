"""Safeguarding Module - Routes"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime

from core.database import get_db
from core.dependencies import get_current_active_user, require_admin
from modules.safeguarding.services import SafeguardingService
from modules.safeguarding.models import SafeguardingCase
from modules.safeguarding.schemas import (
    SafeguardingCaseCreate,
    SafeguardingCaseUpdate,
    SafeguardingCaseResponse
)

router = APIRouter()


@router.post("/cases", response_model=SafeguardingCaseResponse, status_code=201)
async def report_case(
    case_data: SafeguardingCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Report a new safeguarding case
    
    Any authenticated user can submit a safeguarding report. The report will be sent to:
    - All Admin users
    - All HR Managers
    
    Set `is_anonymous: true` to submit anonymously (reporter identity will not be stored).
    """
    case = await SafeguardingService.create_case(
        session=db,
        case_data=case_data,
        reporter_id=current_user["id"],
        country_code=current_user["country_code"]
    )
    return case


@router.get("/cases", response_model=List[SafeguardingCaseResponse])
async def list_cases(
    status: Optional[str] = Query(None, description="Filter by status: open, investigating, resolved, closed"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    List all safeguarding cases (Admin/HR only)
    
    Only users with Admin or HR Manager roles can view safeguarding cases.
    """
    cases = await SafeguardingService.get_all_cases(
        session=db,
        country_code=current_user["country_code"],
        status=status
    )
    return cases


@router.get("/cases/{case_id}", response_model=SafeguardingCaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get specific case details (Admin/HR only)
    
    Returns full details of a safeguarding case including investigation notes and outcomes.
    """
    case = await SafeguardingService.get_case_by_id(
        session=db,
        case_id=case_id
    )
    return case


@router.patch("/cases/{case_id}", response_model=SafeguardingCaseResponse)
async def update_case(
    case_id: str,
    update_data: SafeguardingCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Update a safeguarding case (Admin/HR only)
    
    Update investigation status, assign investigators, add findings, or close cases.
    """
    case = await SafeguardingService.update_case(
        session=db,
        case_id=case_id,
        update_data=update_data,
        user_id=current_user["id"]
    )
    return case


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_safeguarding_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete safeguarding case (Admin only - soft delete)"""
    try:
        case_uuid = uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    result = await db.execute(
        select(SafeguardingCase).where(
            SafeguardingCase.id == case_uuid,
            SafeguardingCase.is_deleted == False
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Safeguarding case not found")
    
    # Soft delete
    case.is_deleted = True
    case.deleted_at = datetime.utcnow()
    
    await db.commit()
    return None
