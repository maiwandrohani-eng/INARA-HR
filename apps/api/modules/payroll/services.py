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
        year: int
    ) -> bool:
        """Check if payroll already exists for the given month/year"""
        query = select(Payroll).where(
            Payroll.month == month,
            Payroll.year == year,
            Payroll.is_deleted == False
        )
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def create_payroll(
        session: AsyncSession,
        payroll_data: PayrollCreate,
        user_id: str
    ) -> Payroll:
        """Create a new payroll batch"""
        
        # Check if payroll already exists for this month
        exists = await PayrollService.check_payroll_exists(
            session, payroll_data.month, payroll_data.year
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
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def get_payroll(
        session: AsyncSession,
        payroll_id: str
    ) -> Payroll:
        """Get payroll by ID with entries and approvals"""
        query = (
            select(Payroll)
            .options(selectinload(Payroll.entries))
            .options(selectinload(Payroll.approvals))
            .where(
                Payroll.id == uuid.UUID(payroll_id),
                Payroll.is_deleted == False
            )
        )
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
        year: Optional[int] = None
    ) -> tuple[List[Payroll], int]:
        """List payrolls with pagination and filters"""
        
        # Build query
        query = select(Payroll).where(Payroll.is_deleted == False)
        
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
        """Submit payroll to Finance Manager for review"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.DRAFT:
            raise BadRequestException("Can only submit payroll in DRAFT status")
        
        if not payroll.entries:
            raise BadRequestException("Cannot submit empty payroll")
        
        # Update status
        payroll.status = PayrollStatus.PENDING_FINANCE
        payroll.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(payroll)
        
        return payroll
    
    @staticmethod
    async def finance_approve(
        session: AsyncSession,
        payroll_id: str,
        user_id: str,
        approved: bool,
        comments: Optional[str] = None
    ) -> Payroll:
        """Finance Manager approves or rejects payroll"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.PENDING_FINANCE:
            raise BadRequestException("Payroll is not pending Finance approval")
        
        # Create approval record
        approval = PayrollApproval(
            id=uuid.uuid4(),
            payroll_id=payroll.id,
            approver_role="finance_manager",
            approver_id=uuid.UUID(user_id),
            approved="true" if approved else "false",
            decision_date=datetime.utcnow(),
            comments=comments,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(approval)
        
        # Update payroll status
        if approved:
            payroll.status = PayrollStatus.PENDING_CEO
        else:
            payroll.status = PayrollStatus.REJECTED
        
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
        comments: Optional[str] = None
    ) -> Payroll:
        """CEO approves or rejects payroll"""
        
        payroll = await PayrollService.get_payroll(session, payroll_id)
        
        if payroll.status != PayrollStatus.PENDING_CEO:
            raise BadRequestException("Payroll is not pending CEO approval")
        
        # Create approval record
        approval = PayrollApproval(
            id=uuid.uuid4(),
            payroll_id=payroll.id,
            approver_role="ceo",
            approver_id=uuid.UUID(user_id),
            approved="true" if approved else "false",
            decision_date=datetime.utcnow(),
            comments=comments,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(approval)
        
        # Update payroll status
        if approved:
            payroll.status = PayrollStatus.APPROVED
        else:
            payroll.status = PayrollStatus.REJECTED
        
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
        user_id: str
    ) -> dict:
        """Get payroll statistics for dashboard"""
        
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        
        # Total payrolls
        total_query = select(func.count()).select_from(Payroll).where(
            Payroll.is_deleted == False
        )
        total_payrolls = await session.scalar(total_query)
        
        # Pending counts
        pending_finance_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.PENDING_FINANCE,
            Payroll.is_deleted == False
        )
        pending_finance = await session.scalar(pending_finance_query)
        
        pending_ceo_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.PENDING_CEO,
            Payroll.is_deleted == False
        )
        pending_ceo = await session.scalar(pending_ceo_query)
        
        approved_query = select(func.count()).select_from(Payroll).where(
            Payroll.status == PayrollStatus.APPROVED,
            Payroll.is_deleted == False
        )
        approved = await session.scalar(approved_query)
        
        # Total amount this month
        month_amount_query = select(func.sum(Payroll.total_net_salary)).where(
            Payroll.year == current_year,
            Payroll.month == current_month,
            Payroll.is_deleted == False
        )
        month_amount = await session.scalar(month_amount_query) or Decimal('0')
        
        # Total amount this year
        year_amount_query = select(func.sum(Payroll.total_net_salary)).where(
            Payroll.year == current_year,
            Payroll.is_deleted == False
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
