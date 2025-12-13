"""Learning & Development Module - Models"""
from sqlalchemy import Column, String, Date, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin

class TrainingCourse(BaseModel, TenantMixin, Base):
    __tablename__ = "training_courses"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_hours = Column(Integer, nullable=True)
    provider = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)

class TrainingEnrollment(BaseModel, TenantMixin, AuditMixin, Base):
    __tablename__ = "training_enrollments"
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('training_courses.id'), nullable=False)
    enrollment_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    status = Column(String(20), default="enrolled")  # enrolled, in_progress, completed, dropped
    certificate_url = Column(String(500), nullable=True)
