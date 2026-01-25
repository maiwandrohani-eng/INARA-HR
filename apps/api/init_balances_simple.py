"""
Simple script to initialize leave balances using direct SQL
"""
import asyncio
import os
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def initialize_balances():
    """Initialize leave balances for all employees"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Convert to asyncpg
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    # Remove sslmode
    if '?sslmode=' in database_url:
        database_url = database_url.split('?sslmode=')[0]
    elif '&sslmode=' in database_url:
        database_url = database_url.replace('&sslmode=require', '').replace('&sslmode=disable', '')
    
    print("🚀 Initializing leave balances...")
    print("🔗 Connecting to database...")
    
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        current_year = str(datetime.now().year)
        print(f"📅 Year: {current_year}\n")
        
        # Get active employees (remove status filter since enum might be different)
        employees = await conn.execute(
            text("SELECT id, first_name, last_name, employee_number, country_code FROM employees WHERE is_deleted = false")
        )
        employees = employees.fetchall()
        print(f"👥 Found {len(employees)} active employees")
        
        if not employees:
            print("⚠️  No active employees found")
            await engine.dispose()
            return
        
        # Get leave policies
        policies = await conn.execute(
            text("SELECT id, name, leave_type, days_per_year FROM leave_policies WHERE is_deleted = false")
        )
        policies = policies.fetchall()
        print(f"📋 Found {len(policies)} leave policies\n")
        
        if not policies:
            print("⚠️  No leave policies found. Create policies first!")
            await engine.dispose()
            return
        
        for policy in policies:
            print(f"   - {policy[1]}: {policy[2]} ({policy[3]} days/year)")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # For each employee and policy
        for emp in employees:
            emp_name = f"{emp[1]} {emp[2]}"
            print(f"\n👤 {emp_name} ({emp[3]})...")
            
            for policy in policies:
                # Check if balance exists
                existing = await conn.execute(
                    text("""
                        SELECT id, total_days, used_days, pending_days 
                        FROM leave_balances 
                        WHERE employee_id = :emp_id 
                          AND leave_type = :leave_type 
                          AND year = :year 
                          AND is_deleted = false
                    """),
                    {
                        "emp_id": str(emp[0]),
                        "leave_type": policy[2],
                        "year": current_year
                    }
                )
                existing = existing.fetchone()
                
                if existing:
                    # Update if days changed
                    if existing[1] != policy[3]:
                        new_available = policy[3] - existing[2] - existing[3]
                        await conn.execute(
                            text("""
                                UPDATE leave_balances 
                                SET total_days = :total, 
                                    available_days = :available,
                                    updated_at = NOW()
                                WHERE id = :id
                            """),
                            {
                                "total": policy[3],
                                "available": new_available,
                                "id": str(existing[0])
                            }
                        )
                        print(f"   ✏️  Updated {policy[2]}: {existing[1]} → {policy[3]} days")
                        updated_count += 1
                    else:
                        print(f"   ⏭️  Skipped {policy[2]} (already exists)")
                        skipped_count += 1
                else:
                    # Create new balance
                    await conn.execute(
                        text("""
                            INSERT INTO leave_balances 
                            (id, employee_id, leave_type, year, total_days, used_days, pending_days, available_days, country_code, is_deleted, created_at, updated_at)
                            VALUES 
                            (gen_random_uuid(), :emp_id, :leave_type, :year, :total, 0, 0, :total, :country, false, NOW(), NOW())
                        """),
                        {
                            "emp_id": str(emp[0]),
                            "leave_type": policy[2],
                            "year": current_year,
                            "total": policy[3],
                            "country": emp[4] or 'AF'
                        }
                    )
                    print(f"   ✅ Created {policy[2]}: {policy[3]} days")
                    created_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Initialization complete!")
        print(f"   Created: {created_count} balances")
        print(f"   Updated: {updated_count} balances")
        print(f"   Skipped: {skipped_count} balances")
        print(f"{'='*60}")
    
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(initialize_balances())
