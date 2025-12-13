"""
Custom Exception Classes
Standardized error handling across the application
"""

from fastapi import status
from typing import Optional, Any


class BaseHTTPException(Exception):
    """Base class for all HTTP exceptions"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class UnauthorizedException(BaseHTTPException):
    """Raised when user is not authenticated"""
    def __init__(self, message: str = "Authentication required", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details
        )


class ForbiddenException(BaseHTTPException):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details
        )


class InvalidCredentialsException(BaseHTTPException):
    """Raised when login credentials are invalid"""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS"
        )


# Resource Exceptions
class NotFoundException(BaseHTTPException):
    """Raised when a resource is not found"""
    def __init__(self, resource: str = "Resource", details: Optional[Any] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class BadRequestException(BaseHTTPException):
    """Raised when request data is invalid or malformed"""
    def __init__(self, message: str = "Bad request", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            details=details
        )


class AlreadyExistsException(BaseHTTPException):
    """Raised when attempting to create a duplicate resource"""
    def __init__(self, resource: str = "Resource", details: Optional[Any] = None):
        super().__init__(
            message=f"{resource} already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="ALREADY_EXISTS",
            details=details
        )


class ValidationException(BaseHTTPException):
    """Raised when business logic validation fails"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


# Business Logic Exceptions
class InsufficientLeaveBalanceException(BaseHTTPException):
    """Raised when employee has insufficient leave balance"""
    def __init__(self, required: float, available: float):
        super().__init__(
            message="Insufficient leave balance",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="INSUFFICIENT_LEAVE_BALANCE",
            details={"required": required, "available": available}
        )


class InvalidStatusTransitionException(BaseHTTPException):
    """Raised when attempting an invalid status transition"""
    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            message=f"Cannot transition from {from_status} to {to_status}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="INVALID_STATUS_TRANSITION",
            details={"from": from_status, "to": to_status}
        )


class FileUploadException(BaseHTTPException):
    """Raised when file upload fails"""
    def __init__(self, message: str = "File upload failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="FILE_UPLOAD_ERROR",
            details=details
        )
