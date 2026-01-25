"""
Initialize leave balances for all employees based on leave policies
Run this after creating or updating leave policies
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the apps/api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'api'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from decimal import Decimal

from core.database import Base
from modules.employees.models import Employee
from modules.leave.models import LeavePolicy, LeaveBalance


async def initialize_balances():
    """Initialize leave balances for all employees"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return
    
    print("🔗 Connecting to database...")
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Get current year
            current_year = str(datetime.now().year)
            
            # Get all active employees
            employees_result = await session.execute(
                select(Employee).where(
                    and_(
                        Employee.is_deleted == False,
                        Employee.status == 'active'
                    )
                )
            )
            employees = employees_result.scalars().all()
            print(f"👥 Found {len(employees)} active employees")
            
            if not employees:
                print("⚠️  No active employees found")
                return
            
            # Get all leave policies
            policies_result = await session.execute(
                select(LeavePolicy).where(LeavePolicy.is_deleted == False)
            )
            policies = policies_result.scalars().all()
            print(f"📋 Found {len(policies)} leave policies")
            
            if not policies:
                print("⚠️  No leave policies found. Create policies first!")
                return
            
            # Print policies
            for policy in policies:
                print(f"   - {policy.name}: {policy.leave_type} ({policy.days_per_year} days/year)")
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            # For each employee
            for emp in employees:
                emp_name = f"{emp.first_name} {emp.last_name}"
                print(f"\n👤 Processing {emp_name} ({emp.employee_number})...")
                
                # For each policy, create or update balance
                for policy in policies:
                    # Check if balance already exists
                    existing_balance_result = await session.execute(
                        select(LeaveBalance).where(
                            and_(
                                LeaveBalance.employee_id == emp.id,
                                LeaveBalance.leave_type == policy.leave_type,
                                LeaveBalance.year == current_year,
                                LeaveBalance.is_deleted == False
                            )
                        )
                    )
                    existing_balance = existing_balance_result.scalar_one_or_none()
                    
                    if existing_balance:
                        # Update if days changed
                        if existing_balance.total_days != policy.days_per_year:
                            old_total = existing_balance.total_days
                            existing_balance.total_days = policy.days_per_year
                            existing_balance.available_days = policy.days_per_year - existing_balance.used_days - existing_balance.pending_days
                            print(f"   ✏️  Updated {policy.leave_type}: {old_total} → {policy.days_per_year} days")
                            updated_count += 1
                        else:
                            print(f"   ⏭️  Skipped {policy.leave_type} (already exists)")
                            skipped_count += 1
                    else:
                        # Create new balance
                        balance = LeaveBalance(
                            employee_id=emp.id,
                            leave_type=policy.leave_type,
                            year=current_year,
                            total_days=policy.days_per_year,
                            used_days=Decimal("0"),
                            pending_days=Decimal("0"),
                            available_days=policy.days_per_year,
                            country_code=emp.country_code
                        )
                        session.add(balance)
                        print(f"   ✅ Created {policy.leave_type}: {policy.days_per_year} days")
                        created_count += 1
            
            # Commit all changes
            await session.commit()
            
            print(f"\n{'='*60}")
            print(f"✅ Initialization complete!")
            print(f"   Created: {created_count} balances")
            print(f"   Updated: {updated_count} balances")
            print(f"   Skipped: {skipped_count} balances")
            print(f"{'='*60}")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()


if __name__ == '__main__':
    print("🚀 Initializing leave balances for all employees...")
    print(f"📅 Year: {datetime.now().year}\n")
    asyncio.run(initialize_balances())
