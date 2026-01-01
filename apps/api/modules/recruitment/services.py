"""Recruitment Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timedelta
import uuid
import json

from modules.recruitment.repositories import (
    JobPostingRepository, ApplicationRepository,
    InterviewRepository, OfferLetterRepository
)
from modules.recruitment.schemas import (
    JobPostingCreate, ApplicationCreate, InterviewSchedule, OfferLetterCreate
)
from core.exceptions import NotFoundException, BadRequestException


class RecruitmentService:
    """Service for recruitment and ATS operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.posting_repo = JobPostingRepository(db)
        self.application_repo = ApplicationRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.offer_repo = OfferLetterRepository(db)
    
    # Job Posting methods
    async def create_job_posting(self, posting_data: JobPostingCreate, created_by: uuid.UUID) -> dict:
        """Create a new job posting"""
        from modules.employees.repositories import EmployeeRepository
        from sqlalchemy import select
        from modules.employees.models import Employee
        from modules.auth.models import User
        
        # Get employee to retrieve country_code
        employee_repo = EmployeeRepository(self.db)
        employee = await employee_repo.get_by_user_id(created_by)
        
        posting_dict = posting_data.model_dump()
        posting_dict["status"] = "draft"
        posting_dict["created_by"] = created_by
        # Set country_code from employee, or default to 'US'
        posting_dict["country_code"] = employee.country_code if employee and employee.country_code else 'US'
        
        posting = await self.posting_repo.create(posting_dict)
        await self.db.commit()
        
        return {
            "id": str(posting.id),
            "title": posting.title,
            "status": posting.status,
            "description": posting.description
        }
    
    async def publish_job_posting(self, posting_id: uuid.UUID) -> dict:
        """Publish a job posting"""
        posting = await self.posting_repo.get_by_id(posting_id)
        if not posting:
            raise NotFoundException(resource="Job posting")
        
        posting.status = "open"
        posting.posted_date = date.today()
        await self.db.commit()
        
        return {"id": str(posting.id), "status": posting.status}
    
    async def get_job_postings(self, status: Optional[str] = None) -> List[dict]:
        """Get all job postings"""
        postings = await self.posting_repo.get_all(status=status)
        return [{
            "id": str(p.id),
            "title": p.title,
            "description": p.description,
            "employment_type": p.employment_type,
            "location": p.location,
            "status": p.status,
            "posted_date": str(p.posted_date) if p.posted_date else None,
            "closing_date": str(p.closing_date) if p.closing_date else None,
            "salary_range_min": p.salary_range_min,
            "salary_range_max": p.salary_range_max,
            "currency": p.currency or "USD"
        } for p in postings]
    
    # Application methods
    async def submit_application(self, application_data: ApplicationCreate) -> dict:
        """Submit a job application"""
        # Verify job posting exists and is open
        posting = await self.posting_repo.get_by_id(application_data.job_posting_id)
        if not posting:
            raise NotFoundException(resource="Job posting")
        
        if posting.status != "open":
            raise BadRequestException(message="Job posting is not currently accepting applications")
        
        application_dict = application_data.model_dump()
        application_dict["applied_date"] = date.today()
        application_dict["status"] = "received"
        
        application = await self.application_repo.create(application_dict)
        await self.db.commit()
        
        return {
            "id": str(application.id),
            "status": application.status,
            "applied_date": str(application.applied_date)
        }
    
    async def get_applications(
        self, 
        job_posting_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """Get all applications"""
        applications = await self.application_repo.get_all(job_posting_id, status)
        return [{
            "id": str(a.id),
            "job_posting_id": str(a.job_posting_id),
            "first_name": a.first_name,
            "last_name": a.last_name,
            "email": a.email,
            "status": a.status,
            "applied_date": str(a.applied_date)
        } for a in applications]
    
    async def update_application_status(
        self, 
        application_id: uuid.UUID, 
        status: str
    ) -> dict:
        """Update application status"""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            raise NotFoundException(resource="Application")
        
        application.status = status
        await self.db.commit()
        
        return {"id": str(application.id), "status": application.status}
    
    # Interview methods
    async def schedule_interview(
        self, 
        interview_data: InterviewSchedule,
        interviewer_ids: List[uuid.UUID],
        created_by: uuid.UUID
    ) -> dict:
        """Schedule an interview"""
        # Verify application exists
        application = await self.application_repo.get_by_id(interview_data.application_id)
        if not application:
            raise NotFoundException(resource="Application")
        
        interview_dict = interview_data.model_dump()
        interview_dict["interviewer_ids"] = json.dumps([str(id) for id in interviewer_ids])
        interview_dict["status"] = "scheduled"
        interview_dict["created_by"] = created_by
        
        interview = await self.interview_repo.create(interview_dict)
        await self.db.commit()
        
        return {
            "id": str(interview.id),
            "application_id": str(interview.application_id),
            "scheduled_date": str(interview.scheduled_date),
            "status": interview.status
        }
    
    async def get_interviews_for_application(self, application_id: uuid.UUID) -> List[dict]:
        """Get all interviews for an application"""
        interviews = await self.interview_repo.get_by_application(application_id)
        return [{
            "id": str(i.id),
            "interview_type": i.interview_type,
            "scheduled_date": str(i.scheduled_date),
            "status": i.status,
            "rating": i.rating
        } for i in interviews]
    
    async def update_interview_feedback(
        self,
        interview_id: uuid.UUID,
        feedback: str,
        rating: Optional[int] = None
    ) -> dict:
        """Update interview feedback"""
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            raise NotFoundException(resource="Interview")
        
        interview.feedback = feedback
        interview.rating = rating
        interview.status = "completed"
        await self.db.commit()
        
        return {"id": str(interview.id), "status": interview.status}
    
    # Offer letter methods
    async def create_offer_letter(
        self,
        offer_data: OfferLetterCreate,
        created_by: uuid.UUID
    ) -> dict:
        """Create an offer letter"""
        # Verify application exists
        application = await self.application_repo.get_by_id(offer_data.application_id)
        if not application:
            raise NotFoundException(resource="Application")
        
        offer_dict = offer_data.model_dump()
        offer_dict["status"] = "draft"
        offer_dict["created_by"] = created_by
        
        offer = await self.offer_repo.create(offer_dict)
        await self.db.commit()
        
        return {
            "id": str(offer.id),
            "application_id": str(offer.application_id),
            "status": offer.status
        }
    
    async def send_offer_letter(self, offer_id: uuid.UUID) -> dict:
        """Send offer letter to candidate"""
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundException(resource="Offer letter")
        
        offer.status = "sent"
        offer.sent_date = date.today()
        offer.expiry_date = date.today() + timedelta(days=7)  # 7 days to respond
        
        await self.db.commit()
        
        return {"id": str(offer.id), "status": offer.status}
