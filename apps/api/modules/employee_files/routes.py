"""
API routes for employee files management
"""
from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user, require_hr_write, require_hr_read
from .services import DocumentService, ContractService, ResignationService
from .schemas import (
    DocumentCreate, DocumentResponse, DocumentListResponse,
    ContractCreate, ContractResponse, ContractListResponse, ContractUpdate,
    ExtensionCreate, ExtensionResponse, ExtensionListResponse, ExtensionAccept,
    ResignationCreate, ResignationResponse, ResignationListResponse,
    ResignationApprove, ResignationCEOApprove, ResignationComplete,
    PersonalFileSummary, PendingExtensionNotification, PendingResignationNotification
)
from .models import DocumentCategory, ResignationStatus

router = APIRouter(prefix="/employee-files", tags=["employee-files"])


# ============= Document Routes =============

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    employee_id: UUID = Form(...),
    category: DocumentCategory = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    expiry_date: Optional[date] = Form(None),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document to an employee's personal file"""
    from core.file_storage import file_storage
    from core.config import settings
    from core.exceptions import FileUploadException
    import os
    
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_FILE_SIZE_BYTES:
        max_size_mb = settings.MAX_FILE_SIZE_MB
        raise FileUploadException(
            message=f"File size exceeds maximum allowed size of {max_size_mb}MB",
            details=f"Uploaded file: {file_size / (1024*1024):.2f}MB, Maximum: {max_size_mb}MB"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext and file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise FileUploadException(
            message=f"File type not allowed",
            details=f"Allowed extensions: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Upload file to storage (S3 or local)
    upload_result = await file_storage.upload_file(
        file_content=file_content,
        file_name=file.filename,
        folder="employee_files",
        employee_id=str(employee_id)
    )
    
    document = await DocumentService.create_document(
        db=db,
        employee_id=employee_id,
        category=category,
        title=title,
        file_path=upload_result["file_path"],
        file_name=upload_result["file_name"],
        file_size=upload_result["file_size"],
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by=current_user["id"],
        country_code=current_user.get("country_code", "AFG"),
        description=description,
        is_confidential=is_confidential,
        expiry_date=expiry_date,
        notes=notes
    )
    
    return document


@router.get("/documents/employee/{employee_id}", response_model=DocumentListResponse)
async def get_employee_documents(
    employee_id: UUID,
    category: Optional[DocumentCategory] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all documents for an employee"""
    documents = await DocumentService.get_employee_documents(
        db=db,
        employee_id=employee_id,
        category=category
    )
    
    return DocumentListResponse(
        documents=documents,
        total=len(documents)
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document"""
    document = await DocumentService.get_document_by_id(db, document_id)
    return document


@router.delete("/documents/{document_id}", response_model=DocumentResponse)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Soft delete a document"""
    document = await DocumentService.soft_delete_document(db, document_id)
    return document


# ============= Contract Routes =============

@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    contract: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new employment contract"""
    new_contract = await ContractService.create_contract(
        db=db,
        employee_id=contract.employee_id,
        contract_number=contract.contract_number,
        position_title=contract.position_title,
        location=contract.location,
        contract_type=contract.contract_type,
        start_date=contract.start_date,
        end_date=contract.end_date,
        monthly_salary=contract.monthly_salary,
        currency=contract.currency,
        country_code=current_user.get("country_code", "AFG"),
        created_by=current_user["id"],
        document_id=contract.document_id,
        notice_period_days=contract.notice_period_days,
        signed_date=contract.signed_date
    )
    
    return new_contract


@router.get("/contracts/employee/{employee_id}", response_model=ContractListResponse)
async def get_employee_contracts(
    employee_id: UUID,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all contracts for an employee"""
    contracts = await ContractService.get_employee_contracts(
        db=db,
        employee_id=employee_id,
        include_inactive=include_inactive
    )
    
    return ContractListResponse(
        contracts=contracts,
        total=len(contracts)
    )


@router.get("/contracts/employee/{employee_id}/active", response_model=Optional[ContractResponse])
async def get_active_contract(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the currently active contract for an employee"""
    contract = await ContractService.get_active_contract(db, employee_id)
    return contract


# ============= Extension Routes =============

@router.post("/extensions", response_model=ExtensionResponse)
async def create_extension(
    extension: ExtensionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a contract extension"""
    new_extension = await ContractService.create_extension(
        db=db,
        contract_id=extension.contract_id,
        employee_id=extension.employee_id,
        new_start_date=extension.new_start_date,
        new_end_date=extension.new_end_date,
        country_code=current_user.get("country_code", "AFG"),
        created_by=current_user["id"],
        new_monthly_salary=extension.new_monthly_salary,
        salary_change_reason=extension.salary_change_reason,
        new_position_title=extension.new_position_title,
        new_location=extension.new_location,
        terms_changes=extension.terms_changes,
        document_id=extension.document_id
    )
    
    return new_extension


@router.post("/extensions/{extension_id}/accept", response_model=ExtensionResponse)
async def accept_extension(
    extension_id: UUID,
    accept_data: ExtensionAccept,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Employee accepts a contract extension (digital signature)"""
    extension = await ContractService.accept_extension(
        db=db,
        extension_id=extension_id,
        employee_signature_ip=accept_data.employee_signature_ip
    )
    
    return extension


@router.get("/extensions/pending", response_model=ExtensionListResponse)
async def get_pending_extensions(
    employee_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending contract extensions"""
    # If no employee_id provided, use current user's employee_id
    if not employee_id:
        employee_id = current_user.get("employee_id")
    
    extensions = await ContractService.get_pending_extensions(
        db=db,
        employee_id=employee_id
    )
    
    return ExtensionListResponse(
        extensions=extensions,
        total=len(extensions)
    )


@router.get("/extensions/pending/notifications", response_model=List[PendingExtensionNotification])
async def get_extension_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending extension notifications for current user"""
    employee_id = current_user.get("employee_id")
    if not employee_id:
        return []
    
    extensions = await ContractService.get_pending_extensions(db=db, employee_id=employee_id)
    
    notifications = []
    for ext in extensions:
        days_until_expiry = None
        if ext.expires_at:
            days_until_expiry = (ext.expires_at - date.today()).days
        
        # Calculate salary change percent
        salary_change_percent = None
        if ext.new_monthly_salary and ext.contract:
            old_salary = ext.contract.monthly_salary
            if old_salary and old_salary > 0:
                salary_change_percent = ((ext.new_monthly_salary - old_salary) / old_salary) * 100
        
        notifications.append(PendingExtensionNotification(
            extension_id=ext.id,
            employee_id=ext.employee_id,
            employee_name=ext.employee.full_name if ext.employee else "",
            new_start_date=ext.new_start_date,
            new_end_date=ext.new_end_date,
            expires_at=ext.expires_at,
            days_until_expiry=days_until_expiry,
            new_monthly_salary=ext.new_monthly_salary,
            salary_change_percent=salary_change_percent
        ))
    
    return notifications


# ============= Resignation Routes =============

@router.post("/resignations", response_model=ResignationResponse)
async def submit_resignation(
    resignation: ResignationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Employee submits a resignation"""
    # Generate resignation number
    from datetime import datetime
    resignation_number = f"RES-{datetime.now().year}-{resignation.employee_id.hex[:8].upper()}"
    
    new_resignation = await ResignationService.submit_resignation(
        db=db,
        employee_id=resignation.employee_id,
        resignation_number=resignation_number,
        resignation_date=resignation.resignation_date,
        intended_last_working_day=resignation.intended_last_working_day,
        reason=resignation.reason,
        country_code=current_user.get("country_code", "AFG"),
        supervisor_id=resignation.supervisor_id,
        notice_period_days=resignation.notice_period_days,
        document_id=resignation.document_id
    )
    
    return new_resignation


@router.post("/resignations/{resignation_id}/approve/supervisor", response_model=ResignationResponse)
async def approve_resignation_supervisor(
    resignation_id: UUID,
    approval: ResignationApprove,
    approval_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supervisor approves a resignation through approval workflow"""
    from modules.employees.repositories import EmployeeRepository
    
    # Get supervisor employee ID from user
    employee_repo = EmployeeRepository(db)
    supervisor_employee = await employee_repo.get_by_user_id(current_user["id"])
    if not supervisor_employee:
        raise HTTPException(status_code=404, detail="Supervisor employee record not found")
    
    approval_uuid = UUID(approval_id) if approval_id else None
    
    resignation = await ResignationService.approve_by_supervisor(
        db=db,
        resignation_id=resignation_id,
        supervisor_id=supervisor_employee.id,
        comments=approval.comments,
        approval_id=approval_uuid
    )
    
    return resignation


@router.post("/resignations/{resignation_id}/approve/hr", response_model=ResignationResponse)
async def approve_resignation_hr(
    resignation_id: UUID,
    approval: ResignationApprove,
    approval_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """HR approves a resignation through approval workflow"""
    approval_uuid = UUID(approval_id) if approval_id else None
    
    resignation = await ResignationService.approve_by_hr(
        db=db,
        resignation_id=resignation_id,
        hr_user_id=current_user["id"],
        comments=approval.comments,
        approval_id=approval_uuid
    )
    
    return resignation


@router.post("/resignations/{resignation_id}/approve/ceo", response_model=ResignationResponse)
async def approve_resignation_ceo(
    resignation_id: UUID,
    approval: ResignationCEOApprove,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """CEO gives final approval for resignation"""
    resignation = await ResignationService.approve_by_ceo(
        db=db,
        resignation_id=resignation_id,
        ceo_user_id=current_user["id"],
        approved_last_working_day=approval.approved_last_working_day,
        comments=approval.comments
    )
    
    return resignation


@router.post("/resignations/{resignation_id}/complete", response_model=ResignationResponse)
async def complete_resignation(
    resignation_id: UUID,
    completion: ResignationComplete,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark resignation as completed"""
    resignation = await ResignationService.complete_resignation(
        db=db,
        resignation_id=resignation_id,
        exit_interview_date=completion.exit_interview_date
    )
    
    return resignation


@router.get("/resignations/pending", response_model=ResignationListResponse)
async def get_pending_resignations(
    for_hr: bool = False,
    for_ceo: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending resignations for approval"""
    # Determine if checking for supervisor
    for_supervisor_id = None
    if not for_hr and not for_ceo:
        # Check if user is a supervisor
        employee_id = current_user.get("employee_id")
        if employee_id:
            for_supervisor_id = employee_id
    
    resignations = await ResignationService.get_pending_resignations(
        db=db,
        for_supervisor_id=for_supervisor_id,
        for_hr=for_hr,
        for_ceo=for_ceo
    )
    
    return ResignationListResponse(
        resignations=resignations,
        total=len(resignations)
    )


@router.get("/resignations/pending/notifications", response_model=List[PendingResignationNotification])
async def get_resignation_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending resignation notifications based on user role"""
    # TODO: Check user permissions to determine what they should see
    # For now, get all pending resignations
    resignations = await ResignationService.get_pending_resignations(db=db)
    
    notifications = []
    for res in resignations:
        days_since = (date.today() - res.resignation_date).days
        
        # Determine who it's pending with
        pending_with = "Supervisor"
        if res.status == ResignationStatus.ACCEPTED_BY_SUPERVISOR:
            pending_with = "HR"
        elif res.status == ResignationStatus.ACCEPTED_BY_HR:
            pending_with = "CEO"
        
        notifications.append(PendingResignationNotification(
            resignation_id=res.id,
            employee_id=res.employee_id,
            employee_name=res.employee.full_name if res.employee else "",
            resignation_date=res.resignation_date,
            intended_last_working_day=res.intended_last_working_day,
            status=res.status,
            days_since_submission=days_since,
            pending_with=pending_with
        ))
    
    return notifications


@router.get("/resignations/employee/{employee_id}", response_model=ResignationListResponse)
async def get_employee_resignations(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all resignations for an employee"""
    resignations = await ResignationService.get_employee_resignations(
        db=db,
        employee_id=employee_id
    )
    
    return ResignationListResponse(
        resignations=resignations,
        total=len(resignations)
    )


# ============= Personal File Summary =============

@router.get("/summary/{employee_id}", response_model=PersonalFileSummary)
async def get_personal_file_summary(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a comprehensive summary of an employee's personal file"""
    from sqlalchemy import select
    from modules.employees.models import Employee
    
    # Get employee
    employee_query = select(Employee).where(Employee.id == employee_id)
    employee_result = await db.execute(employee_query)
    employee = employee_result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get documents
    documents = await DocumentService.get_employee_documents(db, employee_id)
    recent_documents = sorted(documents, key=lambda d: d.uploaded_at, reverse=True)[:5]
    
    # Get contracts
    contracts = await ContractService.get_employee_contracts(db, employee_id, include_inactive=False)
    current_contract = await ContractService.get_active_contract(db, employee_id)
    
    # Get extensions
    extensions = await ContractService.get_pending_extensions(db, employee_id)
    
    # Get resignations
    resignations = await ResignationService.get_employee_resignations(db, employee_id)
    
    # Calculate days until contract end
    days_until_contract_end = None
    contract_end_date = None
    if current_contract and current_contract.end_date:
        contract_end_date = current_contract.end_date
        days_until_contract_end = (contract_end_date - date.today()).days
    
    # Collect pending actions
    pending_actions = []
    if extensions:
        pending_actions.append(f"{len(extensions)} pending contract extension(s)")
    pending_resignations = [r for r in resignations if r.status != ResignationStatus.COMPLETED]
    if pending_resignations:
        pending_actions.append(f"{len(pending_resignations)} resignation(s) in progress")
    if days_until_contract_end and days_until_contract_end < 60:
        pending_actions.append(f"Contract ending in {days_until_contract_end} days")
    
    return PersonalFileSummary(
        employee_id=employee_id,
        employee_name=employee.full_name,
        employee_number=employee.employee_number,
        total_documents=len(documents),
        active_contracts=len(contracts),
        pending_extensions=len(extensions),
        total_resignations=len(resignations),
        current_contract=current_contract,
        current_contract_end_date=contract_end_date,
        days_until_contract_end=days_until_contract_end,
        recent_documents=recent_documents,
        pending_actions=pending_actions
    )


# ============= PDF Download Routes =============

@router.get("/contracts/{contract_id}/download-pdf")
async def download_contract_pdf(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download employment contract as PDF"""
    from fastapi.responses import StreamingResponse
    from core.pdf_generator import generate_employment_contract_pdf
    from sqlalchemy import select
    from .models import EmploymentContract
    from modules.employees.models import Employee
    
    # Get contract with employee
    query = select(EmploymentContract).where(EmploymentContract.id == contract_id)
    result = await db.execute(query)
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Get employee
    emp_query = select(Employee).where(Employee.id == contract.employee_id)
    emp_result = await db.execute(emp_query)
    employee = emp_result.scalar_one_or_none()
    
    # Convert to dict for PDF generator
    contract_dict = {
        'contract_number': contract.contract_number,
        'position_title': contract.position_title,
        'location': contract.location,
        'contract_type': contract.contract_type,
        'start_date': str(contract.start_date),
        'end_date': str(contract.end_date),
        'monthly_salary': float(contract.monthly_salary),
        'currency': contract.currency,
        'notice_period_days': int(contract.notice_period_days) if contract.notice_period_days else 30
    }
    
    employee_dict = {
        'full_name': employee.full_name if hasattr(employee, 'full_name') else f"{employee.first_name} {employee.last_name}",
        'first_name': employee.first_name,
        'last_name': employee.last_name,
        'employee_number': employee.employee_number,
        'work_email': employee.work_email
    }
    
    # Generate PDF
    pdf_buffer = generate_employment_contract_pdf(contract_dict, employee_dict)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contract_{contract.contract_number}.pdf"}
    )


@router.get("/resignations/{resignation_id}/download-pdf")
async def download_resignation_pdf(
    resignation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download resignation letter as PDF"""
    from fastapi.responses import StreamingResponse
    from core.pdf_generator import generate_resignation_letter_pdf
    from sqlalchemy import select
    from .models import Resignation
    from modules.employees.models import Employee
    
    # Get resignation with employee
    query = select(Resignation).where(Resignation.id == resignation_id)
    result = await db.execute(query)
    resignation = result.scalar_one_or_none()
    
    if not resignation:
        raise HTTPException(status_code=404, detail="Resignation not found")
    
    # Get employee
    emp_query = select(Employee).where(Employee.id == resignation.employee_id)
    emp_result = await db.execute(emp_query)
    employee = emp_result.scalar_one_or_none()
    
    # Convert to dict
    resignation_dict = {
        'resignation_number': resignation.resignation_number,
        'resignation_date': str(resignation.resignation_date),
        'intended_last_working_day': str(resignation.intended_last_working_day),
        'reason': resignation.reason,
        'notice_period_days': resignation.notice_period_days
    }
    
    employee_dict = {
        'full_name': employee.full_name if hasattr(employee, 'full_name') else f"{employee.first_name} {employee.last_name}",
        'employee_number': employee.employee_number,
        'work_email': employee.work_email
    }
    
    # Generate PDF
    pdf_buffer = generate_resignation_letter_pdf(resignation_dict, employee_dict)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resignation_{resignation.resignation_number}.pdf"}
    )
