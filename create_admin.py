#!/usr/bin/env python3
"""Create admin user for INARA HRIS"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

import asyncio
import uuid
from sqlalchemy import select
from core.database import get_db_session
from modules.auth.models import User, Role
from core.security import hash_password

async def create_admin():
    """Create admin user"""
    async with get_db_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == "admin@inara.org")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Admin user already exists!")
            print("Email: admin@inara.org")
            print("Password: Admin@123")
            return
        
        # Get or create admin role
        result = await session.execute(
            select(Role).where(Role.name == "super_admin")
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            admin_role = Role(
                name="super_admin",
                display_name="Super Administrator",
                description="Full system access",
                is_system=True
            )
            session.add(admin_role)
            await session.flush()
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@inara.org",
            hashed_password=hash_password("Admin@123"),
            first_name="System",
            last_name="Administrator",
            country_code="US",
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        admin_user.roles.append(admin_role)
        
        session.add(admin_user)
        await session.commit()
        
        print("✓ Admin user created successfully!")
        print("\nLogin credentials:")
        print("Email: admin@inara.org")
        print("Password: Admin@123")
        print("\nYou can now log in at: http://localhost:3000/login")

if __name__ == "__main__":
    asyncio.run(create_admin())
