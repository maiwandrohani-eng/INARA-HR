#!/usr/bin/env python3
"""
Database Optimization Script
Analyze and optimize database performance
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from core.database import async_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def analyze_tables():
    """Run ANALYZE on all tables to update statistics"""
    logger.info("Analyzing database tables...")
    
    async with async_engine.connect() as conn:
        # Get all user tables
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result]
        
        logger.info(f"Found {len(tables)} tables to analyze")
        
        for table in tables:
            try:
                await conn.execute(text(f"ANALYZE {table}"))
                logger.info(f"✅ Analyzed table: {table}")
            except Exception as e:
                logger.error(f"❌ Failed to analyze {table}: {str(e)}")
        
        await conn.commit()


async def vacuum_tables():
    """Run VACUUM on all tables to reclaim space"""
    logger.info("Vacuuming database tables...")
    
    # Note: VACUUM cannot run inside a transaction block
    # We need to use autocommit mode
    async with async_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result]
        
        for table in tables:
            try:
                await conn.execute(text(f"VACUUM {table}"))
                logger.info(f"✅ Vacuumed table: {table}")
            except Exception as e:
                logger.error(f"❌ Failed to vacuum {table}: {str(e)}")


async def check_missing_indexes():
    """Check for missing indexes on foreign keys"""
    logger.info("Checking for missing indexes...")
    
    query = """
    SELECT
        c.relname as table_name,
        a.attname as column_name
    FROM pg_constraint con
    JOIN pg_class c ON c.oid = con.conrelid
    JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(con.conkey)
    WHERE con.contype = 'f'
    AND NOT EXISTS (
        SELECT 1 FROM pg_index i
        WHERE i.indrelid = c.oid
        AND a.attnum = ANY(i.indkey)
    )
    ORDER BY c.relname, a.attname;
    """
    
    async with async_engine.connect() as conn:
        result = await conn.execute(text(query))
        missing = list(result)
        
        if missing:
            logger.warning(f"Found {len(missing)} foreign keys without indexes:")
            for row in missing:
                logger.warning(f"  - {row[0]}.{row[1]}")
        else:
            logger.info("✅ All foreign keys have indexes")


async def show_table_sizes():
    """Show size of each table"""
    logger.info("Analyzing table sizes...")
    
    query = """
    SELECT
        relname as table_name,
        pg_size_pretty(pg_total_relation_size(relid)) as total_size,
        pg_size_pretty(pg_relation_size(relid)) as table_size,
        pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC
    LIMIT 20;
    """
    
    async with async_engine.connect() as conn:
        result = await conn.execute(text(query))
        
        logger.info("\nLargest tables:")
        logger.info(f"{'Table':<40} {'Total Size':<15} {'Table Size':<15} {'Index Size':<15}")
        logger.info("-" * 85)
        
        for row in result:
            logger.info(f"{row[0]:<40} {row[1]:<15} {row[2]:<15} {row[3]:<15}")


async def check_connection_limits():
    """Check current connection usage vs limits"""
    logger.info("Checking connection limits...")
    
    query = """
    SELECT
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_conn,
        (SELECT count(*) FROM pg_stat_activity) as current_conn,
        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_conn,
        (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_conn;
    """
    
    async with async_engine.connect() as conn:
        result = await conn.execute(text(query))
        row = result.fetchone()
        
        logger.info(f"\nConnection Status:")
        logger.info(f"  Max connections: {row[0]}")
        logger.info(f"  Current connections: {row[1]}")
        logger.info(f"  Active connections: {row[2]}")
        logger.info(f"  Idle connections: {row[3]}")
        logger.info(f"  Utilization: {row[1]/row[0]*100:.1f}%")


async def main():
    """Run all optimization tasks"""
    try:
        logger.info("=" * 60)
        logger.info("Database Optimization Script")
        logger.info("=" * 60)
        
        await show_table_sizes()
        print()
        
        await check_connection_limits()
        print()
        
        await check_missing_indexes()
        print()
        
        logger.info("Running ANALYZE on tables...")
        await analyze_tables()
        print()
        
        # Uncomment to run VACUUM (can be slow)
        # logger.info("Running VACUUM on tables...")
        # await vacuum_tables()
        
        logger.info("✅ Database optimization completed")
        
    except Exception as e:
        logger.error(f"❌ Error during optimization: {str(e)}")
        raise
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
