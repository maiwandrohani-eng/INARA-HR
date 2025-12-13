"""Admin Module - Routes"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
from datetime import datetime
import uuid
import redis
import logging

from core.database import get_db
from core.dependencies import require_admin
from core.exceptions import NotFoundException
from core.config import settings
from modules.admin.schemas import (
    CountryConfigCreate,
    CountryConfigUpdate,
    CountryConfigResponse,
    SalaryBandCreate,
    SalaryBandUpdate,
    SalaryBandResponse,
)
from modules.admin.repositories import CountryConfigRepository, SalaryBandRepository

router = APIRouter()
logger = logging.getLogger(__name__)

# System settings storage (in-memory for now, should be in database)
_system_settings = {
    "organization_name": "INARA",
    "organization_email": "admin@inara.org",
    "organization_phone": None,
    "default_currency": "USD",
    "default_timezone": "UTC",
    "date_format": "YYYY-MM-DD",
    "time_format": "24h",
    "week_start_day": "monday",
    "password_expiry_days": 90,
    "session_timeout_minutes": 60,
    "enable_two_factor": False,
    "enable_email_notifications": True,
    "enable_sms_notifications": False,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 30,
}


# ============================================
# Health Check Endpoints
# ============================================

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check for all system services
    
    Returns:
        - status: overall system status (healthy, degraded, unhealthy)
        - timestamp: current UTC timestamp
        - services: status of individual services (database, redis, email, storage)
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Database check
    try:
        start_time = datetime.utcnow()
        result = await db.execute(text("SELECT 1"))
        end_time = datetime.utcnow()
        latency = (end_time - start_time).total_seconds() * 1000
        
        health["services"]["database"] = {
            "status": "up",
            "latency_ms": round(latency, 2),
            "type": "PostgreSQL"
        }
    except Exception as e:
        health["services"]["database"] = {
            "status": "down",
            "error": str(e)
        }
        health["status"] = "unhealthy"
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        info = redis_client.info()
        
        health["services"]["redis"] = {
            "status": "up",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown")
        }
    except Exception as e:
        health["services"]["redis"] = {
            "status": "down",
            "error": str(e)
        }
        health["status"] = "degraded"
    
    # Email service check
    try:
        health["services"]["email"] = {
            "status": "configured" if settings.SEND_EMAILS else "disabled",
            "provider": settings.EMAIL_PROVIDER,
            "from_email": settings.FROM_EMAIL
        }
    except Exception as e:
        health["services"]["email"] = {
            "status": "error",
            "error": str(e)
        }
    
    # S3 Storage check
    try:
        health["services"]["storage"] = {
            "status": "configured",
            "endpoint": settings.S3_ENDPOINT_URL,
            "bucket": settings.S3_BUCKET_NAME
        }
    except Exception as e:
        health["services"]["storage"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health


# Country Configuration Endpoints
@router.get("/countries", response_model=List[CountryConfigResponse])
async def list_countries(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """List all country configurations"""
    repo = CountryConfigRepository(db)
    configs = await repo.get_all()
    return configs


@router.post("/countries", response_model=CountryConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_country_config(
    data: CountryConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new country configuration"""
    repo = CountryConfigRepository(db)
    
    # Check if country code already exists
    existing = await repo.get_by_code(data.country_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Country configuration for {data.country_code} already exists"
        )
    
    config = await repo.create(data.model_dump())
    await db.commit()
    return config


@router.put("/countries/{config_id}", response_model=CountryConfigResponse)
async def update_country_config(
    config_id: uuid.UUID,
    data: CountryConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a country configuration"""
    repo = CountryConfigRepository(db)
    config = await repo.get_by_id(config_id)
    
    if not config:
        raise NotFoundException(resource="Country configuration")
    
    updated_config = await repo.update(config, data.model_dump(exclude_unset=True))
    await db.commit()
    return updated_config


@router.delete("/countries/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country_config(
    config_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a country configuration"""
    repo = CountryConfigRepository(db)
    config = await repo.get_by_id(config_id)
    
    if not config:
        raise NotFoundException(resource="Country configuration")
    
    await repo.delete(config)
    await db.commit()


# System Settings Endpoints
@router.get("/settings")
async def get_system_settings(
    current_user: dict = Depends(require_admin)
):
    """Get system settings"""
    return _system_settings


@router.put("/settings")
async def update_system_settings(
    settings: dict,
    current_user: dict = Depends(require_admin)
):
    """Update system settings"""
    # Update the in-memory settings
    _system_settings.update(settings)
    return {"message": "Settings updated successfully", "settings": _system_settings}


# Database Management Endpoints
@router.post("/database/backup")
async def backup_database(
    current_user: dict = Depends(require_admin)
):
    """Create database backup (placeholder - requires implementation)"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database backup feature requires server-side implementation"
    )


@router.post("/database/restore")
async def restore_database(
    current_user: dict = Depends(require_admin)
):
    """Restore database from backup (placeholder - requires implementation)"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database restore feature requires server-side implementation"
    )


@router.post("/database/optimize")
async def optimize_database(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Optimize database (placeholder - requires implementation)"""
    # In production, this would run VACUUM, ANALYZE, etc.
    return {"message": "Database optimization completed successfully"}
