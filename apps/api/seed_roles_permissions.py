"""
Seed roles and permissions for INARA HR system
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.database import AsyncSessionLocal
from modules.employees.models import Employee  # Import first to resolve relationship
from modules.employee_files.models import Resignation, EmploymentContract, ContractExtension  # Import for relationships
from modules.auth.models import User, Role, Permission, user_roles, role_permissions


async def seed_roles_permissions():
    """Create basic roles and permissions and assign to all users"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if permissions already exist
            result = await session.execute(select(Permission))
            existing_perms = result.scalars().all()
            
            if existing_perms:
                print(f"Found {len(existing_perms)} existing permissions")
            else:
                # Create permissions
                permissions_data = [
                    {"name": "hr:read", "description": "Read HR data"},
                    {"name": "hr:write", "description": "Write/update HR data"},
                    {"name": "hr:admin", "description": "Full HR administration"},
                    {"name": "admin:all", "description": "Full system administration"},
                ]
                
                permissions = []
                for perm_data in permissions_data:
                    perm = Permission(**perm_data)
                    session.add(perm)
                    permissions.append(perm)
                
                await session.flush()
                print(f"Created {len(permissions)} permissions")
            
            # Refresh permissions
            result = await session.execute(select(Permission))
            all_permissions = {p.name: p for p in result.scalars().all()}
            
            # Check if roles already exist
            result = await session.execute(select(Role))
            existing_roles = result.scalars().all()
            existing_role_names = {r.name for r in existing_roles}
            
            print(f"Found {len(existing_roles)} existing roles: {existing_role_names}")
            
            # Define all roles that should exist
            roles_data = [
                {
                    "name": "hr_admin",
                    "display_name": "HR Administrator",
                    "description": "HR Administrator - full HR access",
                    "permissions": ["hr:admin", "hr:read", "hr:write"]
                },
                {
                    "name": "hr_manager",
                    "display_name": "HR Manager",
                    "description": "HR Manager - read/write access",
                    "permissions": ["hr:read", "hr:write"]
                },
                {
                    "name": "finance_manager",
                    "display_name": "Finance Manager",
                    "description": "Finance Manager - payroll and finance access",
                    "permissions": ["hr:read", "hr:write"]
                },
                {
                    "name": "employee",
                    "display_name": "Employee",
                    "description": "Regular Employee - basic access",
                    "permissions": ["hr:read"]
                },
                {
                    "name": "admin",
                    "display_name": "Administrator",
                    "description": "System Administrator",
                    "permissions": ["admin:all", "hr:admin", "hr:read", "hr:write"]
                }
            ]
            
            # Create missing roles
            roles_created = 0
            for role_data in roles_data:
                if role_data["name"] not in existing_role_names:
                    role = Role(
                        name=role_data["name"],
                        display_name=role_data["display_name"],
                        description=role_data["description"]
                    )
                    
                    # Add permissions to role
                    for perm_name in role_data["permissions"]:
                        if perm_name in all_permissions:
                            role.permissions.append(all_permissions[perm_name])
                    
                    session.add(role)
                    roles_created += 1
            
            if roles_created > 0:
                await session.flush()
                print(f"Created {roles_created} new roles")
            
            # Refresh roles
            result = await session.execute(select(Role))
            all_roles = {r.name: r for r in result.scalars().all()}
            
            # Get employee role
            employee_role = all_roles.get("employee")
            
            if not employee_role:
                print("ERROR: employee role not found!")
                return
            
            # Assign employee role to all users who don't have any roles
            result = await session.execute(
                select(User).options(selectinload(User.roles))
            )
            users = result.scalars().all()
            
            users_updated = 0
            for user in users:
                # Check if user already has roles
                if not user.roles:
                    user.roles.append(employee_role)
                    users_updated += 1
            
            await session.commit()
            
            print(f"\n=== Summary ===")
            print(f"Permissions: {len(all_permissions)}")
            print(f"Roles: {len(all_roles)}")
            print(f"Users updated with employee role: {users_updated}")
            print(f"Total users: {len(users)}")
            
            # Show role details
            print(f"\n=== Roles and Permissions ===")
            for role_name, role in all_roles.items():
                perms = [p.name for p in role.permissions]
                print(f"{role_name}: {', '.join(perms)}")
            
            print("\n✅ Roles and permissions seeded successfully!")
            
        except Exception as e:
            print(f"❌ Error seeding roles and permissions: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(seed_roles_permissions())
