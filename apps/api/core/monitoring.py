"""
Database Monitoring and Performance Tracking
Real-time monitoring of database connections and queries
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict
import time

from core.database import async_engine

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Monitor database connection pool and query performance"""
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_query_threshold = 1.0  # seconds
        self._monitoring = False
        self._monitor_task = None
    
    def record_query(self, query_name: str, duration: float):
        """
        Record query execution time
        
        Args:
            query_name: Name or identifier of the query
            duration: Execution time in seconds
        """
        self.query_stats[query_name].append({
            "duration": duration,
            "timestamp": datetime.utcnow()
        })
        
        # Log slow queries
        if duration > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected: {query_name} took {duration:.2f}s"
            )
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get current connection pool statistics"""
        try:
            pool = async_engine.pool
            return {
                "size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in": pool.checkedin(),
                "total_available": pool.size() - pool.checkedout(),
                "utilization_percent": round(
                    (pool.checkedout() / pool.size() * 100) if pool.size() > 0 else 0,
                    2
                )
            }
        except Exception as e:
            logger.error(f"Failed to get pool stats: {str(e)}")
            return {}
    
    def get_query_stats(self, minutes: int = 5) -> Dict[str, Any]:
        """
        Get query statistics for the last N minutes
        
        Args:
            minutes: Time window in minutes
        
        Returns:
            Dictionary with query statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        stats = {}
        
        for query_name, executions in self.query_stats.items():
            recent = [
                e for e in executions
                if e["timestamp"] > cutoff_time
            ]
            
            if recent:
                durations = [e["duration"] for e in recent]
                stats[query_name] = {
                    "count": len(recent),
                    "avg_duration": round(sum(durations) / len(durations), 3),
                    "max_duration": round(max(durations), 3),
                    "min_duration": round(min(durations), 3)
                }
        
        return stats
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                pool_stats = self.get_pool_stats()
                
                # Log warnings for high utilization
                if pool_stats.get("utilization_percent", 0) > 80:
                    logger.warning(
                        f"High connection pool utilization: {pool_stats['utilization_percent']}% "
                        f"({pool_stats['checked_out']}/{pool_stats['size']} connections in use)"
                    )
                
                # Log pool stats periodically
                logger.info(
                    f"Pool stats - Available: {pool_stats.get('total_available', 0)}, "
                    f"In use: {pool_stats.get('checked_out', 0)}, "
                    f"Utilization: {pool_stats.get('utilization_percent', 0)}%"
                )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Database monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self._monitoring:
            self._monitoring = False
            if self._monitor_task:
                self._monitor_task.cancel()
            logger.info("Database monitoring stopped")


# Global monitor instance
db_monitor = DatabaseMonitor()


class QueryTimer:
    """Context manager for timing database queries"""
    
    def __init__(self, query_name: str):
        self.query_name = query_name
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        db_monitor.record_query(self.query_name, self.duration)
        return False


def get_monitoring_stats() -> Dict[str, Any]:
    """Get all monitoring statistics"""
    return {
        "pool": db_monitor.get_pool_stats(),
        "queries": db_monitor.get_query_stats(minutes=5),
        "timestamp": datetime.utcnow().isoformat()
    }
