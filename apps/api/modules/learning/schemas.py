"""Learning - Schemas"""
from pydantic import BaseModel
import uuid
class CourseCreate(BaseModel):
    title: str
class EnrollmentCreate(BaseModel):
    course_id: uuid.UUID
