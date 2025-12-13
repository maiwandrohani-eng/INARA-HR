"""
Create user account directly in database
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys

# Set working directory to API folder
os.chdir('/Users/maiwand/INARA-HR/apps/api')
sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from modules.auth.models import User, Role
from core.security import hash_password

# Database connection
DATABASE_URL = "postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris"

async def create_user():
    """Create user account"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == "maiwand@inara.org")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("\n✅ User maiwand@inara.org already exists!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
            print(f"   Active: {existing_user.is_active}")
            return
        
        # Get super_admin role
        result = await session.execute(
            select(Role).where(Role.name == "super_admin")
        )
        super_admin_role = result.scalar_one_or_none()
        
        # Create user
        new_user = User(
            email="maiwand@inara.org",
            hashed_password=hash_password("Come*1234"),
            first_name="Maiwand",
            last_name="User",
            country_code="AF",
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
        
        if super_admin_role:
            new_user.roles.append(super_admin_role)
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        print("\n✅ User created successfully!")
        print(f"   Email: maiwand@inara.org")
        print(f"   Password: Come*1234")
        print(f"   User ID: {new_user.id}")
        print(f"   Name: {new_user.first_name} {new_user.last_name}")
        print("\n👉 You can now login at http://localhost:3000/login")

if __name__ == "__main__":
    asyncio.run(create_user())
