"""Create Maiwand user account for INARA HRIS"""
import asyncio
import sys
import os
import uuid

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from modules.auth.models import User, Role
from core.security import hash_password

async def create_maiwand_user():
    """Create Maiwand user account"""
    print("🚀 Creating Maiwand user account...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == "maiwand@inara.org")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ User maiwand@inara.org already exists!")
                print(f"   User ID: {existing_user.id}")
                print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
                print(f"   Active: {existing_user.is_active}")
                print(f"   Superuser: {existing_user.is_superuser}")
                return
            
            # Get or create super_admin role
            result = await session.execute(
                select(Role).where(Role.name == "super_admin")
            )
            super_admin_role = result.scalar_one_or_none()
            
            if not super_admin_role:
                # Create super_admin role if it doesn't exist
                print("⚠️  super_admin role not found. Creating it...")
                super_admin_role = Role(
                    id=uuid.uuid4(),
                    name="super_admin",
                    display_name="Super Administrator",
                    description="Full system access",
                    is_system=True
                )
                session.add(super_admin_role)
                await session.flush()
                print("✅ Created super_admin role")
            
            # Create Maiwand user
            print("Creating user: maiwand@inara.org...")
            maiwand_user = User(
                id=uuid.uuid4(),
                email="maiwand@inara.org",
                hashed_password=hash_password("Come*1234"),
                first_name="Maiwand",
                last_name="User",
                country_code="AF",
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            
            # Assign super_admin role
            maiwand_user.roles.append(super_admin_role)
            
            session.add(maiwand_user)
            await session.commit()
            
            print("✅ User created successfully!")
            print("\n" + "="*50)
            print("Login Credentials:")
            print("="*50)
            print(f"Email: maiwand@inara.org")
            print(f"Password: Come*1234")
            print(f"User ID: {maiwand_user.id}")
            print(f"Name: {maiwand_user.first_name} {maiwand_user.last_name}")
            print(f"Country: {maiwand_user.country_code}")
            print(f"Superuser: {maiwand_user.is_superuser}")
            print("="*50)
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise

async def main():
    """Main function"""
    try:
        await create_maiwand_user()
        print("\n✅ Done! You can now login with maiwand@inara.org")
    except Exception as e:
        print(f"\n❌ Failed to create user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

