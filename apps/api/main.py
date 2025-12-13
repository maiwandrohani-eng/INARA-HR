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

from core.config import settings
from core.database import engine, Base
from core.exceptions import BaseHTTPException

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

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    if not await verify_db_connection():
        logger.error("❌ Failed to connect to database. Please check your DATABASE_ASYNC_URL configuration.")
        raise Exception("Database connection failed")
    
    # Initialize Redis cache
    await init_redis()
    
    # Start database monitoring
    db_monitor.start_monitoring()
    logger.info("📊 Database monitoring enabled")
    
    logger.info("✅ All systems initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down INARA HRIS API...")
    
    # Stop monitoring
    from core.monitoring import db_monitor
    from core.cache import close_redis
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


# ============================================
# MIDDLEWARE
# ============================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"🌐 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}s")
    logger.info(f"✅ {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response


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
app.include_router(grievance_router, prefix=f"{settings.API_PREFIX}/grievance", tags=["Grievance & Disciplinary"])
app.include_router(travel_router, prefix=f"{settings.API_PREFIX}/travel", tags=["Travel & Deployment"])
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(admin_router, prefix=f"{settings.API_PREFIX}/admin", tags=["Administration"])
app.include_router(ess_router, prefix=f"{settings.API_PREFIX}/ess", tags=["Employee Self-Service"])
app.include_router(approvals_router, prefix=f"{settings.API_PREFIX}", tags=["Approvals"])
app.include_router(employee_files_router, prefix=f"{settings.API_PREFIX}", tags=["Employee Files"])
app.include_router(payroll_router, prefix=f"{settings.API_PREFIX}", tags=["Payroll"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
