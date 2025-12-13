#!/usr/bin/env python3
"""
Setup Finance Manager (Mer Wais) and HR Manager (Gokce Kaya Allende)
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


async def setup_managers():
    """Create/Update Finance Manager and HR Manager"""
    
    # Create async session
    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as db:
        try:
            print("\n" + "="*70)
            print("SETTING UP FINANCE MANAGER AND HR MANAGER")
            print("="*70)
            
            # Get the roles first
            result = await db.execute(
                select(Role).where(Role.name == "finance_manager")
            )
            finance_role = result.scalar_one_or_none()
            
            result = await db.execute(
                select(Role).where(Role.name == "hr_manager")
            )
            hr_role = result.scalar_one_or_none()
            
            if not finance_role or not hr_role:
                print("✗ Required roles not found! Run seed_roles_permissions.py first")
                return
            
            # ===== 1. UPDATE MER WAIS AS FINANCE MANAGER =====
            print("\n" + "-"*70)
            print("1. FINANCE MANAGER - Mer Wais")
            print("-"*70)
            
            result = await db.execute(
                select(User).where(User.email == "mer@inara.org")
            )
            mer_user = result.scalar_one_or_none()
            
            if mer_user:
                print(f"✓ Found user: {mer_user.first_name} {mer_user.last_name} ({mer_user.email})")
                
                # Clear existing roles and add finance_manager
                mer_user.roles.clear()
                mer_user.roles.append(finance_role)
                print(f"✓ Updated role to Finance Manager")
            else:
                # Create new user
                hashed_password = hash_password("password123")
                mer_user = User(
                    email="mer@inara.org",
                    first_name="Mer",
                    last_name="Wais",
                    password_hash=hashed_password,
                    is_active=True,
                    is_superuser=False
                )
                db.add(mer_user)
                await db.flush()
                
                mer_user.roles.append(finance_role)
                print(f"✓ Created user: Mer Wais (mer@inara.org)")
                print(f"  Default password: password123")
            
            # ===== 2. CREATE/UPDATE GOKCE KAYA AS HR MANAGER =====
            print("\n" + "-"*70)
            print("2. HR MANAGER - Gokce Kaya Allende")
            print("-"*70)
            
            result = await db.execute(
                select(User).where(User.email == "gokce@inara.org")
            )
            gokce_user = result.scalar_one_or_none()
            
            if gokce_user:
                print(f"✓ Found user: {gokce_user.first_name} {gokce_user.last_name} ({gokce_user.email})")
                
                # Clear existing roles and add hr_manager
                gokce_user.roles.clear()
                gokce_user.roles.append(hr_role)
                print(f"✓ Updated role to HR Manager")
            else:
                # Create new user
                hashed_password = hash_password("password123")
                gokce_user = User(
                    email="gokce@inara.org",
                    first_name="Gokce",
                    last_name="Kaya Allende",
                    password_hash=hashed_password,
                    is_active=True,
                    is_superuser=False
                )
                db.add(gokce_user)
                await db.flush()
                
                gokce_user.roles.append(hr_role)
                print(f"✓ Created user: Gokce Kaya Allende (gokce@inara.org)")
                print(f"  Default password: password123")
            
            await db.commit()
            
            print("\n" + "="*70)
            print("✅ MANAGERS SETUP COMPLETED SUCCESSFULLY")
            print("="*70)
            print("\n📋 Account Details:\n")
            print("FINANCE MANAGER:")
            print(f"  Name: Mer Wais")
            print(f"  Email: mer@inara.org")
            print(f"  Password: password123")
            print(f"  Role: Finance Manager")
            
            print("\nHR MANAGER:")
            print(f"  Name: Gokce Kaya Allende")
            print(f"  Email: gokce@inara.org")
            print(f"  Password: password123")
            print(f"  Role: HR Manager")
            
            print("\n⚠️  IMPORTANT: Both users should change their passwords after first login!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error setting up managers: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(setup_managers())
