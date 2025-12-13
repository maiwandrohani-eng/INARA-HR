"""
Authentication Dependencies
Reusable dependencies for route protection and user authentication
"""

from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from core.database import get_db
from core.security import decode_token
from core.exceptions import UnauthorizedException, ForbiddenException

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user from JWT token
    
    Returns:
        Current user object
    
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(message="Invalid token payload")
        
        # Fetch user from database
        from modules.auth.repositories import UserRepository
        import uuid
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(uuid.UUID(user_id))
        
        if not user:
            raise UnauthorizedException(message="User not found")
        
        if not user.is_active:
            raise UnauthorizedException(message="User account is inactive")
        
        # Return user dict with token data
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": [role.name for role in user.roles],
            "permissions": [
                perm.name
                for role in user.roles
                for perm in role.permissions
            ],
            "employee_id": str(user.employee.id) if user.employee else None,
            "country_code": user.country_code,
            "is_superuser": user.is_superuser
        }
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise UnauthorizedException(message="Authentication failed", details=str(e))


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user and verify they are active
    
    Raises:
        ForbiddenException: If user is inactive
    """
    # TODO: Check if user is active in database
    if not current_user.get("is_active", True):
        raise ForbiddenException(message="Inactive user")
    
    return current_user


class PermissionChecker:
    """Dependency class to check user permissions"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, current_user: dict = Depends(get_current_active_user)):
        """
        Check if user has required permissions
        
        Raises:
            ForbiddenException: If user lacks required permissions
        """
        user_permissions = current_user.get("permissions", [])
        
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise ForbiddenException(
                    message=f"Missing required permission: {permission}",
                    details={"required": self.required_permissions, "available": user_permissions}
                )
        
        return current_user


class RoleChecker:
    """Dependency class to check user roles"""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    async def __call__(self, current_user: dict = Depends(get_current_active_user)):
        """
        Check if user has one of the required roles
        
        Raises:
            ForbiddenException: If user lacks required role
        """
        user_roles = current_user.get("roles", [])
        
        has_role = any(role in user_roles for role in self.required_roles)
        
        if not has_role:
            raise ForbiddenException(
                message="Insufficient role privileges",
                details={"required": self.required_roles, "available": user_roles}
            )
        
        return current_user


# Common permission checkers
require_admin = PermissionChecker(["admin:all"])
require_hr_admin = PermissionChecker(["hr:admin"])
require_hr_read = PermissionChecker(["hr:read"])
require_hr_write = PermissionChecker(["hr:write"])
