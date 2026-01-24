#!/usr/bin/env python3
"""
Add permissions to existing roles using raw SQL - simple and direct
Run this to fix existing roles without permissions
"""
import asyncio
import sys
from pathlib import Path

# Add the API directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

from sqlalchemy import text
from core.database import AsyncSessionLocal
import uuid


async def fix_role_permissions_sql():
    """Add permissions to existing roles using raw SQL"""
    async with AsyncSessionLocal() as session:
        try:
            print("\n" + "="*70)
            print("FIXING ROLE PERMISSIONS (Raw SQL)")
            print("="*70)
            
            # 1. Create permissions if they don't exist
            permissions = [
                {"name": "hr:read", "resource": "hr", "action": "read", "description": "Read HR data"},
                {"name": "hr:write", "resource": "hr", "action": "write", "description": "Write/update HR data"},
                {"name": "hr:admin", "resource": "hr", "action": "admin", "description": "Full HR administration"},
                {"name": "admin:all", "resource": "admin", "action": "all", "description": "Full system administration"},
            ]
            
            print("\n1. Creating permissions...")
            for perm in permissions:
                result = await session.execute(
                    text("SELECT id FROM permissions WHERE name = :name"),
                    {"name": perm["name"]}
                )
                existing = result.first()
                
                if not existing:
                    perm_id = str(uuid.uuid4())
                    await session.execute(
                        text("""
                            INSERT INTO permissions (id, name, resource, action, description, created_at, updated_at)
                            VALUES (:id, :name, :resource, :action, :description, NOW(), NOW())
                        """),
                        {"id": perm_id, **perm}
                    )
                    print(f"✓ Created permission: {perm['name']}")
                else:
                    print(f"- Permission exists: {perm['name']}")
            
            await session.commit()
            
            # 2. Define which permissions each role should have
            role_permissions_map = {
                "super_admin": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "admin": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "ceo": ["admin:all", "hr:admin", "hr:read", "hr:write"],
                "hr_admin": ["hr:admin", "hr:read", "hr:write"],
                "hr_manager": ["hr:read", "hr:write"],
                "finance_manager": ["hr:read", "hr:write"],
                "employee": ["hr:read"]
            }
            
            print("\n2. Assigning permissions to roles...")
            roles_updated = 0
            
            for role_name, perm_names in role_permissions_map.items():
                # Check if role exists
                result = await session.execute(
                    text("SELECT id FROM roles WHERE name = :name"),
                    {"name": role_name}
                )
                role = result.first()
                
                if role:
                    role_id = role[0]
                    print(f"\nRole: {role_name}")
                    
                    # Get current permissions for this role
                    result = await session.execute(
                        text("""
                            SELECT p.name 
                            FROM permissions p
                            JOIN role_permissions rp ON p.id = rp.permission_id
                            WHERE rp.role_id = :role_id
                        """),
                        {"role_id": role_id}
                    )
                    current_perms = {row[0] for row in result}
                    print(f"  Current permissions: {list(current_perms) if current_perms else 'NONE'}")
                    print(f"  Expected permissions: {perm_names}")
                    
                    # Add missing permissions
                    for perm_name in perm_names:
                        if perm_name not in current_perms:
                            # Get permission ID
                            result = await session.execute(
                                text("SELECT id FROM permissions WHERE name = :name"),
                                {"name": perm_name}
                            )
                            perm = result.first()
                            
                            if perm:
                                perm_id = perm[0]
                                # Check if association already exists
                                result = await session.execute(
                                    text("""
                                        SELECT 1 FROM role_permissions 
                                        WHERE role_id = :role_id AND permission_id = :perm_id
                                    """),
                                    {"role_id": role_id, "perm_id": perm_id}
                                )
                                exists = result.first()
                                
                                if not exists:
                                    await session.execute(
                                        text("""
                                            INSERT INTO role_permissions (role_id, permission_id)
                                            VALUES (:role_id, :perm_id)
                                        """),
                                        {"role_id": role_id, "perm_id": perm_id}
                                    )
                                    print(f"  ✓ Added permission: {perm_name}")
                                    roles_updated += 1
                    
                    if all(p in current_perms for p in perm_names):
                        print(f"  ✓ Already has all permissions")
                else:
                    print(f"⚠️  Role not found: {role_name}")
            
            await session.commit()
            
            if roles_updated > 0:
                print(f"\n✅ Successfully added {roles_updated} permission(s) to roles")
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
    asyncio.run(fix_role_permissions_sql())
