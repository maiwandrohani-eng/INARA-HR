"""
Payroll Module - Business Logic
Service layer for payroll processing and approvals
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import uuid

from modules.payroll.models import Payroll, PayrollEntry, PayrollApproval, PayrollStatus
from modules.payroll.schemas import (
    PayrollCreate, PayrollUpdate, PayrollEntryCreate,
    EmployeePayrollSummary
)
from modules.employees.models import Employee, EmploymentStatus
from modules.employee_files.models import EmploymentContract, ContractStatus
from core.exceptions import NotFoundException, BadRequestException


class PayrollService:
    """Service for payroll management"""
    
    @staticmethod
    async def get_active_employees_for_payroll(
        session: AsyncSession,
        user_id: str
    ) -> List[EmployeePayrollSummary]:
        """Get all active employees with their contract salary for payroll processing"""
        
        # Query active employees with their active contracts
        query = (
            select(Employee)
            .outerjoin(EmploymentContract, and_(
                EmploymentContract.employee_id == Employee.id,
                EmploymentContract.status == ContractStatus.ACTIVE,
                EmploymentContract.is_deleted == False
            ))
            .where(
                Employee.status == EmploymentStatus.ACTIVE,
                Employee.is_deleted == False
            )
            .options(selectinload(Employee.position))
            .options(selectinload(Employee.department))
        )
        
        result = await session.execute(query)
        employees = result.scalars().unique().all()
        
        summaries = []
        for employee in employees:
            # Get active contract for this employee
            contract_query = (
                select(EmploymentContract)
                .where(
                    EmploymentContract.employee_id == employee.id,
                    EmploymentContract.status == ContractStatus.ACTIVE,
                    EmploymentContract.is_deleted == False
                )
                .order_by(EmploymentContract.start_date.desc())
                .limit(1)
            )
            contract_result = await session.execute(contract_query)
            contract = contract_result.scalar_one_or_none()
            
            summaries.append(EmployeePayrollSummary(
                employee_id=str(employee.id),
                employee_number=employee.employee_number or "",
                first_name=employee.first_name,
                last_name=employee.last_name,
                position=employee.position.title if employee.position else None,
                department=employee.department.name if employee.department else None,
                basic_salary=contract.monthly_salary if contract else Decimal('0'),
                has_active_contract=contract is not None,
                contract_monthly_salary=contract.monthly_salary if contract else None
            ))
        
        return summaries
    
    @staticmethod
    async def check_payroll_exists(
        session: AsyncSession,
        month: int,
        year: int,
        country_code: str = None
    ) -> bool:
        """Check if payroll already exists for the given month/year (tenant-aware)"""
        query = select(Payroll).where(
            Payroll.month == month,
            Payroll.year == year,
            Payroll.is_deleted == False
        )
        
        # Add tenant filtering if country_code provided
        if country_code:
            query = query.where(Payroll.country_code == country_code)
        
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def create_payroll(
        session: AsyncSession,
        payroll_data: PayrollCreate,
        user_id: str
    ) -> Payroll:
        """Create a new payroll batch"""
        
        # Get user's country_code for tenant filtering
        from modules.auth.models import User
        user_query = select(User).where(User.id == uuid.UUID(user_id))
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        user_country = user.country_code if user else None
        
        # Check if payroll already exists for this month in this tenant
        exists = await PayrollService.check_payroll_exists(
            session, payroll_data.month, payroll_data.year, user_country
        )
        if exists:
            raise BadRequestException(
                f"Payroll for {payroll_data.year}-{payroll_data.month:02d} already exists"
            )
        
        # Calculate totals
        total_basic = sum(entry.basic_salary for entry in payroll_data.entries)
        total_allowances = sum(entry.allowances for entry in payroll_data.entries)
        total_deductions = sum(entry.deductions for entry in payroll_data.entries)
        total_gross = total_basic + total_allowances
        total_net = total_gross - total_deductions
        
        # Create payroll
        payroll = Payroll(
            id=uuid.uuid4(),
            month=payroll_data.month,
            year=payroll_data.year,
            payment_date=payroll_data.payment_date,
            total_basic_salary=total_basic,
            total_allowances=total_allowances,
            total_gross_salary=total_gross,
            total_deductions=total_deductions,
            total_net_salary=total_net,
            status=PayrollStatus.DRAFT,
            country_code=user_country,
            created_by_id=uuid.UUID(user_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(payroll)
        await session.flush()
        
        # Create entries
        for entry_data in payroll_data.entries:
            gross_salary = entry_data.basic_salary + entry_data.allowances
            net_salary = gross_salary - entry_data.deductions
            
            entry = PayrollEntry(
                id=uuid.uuid4(),
                payroll_id=payroll.id,
                employee_id=uuid.UUID(entry_data.employee_id),
                employee_number=entry_data.employee_number,
                first_name=entry_data.first_name,
                last_name=entry_data.last_name,
                position=entry_data.position,
                department=entry_data.department,
                basic_salary=entry_data.basic_salary,
                allowances=entry_data.allowances,
                gross_salary=gross_salary,
                deductions=entry_data.deductions,
                net_salary=net_salary,
                currency=entry_data.currency,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(entry)
        
        await session.commit()
        
        # Reload with relationships
        query = (
            select(Payroll)
            .options(selectinload(Payroll.entries))
            .options(selectinload(Payroll.approvals))
            .where(Payroll.id == payroll.id)
        )
        result = await session.execute(query)
        payroll = result.scalar_one()
        
        return payroll
    
    @staticmethod
    async def get_payroll(
        session: AsyncSession,
        payroll_id: str,
        country_code: Optional[str] = None
    ) -> Payroll:
        """Get payroll by ID with entries and approvals (tenant-aware)"""
        query = (
            select(Payroll)
            .options(selectinload(Payroll.entries))
            .options(selectinload(Payroll.approvals))
            .where(
                Payroll.id == uuid.UUID(payroll_id),
                Payroll.is_deleted == False
            )
        )
        
        # Add tenant filtering if country_code provided
        if country_code:
            query = query.where(Payroll.country_code == country_code)
        result = await session.execute(query)
        payroll = result.scalar_one_or_none()
        
        if not payroll:
            raise NotFoundException(f"Payroll {payroll_id} not found")
        
        return payroll
    
    @staticmethod
    async def list_payrolls(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        year: Optional[int] = None,
        country_code: Optional[str] = None
    ) -> tuple[List[Payroll], int]:
        """List payrolls with pagination and filters (tenant-aware)"""
        
        # Build query
        query = select(Payroll).where(Payroll.is_deleted == False)
        
        # Add tenant filtering
        if country_code:
            query = query.where(Payroll.country_code == country_code)
        
        if status:
            query = query.where(Payroll.status == status)
        if year:
            query = query.where(Payroll.year == year)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)
        
        # Apply pagination
        query = (
            query
            .options(selectinload(Payroll.entries))
            .options(selectinload(Payroll.approvals))
            .order_by(Payroll.year.desc(), Payroll.month.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await session.execute(query)
        payrolls = result.scalars().all()
        
        return payrolls, total
    
    @staticmethod
    async def update_payroll(
        session: AsyncSession,
        payroll_id: str,
        payroll_data: PayrollUpdate,
        user_id: str
    ) -> Payroll:
        """Update payroll (only in DRAFT status)"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.DRAFT:
            raise BadRequestException("Can only update payroll in DRAFT status")
        
        # Update payment date if provided
        if payroll_data.payment_date:
            payroll.payment_date = payroll_data.payment_date
        
        # Update entries if provided
        if payroll_data.entries:
            # Delete existing entries
            for entry in payroll.entries:
                await session.delete(entry)
            
            # Recalculate totals
            total_basic = sum(e.basic_salary for e in payroll_data.entries)
            total_allowances = sum(e.allowances for e in payroll_data.entries)
            total_deductions = sum(e.deductions for e in payroll_data.entries)
            total_gross = total_basic + total_allowances
            total_net = total_gross - total_deductions
            
            payroll.total_basic_salary = total_basic
            payroll.total_allowances = total_allowances
            payroll.total_gross_salary = total_gross
            payroll.total_deductions = total_deductions
            payroll.total_net_salary = total_net
            
            # Create new entries
            for entry_data in payroll_data.entries:
                gross_salary = entry_data.basic_salary + entry_data.allowances
                net_salary = gross_salary - entry_data.deductions
                
                entry = PayrollEntry(
                    id=uuid.uuid4(),
                    payroll_id=payroll.id,
                    employee_id=uuid.UUID(entry_data.employee_id),
                    employee_number=entry_data.employee_number,
                    first_name=entry_data.first_name,
                    last_name=entry_data.last_name,
                    position=entry_data.position,
                    department=entry_data.department,
                    basic_salary=entry_data.basic_salary,
                    allowances=entry_data.allowances,
                    gross_salary=gross_salary,
                    deductions=entry_data.deductions,
                    net_salary=net_salary,
                    currency=entry_data.currency,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(entry)
        
        payroll.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def submit_to_finance(
        session: AsyncSession,
        payroll_id: str,
        user_id: str
    ) -> Payroll:
        """
        Submit payroll to Finance Manager for review
        Creates approval chain: Finance Manager → CEO
        """
        from core.role_helpers import get_finance_manager, get_ceo
        from modules.approvals.services import ApprovalService
        from modules.approvals.schemas import ApprovalRequestCreate
        from modules.approvals.models import ApprovalType
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        from sqlalchemy import select
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.DRAFT:
            raise BadRequestException("Can only submit payroll in DRAFT status")
        
        if not payroll.entries:
            raise BadRequestException("Cannot submit empty payroll")
        
        # Get HR Manager employee (who created this)
        hr_employee_result = await session.execute(
            select(Employee).where(Employee.user_id == uuid.UUID(user_id))
        )
        hr_employee = hr_employee_result.scalar_one_or_none()
        if not hr_employee:
            raise BadRequestException("HR Manager employee record not found")
        
        country_code = payroll.country_code or hr_employee.country_code or 'US'
        
        # Find Finance Manager and CEO
        finance_manager = await get_finance_manager(session, country_code)
        ceo = await get_ceo(session, country_code)
        
        if not finance_manager:
            raise BadRequestException("Finance Manager not found. Cannot create approval chain.")
        if not ceo:
            raise BadRequestException("CEO (Admin) not found. Cannot create approval chain.")
        
        # Update status
        payroll.status = PayrollStatus.PENDING_FINANCE
        payroll.updated_at = datetime.utcnow()
        await session.commit()
        
        # Create approval chain: Finance Manager → CEO
        approval_service = ApprovalService(session)
        
        # First approval: Finance Manager
        approval_data = ApprovalRequestCreate(
            request_type=ApprovalType.PAYROLL,
            request_id=payroll.id,
            employee_id=hr_employee.id,  # HR Manager who initiated
            comments=f"Payroll for {payroll.year}-{payroll.month:02d}"
        )
        
        finance_approval = await approval_service.create_approval_request(
            approval_data,
            finance_manager.id,
            country_code=country_code,
            approval_level=1,
            is_final_approval=False
        )
        
        # Second approval: CEO
        ceo_approval = await approval_service.create_approval_request(
            approval_data,
            ceo.id,
            country_code=country_code,
            approval_level=2,
            previous_approval_id=finance_approval.id,
            is_final_approval=True
        )
        
        # Send notification to Finance Manager
        from core.email import email_service
        if finance_manager.email:
            await email_service.send_approval_request_notification(
                to_email=finance_manager.email,
                employee_name=f"{hr_employee.first_name} {hr_employee.last_name}",
                request_type="payroll",
                request_details={
                    "Period": f"{payroll.year}-{payroll.month:02d}",
                    "Total Net Salary": str(payroll.total_net_salary),
                    "Total Employees": str(len(payroll.entries))
                }
            )
        
        await session.refresh(payroll)
        return payroll
    
    @staticmethod
    async def finance_approve(
        session: AsyncSession,
        payroll_id: str,
        user_id: str,
        approved: bool,
        comments: Optional[str] = None,
        approval_id: Optional[uuid.UUID] = None
    ) -> Payroll:
        """
        Finance Manager approves or rejects payroll
        If approved, automatically forwards to CEO
        """
        from modules.approvals.services import ApprovalService
        from modules.approvals.models import ApprovalType, ApprovalStatus
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        from sqlalchemy import select
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.PENDING_FINANCE:
            raise BadRequestException("Payroll is not pending Finance approval")
        
        # Get employee for user
        employee_repo = EmployeeRepository(session)
        finance_employee = await employee_repo.get_by_user_id(user_id)
        if not finance_employee:
            raise BadRequestException("Finance Manager employee record not found")
        
        # Get approval request
        approval_service = ApprovalService(session)
        if not approval_id:
            approval = await approval_service.get_approval_by_request(ApprovalType.PAYROLL, payroll.id)
            if not approval:
                raise BadRequestException("Approval request not found for this payroll")
            approval_id = approval.id
        else:
            approval = await approval_service.get_approval_request(approval_id)
        
        # Approve or reject through approval system
        if approved:
            await approval_service.approve_request(approval_id, finance_employee.id, comments)
            payroll.status = PayrollStatus.PENDING_CEO
            payroll.finance_reviewed_at = datetime.utcnow()
            payroll.finance_reviewed_by_id = uuid.UUID(user_id)
        else:
            await approval_service.reject_request(approval_id, finance_employee.id, comments)
            payroll.status = PayrollStatus.REJECTED
            
            # Notify HR Manager
            from core.email import email_service
            hr_result = await session.execute(
                select(Employee).where(Employee.user_id == payroll.created_by_id)
            )
            hr_employee = hr_result.scalar_one_or_none()
            if hr_employee and hr_employee.email:
                await email_service.send_approval_status_notification(
                    to_email=hr_employee.email,
                    request_type="payroll",
                    status="rejected",
                    comments=comments
                )
        
        payroll.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def ceo_approve(
        session: AsyncSession,
        payroll_id: str,
        user_id: str,
        approved: bool,
        comments: Optional[str] = None,
        approval_id: Optional[uuid.UUID] = None
    ) -> Payroll:
        """
        CEO approves or rejects payroll
        If approved, status changes to APPROVED and goes back to Finance/HR for processing
        """
        from modules.approvals.services import ApprovalService
        from modules.approvals.models import ApprovalType
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        from sqlalchemy import select
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.PENDING_CEO:
            raise BadRequestException("Payroll is not pending CEO approval")
        
        # Get employee for user
        employee_repo = EmployeeRepository(session)
        ceo_employee = await employee_repo.get_by_user_id(user_id)
        if not ceo_employee:
            raise BadRequestException("CEO employee record not found")
        
        # Get approval request (should be the final one - level 2)
        approval_service = ApprovalService(session)
        if not approval_id:
            approval = await approval_service.get_approval_by_request(ApprovalType.PAYROLL, payroll.id)
            if not approval:
                raise BadRequestException("Approval request not found for this payroll")
            # Get the final approval (level 2 - CEO)
            all_approvals = await approval_service.approval_repo.get_all_approvals_for_request(
                ApprovalType.PAYROLL, payroll.id
            )
            ceo_approval = next((a for a in all_approvals if a.approval_level == 2), None)
            if not ceo_approval:
                raise BadRequestException("CEO approval request not found")
            approval_id = ceo_approval.id
        else:
            ceo_approval = await approval_service.get_approval_request(approval_id)
        
        # Approve or reject through approval system
        if approved:
            await approval_service.approve_request(approval_id, ceo_employee.id, comments)
            payroll.status = PayrollStatus.APPROVED
            payroll.ceo_approved_at = datetime.utcnow()
            payroll.ceo_approved_by_id = uuid.UUID(user_id)
            
            # Notify Finance Manager and HR Manager that it's approved and ready for processing
            from core.email import email_service
            from core.role_helpers import get_finance_manager, get_hr_manager
            
            finance_manager = await get_finance_manager(session, payroll.country_code)
            hr_manager = await get_hr_manager(session, payroll.country_code)
            
            for manager in [finance_manager, hr_manager]:
                if manager and manager.email:
                    await email_service.send_approval_status_notification(
                        to_email=manager.email,
                        request_type="payroll",
                        status="approved",
                        comments=f"Payroll approved by CEO. Ready for processing."
                    )
        else:
            await approval_service.reject_request(approval_id, ceo_employee.id, comments)
            payroll.status = PayrollStatus.REJECTED
            
            # Notify HR Manager and Finance Manager
            from core.email import email_service
            hr_result = await session.execute(
                select(Employee).where(Employee.user_id == payroll.created_by_id)
            )
            hr_employee = hr_result.scalar_one_or_none()
            if hr_employee and hr_employee.email:
                await email_service.send_approval_status_notification(
                    to_email=hr_employee.email,
                    request_type="payroll",
                    status="rejected",
                    comments=comments
                )
        
        payroll.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def mark_processed(
        session: AsyncSession,
        payroll_id: str,
        user_id: str
    ) -> Payroll:
        """Finance Manager marks payroll as processed after payment"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.APPROVED:
            raise BadRequestException("Can only process approved payroll")
        
        payroll.status = PayrollStatus.PROCESSED
        payroll.processed_by_id = uuid.UUID(user_id)
        payroll.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def delete_payroll(
        session: AsyncSession,
        payroll_id: str,
        user_id: str
    ) -> None:
        """Soft delete payroll (only in DRAFT or REJECTED status)"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status not in [PayrollStatus.DRAFT, PayrollStatus.REJECTED]:
            raise BadRequestException("Can only delete payroll in DRAFT or REJECTED status")
        
        payroll.is_deleted = True
        payroll.deleted_at = datetime.utcnow()
        payroll.updated_at = datetime.utcnow()
        
        await session.commit()
    
    @staticmethod
    async def get_payroll_stats(
        session: AsyncSession,
        user_id: str,
        country_code: Optional[str] = None
    ) -> dict:
        """Get payroll statistics for dashboard (tenant-aware)"""
        
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        
        # Build base filters
        base_filters = [Payroll.is_deleted == False]
        if country_code:
            base_filters.append(Payroll.country_code == country_code)
        
        # Total payrolls
        total_query = select(func.count()).select_from(Payroll).where(*base_filters)
        total_payrolls = await session.scalar(total_query)
        
        # Pending counts
        pending_finance_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.PENDING_FINANCE,
            *base_filters
        )
        pending_finance = await session.scalar(pending_finance_query)
        
        pending_ceo_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.PENDING_CEO,
            *base_filters
        )
        pending_ceo = await session.scalar(pending_ceo_query)
        
        approved_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.APPROVED,
            *base_filters
        )
        approved = await session.scalar(approved_query)
        
        # Total amount this month
        month_amount_query = select(func.sum(Payroll.total_net_salary)).where(
            Payroll.year == current_year,
            Payroll.month == current_month,
            *base_filters
        )
        month_amount = await session.scalar(month_amount_query) or Decimal('0')
        
        # Total amount this year
        year_amount_query = select(func.sum(Payroll.total_net_salary)).where(
            Payroll.year == current_year,
            *base_filters
        )
        year_amount = await session.scalar(year_amount_query) or Decimal('0')
        
        return {
            "total_payrolls": total_payrolls or 0,
            "pending_finance_count": pending_finance or 0,
            "pending_ceo_count": pending_ceo or 0,
            "approved_count": approved or 0,
            "total_amount_this_month": month_amount,
            "total_amount_this_year": year_amount
        }
