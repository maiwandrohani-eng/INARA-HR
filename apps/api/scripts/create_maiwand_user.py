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
            
            # Get or create required roles (admin, ceo, super_admin)
            roles_to_create = [
                {
                    "name": "super_admin",
                    "display_name": "Super Administrator",
                    "description": "Full system access",
                    "is_system": True
                },
                {
                    "name": "admin",
                    "display_name": "Administrator",
                    "description": "System Administrator with full access",
                    "is_system": True
                },
                {
                    "name": "ceo",
                    "display_name": "Chief Executive Officer",
                    "description": "CEO access - full organizational access",
                    "is_system": True
                }
            ]
            
            created_roles = {}
            for role_data in roles_to_create:
                result = await session.execute(
                    select(Role).where(Role.name == role_data["name"])
                )
                role = result.scalar_one_or_none()
                
                if not role:
                    print(f"⚠️  {role_data['name']} role not found. Creating it...")
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_data["name"],
                        display_name=role_data["display_name"],
                        description=role_data["description"],
                        is_system=role_data["is_system"]
                    )
                    session.add(role)
                    await session.flush()
                    print(f"✅ Created {role_data['name']} role")
                else:
                    print(f"✅ Found existing {role_data['name']} role")
                
                created_roles[role_data["name"]] = role
            
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
            
            # Assign all three roles for full access (admin, ceo, super_admin)
            maiwand_user.roles.extend([
                created_roles["super_admin"],
                created_roles["admin"],
                created_roles["ceo"]
            ])
            
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

