"""
Admin Module - Pydantic Schemas
Request/response validation schemas for admin operations
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class CountryConfigBase(BaseModel):
    """Base country config schema"""
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str = Field(..., min_length=1, max_length=100)
    default_currency: str = Field(..., min_length=3, max_length=3)
    timezone: str = Field(..., min_length=1, max_length=50)
    working_hours_per_week: float = Field(..., ge=0, le=168)
    working_days_per_week: int = Field(..., ge=1, le=7)
    public_holidays: Optional[str] = None


class CountryConfigCreate(CountryConfigBase):
    """Country config creation schema"""
    is_active: bool = True


class CountryConfigUpdate(BaseModel):
    """Country config update schema"""
    default_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    timezone: Optional[str] = Field(None, min_length=1, max_length=50)
    working_hours_per_week: Optional[float] = Field(None, ge=0, le=168)
    working_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    public_holidays: Optional[str] = None
    is_active: Optional[bool] = None


class CountryConfigResponse(CountryConfigBase):
    """Country config response schema"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SalaryBandBase(BaseModel):
    """Base salary band schema"""
    name: str = Field(..., min_length=1, max_length=50)
    level: int = Field(..., ge=1)
    min_salary: float = Field(..., ge=0)
    max_salary: float = Field(..., gt=0)
    currency_code: str = Field(..., min_length=3, max_length=3)
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    description: Optional[str] = None


class SalaryBandCreate(SalaryBandBase):
    """Salary band creation schema"""
    is_active: bool = True


class SalaryBandUpdate(BaseModel):
    """Salary band update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    level: Optional[int] = Field(None, ge=1)
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, gt=0)
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SalaryBandResponse(SalaryBandBase):
    """Salary band response schema"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
