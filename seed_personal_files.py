"""
Seed script to create sample personal file data
"""
import asyncio
import sys
from datetime import date, datetime, timedelta
from uuid import UUID

sys.path.insert(0, '/Users/maiwand/INARA-HR/apps/api')

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from modules.employee_files.models import (
    PersonalFileDocument,
    EmploymentContract,
    ContractExtension,
    Resignation,
    DocumentCategory,
    ContractStatus,
    ExtensionStatus,
    ResignationStatus
)
from modules.employees.models import Employee
from modules.auth.models import User


DATABASE_URL = "postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris"
engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_data():
    """Create sample personal file data"""
    print("\n🌱 Seeding Personal Files Data...")
    print("=" * 50)
    
    async with SessionLocal() as db:
        # Get first employee
        result = await db.execute(select(Employee).limit(1))
        employee = result.scalar_one_or_none()
        
        if not employee:
            print("❌ No employees found. Import employees first.")
            return
        
        print(f"✅ Using employee: {employee.first_name} {employee.last_name} ({employee.id})")
        
        # Get first user (for uploaded_by, created_by)
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No users found.")
            return
        
        print(f"✅ Using user: {user.email}")
        
        # Create a contract
        print("\n📄 Creating employment contract...")
        contract = EmploymentContract(
            employee_id=employee.id,
            contract_number=f"CON-2024-{employee.employee_number}",
            position_title=employee.position or "Software Engineer",
            location="Kabul, Afghanistan",
            contract_type="Fixed-Term",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            signed_date=date(2024, 1, 1),
            monthly_salary=2000.00,
            currency="USD",
            status=ContractStatus.ACTIVE,
            notice_period_days=30,
            country_code="AFG",
            created_by=user.id
        )
        db.add(contract)
        await db.flush()
        print(f"✅ Created contract: {contract.contract_number}")
        
        # Create a document
        print("\n📎 Creating sample document...")
        document = PersonalFileDocument(
            employee_id=employee.id,
            category=DocumentCategory.CONTRACT,
            title="Employment Contract 2024",
            description="Initial employment contract for 2024",
            file_path=f"/uploads/employees/{employee.id}/contract_2024.pdf",
            file_name="contract_2024.pdf",
            file_size=1024000,  # 1MB
            mime_type="application/pdf",
            uploaded_by=user.id,
            is_confidential=True,
            country_code="AFG",
            created_by=user.id
        )
        db.add(document)
        await db.flush()
        print(f"✅ Created document: {document.title}")
        
        # Create a contract extension
        print("\n📋 Creating contract extension...")
        extension = ContractExtension(
            contract_id=contract.id,
            employee_id=employee.id,
            extension_number=1,
            new_start_date=date(2025, 1, 1),
            new_end_date=date(2025, 6, 30),
            new_monthly_salary=2200.00,
            salary_change_reason="Annual performance increase",
            terms_changes="6-month extension with 10% salary increase",
            status=ExtensionStatus.PENDING,
            expires_at=date(2024, 12, 15),  # Expires 2 weeks before new start
            country_code="AFG",
            created_by=user.id
        )
        db.add(extension)
        await db.flush()
        print(f"✅ Created extension: Extension #{extension.extension_number}")
        
        await db.commit()
        
        print("\n" + "=" * 50)
        print("✅ Seeding completed successfully!")
        print(f"\n🔗 Test the Personal Files tab:")
        print(f"   http://localhost:3000/dashboard/employees/{employee.id}")
        print(f"\n🔗 Test API directly:")
        print(f"   http://localhost:8000/api/v1/employee-files/summary/{employee.id}")


async def main():
    try:
        await seed_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
