"""Learning Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from core.database import get_db
from core.dependencies import get_current_active_user, require_admin
from modules.learning.services import LearningService
from modules.learning.schemas import CourseCreate, EnrollmentCreate, EnrollmentStatusUpdate
from modules.learning.models import TrainingEnrollment
from modules.employees.repositories import EmployeeRepository

router = APIRouter()


@router.get("/courses")
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all training courses"""
    learning_service = LearningService(db)
    courses = await learning_service.get_all_courses()
    return courses


@router.post("/courses", status_code=201)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new training course"""
    learning_service = LearningService(db)
    course = await learning_service.create_course(course_data)
    return course


@router.post("/enrollments")
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Enroll in a training course"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    learning_service = LearningService(db)
    enrollment = await learning_service.enroll_employee(employee.id, enrollment_data)
    return enrollment


@router.get("/my-courses")
async def my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get my enrolled courses"""
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    learning_service = LearningService(db)
    enrollments = await learning_service.get_employee_enrollments(employee.id)
    return enrollments


@router.patch("/enrollments/{enrollment_id}/status")
async def update_enrollment_status(
    enrollment_id: str,
    status_data: EnrollmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update enrollment status"""
    try:
        enrollment_uuid = uuid.UUID(enrollment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid enrollment ID format")
    
    learning_service = LearningService(db)
    enrollment = await learning_service.update_enrollment_status(
        enrollment_uuid,
        status_data.status,
        status_data.completion_date
    )
    return enrollment


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete training enrollment (Admin only - soft delete)"""
    try:
        enrollment_uuid = uuid.UUID(enrollment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid enrollment ID format")
    
    result = await db.execute(
        select(TrainingEnrollment).where(
            TrainingEnrollment.id == enrollment_uuid,
            TrainingEnrollment.is_deleted == False
        )
    )
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Soft delete
    enrollment.is_deleted = True
    enrollment.deleted_at = datetime.utcnow()
    
    await db.commit()
    return None
