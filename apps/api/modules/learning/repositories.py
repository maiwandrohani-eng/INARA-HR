"""Learning Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date
import uuid

from modules.learning.models import TrainingCourse, TrainingEnrollment


class TrainingCourseRepository:
    """Repository for training course operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, course_data: dict) -> TrainingCourse:
        """Create a new training course"""
        course = TrainingCourse(**course_data)
        self.db.add(course)
        await self.db.flush()
        await self.db.refresh(course)
        return course
    
    async def get_by_id(self, course_id: uuid.UUID) -> Optional[TrainingCourse]:
        """Get course by ID"""
        result = await self.db.execute(
            select(TrainingCourse).where(
                and_(TrainingCourse.id == course_id, TrainingCourse.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[TrainingCourse]:
        """Get all training courses"""
        result = await self.db.execute(
            select(TrainingCourse).where(TrainingCourse.is_deleted == False)
        )
        return result.scalars().all()
    
    async def update(self, course_id: uuid.UUID, course_data: dict) -> Optional[TrainingCourse]:
        """Update training course"""
        course = await self.get_by_id(course_id)
        if not course:
            return None
        
        for key, value in course_data.items():
            if hasattr(course, key):
                setattr(course, key, value)
        
        await self.db.flush()
        return course


class TrainingEnrollmentRepository:
    """Repository for training enrollment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, enrollment_data: dict) -> TrainingEnrollment:
        """Create a new enrollment"""
        enrollment = TrainingEnrollment(**enrollment_data)
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
    
    async def get_by_id(self, enrollment_id: uuid.UUID) -> Optional[TrainingEnrollment]:
        """Get enrollment by ID"""
        result = await self.db.execute(
            select(TrainingEnrollment).where(
                and_(TrainingEnrollment.id == enrollment_id, TrainingEnrollment.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(self, employee_id: uuid.UUID) -> List[TrainingEnrollment]:
        """Get all enrollments for an employee"""
        result = await self.db.execute(
            select(TrainingEnrollment).where(
                and_(
                    TrainingEnrollment.employee_id == employee_id,
                    TrainingEnrollment.is_deleted == False
                )
            ).order_by(TrainingEnrollment.enrollment_date.desc())
        )
        return result.scalars().all()
    
    async def get_by_course(self, course_id: uuid.UUID) -> List[TrainingEnrollment]:
        """Get all enrollments for a course"""
        result = await self.db.execute(
            select(TrainingEnrollment).where(
                and_(
                    TrainingEnrollment.course_id == course_id,
                    TrainingEnrollment.is_deleted == False
                )
            )
        )
        return result.scalars().all()
    
    async def get_by_employee_and_course(
        self, 
        employee_id: uuid.UUID, 
        course_id: uuid.UUID
    ) -> Optional[TrainingEnrollment]:
        """Get enrollment for specific employee and course"""
        result = await self.db.execute(
            select(TrainingEnrollment).where(
                and_(
                    TrainingEnrollment.employee_id == employee_id,
                    TrainingEnrollment.course_id == course_id,
                    TrainingEnrollment.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, enrollment_id: uuid.UUID, enrollment_data: dict) -> Optional[TrainingEnrollment]:
        """Update enrollment"""
        enrollment = await self.get_by_id(enrollment_id)
        if not enrollment:
            return None
        
        for key, value in enrollment_data.items():
            if hasattr(enrollment, key):
                setattr(enrollment, key, value)
        
        await self.db.flush()
        return enrollment
