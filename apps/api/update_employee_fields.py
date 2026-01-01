#!/usr/bin/env python3
"""
Update existing employees with new fields (salary, contracts, emergency contacts, etc.)
"""
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from core.database import AsyncSessionLocal
from sqlalchemy import text


async def update_employees():
    async with AsyncSessionLocal() as db:
        try:
            # Fetch all existing employees
            result = await db.execute(text("SELECT id, employee_number, first_name, last_name, hire_date, country_code FROM employees ORDER BY employee_number"))
            employees = result.fetchall()
            
            print(f"\n📋 Found {len(employees)} employees to update\n")
            
            for idx, emp in enumerate(employees, 1):
                emp_id, emp_number, first_name, last_name, hire_date, country_code = emp
                print(f"Updating Employee {idx}: {first_name} {last_name} ({emp_number})")
                
                # Update personal information fields
                national_id = f"NID-{emp_number}-{2024 + idx}"
                passport_number = f"P{emp_number}{1000 + idx}"
                
                await db.execute(text("""
                    UPDATE employees 
                    SET national_id = :national_id,
                        passport_number = :passport_number
                    WHERE id = :emp_id AND (national_id IS NULL OR national_id = '')
                """), {"national_id": national_id, "passport_number": passport_number, "emp_id": emp_id})
                print(f"  ✓ Added National ID: {national_id}")
                print(f"  ✓ Added Passport: {passport_number}")
                
                # Update emergency contact information
                emergency_contact_name = f"Emergency Contact for {first_name}"
                emergency_contact_phone = f"+93 70 123 {1000 + idx}"
                emergency_contact_relationship = "Spouse" if idx % 2 == 0 else "Parent"
                
                await db.execute(text("""
                    UPDATE employees 
                    SET emergency_contact_name = :name,
                        emergency_contact_phone = :phone,
                        emergency_contact_relationship = :relationship
                    WHERE id = :emp_id AND (emergency_contact_name IS NULL OR emergency_contact_name = '')
                """), {
                    "name": emergency_contact_name,
                    "phone": emergency_contact_phone,
                    "relationship": emergency_contact_relationship,
                    "emp_id": emp_id
                })
                print(f"  ✓ Added Emergency Contact: {emergency_contact_name} ({emergency_contact_relationship})")
                
                # Update probation end date (3 months after hire date)
                if hire_date:
                    probation_end = hire_date + timedelta(days=90)
                    await db.execute(text("""
                        UPDATE employees 
                        SET probation_end_date = :probation_end
                        WHERE id = :emp_id AND probation_end_date IS NULL
                    """), {"probation_end": probation_end, "emp_id": emp_id})
                    print(f"  ✓ Set Probation End Date: {probation_end}")
                
                # Check if employee already has a contract
                contract_check = await db.execute(text("SELECT contract_number FROM contracts WHERE employee_id = :emp_id"), {"emp_id": emp_id})
                existing_contract = contract_check.fetchone()
                
                if not existing_contract:
                    # Create a contract for this employee
                    salary = Decimal('5000.00') if idx == 1 else Decimal('4500.00') if idx == 2 else Decimal('4000.00')
                    
                    # Get the next contract number
                    contract_count = await db.execute(text("SELECT COUNT(*) FROM contracts"))
                    count = contract_count.scalar()
                    contract_number = f"CON-{str(count + 1).zfill(4)}"
                    
                    contract_type = "Permanent" if idx <= 2 else "Fixed-Term"
                    start_date = hire_date or datetime.now().date()
                    end_date = None if idx <= 2 else (datetime.now() + timedelta(days=365)).date()
                    
                    await db.execute(text("""
                        INSERT INTO contracts (id, contract_number, employee_id, contract_type, start_date, end_date, salary, currency, salary_frequency, is_active, is_deleted, country_code, created_at, updated_at)
                        VALUES (gen_random_uuid(), :contract_number, :employee_id, :contract_type, :start_date, :end_date, :salary, :currency, :salary_frequency, :is_active, FALSE, :country_code, NOW(), NOW())
                    """), {
                        "contract_number": contract_number,
                        "employee_id": emp_id,
                        "contract_type": contract_type,
                        "start_date": start_date,
                        "end_date": end_date,
                        "salary": float(salary),
                        "currency": "USD",
                        "salary_frequency": "Monthly",
                        "is_active": "true",
                        "country_code": country_code or "AF"
                    })
                    
                    print(f"  ✓ Created Contract: {contract_number} - ${salary}/month ({contract_type})")
                else:
                    print(f"  ℹ Already has contract: {existing_contract[0]}")
                
                print()
            
            await db.commit()
            print("✅ All employees updated successfully!\n")
            
            # Display summary
            print("=" * 60)
            print("SUMMARY OF UPDATES")
            print("=" * 60)
            
            result = await db.execute(text("""
                SELECT e.first_name, e.last_name, e.employee_number, e.national_id, e.passport_number,
                       e.emergency_contact_name, e.emergency_contact_phone, e.emergency_contact_relationship,
                       e.probation_end_date, c.contract_number, c.salary, c.currency, c.contract_type, c.is_active
                FROM employees e
                LEFT JOIN contracts c ON e.id = c.employee_id
                ORDER BY e.employee_number
            """))
            employees = result.fetchall()
            
            for emp in employees:
                first_name, last_name, emp_number, national_id, passport, ec_name, ec_phone, ec_rel, prob_end, contract_num, salary, currency, contract_type, is_active = emp
                print(f"\n👤 {first_name} {last_name} ({emp_number})")
                print(f"   National ID: {national_id or 'Not set'}")
                print(f"   Passport: {passport or 'Not set'}")
                print(f"   Emergency Contact: {ec_name or 'Not set'}")
                if ec_name:
                    print(f"   Emergency Phone: {ec_phone}")
                    print(f"   Relationship: {ec_rel}")
                print(f"   Probation End: {prob_end or 'Not set'}")
                
                if contract_num:
                    print(f"   💼 Contract: {contract_num}")
                    print(f"   Salary: {currency} {salary}/month")
                    print(f"   Type: {contract_type}")
                    print(f"   Status: {'Active' if is_active == 'true' else 'Inactive'}")
            
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"❌ Error updating employees: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(update_employees())
