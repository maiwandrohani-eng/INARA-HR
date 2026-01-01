"""Safeguarding Module - Services"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, date
from typing import List, Optional
import uuid
import logging

from modules.safeguarding.models import SafeguardingCase
from modules.safeguarding.schemas import SafeguardingCaseCreate, SafeguardingCaseUpdate
from modules.auth.models import User
from core.email import EmailService
from core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class SafeguardingService:
    """Service for handling safeguarding cases"""
    
    @staticmethod
    async def create_case(
        session: AsyncSession,
        case_data: SafeguardingCaseCreate,
        reporter_id: str,
        country_code: str
    ) -> SafeguardingCase:
        """Create a new safeguarding case and notify admins/HR"""
        
        # Generate unique case number
        year = datetime.utcnow().year
        result = await session.execute(
            select(SafeguardingCase).where(
                SafeguardingCase.country_code == country_code
            ).order_by(SafeguardingCase.created_at.desc())
        )
        last_case = result.scalars().first()
        
        if last_case and last_case.case_number:
            try:
                last_num = int(last_case.case_number.split('-')[-1])
                case_num = last_num + 1
            except (ValueError, IndexError):
                case_num = 1
        else:
            case_num = 1
        
        case_number = f"SG-{year}-{case_num:04d}"
        
        # Determine case_type and location (support both old and new field names)
        final_case_type = case_data.case_type or case_data.incident_type or 'safeguarding'
        final_location = case_data.location or case_data.incident_location
        
        # Create case
        new_case = SafeguardingCase(
            id=uuid.uuid4(),
            case_number=case_number,
            case_type=final_case_type,
            severity=case_data.severity,
            reported_date=date.today(),
            incident_date=case_data.incident_date,
            description=case_data.description,
            location=final_location,
            involved_persons=case_data.involved_persons,
            witnesses=case_data.witnesses,
            reporter_id=None if case_data.is_anonymous else uuid.UUID(reporter_id),
            subject_id=uuid.UUID(case_data.subject_id) if case_data.subject_id else None,
            investigation_status="pending",
            status="open",
            actions_taken=case_data.action_taken,
            confidentiality_level="high",
            country_code=country_code,
            created_by=uuid.UUID(reporter_id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_case)
        await session.flush()
        
        # Create approval requests for HR Manager and CEO (both can review)
        from core.role_helpers import get_hr_manager, get_ceo
        from modules.approvals.services import ApprovalService
        from modules.approvals.schemas import ApprovalRequestCreate
        from modules.approvals.models import ApprovalType
        from modules.employees.models import Employee
        from modules.employees.repositories import EmployeeRepository
        
        # Get reporter employee
        employee_repo = EmployeeRepository(session)
        reporter_employee = None
        if reporter_id:
            reporter_employee = await employee_repo.get_by_user_id(reporter_id)
        
        hr_manager = await get_hr_manager(session, country_code)
        ceo = await get_ceo(session, country_code)
        
        if hr_manager or ceo:
            approval_service = ApprovalService(session)
            approval_data = ApprovalRequestCreate(
                request_type=ApprovalType.SAFEGUARDING,
                request_id=new_case.id,
                employee_id=reporter_employee.id if reporter_employee else (hr_manager.id if hr_manager else ceo.id),
                comments=f"Safeguarding case: {case_number} - {final_case_type}"
            )
            
            # Create approval for HR Manager (if exists)
            if hr_manager:
                await approval_service.create_approval_request(
                    approval_data,
                    hr_manager.id,
                    country_code=country_code,
                    approval_level=1,
                    is_final_approval=False
                )
            
            # Create approval for CEO (if exists) - can review independently
            if ceo:
                await approval_service.create_approval_request(
                    approval_data,
                    ceo.id,
                    country_code=country_code,
                    approval_level=1,
                    is_final_approval=True  # CEO can finalize
                )
        
        # Send notifications to admins and HR managers
        await SafeguardingService._notify_admins(session, new_case, country_code)
        
        await session.commit()
        await session.refresh(new_case)
        
        logger.info(f"Safeguarding case {case_number} created by user {reporter_id}")
        
        return new_case
    
    @staticmethod
    async def _notify_admins(session: AsyncSession, case: SafeguardingCase, country_code: str):
        """Send email notifications to admins and HR managers"""
        
        try:
            # Find all admins and HR managers
            result = await session.execute(
                select(User).where(
                    and_(
                        User.is_active == True,
                        User.country_code == country_code,
                        or_(
                            User.role.in_(['super_admin', 'admin', 'hr_manager']),
                        )
                    )
                )
            )
            recipients = result.scalars().all()
            
            if not recipients:
                logger.warning(f"No admin/HR users found to notify for case {case.case_number}")
                return
            
            email_service = EmailService()
            
            for user in recipients:
                if user.email:
                    subject = f"⚠️ New Safeguarding Report: {case.case_number}"
                    
                    html_body = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <div style="background-color: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                                <h2 style="margin: 0;">⚠️ New Safeguarding Report</h2>
                            </div>
                            
                            <div style="background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; border-top: none;">
                                <p>A new safeguarding case has been reported and requires your immediate attention.</p>
                                
                                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                                    <h3 style="color: #dc2626; margin-top: 0;">Case Details</h3>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Case Number:</td>
                                            <td style="padding: 8px 0;">{case.case_number}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; font-weight: bold;">Type:</td>
                                            <td style="padding: 8px 0;">{case.case_type.upper()}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; font-weight: bold;">Severity:</td>
                                            <td style="padding: 8px 0;">
                                                <span style="background-color: {'#dc2626' if case.severity == 'critical' else '#f59e0b' if case.severity == 'high' else '#10b981'}; 
                                                             color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">
                                                    {case.severity.upper()}
                                                </span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; font-weight: bold;">Reported Date:</td>
                                            <td style="padding: 8px 0;">{case.reported_date.strftime('%B %d, %Y')}</td>
                                        </tr>
                                        {f'<tr><td style="padding: 8px 0; font-weight: bold;">Incident Date:</td><td style="padding: 8px 0;">{case.incident_date.strftime("%B %d, %Y")}</td></tr>' if case.incident_date else ''}
                                        {f'<tr><td style="padding: 8px 0; font-weight: bold;">Location:</td><td style="padding: 8px 0;">{case.location}</td></tr>' if case.location else ''}
                                    </table>
                                </div>
                                
                                <div style="background-color: #fef2f2; padding: 15px; border-left: 4px solid #dc2626; border-radius: 4px; margin: 15px 0;">
                                    <p style="margin: 0; font-weight: bold; color: #dc2626;">⚠️ This case requires urgent attention</p>
                                    <p style="margin: 10px 0 0 0;">Please review this case immediately and assign an investigator if necessary.</p>
                                </div>
                                
                                <div style="text-align: center; margin: 25px 0;">
                                    <a href="{email_service.config.APP_URL}/safeguarding/cases/{case.id}" 
                                       style="background-color: #dc2626; color: white; padding: 12px 30px; text-decoration: none; 
                                              border-radius: 6px; font-weight: bold; display: inline-block;">
                                        View Case Details
                                    </a>
                                </div>
                                
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280;">
                                    <p style="margin: 5px 0;"><strong>Confidentiality Notice:</strong> This case contains sensitive information. 
                                    Handle with strict confidentiality and in accordance with safeguarding policies.</p>
                                </div>
                            </div>
                            
                            <div style="text-align: center; padding: 15px; font-size: 12px; color: #6b7280;">
                                <p>This is an automated notification from INARA HR System</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_body = f"""
New Safeguarding Report

Case Number: {case.case_number}
Type: {case.case_type.upper()}
Severity: {case.severity.upper()}
Reported Date: {case.reported_date.strftime('%B %d, %Y')}
{'Incident Date: ' + case.incident_date.strftime('%B %d, %Y') if case.incident_date else ''}
{'Location: ' + case.location if case.location else ''}

This case requires urgent attention. Please log in to the INARA HR System to review the full details.

View case: {email_service.config.APP_URL}/safeguarding/cases/{case.id}

Confidentiality Notice: Handle this case with strict confidentiality in accordance with safeguarding policies.
                    """
                    
                    email_service._send_email(user.email, subject, html_body, text_body)
                    logger.info(f"Notification sent to {user.email} for case {case.case_number}")
        
        except Exception as e:
            logger.error(f"Error sending notifications for case {case.case_number}: {str(e)}")
    
    @staticmethod
    async def get_all_cases(
        session: AsyncSession,
        country_code: str,
        status: Optional[str] = None
    ) -> List[SafeguardingCase]:
        """Get all safeguarding cases (admin/HR only)"""
        
        conditions = [SafeguardingCase.country_code == country_code]
        if status:
            conditions.append(SafeguardingCase.status == status)
        
        result = await session.execute(
            select(SafeguardingCase)
            .where(and_(*conditions))
            .order_by(SafeguardingCase.created_at.desc())
        )
        
        return result.scalars().all()
    
    @staticmethod
    async def get_case_by_id(
        session: AsyncSession,
        case_id: str
    ) -> SafeguardingCase:
        """Get a specific case by ID"""
        
        result = await session.execute(
            select(SafeguardingCase).where(SafeguardingCase.id == uuid.UUID(case_id))
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise NotFoundException(f"Case with ID {case_id} not found")
        
        return case
    
    @staticmethod
    async def update_case(
        session: AsyncSession,
        case_id: str,
        update_data: SafeguardingCaseUpdate,
        user_id: str
    ) -> SafeguardingCase:
        """Update a safeguarding case"""
        
        case = await SafeguardingService.get_case_by_id(session, case_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if value is not None:
                if field == 'investigator_id':
                    setattr(case, field, uuid.UUID(value) if value else None)
                else:
                    setattr(case, field, value)
        
        case.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(case)
        
        logger.info(f"Case {case.case_number} updated by user {user_id}")
        
        return case
