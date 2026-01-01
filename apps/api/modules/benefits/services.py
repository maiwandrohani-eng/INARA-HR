"""Benefits Management Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
import uuid

from modules.benefits.repositories import (
    BenefitPlanRepository, BenefitEnrollmentRepository, BenefitDependentRepository
)
from modules.benefits.schemas import (
    BenefitPlanCreate, BenefitEnrollmentCreate, BenefitDependentCreate
)
from core.exceptions import NotFoundException, BadRequestException


class BenefitService:
    """Service for benefit management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_repo = BenefitPlanRepository(db)
        self.enrollment_repo = BenefitEnrollmentRepository(db)
        self.dependent_repo = BenefitDependentRepository(db)
    
    # Benefit Plan methods
    async def create_plan(self, plan_data: BenefitPlanCreate) -> dict:
        """Create a new benefit plan"""
        plan = await self.plan_repo.create(plan_data)
        await self.db.commit()
        return {
            "id": str(plan.id),
            "name": plan.name,
            "benefit_type": plan.benefit_type,
            "is_active": plan.is_active
        }
    
    async def get_plans(self, benefit_type: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]:
        """Get all benefit plans"""
        plans = await self.plan_repo.get_all(benefit_type=benefit_type, is_active=is_active)
        return [{
            "id": str(p.id),
            "name": p.name,
            "benefit_type": p.benefit_type,
            "provider": p.provider,
            "description": p.description,
            "is_active": p.is_active,
            "employer_contribution_amount": float(p.employer_contribution_amount) if p.employer_contribution_amount else None,
            "employee_cost_per_pay_period": float(p.employee_cost_per_pay_period) if p.employee_cost_per_pay_period else None,
            "currency": p.currency
        } for p in plans]
    
    # Enrollment methods
    async def enroll_employee(self, enrollment_data: BenefitEnrollmentCreate) -> dict:
        """Enroll employee in a benefit plan"""
        # Verify plan exists and is active
        plan = await self.plan_repo.get_by_id(enrollment_data.benefit_plan_id)
        if not plan:
            raise NotFoundException(resource="Benefit plan")
        
        if not plan.is_active:
            raise BadRequestException(message="Benefit plan is not active")
        
        enrollment = await self.enrollment_repo.create(enrollment_data)
        await self.db.commit()
        
        return {
            "id": str(enrollment.id),
            "employee_id": str(enrollment.employee_id),
            "benefit_plan_id": str(enrollment.benefit_plan_id),
            "status": enrollment.status,
            "effective_date": str(enrollment.effective_date)
        }
    
    async def get_employee_enrollments(self, employee_id: uuid.UUID) -> List[dict]:
        """Get all enrollments for an employee"""
        enrollments = await self.enrollment_repo.get_by_employee(employee_id)
        return [{
            "id": str(e.id),
            "benefit_plan_id": str(e.benefit_plan_id),
            "plan_name": e.plan.name if e.plan else None,
            "benefit_type": e.plan.benefit_type if e.plan else None,
            "enrollment_date": str(e.enrollment_date),
            "effective_date": str(e.effective_date),
            "status": e.status,
            "coverage_level": e.coverage_level,
            "dependents_count": e.dependents_count
        } for e in enrollments]
    
    async def cancel_enrollment(self, enrollment_id: uuid.UUID, end_date: Optional[date] = None) -> dict:
        """Cancel an enrollment"""
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise NotFoundException(resource="Enrollment")
        
        enrollment.status = "cancelled"
        enrollment.end_date = end_date or date.today()
        await self.db.commit()
        
        return {"id": str(enrollment.id), "status": enrollment.status}
    
    # Dependent methods
    async def add_dependent(self, dependent_data: BenefitDependentCreate) -> dict:
        """Add a dependent to an enrollment"""
        enrollment = await self.enrollment_repo.get_by_id(dependent_data.enrollment_id)
        if not enrollment:
            raise NotFoundException(resource="Enrollment")
        
        dependent = await self.dependent_repo.create(dependent_data)
        
        # Update dependents count
        dependents = await self.dependent_repo.get_by_enrollment(enrollment.id)
        enrollment.dependents_count = len([d for d in dependents if d.is_active])
        await self.db.commit()
        
        return {
            "id": str(dependent.id),
            "first_name": dependent.first_name,
            "last_name": dependent.last_name,
            "relationship": dependent.relationship
        }

