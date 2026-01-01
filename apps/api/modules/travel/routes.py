"""Travel Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime

from core.database import get_db
from core.dependencies import get_current_active_user, require_admin
from core.pdf_generator import create_travel_request_pdf
from modules.travel.models import TravelRequest

router = APIRouter()

@router.post("/requests")
async def create_travel_request(
    request_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new travel request"""
    try:
        # Parse dates from first travel segment
        travel_segments = request_data.get('travel_segments', [])
        if not travel_segments:
            raise HTTPException(status_code=400, detail="At least one travel segment required")
        
        first_segment = travel_segments[0]
        last_segment = travel_segments[-1]
        
        # Calculate destination
        destinations = [seg.get('to', '') for seg in travel_segments if seg.get('to')]
        destination = ' → '.join(destinations)
        
        from datetime import datetime
        departure_date = datetime.fromisoformat(first_segment['startDate']).date()
        return_date = datetime.fromisoformat(last_segment['endDate']).date()
        duration = (return_date - departure_date).days + 1
        
        # Get transport mode from first segment
        transport_mode = first_segment.get('mode', 'Not specified')
        
        new_request = TravelRequest(
            employee_id=uuid.UUID(request_data['employee_id']),
            destination=destination,
            purpose=request_data.get('purpose', ''),
            departure_date=departure_date,
            return_date=return_date,
            duration_days=duration,
            transport_mode=transport_mode,
            estimated_cost=request_data.get('total_estimated_expenses', 0),
            description=request_data.get('purpose', ''),
            status='pending',
            created_by=current_user['id']
        )
        
        db.add(new_request)
        await db.commit()
        await db.refresh(new_request)
        
        return {
            "id": str(new_request.id),
            "destination": new_request.destination,
            "status": new_request.status,
            "message": "Travel request created successfully"
        }
    except Exception as e:
        print(f"Error creating travel request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        "employee_name": f"{req.employee.first_name} {req.employee.last_name}" if req.employee else "",
        "employee": {
            "first_name": req.employee.first_name if req.employee else "",
            "last_name": req.employee.last_name if req.employee else ""
        },
        "destination": req.destination,
        "purpose": req.purpose,
        "departure_date": str(req.departure_date) if req.departure_date else None,
        "return_date": str(req.return_date) if req.return_date else None,
        "start_date": str(req.departure_date) if req.departure_date else None,
        "end_date": str(req.return_date) if req.return_date else None,
        "duration_days": float(req.duration_days) if req.duration_days else 0,
        "transport_mode": req.transport_mode,
        "estimated_cost": float(req.estimated_cost) if req.estimated_cost else 0,
        "description": req.description,
        "notes": req.description,
        "accommodation_required": False,
        "status": req.status,
        "approval_date": str(req.approval_date) if req.approval_date else None,
        "approver_name": f"{req.approver.first_name} {req.approver.last_name}" if req.approver else None
    } for req in requests]

@router.patch("/requests/{request_id}")
async def update_travel_request(
    request_id: str,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Approve or reject a travel request"""
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    query = select(TravelRequest).where(
        TravelRequest.id == req_uuid,
        TravelRequest.is_deleted == False
    )
    result = await db.execute(query)
    travel_req = result.scalar_one_or_none()
    
    if not travel_req:
        raise HTTPException(status_code=404, detail="Travel request not found")
    
    # Update status
    if 'status' in update_data:
        travel_req.status = update_data['status']
        if update_data['status'] in ['approved', 'rejected']:
            from datetime import date
            travel_req.approval_date = date.today()
            travel_req.approver_id = current_user['id']
    
    travel_req.updated_by = current_user['id']
    
    await db.commit()
    await db.refresh(travel_req)
    
    return {
        "id": str(travel_req.id),
        "status": travel_req.status,
        "message": "Travel request updated successfully"
    }

@router.get("/visas")
async def list_visas(
    employee_id: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List visa records"""
    from modules.travel.services import TravelService
    from modules.employees.repositories import EmployeeRepository
    import uuid
    
    employee_repo = EmployeeRepository(db)
    
    if employee_id:
        try:
            target_employee_id = uuid.UUID(employee_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid employee ID format")
    else:
        # Get current user's employee record
        employee = await employee_repo.get_by_user_id(current_user["id"])
        if not employee:
            raise HTTPException(status_code=404, detail="Employee profile not found")
        target_employee_id = employee.id
    
    travel_service = TravelService(db)
    visas = await travel_service.get_visa_records(target_employee_id)
    return visas


@router.post("/visas")
async def add_visa_record(
    visa_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Add visa record"""
    from modules.travel.services import TravelService
    from modules.employees.repositories import EmployeeRepository
    from datetime import datetime
    import uuid
    
    employee_repo = EmployeeRepository(db)
    
    try:
        employee_uuid = uuid.UUID(visa_data['employee_id'])
        expiry_date = datetime.fromisoformat(visa_data['expiry_date']).date()
        issue_date = datetime.fromisoformat(visa_data['issue_date']).date() if visa_data.get('issue_date') else None
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    travel_service = TravelService(db)
    visa = await travel_service.add_visa_record(
        employee_id=employee_uuid,
        country=visa_data['country'],
        visa_type=visa_data['visa_type'],
        expiry_date=expiry_date,
        visa_number=visa_data.get('visa_number'),
        issue_date=issue_date,
        notes=visa_data.get('notes'),
        created_by=uuid.UUID(current_user["id"])
    )
    
    return visa

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


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_travel_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete travel request (Admin only - soft delete)"""
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    result = await db.execute(
        select(TravelRequest).where(
            TravelRequest.id == req_uuid,
            TravelRequest.is_deleted == False
        )
    )
    travel_req = result.scalar_one_or_none()
    
    if not travel_req:
        raise HTTPException(status_code=404, detail="Travel request not found")
    
    # Soft delete
    travel_req.is_deleted = True
    travel_req.deleted_at = datetime.utcnow()
    
    await db.commit()
    return None
