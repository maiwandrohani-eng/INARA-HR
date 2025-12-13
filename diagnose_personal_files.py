"""
Diagnostic script for Personal Files Tab
Checks database tables, API endpoints, and data
"""
import asyncio
import sys
sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from sqlalchemy import inspect, select, text
from core.database import engine, get_db
from modules.employee_files.models import (
    PersonalFileDocument,
    EmploymentContract,
    ContractExtension,
    Resignation
)
from modules.employees.models import Employee


async def check_tables():
    """Check if required tables exist"""
    print("\n📋 Checking Database Tables...")
    print("=" * 50)
    
    async with engine.begin() as conn:
        def check_table(connection):
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            return tables
        
        tables = await conn.run_sync(check_table)
        
        required_tables = [
            'personal_file_documents',
            'employment_contracts',
            'contract_extensions',
            'resignations'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"✅ {table} - EXISTS")
            else:
                print(f"❌ {table} - MISSING")
        
        return all(table in tables for table in required_tables)


async def check_data():
    """Check if there's any data"""
    print("\n📊 Checking Data...")
    print("=" * 50)
    
    async with engine.begin() as conn:
        # Check employees
        result = await conn.execute(text("SELECT COUNT(*) FROM employees"))
        employee_count = result.scalar()
        print(f"Employees: {employee_count}")
        
        # Check documents
        result = await conn.execute(text("SELECT COUNT(*) FROM personal_file_documents"))
        doc_count = result.scalar()
        print(f"Documents: {doc_count}")
        
        # Check contracts
        result = await conn.execute(text("SELECT COUNT(*) FROM employment_contracts"))
        contract_count = result.scalar()
        print(f"Contracts: {contract_count}")
        
        # Check extensions
        result = await conn.execute(text("SELECT COUNT(*) FROM contract_extensions"))
        extension_count = result.scalar()
        print(f"Extensions: {extension_count}")
        
        # Check resignations
        result = await conn.execute(text("SELECT COUNT(*) FROM resignations"))
        resignation_count = result.scalar()
        print(f"Resignations: {resignation_count}")
        
        return {
            'employees': employee_count,
            'documents': doc_count,
            'contracts': contract_count,
            'extensions': extension_count,
            'resignations': resignation_count
        }


async def check_sample_employee():
    """Check a sample employee"""
    print("\n👤 Checking Sample Employee...")
    print("=" * 50)
    
    async with engine.begin() as conn:
        # Get first employee
        result = await conn.execute(
            text("SELECT id, first_name, last_name, employee_number FROM employees LIMIT 1")
        )
        employee = result.first()
        
        if employee:
            print(f"Sample Employee: {employee.first_name} {employee.last_name} ({employee.employee_number})")
            print(f"ID: {employee.id}")
            
            # Check their documents
            result = await conn.execute(
                text("SELECT COUNT(*) FROM personal_file_documents WHERE employee_id = :emp_id"),
                {"emp_id": employee.id}
            )
            docs = result.scalar()
            print(f"  Documents: {docs}")
            
            # Check their contracts
            result = await conn.execute(
                text("SELECT COUNT(*) FROM employment_contracts WHERE employee_id = :emp_id"),
                {"emp_id": employee.id}
            )
            contracts = result.scalar()
            print(f"  Contracts: {contracts}")
            
            return str(employee.id)
        else:
            print("❌ No employees found")
            return None


async def main():
    """Run all diagnostics"""
    print("\n" + "=" * 50)
    print("🔍 PERSONAL FILES TAB DIAGNOSTIC")
    print("=" * 50)
    
    try:
        # Check tables
        tables_ok = await check_tables()
        
        if not tables_ok:
            print("\n❌ ERROR: Missing required tables!")
            print("   Run: cd apps/api && alembic upgrade head")
            return
        
        # Check data
        data = await check_data()
        
        if data['employees'] == 0:
            print("\n⚠️  WARNING: No employees in database")
            print("   Import employees first")
        
        # Check sample employee
        employee_id = await check_sample_employee()
        
        print("\n" + "=" * 50)
        print("📝 RECOMMENDATIONS:")
        print("=" * 50)
        
        if data['employees'] > 0:
            print("✅ Database has employees")
        else:
            print("❌ Import employees: python import_employees.py")
        
        if data['contracts'] == 0:
            print("⚠️  No contracts found - create test contracts")
        
        if employee_id:
            print(f"\n🔗 Test URL:")
            print(f"   http://localhost:3000/dashboard/employees/{employee_id}")
            print(f"\n🔗 API Test:")
            print(f"   curl http://localhost:8000/api/v1/employee-files/summary/{employee_id}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
