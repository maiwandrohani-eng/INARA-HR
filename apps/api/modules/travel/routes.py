"""Travel Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from core.pdf_generator import create_travel_request_pdf
from modules.travel.models import TravelRequest

router = APIRouter()

@router.post("/requests")
async def create_travel_request(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "Create travel request - TODO"}

@router.get("/requests")
async def list_travel_requests(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List travel requests"""
    query = select(TravelRequest).options(
        selectinload(TravelRequest.employee),
        selectinload(TravelRequest.approver)
    ).where(TravelRequest.is_deleted == False)
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return [{
        "id": str(req.id),
        "employee": {
            "first_name": req.employee.first_name if req.employee else "",
            "last_name": req.employee.last_name if req.employee else ""
        },
        "destination": req.destination,
        "departure_date": str(req.departure_date),
        "return_date": str(req.return_date),
        "status": req.status
    } for req in requests]

@router.get("/visas")
async def list_visas(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "List visas - TODO"}

@router.post("/visas")
async def add_visa_record(db = Depends(get_db), current_user = Depends(get_current_active_user)):
    return {"message": "Add visa record - TODO"}

@router.get("/requests/{request_id}/export")
async def export_travel_request_pdf(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Export travel request as PDF"""
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    # Fetch travel request with relationships
    query = select(TravelRequest).options(
        selectinload(TravelRequest.employee),
        selectinload(TravelRequest.approver)
    ).where(
        TravelRequest.id == req_uuid,
        TravelRequest.is_deleted == False
    )
    
    result = await db.execute(query)
    travel_req = result.scalar_one_or_none()
    
    if not travel_req:
        raise HTTPException(status_code=404, detail="Travel request not found")
    
    # Calculate duration
    duration = (travel_req.return_date - travel_req.departure_date).days + 1 if travel_req.departure_date and travel_req.return_date else 0
    
    # Build data for PDF
    travel_request = {
        "id": str(travel_req.id),
        "employee": {
            "first_name": travel_req.employee.first_name if travel_req.employee else "",
            "last_name": travel_req.employee.last_name if travel_req.employee else ""
        },
        "destination": travel_req.destination,
        "purpose": travel_req.purpose,
        "departure_date": str(travel_req.departure_date),
        "return_date": str(travel_req.return_date),
        "duration_days": duration,
        "transport_mode": travel_req.transport_mode or "N/A",
        "estimated_cost": float(travel_req.estimated_cost) if travel_req.estimated_cost else 0,
        "status": travel_req.status,
        "description": travel_req.description or "",
        "created_at": travel_req.created_at.isoformat() if travel_req.created_at else "",
        "approved_by": {
            "first_name": travel_req.approver.first_name if travel_req.approver else "",
            "last_name": travel_req.approver.last_name if travel_req.approver else ""
        } if travel_req.approver else None
    }
    
    pdf_buffer = create_travel_request_pdf(travel_request)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=travel_request_{request_id}.pdf"
        }
    )
