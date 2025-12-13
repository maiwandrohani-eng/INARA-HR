"""Create all database tables"""
import asyncio
from core.database import async_engine, Base

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
    print("Creating all tables...")
    async with async_engine.begin() as conn:
        # Drop all tables first
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
