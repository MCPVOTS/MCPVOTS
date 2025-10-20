"""
Enhanced Database and Vector Storage Implementation for MAXX Ecosystem
Provides persistent storage for trading data, market history, and vector-based analysis
"""
import asyncio
import json
import time
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from contextlib import asynccontextmanager
import pickle
import sqlite3

import numpy as np
from core.config import get_app_config
from core.logging import get_logger, log_performance
from core.database import get_database_manager
from core.analytics import get_analytics_manager


@dataclass
class VectorData:
    """Vector data structure for storage"""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    timestamp: float
    data_type: str
    source: str


@dataclass
class StorageStats:
    """Storage statistics"""
    total_records: int
    storage_size_bytes: int
    oldest_record: float
    newest_record: float
    data_types: Dict[str, int]
    sources: Dict[str, int]


class VectorStorage:
    """
    Enhanced vector storage system with database backend
    Supports efficient similarity search and metadata filtering
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.config = get_app_config()
        self.logger = get_logger(self.__class__.__name__)
        self.db_manager = None
        self.analytics_manager = None

        # Storage configuration
        self.storage_path = storage_path or os.path.join(
            self.config.data_dir, "vectors.db"
        )
        self.vector_dimension = 384  # Default embedding dimension
        self.max_records = 1000000  # Maximum records to store
        self.retention_days = 90  # Default retention period

        # Cache for frequently accessed vectors
        self._cache: Dict[str, VectorData] = {}
        self._cache_size = 1000
        self._cache_hits = 0
        self._cache_misses = 0

    async def initialize(self):
        """Initialize the vector storage system"""
        self.db_manager = await get_database_manager()
        self.analytics_manager = await get_analytics_manager()

        # Create vector storage tables
        await self._ensure_schema()

        self.logger.info("Vector storage system initialized")

    async def _ensure_schema(self):
        """Ensure database schema exists"""
        try:
            # Create vectors table
            await self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    vector TEXT NOT NULL,
                    metadata TEXT,
                    timestamp REAL,
                    data_type TEXT,
                    source TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create indexes for efficient querying
            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_vectors_timestamp ON vectors(timestamp)
            """)

            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_vectors_type ON vectors(data_type)
            """)

            await self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_vectors_source ON vectors(source)
            """)

            # Create vector similarity cache table
            await self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS vector_similarity_cache (
                    id_a TEXT,
                    id_b TEXT,
                    similarity REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    PRIMARY KEY (id_a, id_b)
                )
            """)

            self.logger.debug("Vector storage schema created/verified")

        except Exception as e:
            self.logger.error(f"Failed to create vector storage schema: {e}")
            raise

    @log_performance("storage.store_vector")
    async def store_vector(self, vector_data: VectorData) -> bool:
        """
        Store a vector with metadata
        """
        try:
            # Validate vector dimension
            if len(vector_data.vector) != self.vector_dimension:
                self.logger.warning(
                    f"Vector dimension mismatch: expected {self.vector_dimension}, "
                    f"got {len(vector_data.vector)}"
                )
                # Resize or pad vector if needed
                vector_data.vector = self._normalize_vector_dimension(vector_data.vector)

            # Check if we need to clean up old records
            await self._cleanup_old_records()

            # Store in database
            await self.db_manager.execute_query("""
                INSERT OR REPLACE INTO vectors
                (id, vector, metadata, timestamp, data_type, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                vector_data.id,
                json.dumps(vector_data.vector),
                json.dumps(vector_data.metadata),
                vector_data.timestamp,
                vector_data.data_type,
                vector_data.source
            ))

            # Update cache
            self._update_cache(vector_data)

            # Record metrics
            await self.analytics_manager.record_metric(
                "vector_stored",
                1,
                tags={
                    "data_type": vector_data.data_type,
                    "source": vector_data.source
                }
            )

            self.logger.debug(f"Stored vector {vector_data.id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to store vector {vector_data.id}: {e}")
            return False

    async def get_vector(self, vector_id: str) -> Optional[VectorData]:
        """
        Retrieve a vector by ID
        """
        try:
            # Check cache first
            if vector_id in self._cache:
                self._cache_hits += 1
                return self._cache[vector_id]

            self._cache_misses += 1

            # Query database
            result = await self.db_manager.execute_query("""
                SELECT id, vector, metadata, timestamp, data_type, source
                FROM vectors
                WHERE id = ?
            """, (vector_id,))

            if result:
                row = result[0]
                vector_data = VectorData(
                    id=row['id'],
                    vector=json.loads(row['vector']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    timestamp=row['timestamp'],
                    data_type=row['data_type'],
                    source=row['source']
                )

                # Update cache
                self._update_cache(vector_data)

                return vector_data

            return None

        except Exception as e:
            self.logger.error(f"Failed to get vector {vector_id}: {e}")
            return None

    @log_performance("storage.search_similar")
    async def search_similar_vectors(
        self,
        query_vector: List[float],
        limit: int = 10,
        data_type: Optional[str] = None,
        source: Optional[str] = None,
        time_range: Optional[Tuple[float, float]] = None,
        min_similarity: float = 0.7
    ) -> List[Tuple[VectorData, float]]:
        """
        Search for similar vectors using cosine similarity
        """
        try:
            # Normalize query vector
            query_vector = self._normalize_vector(query_vector)

            # Build query
            where_clauses = []
            params = []

            if data_type:
                where_clauses.append("data_type = ?")
                params.append(data_type)

            if source:
                where_clauses.append("source = ?")
                params.append(source)

            if time_range:
                where_clauses.append("timestamp BETWEEN ? AND ?")
                params.extend(time_range)

            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            # Get candidate vectors
            candidates = await self.db_manager.execute_query(f"""
                SELECT id, vector, metadata, timestamp, data_type, source
                FROM vectors
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT 1000
            """, params)

            # Calculate similarities
            similarities = []
            for candidate in candidates:
                candidate_vector = json.loads(candidate['vector'])
                similarity = self._cosine_similarity(query_vector, candidate_vector)

                if similarity >= min_similarity:
                    vector_data = VectorData(
                        id=candidate['id'],
                        vector=candidate_vector,
                        metadata=json.loads(candidate['metadata']) if candidate['metadata'] else {},
                        timestamp=candidate['timestamp'],
                        data_type=candidate['data_type'],
                        source=candidate['source']
                    )
                    similarities.append((vector_data, similarity))

            # Sort by similarity and limit
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Record metrics
            await self.analytics_manager.record_metric(
                "vector_search",
                1,
                tags={
                    "candidates": len(candidates),
                    "results": len(similarities),
                    "data_type": data_type or "all"
                }
            )

            return similarities[:limit]

        except Exception as e:
            self.logger.error(f"Failed to search similar vectors: {e}")
            return []

    async def get_vectors_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: int = 100
    ) -> List[VectorData]:
        """
        Get vectors matching metadata filters
        """
        try:
            # Build JSON query for metadata
            where_clauses = []
            params = []

            for key, value in metadata_filters.items():
                where_clauses.append("json_extract(metadata, ?) = ?")
                params.extend([f"$.{key}", json.dumps(value)])

            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            results = await self.db_manager.execute_query(f"""
                SELECT id, vector, metadata, timestamp, data_type, source
                FROM vectors
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """, params + [limit])

            vectors = []
            for row in results:
                vector_data = VectorData(
                    id=row['id'],
                    vector=json.loads(row['vector']),
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    timestamp=row['timestamp'],
                    data_type=row['data_type'],
                    source=row['source']
                )
                vectors.append(vector_data)

            return vectors

        except Exception as e:
            self.logger.error(f"Failed to get vectors by metadata: {e}")
            return []

    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by ID
        """
        try:
            await self.db_manager.execute_query("""
                DELETE FROM vectors WHERE id = ?
            """, (vector_id,))

            # Remove from cache
            if vector_id in self._cache:
                del self._cache[vector_id]

            self.logger.debug(f"Deleted vector {vector_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False

    async def get_storage_stats(self) -> StorageStats:
        """
        Get storage statistics
        """
        try:
            # Get basic stats
            result = await self.db_manager.execute_query("""
                SELECT
                    COUNT(*) as total_records,
                    MIN(timestamp) as oldest_record,
                    MAX(timestamp) as newest_record
                FROM vectors
            """)

            if result:
                stats = result[0]

                # Get data type distribution
                type_result = await self.db_manager.execute_query("""
                    SELECT data_type, COUNT(*) as count
                    FROM vectors
                    GROUP BY data_type
                """)

                data_types = {row['data_type']: row['count'] for row in type_result}

                # Get source distribution
                source_result = await self.db_manager.execute_query("""
                    SELECT source, COUNT(*) as count
                    FROM vectors
                    GROUP BY source
                """)

                sources = {row['source']: row['count'] for row in source_result}

                # Get storage size
                storage_size = os.path.getsize(self.storage_path) if os.path.exists(self.storage_path) else 0

                return StorageStats(
                    total_records=stats['total_records'],
                    storage_size_bytes=storage_size,
                    oldest_record=stats['oldest_record'] or 0,
                    newest_record=stats['newest_record'] or 0,
                    data_types=data_types,
                    sources=sources
                )

            return StorageStats(
                total_records=0,
                storage_size_bytes=0,
                oldest_record=0,
                newest_record=0,
                data_types={},
                sources={}
            )

        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return StorageStats(
                total_records=0,
                storage_size_bytes=0,
                oldest_record=0,
                newest_record=0,
                data_types={},
                sources={}
            )

    async def _cleanup_old_records(self):
        """Clean up old records based on retention policy"""
        try:
            cutoff_time = time.time() - (self.retention_days * 86400)

            # Delete old records
            result = await self.db_manager.execute_query("""
                DELETE FROM vectors
                WHERE timestamp < ?
                AND id NOT IN (
                    SELECT id FROM vectors
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """, (cutoff_time, self.max_records))

            if result and result[0]['changes'] > 0:
                self.logger.info(f"Cleaned up {result[0]['changes']} old vector records")

                # Clear cache of deleted items
                self._cache.clear()

        except Exception as e:
            self.logger.error(f"Failed to cleanup old records: {e}")

    def _normalize_vector_dimension(self, vector: List[float]) -> List[float]:
        """Normalize vector to expected dimension"""
        if len(vector) == self.vector_dimension:
            return vector

        if len(vector) < self.vector_dimension:
            # Pad with zeros
            return vector + [0.0] * (self.vector_dimension - len(vector))

        # Truncate if too long
        return vector[:self.vector_dimension]

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return (np.array(vector) / norm).tolist()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)

            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0

            return float(dot_product / (norm_v1 * norm_v2))

        except Exception:
            return 0.0

    def _update_cache(self, vector_data: VectorData):
        """Update the vector cache"""
        # Remove oldest item if cache is full
        if len(self._cache) >= self._cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[vector_data.id] = vector_data

    async def export_vectors(
        self,
        output_path: str,
        data_type: Optional[str] = None,
        time_range: Optional[Tuple[float, float]] = None
    ) -> bool:
        """
        Export vectors to a file
        """
        try:
            where_clauses = []
            params = []

            if data_type:
                where_clauses.append("data_type = ?")
                params.append(data_type)

            if time_range:
                where_clauses.append("timestamp BETWEEN ? AND ?")
                params.extend(time_range)

            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            results = await self.db_manager.execute_query(f"""
                SELECT id, vector, metadata, timestamp, data_type, source
                FROM vectors
                {where_clause}
                ORDER BY timestamp
            """, params)

            export_data = []
            for row in results:
                export_data.append({
                    'id': row['id'],
                    'vector': json.loads(row['vector']),
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'timestamp': row['timestamp'],
                    'data_type': row['data_type'],
                    'source': row['source']
                })

            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"Exported {len(export_data)} vectors to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export vectors: {e}")
            return False

    async def import_vectors(self, input_path: str) -> bool:
        """
        Import vectors from a file
        """
        try:
            with open(input_path, 'r') as f:
                import_data = json.load(f)

            imported_count = 0
            for item in import_data:
                vector_data = VectorData(
                    id=item['id'],
                    vector=item['vector'],
                    metadata=item.get('metadata', {}),
                    timestamp=item['timestamp'],
                    data_type=item['data_type'],
                    source=item['source']
                )

                if await self.store_vector(vector_data):
                    imported_count += 1

            self.logger.info(f"Imported {imported_count} vectors from {input_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import vectors: {e}")
            return False

    async def close(self):
        """Close the vector storage system"""
        self.logger.info("Vector storage system closed")


# Global vector storage instance
_vector_storage: Optional[VectorStorage] = None


async def get_vector_storage() -> VectorStorage:
    """Get global vector storage instance"""
    global _vector_storage

    if _vector_storage is None:
        _vector_storage = VectorStorage()
        await _vector_storage.initialize()

    return _vector_storage


async def close_vector_storage():
    """Close global vector storage"""
    global _vector_storage

    if _vector_storage:
        await _vector_storage.close()
        _vector_storage = None


if __name__ == "__main__":
    import asyncio

    async def main():
        storage = await get_vector_storage()

        # Test storing and retrieving vectors
        test_vector = VectorData(
            id="test_1",
            vector=[0.1, 0.2, 0.3] * 128,  # 384 dimensions
            metadata={"test": True},
            timestamp=time.time(),
            data_type="test",
            source="test"
        )

        await storage.store_vector(test_vector)

        retrieved = await storage.get_vector("test_1")
        print(f"Retrieved vector: {retrieved.id if retrieved else 'None'}")

        # Test similarity search
        similar = await storage.search_similar_vectors(test_vector.vector)
        print(f"Found {len(similar)} similar vectors")

        # Get stats
        stats = await storage.get_storage_stats()
        print(f"Storage stats: {stats.total_records} records")

        await close_vector_storage()

    asyncio.run(main())
