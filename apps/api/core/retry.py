"""
Retry Logic for Database Operations
Handle transient database errors with exponential backoff
"""

import asyncio
import logging
from functools import wraps
from typing import TypeVar, Callable, Any
from sqlalchemy.exc import OperationalError, DBAPIError, TimeoutError as SQLAlchemyTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    initial_delay: float = 0.5  # seconds
    max_delay: float = 5.0  # seconds
    exponential_base: float = 2.0


def is_transient_error(error: Exception) -> bool:
    """
    Determine if an error is transient and should be retried
    
    Args:
        error: Exception to check
    
    Returns:
        True if error is transient
    """
    transient_errors = (
        OperationalError,
        DBAPIError,
        SQLAlchemyTimeoutError,
        TimeoutError,
        ConnectionError,
        asyncio.TimeoutError
    )
    
    if isinstance(error, transient_errors):
        return True
    
    # Check for specific error messages
    error_msg = str(error).lower()
    transient_keywords = [
        "connection",
        "timeout",
        "deadlock",
        "could not serialize",
        "connection refused",
        "connection reset",
        "broken pipe",
        "lost connection"
    ]
    
    return any(keyword in error_msg for keyword in transient_keywords)


def retry_on_db_error(
    max_retries: int = RetryConfig.max_retries,
    initial_delay: float = RetryConfig.initial_delay,
    max_delay: float = RetryConfig.max_delay,
    exponential_base: float = RetryConfig.exponential_base
):
    """
    Decorator to retry database operations on transient errors
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
    
    Example:
        @retry_on_db_error(max_retries=3)
        async def fetch_user(user_id):
            return await db.get(User, user_id)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    # Don't retry on non-transient errors
                    if not is_transient_error(e):
                        logger.error(f"Non-transient error in {func.__name__}: {str(e)}")
                        raise
                    
                    # Don't retry on last attempt
                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) reached for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    logger.warning(
                        f"Transient error in {func.__name__} (attempt {attempt + 1}/{max_retries}): "
                        f"{str(e)}. Retrying in {delay:.2f}s..."
                    )
                    
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            if last_error:
                raise last_error
        
        return wrapper
    return decorator


async def retry_db_operation(
    operation: Callable[..., Any],
    *args: Any,
    max_retries: int = RetryConfig.max_retries,
    **kwargs: Any
) -> Any:
    """
    Retry a database operation with exponential backoff
    
    Args:
        operation: Async function to retry
        *args: Positional arguments for operation
        max_retries: Maximum retry attempts
        **kwargs: Keyword arguments for operation
    
    Returns:
        Result of operation
    
    Example:
        result = await retry_db_operation(
            user_repo.get_by_id,
            user_id,
            max_retries=3
        )
    """
    last_error = None
    initial_delay = RetryConfig.initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            last_error = e
            
            if not is_transient_error(e) or attempt == max_retries:
                raise
            
            delay = min(
                initial_delay * (RetryConfig.exponential_base ** attempt),
                RetryConfig.max_delay
            )
            
            logger.warning(
                f"Retrying operation (attempt {attempt + 1}/{max_retries}) "
                f"after {delay:.2f}s: {str(e)}"
            )
            
            await asyncio.sleep(delay)
    
    if last_error:
        raise last_error
