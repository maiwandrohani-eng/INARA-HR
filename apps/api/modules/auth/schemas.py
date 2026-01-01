"""
Authentication Module - Pydantic Schemas
Request/response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator, computed_field
from typing import List, Optional
from datetime import datetime
import uuid


# ============================================
# Authentication Schemas
# ============================================

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    """User login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    token: str


# ============================================
# User Schemas
# ============================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    country_code: str = Field(..., min_length=2, max_length=2)


class UserCreate(UserBase):
    """User creation schema"""
    password: Optional[str] = Field(None, min_length=8)  # Optional - will be auto-generated if not provided
    role_ids: List[uuid.UUID] = []
    employee_id: Optional[uuid.UUID] = None  # Link to existing employee


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    is_active: Optional[bool] = None
    role_ids: Optional[List[uuid.UUID]] = None


class UserResponse(UserBase):
    """User response schema"""
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    employee_id: Optional[uuid.UUID] = None
    last_login: Optional[datetime]
    created_at: datetime
    roles: List['RoleResponse'] = []
    generated_password: Optional[str] = None  # Only included when password is auto-generated
    
    class Config:
        from_attributes = True


# ============================================
# Role Schemas
# ============================================

class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema"""
    permission_ids: List[uuid.UUID] = []


class RoleUpdate(BaseModel):
    """Role update schema"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[List[uuid.UUID]] = None


class RoleResponse(RoleBase):
    """Role response schema"""
    id: uuid.UUID
    is_system: bool
    created_at: datetime
    permissions: List['PermissionResponse'] = []
    
    class Config:
        from_attributes = True


# ============================================
# Permission Schemas
# ============================================

class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Permission creation schema"""
    pass


class PermissionResponse(PermissionBase):
    """Permission response schema"""
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward references
UserResponse.model_rebuild()
RoleResponse.model_rebuild()
