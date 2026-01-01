"""Enhanced Exit Management Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime
import uuid

from modules.exit_management.models import ExitInterview, ExitChecklist, KnowledgeTransfer
from modules.exit_management.schemas import ExitInterviewCreate, ExitChecklistCreate, KnowledgeTransferCreate


class ExitInterviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, interview_data: ExitInterviewCreate, country_code: str) -> ExitInterview:
        interview = ExitInterview(**interview_data.model_dump(), country_code=country_code)
        self.db.add(interview)
        await self.db.flush()
        return interview
    
    async def get_by_resignation(self, resignation_id: uuid.UUID) -> ExitInterview:
        result = await self.db.execute(
            select(ExitInterview).where(
                and_(ExitInterview.resignation_id == resignation_id, ExitInterview.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()


class ExitChecklistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, checklist_data: ExitChecklistCreate, country_code: str) -> ExitChecklist:
        checklist = ExitChecklist(**checklist_data.model_dump(), country_code=country_code)
        self.db.add(checklist)
        await self.db.flush()
        return checklist
    
    async def get_by_resignation(self, resignation_id: uuid.UUID) -> List[ExitChecklist]:
        result = await self.db.execute(
            select(ExitChecklist).where(
                and_(ExitChecklist.resignation_id == resignation_id, ExitChecklist.is_deleted == False)
            )
        )
        return list(result.scalars().all())
    
    async def mark_complete(self, checklist_id: uuid.UUID, completed_by: uuid.UUID) -> ExitChecklist:
        result = await self.db.execute(
            select(ExitChecklist).where(
                and_(ExitChecklist.id == checklist_id, ExitChecklist.is_deleted == False)
            )
        )
        checklist = result.scalar_one_or_none()
        if checklist:
            checklist.is_completed = True
            checklist.completed_date = datetime.utcnow()
            checklist.completed_by = completed_by
            await self.db.flush()
        return checklist


class KnowledgeTransferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, transfer_data: KnowledgeTransferCreate, country_code: str) -> KnowledgeTransfer:
        transfer = KnowledgeTransfer(**transfer_data.model_dump(), country_code=country_code)
        self.db.add(transfer)
        await self.db.flush()
        return transfer
    
    async def get_by_resignation(self, resignation_id: uuid.UUID) -> List[KnowledgeTransfer]:
        result = await self.db.execute(
            select(KnowledgeTransfer).where(
                and_(KnowledgeTransfer.resignation_id == resignation_id, KnowledgeTransfer.is_deleted == False)
            )
        )
        return list(result.scalars().all())

