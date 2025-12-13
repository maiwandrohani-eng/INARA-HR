"""
Employee Management Module - Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import uuid


class EmployeeBase(BaseModel):
    """Base employee schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    work_email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)


class EmployeeCreate(EmployeeBase):
    """Employee creation schema"""
    employee_number: Optional[str] = None  # Auto-generated if not provided
    employment_type: str
    hire_date: date
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    work_location: Optional[str] = None


class EmployeeUpdate(BaseModel):
    """Employee update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    status: Optional[str] = None


class EmployeeHierarchyUpdate(BaseModel):
    """Update employee's organizational hierarchy"""
    manager_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None


class DepartmentBase(BaseModel):
    """Base department schema"""
    name: str
    code: str
    description: Optional[str] = None
    country_code: str = Field(default="US", min_length=2, max_length=2)
    parent_id: Optional[uuid.UUID] = None
    head_id: Optional[uuid.UUID] = None


class DepartmentCreate(DepartmentBase):
    """Department creation schema"""
    pass


class DepartmentUpdate(BaseModel):
    """Department update schema"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    head_id: Optional[uuid.UUID] = None


class DepartmentResponse(DepartmentBase):
    """Department response schema"""
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    """Base position schema"""
    title: str
    code: str
    description: Optional[str] = None
    level: Optional[str] = None
    country_code: str = Field(default="US", min_length=2, max_length=2)


class PositionCreate(PositionBase):
    """Position creation schema"""
    pass


class PositionUpdate(BaseModel):
    """Position update schema"""
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None


class PositionResponse(PositionBase):
    """Position response schema"""
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    """Employee response schema"""
    id: uuid.UUID
    employee_number: str
    status: str
    employment_type: str
    hire_date: date
    work_location: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    position_id: Optional[uuid.UUID] = None
    department: Optional[DepartmentResponse] = None
    position: Optional[PositionResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    """Contract creation schema"""
    employee_id: uuid.UUID
    contract_number: str
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    salary: Decimal
    currency: str = "USD"
    salary_frequency: str = "monthly"


class ContractResponse(BaseModel):
    """Contract response schema"""
    id: uuid.UUID
    contract_number: str
    contract_type: str
    start_date: date
    end_date: Optional[date]
    salary: Decimal
    currency: str
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True
