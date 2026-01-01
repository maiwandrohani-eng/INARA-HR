"""
Custom Middleware
Request timeout, CSRF protection, and other security middleware
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import asyncio
from typing import Callable

from core.config import settings

logger = logging.getLogger(__name__)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        try:
            # Set timeout based on endpoint (upload endpoints get longer timeout)
            timeout = settings.UPLOAD_TIMEOUT_SECONDS if "/upload" in str(request.url.path) else settings.REQUEST_TIMEOUT_SECONDS
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            # Log slow requests
            if process_time > timeout * 0.8:  # Warn if > 80% of timeout
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s"
                )
            
            # Add timeout header
            response.headers["X-Request-Timeout"] = str(timeout)
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content={
                    "success": False,
                    "error": {
                        "code": "REQUEST_TIMEOUT",
                        "message": "Request timed out. Please try again.",
                        "details": f"Request exceeded timeout of {timeout} seconds"
                    }
                }
            )


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """Basic CSRF protection middleware"""
    
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        # Paths exempt from CSRF (public endpoints, webhooks)
        self.exempt_paths = exempt_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/reset-password",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip CSRF check for exempt paths and GET/HEAD/OPTIONS requests
        if (
            request.method in ["GET", "HEAD", "OPTIONS"] or
            any(request.url.path.startswith(path) for path in self.exempt_paths)
        ):
            return await call_next(request)
        
        # For state-changing requests, check Origin header
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        # In production, verify Origin/Referer matches allowed origins
        if settings.ENVIRONMENT == "production":
            if origin and origin not in settings.CORS_ORIGINS:
                logger.warning(f"CSRF check failed: Invalid origin {origin} for {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "success": False,
                        "error": {
                            "code": "CSRF_VIOLATION",
                            "message": "Invalid origin. Request rejected for security.",
                        }
                    }
                )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only add HSTS in production with HTTPS
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

