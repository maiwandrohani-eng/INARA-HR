"""
Admin Configuration Module - Models
Country-specific HR rules, salary bands, leave policies
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, Numeric
from core.database import Base
from core.models import BaseModel, TenantMixin

class CountryConfig(BaseModel, TenantMixin, Base):
    """Country-specific HR configuration"""
    __tablename__ = "country_configs"
    
    country_code = Column(String(2), nullable=False, unique=True)
    country_name = Column(String(100), nullable=False)
    default_currency = Column(String(3), nullable=False)
    timezone = Column(String(50), nullable=False)
    working_hours_per_week = Column(Numeric(5, 2), nullable=False, default=40)
    working_days_per_week = Column(Integer, nullable=False, default=5)
    public_holidays = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class SalaryBand(BaseModel, TenantMixin, Base):
    """Salary band definitions"""
    __tablename__ = "salary_bands"
    
    name = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    min_salary = Column(Numeric(12, 2), nullable=False)
    max_salary = Column(Numeric(12, 2), nullable=False)
    currency_code = Column(String(3), default="USD")
    country_code = Column(String(2), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
