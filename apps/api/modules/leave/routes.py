"""Leave & Attendance Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from core.pdf_generator import create_leave_request_pdf
from modules.leave.models import LeaveRequest
from modules.employees.models import Employee

router = APIRouter()

@router.get("/balance")
async def get_leave_balance(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Get employee leave balance"""
    return {"message": "Get leave balance - TODO"}

@router.post("/requests")
async def submit_leave_request(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Submit leave request"""
    return {"message": "Submit leave request - TODO"}

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
async def approve_leave_request(request_id: str, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Approve leave request"""
    return {"message": f"Approve leave request {request_id} - TODO"}

@router.post("/attendance")
async def record_attendance(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Record attendance"""
    return {"message": "Record attendance - TODO"}

@router.get("/policies")
async def list_leave_policies(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List leave policies"""
    return {"message": "List leave policies - TODO"}
