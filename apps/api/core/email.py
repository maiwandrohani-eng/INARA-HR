"""
Email Notification Service
Handles sending email notifications for approval workflows and other events

Configuration Options:
1. SMTP (Gmail, Office365, etc.)
2. SendGrid API
3. AWS SES

To enable email notifications:
1. Set EMAIL_PROVIDER environment variable ('smtp', 'sendgrid', or 'aws_ses')
2. Set SEND_EMAILS=true
3. Configure provider-specific credentials

Example SMTP Setup (Gmail):
- SMTP_HOST=smtp.gmail.com
- SMTP_PORT=587
- SMTP_USERNAME=your-email@gmail.com
- SMTP_PASSWORD=your-app-password (generate at https://myaccount.google.com/apppasswords)
- FROM_EMAIL=noreply@inarahr.org

Example SendGrid Setup:
- SENDGRID_API_KEY=your-sendgrid-api-key
- FROM_EMAIL=noreply@inarahr.org

Example AWS SES Setup:
- AWS_REGION=us-east-1
- AWS_ACCESS_KEY=your-aws-access-key
- AWS_SECRET_KEY=your-aws-secret-key
- FROM_EMAIL=noreply@inarahr.org (must be verified in SES)
"""

from typing import List, Optional
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Uncomment when using SendGrid:
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# Uncomment when using AWS SES:
# import boto3

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration from environment variables"""
    
    PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # 'smtp', 'sendgrid', 'aws_ses'
    SEND_EMAILS = os.getenv("SEND_EMAILS", "false").lower() == "true"
    
    # SMTP Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # SendGrid Configuration
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    
    # AWS SES Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")
    
    # Sender Information
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@inarahr.org")
    FROM_NAME = os.getenv("FROM_NAME", "INARA HR System")
    
    # Application URLs
    APP_URL = os.getenv("APP_URL", "http://localhost:3000")


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.config = EmailConfig()
        if self.config.SEND_EMAILS:
            logger.info(f"Email service initialized with provider: {self.config.PROVIDER}")
        else:
            logger.info("Email service initialized in DISABLED mode (set SEND_EMAILS=true to enable)")
    
    def _send_smtp(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg['To'] = to_email
            
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                if self.config.SMTP_USE_TLS:
                    server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"SMTP email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMTP email: {str(e)}")
            return False
    
    def _send_sendgrid(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email via SendGrid"""
        try:
            # Uncomment when configured:
            # message = Mail(
            #     from_email=self.config.FROM_EMAIL,
            #     to_emails=to_email,
            #     subject=subject,
            #     html_content=html_body
            # )
            # sg = SendGridAPIClient(self.config.SENDGRID_API_KEY)
            # response = sg.send(message)
            # logger.info(f"SendGrid email sent to {to_email}: {subject}")
            # return True
            
            logger.info(f"[SENDGRID] Would send to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SendGrid email: {str(e)}")
            return False
    
    def _send_aws_ses(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email via AWS SES"""
        try:
            # Uncomment when configured:
            # client = boto3.client(
            #     'ses',
            #     region_name=self.config.AWS_REGION,
            #     aws_access_key_id=self.config.AWS_ACCESS_KEY,
            #     aws_secret_access_key=self.config.AWS_SECRET_KEY
            # )
            # response = client.send_email(
            #     Source=self.config.FROM_EMAIL,
            #     Destination={'ToAddresses': [to_email]},
            #     Message={
            #         'Subject': {'Data': subject},
            #         'Body': {'Html': {'Data': html_body}}
            #     }
            # )
            # logger.info(f"AWS SES email sent to {to_email}: {subject}")
            # return True
            
            logger.info(f"[AWS SES] Would send to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send AWS SES email: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """Internal method to send email via configured provider"""
        if not self.config.SEND_EMAILS:
            logger.info(f"[DISABLED] Would send to {to_email}: {subject}")
            return True
        
        if self.config.PROVIDER == "smtp":
            return self._send_smtp(to_email, subject, html_body, text_body)
        elif self.config.PROVIDER == "sendgrid":
            return self._send_sendgrid(to_email, subject, html_body)
        elif self.config.PROVIDER == "aws_ses":
            return self._send_aws_ses(to_email, subject, html_body)
        else:
            logger.error(f"Unknown email provider: {self.config.PROVIDER}")
            return False
    
    async def send_approval_request_notification(
        self,
        to_email: str,
        employee_name: str,
        request_type: str,
        request_details: dict
    ) -> bool:
        """
        Send notification when a new approval request is created
        
        Args:
            to_email: Supervisor's email
            employee_name: Name of employee who submitted request
            request_type: Type of request (leave, travel, etc.)
            request_details: Additional details about the request
        """
        subject = f"New {request_type.title()} Request Requires Your Approval"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">New Approval Request</h2>
                <p>Hello,</p>
                <p><strong>{employee_name}</strong> has submitted a <strong>{request_type}</strong> request that requires your approval.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Request Details:</h3>
                    {''.join([f"<p><strong>{k}:</strong> {v}</p>" for k, v in request_details.items()])}
                </div>
                
                <p>
                    <a href="{self.config.APP_URL}/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Review Request
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        New Approval Request
        
        {employee_name} has submitted a {request_type} request that requires your approval.
        
        Request Details:
        {chr(10).join([f"{k}: {v}" for k, v in request_details.items()])}
        
        Please log in to the INARA HRIS system to review and approve/reject this request.
        {self.config.APP_URL}/dashboard
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_approval_status_notification(
        self,
        to_email: str,
        request_type: str,
        status: str,
        comments: Optional[str] = None
    ) -> bool:
        """
        Send notification when an approval request is approved/rejected
        
        Args:
            to_email: Employee's email
            request_type: Type of request
            status: 'approved' or 'rejected'
            comments: Optional comments from approver
        """
        subject = f"Your {request_type.title()} Request Has Been {status.title()}"
        status_color = "#10b981" if status == "approved" else "#ef4444"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {status_color};">Request {status.title()}</h2>
                <p>Hello,</p>
                <p>Your <strong>{request_type}</strong> request has been <strong style="color: {status_color};">{status}</strong>.</p>
                
                {f'''<div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Approver Comments:</h3>
                    <p>{comments}</p>
                </div>''' if comments else ''}
                
                <p>
                    <a href="{self.config.APP_URL}/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        View Dashboard
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Request {status.title()}
        
        Your {request_type} request has been {status}.
        
        {f'Approver Comments: {comments}' if comments else ''}
        
        View your dashboard: {self.config.APP_URL}/dashboard
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_delegation_notification(
        self,
        to_email: str,
        supervisor_name: str,
        start_date: str,
        end_date: str
    ) -> bool:
        """
        Send notification when approval authority is delegated
        
        Args:
            to_email: Delegate's email
            supervisor_name: Name of supervisor delegating authority
            start_date: Delegation start date
            end_date: Delegation end date
        """
        subject = "You Have Been Delegated Approval Authority"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #7c3aed;">Approval Authority Delegated</h2>
                <p>Hello,</p>
                <p><strong>{supervisor_name}</strong> has delegated their approval authority to you.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Delegation Period:</h3>
                    <p><strong>From:</strong> {start_date}</p>
                    <p><strong>To:</strong> {end_date}</p>
                </div>
                
                <p>During this period, you will be responsible for approving requests that would normally go to {supervisor_name}.</p>
                
                <p>
                    <a href="{self.config.APP_URL}/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        View Pending Approvals
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Approval Authority Delegated
        
        {supervisor_name} has delegated their approval authority to you.
        
        Delegation Period:
        From: {start_date}
        To: {end_date}
        
        During this period, you will be responsible for approving requests that would normally go to {supervisor_name}.
        
        View pending approvals: {self.config.APP_URL}/dashboard
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_timesheet_reminder(
        self,
        to_emails: List[str],
        period_end: str
    ) -> bool:
        """
        Send reminder to submit timesheets
        
        Args:
            to_emails: List of employee emails
            period_end: End of timesheet period
        """
        subject = "Reminder: Submit Your Timesheet"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #f59e0b;">Timesheet Reminder</h2>
                <p>Hello,</p>
                <p>This is a friendly reminder to submit your timesheet for the period ending <strong>{period_end}</strong>.</p>
                
                <p>
                    <a href="{self.config.APP_URL}/timesheets" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Submit Timesheet
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Timesheet Reminder
        
        This is a friendly reminder to submit your timesheet for the period ending {period_end}.
        
        Submit your timesheet: {self.config.APP_URL}/timesheets
        """
        
        # Send to all recipients
        success_count = 0
        for email in to_emails:
            if self._send_email(email, subject, html_body, text_body):
                success_count += 1
        
        logger.info(f"Sent timesheet reminders to {success_count}/{len(to_emails)} recipients")
        return success_count > 0

    async def send_resignation_notification(
        self,
        to_email: str,
        employee_name: str,
        resignation_date: str,
        last_working_day: str,
        reason: str
    ) -> bool:
        """
        Send notification when an employee submits a resignation
        
        Args:
            to_email: Supervisor/HR email
            employee_name: Name of resigning employee
            resignation_date: Date of resignation submission
            last_working_day: Proposed last working day
            reason: Reason for resignation
        """
        subject = f"Resignation Submitted - {employee_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ef4444;">Resignation Notice</h2>
                <p>Hello,</p>
                <p><strong>{employee_name}</strong> has submitted their resignation.</p>
                
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #991b1b;">Resignation Details:</h3>
                    <p><strong>Resignation Date:</strong> {resignation_date}</p>
                    <p><strong>Intended Last Working Day:</strong> {last_working_day}</p>
                    <p><strong>Reason:</strong> {reason}</p>
                </div>
                
                <p>Please review and approve this resignation in the HR system.</p>
                
                <p>
                    <a href="{self.config.APP_URL}/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #ef4444; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Review Resignation
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Resignation Notice
        
        {employee_name} has submitted their resignation.
        
        Resignation Details:
        Resignation Date: {resignation_date}
        Intended Last Working Day: {last_working_day}
        Reason: {reason}
        
        Please review and approve this resignation in the HR system.
        {self.config.APP_URL}/dashboard
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_contract_extension_notification(
        self,
        to_email: str,
        employee_name: str,
        new_start_date: str,
        new_end_date: str,
        changes: dict
    ) -> bool:
        """
        Send notification when a contract extension is created
        
        Args:
            to_email: Employee's email
            employee_name: Name of employee
            new_start_date: Extension start date
            new_end_date: Extension end date
            changes: Dictionary of changes (salary, position, etc.)
        """
        subject = f"Contract Extension Offer - Action Required"
        
        changes_html = ""
        if changes:
            changes_html = "<h3 style='margin-top: 0;'>Changes to Terms:</h3>"
            for key, value in changes.items():
                changes_html += f"<p><strong>{key}:</strong> {value}</p>"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Contract Extension Offer</h2>
                <p>Dear {employee_name},</p>
                <p>We are pleased to offer you a contract extension with the following terms:</p>
                
                <div style="background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Extension Period:</h3>
                    <p><strong>From:</strong> {new_start_date}</p>
                    <p><strong>To:</strong> {new_end_date}</p>
                    {changes_html}
                </div>
                
                <p><strong>Important:</strong> Please review and accept this extension within 7 days before the start date.</p>
                
                <p>
                    <a href="{self.config.APP_URL}/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #10b981; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Review & Accept Extension
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        changes_text = ""
        if changes:
            changes_text = "\nChanges to Terms:\n" + "\n".join([f"{k}: {v}" for k, v in changes.items()])
        
        text_body = f"""
        Contract Extension Offer
        
        Dear {employee_name},
        
        We are pleased to offer you a contract extension with the following terms:
        
        Extension Period:
        From: {new_start_date}
        To: {new_end_date}
        {changes_text}
        
        Important: Please review and accept this extension within 7 days before the start date.
        
        Review and accept: {self.config.APP_URL}/dashboard
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: User's email
            user_name: User's full name
            verification_token: Email verification token
        """
        subject = "Verify Your Email Address"
        
        verification_url = f"{self.config.APP_URL}/verify-email?token={verification_token}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Verify Your Email Address</h2>
                <p>Hello {user_name},</p>
                <p>Thank you for registering with INARA HRIS. Please verify your email address by clicking the button below:</p>
                
                <p>
                    <a href="{verification_url}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Verify Email Address
                    </a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #6b7280; word-break: break-all;">{verification_url}</p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This verification link will expire in 7 days. If you didn't create an account, please ignore this email.
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Verify Your Email Address
        
        Hello {user_name},
        
        Thank you for registering with INARA HRIS. Please verify your email address by visiting:
        
        {verification_url}
        
        This verification link will expire in 7 days. If you didn't create an account, please ignore this email.
        
        This is an automated notification from INARA HR System.
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: User's email
            user_name: User's full name
            reset_token: Password reset token
        """
        subject = "Reset Your Password"
        
        reset_url = f"{self.config.APP_URL}/reset-password?token={reset_token}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ef4444;">Reset Your Password</h2>
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <p>
                    <a href="{reset_url}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #ef4444; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Reset Password
                    </a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #6b7280; word-break: break-all;">{reset_url}</p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This password reset link will expire in 24 hours. If you didn't request a password reset, please ignore this email.
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Reset Your Password
        
        Hello {user_name},
        
        We received a request to reset your password. Visit the link below to create a new password:
        
        {reset_url}
        
        This password reset link will expire in 24 hours. If you didn't request a password reset, please ignore this email.
        
        This is an automated notification from INARA HR System.
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_password_reset_confirmation(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Send password reset confirmation email
        
        Args:
            to_email: User's email
            user_name: User's full name
        """
        subject = "Your Password Has Been Reset"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10b981;">Password Reset Successful</h2>
                <p>Hello {user_name},</p>
                <p>Your password has been successfully reset.</p>
                
                <p>If you didn't make this change, please contact your system administrator immediately.</p>
                
                <p>
                    <a href="{self.config.APP_URL}/login" 
                       style="display: inline-block; padding: 12px 24px; background-color: #2563eb; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Log In
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Successful
        
        Hello {user_name},
        
        Your password has been successfully reset.
        
        If you didn't make this change, please contact your system administrator immediately.
        
        Log in: {self.config.APP_URL}/login
        
        This is an automated notification from INARA HR System.
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    async def send_password_change_notification(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Send password change notification email
        
        Args:
            to_email: User's email
            user_name: User's full name
        """
        subject = "Your Password Has Been Changed"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10b981;">Password Changed</h2>
                <p>Hello {user_name},</p>
                <p>Your password has been successfully changed.</p>
                
                <p>If you didn't make this change, please contact your system administrator immediately.</p>
                
                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    This is an automated notification from INARA HR System.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Changed
        
        Hello {user_name},
        
        Your password has been successfully changed.
        
        If you didn't make this change, please contact your system administrator immediately.
        
        This is an automated notification from INARA HR System.
        """
        
        return self._send_email(to_email, subject, html_body, text_body)


# Create singleton instance for easy importing
email_service = EmailService()
