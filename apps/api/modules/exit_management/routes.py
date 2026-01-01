"""Enhanced Exit Management Module - Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.exit_management.services import ExitManagementService
from modules.exit_management.schemas import ExitInterviewCreate, ExitChecklistCreate, KnowledgeTransferCreate

router = APIRouter()


@router.post("/exit-interviews", status_code=201)
async def create_exit_interview(
    interview_data: ExitInterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create exit interview"""
    service = ExitManagementService(db)
    return await service.create_exit_interview(interview_data)


@router.post("/exit-checklists", status_code=201)
async def create_checklist_item(
    checklist_data: ExitChecklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create exit checklist item"""
    service = ExitManagementService(db)
    return await service.create_checklist_item(checklist_data)


@router.get("/exit-checklists/resignation/{resignation_id}")
async def get_resignation_checklist(
    resignation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get exit checklist for a resignation"""
    try:
        resignation_uuid = uuid.UUID(resignation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resignation ID format")
    
    service = ExitManagementService(db)
    return await service.get_resignation_checklist(resignation_uuid)


@router.post("/knowledge-transfers", status_code=201)
async def create_knowledge_transfer(
    transfer_data: KnowledgeTransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create knowledge transfer record"""
    service = ExitManagementService(db)
    return await service.create_knowledge_transfer(transfer_data)

