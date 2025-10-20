#!/usr/bin/env python3
"""
MAXX Ecosystem Vector Memory MCP Server
SQLite-based vector memory for the PumpFun ecosystem
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Sequence
import numpy as np
from datetime import datetime
import hashlib

# MCP imports
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maxx-memory-mcp")

class VectorMemoryStore:
    """SQLite-based vector memory store for MAXX ecosystem"""

    def __init__(self, db_path: str = "data/maxx_memory.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with vector storage tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Create tables for vector storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content TEXT NOT NULL,
                vector BLOB,
                metadata TEXT,
                timestamp REAL,
                category TEXT DEFAULT 'general'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                target_id INTEGER,
                relationship_type TEXT,
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (source_id) REFERENCES memory_vectors (id),
                FOREIGN KEY (target_id) REFERENCES memory_vectors (id)
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON memory_vectors(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON memory_vectors(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_vectors(timestamp)')

        self.conn.commit()
        logger.info(f"Initialized MAXX memory database at {self.db_path}")

    def _content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _vector_to_blob(self, vector: List[float]) -> bytes:
        """Convert vector to binary blob"""
        return np.array(vector, dtype=np.float32).tobytes()

    def _blob_to_vector(self, blob: bytes) -> List[float]:
        """Convert binary blob back to vector"""
        return np.frombuffer(blob, dtype=np.float32).tolist()

    def store_memory(self, content: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None, category: str = "general") -> int:
        """Store a memory vector"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        content_hash = self._content_hash(content)
        vector_blob = self._vector_to_blob(vector)
        metadata_json = json.dumps(metadata or {})
        timestamp = datetime.now().timestamp()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO memory_vectors
                (content_hash, content, vector, metadata, timestamp, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, content, vector_blob, metadata_json, timestamp, category))

            memory_id = cursor.lastrowid
            if memory_id is None:
                raise RuntimeError("Failed to get memory ID after insertion")
            self.conn.commit()
            logger.info(f"Stored memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            self.conn.rollback()
            raise

    def search_similar(self, query_vector: List[float], limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar memories using cosine similarity"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()

        # Get all vectors
        query = "SELECT id, content, vector, metadata, timestamp, category FROM memory_vectors"
        params = []
        if category:
            query += " WHERE category = ?"
            params.append(category)

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Calculate similarities
        similarities = []
        query_vec = np.array(query_vector, dtype=np.float32)
        query_dim = len(query_vec)

        for row in results:
            memory_id, content, vector_blob, metadata_json, timestamp, cat = row
            stored_vec = np.array(self._blob_to_vector(vector_blob), dtype=np.float32)

            # Only compare vectors of the same dimension
            if len(stored_vec) != query_dim:
                continue

            # Cosine similarity
            dot_product = np.dot(query_vec, stored_vec)
            query_norm = np.linalg.norm(query_vec)
            stored_norm = np.linalg.norm(stored_vec)

            if query_norm > 0 and stored_norm > 0:
                similarity = dot_product / (query_norm * stored_norm)
            else:
                similarity = 0.0

            similarities.append({
                'id': memory_id,
                'content': content,
                'similarity': float(similarity),
                'metadata': json.loads(metadata_json),
                'timestamp': timestamp,
                'category': cat
            })

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:limit]

    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, content, vector, metadata, timestamp, category FROM memory_vectors WHERE id = ?', (memory_id,))
        row = cursor.fetchone()

        if row:
            memory_id, content, vector_blob, metadata_json, timestamp, category = row
            return {
                'id': memory_id,
                'content': content,
                'vector': self._blob_to_vector(vector_blob),
                'metadata': json.loads(metadata_json),
                'timestamp': timestamp,
                'category': category
            }
        return None

    def get_all_memories(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all memories, optionally filtered by category"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        query = "SELECT id, content, vector, metadata, timestamp, category FROM memory_vectors"
        params = []

        if category:
            query += " WHERE category = ?"
            params.append(category)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        memories = []
        for row in results:
            memory_id, content, vector_blob, metadata_json, timestamp, cat = row
            memories.append({
                'id': memory_id,
                'content': content,
                'vector': self._blob_to_vector(vector_blob),
                'metadata': json.loads(metadata_json),
                'timestamp': timestamp,
                'category': cat
            })

        return memories

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by ID"""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized")
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM memory_vectors WHERE id = ?', (memory_id,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        return deleted

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Global memory store instance
memory_store = None

def get_memory_store() -> VectorMemoryStore:
    """Get or create memory store instance"""
    global memory_store
    if memory_store is None:
        db_path = os.getenv("MAXX_MEMORY_DB", "data/maxx_memory.db")
        memory_store = VectorMemoryStore(db_path)
    return memory_store

# MCP Server setup
server = FastMCP("maxx-memory-mcp", instructions="SQLite-based vector memory system for the MAXX ecosystem")

@server.tool()
async def store_memory(content: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None, category: str = "general") -> str:
    """Store a memory vector in the MAXX ecosystem memory system"""
    try:
        store = get_memory_store()
        memory_id = store.store_memory(content, vector, metadata or {}, category)
        return f"Successfully stored memory with ID: {memory_id}"
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return f"Error storing memory: {str(e)}"

@server.tool()
async def search_memory(query_vector: List[float], limit: int = 10, category: Optional[str] = None) -> str:
    """Search for similar memories using vector similarity"""
    try:
        store = get_memory_store()
        results = store.search_similar(query_vector, limit, category)

        if not results:
            return "No similar memories found"

        response = f"Found {len(results)} similar memories:\n\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. [ID: {result['id']}] Similarity: {result['similarity']:.3f}\n"
            response += f"   Content: {result['content'][:200]}{'...' if len(result['content']) > 200 else ''}\n"
            if result['metadata']:
                response += f"   Metadata: {result['metadata']}\n"
            response += f"   Category: {result['category']}\n\n"

        return response
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return f"Error searching memory: {str(e)}"

@server.tool()
async def retrieve_memory(memory_id: int) -> str:
    """Retrieve a specific memory by ID"""
    try:
        store = get_memory_store()
        memory = store.get_memory(memory_id)

        if not memory:
            return f"Memory with ID {memory_id} not found"

        response = f"Memory ID: {memory['id']}\n"
        response += f"Content: {memory['content']}\n"
        response += f"Vector: {len(memory['vector'])} dimensions\n"
        response += f"Metadata: {memory['metadata']}\n"
        response += f"Category: {memory['category']}\n"
        response += f"Timestamp: {datetime.fromtimestamp(memory['timestamp']).isoformat()}\n"

        return response
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        return f"Error retrieving memory: {str(e)}"

@server.tool()
async def list_memories(category: Optional[str] = None, limit: int = 50) -> str:
    """List all memories, optionally filtered by category"""
    try:
        store = get_memory_store()
        memories = store.get_all_memories(category, limit)

        if not memories:
            return "No memories found"

        response = f"Found {len(memories)} memories"
        if category:
            response += f" in category '{category}'"
        response += ":\n\n"

        for memory in memories:
            response += f"ID: {memory['id']} | Category: {memory['category']}\n"
            response += f"Content: {memory['content'][:100]}{'...' if len(memory['content']) > 100 else ''}\n"
            response += f"Time: {datetime.fromtimestamp(memory['timestamp']).isoformat()}\n\n"

        return response
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        return f"Error listing memories: {str(e)}"

@server.tool()
async def delete_memory(memory_id: int) -> str:
    """Delete a memory by ID"""
    try:
        store = get_memory_store()
        deleted = store.delete_memory(memory_id)
        if deleted:
            return f"Successfully deleted memory with ID: {memory_id}"
        else:
            return f"Memory with ID {memory_id} not found"
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        return f"Error deleting memory: {str(e)}"

@server.tool()
async def get_memory_stats() -> str:
    """Get statistics about the memory store"""
    try:
        store = get_memory_store()
        if store.conn is None:
            return "Error: Database connection not available"
        cursor = store.conn.cursor()

        # Count total memories
        cursor.execute('SELECT COUNT(*) FROM memory_vectors')
        total_count = cursor.fetchone()[0]

        # Count by category
        cursor.execute('SELECT category, COUNT(*) FROM memory_vectors GROUP BY category')
        category_counts = cursor.fetchall()

        response = f"MAXX Memory Statistics:\n"
        response += f"Total memories: {total_count}\n\n"
        response += "Memories by category:\n"

        for category, count in category_counts:
            response += f"  {category}: {count}\n"

        return response
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return f"Error getting memory stats: {str(e)}"

async def main():
    """Main MCP server entry point"""
    try:
        logger.info("Starting MAXX Ecosystem Vector Memory MCP Server")
        await server.run_stdio_async()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        if memory_store:
            memory_store.close()

if __name__ == "__main__":
    asyncio.run(main())
