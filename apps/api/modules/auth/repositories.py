"""
Authentication Module - Repository Layer
Database operations for auth entities
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from modules.auth.models import User, Role, Permission, LoginAttempt, RefreshToken
from core.security import hash_password
from core.retry import retry_on_db_error

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @retry_on_db_error(max_retries=3)
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID with automatic retry on transient errors"""
        try:
            result = await self.db.execute(
                select(User)
                .options(
                    selectinload(User.roles).selectinload(Role.permissions),
                    selectinload(User.employee)
                )
                .where(and_(User.id == user_id, User.is_deleted == False))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
            raise
    
    @retry_on_db_error(max_retries=3)
    async def get_by_email(self, email: str, include_employee: bool = False) -> Optional[User]:
        """Get user by email with automatic retry on transient errors"""
        try:
            query = select(User).options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            
            # Optionally include employee for login operations
            if include_employee:
                query = query.options(selectinload(User.employee))
            
            query = query.where(and_(User.email == email.lower(), User.is_deleted == False))
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {str(e)}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, user_data: dict) -> User:
        """Create new user"""
        # Hash password
        if 'password' in user_data:
            user_data['hashed_password'] = hash_password(user_data.pop('password'))
        
        # Normalize email
        if 'email' in user_data:
            user_data['email'] = user_data['email'].lower()
        
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, user_id: uuid.UUID, user_data: dict) -> Optional[User]:
        """Update user"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: uuid.UUID) -> bool:
        """Soft delete user"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        await self.db.flush()
        return True
    
    async def update_last_login(self, user_id: uuid.UUID):
        """Update user's last login timestamp"""
        # Use direct update for better performance
        from sqlalchemy import update
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.flush()
    
    async def get_by_reset_token(self, token: str) -> Optional[User]:
        """Get user by password reset token"""
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.reset_token == token,
                    User.is_deleted == False,
                    User.reset_token_expires > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by email verification token"""
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.verification_token == token,
                    User.is_deleted == False,
                    User.verification_token_expires > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()


class RoleRepository:
    """Repository for Role database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(and_(Role.id == role_id, Role.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(and_(Role.name == name, Role.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Role]:
        """Get all roles"""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.is_deleted == False)
        )
        return result.scalars().all()
    
    async def create(self, role_data: dict) -> Role:
        """Create new role"""
        role = Role(**role_data)
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role


class PermissionRepository:
    """Repository for Permission database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, permission_id: uuid.UUID) -> Optional[Permission]:
        """Get permission by ID"""
        result = await self.db.execute(
            select(Permission).where(and_(Permission.id == permission_id, Permission.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        result = await self.db.execute(
            select(Permission).where(and_(Permission.name == name, Permission.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Permission]:
        """Get all permissions"""
        result = await self.db.execute(
            select(Permission).where(Permission.is_deleted == False)
        )
        return result.scalars().all()
    
    async def create(self, permission_data: dict) -> Permission:
        """Create new permission"""
        permission = Permission(**permission_data)
        self.db.add(permission)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission


class LoginAttemptRepository:
    """Repository for LoginAttempt database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, attempt_data: dict) -> LoginAttempt:
        """Record login attempt"""
        attempt = LoginAttempt(**attempt_data)
        self.db.add(attempt)
        await self.db.flush()
        return attempt


class RefreshTokenRepository:
    """Repository for RefreshToken database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, token_data: dict) -> RefreshToken:
        """Create refresh token"""
        token = RefreshToken(**token_data)
        self.db.add(token)
        await self.db.flush()
        return token
    
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == token,
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        token_obj = await self.get_by_token(token)
        if token_obj:
            token_obj.revoked = True
            token_obj.revoked_at = datetime.utcnow()
            await self.db.flush()
            return True
        return False
    
    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user"""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False
                )
            )
        )
        tokens = result.scalars().all()
        count = 0
        for token in tokens:
            token.revoked = True
            token.revoked_at = datetime.utcnow()
            count += 1
        await self.db.flush()
        return count
