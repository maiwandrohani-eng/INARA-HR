"""
Recruitment Module - Models (ATS - Applicant Tracking System)
Job postings, applications, interviews, offer letters
"""

from sqlalchemy import Column, String, Date, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from core.database import Base
from core.models import BaseModel, TenantMixin, AuditMixin


class JobPosting(BaseModel, TenantMixin, AuditMixin, Base):
    """Job posting/vacancy"""
    __tablename__ = "job_postings"
    
    title = Column(String(200), nullable=False)
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id'), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    
    employment_type = Column(String(50), nullable=False)
    location = Column(String(200), nullable=True)
    salary_range_min = Column(String(20), nullable=True)
    salary_range_max = Column(String(20), nullable=True)
    currency = Column(String(3), default="USD")
    
    status = Column(String(20), default="draft")  # draft, open, closed, filled
    posted_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    
    applications = relationship("Application", back_populates="job_posting")


class Application(BaseModel, TenantMixin, AuditMixin, Base):
    """Job application"""
    __tablename__ = "applications"
    
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id'), nullable=False)
    
    # Applicant Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    resume_url = Column(String(500), nullable=True)
    cover_letter = Column(Text, nullable=True)
    
    # Application Status
    status = Column(String(50), default="received")  # received, screening, interview, offer, hired, rejected
    source = Column(String(100), nullable=True)  # website, referral, linkedin, etc.
    
    applied_date = Column(Date, nullable=False)
    
    job_posting = relationship("JobPosting", back_populates="applications")
    interviews = relationship("Interview", back_populates="application")


class Interview(BaseModel, TenantMixin, AuditMixin, Base):
    """Interview schedule and feedback"""
    __tablename__ = "interviews"
    
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    
    interview_type = Column(String(50), nullable=False)  # phone, video, in-person, panel
    scheduled_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    
    interviewer_ids = Column(Text, nullable=True)  # JSON array of employee IDs
    
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled, no-show
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    
    application = relationship("Application", back_populates="interviews")


class OfferLetter(BaseModel, TenantMixin, AuditMixin, Base):
    """Job offer letters"""
    __tablename__ = "offer_letters"
    
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    
    position_title = Column(String(200), nullable=False)
    salary = Column(String(20), nullable=False)
    currency = Column(String(3), default="USD")
    start_date = Column(Date, nullable=False)
    
    offer_letter_url = Column(String(500), nullable=True)
    sent_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    status = Column(String(20), default="draft")  # draft, sent, accepted, rejected, expired
    accepted_date = Column(Date, nullable=True)
    rejected_reason = Column(Text, nullable=True)
