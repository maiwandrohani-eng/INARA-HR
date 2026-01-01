"""Enhanced Exit Management Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from modules.exit_management.repositories import ExitInterviewRepository, ExitChecklistRepository, KnowledgeTransferRepository
from modules.exit_management.schemas import ExitInterviewCreate, ExitChecklistCreate, KnowledgeTransferCreate


class ExitManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.interview_repo = ExitInterviewRepository(db)
        self.checklist_repo = ExitChecklistRepository(db)
        self.transfer_repo = KnowledgeTransferRepository(db)
    
    async def create_exit_interview(self, interview_data: ExitInterviewCreate, country_code: str = "US") -> dict:
        interview = await self.interview_repo.create(interview_data, country_code)
        await self.db.commit()
        return {"id": str(interview.id), "resignation_id": str(interview.resignation_id)}
    
    async def create_checklist_item(self, checklist_data: ExitChecklistCreate, country_code: str = "US") -> dict:
        checklist = await self.checklist_repo.create(checklist_data, country_code)
        await self.db.commit()
        return {"id": str(checklist.id), "checklist_item": checklist.checklist_item}
    
    async def get_resignation_checklist(self, resignation_id: uuid.UUID) -> List[dict]:
        items = await self.checklist_repo.get_by_resignation(resignation_id)
        return [{
            "id": str(item.id),
            "checklist_item": item.checklist_item,
            "category": item.category,
            "is_completed": item.is_completed,
            "is_critical": item.is_critical
        } for item in items]
    
    async def create_knowledge_transfer(self, transfer_data: KnowledgeTransferCreate, country_code: str = "US") -> dict:
        transfer = await self.transfer_repo.create(transfer_data, country_code)
        await self.db.commit()
        return {"id": str(transfer.id), "knowledge_area": transfer.knowledge_area}

