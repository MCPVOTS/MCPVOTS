"""
Advanced Database System for MAXX Ecosystem
Provides async database operations with connection pooling, transactions, and metrics
"""
import asyncio
import aiosqlite
import sqlite3
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from datetime import datetime, timedelta
import threading
from enum import Enum
import weakref

from .config import get_database_config
from .logging import get_logger, log_performance


class DatabaseError(Exception):
    """Database operation error"""
    pass


class TransactionError(DatabaseError):
    """Transaction error"""
    pass


class ConnectionPoolError(DatabaseError):
    """Connection pool error"""
    pass


class QueryType(Enum):
    """Query types for metrics"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_type: QueryType
    table: str
    duration: float
    rows_affected: int
    timestamp: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class DatabaseSchema:
    """Database schema definition"""
    tables: Dict[str, str]  # table_name: create_sql
    indexes: Dict[str, str]  # index_name: create_sql
    triggers: Dict[str, str]  # trigger_name: create_sql


class AsyncConnectionPool:
    """Async connection pool for SQLite"""

    def __init__(self, db_path: str, max_connections: int = 10, timeout: float = 30.0):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self._active_connections: int = 0
        self._lock = asyncio.Lock()
        self.logger = get_logger(self.__class__.__name__)
        self._closed = False

    async def initialize(self):
        """Initialize connection pool"""
        # Create database directory if it doesn't exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Pre-warm the pool with connections
        for _ in range(min(3, self.max_connections)):
            conn = await self._create_connection()
            await self._pool.put(conn)

        self.logger.info(f"Connection pool initialized with {self.max_connections} max connections")

    async def _create_connection(self) -> aiosqlite.Connection:
        """Create a new database connection"""
        conn = await aiosqlite.connect(
            self.db_path,
            timeout=self.timeout,
            isolation_level=None  # Autocommit mode
        )

        # Enable WAL mode for better concurrency
        await conn.execute("PRAGMA journal_mode=WAL")

        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys=ON")

        # Optimize for performance
        await conn.execute("PRAGMA synchronous=NORMAL")
        await conn.execute("PRAGMA cache_size=10000")
        await conn.execute("PRAGMA temp_store=MEMORY")

        # Set row factory for dict-like access
        conn.row_factory = aiosqlite.Row

        return conn

    @asynccontextmanager
    async def get_connection(self) -> aiosqlite.Connection:
        """Get a connection from the pool"""
        if self._closed:
            raise ConnectionPoolError("Connection pool is closed")

        async with self._lock:
            if self._active_connections >= self.max_connections:
                raise ConnectionPoolError("Maximum connections reached")

            self._active_connections += 1

        try:
            # Get connection from pool or create new one
            try:
                conn = await asyncio.wait_for(self._pool.get(), timeout=self.timeout)
            except asyncio.TimeoutError:
                conn = await self._create_connection()

            yield conn

        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Connection error: {e}")
        finally:
            async with self._lock:
                self._active_connections -= 1

            # Return connection to pool if not closed
            try:
                if not conn._connection.closed:
                    await self._pool.put(conn)
            except Exception:
                pass  # Connection might be closed, just discard it

    async def close(self):
        """Close all connections in the pool"""
        self._closed = True

        # Close all connections in the pool
        while not self._pool.empty():
            try:
                conn = await asyncio.wait_for(self._pool.get(), timeout=1.0)
                await conn.close()
            except Exception:
                pass

        self.logger.info("Connection pool closed")

    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'max_connections': self.max_connections,
            'active_connections': self._active_connections,
            'available_connections': self._pool.qsize(),
            'closed': self._closed
        }


class DatabaseManager:
    """Advanced database manager with connection pooling and metrics"""

    def __init__(self, db_path: Optional[str] = None):
        self.config = get_database_config()
        self.db_path = db_path or self.config.path
        self.pool = AsyncConnectionPool(
            self.db_path,
            max_connections=self.config.max_connections,
            timeout=self.config.connection_timeout
        )
        self.logger = get_logger(self.__class__.__name__)
        self._metrics: List[QueryMetrics] = []
        self._metrics_lock = threading.Lock()
        self._schema = DatabaseSchema(tables={}, indexes={}, triggers={})
        self._initialized = False

        # Register cleanup handler
        weakref.finalize(self, self._cleanup)

    async def initialize(self):
        """Initialize database and create schema"""
        if self._initialized:
            return

        await self.pool.initialize()

        # Create schema
        await self._create_schema()

        self._initialized = True
        self.logger.info(f"Database initialized: {self.db_path}")

    def _cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'pool'):
            asyncio.create_task(self.pool.close())

    async def _create_schema(self):
        """Create database schema"""
        # Define tables
        self._schema.tables = {
            'market_data': """
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume REAL DEFAULT 0,
                    liquidity REAL DEFAULT 0,
                    high_24h REAL DEFAULT 0,
                    low_24h REAL DEFAULT 0,
                    timestamp REAL NOT NULL,
                    additional_data TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    INDEX(symbol, timestamp),
                    INDEX(timestamp)
                )
            """,
            'trades': """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    strategy TEXT,
                    timestamp REAL NOT NULL,
                    additional_data TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    INDEX(bot_id, symbol, timestamp),
                    INDEX(symbol, timestamp)
                )
            """,
            'social_sentiment': """
                CREATE TABLE IF NOT EXISTS social_sentiment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    mentions_count INTEGER DEFAULT 0,
                    positive_mentions INTEGER DEFAULT 0,
                    negative_mentions INTEGER DEFAULT 0,
                    neutral_mentions INTEGER DEFAULT 0,
                    additional_data TEXT,
                    timestamp REAL NOT NULL,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    INDEX(symbol, timestamp)
                )
            """,
            'bot_performance': """
                CREATE TABLE IF NOT EXISTS bot_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    additional_data TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    INDEX(bot_id, metric_name, timestamp)
                )
            """,
            'market_vectors': """
                CREATE TABLE IF NOT EXISTS market_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vector_id TEXT UNIQUE NOT NULL,
                    market_data TEXT NOT NULL,
                    vector_data BLOB,
                    timestamp REAL NOT NULL,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    INDEX(vector_id),
                    INDEX(timestamp)
                )
            """,
            'analyzed_transactions': """
                CREATE TABLE IF NOT EXISTS analyzed_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_hash TEXT UNIQUE,
                    block_number INTEGER,
                    timestamp REAL,
                    from_address TEXT,
                    to_address TEXT,
                    value TEXT,
                    gas_used INTEGER,
                    gas_price INTEGER,
                    is_swarm_transaction INTEGER DEFAULT 0,
                    is_cluster_transaction INTEGER DEFAULT 0,
                    swarm_id TEXT,
                    cluster_id TEXT,
                    calculated_profit REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """,
            'identified_bots': """
                CREATE TABLE IF NOT EXISTS identified_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE,
                    bot_type TEXT,
                    first_seen REAL,
                    last_seen REAL,
                    transaction_count INTEGER DEFAULT 0,
                    total_volume TEXT,
                    profit_margin REAL,
                    is_active INTEGER DEFAULT 1,
                    pattern_signature TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """
        }

        # Create tables
        async with self.pool.get_connection() as conn:
            for table_name, create_sql in self._schema.tables.items():
                await conn.execute(create_sql)
                self.logger.debug(f"Created table: {table_name}")

            await conn.commit()

    @asynccontextmanager
    async def transaction(self):
        """Database transaction context manager"""
        async with self.pool.get_connection() as conn:
            # Begin transaction
            await conn.execute("BEGIN IMMEDIATE")

            try:
                yield conn
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise TransactionError(f"Transaction failed: {e}")

    @log_performance("database.execute_query")
    async def execute_query(self,
                          query: str,
                          params: Optional[Tuple] = None,
                          query_type: QueryType = QueryType.SELECT) -> List[Dict[str, Any]]:
        """Execute a database query"""
        start_time = time.time()
        rows_affected = 0
        success = False
        error_message = None

        try:
            async with self.pool.get_connection() as conn:
                cursor = await conn.execute(query, params or ())

                if query_type in [QueryType.SELECT]:
                    results = [dict(row) for row in await cursor.fetchall()]
                    rows_affected = len(results)
                else:
                    rows_affected = cursor.rowcount
                    await conn.commit()
                    results = []

                success = True
                return results

        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Query execution failed: {query}, error: {e}")
            raise DatabaseError(f"Query execution failed: {e}")

        finally:
            # Record metrics
            duration = time.time() - start_time
            self._record_metrics(QueryMetrics(
                query_type=query_type,
                table=self._extract_table_name(query),
                duration=duration,
                rows_affected=rows_affected,
                timestamp=time.time(),
                success=success,
                error_message=error_message
            ))

    @log_performance("database.execute_many")
    async def execute_many(self,
                         query: str,
                         params_list: List[Tuple],
                         query_type: QueryType = QueryType.INSERT) -> int:
        """Execute a query multiple times with different parameters"""
        start_time = time.time()
        rows_affected = 0
        success = False
        error_message = None

        try:
            async with self.pool.get_connection() as conn:
                await conn.executemany(query, params_list)
                rows_affected = len(params_list)
                await conn.commit()

                success = True
                return rows_affected

        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Batch execution failed: {query}, error: {e}")
            raise DatabaseError(f"Batch execution failed: {e}")

        finally:
            # Record metrics
            duration = time.time() - start_time
            self._record_metrics(QueryMetrics(
                query_type=query_type,
                table=self._extract_table_name(query),
                duration=duration,
                rows_affected=rows_affected,
                timestamp=time.time(),
                success=success,
                error_message=error_message
            ))

    def _extract_table_name(self, query: str) -> str:
        """Extract table name from query"""
        query_upper = query.upper()

        for keyword in ['FROM', 'INTO', 'UPDATE', 'TABLE']:
            if keyword in query_upper:
                parts = query_upper.split(keyword)
                if len(parts) > 1:
                    table_name = parts[1].strip().split()[0].strip('`"[]')
                    return table_name

        return "unknown"

    def _record_metrics(self, metrics: QueryMetrics):
        """Record query metrics"""
        with self._metrics_lock:
            self._metrics.append(metrics)

            # Keep only last 10000 metrics
            if len(self._metrics) > 10000:
                self._metrics = self._metrics[-10000:]

    async def get_metrics(self,
                         since: Optional[float] = None,
                         query_type: Optional[QueryType] = None) -> List[Dict[str, Any]]:
        """Get query metrics"""
        with self._metrics_lock:
            metrics = self._metrics.copy()

        # Filter metrics
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        if query_type:
            metrics = [m for m in metrics if m.query_type == query_type]

        return [asdict(m) for m in metrics]

    async def cleanup_old_data(self):
        """Clean up old data based on retention settings"""
        current_time = time.time()

        # Calculate cutoff times
        cutoff_times = {
            'market_data': current_time - (self.config.retention_days['market_data'] * 86400),
            'trades': current_time - (self.config.retention_days['trades'] * 86400),
            'social_sentiment': current_time - (self.config.retention_days['sentiment'] * 86400),
            'bot_performance': current_time - (90 * 86400),  # 90 days for performance
            'market_vectors': current_time - (30 * 86400),  # 30 days for vectors
        }

        async with self.transaction() as conn:
            for table, cutoff_time in cutoff_times.items():
                await conn.execute(
                    f"DELETE FROM {table} WHERE created_at < ?",
                    (cutoff_time,)
                )

                self.logger.info(f"Cleaned up old data from {table}")

    async def vacuum(self):
        """Vacuum the database to reclaim space"""
        async with self.pool.get_connection() as conn:
            await conn.execute("VACUUM")
            self.logger.info("Database vacuum completed")

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        async with self.pool.get_connection() as conn:
            # Get table info
            tables_info = {}
            for table_name in self._schema.tables.keys():
                cursor = await conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = (await cursor.fetchone())['count']
                tables_info[table_name] = {'row_count': count}

            # Get database size
            cursor = await conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            size_info = await cursor.fetchone()
            db_size = size_info['size'] if size_info else 0

            # Get pool stats
            pool_stats = await self.pool.get_pool_stats()

            return {
                'path': self.db_path,
                'size_bytes': db_size,
                'size_mb': db_size / (1024 * 1024),
                'tables': tables_info,
                'pool_stats': pool_stats,
                'initialized': self._initialized
            }

    async def close(self):
        """Close database manager"""
        await self.pool.close()
        self.logger.info("Database manager closed")


# Global database instance
_database_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _database_manager

    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()

    return _database_manager


async def close_database():
    """Close global database manager"""
    global _database_manager

    if _database_manager:
        await _database_manager.close()
        _database_manager = None