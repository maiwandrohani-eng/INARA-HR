#!/usr/bin/env python3
"""
Update existing employees with new fields (salary, contracts, emergency contacts, etc.)
"""
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
sys.path.append('apps/api')

from core.database import AsyncSessionLocal
from core.models import Employee, Contract
from sqlalchemy import select


async def update_employees():
    async with AsyncSessionLocal() as db:
        try:
            # Fetch all existing employees
            result = await db.execute(select(Employee))
            employees = result.scalars().all()
            
            print(f"\n📋 Found {len(employees)} employees to update\n")
            
            for idx, emp in enumerate(employees, 1):
                print(f"Updating Employee {idx}: {emp.first_name} {emp.last_name} ({emp.employee_number})")
                
                # Update personal information fields
                if not emp.national_id:
                    emp.national_id = f"NID-{emp.employee_number}-{2024 + idx}"
                    print(f"  ✓ Added National ID: {emp.national_id}")
                
                if not emp.passport_number:
                    emp.passport_number = f"P{emp.employee_number}{1000 + idx}"
                    print(f"  ✓ Added Passport: {emp.passport_number}")
                
                # Update emergency contact information
                if not emp.emergency_contact_name:
                    emp.emergency_contact_name = f"Emergency Contact for {emp.first_name}"
                    emp.emergency_contact_phone = f"+93 70 123 {1000 + idx}"
                    emp.emergency_contact_relationship = "Spouse" if idx % 2 == 0 else "Parent"
                    print(f"  ✓ Added Emergency Contact: {emp.emergency_contact_name} ({emp.emergency_contact_relationship})")
                
                # Update probation end date (3 months after hire date)
                if not emp.probation_end_date and emp.hire_date:
                    emp.probation_end_date = emp.hire_date + timedelta(days=90)
                    print(f"  ✓ Set Probation End Date: {emp.probation_end_date}")
                
                # Check if employee already has a contract
                contract_result = await db.execute(
                    select(Contract).where(Contract.employee_id == emp.id)
                )
                existing_contract = contract_result.scalar_one_or_none()
                
                if not existing_contract:
                    # Create a contract for this employee
                    # Assign different salaries based on position
                    salary = Decimal('5000.00') if idx == 1 else Decimal('4500.00') if idx == 2 else Decimal('4000.00')
                    
                    # Get the next contract number
                    contract_count_result = await db.execute(select(Contract))
                    existing_contracts = contract_count_result.scalars().all()
                    contract_number = f"CON-{str(len(existing_contracts) + 1).zfill(4)}"
                    
                    contract = Contract(
                        contract_number=contract_number,
                        employee_id=emp.id,
                        contract_type="Permanent" if idx <= 2 else "Fixed-Term",
                        start_date=emp.hire_date or datetime.now().date(),
                        end_date=None if idx <= 2 else (datetime.now() + timedelta(days=365)).date(),
                        salary=salary,
                        currency="USD",
                        status="Active",
                        country_code=emp.country_code or "AF"
                    )
                    
                    db.add(contract)
                    print(f"  ✓ Created Contract: {contract_number} - ${salary}/month ({contract.contract_type})")
                else:
                    print(f"  ℹ Already has contract: {existing_contract.contract_number}")
                
                print()
            
            await db.commit()
            print("✅ All employees updated successfully!\n")
            
            # Display summary
            print("=" * 60)
            print("SUMMARY OF UPDATES")
            print("=" * 60)
            
            result = await db.execute(select(Employee))
            employees = result.scalars().all()
            
            for emp in employees:
                print(f"\n👤 {emp.first_name} {emp.last_name} ({emp.employee_number})")
                print(f"   National ID: {emp.national_id or 'Not set'}")
                print(f"   Passport: {emp.passport_number or 'Not set'}")
                print(f"   Emergency Contact: {emp.emergency_contact_name or 'Not set'}")
                if emp.emergency_contact_name:
                    print(f"   Emergency Phone: {emp.emergency_contact_phone}")
                    print(f"   Relationship: {emp.emergency_contact_relationship}")
                print(f"   Probation End: {emp.probation_end_date or 'Not set'}")
                
                # Get contract info
                contract_result = await db.execute(
                    select(Contract).where(Contract.employee_id == emp.id)
                )
                contract = contract_result.scalar_one_or_none()
                if contract:
                    print(f"   💼 Contract: {contract.contract_number}")
                    print(f"   Salary: {contract.currency} {contract.salary}/month")
                    print(f"   Type: {contract.contract_type}")
                    print(f"   Status: {contract.status}")
            
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"❌ Error updating employees: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(update_employees())
