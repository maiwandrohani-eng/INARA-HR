"""Recruitment Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.recruitment.services import RecruitmentService
from modules.recruitment.schemas import (
    JobPostingCreate, ApplicationCreate, InterviewSchedule,
    InterviewFeedback, OfferLetterCreate
)
import uuid

router = APIRouter()


@router.get("/")
async def list_job_postings(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all job postings"""
    recruitment_service = RecruitmentService(db)
    postings = await recruitment_service.get_job_postings(status=status)
    return postings


@router.post("/postings", status_code=201)
async def create_job_posting(
    posting_data: JobPostingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new job posting"""
    recruitment_service = RecruitmentService(db)
    posting = await recruitment_service.create_job_posting(
        posting_data,
        uuid.UUID(current_user["id"])
    )
    return posting


@router.post("/postings/{posting_id}/publish")
async def publish_job_posting(
    posting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Publish a job posting"""
    try:
        posting_uuid = uuid.UUID(posting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid posting ID format")
    
    recruitment_service = RecruitmentService(db)
    posting = await recruitment_service.publish_job_posting(posting_uuid)
    return posting


@router.post("/applications")
async def submit_application(
    application_data: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit job application (public endpoint)"""
    recruitment_service = RecruitmentService(db)
    application = await recruitment_service.submit_application(application_data)
    return application


@router.get("/applications")
async def list_applications(
    job_posting_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all applications"""
    recruitment_service = RecruitmentService(db)
    
    posting_uuid = None
    if job_posting_id:
        try:
            posting_uuid = uuid.UUID(job_posting_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid job posting ID format")
    
    applications = await recruitment_service.get_applications(
        job_posting_id=posting_uuid,
        status=status
    )
    return applications


@router.patch("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update application status"""
    try:
        application_uuid = uuid.UUID(application_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    recruitment_service = RecruitmentService(db)
    application = await recruitment_service.update_application_status(
        application_uuid,
        status
    )
    return application


@router.post("/interviews")
async def schedule_interview(
    interview_data: InterviewSchedule,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Schedule interview"""
    recruitment_service = RecruitmentService(db)
    interview = await recruitment_service.schedule_interview(
        interview_data,
        interview_data.interviewer_ids,
        uuid.UUID(current_user["id"])
    )
    return interview


@router.get("/applications/{application_id}/interviews")
async def get_application_interviews(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get interviews for an application"""
    try:
        application_uuid = uuid.UUID(application_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    recruitment_service = RecruitmentService(db)
    interviews = await recruitment_service.get_interviews_for_application(application_uuid)
    return interviews


@router.post("/interviews/{interview_id}/feedback")
async def submit_interview_feedback(
    interview_id: str,
    feedback_data: InterviewFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Submit interview feedback"""
    try:
        interview_uuid = uuid.UUID(interview_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid interview ID format")
    
    recruitment_service = RecruitmentService(db)
    interview = await recruitment_service.update_interview_feedback(
        interview_uuid,
        feedback_data.feedback,
        feedback_data.rating
    )
    return interview


@router.post("/offers")
async def create_offer_letter(
    offer_data: OfferLetterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create offer letter"""
    recruitment_service = RecruitmentService(db)
    offer = await recruitment_service.create_offer_letter(
        offer_data,
        uuid.UUID(current_user["id"])
    )
    return offer


@router.post("/offers/{offer_id}/send")
async def send_offer_letter(
    offer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Send offer letter to candidate"""
    try:
        offer_uuid = uuid.UUID(offer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid offer ID format")
    
    recruitment_service = RecruitmentService(db)
    offer = await recruitment_service.send_offer_letter(offer_uuid)
    return offer
