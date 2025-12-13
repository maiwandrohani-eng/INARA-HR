"""
Transaction Management Utilities
Helpers for managing database transactions consistently
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@asynccontextmanager
async def transaction(db: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database transactions with automatic commit/rollback
    
    Usage:
        async with transaction(db) as session:
            employee = Employee(name="John")
            session.add(employee)
            # Automatically commits on success, rolls back on error
    
    Args:
        db: Database session
    
    Yields:
        Database session
    """
    try:
        yield db
        await db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise


async def save_and_refresh(db: AsyncSession, instance):
    """
    Save an instance to database and refresh it
    
    Args:
        db: Database session
        instance: Model instance to save
    
    Returns:
        Refreshed instance
    """
    try:
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save instance: {str(e)}")
        raise


async def safe_delete(db: AsyncSession, instance) -> bool:
    """
    Safely delete an instance with proper error handling
    
    Args:
        db: Database session
        instance: Model instance to delete
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        await db.delete(instance)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete instance: {str(e)}")
        return False


async def bulk_save(db: AsyncSession, instances: list) -> bool:
    """
    Save multiple instances in a single transaction
    
    Args:
        db: Database session
        instances: List of model instances to save
    
    Returns:
        True if all saved successfully, False otherwise
    """
    try:
        db.add_all(instances)
        await db.commit()
        
        # Refresh all instances
        for instance in instances:
            await db.refresh(instance)
        
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to bulk save instances: {str(e)}")
        return False


class TransactionManager:
    """
    Transaction manager for complex operations
    
    Usage:
        tm = TransactionManager(db)
        await tm.begin()
        try:
            # ... do work ...
            await tm.commit()
        except:
            await tm.rollback()
            raise
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._in_transaction = False
    
    async def begin(self):
        """Start a new transaction"""
        if self._in_transaction:
            logger.warning("Transaction already in progress")
            return
        
        self._in_transaction = True
        logger.debug("Transaction started")
    
    async def commit(self):
        """Commit the current transaction"""
        if not self._in_transaction:
            logger.warning("No transaction to commit")
            return
        
        try:
            await self.db.commit()
            logger.debug("Transaction committed")
        finally:
            self._in_transaction = False
    
    async def rollback(self):
        """Rollback the current transaction"""
        if not self._in_transaction:
            logger.warning("No transaction to rollback")
            return
        
        try:
            await self.db.rollback()
            logger.debug("Transaction rolled back")
        finally:
            self._in_transaction = False
    
    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        return False
