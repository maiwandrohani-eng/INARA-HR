"""Performance Module - Services with 360-degree Reviews"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List
from datetime import date
from statistics import mean
import uuid

from modules.performance.models import (
    PerformanceReviewCycle, 
    PerformanceEvaluation, 
    ReviewerType,
    PerformanceGoal
)
from modules.performance.schemas import (
    PerformanceReviewCycleCreate,
    PerformanceReviewCycleResponse,
    PerformanceEvaluationSubmit,
    PerformanceEvaluationResponse,
    Review360Summary
)
from modules.employees.models import Employee
from modules.approvals.services import ApprovalService
from modules.approvals.schemas import ApprovalRequestCreate
from modules.approvals.models import ApprovalType
from core.exceptions import NotFoundException, BadRequestException

class PerformanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_service = ApprovalService(db)
    
    async def initiate_360_review(
        self,
        review_data: PerformanceReviewCycleCreate,
        initiator_id: uuid.UUID
    ) -> PerformanceReviewCycleResponse:
        """
        Initiate a 360-degree review cycle for an employee
        Automatically creates evaluation slots for supervisor, peers, and subordinates
        """
        # Get employee
        result = await self.db.execute(
            select(Employee).where(Employee.id == review_data.employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise NotFoundException("Employee not found")
        
        # Create review cycle
        review_cycle = PerformanceReviewCycle(
            employee_id=review_data.employee_id,
            review_period_start=review_data.review_period_start,
            review_period_end=review_data.review_period_end,
            review_type=review_data.review_type,
            status="in_progress"
        )
        
        self.db.add(review_cycle)
        await self.db.commit()
        await self.db.refresh(review_cycle)
        
        # Create evaluation slots
        
        # 1. Supervisor evaluation
        if employee.manager_id:
            supervisor_eval = PerformanceEvaluation(
                review_cycle_id=review_cycle.id,
                evaluator_id=employee.manager_id,
                evaluator_type=ReviewerType.SUPERVISOR,
                status="pending"
            )
            self.db.add(supervisor_eval)
        
        # 2. Self evaluation
        self_eval = PerformanceEvaluation(
            review_cycle_id=review_cycle.id,
            evaluator_id=review_data.employee_id,
            evaluator_type=ReviewerType.SELF,
            status="pending"
        )
        self.db.add(self_eval)
        
        # 3. Peer evaluations (if specified)
        if review_data.peer_ids:
            for peer_id in review_data.peer_ids:
                peer_eval = PerformanceEvaluation(
                    review_cycle_id=review_cycle.id,
                    evaluator_id=peer_id,
                    evaluator_type=ReviewerType.PEER,
                    status="pending"
                )
                self.db.add(peer_eval)
        
        # 4. Subordinate evaluations (get direct reports)
        subordinates_result = await self.db.execute(
            select(Employee).where(Employee.manager_id == review_data.employee_id)
        )
        subordinates = subordinates_result.scalars().all()
        
        # Optionally filter by specified subordinate_ids
        if review_data.subordinate_ids:
            subordinates = [s for s in subordinates if s.id in review_data.subordinate_ids]
        
        for subordinate in subordinates:
            sub_eval = PerformanceEvaluation(
                review_cycle_id=review_cycle.id,
                evaluator_id=subordinate.id,
                evaluator_type=ReviewerType.SUBORDINATE,
                status="pending"
            )
            self.db.add(sub_eval)
        
        await self.db.commit()
        
        return PerformanceReviewCycleResponse.model_validate(review_cycle)
    
    async def submit_evaluation(
        self,
        review_cycle_id: uuid.UUID,
        evaluator_id: uuid.UUID,
        evaluation_data: PerformanceEvaluationSubmit
    ) -> PerformanceEvaluationResponse:
        """
        Submit an evaluation for a 360-degree review
        """
        # Find the evaluation slot
        result = await self.db.execute(
            select(PerformanceEvaluation).where(
                and_(
                    PerformanceEvaluation.review_cycle_id == review_cycle_id,
                    PerformanceEvaluation.evaluator_id == evaluator_id
                )
            )
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            raise NotFoundException("Evaluation slot not found for this evaluator")
        
        if evaluation.status == "submitted":
            raise BadRequestException("Evaluation already submitted")
        
        # Update evaluation
        for key, value in evaluation_data.model_dump(exclude_unset=True).items():
            setattr(evaluation, key, value)
        
        evaluation.status = "submitted"
        evaluation.submitted_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(evaluation)
        
        # Check if all evaluations are submitted
        await self._check_review_completion(review_cycle_id)
        
        return PerformanceEvaluationResponse.model_validate(evaluation)
    
    async def get_360_review_summary(
        self,
        review_cycle_id: uuid.UUID
    ) -> Review360Summary:
        """
        Get comprehensive 360-degree review summary with all evaluations
        """
        # Get review cycle
        result = await self.db.execute(
            select(PerformanceReviewCycle).where(PerformanceReviewCycle.id == review_cycle_id)
        )
        review_cycle = result.scalar_one_or_none()
        
        if not review_cycle:
            raise NotFoundException("Review cycle not found")
        
        # Get employee
        result = await self.db.execute(
            select(Employee).where(Employee.id == review_cycle.employee_id)
        )
        employee = result.scalar_one_or_none()
        
        # Get all evaluations
        result = await self.db.execute(
            select(PerformanceEvaluation).where(
                PerformanceEvaluation.review_cycle_id == review_cycle_id
            )
        )
        evaluations = result.scalars().all()
        
        # Organize evaluations by type
        supervisor_eval = None
        peer_evals = []
        subordinate_evals = []
        self_eval = None
        
        for eval in evaluations:
            eval_response = PerformanceEvaluationResponse.model_validate(eval)
            if eval.evaluator_type == ReviewerType.SUPERVISOR:
                supervisor_eval = eval_response
            elif eval.evaluator_type == ReviewerType.PEER:
                peer_evals.append(eval_response)
            elif eval.evaluator_type == ReviewerType.SUBORDINATE:
                subordinate_evals.append(eval_response)
            elif eval.evaluator_type == ReviewerType.SELF:
                self_eval = eval_response
        
        # Calculate statistics
        total_evals = len(evaluations)
        completed_evals = sum(1 for e in evaluations if e.status == "submitted")
        pending_evals = total_evals - completed_evals
        
        # Calculate average ratings
        submitted_evals = [e for e in evaluations if e.status == "submitted" and e.rating is not None]
        average_rating = mean([e.rating for e in submitted_evals]) if submitted_evals else None
        
        supervisor_rating = supervisor_eval.rating if supervisor_eval and supervisor_eval.rating else None
        
        peer_ratings = [e.rating for e in peer_evals if e.rating is not None]
        peer_avg = mean(peer_ratings) if peer_ratings else None
        
        sub_ratings = [e.rating for e in subordinate_evals if e.rating is not None]
        sub_avg = mean(sub_ratings) if sub_ratings else None
        
        self_rating = self_eval.rating if self_eval and self_eval.rating else None
        
        return Review360Summary(
            review_cycle_id=review_cycle.id,
            employee_id=review_cycle.employee_id,
            employee_name=f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
            review_period=f"{review_cycle.review_period_start} to {review_cycle.review_period_end}",
            status=review_cycle.status,
            total_evaluations=total_evals,
            completed_evaluations=completed_evals,
            pending_evaluations=pending_evals,
            supervisor_evaluation=supervisor_eval,
            peer_evaluations=peer_evals,
            subordinate_evaluations=subordinate_evals,
            self_evaluation=self_eval,
            average_rating=average_rating,
            supervisor_rating=supervisor_rating,
            peer_average_rating=peer_avg,
            subordinate_average_rating=sub_avg,
            self_rating=self_rating,
            final_rating=review_cycle.final_rating,
            final_strengths=review_cycle.final_strengths,
            final_areas_for_improvement=review_cycle.final_areas_for_improvement,
            final_development_plan=review_cycle.final_development_plan
        )
    
    async def finalize_360_review(
        self,
        review_cycle_id: uuid.UUID,
        final_rating: int,
        final_strengths: str,
        final_areas_for_improvement: str,
        final_development_plan: str,
        hr_admin_id: uuid.UUID
    ) -> PerformanceReviewCycleResponse:
        """
        Finalize a 360-degree review with aggregated results
        Typically done by HR admin after reviewing all evaluations
        """
        result = await self.db.execute(
            select(PerformanceReviewCycle).where(PerformanceReviewCycle.id == review_cycle_id)
        )
        review_cycle = result.scalar_one_or_none()
        
        if not review_cycle:
            raise NotFoundException("Review cycle not found")
        
        review_cycle.final_rating = final_rating
        review_cycle.final_strengths = final_strengths
        review_cycle.final_areas_for_improvement = final_areas_for_improvement
        review_cycle.final_development_plan = final_development_plan
        review_cycle.status = "completed"
        
        await self.db.commit()
        await self.db.refresh(review_cycle)
        
        return PerformanceReviewCycleResponse.model_validate(review_cycle)
    
    async def acknowledge_review(
        self,
        review_cycle_id: uuid.UUID,
        employee_id: uuid.UUID,
        comments: Optional[str] = None
    ) -> PerformanceReviewCycleResponse:
        """
        Employee acknowledges their completed 360-degree review
        """
        result = await self.db.execute(
            select(PerformanceReviewCycle).where(PerformanceReviewCycle.id == review_cycle_id)
        )
        review_cycle = result.scalar_one_or_none()
        
        if not review_cycle:
            raise NotFoundException("Review cycle not found")
        
        if review_cycle.employee_id != employee_id:
            raise BadRequestException("Not authorized")
        
        if review_cycle.status != "completed":
            raise BadRequestException("Review must be completed before acknowledgment")
        
        review_cycle.status = "acknowledged"
        review_cycle.employee_comments = comments
        review_cycle.acknowledged_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(review_cycle)
        
        return PerformanceReviewCycleResponse.model_validate(review_cycle)
    
    async def get_my_pending_evaluations(
        self,
        evaluator_id: uuid.UUID
    ) -> List[dict]:
        """
        Get pending evaluations for a specific evaluator
        """
        result = await self.db.execute(
            select(PerformanceEvaluation, PerformanceReviewCycle, Employee).join(
                PerformanceReviewCycle,
                PerformanceEvaluation.review_cycle_id == PerformanceReviewCycle.id
            ).join(
                Employee,
                PerformanceReviewCycle.employee_id == Employee.id
            ).where(
                and_(
                    PerformanceEvaluation.evaluator_id == evaluator_id,
                    PerformanceEvaluation.status == "pending"
                )
            )
        )
        
        results = result.all()
        
        return [
            {
                "evaluation_id": str(eval.id),
                "review_cycle_id": str(cycle.id),
                "employee_id": str(employee.id),
                "employee_name": f"{employee.first_name} {employee.last_name}",
                "evaluator_type": eval.evaluator_type.value,
                "review_period": f"{cycle.review_period_start} to {cycle.review_period_end}",
                "review_type": cycle.review_type
            }
            for eval, cycle, employee in results
        ]
    
    async def _check_review_completion(self, review_cycle_id: uuid.UUID):
        """
        Check if all evaluations are submitted and auto-complete if needed
        """
        result = await self.db.execute(
            select(func.count(PerformanceEvaluation.id)).where(
                and_(
                    PerformanceEvaluation.review_cycle_id == review_cycle_id,
                    PerformanceEvaluation.status == "pending"
                )
            )
        )
        pending_count = result.scalar()
        
        if pending_count == 0:
            # All evaluations submitted, calculate aggregated rating
            result = await self.db.execute(
                select(PerformanceEvaluation).where(
                    and_(
                        PerformanceEvaluation.review_cycle_id == review_cycle_id,
                        PerformanceEvaluation.rating.isnot(None)
                    )
                )
            )
            evaluations = result.scalars().all()
            
            if evaluations:
                avg_rating = round(mean([e.rating for e in evaluations]))
                
                # Update review cycle
                result = await self.db.execute(
                    select(PerformanceReviewCycle).where(
                        PerformanceReviewCycle.id == review_cycle_id
                    )
                )
                review_cycle = result.scalar_one_or_none()
                
                if review_cycle:
                    review_cycle.final_rating = avg_rating
                    # Keep status as in_progress until HR finalizes
                    await self.db.commit()
