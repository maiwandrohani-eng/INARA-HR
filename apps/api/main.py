"""
INARA HRIS - Main FastAPI Application
Fast, scalable HR Management System backend
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
import os

from core.config import settings
from core.database import engine, Base
from core.exceptions import BaseHTTPException

# Configure centralized logging FIRST (before any logger usage)
import sys
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure root logger
log_level = logging.DEBUG if settings.DEBUG else logging.INFO
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
date_format = '%Y-%m-%d %H:%M:%S'

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# File handler with rotation
file_handler = RotatingFileHandler(
    'logs/inara-hris.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Error file handler (only errors)
error_handler = RotatingFileHandler(
    'logs/inara-hris-errors.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

# Configure root logger
logging.basicConfig(
    level=log_level,
    format=log_format,
    datefmt=date_format,
    handlers=[console_handler, file_handler, error_handler]
)

logger = logging.getLogger(__name__)
logger.info("Logging system initialized")

# Initialize Sentry for error tracking (optional)
try:
    if settings.SENTRY_DSN and settings.ENVIRONMENT == "production":
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
            )
            logger.info("Sentry error tracking initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed. Error tracking disabled.")
except Exception as e:
    logger.warning(f"Failed to initialize Sentry: {e}")

# Initialize rate limiting
if settings.RATE_LIMIT_ENABLED:
    try:
        from core.rate_limit import limiter, rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded
        rate_limiting_enabled = True
    except Exception as e:
        logger.warning(f"Failed to initialize rate limiting: {e}")
        rate_limiting_enabled = False
else:
    rate_limiting_enabled = False

# Import all routers
from modules.auth.routes import router as auth_router
from modules.employees.routes import router as employees_router
from modules.recruitment.routes import router as recruitment_router
from modules.onboarding.routes import router as onboarding_router
from modules.leave.routes import router as leave_router
from modules.timesheets.routes import router as timesheets_router
from modules.performance.routes import router as performance_router
from modules.learning.routes import router as learning_router
from modules.compensation.routes import router as compensation_router
from modules.safeguarding.routes import router as safeguarding_router
from modules.grievance.routes import router as grievance_router
from modules.travel.routes import router as travel_router
from modules.analytics.routes import router as analytics_router
from modules.admin.routes import router as admin_router
from modules.ess.routes import router as ess_router
from modules.dashboard.routes import router as dashboard_router
from modules.approvals.routes import router as approvals_router
from modules.employee_files.routes import router as employee_files_router
from modules.payroll.routes import router as payroll_router
from modules.benefits.routes import router as benefits_router
from modules.assets.routes import router as assets_router
from modules.expenses.routes import router as expenses_router
from modules.notifications.routes import router as notifications_router
from modules.compliance.routes import router as compliance_router
from modules.succession.routes import router as succession_router
from modules.engagement.routes import router as engagement_router
from modules.workforce.routes import router as workforce_router
from modules.exit_management.routes import router as exit_management_router

# Logging is already configured above


# Helper functions for user/role initialization (defined before lifespan)
async def create_initial_user_background():
    """Create initial user in background (non-blocking)"""
    from sqlalchemy import select
    from core.database import AsyncSessionLocal
    from modules.auth.models import User, Role
    from core.security import hash_password
    import uuid
    
    async with AsyncSessionLocal() as user_session:
        # Check if user exists
        result = await user_session.execute(
            select(User).where(User.email == "maiwand@inara.org")
        )
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            logger.info("Creating initial user: maiwand@inara.org...")
            
            # Get or create ALL required roles
            roles_to_create = [
                {"name": "super_admin", "display_name": "Super Administrator", "description": "Full system access", "is_system": True},
                {"name": "admin", "display_name": "Administrator", "description": "System Administrator with full access", "is_system": True},
                {"name": "ceo", "display_name": "Chief Executive Officer", "description": "CEO access - full organizational access", "is_system": True},
                {"name": "hr_admin", "display_name": "HR Administrator", "description": "HR Administrator - full HR access", "is_system": True},
                {"name": "hr_manager", "display_name": "HR Manager", "description": "HR Manager - read/write access", "is_system": True},
                {"name": "finance_manager", "display_name": "Finance Manager", "description": "Finance Manager - payroll and finance access", "is_system": True},
                {"name": "employee", "display_name": "Employee", "description": "Regular Employee - basic access", "is_system": False}
            ]
            
            created_roles = {}
            for role_data in roles_to_create:
                result = await user_session.execute(
                    select(Role).where(Role.name == role_data["name"])
                )
                role = result.scalar_one_or_none()
                
                if not role:
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_data["name"],
                        display_name=role_data["display_name"],
                        description=role_data["description"],
                        is_system=role_data["is_system"]
                    )
                    user_session.add(role)
                    await user_session.flush()
                    logger.info(f"Created role: {role_data['name']}")
                
                created_roles[role_data["name"]] = role
            
            # Create user with admin, ceo, and super_admin roles
            maiwand_user = User(
                id=uuid.uuid4(),
                email="maiwand@inara.org",
                hashed_password=hash_password("Come*1234"),
                first_name="Maiwand",
                last_name="User",
                country_code="AF",
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            
            # Assign all three roles for full access
            maiwand_user.roles.extend([
                created_roles["super_admin"],
                created_roles["admin"],
                created_roles["ceo"]
            ])
            
            user_session.add(maiwand_user)
            await user_session.commit()
            logger.info("✅ Initial user (maiwand@inara.org) created successfully with admin, ceo, and super_admin roles!")


async def update_maiwand_roles_background():
    """Update existing user roles in background (non-blocking)"""
    from sqlalchemy import select
    from core.database import AsyncSessionLocal
    from modules.auth.models import User, Role
    import uuid
    
    async with AsyncSessionLocal() as user_session:
        # Check if user exists
        result = await user_session.execute(
            select(User).where(User.email == "maiwand@inara.org")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # User exists, ensure they have admin and ceo roles
            result = await user_session.execute(
                select(Role).where(Role.name.in_(["admin", "ceo", "super_admin", "hr_admin", "hr_manager", "finance_manager", "employee"]))
            )
            existing_roles = {r.name: r for r in result.scalars().all()}
            
            # Create missing roles
            for role_name in ["admin", "ceo", "super_admin", "hr_admin", "hr_manager", "finance_manager", "employee"]:
                if role_name not in existing_roles:
                    role_display = {
                        "admin": "Administrator",
                        "ceo": "Chief Executive Officer",
                        "super_admin": "Super Administrator",
                        "hr_admin": "HR Administrator",
                        "hr_manager": "HR Manager",
                        "finance_manager": "Finance Manager",
                        "employee": "Employee"
                    }
                    role = Role(
                        id=uuid.uuid4(),
                        name=role_name,
                        display_name=role_display[role_name],
                        description=f"{role_display[role_name]} access",
                        is_system=role_name != "employee"  # Only employee role is not a system role
                    )
                    user_session.add(role)
                    await user_session.flush()
                    existing_roles[role_name] = role
            
            # Add missing roles to user (include super_admin as well)
            user_role_names = {r.name for r in existing_user.roles}
            roles_to_add = []
            for role_name in ["admin", "ceo", "super_admin"]:
                if role_name not in user_role_names:
                    roles_to_add.append(existing_roles[role_name])
            
            if roles_to_add:
                existing_user.roles.extend(roles_to_add)
                await user_session.commit()
                logger.info(f"✅ Added roles {[r.name for r in roles_to_add]} to existing user: maiwand@inara.org")
            else:
                logger.info(f"✅ User maiwand@inara.org already has all required roles: {list(user_role_names)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting INARA HRIS API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    # Import database and cache functions
    from core.database import verify_db_connection, close_db
    from core.monitoring import db_monitor
    from core.cache import init_redis, close_redis
    
    # Verify database connection
    logger.info("Verifying database connection...")
    try:
        db_connected = await verify_db_connection()
        if not db_connected:
            logger.error("❌ Failed to connect to database. Please check your DATABASE_ASYNC_URL configuration.")
            logger.warning("⚠️  Application will start but database operations may fail")
        else:
            logger.info("✅ Database connection verified")
    except Exception as db_conn_error:
        logger.error(f"❌ Database connection error: {db_conn_error}")
        logger.warning("⚠️  Application will start but database operations may fail")
    
    # Check if tables exist, create if they don't
    from sqlalchemy import text
    from core.database import async_engine
    try:
        # Try to query the users table to check if it exists
        async with async_engine.connect() as conn:
            try:
                result = await conn.execute(text("SELECT 1 FROM users LIMIT 1"))
                await result.fetchone()
                logger.info("✅ Database tables already exist")
                
                # Tables exist, try to update user roles in background (don't block startup)
                try:
                    await update_maiwand_roles_background()
                except Exception as bg_error:
                    logger.warning(f"⚠️  Background role update failed (non-critical): {bg_error}")
                    
            except Exception:
                # Table doesn't exist, create all tables
                logger.warning("⚠️  Database tables not found. Creating tables...")
                try:
                    from core.database import Base
                    # Import all models to register them with Base.metadata
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
                    
                    # Create all tables
                    async with async_engine.begin() as create_conn:
                        await create_conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ Database tables created successfully!")
                    
                    # After creating tables, try to create initial user (non-blocking)
                    try:
                        await create_initial_user_background()
                    except Exception as user_error:
                        logger.warning(f"⚠️  Could not create initial user automatically: {user_error}")
                        logger.warning("⚠️  You can create it manually by running: python scripts/create_maiwand_user.py")
                        
                except Exception as table_error:
                    logger.error(f"❌ Failed to create tables: {table_error}")
                    logger.warning("⚠️  You may need to run: python scripts/init_db.py manually")
                    # Don't raise - allow app to start even if tables can't be created
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.warning("⚠️  Application will start but database operations may fail")
        import traceback
        logger.debug(traceback.format_exc())
        # Don't raise - allow app to start even if initialization fails
    
    # Initialize Redis cache (non-blocking)
    try:
        await init_redis()
        logger.info("✅ Redis cache initialized")
    except Exception as redis_error:
        logger.warning(f"⚠️  Redis initialization failed (non-critical): {redis_error}")
        logger.warning("⚠️  Application will continue without Redis caching")
    
    # Start database monitoring (non-blocking)
    try:
        db_monitor.start_monitoring()
        logger.info("📊 Database monitoring enabled")
    except Exception as monitor_error:
        logger.warning(f"⚠️  Database monitoring initialization failed (non-critical): {monitor_error}")
        logger.warning("⚠️  Application will continue without monitoring")
    
    logger.info("✅ All systems initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down INARA HRIS API...")
    
    # Stop monitoring
    db_monitor.stop_monitoring()
    
    # Close cache connection
    await close_redis()
    
    # Close database connections
    await close_db()
    logger.info("✅ Cleanup completed")


# Initialize FastAPI application
app = FastAPI(
    title="INARA HRIS API",
    description="Comprehensive HR Management System for Multi-Country NGO Operations",
    version="1.0.0",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)

# Add rate limiting if enabled
if rate_limiting_enabled:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# ============================================
# MIDDLEWARE
# ============================================

# CORS Middleware
# Support both specific origins and wildcard patterns for Vercel preview deployments
cors_origins = settings.get_cors_origins()

# Add custom domain and Vercel preview regex patterns
# Allow: https://hrmis.inara.ngo (production domain)
# Allow: *.vercel.app (all Vercel preview deployments)
cors_origin_regex = r"https://.*\.vercel\.app|https://hrmis\.inara\.ngo"

# Ensure custom domain is in allowed origins list
if "https://hrmis.inara.ngo" not in cors_origins:
    cors_origins.append("https://hrmis.inara.ngo")

logger.info(f"CORS configured with origins: {cors_origins}")
logger.info(f"CORS regex pattern: {cors_origin_regex}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with enhanced logging"""
    client_ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get("user-agent", "unknown")
    
    logger.info(
        f"🌐 {request.method} {request.url.path} - "
        f"Client: {client_ip} - "
        f"User-Agent: {user_agent[:50]}"
    )
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log with appropriate level based on status code
        if response.status_code >= 500:
            logger.error(
                f"❌ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
        elif response.status_code >= 400:
            logger.warning(
                f"⚠️ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
        else:
            logger.info(
                f"✅ {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"💥 {request.method} {request.url.path} - "
            f"Exception: {str(e)} - "
            f"Time: {process_time:.4f}s",
            exc_info=True
        )
        raise


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(BaseHTTPException)
async def http_exception_handler(request: Request, exc: BaseHTTPException):
    """Handle custom HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )


# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "message": "INARA HRIS API",
        "version": "1.0.0",
        "docs": f"{settings.API_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with database and system metrics
    
    Returns comprehensive health information including:
    - Database connection status
    - Connection pool statistics
    - Database table verification
    - Response times
    """
    from core.health import check_database_health, check_database_tables, get_db_connection_info
    from core.monitoring import get_monitoring_stats
    from datetime import datetime
    
    db_health = await check_database_health()
    tables_status = await check_database_tables()
    connection_info = await get_db_connection_info()
    monitoring_stats = get_monitoring_stats()
    
    overall_healthy = db_health.get("healthy", False) and tables_status.get("healthy", False)
    
    return {
        "success": True,
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": db_health,
            "tables": tables_status,
            "connection": connection_info
        },
        "monitoring": monitoring_stats
    }


# Include all module routers
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix=f"{settings.API_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(employees_router, prefix=f"{settings.API_PREFIX}/employees", tags=["Employees"])
app.include_router(recruitment_router, prefix=f"{settings.API_PREFIX}/recruitment", tags=["Recruitment"])
app.include_router(onboarding_router, prefix=f"{settings.API_PREFIX}/onboarding", tags=["Onboarding"])
app.include_router(leave_router, prefix=f"{settings.API_PREFIX}/leave", tags=["Leave & Attendance"])
app.include_router(timesheets_router, prefix=f"{settings.API_PREFIX}/timesheets", tags=["Timesheets"])
app.include_router(performance_router, prefix=f"{settings.API_PREFIX}/performance", tags=["Performance"])
app.include_router(learning_router, prefix=f"{settings.API_PREFIX}/learning", tags=["Learning & Development"])
app.include_router(compensation_router, prefix=f"{settings.API_PREFIX}/compensation", tags=["Compensation"])
app.include_router(safeguarding_router, prefix=f"{settings.API_PREFIX}/safeguarding", tags=["Safeguarding"])
app.include_router(grievance_router, prefix=f"{settings.API_PREFIX}", tags=["Grievance & Disciplinary"])
app.include_router(travel_router, prefix=f"{settings.API_PREFIX}/travel", tags=["Travel & Deployment"])
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(admin_router, prefix=f"{settings.API_PREFIX}/admin", tags=["Administration"])
app.include_router(ess_router, prefix=f"{settings.API_PREFIX}/ess", tags=["Employee Self-Service"])
app.include_router(approvals_router, prefix=f"{settings.API_PREFIX}", tags=["Approvals"])
app.include_router(employee_files_router, prefix=f"{settings.API_PREFIX}", tags=["Employee Files"])
app.include_router(payroll_router, prefix=f"{settings.API_PREFIX}", tags=["Payroll"])
app.include_router(benefits_router, prefix=f"{settings.API_PREFIX}/benefits", tags=["Benefits"])
app.include_router(assets_router, prefix=f"{settings.API_PREFIX}/assets", tags=["Assets"])
app.include_router(expenses_router, prefix=f"{settings.API_PREFIX}/expenses", tags=["Expenses"])
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(compliance_router, prefix=f"{settings.API_PREFIX}/compliance", tags=["Compliance"])
app.include_router(succession_router, prefix=f"{settings.API_PREFIX}/succession", tags=["Succession Planning"])
app.include_router(engagement_router, prefix=f"{settings.API_PREFIX}/engagement", tags=["Employee Engagement"])
app.include_router(workforce_router, prefix=f"{settings.API_PREFIX}/workforce", tags=["Workforce Planning"])
app.include_router(exit_management_router, prefix=f"{settings.API_PREFIX}/exit", tags=["Exit Management"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
