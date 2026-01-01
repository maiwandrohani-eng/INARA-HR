"""Benefits Management Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date
import uuid

from modules.benefits.models import (
    BenefitPlan, BenefitEnrollment, BenefitDependent, OpenEnrollmentPeriod
)
from modules.benefits.schemas import (
    BenefitPlanCreate, BenefitEnrollmentCreate, BenefitDependentCreate,
    OpenEnrollmentPeriodCreate
)


class BenefitPlanRepository:
    """Repository for benefit plan operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, plan_data: BenefitPlanCreate) -> BenefitPlan:
        """Create a new benefit plan"""
        plan = BenefitPlan(**plan_data.model_dump())
        self.db.add(plan)
        await self.db.flush()
        await self.db.refresh(plan)
        return plan
    
    async def get_by_id(self, plan_id: uuid.UUID) -> Optional[BenefitPlan]:
        """Get benefit plan by ID"""
        result = await self.db.execute(
            select(BenefitPlan).where(
                and_(BenefitPlan.id == plan_id, BenefitPlan.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, benefit_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[BenefitPlan]:
        """Get all benefit plans"""
        query = select(BenefitPlan).where(BenefitPlan.is_deleted == False)
        
        if benefit_type:
            query = query.where(BenefitPlan.benefit_type == benefit_type)
        
        if is_active is not None:
            query = query.where(BenefitPlan.is_active == is_active)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, plan_id: uuid.UUID, plan_data: dict) -> Optional[BenefitPlan]:
        """Update benefit plan"""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return None
        
        for key, value in plan_data.items():
            if hasattr(plan, key) and value is not None:
                setattr(plan, key, value)
        
        await self.db.flush()
        return plan


class BenefitEnrollmentRepository:
    """Repository for benefit enrollment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, enrollment_data: BenefitEnrollmentCreate) -> BenefitEnrollment:
        """Create a new enrollment"""
        enrollment = BenefitEnrollment(**enrollment_data.model_dump())
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
    
    async def get_by_id(self, enrollment_id: uuid.UUID) -> Optional[BenefitEnrollment]:
        """Get enrollment by ID"""
        result = await self.db.execute(
            select(BenefitEnrollment).where(
                and_(BenefitEnrollment.id == enrollment_id, BenefitEnrollment.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(self, employee_id: uuid.UUID, status: Optional[str] = None) -> List[BenefitEnrollment]:
        """Get all enrollments for an employee"""
        query = select(BenefitEnrollment).where(
            and_(
                BenefitEnrollment.employee_id == employee_id,
                BenefitEnrollment.is_deleted == False
            )
        )
        
        if status:
            query = query.where(BenefitEnrollment.status == status)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, enrollment_id: uuid.UUID, enrollment_data: dict) -> Optional[BenefitEnrollment]:
        """Update enrollment"""
        enrollment = await self.get_by_id(enrollment_id)
        if not enrollment:
            return None
        
        for key, value in enrollment_data.items():
            if hasattr(enrollment, key) and value is not None:
                setattr(enrollment, key, value)
        
        await self.db.flush()
        return enrollment


class BenefitDependentRepository:
    """Repository for benefit dependent operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, dependent_data: BenefitDependentCreate) -> BenefitDependent:
        """Create a new dependent"""
        dependent = BenefitDependent(**dependent_data.model_dump())
        self.db.add(dependent)
        await self.db.flush()
        await self.db.refresh(dependent)
        return dependent
    
    async def get_by_enrollment(self, enrollment_id: uuid.UUID) -> List[BenefitDependent]:
        """Get all dependents for an enrollment"""
        result = await self.db.execute(
            select(BenefitDependent).where(
                and_(
                    BenefitDependent.enrollment_id == enrollment_id,
                    BenefitDependent.is_deleted == False
                )
            )
        )
        return list(result.scalars().all())
    
    async def delete(self, dependent_id: uuid.UUID) -> bool:
        """Soft delete a dependent"""
        result = await self.db.execute(
            select(BenefitDependent).where(
                and_(BenefitDependent.id == dependent_id, BenefitDependent.is_deleted == False)
            )
        )
        dependent = result.scalar_one_or_none()
        if dependent:
            dependent.is_deleted = True
            dependent.deleted_at = date.today()
            await self.db.flush()
            return True
        return False

