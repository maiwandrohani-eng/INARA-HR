"""
Database Configuration and Session Management
SQLAlchemy setup for PostgreSQL with async support
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import logging
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import ssl

from core.config import settings

logger = logging.getLogger(__name__)

# Create sync engine for migrations (commented out - only needed for Alembic)
# Uncomment and install psycopg2-binary when running migrations
# engine = create_engine(
#     settings.DATABASE_URL,
#     echo=settings.DEBUG,
#     pool_pre_ping=True,
#     pool_size=5,
#     max_overflow=10
# )
engine = None  # Placeholder for now

# Parse DATABASE_ASYNC_URL to handle SSL properly for asyncpg
def prepare_async_url(url: str) -> str:
    """
    Prepare async database URL by removing SSL parameters from query string.
    asyncpg doesn't accept sslmode as query parameter - SSL is configured via connect_args.
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove SSL-related parameters that asyncpg doesn't understand
    ssl_params = ['sslmode', 'channel_binding']
    for param in ssl_params:
        query_params.pop(param, None)
    
    # Rebuild query string without SSL params
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

# Determine if SSL is required based on original URL
def get_ssl_config(url: str):
    """
    Extract SSL requirements from URL and return SSL config for asyncpg.
    asyncpg uses ssl='require' or ssl context, not query string params.
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    ssl_mode = query_params.get('sslmode', ['prefer'])[0]
    
    # For Neon.tech and most cloud providers, require SSL
    if ssl_mode == 'require' or 'neon.tech' in parsed.netloc or 'pooler.supabase.com' in parsed.netloc:
        # Return SSL context that requires SSL
        return ssl.create_default_context()
    
    return None

# Prepare the async URL without SSL query params
async_url = prepare_async_url(settings.DATABASE_ASYNC_URL)
ssl_config = get_ssl_config(settings.DATABASE_ASYNC_URL)

# Build connect_args for asyncpg
connect_args = {
    "timeout": 10,  # Connection timeout
    "command_timeout": 30,  # Command timeout
    "server_settings": {
        "application_name": "inara_hris_api",
        "jit": "off"  # Disable JIT compilation for stability
    }
}

# Add SSL config if needed
if ssl_config:
    connect_args["ssl"] = ssl_config
    logger.info("SSL enabled for database connection")

# Create async engine for application with optimized settings
async_engine = create_async_engine(
    async_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=20,  # Increased from 5 to handle more concurrent requests
    max_overflow=40,  # Allow more overflow connections
    pool_timeout=30,  # Wait up to 30 seconds for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args=connect_args
)

# Session factories
# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Base class for models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Note: This dependency does NOT auto-commit. Services/routes must
    explicitly commit when needed.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        raise
    finally:
        await session.close()


# Verify database connection
async def verify_db_connection() -> bool:
    """Verify database connection is working"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False


# Initialize database
async def init_db():
    """Initialize database - create all tables"""
    try:
        # First verify connection
        if not await verify_db_connection():
            raise Exception("Cannot connect to database")
        
        # Create tables if needed
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


# Close database connections
async def close_db():
    """Close database connections gracefully"""
    try:
        await async_engine.dispose()
        logger.info("👋 Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")
