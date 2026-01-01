"""Travel Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
import uuid

from modules.travel.repositories import VisaRepository
from core.exceptions import NotFoundException


class TravelService:
    """Service for travel operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.visa_repo = VisaRepository(db)
    
    async def get_visa_records(self, employee_id: uuid.UUID) -> List[dict]:
        """Get visa records for an employee"""
        visas = await self.visa_repo.get_by_employee(employee_id)
        return [{
            "id": str(v.id),
            "country": v.country,
            "visa_type": v.visa_type,
            "visa_number": v.visa_number,
            "issue_date": str(v.issue_date) if v.issue_date else None,
            "expiry_date": str(v.expiry_date),
            "status": v.status,
            "notes": v.notes
        } for v in visas]
    
    async def add_visa_record(
        self,
        employee_id: uuid.UUID,
        country: str,
        visa_type: str,
        expiry_date: date,
        visa_number: str = None,
        issue_date: date = None,
        notes: str = None,
        created_by: uuid.UUID = None
    ) -> dict:
        """Add visa record"""
        visa_data = {
            "employee_id": employee_id,
            "country": country,
            "visa_type": visa_type,
            "expiry_date": expiry_date,
            "visa_number": visa_number,
            "issue_date": issue_date,
            "notes": notes,
            "status": "active"
        }
        if created_by:
            visa_data["created_by"] = created_by
        
        visa = await self.visa_repo.create(visa_data)
        await self.db.commit()
        
        return {
            "id": str(visa.id),
            "country": visa.country,
            "visa_type": visa.visa_type,
            "expiry_date": str(visa.expiry_date)
        }
