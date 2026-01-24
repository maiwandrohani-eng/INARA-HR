#!/usr/bin/env python3
"""
Add permissions to existing roles that don't have them
Run this on Railway to fix existing roles
"""
import asyncio
import sys
from pathlib import Path

# Add the API directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.database import AsyncSessionLocal

# Import all models to avoid relationship resolution errors
from modules.auth.models import Role, Permission, User
from modules.employees.models import Employee  # Import to resolve User.employee relationship
import uuid


async def fix_role_permissions():
    """Add permissions to existing roles"""
    async with AsyncSessionLocal() as session:
        try:
            print("\n" + "="*70)
            print("FIXING ROLE PERMISSIONS")
            print("="*70)
            
            # First, ensure all permissions exist
            permissions_to_create = [
                {"name": "hr:read", "resource": "hr", "action": "read", "description": "Read HR data"},
                {"name": "hr:write", "resource": "hr", "action": "write", "description": "Write/update HR data"},
                {"name": "hr:admin", "resource": "hr", "action": "admin", "description": "Full HR administration"},
                {"name": "admin:all", "resource": "admin", "action": "all", "description": "Full system administration"},
            ]
            
            created_permissions = {}
            for perm_data in permissions_to_create:
                result = await session.execute(
                    select(Permission).where(Permission.name == perm_data["name"])
                )
                perm = result.scalar_one_or_none()
                
                if not perm:
                    perm = Permission(
                        id=uuid.uuid4(),
                        name=perm_data["name"],
                        resource=perm_data["resource"],
                        action=perm_data["action"],
                        description=perm_data["description"]
                    )
                    session.add(perm)
                    print(f"✓ Created permission: {perm_data['name']}")
                else:
                    print(f"- Permission exists: {perm_data['name']}")
                
                created_permissions[perm_data["name"]] = perm
            
            await session.flush()
            
            # Define which permissions each role should have
            role_permissions_map = {
                "super_admin": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "admin": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "ceo": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "hr_admin": ["hr:admin", "hr:read", "hr:write"],
                "hr_manager": ["hr:read", "hr:write"],
                "finance_manager": ["hr:read", "hr:write"],
                "employee": ["hr:read"]
            }
            
            # Load all roles with their current permissions
            result = await session.execute(
                select(Role).options(selectinload(Role.permissions))
            )
            roles = result.scalars().all()
            
            print(f"\nFound {len(roles)} roles")
            print("-"*70)
            
            # Update each role with correct permissions
            roles_updated = 0
            for role in roles:
                if role.name in role_permissions_map:
                    expected_perms = role_permissions_map[role.name]
                    current_perm_names = {p.name for p in role.permissions}
                    
                    print(f"\nRole: {role.name}")
                    print(f"  Current permissions: {list(current_perm_names) if current_perm_names else 'NONE'}")
                    print(f"  Expected permissions: {expected_perms}")
                    
                    # Add missing permissions
                    missing_perms = set(expected_perms) - current_perm_names
                    if missing_perms:
                        for perm_name in missing_perms:
                            if perm_name in created_permissions:
                                role.permissions.append(created_permissions[perm_name])
                                print(f"  ✓ Added permission: {perm_name}")
                        roles_updated += 1
                    else:
                        print(f"  ✓ Already has all permissions")
            
            if roles_updated > 0:
                await session.commit()
                print(f"\n✅ Successfully updated {roles_updated} role(s) with permissions")
            else:
                print(f"\n✅ All roles already have correct permissions")
            
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error fixing role permissions: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(fix_role_permissions())
