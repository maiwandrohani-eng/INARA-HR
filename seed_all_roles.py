#!/usr/bin/env python3
"""
Seed ALL required roles in the database
Run this on Railway or any deployed environment to ensure all roles exist
"""
import asyncio
import sys
from pathlib import Path

# Add the API directory to the path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

from sqlalchemy import select
from core.database import AsyncSessionLocal
from modules.auth.models import Role
import uuid


async def seed_all_roles():
    """Create all required roles if they don't exist"""
    async with AsyncSessionLocal() as session:
        try:
            print("\n" + "="*70)
            print("SEEDING ALL REQUIRED ROLES")
            print("="*70)
            
            # Define all roles that should exist
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
                },
                {
                    "name": "hr_admin",
                    "display_name": "HR Administrator",
                    "description": "HR Administrator - full HR access",
                    "is_system": True
                },
                {
                    "name": "hr_manager",
                    "display_name": "HR Manager",
                    "description": "HR Manager - read/write access",
                    "is_system": True
                },
                {
                    "name": "finance_manager",
                    "display_name": "Finance Manager",
                    "description": "Finance Manager - payroll and finance access",
                    "is_system": True
                },
                {
                    "name": "employee",
                    "display_name": "Employee",
                    "description": "Regular Employee - basic access",
                    "is_system": False
                }
            ]
            
            # Check which roles exist
            result = await session.execute(select(Role))
            existing_roles = {r.name: r for r in result.scalars().all()}
            
            print(f"\nExisting roles: {list(existing_roles.keys())}")
            print(f"Total existing: {len(existing_roles)}\n")
            
            # Create missing roles
            roles_created = 0
            for role_data in roles_to_create:
                if role_data["name"] not in existing_roles:
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_data["name"],
                        display_name=role_data["display_name"],
                        description=role_data["description"],
                        is_system=role_data["is_system"]
                    )
                    session.add(role)
                    roles_created += 1
                    print(f"✓ Created role: {role_data['name']} ({role_data['display_name']})")
                else:
                    print(f"- Role already exists: {role_data['name']}")
            
            if roles_created > 0:
                await session.commit()
                print(f"\n✅ Successfully created {roles_created} new role(s)")
            else:
                print(f"\n✅ All roles already exist - no changes needed")
            
            # Show final count
            result = await session.execute(select(Role))
            all_roles = result.scalars().all()
            print(f"\nTotal roles in database: {len(all_roles)}")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error seeding roles: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_all_roles())
