"""
Authentication Module - Service Layer
Business logic for authentication operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError
import logging

from modules.auth.repositories import UserRepository, RoleRepository, LoginAttemptRepository
from modules.auth.schemas import UserCreate, LoginRequest
from core.security import verify_password, create_access_token, create_refresh_token, hash_password, decode_token
from core.exceptions import InvalidCredentialsException, AlreadyExistsException, NotFoundException, UnauthorizedException, BadRequestException
from core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.login_attempt_repo = LoginAttemptRepository(db)
    
    async def login(
        self,
        credentials: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Authenticate user and return access and refresh tokens
        
        Args:
            credentials: Login credentials
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (access_token, refresh_token)
        
        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        # Get user by email (include employee relationship for login)
        user = await self.user_repo.get_by_email(credentials.email, include_employee=True)
        
        # Verify user exists and password is correct
        if not user or not verify_password(credentials.password, user.hashed_password):
            # Log failed attempt
            await self.login_attempt_repo.create({
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": False,
                "failure_reason": "Invalid credentials"
            })
            
            # If user exists, increment failed login attempts
            if user:
                failed_attempts = int(user.failed_login_attempts or "0") + 1
                update_data = {"failed_login_attempts": str(failed_attempts)}
                
                # Lock account after 5 failed attempts for 30 minutes
                if failed_attempts >= 5:
                    update_data["locked_until"] = datetime.utcnow() + timedelta(minutes=30)
                    logger.warning(f"Account {user.email} locked after {failed_attempts} failed attempts")
                
                await self.user_repo.update(user.id, update_data)
                await self.db.commit()
            
            raise InvalidCredentialsException()
        
        # Check if user is active (do this early before any DB commits)
        if not user.is_active:
            await self.login_attempt_repo.create({
                "user_id": user.id,
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": False,
                "failure_reason": "User inactive"
            })
            raise InvalidCredentialsException(message="User account is inactive")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            await self.login_attempt_repo.create({
                "user_id": user.id,
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": False,
                "failure_reason": "Account locked"
            })
            raise InvalidCredentialsException(message="Account is temporarily locked. Please try again later.")
        
        # Check if email verification is required (only for non-superusers)
        if not user.is_superuser and not user.is_verified:
            await self.login_attempt_repo.create({
                "user_id": user.id,
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": False,
                "failure_reason": "Email not verified"
            })
            raise InvalidCredentialsException(message="Please verify your email before logging in")
        
        # Generate tokens first (before committing, to avoid blocking)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "permissions": [
                perm.name
                for role in user.roles
                for perm in role.permissions
            ],
            "employee_id": str(user.employee.id) if user.employee else None,
            "country_code": user.country_code
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Reset failed login attempts and update last login in one operation
        update_data = {
            "last_login": datetime.utcnow()
        }
        if int(user.failed_login_attempts or "0") > 0:
            update_data["failed_login_attempts"] = "0"
            update_data["locked_until"] = None
        
        # Update user in background (don't block login)
        try:
            await self.user_repo.update(user.id, update_data)
            
            # Log successful attempt (non-blocking)
            await self.login_attempt_repo.create({
                "user_id": user.id,
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": True
            })
            
            # Single commit for all updates
            await self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to update login tracking: {str(e)}")
            # Don't fail login if tracking fails
            try:
                await self.db.rollback()
            except:
                pass
        
        logger.info(f"User {user.email} logged in successfully")
        
        return access_token, refresh_token
    
    async def register(self, user_data: UserCreate) -> dict:
        """
        Register a new user
        
        Args:
            user_data: User registration data
        
        Returns:
            Created user data with generated password if applicable
        
        Raises:
            AlreadyExistsException: If email already exists
        """
        from core.security import generate_secure_password
        from modules.employees.models import Employee
        
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise AlreadyExistsException(resource="User with this email")
        
        # Handle employee linking
        employee = None
        generated_password = None
        
        if user_data.employee_id:
            # Check if employee exists and doesn't already have a user
            result = await self.db.execute(
                select(Employee).where(
                    Employee.id == user_data.employee_id,
                    Employee.is_deleted == False
                )
            )
            employee = result.scalar_one_or_none()
            
            if not employee:
                raise NotFoundException(resource="Employee")
            
            if employee.user_id:
                raise BadRequestException(message="Employee already has a user account")
            
            # Use employee's email and personal info if not provided
            if not user_data.email:
                user_data.email = employee.work_email or employee.personal_email
            if not user_data.first_name:
                user_data.first_name = employee.first_name
            if not user_data.last_name:
                user_data.last_name = employee.last_name
            if not user_data.phone:
                user_data.phone = employee.phone or employee.mobile
            if not user_data.country_code:
                user_data.country_code = employee.country_code or "US"
        
        # Auto-generate password if not provided
        if not user_data.password:
            generated_password = generate_secure_password(12)
            user_data.password = generated_password
        
        # Create user
        user_dict = user_data.model_dump(exclude={'role_ids', 'employee_id'})
        user = await self.user_repo.create(user_dict)
        await self.db.flush()
        
        # Link employee if provided
        if employee:
            employee.user_id = user.id
            await self.db.flush()
        
        # Assign roles using direct SQL to avoid lazy loading issues
        if user_data.role_ids:
            from sqlalchemy import text
            for role_id in user_data.role_ids:
                role = await self.role_repo.get_by_id(role_id)
                if role:
                    await self.db.execute(
                        text('INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)'),
                        {'user_id': str(user.id), 'role_id': str(role.id)}
                    )
        
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"New user registered: {user.email}")
        
        # Store generated password temporarily for response
        response_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "country_code": user.country_code,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "roles": [{"id": role.id, "name": role.name, "display_name": role.display_name} for role in user.roles],
            "generated_password": generated_password  # Include generated password in response
        }
        
        # Generate verification token
        from core.security import generate_reset_token
        verification_token = generate_reset_token()
        verification_expires = datetime.utcnow() + timedelta(days=7)
        
        await self.user_repo.update(user.id, {
            "verification_token": verification_token,
            "verification_token_expires": verification_expires
        })
        await self.db.commit()
        
        # Send verification email
        try:
            from core.email import EmailService
            email_service = EmailService()
            await email_service.send_verification_email(
                to_email=user.email,
                user_name=f"{user.first_name} {user.last_name}",
                verification_token=verification_token
            )
        except Exception as e:
            logger.warning(f"Failed to send verification email: {str(e)}")
            # Don't fail registration if email fails
        
        return response_data
    
    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access and refresh tokens
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Tuple of (new_access_token, new_refresh_token)
        
        Raises:
            UnauthorizedException: If refresh token is invalid or expired
        """
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise UnauthorizedException(message="Invalid token type")
            
            # Get user ID from token
            user_id = payload.get("sub")
            if not user_id:
                raise UnauthorizedException(message="Invalid token payload")
            
            # Get user from database
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UnauthorizedException(message="User not found")
            
            # Check if user is still active
            if not user.is_active:
                raise UnauthorizedException(message="User account is inactive")
            
            # Generate new tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": [role.name for role in user.roles],
                "permissions": [
                    perm.name
                    for role in user.roles
                    for perm in role.permissions
                ],
                "employee_id": str(user.employee.id) if user.employee else None,
                "country_code": user.country_code
            }
            
            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token({"sub": str(user.id)})
            
            logger.info(f"Tokens refreshed for user {user.email}")
            
            return new_access_token, new_refresh_token
            
        except JWTError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            raise UnauthorizedException(message="Invalid or expired refresh token")
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            True if successful
        
        Raises:
            NotFoundException: If user not found
            InvalidCredentialsException: If current password is incorrect
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(resource="User")
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsException(message="Current password is incorrect")
        
        # Update password
        await self.user_repo.update(user_id, {
            "hashed_password": hash_password(new_password),
            "password_changed_at": datetime.utcnow()
        })
        
        await self.db.commit()
        
        logger.info(f"User {user.email} changed password")
        
        # Send password change notification email
        try:
            from core.email import EmailService
            email_service = EmailService()
            await email_service.send_password_change_notification(user.email, f"{user.first_name} {user.last_name}")
        except Exception as e:
            logger.warning(f"Failed to send password change notification: {str(e)}")
        
        # Invalidate all refresh tokens
        try:
            from modules.auth.repositories import RefreshTokenRepository
            refresh_token_repo = RefreshTokenRepository(self.db)
            await refresh_token_repo.revoke_all_user_tokens(user.id)
            await self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to revoke refresh tokens: {str(e)}")
        
        return True
    
    async def forgot_password(self, email: str) -> bool:
        """
        Initiate password reset process
        
        Args:
            email: User email
        
        Returns:
            True if email sent (always returns True for security)
        """
        user = await self.user_repo.get_by_email(email)
        
        if user and user.is_active:
            # Generate reset token
            from core.security import generate_reset_token
            reset_token = generate_reset_token()
            reset_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Save reset token with expiration
            await self.user_repo.update(user.id, {
                "reset_token": reset_token,
                "reset_token_expires": reset_expires
            })
            await self.db.commit()
            
            # Send password reset email
            try:
                from core.email import EmailService
                email_service = EmailService()
                await email_service.send_password_reset_email(
                    to_email=user.email,
                    user_name=f"{user.first_name} {user.last_name}",
                    reset_token=reset_token
                )
                logger.info(f"Password reset email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
        
        # Always return True to prevent email enumeration
        return True
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
        
        Returns:
            True if successful
        
        Raises:
            NotFoundException: If token is invalid
            BadRequestException: If token is expired
        """
        from core.exceptions import NotFoundException, BadRequestException
        
        # Find user by reset token
        user = await self.user_repo.get_by_reset_token(token)
        if not user:
            raise NotFoundException(resource="Reset token")
        
        # Verify token not expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            raise BadRequestException(message="Reset token has expired. Please request a new one.")
        
        # Verify token matches
        if user.reset_token != token:
            raise NotFoundException(resource="Reset token")
        
        # Update password
        await self.user_repo.update(user.id, {
            "hashed_password": hash_password(new_password),
            "password_changed_at": datetime.utcnow(),
            "reset_token": None,
            "reset_token_expires": None,
            "failed_login_attempts": "0",
            "locked_until": None
        })
        await self.db.commit()
        
        # Send confirmation email
        try:
            from core.email import EmailService
            email_service = EmailService()
            await email_service.send_password_reset_confirmation(user.email, f"{user.first_name} {user.last_name}")
        except Exception as e:
            logger.warning(f"Failed to send password reset confirmation: {str(e)}")
        
        logger.info(f"Password reset completed for {user.email}")
        return True
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email using verification token
        
        Args:
            token: Email verification token
        
        Returns:
            True if successful
        
        Raises:
            NotFoundException: If token is invalid
            BadRequestException: If token is expired
        """
        from core.exceptions import NotFoundException, BadRequestException
        
        # Find user by verification token
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise NotFoundException(resource="Verification token")
        
        # Verify token not expired
        if not user.verification_token_expires or user.verification_token_expires < datetime.utcnow():
            raise BadRequestException(message="Verification token has expired. Please request a new one.")
        
        # Verify token matches
        if user.verification_token != token:
            raise NotFoundException(resource="Verification token")
        
        # Mark email as verified
        await self.user_repo.update(user.id, {
            "is_verified": True,
            "verification_token": None,
            "verification_token_expires": None
        })
        await self.db.commit()
        
        logger.info(f"Email verified for {user.email}")
        return True
    
    async def resend_verification_email(self, email: str) -> bool:
        """
        Resend verification email
        
        Args:
            email: User email
        
        Returns:
            True if email sent (always returns True for security)
        """
        user = await self.user_repo.get_by_email(email)
        
        if user and not user.is_verified:
            # Generate new verification token
            from core.security import generate_reset_token
            verification_token = generate_reset_token()
            verification_expires = datetime.utcnow() + timedelta(days=7)
            
            await self.user_repo.update(user.id, {
                "verification_token": verification_token,
                "verification_token_expires": verification_expires
            })
            await self.db.commit()
            
            # Send verification email
            try:
                from core.email import EmailService
                email_service = EmailService()
                await email_service.send_verification_email(
                    to_email=user.email,
                    user_name=f"{user.first_name} {user.last_name}",
                    verification_token=verification_token
                )
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
        
        # Always return True to prevent email enumeration
        return True
