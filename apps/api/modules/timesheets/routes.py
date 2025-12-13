"""Timesheets Module - Routes"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.database import get_db
from core.dependencies import get_current_active_user
from core.pdf_generator import create_timesheet_pdf
from modules.timesheets.models import Timesheet
from modules.employees.models import Employee

router = APIRouter()

@router.get("/")
async def list_timesheets(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List employee timesheets"""
    result = await db.execute(
        select(Timesheet)
        .options(selectinload(Timesheet.employee))
        .where(Timesheet.is_deleted == False)
        .order_by(Timesheet.created_at.desc())
    )
    timesheets = result.scalars().all()
    return {"timesheets": [{"id": str(t.id), "employee": f"{t.employee.first_name} {t.employee.last_name}", "start_date": str(t.start_date), "end_date": str(t.end_date), "status": t.status} for t in timesheets]}

@router.post("/")
async def create_timesheet(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Create timesheet"""
    return {"message": "Create timesheet - TODO"}

@router.post("/{timesheet_id}/entries")
async def add_timesheet_entry(timesheet_id: str, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Add timesheet entry"""
    return {"message": f"Add entry to {timesheet_id} - TODO"}

@router.post("/{timesheet_id}/submit")
async def submit_timesheet(timesheet_id: str, db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """Submit timesheet for approval"""
    return {"message": f"Submit timesheet {timesheet_id} - TODO"}

@router.get("/projects")
async def list_projects(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List available projects"""
    return {"message": "List projects - TODO"}

@router.get("/{timesheet_id}/export")
async def export_timesheet_pdf(
    timesheet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Export timesheet as PDF"""
    try:
        timesheet_uuid = uuid.UUID(timesheet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timesheet ID format")
    
    # Query the database for the actual timesheet
    result = await db.execute(
        select(Timesheet)
        .options(
            selectinload(Timesheet.employee),
            selectinload(Timesheet.approver),
            selectinload(Timesheet.entries)
        )
        .where(Timesheet.id == timesheet_uuid)
        .where(Timesheet.is_deleted == False)
    )
    timesheet_record = result.scalar_one_or_none()
    
    if not timesheet_record:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    # Build the timesheet dict from actual database data
    timesheet = {
        "id": str(timesheet_record.id),
        "employee": {
            "first_name": timesheet_record.employee.first_name,
            "last_name": timesheet_record.employee.last_name
        },
        "start_date": str(timesheet_record.start_date),
        "end_date": str(timesheet_record.end_date),
        "total_hours": float(timesheet_record.total_hours or 0),
        "status": timesheet_record.status,
        "submitted_at": timesheet_record.submitted_at.isoformat() if timesheet_record.submitted_at else None,
        "approved_at": timesheet_record.approved_at.isoformat() if timesheet_record.approved_at else None,
        "approved_by": f"{timesheet_record.approver.first_name} {timesheet_record.approver.last_name}" if timesheet_record.approver else None,
        "entries": [
            {
                "date": str(entry.date),
                "hours": float(entry.hours),
                "description": entry.description or ""
            }
            for entry in timesheet_record.entries
        ]
    }
    
    pdf_buffer = create_timesheet_pdf(timesheet)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=timesheet_{timesheet_id}.pdf"
        }
    )
