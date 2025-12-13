"""
Employee files services for document management, contracts, and resignations
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from .models import (
    PersonalFileDocument, 
    EmploymentContract, 
    ContractExtension, 
    Resignation,
    DocumentCategory,
    ContractStatus,
    ExtensionStatus,
    ResignationStatus
)
from core.exceptions import NotFoundException, BadRequestException


class DocumentService:
    """Service for managing employee documents"""
    
    @staticmethod
    async def create_document(
        db: AsyncSession,
        employee_id: UUID,
        category: DocumentCategory,
        title: str,
        file_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        uploaded_by: UUID,
        country_code: str,
        description: Optional[str] = None,
        is_confidential: bool = False,
        expiry_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> PersonalFileDocument:
        """Create a new employee document"""
        document = PersonalFileDocument(
            employee_id=employee_id,
            category=category,
            title=title,
            description=description,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            is_confidential=is_confidential,
            expiry_date=expiry_date,
            notes=notes,
            country_code=country_code
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document
    
    @staticmethod
    async def get_employee_documents(
        db: AsyncSession,
        employee_id: UUID,
        category: Optional[DocumentCategory] = None,
        include_deleted: bool = False
    ) -> List[PersonalFileDocument]:
        """Get all documents for an employee"""
        query = select(PersonalFileDocument).where(PersonalFileDocument.employee_id == employee_id)
        
        if category:
            query = query.where(PersonalFileDocument.category == category)
        
        if not include_deleted:
            query = query.where(PersonalFileDocument.deleted_at.is_(None))
        
        query = query.options(
            selectinload(PersonalFileDocument.employee),
            selectinload(PersonalFileDocument.uploader)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: UUID) -> PersonalFileDocument:
        """Get a specific document by ID"""
        query = select(PersonalFileDocument).where(PersonalFileDocument.id == document_id).options(
            selectinload(PersonalFileDocument.employee),
            selectinload(PersonalFileDocument.uploader)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise NotFoundException("Document not found")
        
        return document
    
    @staticmethod
    async def soft_delete_document(db: AsyncSession, document_id: UUID) -> PersonalFileDocument:
        """Soft delete a document"""
        document = await DocumentService.get_document_by_id(db, document_id)
        document.deleted_at = datetime.utcnow()
        await db.commit()
        await db.refresh(document)
        return document


class ContractService:
    """Service for managing employment contracts and extensions"""
    
    @staticmethod
    async def create_contract(
        db: AsyncSession,
        employee_id: UUID,
        contract_number: str,
        position_title: str,
        location: str,
        contract_type: str,
        start_date: date,
        end_date: date,
        monthly_salary: float,
        currency: str,
        country_code: str,
        created_by: UUID,
        document_id: Optional[UUID] = None,
        notice_period_days: int = 30,
        signed_date: Optional[date] = None
    ) -> EmploymentContract:
        """Create a new employment contract"""
        contract = EmploymentContract(
            employee_id=employee_id,
            contract_number=contract_number,
            position_title=position_title,
            location=location,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            monthly_salary=monthly_salary,
            currency=currency,
            notice_period_days=notice_period_days,
            signed_date=signed_date,
            document_id=document_id,
            status=ContractStatus.ACTIVE if signed_date else ContractStatus.DRAFT,
            country_code=country_code,
            created_by=created_by
        )
        db.add(contract)
        await db.commit()
        await db.refresh(contract)
        return contract
    
    @staticmethod
    async def get_employee_contracts(
        db: AsyncSession,
        employee_id: UUID,
        include_inactive: bool = False
    ) -> List[EmploymentContract]:
        """Get all contracts for an employee"""
        query = select(EmploymentContract).where(EmploymentContract.employee_id == employee_id)
        
        if not include_inactive:
            query = query.where(
                or_(
                    EmploymentContract.status == ContractStatus.ACTIVE,
                    EmploymentContract.status == ContractStatus.EXTENDED
                )
            )
        
        query = query.options(
            selectinload(EmploymentContract.employee),
            selectinload(EmploymentContract.document),
            selectinload(EmploymentContract.extensions)
        ).order_by(EmploymentContract.start_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_active_contract(db: AsyncSession, employee_id: UUID) -> Optional[EmploymentContract]:
        """Get the currently active contract for an employee"""
        query = select(EmploymentContract).where(
            and_(
                EmploymentContract.employee_id == employee_id,
                or_(
                    EmploymentContract.status == ContractStatus.ACTIVE,
                    EmploymentContract.status == ContractStatus.EXTENDED
                ),
                EmploymentContract.start_date <= date.today(),
                or_(
                    EmploymentContract.end_date >= date.today(),
                    EmploymentContract.end_date.is_(None)
                )
            )
        ).options(
            selectinload(EmploymentContract.employee),
            selectinload(EmploymentContract.extensions)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_extension(
        db: AsyncSession,
        contract_id: UUID,
        employee_id: UUID,
        new_start_date: date,
        new_end_date: date,
        country_code: str,
        created_by: UUID,
        extension_number: Optional[int] = None,
        new_monthly_salary: Optional[float] = None,
        salary_change_reason: Optional[str] = None,
        new_position_title: Optional[str] = None,
        new_location: Optional[str] = None,
        terms_changes: Optional[str] = None,
        document_id: Optional[UUID] = None
    ) -> ContractExtension:
        """Create a contract extension"""
        # Get the contract
        contract_query = select(EmploymentContract).where(EmploymentContract.id == contract_id)
        result = await db.execute(contract_query)
        contract = result.scalar_one_or_none()
        
        if not contract:
            raise NotFoundException("Contract not found")
        
        # Calculate extension number if not provided
        if extension_number is None:
            extensions_query = select(ContractExtension).where(
                ContractExtension.contract_id == contract_id
            )
            extensions_result = await db.execute(extensions_query)
            existing_extensions = extensions_result.scalars().all()
            extension_number = len(existing_extensions) + 1
        
        # Calculate expiry date (e.g., 7 days before new start date)
        from datetime import timedelta
        expires_at = new_start_date - timedelta(days=7)
        
        extension = ContractExtension(
            contract_id=contract_id,
            employee_id=employee_id,
            extension_number=extension_number,
            new_start_date=new_start_date,
            new_end_date=new_end_date,
            new_monthly_salary=new_monthly_salary,
            salary_change_reason=salary_change_reason,
            new_position_title=new_position_title,
            new_location=new_location,
            terms_changes=terms_changes,
            document_id=document_id,
            status=ExtensionStatus.PENDING,
            expires_at=expires_at,
            country_code=country_code,
            created_by=created_by
        )
        db.add(extension)
        await db.commit()
        await db.refresh(extension)
        return extension
    
    @staticmethod
    async def accept_extension(
        db: AsyncSession,
        extension_id: UUID,
        employee_signature_ip: str
    ) -> ContractExtension:
        """Employee accepts a contract extension (digital signature)"""
        query = select(ContractExtension).where(ContractExtension.id == extension_id)
        result = await db.execute(query)
        extension = result.scalar_one_or_none()
        
        if not extension:
            raise NotFoundException("Extension not found")
        
        if extension.status != ExtensionStatus.PENDING:
            raise BadRequestException("Extension is not pending")
        
        if extension.expires_at and extension.expires_at < date.today():
            extension.status = ExtensionStatus.EXPIRED
            await db.commit()
            raise BadRequestException("Extension has expired")
        
        # Record acceptance
        extension.employee_accepted_at = datetime.utcnow()
        extension.employee_signature_ip = employee_signature_ip
        extension.status = ExtensionStatus.ACCEPTED
        
        # Update the contract
        contract_query = select(EmploymentContract).where(
            EmploymentContract.id == extension.contract_id
        )
        contract_result = await db.execute(contract_query)
        contract = contract_result.scalar_one_or_none()
        
        if contract:
            contract.end_date = extension.new_end_date
            if extension.new_monthly_salary:
                contract.monthly_salary = extension.new_monthly_salary
            if extension.new_position_title:
                contract.position_title = extension.new_position_title
            if extension.new_location:
                contract.location = extension.new_location
            contract.status = ContractStatus.EXTENDED
            
            # Also update the employee record with new details
            from modules.employees.models import Employee
            employee_query = select(Employee).where(Employee.id == extension.employee_id)
            employee_result = await db.execute(employee_query)
            employee = employee_result.scalar_one_or_none()
            
            if employee:
                if extension.new_location:
                    employee.work_location = extension.new_location
                # Note: position and salary updates would need department/position lookup
                # For now, we update work_location as it's a direct field
        
        await db.commit()
        await db.refresh(extension)
        return extension
    
    @staticmethod
    async def get_pending_extensions(
        db: AsyncSession,
        employee_id: Optional[UUID] = None
    ) -> List[ContractExtension]:
        """Get pending contract extensions"""
        query = select(ContractExtension).where(
            ContractExtension.status == ExtensionStatus.PENDING
        )
        
        if employee_id:
            query = query.where(ContractExtension.employee_id == employee_id)
        
        query = query.options(
            selectinload(ContractExtension.employee),
            selectinload(ContractExtension.contract),
            selectinload(ContractExtension.document)
        )
        
        result = await db.execute(query)
        return result.scalars().all()


class ResignationService:
    """Service for managing employee resignations"""
    
    @staticmethod
    async def submit_resignation(
        db: AsyncSession,
        employee_id: UUID,
        resignation_number: str,
        resignation_date: date,
        intended_last_working_day: date,
        reason: str,
        country_code: str,
        supervisor_id: Optional[UUID] = None,
        notice_period_days: int = 30,
        document_id: Optional[UUID] = None
    ) -> Resignation:
        """Employee submits a resignation"""
        resignation = Resignation(
            employee_id=employee_id,
            resignation_number=resignation_number,
            resignation_date=resignation_date,
            intended_last_working_day=intended_last_working_day,
            reason=reason,
            supervisor_id=supervisor_id,
            notice_period_days=notice_period_days,
            document_id=document_id,
            status=ResignationStatus.SUBMITTED,
            country_code=country_code
        )
        db.add(resignation)
        await db.commit()
        await db.refresh(resignation)
        return resignation
    
    @staticmethod
    async def approve_by_supervisor(
        db: AsyncSession,
        resignation_id: UUID,
        supervisor_id: UUID,
        comments: Optional[str] = None
    ) -> Resignation:
        """Supervisor approves a resignation"""
        query = select(Resignation).where(Resignation.id == resignation_id)
        result = await db.execute(query)
        resignation = result.scalar_one_or_none()
        
        if not resignation:
            raise NotFoundException("Resignation not found")
        
        if resignation.status != ResignationStatus.SUBMITTED:
            raise BadRequestException("Resignation is not in submitted status")
        
        resignation.supervisor_accepted_at = datetime.utcnow()
        resignation.supervisor_comments = comments
        resignation.status = ResignationStatus.ACCEPTED_BY_SUPERVISOR
        
        await db.commit()
        await db.refresh(resignation)
        return resignation
    
    @staticmethod
    async def approve_by_hr(
        db: AsyncSession,
        resignation_id: UUID,
        hr_user_id: UUID,
        comments: Optional[str] = None
    ) -> Resignation:
        """HR approves a resignation"""
        query = select(Resignation).where(Resignation.id == resignation_id)
        result = await db.execute(query)
        resignation = result.scalar_one_or_none()
        
        if not resignation:
            raise NotFoundException("Resignation not found")
        
        if resignation.status != ResignationStatus.ACCEPTED_BY_SUPERVISOR:
            raise BadRequestException("Resignation must be approved by supervisor first")
        
        resignation.hr_accepted_by = hr_user_id
        resignation.hr_accepted_at = datetime.utcnow()
        resignation.hr_comments = comments
        resignation.status = ResignationStatus.ACCEPTED_BY_HR
        
        await db.commit()
        await db.refresh(resignation)
        return resignation
    
    @staticmethod
    async def approve_by_ceo(
        db: AsyncSession,
        resignation_id: UUID,
        ceo_user_id: UUID,
        approved_last_working_day: date,
        comments: Optional[str] = None
    ) -> Resignation:
        """CEO gives final approval for resignation"""
        query = select(Resignation).where(Resignation.id == resignation_id)
        result = await db.execute(query)
        resignation = result.scalar_one_or_none()
        
        if not resignation:
            raise NotFoundException("Resignation not found")
        
        if resignation.status != ResignationStatus.ACCEPTED_BY_HR:
            raise BadRequestException("Resignation must be approved by HR first")
        
        resignation.ceo_accepted_by = ceo_user_id
        resignation.ceo_accepted_at = datetime.utcnow()
        resignation.ceo_comments = comments
        resignation.approved_last_working_day = approved_last_working_day
        resignation.status = ResignationStatus.ACCEPTED_BY_CEO
        
        await db.commit()
        await db.refresh(resignation)
        return resignation
    
    @staticmethod
    async def complete_resignation(
        db: AsyncSession,
        resignation_id: UUID,
        exit_interview_date: Optional[date] = None
    ) -> Resignation:
        """Mark resignation as completed"""
        query = select(Resignation).where(Resignation.id == resignation_id)
        result = await db.execute(query)
        resignation = result.scalar_one_or_none()
        
        if not resignation:
            raise NotFoundException("Resignation not found")
        
        resignation.exit_interview_completed = True
        resignation.exit_interview_date = exit_interview_date or date.today()
        resignation.status = ResignationStatus.COMPLETED
        
        await db.commit()
        await db.refresh(resignation)
        return resignation
    
    @staticmethod
    async def get_pending_resignations(
        db: AsyncSession,
        for_supervisor_id: Optional[UUID] = None,
        for_hr: bool = False,
        for_ceo: bool = False
    ) -> List[Resignation]:
        """Get resignations pending approval"""
        query = select(Resignation)
        
        if for_supervisor_id:
            query = query.where(
                and_(
                    Resignation.supervisor_id == for_supervisor_id,
                    Resignation.status == ResignationStatus.SUBMITTED
                )
            )
        elif for_hr:
            query = query.where(Resignation.status == ResignationStatus.ACCEPTED_BY_SUPERVISOR)
        elif for_ceo:
            query = query.where(Resignation.status == ResignationStatus.ACCEPTED_BY_HR)
        else:
            query = query.where(
                Resignation.status.in_([
                    ResignationStatus.SUBMITTED,
                    ResignationStatus.ACCEPTED_BY_SUPERVISOR,
                    ResignationStatus.ACCEPTED_BY_HR
                ])
            )
        
        query = query.options(
            selectinload(Resignation.employee),
            selectinload(Resignation.supervisor),
            selectinload(Resignation.document)
        ).order_by(Resignation.resignation_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_employee_resignations(
        db: AsyncSession,
        employee_id: UUID
    ) -> List[Resignation]:
        """Get all resignations for an employee"""
        query = select(Resignation).where(
            Resignation.employee_id == employee_id
        ).options(
            selectinload(Resignation.supervisor),
            selectinload(Resignation.hr_user),
            selectinload(Resignation.ceo_user),
            selectinload(Resignation.document)
        ).order_by(Resignation.resignation_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
