"""
Seed Data Script
Creates initial data for development and testing
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from core.security import hash_password
from modules.auth.models import User, Role, Permission
from modules.employees.models import Department, Position
from modules.admin.models import CountryConfig


async def create_permissions():
    """Create default permissions"""
    permissions_data = [
        # Admin
        {"name": "admin:all", "resource": "admin", "action": "all", "description": "Full system access"},
        
        # HR
        {"name": "hr:read", "resource": "hr", "action": "read", "description": "Read HR data"},
        {"name": "hr:write", "resource": "hr", "action": "write", "description": "Write HR data"},
        {"name": "hr:admin", "resource": "hr", "action": "admin", "description": "HR administration"},
        
        # Employees
        {"name": "employees:read", "resource": "employees", "action": "read", "description": "View employees"},
        {"name": "employees:write", "resource": "employees", "action": "write", "description": "Manage employees"},
        
        # Leave
        {"name": "leave:request", "resource": "leave", "action": "request", "description": "Request leave"},
        {"name": "leave:approve", "resource": "leave", "action": "approve", "description": "Approve leave"},
        
        # Payroll
        {"name": "payroll:admin", "resource": "payroll", "action": "admin", "description": "Manage payroll"},
        
        # Reports
        {"name": "reports:view", "resource": "reports", "action": "view", "description": "View reports"},
    ]
    
    return permissions_data


async def seed_data():
    """Seed initial data"""
    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Seeding database...")
            
            # Create permissions
            print("Creating permissions...")
            permissions_data = await create_permissions()
            permissions = []
            for perm_data in permissions_data:
                permission = Permission(**perm_data)
                session.add(permission)
                permissions.append(permission)
            
            await session.flush()
            
            # Create roles
            print("Creating roles...")
            
            # Super Admin role (all permissions)
            super_admin_role = Role(
                name="super_admin",
                display_name="Super Administrator",
                description="Full system access",
                is_system=True
            )
            super_admin_role.permissions = permissions
            session.add(super_admin_role)
            
            # HR Admin role
            hr_admin_role = Role(
                name="hr_admin",
                display_name="HR Administrator",
                description="HR administration access",
                is_system=True
            )
            hr_perms = [p for p in permissions if p.resource in ["hr", "employees", "leave", "reports"]]
            hr_admin_role.permissions = hr_perms
            session.add(hr_admin_role)
            
            # Employee role (basic access)
            employee_role = Role(
                name="employee",
                display_name="Employee",
                description="Basic employee access",
                is_system=True
            )
            emp_perms = [p for p in permissions if p.name in ["leave:request", "reports:view"]]
            employee_role.permissions = emp_perms
            session.add(employee_role)
            
            await session.flush()
            
            # Create admin user
            print("Creating admin user...")
            admin_user = User(
                email="admin@inara.org",
                hashed_password=hash_password("Admin@123"),
                first_name="System",
                last_name="Administrator",
                country_code="US",
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            admin_user.roles = [super_admin_role]
            session.add(admin_user)
            
            # Create HR user
            print("Creating HR user...")
            hr_user = User(
                email="hr@inara.org",
                hashed_password=hash_password("HR@123"),
                first_name="HR",
                last_name="Manager",
                country_code="US",
                is_active=True,
                is_verified=True,
                is_superuser=False
            )
            hr_user.roles = [hr_admin_role]
            session.add(hr_user)
            
            # Create sample departments
            print("Creating departments...")
            departments = [
                Department(name="Human Resources", code="HR", country_code="US"),
                Department(name="Finance", code="FIN", country_code="US"),
                Department(name="Operations", code="OPS", country_code="US"),
                Department(name="Programs", code="PROG", country_code="US"),
            ]
            for dept in departments:
                session.add(dept)
            
            # Create sample positions
            print("Creating positions...")
            positions = [
                Position(title="HR Manager", code="HR-MGR", level="Manager", country_code="US"),
                Position(title="HR Officer", code="HR-OFF", level="Officer", country_code="US"),
                Position(title="Program Manager", code="PROG-MGR", level="Manager", country_code="US"),
                Position(title="Finance Officer", code="FIN-OFF", level="Officer", country_code="US"),
            ]
            for pos in positions:
                session.add(pos)
            
            # Create country configs
            print("Creating country configurations...")
            countries = [
                CountryConfig(
                    country_code="US",
                    country_name="United States",
                    timezone="America/New_York",
                    default_currency="USD",
                    working_hours_per_week=40,
                    working_days_per_week=5
                ),
                CountryConfig(
                    country_code="SY",
                    country_name="Syria",
                    timezone="Asia/Damascus",
                    default_currency="USD",
                    working_hours_per_week=40,
                    working_days_per_week=5
                ),
                CountryConfig(
                    country_code="TR",
                    country_name="Turkey",
                    timezone="Europe/Istanbul",
                    default_currency="TRY",
                    working_hours_per_week=45,
                    working_days_per_week=5
                ),
            ]
            for country in countries:
                session.add(country)
            
            await session.commit()
            
            print("\n✅ Database seeded successfully!")
            print("\n📝 Login credentials:")
            print("   Admin: admin@inara.org / Admin@123")
            print("   HR:    hr@inara.org / HR@123")
            print("\n⚠️  Remember to change these passwords in production!")
            
        except Exception as e:
            print(f"\n❌ Error seeding database: {str(e)}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
