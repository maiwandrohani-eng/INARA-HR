"""Update maiwand@inara.org with admin and ceo roles"""
import asyncio
import sys
import os
import uuid

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from modules.auth.models import User, Role

async def update_maiwand_roles():
    """Add admin and ceo roles to maiwand@inara.org"""
    print("🔄 Updating Maiwand user roles...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Find user
            result = await session.execute(
                select(User).where(User.email == "maiwand@inara.org")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User maiwand@inara.org not found!")
                return
            
            print(f"✅ Found user: {user.email}")
            print(f"   Current roles: {[r.name for r in user.roles]}")
            
            # Get or create required roles
            roles_to_check = ["admin", "ceo", "super_admin"]
            roles_data = {
                "admin": {
                    "display_name": "Administrator",
                    "description": "System Administrator with full access",
                },
                "ceo": {
                    "display_name": "Chief Executive Officer",
                    "description": "CEO access - full organizational access",
                },
                "super_admin": {
                    "display_name": "Super Administrator",
                    "description": "Full system access",
                }
            }
            
            existing_roles = {}
            for role_name in roles_to_check:
                result = await session.execute(
                    select(Role).where(Role.name == role_name)
                )
                role = result.scalar_one_or_none()
                
                if not role:
                    print(f"⚠️  {role_name} role not found. Creating it...")
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_name,
                        display_name=roles_data[role_name]["display_name"],
                        description=roles_data[role_name]["description"],
                        is_system=True
                    )
                    session.add(role)
                    await session.flush()
                    print(f"✅ Created {role_name} role")
                else:
                    print(f"✅ Found {role_name} role")
                
                existing_roles[role_name] = role
            
            # Check current user roles
            user_role_names = {r.name for r in user.roles}
            roles_to_add = []
            
            for role_name in ["admin", "ceo"]:
                if role_name not in user_role_names:
                    roles_to_add.append(existing_roles[role_name])
                    print(f"➕ Will add {role_name} role")
            
            if roles_to_add:
                user.roles.extend(roles_to_add)
                await session.commit()
                print("\n✅ Successfully updated user roles!")
                print(f"   User: {user.email}")
                print(f"   Roles: {[r.name for r in user.roles]}")
            else:
                print("\n✅ User already has all required roles!")
                print(f"   Roles: {[r.name for r in user.roles]}")
            
        except Exception as e:
            print(f"❌ Error updating roles: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise

async def main():
    """Main function"""
    try:
        await update_maiwand_roles()
        print("\n✅ Done! You can now logout and login again to see admin/CEO access.")
    except Exception as e:
        print(f"\n❌ Failed to update roles: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

