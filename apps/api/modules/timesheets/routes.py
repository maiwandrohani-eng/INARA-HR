"""Timesheets Module - Routes"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from core.database import get_db
from core.dependencies import get_current_active_user, require_admin
from core.pdf_generator import create_timesheet_pdf
from modules.timesheets.models import Timesheet
from modules.employees.models import Employee

router = APIRouter()

@router.get("/")
async def list_timesheets(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_active_user)):
    """List employee timesheets"""
    from modules.timesheets.models import TimesheetEntry
    from modules.employees.models import Employee
    from sqlalchemy import and_
    
    # Get current user's employee_id
    employee_result = await db.execute(
        select(Employee).where(Employee.user_id == current_user['id'], Employee.is_deleted == False)
    )
    employee = employee_result.scalar_one_or_none()
    
    # Build query - filter by employee_id if user is not admin/superuser
    query = select(Timesheet).options(
        selectinload(Timesheet.employee),
        selectinload(Timesheet.approver),
        selectinload(Timesheet.entries).selectinload(TimesheetEntry.project)
    ).where(Timesheet.is_deleted == False)
    
    # If user has an employee record, filter by their employee_id
    # If admin/superuser, show all timesheets
    if employee and not current_user.get('is_superuser', False):
        # Check if user has admin role
        from modules.auth.models import User
        user_result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.id == current_user['id'])
        )
        user = user_result.scalar_one_or_none()
        has_admin_role = user and any(role.name in ['admin', 'super_admin', 'hr_admin'] for role in user.roles)
        
        if not has_admin_role:
            query = query.where(Timesheet.employee_id == employee.id)
    
    query = query.order_by(Timesheet.created_at.desc())
    result = await db.execute(query)
    timesheets = result.scalars().all()
    
    timesheet_list = []
    for t in timesheets:
        # Fetch entries for this timesheet (exclude soft-deleted)
        entries_result = await db.execute(
            select(TimesheetEntry)
            .where(
                TimesheetEntry.timesheet_id == t.id,
                TimesheetEntry.is_deleted == False
            )
            .order_by(TimesheetEntry.date)
        )
        entries = entries_result.scalars().all()
        
        timesheet_list.append({
            "id": str(t.id),
            "employee": f"{t.employee.first_name} {t.employee.last_name}" if t.employee else "Unknown",
            "period_start": str(t.period_start) if t.period_start else None,
            "period_end": str(t.period_end) if t.period_end else None,
            "start_date": str(t.period_start) if t.period_start else None,
            "end_date": str(t.period_end) if t.period_end else None,
            "total_hours": float(t.total_hours or 0),
            "status": t.status,
            "submitted_date": str(t.submitted_date) if t.submitted_date else None,
            "approved_date": str(t.approved_date) if t.approved_date else None,
            "approver_name": f"{t.approver.first_name} {t.approver.last_name}" if t.approver else None,
            "entries": [{
                "id": str(e.id),
                "date": str(e.date),
                "project_id": str(e.project_id) if e.project_id else None,
                "project_name": e.project.name if e.project else (str(e.project_id)[:8] if e.project_id else "N/A"),
                "hours": float(e.hours),
                "activity_description": e.activity_description,
                "description": e.activity_description,
                "notes": e.notes
            } for e in entries]
        })
    
    return {"timesheets": timesheet_list}

@router.post("/")
async def create_timesheet(
    timesheet_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create timesheet"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        from datetime import datetime, date
        
        # Calculate total hours from entries
        entries = timesheet_data.get('entries', [])
        logger.info(f"Creating timesheet with {len(entries)} entries. Entry data: {entries[:3] if entries else 'No entries'}")
        total_hours = sum(float(entry.get('hours', 0)) for entry in entries)
        logger.info(f"Total hours calculated: {total_hours}")
        
        # Parse dates - handle both ISO format and YYYY-M-D format
        def parse_date(date_str: str):
            """Parse date string, handling both ISO and non-ISO formats"""
            try:
                return datetime.fromisoformat(date_str).date()
            except ValueError:
                # Try parsing YYYY-M-D format
                try:
                    parts = date_str.split('-')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        return date(year, month, day)
                except (ValueError, AttributeError):
                    pass
                # If all else fails, try datetime.strptime
                from datetime import datetime as dt
                for fmt in ['%Y-%m-%d', '%Y-%m-%d', '%Y/%m/%d']:
                    try:
                        return dt.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                raise ValueError(f"Invalid date format: {date_str}")
        
        new_timesheet = Timesheet(
            employee_id=uuid.UUID(timesheet_data['employee_id']),
            period_start=parse_date(timesheet_data['period_start']),
            period_end=parse_date(timesheet_data['period_end']),
            total_hours=total_hours,
            status='submitted',
            submitted_date=datetime.now().date(),
            created_by=current_user['id']
        )
        
        db.add(new_timesheet)
        await db.flush()
        
        # Add timesheet entries
        from modules.timesheets.models import TimesheetEntry, Project
        from sqlalchemy import or_
        
        # Helper function to get or create project
        async def get_or_create_project(project_identifier: str):
            """Get existing project by UUID or name, or create new one"""
            # Try to parse as UUID first
            try:
                project_uuid = uuid.UUID(project_identifier)
                result = await db.execute(
                    select(Project).where(Project.id == project_uuid, Project.is_deleted == False)
                )
                project = result.scalar_one_or_none()
                if project:
                    return project
            except ValueError:
                pass  # Not a valid UUID, treat as name
            
            # Try to find by name
            result = await db.execute(
                select(Project).where(
                    or_(
                        Project.name == project_identifier,
                        Project.project_code == project_identifier
                    ),
                    Project.is_deleted == False
                )
            )
            project = result.scalar_one_or_none()
            
            if project:
                return project
            
            # Create new project if not found
            project_code = project_identifier.upper().replace(' ', '_')[:50]
            new_project = Project(
                project_code=project_code,
                name=project_identifier,
                status="active",
                country_code=new_timesheet.country_code if hasattr(new_timesheet, 'country_code') else None
            )
            db.add(new_project)
            await db.flush()
            return new_project
        
        entries_created = 0
        for entry in entries:
            if not entry.get('project_id'):
                logger.warning(f"Skipping entry without project_id: {entry}")
                continue  # Skip entries without project_id
                
            # Parse entry date
            entry_date = parse_date(entry['date']) if isinstance(entry['date'], str) else entry['date']
            
            try:
                # Get or create project
                project = await get_or_create_project(entry['project_id'])
                logger.info(f"Using project: {project.name} (ID: {project.id}) for entry on {entry_date}")
                
                timesheet_entry = TimesheetEntry(
                    timesheet_id=new_timesheet.id,
                    project_id=project.id,
                    date=entry_date,
                    hours=float(entry.get('hours', 0)),
                    activity_description=entry.get('activity_description') or entry.get('description', ''),
                    notes=entry.get('notes', ''),
                    country_code=new_timesheet.country_code if hasattr(new_timesheet, 'country_code') else None
                )
                db.add(timesheet_entry)
                entries_created += 1
                logger.info(f"Added entry: {entry_date}, {float(entry.get('hours', 0))} hours for project {project.name}")
            except Exception as e:
                logger.error(f"Error creating entry: {e}")
                logger.error(f"Entry data: {entry}")
                print(f"Warning: Skipping invalid entry: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f"Created {entries_created} entries out of {len(entries)} provided")
        
        await db.commit()
        await db.refresh(new_timesheet)
        
        # Reload entries to verify they were saved
        entries_result = await db.execute(
            select(TimesheetEntry).where(
                TimesheetEntry.timesheet_id == new_timesheet.id,
                TimesheetEntry.is_deleted == False
            )
        )
        saved_entries = entries_result.scalars().all()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Timesheet {new_timesheet.id} created with {len(saved_entries)} entries. Total hours: {total_hours}")
        
        return {
            "id": str(new_timesheet.id),
            "status": new_timesheet.status,
            "total_hours": float(total_hours),
            "entries_count": len(saved_entries),
            "message": f"Timesheet created successfully with {len(saved_entries)} entries"
        }
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating timesheet: {e}")
        logger.error(traceback.format_exc())
        print(f"Error creating timesheet: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create timesheet: {str(e)}")

@router.post("/{timesheet_id}/entries")
async def add_timesheet_entry(
    timesheet_id: str,
    entry_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Add timesheet entry"""
    try:
        timesheet_uuid = uuid.UUID(timesheet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timesheet ID format")
    
    result = await db.execute(
        select(Timesheet).where(
            Timesheet.id == timesheet_uuid,
            Timesheet.is_deleted == False
        )
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "draft":
        raise HTTPException(status_code=400, detail="Can only add entries to draft timesheets")
    
    from modules.timesheets.models import TimesheetEntry
    from datetime import datetime
    
    new_entry = TimesheetEntry(
        timesheet_id=timesheet.id,
        project_id=uuid.UUID(entry_data['project_id']),
        date=datetime.fromisoformat(entry_data['date']).date(),
        hours=float(entry_data['hours']),
        activity_description=entry_data.get('description', ''),
        notes=entry_data.get('notes', '')
    )
    
    db.add(new_entry)
    
    # Recalculate total hours
    entries_result = await db.execute(
        select(TimesheetEntry).where(TimesheetEntry.timesheet_id == timesheet.id)
    )
    all_entries = entries_result.scalars().all()
    timesheet.total_hours = sum(float(e.hours) for e in all_entries)
    
    await db.commit()
    await db.refresh(new_entry)
    
    return {
        "id": str(new_entry.id),
        "message": "Entry added successfully"
    }


@router.post("/{timesheet_id}/submit")
async def submit_timesheet(
    timesheet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Submit timesheet for approval"""
    try:
        timesheet_uuid = uuid.UUID(timesheet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timesheet ID format")
    
    result = await db.execute(
        select(Timesheet).where(
            Timesheet.id == timesheet_uuid,
            Timesheet.is_deleted == False
        )
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft timesheets can be submitted")
    
    from modules.timesheets.services import TimesheetService
    from modules.employees.repositories import EmployeeRepository
    from datetime import date
    
    employee_repo = EmployeeRepository(db)
    employee = await employee_repo.get_by_id(timesheet.employee_id)
    
    if not employee or not employee.manager_id:
        raise HTTPException(status_code=400, detail="Employee has no supervisor assigned")
    
    timesheet.status = "submitted"
    timesheet.submitted_date = date.today()
    timesheet.approver_id = employee.manager_id
    
    await db.commit()
    
    # Create approval request
    from modules.approvals.services import ApprovalService
    from modules.approvals.schemas import ApprovalRequestCreate
    from modules.approvals.models import ApprovalType
    
    approval_service = ApprovalService(db)
    approval_data = ApprovalRequestCreate(
        request_type=ApprovalType.TIMESHEET,
        request_id=timesheet.id,
        employee_id=timesheet.employee_id,
        comments=f"Timesheet for {timesheet.period_start} to {timesheet.period_end}"
    )
    
    await approval_service.create_approval_request(approval_data, employee.manager_id)
    
    return {
        "id": str(timesheet.id),
        "status": timesheet.status,
        "message": "Timesheet submitted successfully"
    }

@router.patch("/{timesheet_id}")
async def update_timesheet(
    timesheet_id: str,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Approve or reject a timesheet"""
    try:
        timesheet_uuid = uuid.UUID(timesheet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timesheet ID format")
    
    result = await db.execute(
        select(Timesheet).where(
            Timesheet.id == timesheet_uuid,
            Timesheet.is_deleted == False
        )
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    # Get current user's employee record
    from modules.employees.models import Employee
    employee_result = await db.execute(
        select(Employee).where(Employee.user_id == current_user['id'])
    )
    current_employee = employee_result.scalar_one_or_none()
    
    if not current_employee:
        raise HTTPException(status_code=403, detail="No employee record found for current user")
    
    # Update status
    if 'status' in update_data:
        timesheet.status = update_data['status']
        if update_data['status'] in ['approved', 'rejected']:
            from datetime import date
            timesheet.approved_date = date.today()
            timesheet.approver_id = current_employee.id
    
    timesheet.updated_by = current_employee.id
    
    await db.commit()
    await db.refresh(timesheet)
    
    return {
        "id": str(timesheet.id),
        "status": timesheet.status,
        "message": "Timesheet updated successfully"
    }

@router.delete("/{timesheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timesheet(
    timesheet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete timesheet (Admin only - soft delete)"""
    from datetime import datetime
    
    try:
        timesheet_uuid = uuid.UUID(timesheet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timesheet ID format")
    
    result = await db.execute(
        select(Timesheet).where(
            Timesheet.id == timesheet_uuid,
            Timesheet.is_deleted == False
        )
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    # Soft delete
    timesheet.is_deleted = True
    timesheet.deleted_at = datetime.utcnow()
    
    await db.commit()
    return None


@router.get("/projects")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List available projects"""
    from modules.timesheets.models import Project
    
    result = await db.execute(
        select(Project).where(
            Project.is_deleted == False,
            Project.status == "active"
        ).order_by(Project.name)
    )
    projects = result.scalars().all()
    
    return [{
        "id": str(p.id),
        "project_code": p.project_code,
        "name": p.name,
        "donor": p.donor,
        "status": p.status
    } for p in projects]

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
    from modules.timesheets.models import TimesheetEntry, Project
    result = await db.execute(
        select(Timesheet)
        .options(
            selectinload(Timesheet.employee),
            selectinload(Timesheet.approver),
            selectinload(Timesheet.entries).selectinload(TimesheetEntry.project)
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
        "start_date": str(timesheet_record.period_start),
        "end_date": str(timesheet_record.period_end),
        "total_hours": float(timesheet_record.total_hours or 0),
        "status": timesheet_record.status,
        "submitted_at": str(timesheet_record.submitted_date) if timesheet_record.submitted_date else None,
        "approved_at": str(timesheet_record.approved_date) if timesheet_record.approved_date else None,
        "approved_by": {
            "first_name": timesheet_record.approver.first_name if timesheet_record.approver else "",
            "last_name": timesheet_record.approver.last_name if timesheet_record.approver else ""
        } if timesheet_record.approver else None,
        "entries": [
            {
                "date": str(entry.date),
                "project_id": str(entry.project_id) if entry.project_id else None,
                "project_name": entry.project.name if entry.project else None,
                "hours": float(entry.hours),
                "description": entry.activity_description or "",
                "activity_description": entry.activity_description or ""
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
