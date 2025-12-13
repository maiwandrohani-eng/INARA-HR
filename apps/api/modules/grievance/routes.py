"""Grievance Module - Routes"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from core.database import get_db
from core.dependencies import get_current_active_user, require_hr_admin
from core.pdf_generator import create_grievance_report_pdf

router = APIRouter()

@router.post("/grievances")
async def file_grievance(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "File grievance - TODO"}

@router.get("/grievances")
async def list_grievances(db = Depends(get_db), current_user = Depends(require_hr_admin)):
    return {"message": "List grievances - TODO"}

@router.post("/disciplinary")
async def record_disciplinary_action(db = Depends(get_db), current_user = Depends(require_hr_admin)):
    return {"message": "Record disciplinary action - TODO"}

@router.get("/grievances/{grievance_id}/export")
async def export_grievance_pdf(
    grievance_id: str,
    db = Depends(get_db),
    current_user = Depends(require_hr_admin)
):
    """Export grievance report as PDF (HR Admin only)"""
    # TODO: Fetch actual grievance from database
    grievance = {
        "id": grievance_id,
        "reporter": {"first_name": "John", "last_name": "Doe"},
        "category": "workplace_harassment",
        "severity": "high",
        "status": "under_investigation",
        "description": "Detailed description of the grievance case. This includes all relevant information about the incident.",
        "resolution": "Case is currently under investigation. HR team has been assigned.",
        "created_at": "2025-01-10T09:00:00",
        "assigned_to": {"first_name": "HR", "last_name": "Manager"}
    }
    
    pdf_buffer = create_grievance_report_pdf(grievance)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=grievance_{grievance_id}.pdf"
        }
    )
