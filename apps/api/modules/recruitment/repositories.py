"""Recruitment Module - Repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date
import uuid

from modules.recruitment.models import JobPosting, Application, Interview, OfferLetter


class JobPostingRepository:
    """Repository for job posting operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, posting_data: dict) -> JobPosting:
        """Create a new job posting"""
        posting = JobPosting(**posting_data)
        self.db.add(posting)
        await self.db.flush()
        await self.db.refresh(posting)
        return posting
    
    async def get_by_id(self, posting_id: uuid.UUID) -> Optional[JobPosting]:
        """Get job posting by ID"""
        result = await self.db.execute(
            select(JobPosting).where(
                and_(JobPosting.id == posting_id, JobPosting.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, status: Optional[str] = None) -> List[JobPosting]:
        """Get all job postings, optionally filtered by status"""
        query = select(JobPosting).where(JobPosting.is_deleted == False)
        if status:
            query = query.where(JobPosting.status == status)
        query = query.order_by(JobPosting.posted_date.desc(), JobPosting.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, posting_id: uuid.UUID, posting_data: dict) -> Optional[JobPosting]:
        """Update job posting"""
        posting = await self.get_by_id(posting_id)
        if not posting:
            return None
        
        for key, value in posting_data.items():
            if hasattr(posting, key):
                setattr(posting, key, value)
        
        await self.db.flush()
        return posting


class ApplicationRepository:
    """Repository for application operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, application_data: dict) -> Application:
        """Create a new application"""
        application = Application(**application_data)
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application
    
    async def get_by_id(self, application_id: uuid.UUID) -> Optional[Application]:
        """Get application by ID"""
        result = await self.db.execute(
            select(Application).where(
                and_(Application.id == application_id, Application.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, job_posting_id: Optional[uuid.UUID] = None, status: Optional[str] = None) -> List[Application]:
        """Get all applications, optionally filtered"""
        query = select(Application).where(Application.is_deleted == False)
        
        if job_posting_id:
            query = query.where(Application.job_posting_id == job_posting_id)
        if status:
            query = query.where(Application.status == status)
        
        query = query.order_by(Application.applied_date.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, application_id: uuid.UUID, application_data: dict) -> Optional[Application]:
        """Update application"""
        application = await self.get_by_id(application_id)
        if not application:
            return None
        
        for key, value in application_data.items():
            if hasattr(application, key):
                setattr(application, key, value)
        
        await self.db.flush()
        return application


class InterviewRepository:
    """Repository for interview operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, interview_data: dict) -> Interview:
        """Create a new interview"""
        interview = Interview(**interview_data)
        self.db.add(interview)
        await self.db.flush()
        await self.db.refresh(interview)
        return interview
    
    async def get_by_id(self, interview_id: uuid.UUID) -> Optional[Interview]:
        """Get interview by ID"""
        result = await self.db.execute(
            select(Interview).where(
                and_(Interview.id == interview_id, Interview.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_application(self, application_id: uuid.UUID) -> List[Interview]:
        """Get all interviews for an application"""
        result = await self.db.execute(
            select(Interview).where(
                and_(
                    Interview.application_id == application_id,
                    Interview.is_deleted == False
                )
            ).order_by(Interview.scheduled_date)
        )
        return result.scalars().all()
    
    async def update(self, interview_id: uuid.UUID, interview_data: dict) -> Optional[Interview]:
        """Update interview"""
        interview = await self.get_by_id(interview_id)
        if not interview:
            return None
        
        for key, value in interview_data.items():
            if hasattr(interview, key):
                setattr(interview, key, value)
        
        await self.db.flush()
        return interview


class OfferLetterRepository:
    """Repository for offer letter operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, offer_data: dict) -> OfferLetter:
        """Create a new offer letter"""
        offer = OfferLetter(**offer_data)
        self.db.add(offer)
        await self.db.flush()
        await self.db.refresh(offer)
        return offer
    
    async def get_by_id(self, offer_id: uuid.UUID) -> Optional[OfferLetter]:
        """Get offer letter by ID"""
        result = await self.db.execute(
            select(OfferLetter).where(
                and_(OfferLetter.id == offer_id, OfferLetter.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_application(self, application_id: uuid.UUID) -> Optional[OfferLetter]:
        """Get offer letter for an application"""
        result = await self.db.execute(
            select(OfferLetter).where(
                and_(
                    OfferLetter.application_id == application_id,
                    OfferLetter.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, offer_id: uuid.UUID, offer_data: dict) -> Optional[OfferLetter]:
        """Update offer letter"""
        offer = await self.get_by_id(offer_id)
        if not offer:
            return None
        
        for key, value in offer_data.items():
            if hasattr(offer, key):
                setattr(offer, key, value)
        
        await self.db.flush()
        return offer
