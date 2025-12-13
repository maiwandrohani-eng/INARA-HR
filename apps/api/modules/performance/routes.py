"""
Performance Management Module - API Routes
360-degree performance review system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, get_current_user
from core.exceptions import NotFoundException, BadRequestException
from core.pdf_generator import create_performance_appraisal_pdf
from modules.auth.models import User
from modules.performance.services import PerformanceService
from modules.performance.schemas import (
    PerformanceReviewCycleCreate,
    PerformanceReviewCycleResponse,
    PerformanceEvaluationSubmit,
    PerformanceEvaluationResponse,
    Review360Summary
)

router = APIRouter()


# 360-Degree Review Endpoints
@router.post("/reviews/360", response_model=PerformanceReviewCycleResponse, status_code=status.HTTP_201_CREATED)
async def initiate_360_review(
    review_data: PerformanceReviewCycleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a 360-degree review cycle for an employee
    Creates evaluation slots for supervisor, peers, and subordinates
    """
    service = PerformanceService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    
    try:
        return await service.initiate_360_review(review_data, current_user.employee.id)
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reviews/360/{review_cycle_id}", response_model=Review360Summary)
async def get_360_review_summary(
    review_cycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive 360-degree review summary with all evaluations"""
    service = PerformanceService(db)
    try:
        return await service.get_360_review_summary(review_cycle_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/reviews/360/{review_cycle_id}/evaluate", response_model=PerformanceEvaluationResponse)
async def submit_evaluation(
    review_cycle_id: uuid.UUID,
    evaluation_data: PerformanceEvaluationSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an evaluation for a 360-degree review
    Can be submitted by supervisor, peer, subordinate, or self
    """
    service = PerformanceService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    
    try:
        return await service.submit_evaluation(
            review_cycle_id,
            current_user.employee.id,
            evaluation_data
        )
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reviews/my-pending-evaluations")
async def get_my_pending_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get pending evaluations assigned to current user
    Shows all 360-reviews where user needs to provide evaluation
    """
    service = PerformanceService(db)
    if not current_user.employee:
        return []
    
    return await service.get_my_pending_evaluations(current_user.employee.id)


@router.post("/reviews/360/{review_cycle_id}/finalize", response_model=PerformanceReviewCycleResponse)
async def finalize_360_review(
    review_cycle_id: uuid.UUID,
    final_rating: int,
    final_strengths: str,
    final_areas_for_improvement: str,
    final_development_plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Finalize a 360-degree review with aggregated results
    Only HR admin or senior management should call this
    """
    service = PerformanceService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    
    try:
        return await service.finalize_360_review(
            review_cycle_id,
            final_rating,
            final_strengths,
            final_areas_for_improvement,
            final_development_plan,
            current_user.employee.id
        )
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reviews/360/{review_cycle_id}/acknowledge", response_model=PerformanceReviewCycleResponse)
async def acknowledge_review(
    review_cycle_id: uuid.UUID,
    comments: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Employee acknowledges their completed 360-degree review"""
    service = PerformanceService(db)
    if not current_user.employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record found")
    
    try:
        return await service.acknowledge_review(
            review_cycle_id,
            current_user.employee.id,
            comments
        )
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Legacy endpoints for backwards compatibility
@router.post("/goals")
async def create_goal(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Create performance goal"""
    return {"message": "Create goal - TODO"}


@router.get("/goals")
async def list_goals(db = Depends(get_db), current_user = Depends(get_current_user)):
    """List performance goals"""
    return {"message": "List goals - TODO"}


@router.post("/reviews")
async def create_review(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Create performance review (legacy - use /reviews/360 instead)"""
    return {"message": "Use /reviews/360 endpoint for 360-degree reviews"}


@router.get("/reviews")
async def list_reviews(db = Depends(get_db), current_user = Depends(get_current_user)):
    """List performance reviews"""
    return {"message": "List reviews - TODO"}


@router.post("/pips")
async def create_pip(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Create Performance Improvement Plan"""
    return {"message": "Create PIP - TODO"}


@router.get("/reviews/360/{review_cycle_id}/export")
async def export_360_review_pdf(
    review_cycle_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export 360-degree review as PDF"""
    # TODO: Fetch actual review from database
    appraisal = {
        "id": review_cycle_id,
        "employee": {
            "first_name": current_user.first_name if hasattr(current_user, 'first_name') else "",
            "last_name": current_user.last_name if hasattr(current_user, 'last_name') else "",
            "position": {"title": "Program Manager"}
        },
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
        "reviewer": {"first_name": "Manager", "last_name": "Name"},
        "overall_rating": 4.5,
        "status": "completed",
        "appraisal_date": "2025-01-15",
        "ratings": [
            {"category": "Communication", "score": 5, "comments": "Excellent communication skills"},
            {"category": "Teamwork", "score": 4, "comments": "Works well with team"},
            {"category": "Technical Skills", "score": 4, "comments": "Strong technical abilities"},
            {"category": "Leadership", "score": 5, "comments": "Outstanding leadership"},
        ],
        "comments": "Outstanding performance throughout the year. Exceeded expectations in all areas.",
        "development_goals": "Focus on strategic planning and mentoring junior staff."
    }
    
    pdf_buffer = create_performance_appraisal_pdf(appraisal)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=performance_review_{review_cycle_id}.pdf"
        }
    )
