# Alembic Configuration
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from core.config import settings
from core.database import Base

# Import all models to ensure they are registered with Base
from modules.auth.models import User, Role, Permission
from modules.employees.models import Employee, Department, Position, Contract
from modules.recruitment.models import JobPosting, Application, Interview
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

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
