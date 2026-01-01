"""
Performance Management Module - API Routes
360-degree performance review system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db, get_current_user, get_current_active_user, require_admin
from core.exceptions import NotFoundException, BadRequestException
from core.pdf_generator import create_performance_appraisal_pdf
from modules.auth.models import User
from modules.performance.services import PerformanceService
from datetime import datetime
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
async def create_goal(
    goal_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create performance goal"""
    from modules.performance.models import PerformanceGoal
    from modules.employees.repositories import EmployeeRepository
    from datetime import datetime
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    new_goal = PerformanceGoal(
        employee_id=employee.id,
        title=goal_data['title'],
        description=goal_data['description'],
        category=goal_data.get('category', 'Individual'),
        start_date=datetime.fromisoformat(goal_data['start_date']).date(),
        target_date=datetime.fromisoformat(goal_data['target_date']).date(),
        status='in_progress',
        progress_percentage=0,
        notes=goal_data.get('notes')
    )
    
    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)
    
    return {
        "id": str(new_goal.id),
        "title": new_goal.title,
        "status": new_goal.status,
        "message": "Goal created successfully"
    }


@router.get("/goals")
async def list_goals(
    employee_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List performance goals"""
    from modules.performance.models import PerformanceGoal
    from sqlalchemy import select
    
    query = select(PerformanceGoal).where(PerformanceGoal.is_deleted == False)
    
    if employee_id:
        query = query.where(PerformanceGoal.employee_id == uuid.UUID(employee_id))
    else:
        # Get current user's employee record
        from modules.employees.repositories import EmployeeRepository
        employee_repo = EmployeeRepository(db)
        employee = await employee_repo.get_by_user_id(current_user["id"])
        if employee:
            query = query.where(PerformanceGoal.employee_id == employee.id)
    
    result = await db.execute(query.order_by(PerformanceGoal.created_at.desc()))
    goals = result.scalars().all()
    
    return [{
        "id": str(g.id),
        "title": g.title,
        "description": g.description,
        "category": g.category,
        "start_date": str(g.start_date),
        "target_date": str(g.target_date),
        "status": g.status,
        "progress_percentage": g.progress_percentage
    } for g in goals]


@router.post("/reviews")
async def create_review(
    review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create performance review"""
    from modules.performance.models import PerformanceReviewCycle
    from modules.employees.models import Employee
    from sqlalchemy import select
    from datetime import datetime
    
    try:
        # Get employee record for current user
        result = await db.execute(
            select(Employee).where(Employee.user_id == current_user['id'])
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(status_code=403, detail="No employee record found")
        
        # Create performance review
        new_review = PerformanceReviewCycle(
            employee_id=uuid.UUID(review_data.get('employee_id', str(employee.id))),
            review_period_start=datetime.fromisoformat(review_data.get('appraisal_start_date', review_data.get('review_period_start'))).date(),
            review_period_end=datetime.fromisoformat(review_data.get('appraisal_end_date', review_data.get('review_period_end'))).date(),
            review_type=review_data.get('review_type', 'annual'),
            status='in_progress',
            created_by=employee.id
        )
        
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)
        
        return {
            "id": str(new_review.id),
            "status": new_review.status,
            "message": "Performance review created successfully"
        }
    except Exception as e:
        print(f"Error creating performance review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews")
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List performance reviews"""
    from modules.performance.models import PerformanceReviewCycle
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    query = select(PerformanceReviewCycle).options(
        selectinload(PerformanceReviewCycle.employee)
    ).where(PerformanceReviewCycle.is_deleted == False).order_by(PerformanceReviewCycle.created_at.desc())
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return {
        "reviews": [{
            "id": str(r.id),
            "employee_name": f"{r.employee.first_name} {r.employee.last_name}" if r.employee else "Unknown",
            "employee": {
                "first_name": r.employee.first_name if r.employee else "",
                "last_name": r.employee.last_name if r.employee else ""
            },
            "review_period_start": str(r.review_period_start) if r.review_period_start else None,
            "review_period_end": str(r.review_period_end) if r.review_period_end else None,
            "review_type": r.review_type,
            "status": r.status,
            "overall_rating": float(r.final_rating) if r.final_rating else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in reviews]
    }


@router.post("/pips")
async def create_pip(
    pip_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create Performance Improvement Plan"""
    from modules.performance.models import PerformanceImprovementPlan
    from modules.employees.repositories import EmployeeRepository
    from datetime import datetime
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee or not employee.manager_id:
        raise HTTPException(status_code=400, detail="Employee or manager not found")
    
    new_pip = PerformanceImprovementPlan(
        employee_id=uuid.UUID(pip_data['employee_id']) if 'employee_id' in pip_data else employee.id,
        manager_id=employee.manager_id,
        start_date=datetime.fromisoformat(pip_data['start_date']).date(),
        end_date=datetime.fromisoformat(pip_data['end_date']).date(),
        concerns=pip_data['concerns'],
        expected_improvements=pip_data['expected_improvements'],
        support_provided=pip_data.get('support_provided'),
        status='active'
    )
    
    db.add(new_pip)
    await db.commit()
    await db.refresh(new_pip)
    
    return {
        "id": str(new_pip.id),
        "status": new_pip.status,
        "message": "PIP created successfully"
    }


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


@router.delete("/reviews/360/{review_cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_performance_review(
    review_cycle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete performance review cycle (Admin only - soft delete)"""
    from modules.performance.models import PerformanceReviewCycle
    
    result = await db.execute(
        select(PerformanceReviewCycle).where(
            PerformanceReviewCycle.id == review_cycle_id,
            PerformanceReviewCycle.is_deleted == False
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise NotFoundException(resource="Performance review")
    
    # Soft delete
    review.is_deleted = True
    review.deleted_at = datetime.utcnow()
    
    await db.commit()
    return None
