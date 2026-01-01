"""
Approval Workflow Module - Service Layer
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from modules.approvals.repositories import ApprovalRequestRepository, ApprovalDelegationRepository
from modules.approvals.schemas import (
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalRequestResponse,
    ApprovalDelegationCreate, ApprovalDelegationUpdate, ApprovalDelegationResponse,
    ApprovalStats
)
from modules.approvals.models import ApprovalStatus, ApprovalType
from core.exceptions import NotFoundException, BadRequestException


class ApprovalService:
    """Service for approval workflow operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_repo = ApprovalRequestRepository(db)
        self.delegation_repo = ApprovalDelegationRepository(db)
    
    async def create_approval_request(
        self,
        request_data: ApprovalRequestCreate,
        supervisor_id: uuid.UUID,
        country_code: str = None,
        approval_level: int = 1,
        previous_approval_id: uuid.UUID = None,
        is_final_approval: bool = False,
        next_approver_id: uuid.UUID = None
    ) -> ApprovalRequestResponse:
        """Create a new approval request"""
        from modules.employees.models import Employee
        from sqlalchemy import select
        
        # Get employee to retrieve country_code if not provided
        if not country_code:
            result = await self.db.execute(
                select(Employee).where(Employee.id == request_data.employee_id)
            )
            employee = result.scalar_one_or_none()
            country_code = employee.country_code if employee and employee.country_code else 'US'
        
        # Check if there's an active delegation
        delegate_id = await self.delegation_repo.get_active_delegate(supervisor_id)
        approver_id = delegate_id if delegate_id else supervisor_id
        
        approval = await self.approval_repo.create(
            request_data,
            approver_id,
            country_code=country_code,
            approval_level=approval_level,
            previous_approval_id=previous_approval_id,
            is_final_approval=is_final_approval,
            next_approver_id=next_approver_id
        )
        return ApprovalRequestResponse.model_validate(approval)
    
    async def get_approval_request(self, approval_id: uuid.UUID) -> ApprovalRequestResponse:
        """Get approval request by ID"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        return ApprovalRequestResponse.model_validate(approval)
    
    async def get_approval_by_request(
        self,
        request_type: ApprovalType,
        request_id: uuid.UUID
    ) -> Optional[ApprovalRequestResponse]:
        """Get approval request by related entity"""
        approval = await self.approval_repo.get_by_request(request_type, request_id)
        if approval:
            return ApprovalRequestResponse.model_validate(approval)
        return None
    
    async def get_pending_approvals(self, approver_id: uuid.UUID) -> List[dict]:
        """Get all pending approvals for an approver"""
        approvals = await self.approval_repo.get_pending_for_approver(approver_id)
        result = []
        for approval in approvals:
            approval_dict = ApprovalRequestResponse.model_validate(approval).model_dump()
            # Add employee name for frontend display
            if approval.employee:
                approval_dict["employee_name"] = f"{approval.employee.first_name} {approval.employee.last_name}"
            result.append(approval_dict)
        return result
    
    async def get_employee_requests(self, employee_id: uuid.UUID) -> List[ApprovalRequestResponse]:
        """Get all approval requests submitted by an employee"""
        approvals = await self.approval_repo.get_by_employee(employee_id)
        return [ApprovalRequestResponse.model_validate(a) for a in approvals]
    
    async def create_sequential_approval_chain(
        self,
        request_data: ApprovalRequestCreate,
        approver_ids: List[uuid.UUID],
        country_code: str = None
    ) -> List[ApprovalRequestResponse]:
        """
        Create a sequential approval chain (multiple approvers in order)
        Each approval must be approved before the next one is created
        """
        from modules.employees.models import Employee
        from sqlalchemy import select
        
        if not approver_ids:
            raise BadRequestException("At least one approver must be specified")
        
        # Get country_code if not provided
        if not country_code:
            result = await self.db.execute(
                select(Employee).where(Employee.id == request_data.employee_id)
            )
            employee = result.scalar_one_or_none()
            country_code = employee.country_code if employee and employee.country_code else 'US'
        
        approvals = []
        previous_approval_id = None
        
        for level, approver_id in enumerate(approver_ids, start=1):
            # Check for delegation
            delegate_id = await self.delegation_repo.get_active_delegate(approver_id)
            final_approver_id = delegate_id if delegate_id else approver_id
            
            # Create approval request with level and chain info
            is_final = (level == len(approver_ids))
            approval = await self.approval_repo.create(
                request_data,
                final_approver_id,
                country_code=country_code,
                approval_level=level,
                previous_approval_id=previous_approval_id,
                is_final_approval=is_final
            )
            
            approvals.append(ApprovalRequestResponse.model_validate(approval))
            previous_approval_id = approval.id
            
            # Only create the first approval now, others will be created when previous is approved
            if level == 1:
                break
        
        return approvals
    
    async def approve_request(
        self,
        approval_id: uuid.UUID,
        approver_id: uuid.UUID,
        comments: Optional[str] = None,
        is_hr_override: bool = False,
        auto_forward: bool = True
    ) -> ApprovalRequestResponse:
        """
        Approve a request and automatically forward to next approver if exists
        
        Returns:
            ApprovalRequestResponse with information about whether there's a next approval
        """
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        # Allow HR admin override (permission check should be done at route level)
        if not is_hr_override and approval.approver_id != approver_id:
            raise BadRequestException("You are not authorized to approve this request")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("This request has already been reviewed")
        
        # Update approval status
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.APPROVED, comments=comments)
        updated = await self.approval_repo.update(approval_id, update_data)
        
        # If not final approval and has next_approver_id, create next approval in chain
        if not updated.is_final_approval and updated.next_approver_id:
            # Create next approval in sequence
            next_approval = await self.approval_repo.create(
                ApprovalRequestCreate(
                    request_type=updated.request_type,
                    request_id=updated.request_id,
                    employee_id=updated.employee_id,
                    comments=comments or updated.comments
                ),
                updated.next_approver_id,
                country_code=updated.country_code,
                approval_level=updated.approval_level + 1,
                previous_approval_id=approval_id,
                is_final_approval=True  # Assume this is final (can be adjusted per workflow)
            )
            
            # Send notification to next approver
            from core.email import email_service
            from modules.employees.models import Employee
            from sqlalchemy import select
            
            next_approver_result = await self.db.execute(
                select(Employee).where(Employee.id == updated.next_approver_id)
            )
            next_approver = next_approver_result.scalar_one_or_none()
            
            if next_approver and next_approver.email:
                employee_result = await self.db.execute(
                    select(Employee).where(Employee.id == updated.employee_id)
                )
                employee = employee_result.scalar_one_or_none()
                employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Employee"
                
                await email_service.send_approval_request_notification(
                    to_email=next_approver.email,
                    employee_name=employee_name,
                    request_type=updated.request_type.value,
                    request_details={"Previous Approver": f"{updated.approver.first_name} {updated.approver.last_name}"}
                )
        elif updated.is_final_approval:
            # This is the final approval - notify employee
            employee_result = await self.db.execute(
                select(Employee).where(Employee.id == updated.employee_id)
            )
            employee = employee_result.scalar_one_or_none()
            if employee and employee.email:
                await email_service.send_approval_status_notification(
                    to_email=employee.email,
                    request_type=updated.request_type.value,
                    status="approved",
                    comments=comments
                )
        else:
            # Notify next approver (if exists)
            next_approval = await self.approval_repo.get_next_approval_in_chain(
                updated.request_type,
                updated.request_id,
                updated.approval_level
            )
            if next_approval and next_approval.approver:
                if next_approval.approver.email:
                    employee_result = await self.db.execute(
                        select(Employee).where(Employee.id == updated.employee_id)
                    )
                    employee = employee_result.scalar_one_or_none()
                    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Employee"
                    
                    await email_service.send_approval_request_notification(
                        to_email=next_approval.approver.email,
                        employee_name=employee_name,
                        request_type=updated.request_type.value,
                        request_details={"Previous Approver": f"{updated.approver.first_name} {updated.approver.last_name}"}
                    )
        
        return ApprovalRequestResponse.model_validate(updated)
    
    async def reject_request(
        self,
        approval_id: uuid.UUID,
        approver_id: uuid.UUID,
        comments: Optional[str] = None,
        is_hr_override: bool = False
    ) -> ApprovalRequestResponse:
        """Reject a request"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        # Allow HR admin override (permission check should be done at route level)
        if not is_hr_override and approval.approver_id != approver_id:
            raise BadRequestException("You are not authorized to reject this request")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("This request has already been reviewed")
        
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.REJECTED, comments=comments)
        updated = await self.approval_repo.update(approval_id, update_data)
        return ApprovalRequestResponse.model_validate(updated)
    
    async def cancel_request(self, approval_id: uuid.UUID, employee_id: uuid.UUID) -> ApprovalRequestResponse:
        """Cancel a pending request (by employee who submitted it)"""
        approval = await self.approval_repo.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request not found")
        
        if approval.employee_id != employee_id:
            raise BadRequestException("You can only cancel your own requests")
        
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("Only pending requests can be cancelled")
        
        update_data = ApprovalRequestUpdate(status=ApprovalStatus.CANCELLED)
        updated = await self.approval_repo.update(approval_id, update_data)
        return ApprovalRequestResponse.model_validate(updated)
    
    async def get_approval_stats(self, approver_id: uuid.UUID) -> ApprovalStats:
        """Get approval statistics for dashboard"""
        stats = await self.approval_repo.get_stats_for_approver(approver_id)
        return ApprovalStats(**stats)
    
    # Delegation methods
    async def create_delegation(self, delegation_data: ApprovalDelegationCreate) -> ApprovalDelegationResponse:
        """Create a new delegation"""
        if delegation_data.start_date >= delegation_data.end_date:
            raise BadRequestException("End date must be after start date")
        
        delegation = await self.delegation_repo.create(delegation_data)
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def get_delegation(self, delegation_id: uuid.UUID) -> ApprovalDelegationResponse:
        """Get delegation by ID"""
        delegation = await self.delegation_repo.get_by_id(delegation_id)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def get_supervisor_delegations(self, supervisor_id: uuid.UUID) -> List[ApprovalDelegationResponse]:
        """Get all delegations for a supervisor"""
        delegations = await self.delegation_repo.get_by_supervisor(supervisor_id)
        return [ApprovalDelegationResponse.model_validate(d) for d in delegations]
    
    async def update_delegation(
        self,
        delegation_id: uuid.UUID,
        update_data: ApprovalDelegationUpdate
    ) -> ApprovalDelegationResponse:
        """Update delegation"""
        delegation = await self.delegation_repo.update(delegation_id, update_data)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def deactivate_delegation(self, delegation_id: uuid.UUID) -> ApprovalDelegationResponse:
        """Deactivate a delegation"""
        delegation = await self.delegation_repo.deactivate(delegation_id)
        if not delegation:
            raise NotFoundException("Delegation not found")
        return ApprovalDelegationResponse.model_validate(delegation)
    
    async def _update_related_entity_status(self, approval):
        """
        Update the status of the related entity (leave request, grievance, etc.) when final approval is given
        """
        from modules.leave.models import LeaveRequest
        from modules.safeguarding.models import SafeguardingCase
        from modules.grievance.models import Grievance
        from modules.workforce.models import PositionRequisition
        from sqlalchemy import select
        from datetime import date
        
        if approval.request_type == ApprovalType.LEAVE:
            # Leave request status is updated in leave service
            pass
        elif approval.request_type == ApprovalType.SAFEGUARDING:
            # Update safeguarding case status
            result = await self.db.execute(
                select(SafeguardingCase).where(SafeguardingCase.id == approval.request_id)
            )
            case = result.scalar_one_or_none()
            if case:
                case.status = "resolved"
                case.investigation_status = "completed"
                case.resolution_date = date.today()
                await self.db.commit()
        elif approval.request_type == ApprovalType.GRIEVANCE:
            # Update grievance status
            result = await self.db.execute(
                select(Grievance).where(Grievance.id == approval.request_id)
            )
            grievance = result.scalar_one_or_none()
            if grievance:
                grievance.status = "resolved"
                grievance.resolution_date = date.today()
                await self.db.commit()
        elif approval.request_type == ApprovalType.WORKFORCE:
            # Update requisition status
            result = await self.db.execute(
                select(PositionRequisition).where(PositionRequisition.id == approval.request_id)
            )
            requisition = result.scalar_one_or_none()
            if requisition:
                requisition.status = "approved"
                requisition.approved_by = approval.approver_id
                requisition.approved_date = date.today()
                
                # Store PDF filename if generated
                # The PDF will be generated by _generate_workforce_approval_pdf
                
                await self.db.commit()
        elif approval.request_type == ApprovalType.RESIGNATION:
            # Resignation approval: check if both Supervisor and HR have approved
            from modules.employee_files.models import Resignation, ResignationStatus
            from core.email import email_service
            
            result = await self.db.execute(
                select(Resignation).where(Resignation.id == approval.request_id)
            )
            resignation = result.scalar_one_or_none()
            if resignation:
                # Check if both Supervisor and HR have approved
                all_approvals = await self.approval_repo.get_all_approvals_for_request(
                    ApprovalType.RESIGNATION, resignation.id
                )
                approved_count = sum(1 for a in all_approvals if a.status == ApprovalStatus.APPROVED)
                
                if approved_count >= 2:  # Both Supervisor and HR approved
                    resignation.status = ResignationStatus.ACCEPTED_BY_HR
                    
                    # Update HR approval details from the HR approval record
                    hr_approval = next((a for a in all_approvals if a.approver_id != resignation.supervisor_id), None)
                    if hr_approval and hr_approval.approver:
                        if hasattr(hr_approval.approver, 'user_id') and hr_approval.approver.user_id:
                            resignation.hr_accepted_by = hr_approval.approver.user_id
                    resignation.hr_accepted_at = datetime.utcnow()
                    
                    await self.db.commit()
                    
                    # Notify employee that resignation is approved and ready for exit interview
                    employee_result = await self.db.execute(
                        select(Employee).where(Employee.id == resignation.employee_id)
                    )
                    employee = employee_result.scalar_one_or_none()
                    if employee and employee.email:
                        await email_service.send_email(
                            to_email=employee.email,
                            subject="Resignation Approved - Ready for Exit Interview",
                            html_body=f"""
                            <p>Dear {employee.first_name},</p>
                            <p>Your resignation (Number: {resignation.resignation_number}) has been approved by both your supervisor and HR.</p>
                            <p><strong>Intended Last Working Day:</strong> {resignation.intended_last_working_day.strftime('%B %d, %Y')}</p>
                            <p>Your resignation is now ready for the exit interview process. Please coordinate with HR to schedule your exit interview.</p>
                            <p>You can view the status of your resignation in your Personnel File.</p>
                            """
                        )
    
    async def _generate_workforce_approval_pdf(self, approval):
        """Generate PDF approval document for workforce requisition"""
        from modules.workforce.models import PositionRequisition
        from modules.employees.models import Employee
        from sqlalchemy import select
        from core.pdf_generator import generate_workforce_approval_pdf
        
        # Get requisition
        result = await self.db.execute(
            select(PositionRequisition).where(PositionRequisition.id == approval.request_id)
        )
        requisition = result.scalar_one_or_none()
        
        if not requisition:
            return
        
        # Get employee and approver
        employee_result = await self.db.execute(
            select(Employee).where(Employee.id == approval.employee_id)
        )
        employee = employee_result.scalar_one_or_none()
        
        approver_result = await self.db.execute(
            select(Employee).where(Employee.id == approval.approver_id)
        )
        approver = approver_result.scalar_one_or_none()
        
        if employee and approver:
            # Generate PDF (this will be implemented in pdf_generator)
            # For now, just log that it should be generated
            # The PDF can be stored and made available for download
            pass
