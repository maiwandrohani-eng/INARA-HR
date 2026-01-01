"""
Rate Limiting Middleware
Implements rate limiting for API endpoints to prevent abuse
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize rate limiter with Redis if available, otherwise in-memory
try:
    from core.cache import redis_client
    if redis_client:
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=settings.REDIS_URL,
            default_limits=[f"{settings.RATE_LIMIT_PER_HOUR}/hour"]
        )
        logger.info("Rate limiting initialized with Redis storage")
    else:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{settings.RATE_LIMIT_PER_HOUR}/hour"]
        )
        logger.info("Rate limiting initialized with in-memory storage")
except Exception as e:
    logger.warning(f"Failed to initialize Redis for rate limiting: {e}. Using in-memory storage.")
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.RATE_LIMIT_PER_HOUR}/hour"]
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "details": f"Rate limit exceeded: {exc.detail}"
            }
        }
    )


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on user or IP"""
    # Try to get user ID from request state if authenticated
    if hasattr(request.state, 'user_id'):
        return f"user:{request.state.user_id}"
    return get_remote_address(request)

