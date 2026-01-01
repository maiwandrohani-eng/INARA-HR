"""Leave & Attendance Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from core.pdf_generator import create_leave_request_pdf
from modules.leave.models import LeaveRequest, LeavePolicy
from modules.employees.models import Employee
from modules.leave.schemas import (
    LeavePolicyCreate, LeavePolicyResponse,
    LeaveRequestCreate, AttendanceRecordCreate
)

router = APIRouter()

@router.get("/balance")
async def get_leave_balance(
    year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get employee leave balance"""
    from modules.leave.services import LeaveService
    from modules.employees.repositories import EmployeeRepository
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    leave_service = LeaveService(db)
    balances = await leave_service.get_employee_balances(employee.id, year)
    
    return [balance.model_dump() for balance in balances]


@router.post("/requests")
async def submit_leave_request(
    request_data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Submit leave request"""
    from modules.leave.services import LeaveService
    from modules.employees.repositories import EmployeeRepository
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    leave_service = LeaveService(db)
    leave_request = await leave_service.submit_leave_request(request_data, employee.id)
    
    return leave_request.model_dump()

@router.get("/requests")
async def list_leave_requests(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List leave requests"""
    # Query leave requests with employee relationships
    query = select(LeaveRequest).options(
        selectinload(LeaveRequest.employee),
        selectinload(LeaveRequest.approver)
    ).where(LeaveRequest.is_deleted == False)
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return [{
        "id": str(req.id),
        "employee": {
            "first_name": req.employee.first_name if req.employee else "",
            "last_name": req.employee.last_name if req.employee else ""
        },
        "leave_type": req.leave_type,
        "start_date": str(req.start_date),
        "end_date": str(req.end_date),
        "total_days": float(req.total_days),
        "status": req.status,
        "created_at": req.created_at.isoformat() if req.created_at else None
    } for req in requests]

@router.get("/requests/{request_id}/export")
async def export_leave_request_pdf(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Export leave request as PDF"""
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    # Fetch leave request with relationships
    query = select(LeaveRequest).options(
        selectinload(LeaveRequest.employee),
        selectinload(LeaveRequest.approver)
    ).where(
        LeaveRequest.id == request_uuid,
        LeaveRequest.is_deleted == False
    )
    
    result = await db.execute(query)
    leave_req = result.scalar_one_or_none()
    
    if not leave_req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    # Build data for PDF
    leave_request = {
        "id": str(leave_req.id),
        "employee": {
            "first_name": leave_req.employee.first_name if leave_req.employee else "",
            "last_name": leave_req.employee.last_name if leave_req.employee else ""
        },
        "leave_type": leave_req.leave_type.replace('_', ' ').title(),
        "start_date": str(leave_req.start_date),
        "end_date": str(leave_req.end_date),
        "total_days": float(leave_req.total_days),
        "status": leave_req.status,
        "reason": leave_req.reason or "N/A",
        "notes": leave_req.notes or "",
        "created_at": leave_req.created_at.isoformat() if leave_req.created_at else "",
        "approved_at": str(leave_req.approved_date) if leave_req.approved_date else None,
        "approved_by": {
            "first_name": leave_req.approver.first_name if leave_req.approver else "",
            "last_name": leave_req.approver.last_name if leave_req.approver else ""
        } if leave_req.approver else None
    }
    
    pdf_buffer = create_leave_request_pdf(leave_request)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=leave_request_{request_id}.pdf"
        }
    )

@router.post("/requests/{request_id}/approve")
async def approve_leave_request(
    request_id: str,
    comments: Optional[str] = None,
    approval_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Approve leave request through approval workflow"""
    from modules.leave.services import LeaveService
    from modules.employees.repositories import EmployeeRepository
    from modules.approvals.services import ApprovalService
    from modules.approvals.models import ApprovalType
    
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    # If approval_id not provided, find the pending approval for this request
    approval_service = ApprovalService(db)
    if not approval_id:
        approval = await approval_service.get_approval_by_request(ApprovalType.LEAVE, request_uuid)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found for this leave request")
        approval_id = approval.id
    else:
        try:
            approval_uuid = uuid.UUID(approval_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid approval ID format")
        approval_id = approval_uuid
    
    leave_service = LeaveService(db)
    leave_request = await leave_service.approve_leave_request(request_uuid, employee.id, comments, approval_id)
    
    return leave_request.model_dump()


@router.post("/requests/{request_id}/reject")
async def reject_leave_request(
    request_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Reject leave request"""
    from modules.leave.services import LeaveService
    from modules.employees.repositories import EmployeeRepository
    
    try:
        request_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_user_id(current_user["id"])
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    leave_service = LeaveService(db)
    leave_request = await leave_service.reject_leave_request(request_uuid, employee.id, reason)
    
    return leave_request.model_dump()


@router.post("/attendance")
async def record_attendance(
    attendance_data: AttendanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Record attendance"""
    from modules.leave.services import LeaveService
    from modules.leave.schemas import AttendanceRecordCreate
    
    leave_service = LeaveService(db)
    record = await leave_service.record_attendance(attendance_data)
    
    return record.model_dump()

@router.get("/policies")
async def list_leave_policies(
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_active_user)
):
    """List all leave policies"""
    query = select(LeavePolicy).where(LeavePolicy.is_deleted == False)
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return [{
        "id": str(policy.id),
        "name": policy.name,
        "leave_type": policy.leave_type,
        "days_per_year": float(policy.days_per_year),
        "accrual_rate": policy.accrual_rate,
        "max_carryover": float(policy.max_carryover) if policy.max_carryover else None,
        "requires_approval": policy.requires_approval,
        "description": policy.description,
        "country_code": policy.country_code,
        "created_at": policy.created_at.isoformat() if policy.created_at else None
    } for policy in policies]

@router.post("/policies")
async def create_leave_policy(
    policy_data: LeavePolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new leave policy"""
    # Create new policy
    new_policy = LeavePolicy(
        name=policy_data.name,
        leave_type=policy_data.leave_type,
        days_per_year=policy_data.days_per_year,
        accrual_rate=policy_data.accrual_rate,
        max_carryover=policy_data.max_carryover,
        requires_approval=policy_data.requires_approval,
        description=policy_data.description,
        country_code=getattr(current_user, 'country_code', 'AF')
    )
    
    db.add(new_policy)
    await db.commit()
    await db.refresh(new_policy)
    
    return {
        "id": str(new_policy.id),
        "name": new_policy.name,
        "leave_type": new_policy.leave_type,
        "days_per_year": float(new_policy.days_per_year),
        "accrual_rate": new_policy.accrual_rate,
        "max_carryover": float(new_policy.max_carryover) if new_policy.max_carryover else None,
        "requires_approval": new_policy.requires_approval,
        "description": new_policy.description,
        "country_code": new_policy.country_code,
        "created_at": new_policy.created_at.isoformat() if new_policy.created_at else None
    }

@router.put("/policies/{policy_id}")
async def update_leave_policy(
    policy_id: str,
    policy_data: LeavePolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update a leave policy"""
    try:
        policy_uuid = uuid.UUID(policy_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid policy ID format")
    
    query = select(LeavePolicy).where(
        LeavePolicy.id == policy_uuid,
        LeavePolicy.is_deleted == False
    )
    result = await db.execute(query)
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Leave policy not found")
    
    # Update fields
    policy.name = policy_data.name
    policy.leave_type = policy_data.leave_type
    policy.days_per_year = policy_data.days_per_year
    policy.accrual_rate = policy_data.accrual_rate
    policy.max_carryover = policy_data.max_carryover
    policy.requires_approval = policy_data.requires_approval
    policy.description = policy_data.description
    
    await db.commit()
    await db.refresh(policy)
    
    return {
        "id": str(policy.id),
        "name": policy.name,
        "leave_type": policy.leave_type,
        "days_per_year": float(policy.days_per_year),
        "accrual_rate": policy.accrual_rate,
        "max_carryover": float(policy.max_carryover) if policy.max_carryover else None,
        "requires_approval": policy.requires_approval,
        "description": policy.description,
        "country_code": policy.country_code,
        "created_at": policy.created_at.isoformat() if policy.created_at else None
    }

@router.delete("/policies/{policy_id}")
async def delete_leave_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete a leave policy (soft delete)"""
    try:
        policy_uuid = uuid.UUID(policy_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid policy ID format")
    
    query = select(LeavePolicy).where(
        LeavePolicy.id == policy_uuid,
        LeavePolicy.is_deleted == False
    )
    result = await db.execute(query)
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Leave policy not found")
    
    policy.is_deleted = True
    await db.commit()
    
    return {"message": "Leave policy deleted successfully"}
