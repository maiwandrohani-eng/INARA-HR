"""Workforce Planning Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import date
import uuid

from modules.workforce.models import WorkforcePlan, PositionRequisition, HeadcountForecast
from modules.workforce.schemas import WorkforcePlanCreate, PositionRequisitionCreate, HeadcountForecastCreate


class WorkforcePlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, plan_data: WorkforcePlanCreate, country_code: str) -> WorkforcePlan:
        plan = WorkforcePlan(**plan_data.model_dump(), country_code=country_code)
        self.db.add(plan)
        await self.db.flush()
        return plan
    
    async def get_all(self, status: Optional[str] = None) -> List[WorkforcePlan]:
        query = select(WorkforcePlan).where(WorkforcePlan.is_deleted == False)
        if status:
            query = query.where(WorkforcePlan.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class PositionRequisitionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_requisition_number(self) -> str:
        result = await self.db.execute(select(func.count(PositionRequisition.id)))
        count = result.scalar() or 0
        return f"REQ-{date.today().year}-{count + 1:06d}"
    
    async def create(self, requisition_data: PositionRequisitionCreate, country_code: str) -> PositionRequisition:
        requisition_dict = requisition_data.model_dump(exclude_none=True)
        requisition_dict["requisition_number"] = await self.generate_requisition_number()
        requisition_dict["country_code"] = country_code
        
        # Handle requested_by - if None, we need to skip it and let DB handle constraint
        if "requested_by" in requisition_dict and requisition_dict["requested_by"] is None:
            # Remove None values that would violate constraints
            if requisition_dict.get("requested_by") is None:
                del requisition_dict["requested_by"]
        
        requisition = PositionRequisition(**requisition_dict)
        self.db.add(requisition)
        await self.db.flush()
        return requisition
    
    async def get_all(self, status: Optional[str] = None) -> List[PositionRequisition]:
        query = select(PositionRequisition).where(PositionRequisition.is_deleted == False)
        if status:
            query = query.where(PositionRequisition.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class HeadcountForecastRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, forecast_data: HeadcountForecastCreate, country_code: str) -> HeadcountForecast:
        forecast_dict = forecast_data.model_dump()
        if forecast_dict.get("planned_headcount") and forecast_dict.get("current_headcount"):
            forecast_dict["headcount_variance"] = forecast_dict["planned_headcount"] - forecast_dict["current_headcount"]
        forecast_dict["country_code"] = country_code
        forecast = HeadcountForecast(**forecast_dict)
        self.db.add(forecast)
        await self.db.flush()
        return forecast

