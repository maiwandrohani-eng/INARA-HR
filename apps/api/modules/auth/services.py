"""
Authentication Module - Service Layer
Business logic for authentication operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError
import logging

from modules.auth.repositories import UserRepository, RoleRepository, LoginAttemptRepository
from modules.auth.schemas import UserCreate, LoginRequest
from core.security import verify_password, create_access_token, create_refresh_token, hash_password, decode_token
from core.exceptions import InvalidCredentialsException, AlreadyExistsException, NotFoundException, UnauthorizedException
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
        # Get user by email
        user = await self.user_repo.get_by_email(credentials.email)
        
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
            raise InvalidCredentialsException()
        
        # Check if user is active
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
        
        # TODO: Check if account is locked
        # TODO: Check if email is verified (if required)
        
        # Log successful attempt and update last login in transaction
        try:
            await self.login_attempt_repo.create({
                "user_id": user.id,
                "email": credentials.email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": True
            })
            
            # Update last login
            await self.user_repo.update_last_login(user.id)
            
            # Commit the login tracking
            await self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to log login attempt: {str(e)}")
            # Don't fail login if logging fails
            await self.db.rollback()
        
        # Generate tokens
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
        
        logger.info(f"User {user.email} logged in successfully")
        
        return access_token, refresh_token
    
    async def register(self, user_data: UserCreate) -> dict:
        """
        Register a new user
        
        Args:
            user_data: User registration data
        
        Returns:
            Created user data
        
        Raises:
            AlreadyExistsException: If email already exists
        """
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise AlreadyExistsException(resource="User with this email")
        
        # Create user
        user_dict = user_data.model_dump(exclude={'role_ids'})
        user = await self.user_repo.create(user_dict)
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
        
        # TODO: Send verification email
        
        return user
    
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
        
        # TODO: Send password change notification email
        # TODO: Invalidate all refresh tokens
        
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
        
        if user:
            # TODO: Generate reset token
            # TODO: Save reset token with expiration
            # TODO: Send password reset email
            logger.info(f"Password reset requested for {email}")
        
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
        """
        # TODO: Find user by reset token
        # TODO: Verify token not expired
        # TODO: Update password
        # TODO: Clear reset token
        # TODO: Send confirmation email
        
        return True
