#!/usr/bin/env python3
"""
Database Optimization Utility
Implements connection pooling and query optimization
"""

import asyncio
import sqlite3
import aiosqlite
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization with connection pooling and query caching"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connection_pool = asyncio.Queue(maxsize=max_connections)
        self.query_cache = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize connection pool"""
        if self._initialized:
            return
        
        for _ in range(self.max_connections):
            conn = await aiosqlite.connect(self.db_path)
            await self.connection_pool.put(conn)
        
        self._initialized = True
        logger.info(f"Database connection pool initialized with {self.max_connections} connections")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        if not self._initialized:
            await self.initialize()
        
        conn = await self.connection_pool.get()
        try:
            yield conn
        finally:
            await self.connection_pool.put(conn)
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query with connection pooling"""
        async with self.get_connection() as conn:
            async with conn.execute(query, params) as cursor:
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = await cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
    
    async def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute insert query and return last row id"""
        async with self.get_connection() as conn:
            async with conn.execute(query, params) as cursor:
                await conn.commit()
                return cursor.lastrowid
    
    async def execute_batch(self, query: str, params_list: List[tuple]) -> None:
        """Execute batch operations"""
        async with self.get_connection() as conn:
            await conn.executemany(query, params_list)
            await conn.commit()
    
    async def optimize_database(self) -> None:
        """Run database optimization commands"""
        optimization_queries = [
            "VACUUM;",
            "ANALYZE;",
            "PRAGMA optimize;",
            "PRAGMA journal_mode = WAL;",
            "PRAGMA synchronous = NORMAL;",
            "PRAGMA cache_size = 10000;",
            "PRAGMA temp_store = MEMORY;"
        ]
        
        async with self.get_connection() as conn:
            for query in optimization_queries:
                try:
                    await conn.execute(query)
                    await conn.commit()
                except Exception as e:
                    logger.warning(f"Could not execute optimization query '{query}': {e}")
        
        logger.info("Database optimization completed")
    
    async def close(self):
        """Close all connections in pool"""
        while not self.connection_pool.empty():
            conn = await self.connection_pool.get()
            await conn.close()

# Global database optimizer instances
_db_optimizers = {}

def get_db_optimizer(db_path: str) -> DatabaseOptimizer:
    """Get or create database optimizer for given path"""
    if db_path not in _db_optimizers:
        _db_optimizers[db_path] = DatabaseOptimizer(db_path)
    return _db_optimizers[db_path]
