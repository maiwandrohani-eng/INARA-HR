"""
Payroll Module - API Routes
FastAPI routes for payroll management
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import io

from core.database import get_db
from core.dependencies import get_current_user
from .schemas import (
    EmployeePayrollSummary,
    PayrollCreate,
    PayrollUpdate,
    PayrollResponse,
    PayrollListResponse,
    PayrollApprovalRequest,
    PayrollStatsResponse
)
from .services import PayrollService

router = APIRouter(prefix="/payroll", tags=["payroll"])


@router.get("/employees", response_model=list[EmployeePayrollSummary])
async def get_employees_for_payroll(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active employees with contract salary for payroll processing.
    Only accessible to HR Manager and HR Admin.
    """
    employees = await PayrollService.get_active_employees_for_payroll(
        session, current_user["id"]
    )
    return employees


@router.post("", response_model=PayrollResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    payroll_data: PayrollCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new payroll batch.
    Only accessible to HR Manager and HR Admin.
    """
    payroll = await PayrollService.create_payroll(
        session, payroll_data, current_user["id"]
    )
    return payroll


@router.get("", response_model=PayrollListResponse)
async def list_payrolls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    year: Optional[int] = None,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all payrolls with pagination and filters.
    Accessible to HR Manager, Finance Manager, and CEO.
    """
    # Get user's country_code for tenant filtering
    # Finance Manager and CEO can see all payrolls across all countries
    user_roles = current_user.get('roles', [])
    user_country = None if any(role in ['finance_manager', 'ceo', 'admin'] for role in user_roles) else current_user.get('country_code')
    
    payrolls, total = await PayrollService.list_payrolls(
        session, page, page_size, status, year, user_country
    )
    
    return PayrollListResponse(
        payrolls=payrolls,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=PayrollStatsResponse)
async def get_payroll_stats(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get payroll statistics for dashboard.
    Accessible to HR Manager, Finance Manager, and CEO.
    """
    # Get user's country_code for tenant filtering
    # Finance Manager and CEO can see all payrolls across all countries
    user_roles = current_user.get('roles', [])
    user_country = None if any(role in ['finance_manager', 'ceo', 'admin'] for role in user_roles) else current_user.get('country_code')
    
    stats = await PayrollService.get_payroll_stats(session, current_user["id"], user_country)
    return stats


@router.get("/{payroll_id}", response_model=PayrollResponse)
async def get_payroll(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get payroll by ID with all entries and approvals.
    Accessible to HR Manager, Finance Manager, and CEO.
    """
    # Get user's country_code for tenant filtering
    # Finance Manager and CEO can see all payrolls across all countries
    user_roles = current_user.get('roles', [])
    user_country = None if any(role in ['finance_manager', 'ceo', 'admin'] for role in user_roles) else current_user.get('country_code')
    
    payroll = await PayrollService.get_payroll(session, payroll_id, user_country)
    return payroll


@router.put("/{payroll_id}", response_model=PayrollResponse)
async def update_payroll(
    payroll_id: str,
    payroll_data: PayrollUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update payroll (only in DRAFT status).
    Only accessible to HR Manager and HR Admin.
    """
    payroll = await PayrollService.update_payroll(
        session, payroll_id, payroll_data, current_user["id"]
    )
    return payroll


@router.post("/{payroll_id}/submit", response_model=PayrollResponse)
async def submit_payroll_to_finance(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit payroll to Finance Manager for review.
    Only accessible to HR Manager and HR Admin.
    """
    payroll = await PayrollService.submit_to_finance(
        session, payroll_id, current_user["id"]
    )
    return payroll


@router.post("/{payroll_id}/finance-approve", response_model=PayrollResponse)
async def finance_approve_payroll(
    payroll_id: str,
    approval_data: PayrollApprovalRequest,
    approval_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Finance Manager approves or rejects payroll.
    Only accessible to Finance Manager.
    """
    import uuid as uuid_lib
    approval_uuid = uuid_lib.UUID(approval_id) if approval_id else None
    
    payroll = await PayrollService.finance_approve(
        session,
        payroll_id,
        current_user["id"],
        approval_data.approved,
        approval_data.comments,
        approval_uuid
    )
    return payroll


@router.post("/{payroll_id}/ceo-approve", response_model=PayrollResponse)
async def ceo_approve_payroll(
    payroll_id: str,
    approval_data: PayrollApprovalRequest,
    approval_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    CEO approves or rejects payroll.
    Only accessible to CEO/Admin.
    """
    import uuid as uuid_lib
    approval_uuid = uuid_lib.UUID(approval_id) if approval_id else None
    
    payroll = await PayrollService.ceo_approve(
        session,
        payroll_id,
        current_user["id"],
        approval_data.approved,
        approval_data.comments,
        approval_uuid
    )
    return payroll


@router.post("/{payroll_id}/mark-processed", response_model=PayrollResponse)
async def mark_payroll_processed(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Finance Manager marks payroll as processed after payment.
    Only accessible to Finance Manager.
    """
    payroll = await PayrollService.mark_processed(
        session, payroll_id, current_user["id"]
    )
    return payroll


@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Soft delete payroll (only in DRAFT or REJECTED status).
    Only accessible to HR Manager and HR Admin.
    """
    await PayrollService.delete_payroll(session, payroll_id, current_user["id"])
    return None


@router.get("/{payroll_id}/download", response_class=Response)
async def download_payroll_pdfs(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download payroll as ZIP file containing individual PDF payslips.
    Only accessible to Finance Manager and CEO after approval.
    """
    from modules.payroll.pdf_generator import pdf_generator
    
    payroll = await PayrollService.get_payroll(session, payroll_id)
    
    # Generate ZIP file with all payslips
    zip_bytes = pdf_generator.generate_payroll_zip(payroll, payroll.entries)
    
    filename = f"payroll_{payroll.year}_{payroll.month:02d}_payslips.zip"
    
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{payroll_id}/my-payslip", response_class=Response)
async def download_my_payslip(
    payroll_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download employee's own payslip for a specific payroll period.
    Only accessible to the employee themselves for approved/processed payrolls.
    """
    from modules.payroll.pdf_generator import pdf_generator
    from modules.payroll.models import PayrollEntry
    from modules.employees.models import Employee
    from sqlalchemy import select, and_
    from fastapi import HTTPException
    
    # Get employee record from user_id
    employee_result = await session.execute(
        select(Employee).where(Employee.user_id == current_user["id"])
    )
    employee = employee_result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    # Get payroll
    payroll = await PayrollService.get_payroll(session, payroll_id)
    
    # Check if payroll is approved or processed
    if payroll.status not in ["APPROVED", "PROCESSED"]:
        raise HTTPException(status_code=403, detail="Payslip not available yet")
    
    # Get employee's payroll entry
    entry_result = await session.execute(
        select(PayrollEntry).where(
            and_(
                PayrollEntry.payroll_id == payroll.id,
                PayrollEntry.employee_id == employee.id
            )
        )
    )
    entry = entry_result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="No payslip found for this period")
    
    # Generate individual payslip PDF
    pdf_bytes = pdf_generator.generate_payslip(payroll, entry)
    
    filename = f"{employee.employee_number}_payslip_{payroll.year}_{payroll.month:02d}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

