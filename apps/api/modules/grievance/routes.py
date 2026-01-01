"""Grievance Module - Routes"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_active_user, require_hr_admin
from core.pdf_generator import create_grievance_report_pdf
from .schemas import GrievanceCreate, GrievanceResponse
from .services import GrievanceService
from typing import List

router = APIRouter()

@router.post("/grievances/", response_model=GrievanceResponse)
async def file_grievance(
    grievance: GrievanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Submit a new grievance"""
    try:
        service = GrievanceService(db)
        new_grievance = await service.create_grievance(grievance, current_user["id"])
        
        return GrievanceResponse(
            id=str(new_grievance.id),
            employee_id=str(new_grievance.employee_id),
            case_number=new_grievance.case_number,
            grievance_type=new_grievance.grievance_type,
            description=new_grievance.description,
            filed_date=new_grievance.filed_date,
            status=new_grievance.status,
            resolution=new_grievance.resolution,
            resolution_date=new_grievance.resolution_date,
            created_at=str(new_grievance.created_at) if hasattr(new_grievance, 'created_at') else None
        )
    except Exception as e:
        print(f"Error creating grievance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grievances/", response_model=List[GrievanceResponse])
async def list_grievances(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """List all grievances (HR/Admin only)"""
    try:
        service = GrievanceService(db)
        grievances = await service.get_all_grievances()
        
        return [
            GrievanceResponse(
                id=str(g.id),
                employee_id=str(g.employee_id),
                case_number=g.case_number,
                grievance_type=g.grievance_type,
                description=g.description,
                filed_date=g.filed_date,
                status=g.status,
                resolution=g.resolution,
                resolution_date=g.resolution_date,
                created_at=str(g.created_at) if hasattr(g, 'created_at') else None
            )
            for g in grievances
        ]
    except Exception as e:
        print(f"Error fetching grievances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/grievances/{grievance_id}", response_model=GrievanceResponse)
async def update_grievance(
    grievance_id: str,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """Update a grievance (HR/Admin only)"""
    try:
        import uuid as uuid_lib
        service = GrievanceService(db)
        updated_grievance = await service.update_grievance(
            uuid_lib.UUID(grievance_id),
            update_data,
            current_user["id"]
        )
        
        if not updated_grievance:
            raise HTTPException(status_code=404, detail="Grievance not found")
        
        return GrievanceResponse(
            id=str(updated_grievance.id),
            employee_id=str(updated_grievance.employee_id),
            case_number=updated_grievance.case_number,
            grievance_type=updated_grievance.grievance_type,
            description=updated_grievance.description,
            filed_date=updated_grievance.filed_date,
            status=updated_grievance.status,
            resolution=updated_grievance.resolution,
            resolution_date=updated_grievance.resolution_date,
            created_at=str(updated_grievance.created_at) if hasattr(updated_grievance, 'created_at') else None
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating grievance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disciplinary")
async def record_disciplinary_action(
    action_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_hr_admin)
):
    """Record disciplinary action"""
    from modules.grievance.repositories import DisciplinaryActionRepository
    from modules.grievance.models import DisciplinaryAction
    from datetime import datetime
    import uuid
    
    try:
        employee_uuid = uuid.UUID(action_data['employee_id'])
        action_date = datetime.fromisoformat(action_data['action_date']).date()
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    
    action_repo = DisciplinaryActionRepository(db)
    action_record = await action_repo.create({
        "employee_id": employee_uuid,
        "action_type": action_data['action_type'],
        "reason": action_data['reason'],
        "action_date": action_date,
        "details": action_data.get('details'),
        "document_url": action_data.get('document_url'),
        "created_by": uuid.UUID(current_user["id"])
    })
    
    await db.commit()
    
    return {
        "id": str(action_record.id),
        "employee_id": str(action_record.employee_id),
        "action_type": action_record.action_type,
        "action_date": str(action_record.action_date),
        "message": "Disciplinary action recorded successfully"
    }

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
