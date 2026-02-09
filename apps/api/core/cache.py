"""
Redis Cache Service
Provides caching layer for frequently accessed data
"""

import redis
import json
from functools import wraps
from typing import Any, Optional, Callable
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching service"""
    
    def __init__(self):
        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.client:
            return False
        
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False


# Global cache instance
cache = RedisCache()


def cache_result(key_prefix: str, ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds (default 5 minutes)
    
    Usage:
        @cache_result("dashboard:employee", ttl=300)
        async def get_employee_dashboard(employee_id: UUID):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            args_str = ",".join(str(arg) for arg in args if arg)
            kwargs_str = ",".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{args_str}:{kwargs_str}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Call function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Delete cache entries matching pattern
    
    Usage:
        invalidate_cache("dashboard:employee:*")
    """
    return cache.delete_pattern(pattern)


# Cache key builders
def build_employee_key(employee_id: str) -> str:
    """Build cache key for employee data"""
    return f"employee:{employee_id}"


def build_dashboard_key(employee_id: str, dashboard_type: str = "employee") -> str:
    """Build cache key for dashboard data"""
    return f"dashboard:{dashboard_type}:{employee_id}"


def build_leave_balance_key(employee_id: str) -> str:
    """Build cache key for leave balance"""
    return f"leave:balance:{employee_id}"


def build_approvals_key(user_id: str) -> str:
    """Build cache key for pending approvals"""
    return f"approvals:pending:{user_id}"


def build_employees_list_key(skip: int = 0, limit: int = 100, filters: dict = None) -> str:
    """Build cache key for employees list"""
    filter_str = ""
    if filters:
        # Sort filters for consistent cache keys
        sorted_filters = sorted(filters.items())
        filter_str = ":" + ":".join(f"{k}={v}" for k, v in sorted_filters if v)
    return f"employees:list:{skip}:{limit}{filter_str}"


# Async Redis initialization functions for lifespan management
async def init_redis():
    """Initialize Redis connection - no-op for sync redis"""
    pass


async def close_redis():
    """Close Redis connection - no-op for sync redis"""
    pass
