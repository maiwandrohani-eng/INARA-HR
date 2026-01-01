"""Learning Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
import uuid

from modules.learning.repositories import TrainingCourseRepository, TrainingEnrollmentRepository
from modules.learning.schemas import CourseCreate, EnrollmentCreate
from core.exceptions import NotFoundException, BadRequestException, AlreadyExistsException


class LearningService:
    """Service for learning and development operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = TrainingCourseRepository(db)
        self.enrollment_repo = TrainingEnrollmentRepository(db)
    
    async def create_course(self, course_data: CourseCreate) -> dict:
        """Create a new training course"""
        course_dict = course_data.model_dump()
        course = await self.course_repo.create(course_dict)
        await self.db.commit()
        return {
            "id": str(course.id),
            "title": course.title,
            "description": course.description,
            "duration_hours": course.duration_hours,
            "provider": course.provider,
            "category": course.category
        }
    
    async def get_all_courses(self) -> List[dict]:
        """Get all training courses"""
        courses = await self.course_repo.get_all()
        return [{
            "id": str(c.id),
            "title": c.title,
            "description": c.description,
            "duration_hours": c.duration_hours,
            "provider": c.provider,
            "category": c.category
        } for c in courses]
    
    async def enroll_employee(
        self, 
        employee_id: uuid.UUID, 
        enrollment_data: EnrollmentCreate
    ) -> dict:
        """Enroll employee in a course"""
        # Check if course exists
        course = await self.course_repo.get_by_id(enrollment_data.course_id)
        if not course:
            raise NotFoundException(resource="Training course")
        
        # Check if already enrolled
        existing = await self.enrollment_repo.get_by_employee_and_course(
            employee_id, 
            enrollment_data.course_id
        )
        
        if existing and existing.status in ["enrolled", "in_progress"]:
            raise AlreadyExistsException(resource="Enrollment for this course")
        
        # Create enrollment
        enrollment = await self.enrollment_repo.create({
            "employee_id": employee_id,
            "course_id": enrollment_data.course_id,
            "enrollment_date": date.today(),
            "status": "enrolled"
        })
        await self.db.commit()
        
        return {
            "id": str(enrollment.id),
            "employee_id": str(enrollment.employee_id),
            "course_id": str(enrollment.course_id),
            "enrollment_date": str(enrollment.enrollment_date),
            "status": enrollment.status
        }
    
    async def get_employee_enrollments(self, employee_id: uuid.UUID) -> List[dict]:
        """Get all enrollments for an employee"""
        enrollments = await self.enrollment_repo.get_by_employee(employee_id)
        
        result = []
        for enrollment in enrollments:
            course = await self.course_repo.get_by_id(enrollment.course_id)
            result.append({
                "id": str(enrollment.id),
                "course": {
                    "id": str(course.id) if course else None,
                    "title": course.title if course else "Unknown",
                    "duration_hours": course.duration_hours if course else None
                },
                "enrollment_date": str(enrollment.enrollment_date),
                "completion_date": str(enrollment.completion_date) if enrollment.completion_date else None,
                "status": enrollment.status,
                "certificate_url": enrollment.certificate_url
            })
        
        return result
    
    async def update_enrollment_status(
        self,
        enrollment_id: uuid.UUID,
        status: str,
        completion_date: Optional[date] = None
    ) -> dict:
        """Update enrollment status"""
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise NotFoundException(resource="Enrollment")
        
        update_data = {"status": status}
        if completion_date:
            update_data["completion_date"] = completion_date
        elif status == "completed":
            update_data["completion_date"] = date.today()
        
        updated = await self.enrollment_repo.update(enrollment_id, update_data)
        await self.db.commit()
        
        return {
            "id": str(updated.id),
            "status": updated.status,
            "completion_date": str(updated.completion_date) if updated.completion_date else None
        }
