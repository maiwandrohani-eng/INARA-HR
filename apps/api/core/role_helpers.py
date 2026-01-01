"""
Helper utilities for finding employees by role
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from modules.auth.models import User, Role
from modules.employees.models import Employee


async def get_employee_by_role(
    db: AsyncSession,
    role_name: str,
    country_code: Optional[str] = None
) -> Optional[Employee]:
    """
    Find an employee by their user role (e.g., 'hr_manager', 'finance_manager', 'admin')
    
    Args:
        db: Database session
        role_name: Name of the role (e.g., 'hr_manager', 'finance_manager', 'admin', 'ceo')
        country_code: Optional country code filter
        
    Returns:
        Employee object if found, None otherwise
    """
    # Map role names - admin is treated as CEO
    role_mapping = {
        'ceo': 'admin',  # CEO maps to admin role
        'admin': 'admin',
        'hr_manager': 'hr_manager',
        'finance_manager': 'finance_manager',
    }
    
    mapped_role = role_mapping.get(role_name.lower(), role_name.lower())
    
    # Find users with this role
    result = await db.execute(
        select(User)
        .join(User.roles)
        .where(Role.name == mapped_role)
        .where(User.is_active == True)
        .options(selectinload(User.employee))
    )
    users = result.scalars().all()
    
    if not users:
        return None
    
    # Filter by country_code if provided
    if country_code:
        for user in users:
            if user.employee and user.employee.country_code == country_code:
                return user.employee
    
    # Return first active employee with this role
    for user in users:
        if user.employee:
            return user.employee
    
    return None


async def get_hr_manager(db: AsyncSession, country_code: Optional[str] = None) -> Optional[Employee]:
    """Get HR Manager employee"""
    return await get_employee_by_role(db, 'hr_manager', country_code)


async def get_finance_manager(db: AsyncSession, country_code: Optional[str] = None) -> Optional[Employee]:
    """Get Finance Manager employee"""
    return await get_employee_by_role(db, 'finance_manager', country_code)


async def get_ceo(db: AsyncSession, country_code: Optional[str] = None) -> Optional[Employee]:
    """Get CEO (Admin) employee"""
    return await get_employee_by_role(db, 'admin', country_code)

