"""
Authentication Module - API Routes
Endpoints for authentication and user management
"""

from fastapi import APIRouter, Depends, status, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
import csv
import io

from core.database import get_db
from core.dependencies import get_current_user, get_current_active_user, require_admin
from modules.auth.services import AuthService
from modules.auth.repositories import UserRepository, RoleRepository, PermissionRepository
from modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    RoleCreate,
    RoleResponse,
    PermissionCreate,
    PermissionResponse
)
from core.config import settings

router = APIRouter()

# Rate limiting for auth endpoints (stricter limits) - optional
try:
    if settings.RATE_LIMIT_ENABLED:
        from core.rate_limit import limiter
        from slowapi.util import get_remote_address
    else:
        limiter = None
except (ImportError, Exception):
    limiter = None  # Rate limiting not available


# ============================================
# Authentication Endpoints
# ============================================

@router.post("/login", response_model=LoginResponse)
@limiter.limit(f"{settings.RATE_LIMIT_AUTH_PER_MINUTE}/minute") if limiter else lambda x: x
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    
    - **email**: User email address
    - **password**: User password
    """
    auth_service = AuthService(db)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Authenticate
    access_token, refresh_token = await auth_service.login(
        credentials,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access_token and refresh_token
    """
    auth_service = AuthService(db)
    
    # Refresh tokens
    access_token, refresh_token = await auth_service.refresh_tokens(
        refresh_data.refresh_token
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)  # Only admins can create users
):
    """
    Register a new user (Admin only)
    
    - **email**: User email address
    - **password**: User password (min 8 chars)
    - **first_name**: First name
    - **last_name**: Last name
    - **country_code**: ISO country code (e.g., US, SY, TR)
    """
    auth_service = AuthService(db)
    user = await auth_service.register(user_data)
    return user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Change current user's password
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    """
    auth_service = AuthService(db)
    await auth_service.change_password(
        user_id=current_user["id"],
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    return {"success": True, "message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email
    
    - **email**: User email address
    """
    auth_service = AuthService(db)
    await auth_service.forgot_password(request_data.email)
    return {
        "success": True,
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    """
    auth_service = AuthService(db)
    await auth_service.reset_password(request_data.token, request_data.new_password)
    return {
        "success": True,
        "message": "Password reset successfully"
    }


@router.post("/verify-email")
async def verify_email(
    request_data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email address using verification token
    
    - **token**: Email verification token from email
    """
    auth_service = AuthService(db)
    await auth_service.verify_email(request_data.token)
    return {
        "success": True,
        "message": "Email verified successfully"
    }


@router.post("/resend-verification")
async def resend_verification(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification link
    
    - **email**: User email address
    """
    auth_service = AuthService(db)
    await auth_service.resend_verification_email(request_data.email)
    return {
        "success": True,
        "message": "If the email exists and is not verified, a verification link has been sent"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user's profile"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user["id"])
    
    # Manually set employee_id if employee relationship exists
    if hasattr(user, 'employee') and user.employee:
        user.employee_id = user.employee.id
    else:
        user.employee_id = None
    
    return user


# ============================================
# User Management Endpoints (Admin)
# ============================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """List all users (Admin only)"""
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Get user by ID (Admin only)"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="User")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update user (Admin only)"""
    user_repo = UserRepository(db)
    
    # Extract role_ids before updating
    update_dict = user_data.model_dump(exclude_unset=True)
    role_ids = update_dict.pop('role_ids', None)
    
    # Update basic user fields
    user = await user_repo.update(user_id, update_dict)
    if not user:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="User")
    
    # Update roles if provided
    if role_ids is not None:
        role_repo = RoleRepository(db)
        # Clear existing roles
        user.roles = []
        # Add new roles
        for role_id in role_ids:
            role = await role_repo.get_by_id(role_id)
            if role:
                user.roles.append(role)
    
    await db.commit()  # Explicit commit for update operation
    await db.refresh(user)
    return user


@router.get("/employees/without-users")
async def list_employees_without_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """List all employees that don't have user accounts yet"""
    from modules.employees.models import Employee
    from sqlalchemy.orm import selectinload
    
    # Get all employees without user_id, with relationships loaded
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.position)
        )
        .where(
            and_(
                Employee.is_deleted == False,
                Employee.user_id.is_(None)
            )
        )
        .order_by(Employee.first_name, Employee.last_name)
    )
    employees = result.scalars().all()
    
    # Return simplified employee data for dropdown
    return [
        {
            "id": str(emp.id),
            "employee_number": emp.employee_number,
            "full_name": f"{emp.first_name} {emp.last_name}",
            "email": emp.work_email or emp.personal_email,
            "department": emp.department.name if emp.department else None,
            "position": emp.position.title if emp.position else None,
        }
        for emp in employees
    ]


@router.get("/users/export")
async def export_users_with_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Export all users with their credentials (passwords will be reset/generated)
    Returns CSV file with email, password, name, role, etc.
    """
    from core.security import generate_secure_password
    from modules.auth.repositories import UserRepository
    from modules.auth.models import User
    
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=0, limit=10000)  # Get all users
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Email",
        "Password",
        "First Name",
        "Last Name",
        "Phone",
        "Country Code",
        "Role",
        "Is Active",
        "Is Verified",
        "Employee ID",
        "Employee Number",
    ])
    
    # Reset passwords and write user data
    for user in users:
        # Generate new password for export
        new_password = generate_secure_password(12)
        
        # Update user password
        await user_repo.update(user.id, {"password": new_password})
        await db.commit()
        
        # Get role names
        role_names = [role.display_name for role in user.roles] if user.roles else []
        role_str = ", ".join(role_names) if role_names else "No Role"
        
        # Get employee info if linked
        employee_number = None
        if user.employee_id:
            from modules.employees.models import Employee
            emp_result = await db.execute(
                select(Employee).where(Employee.id == user.employee_id)
            )
            employee = emp_result.scalar_one_or_none()
            if employee:
                employee_number = employee.employee_number
        
        writer.writerow([
            user.email,
            new_password,
            user.first_name,
            user.last_name,
            user.phone or "",
            user.country_code,
            role_str,
            "Yes" if user.is_active else "No",
            "Yes" if user.is_verified else "No",
            str(user.employee_id) if user.employee_id else "",
            employee_number or "",
        ])
    
    output.seek(0)
    
    # Return CSV file
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users_credentials_export.csv"
        }
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete user (Admin only)"""
    user_repo = UserRepository(db)
    deleted = await user_repo.delete(user_id)
    if not deleted:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="User")
    await db.commit()  # Explicit commit for delete operation


@router.patch("/users/{user_id}/password")
async def reset_user_password(
    user_id: str,
    password_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Reset user's password (Admin only)
    
    - **new_password**: New password (min 8 chars)
    """
    from core.security import hash_password
    
    # Validate new password
    new_password = password_data.get("new_password")
    if not new_password:
        from core.exceptions import BadRequestException
        raise BadRequestException(message="new_password is required")
    
    # Basic password length validation
    if len(new_password) < 8:
        from core.exceptions import BadRequestException
        raise BadRequestException(message="Password must be at least 8 characters")
    
    # Get user
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        from core.exceptions import NotFoundException
        raise NotFoundException(resource="User")
    
    # Update password
    hashed_password = hash_password(new_password)
    update_data = {
        "hashed_password": hashed_password,
        "password_changed_at": None  # Will be set by DB trigger/default
    }
    
    # Use raw update to change password
    await user_repo.update(user_id, update_data)
    await db.commit()  # Explicit commit for password update
    
    return {"success": True, "message": "Password reset successfully"}


# ============================================
# Role Management Endpoints (Admin)
# ============================================

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all roles"""
    role_repo = RoleRepository(db)
    roles = await role_repo.get_all()
    return roles


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create new role (Admin only)"""
    role_repo = RoleRepository(db)
    
    # Check if role already exists
    existing = await role_repo.get_by_name(role_data.name)
    if existing:
        from core.exceptions import AlreadyExistsException
        raise AlreadyExistsException(resource="Role")
    
    role = await role_repo.create(role_data.model_dump(exclude={'permission_ids'}))
    await db.commit()  # Explicit commit for create operation
    await db.refresh(role)
    return role


# ============================================
# Permission Management Endpoints (Admin)
# ============================================

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """List all permissions"""
    perm_repo = PermissionRepository(db)
    permissions = await perm_repo.get_all()
    return permissions


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create new permission (Admin only)"""
    perm_repo = PermissionRepository(db)
    
    # Check if permission already exists
    existing = await perm_repo.get_by_name(permission_data.name)
    if existing:
        from core.exceptions import AlreadyExistsException
        raise AlreadyExistsException(resource="Permission")
    
    permission = await perm_repo.create(permission_data.model_dump())
    await db.commit()  # Explicit commit for create operation
    await db.refresh(permission)
    return permission
