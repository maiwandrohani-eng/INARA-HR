"""
Health Check Utilities
Monitor database, cache, and system health
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
from typing import Dict, Any

from core.database import async_engine

logger = logging.getLogger(__name__)


async def check_database_health() -> Dict[str, Any]:
    """
    Check database connection and performance
    
    Returns:
        Dict with health status and metrics
    """
    status = {
        "healthy": False,
        "response_time_ms": None,
        "pool_size": None,
        "pool_checked_out": None,
        "error": None
    }
    
    try:
        # Measure query response time
        start_time = datetime.now()
        
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        # Get connection pool stats
        pool = async_engine.pool
        
        status.update({
            "healthy": True,
            "response_time_ms": round(response_time, 2),
            "pool_size": pool.size(),
            "pool_checked_out": pool.checkedout(),
            "pool_overflow": pool.overflow(),
            "pool_checked_in": pool.checkedin()
        })
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        status["error"] = str(e)
    
    return status


async def check_database_tables() -> Dict[str, Any]:
    """
    Check if critical tables exist
    
    Returns:
        Dict with table check results
    """
    tables_status = {
        "healthy": False,
        "tables_checked": 0,
        "tables_found": 0,
        "missing_tables": []
    }
    
    critical_tables = [
        "users",
        "roles",
        "permissions",
        "employees",
        "departments"
    ]
    
    try:
        async with async_engine.connect() as conn:
            for table in critical_tables:
                result = await conn.execute(
                    text(f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = '{table}')")
                )
                exists = result.fetchone()[0]
                
                tables_status["tables_checked"] += 1
                if exists:
                    tables_status["tables_found"] += 1
                else:
                    tables_status["missing_tables"].append(table)
        
        tables_status["healthy"] = len(tables_status["missing_tables"]) == 0
        
    except Exception as e:
        logger.error(f"Table check failed: {str(e)}")
        tables_status["error"] = str(e)
    
    return tables_status


async def get_db_connection_info() -> Dict[str, Any]:
    """
    Get current database connection information
    
    Returns:
        Dict with connection details
    """
    info = {
        "database_url": None,
        "pool_size": None,
        "max_overflow": None,
        "pool_timeout": None
    }
    
    try:
        # Obscure password in URL for security
        url_str = str(async_engine.url)
        if "@" in url_str:
            parts = url_str.split("@")
            user_pass = parts[0].split("://")[1]
            user = user_pass.split(":")[0]
            info["database_url"] = f"postgresql://{user}:****@{parts[1]}"
        
        pool = async_engine.pool
        info.update({
            "pool_size": pool.size(),
            "max_overflow": getattr(pool, "_max_overflow", None),
            "timeout": getattr(pool, "_timeout", None)
        })
        
    except Exception as e:
        logger.error(f"Failed to get connection info: {str(e)}")
        info["error"] = str(e)
    
    return info
