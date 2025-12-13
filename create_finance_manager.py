#!/usr/bin/env python3
"""
Create Finance Manager User (Mer Wais)
"""
import asyncio
import sys
from pathlib import Path

# Add the API directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

from sqlalchemy import select
from core.database import get_db, engine
from core.models import User, Role
from core.security import hash_password


async def create_finance_manager():
    """Create Mer Wais as Finance Manager"""
    
    # Create async session
    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as db:
        try:
            # Check if user already exists
            result = await db.execute(
                select(User).where(User.email == "mer@inara.org")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✓ User mer@inara.org already exists with ID: {existing_user.id}")
                user = existing_user
            else:
                # Create new user
                hashed_password = hash_password("password123")  # Change this!
                user = User(
                    email="mer@inara.org",
                    first_name="Mer",
                    last_name="Wais",
                    password_hash=hashed_password,
                    is_active=True,
                    is_superuser=False
                )
                db.add(user)
                await db.flush()
                print(f"✓ Created user: Mer Wais (mer@inara.org)")
                print(f"  User ID: {user.id}")
                print(f"  Default password: password123 (CHANGE THIS!)")
            
            # Get Finance Manager role
            result = await db.execute(
                select(Role).where(Role.name == "finance_manager")
            )
            finance_role = result.scalar_one_or_none()
            
            if not finance_role:
                print("✗ Finance Manager role not found! Run seed_roles_permissions.py first")
                return
            
            # Assign role if not already assigned
            if finance_role not in user.roles:
                user.roles.append(finance_role)
                print(f"✓ Assigned Finance Manager role to {user.first_name} {user.last_name}")
            else:
                print(f"✓ User already has Finance Manager role")
            
            await db.commit()
            
            print("\n" + "="*60)
            print("FINANCE MANAGER ACCOUNT CREATED SUCCESSFULLY")
            print("="*60)
            print(f"Email: mer@inara.org")
            print(f"Password: password123")
            print(f"Role: Finance Manager")
            print(f"User ID: {user.id}")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Error creating Finance Manager: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_finance_manager())
