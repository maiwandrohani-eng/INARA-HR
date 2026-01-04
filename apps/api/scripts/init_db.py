"""Initialize database: Create tables and seed initial data"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import async_engine, Base
from core.config import settings

# Import all models to register them with Base
from modules.auth.models import User, Role, Permission
from modules.employees.models import Employee, Department, Position, Contract, EmployeeDocument
from modules.recruitment.models import JobPosting, Application, Interview, OfferLetter
from modules.leave.models import LeavePolicy, LeaveBalance, LeaveRequest, AttendanceRecord
from modules.timesheets.models import Project, Timesheet, TimesheetEntry
from modules.performance.models import PerformanceGoal, PerformanceReview, PerformanceImprovementPlan
from modules.learning.models import TrainingCourse, TrainingEnrollment
from modules.compensation.models import SalaryHistory
from modules.safeguarding.models import SafeguardingCase
from modules.grievance.models import Grievance, DisciplinaryAction
from modules.travel.models import TravelRequest, VisaRecord
from modules.admin.models import CountryConfig, SalaryBand
from modules.onboarding.models import OnboardingChecklist

async def create_tables():
    """Create all tables in the database"""
    print("📦 Creating database tables...")
    try:
        async with async_engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_tables_exist():
    """Check if tables already exist"""
    try:
        from sqlalchemy import inspect
        async with async_engine.connect() as conn:
            inspector = inspect(await conn.get_sync_engine())
            tables = inspector.get_table_names()
            if 'users' in tables:
                print(f"✅ Database already initialized ({len(tables)} tables found)")
                return True
        return False
    except Exception as e:
        print(f"⚠️  Could not check existing tables: {e}")
        return False

async def main():
    """Main initialization function"""
    print("🚀 Starting database initialization...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'hidden'}")
    
    # Check if tables already exist
    if await check_tables_exist():
        print("✅ Database already initialized, skipping table creation")
        return
    
    # Create tables
    success = await create_tables()
    
    if success:
        print("✅ Database initialization complete!")
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

