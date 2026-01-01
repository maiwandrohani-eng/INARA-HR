"""Travel Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from modules.travel.models import VisaRecord


class VisaRepository:
    """Repository for visa operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, visa_data: dict) -> VisaRecord:
        """Create visa record"""
        visa = VisaRecord(**visa_data)
        self.db.add(visa)
        await self.db.flush()
        await self.db.refresh(visa)
        return visa
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[VisaRecord]:
        """Get all visas for an employee"""
        result = await self.db.execute(
            select(VisaRecord).where(
                and_(
                    VisaRecord.employee_id == employee_id,
                    VisaRecord.is_deleted == False
                )
            ).order_by(VisaRecord.expiry_date)
        )
        return result.scalars().all()
    
    async def get_by_id(self, visa_id: uuid.UUID) -> Optional[VisaRecord]:
        """Get visa by ID"""
        result = await self.db.execute(
            select(VisaRecord).where(
                and_(VisaRecord.id == visa_id, VisaRecord.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, visa_id: uuid.UUID, visa_data: dict) -> Optional[VisaRecord]:
        """Update visa record"""
        visa = await self.get_by_id(visa_id)
        if not visa:
            return None
        
        for key, value in visa_data.items():
            if hasattr(visa, key):
                setattr(visa, key, value)
        
        await self.db.flush()
        return visa
