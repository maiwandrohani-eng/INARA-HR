"""IMMEDIATE FIX: Add admin and ceo roles to maiwand@inara.org"""
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

async def fix_admin_now():
    """Add admin and ceo roles immediately"""
    print("🔧 FIXING ADMIN ACCESS FOR maiwand@inara.org...")
    print("="*60)
    
    async with AsyncSessionLocal() as session:
        try:
            # Find user
            result = await session.execute(
                select(User).where(User.email == "maiwand@inara.org")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User maiwand@inara.org not found!")
                return False
            
            print(f"✅ Found user: {user.email} (ID: {user.id})")
            
            # Get current roles
            current_roles = [r.name for r in user.roles]
            print(f"📋 Current roles: {current_roles}")
            
            # Get or create admin and ceo roles
            roles_needed = ["admin", "ceo"]
            roles_data = {
                "admin": {
                    "display_name": "Administrator",
                    "description": "System Administrator with full access",
                },
                "ceo": {
                    "display_name": "Chief Executive Officer",
                    "description": "CEO access - full organizational access",
                }
            }
            
            roles_to_add = []
            for role_name in roles_needed:
                if role_name in current_roles:
                    print(f"✅ User already has '{role_name}' role")
                    continue
                
                # Find or create role
                result = await session.execute(
                    select(Role).where(Role.name == role_name)
                )
                role = result.scalar_one_or_none()
                
                if not role:
                    print(f"⚠️  Creating '{role_name}' role...")
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_name,
                        display_name=roles_data[role_name]["display_name"],
                        description=roles_data[role_name]["description"],
                        is_system=True
                    )
                    session.add(role)
                    await session.flush()
                    print(f"✅ Created '{role_name}' role")
                else:
                    print(f"✅ Found '{role_name}' role")
                
                roles_to_add.append(role)
            
            if roles_to_add:
                # Add roles to user
                user.roles.extend(roles_to_add)
                await session.commit()
                
                # Refresh to get updated roles
                await session.refresh(user, ["roles"])
                new_roles = [r.name for r in user.roles]
                
                print("\n" + "="*60)
                print("✅ SUCCESS! Roles updated!")
                print("="*60)
                print(f"User: {user.email}")
                print(f"New roles: {new_roles}")
                print("\n⚠️  IMPORTANT: You must logout and login again!")
                print("   The frontend caches your user data.")
                print("="*60)
                return True
            else:
                print("\n✅ User already has all required roles!")
                print(f"   Roles: {current_roles}")
                print("\n⚠️  If you still don't see admin access:")
                print("   1. Logout from frontend")
                print("   2. Clear browser cache (Cmd+Shift+R)")
                print("   3. Login again")
                return True
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False

async def main():
    """Main function"""
    success = await fix_admin_now()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

