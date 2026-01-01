#!/usr/bin/env python3
"""
Sync contracts data to employment_contracts table for payroll processing
"""
import asyncio
from datetime import datetime, date
from sqlalchemy import text
from core.database import AsyncSessionLocal


async def sync_contracts():
    async with AsyncSessionLocal() as db:
        try:
            print("\n📋 Syncing contracts to employment_contracts table...\n")
            
            # Get all contracts
            result = await db.execute(text("""
                SELECT c.id, c.contract_number, c.employee_id, c.salary, c.currency, 
                       c.contract_type, c.start_date, c.end_date, c.is_active, c.country_code,
                       c.created_at, c.updated_at,
                       e.position_id, e.work_location, e.first_name, e.last_name
                FROM contracts c
                JOIN employees e ON c.employee_id = e.id
                WHERE c.is_deleted = FALSE
            """))
            contracts = result.fetchall()
            
            print(f"Found {len(contracts)} contracts to sync\n")
            
            for contract in contracts:
                contract_id, contract_number, employee_id, salary, currency, contract_type, start_date, end_date, is_active, country_code, created_at, updated_at, position_id, work_location, first_name, last_name = contract
                
                # Check if already exists
                check = await db.execute(text("""
                    SELECT id FROM employment_contracts WHERE contract_number = :contract_number
                """), {"contract_number": contract_number})
                existing = check.fetchone()
                
                if existing:
                    print(f"  ℹ  {contract_number} already exists in employment_contracts")
                    continue
                
                # Determine status based on is_active
                status = 'ACTIVE' if is_active == 'true' else 'EXPIRED'
                
                # Insert into employment_contracts
                await db.execute(text("""
                    INSERT INTO employment_contracts (
                        id, employee_id, contract_number, position_title, location,
                        contract_type, start_date, end_date, monthly_salary, currency,
                        notice_period_days, status, country_code,
                        created_at, updated_at, is_deleted
                    ) VALUES (
                        gen_random_uuid(), :employee_id, :contract_number, :position_title, :location,
                        :contract_type, :start_date, :end_date, :monthly_salary, :currency,
                        30, :status, :country_code,
                        :created_at, :updated_at, FALSE
                    )
                """), {
                    "employee_id": str(employee_id),
                    "contract_number": contract_number,
                    "position_title": str(position_id) if position_id else "Staff Position",
                    "location": work_location or "Office",
                    "contract_type": contract_type or "Permanent",
                    "start_date": start_date,
                    "end_date": end_date or date(2099, 12, 31),  # Far future for permanent contracts
                    "monthly_salary": float(salary),
                    "currency": currency,
                    "status": status,
                    "country_code": country_code or "AF",
                    "created_at": created_at or datetime.now(),
                    "updated_at": updated_at or datetime.now()
                })
                
                print(f"  ✅ Synced {contract_number} for {first_name} {last_name} - ${salary} {currency}/month")
            
            await db.commit()
            
            # Show summary
            print("\n" + "=" * 60)
            print("SYNC COMPLETE")
            print("=" * 60)
            
            result = await db.execute(text("""
                SELECT ec.contract_number, e.first_name, e.last_name, e.employee_number,
                       ec.monthly_salary, ec.currency, ec.status
                FROM employment_contracts ec
                JOIN employees e ON ec.employee_id = e.id
                ORDER BY e.employee_number
            """))
            employment_contracts = result.fetchall()
            
            print(f"\n📊 Total Employment Contracts: {len(employment_contracts)}\n")
            for ec in employment_contracts:
                contract_num, first_name, last_name, emp_num, salary, currency, status = ec
                print(f"  {emp_num} - {first_name} {last_name}")
                print(f"    Contract: {contract_num}")
                print(f"    Salary: {currency} {salary}/month")
                print(f"    Status: {status}")
                print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(sync_contracts())
