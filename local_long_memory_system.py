#!/usr/bin/env python3
"""
Local Long Memory Context System for MCPVots AGI Ecosystem
=========================================================

A comprehensive long-term memory system using:
- Ollama embeddings (nomic-embed-text)
- SQLite vector database with FTS5
- Memory MCP integration
- Knowledge graph with temporal reasoning
- Streaming memory context
- Attention-based memory management
- Gemini 2.5 CLI for advanced analysis

No external dependencies (OpenAI, Pinecone) - fully local and integrated.
"""

import asyncio
import json
import logging
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
import httpx
import uuid
import hashlib
import pickle
import threading
from collections import defaultdict, deque
import time
from concurrent.futures import ThreadPoolExecutor
import subprocess
import tempfile
import networkx as nx

# Safe logging for Windows
def safe_log(message, level=logging.INFO):
    """Safe logging function that handles Unicode characters on Windows"""
    try:
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False, indent=2)
        message_str = str(message).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        message_str = message_str.replace('🧠', '[MEMORY]').replace('🔍', '[SEARCH]').replace('💾', '[STORE]').replace('⚡', '[FAST]').replace('🎯', '[TARGET]')
        logging.log(level, message_str)
    except Exception as e:
        logging.error(f"Logging error: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('local_long_memory_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MemoryNode:
    """Memory node with embedding and metadata"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    access_count: int
    attention_weight: float
    importance_score: float
    context_tags: List[str]
    relationships: List[str]

@dataclass
class MemoryCluster:
    """Cluster of related memories"""
    id: str
    centroid: List[float]
    memories: List[str]
    topic: str
    coherence_score: float
    last_updated: datetime

@dataclass
class TemporalMemory:
    """Temporal memory with time-based relationships"""
    memory_id: str
    temporal_context: str
    sequence_position: int
    temporal_relationships: List[str]
    decay_factor: float

class LocalEmbeddingService:
    """Local embedding service using Ollama"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "nomic-embed-text:latest"
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings using Ollama"""
        # Check cache first
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.cache:
            self.cache_hits += 1
            return self.cache[text_hash]
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    
                    # Cache the result
                    self.cache[text_hash] = embedding
                    self.cache_misses += 1
                    
                    return embedding
                else:
                    logger.error(f"Embedding failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        tasks = [self.embed_text(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }

class LocalVectorDatabase:
    """Local vector database using SQLite with FTS5"""
    
    def __init__(self, db_path: str = "local_memory.db"):
        self.db_path = db_path
        self.conn = None
        self.setup_database()
        
    def setup_database(self):
        """Setup SQLite database with vector storage"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")
        
        # Create tables
        self.conn.executescript("""
            -- Memory nodes table
            CREATE TABLE IF NOT EXISTS memory_nodes (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                timestamp REAL,
                access_count INTEGER DEFAULT 0,
                attention_weight REAL DEFAULT 0.0,
                importance_score REAL DEFAULT 0.0,
                context_tags TEXT,
                relationships TEXT
            );
            
            -- Memory clusters table
            CREATE TABLE IF NOT EXISTS memory_clusters (
                id TEXT PRIMARY KEY,
                centroid BLOB,
                memories TEXT,
                topic TEXT,
                coherence_score REAL,
                last_updated REAL
            );
            
            -- Temporal memories table
            CREATE TABLE IF NOT EXISTS temporal_memories (
                memory_id TEXT,
                temporal_context TEXT,
                sequence_position INTEGER,
                temporal_relationships TEXT,
                decay_factor REAL,
                FOREIGN KEY (memory_id) REFERENCES memory_nodes (id)
            );
            
            -- Full-text search
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                id UNINDEXED,
                content,
                context_tags,
                content='memory_nodes',
                content_rowid='rowid'
            );
            
            -- Triggers for FTS
            CREATE TRIGGER IF NOT EXISTS memory_fts_insert AFTER INSERT ON memory_nodes
            BEGIN
                INSERT INTO memory_fts(id, content, context_tags) VALUES (new.id, new.content, new.context_tags);
            END;
            
            CREATE TRIGGER IF NOT EXISTS memory_fts_delete AFTER DELETE ON memory_nodes
            BEGIN
                DELETE FROM memory_fts WHERE id = old.id;
            END;
            
            CREATE TRIGGER IF NOT EXISTS memory_fts_update AFTER UPDATE ON memory_nodes
            BEGIN
                UPDATE memory_fts SET content = new.content, context_tags = new.context_tags WHERE id = new.id;
            END;
            
            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_nodes(timestamp);
            CREATE INDEX IF NOT EXISTS idx_importance ON memory_nodes(importance_score);
            CREATE INDEX IF NOT EXISTS idx_attention ON memory_nodes(attention_weight);
        """)
        
        self.conn.commit()
    
    def store_memory(self, memory: MemoryNode) -> bool:
        """Store a memory node"""
        try:
            embedding_blob = pickle.dumps(memory.embedding)
            
            self.conn.execute("""
                INSERT OR REPLACE INTO memory_nodes 
                (id, content, embedding, metadata, timestamp, access_count, 
                 attention_weight, importance_score, context_tags, relationships)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.content,
                embedding_blob,
                json.dumps(memory.metadata),
                memory.timestamp.timestamp(),
                memory.access_count,
                memory.attention_weight,
                memory.importance_score,
                json.dumps(memory.context_tags),
                json.dumps(memory.relationships)
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 10, min_similarity: float = 0.7) -> List[Tuple[MemoryNode, float]]:
        """Perform similarity search using cosine similarity"""
        try:
            cursor = self.conn.execute("""
                SELECT id, content, embedding, metadata, timestamp, access_count,
                       attention_weight, importance_score, context_tags, relationships
                FROM memory_nodes
            """)
            
            results = []
            query_norm = np.linalg.norm(query_embedding)
            
            for row in cursor:
                stored_embedding = pickle.loads(row[2])
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, stored_embedding) / (
                    query_norm * np.linalg.norm(stored_embedding)
                )
                
                if similarity >= min_similarity:
                    memory = MemoryNode(
                        id=row[0],
                        content=row[1],
                        embedding=stored_embedding,
                        metadata=json.loads(row[3]),
                        timestamp=datetime.fromtimestamp(row[4]),
                        access_count=row[5],
                        attention_weight=row[6],
                        importance_score=row[7],
                        context_tags=json.loads(row[8]),
                        relationships=json.loads(row[9])
                    )
                    results.append((memory, similarity))
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def text_search(self, query: str, top_k: int = 10) -> List[MemoryNode]:
        """Perform full-text search"""
        try:
            cursor = self.conn.execute("""
                SELECT m.id, m.content, m.embedding, m.metadata, m.timestamp, m.access_count,
                       m.attention_weight, m.importance_score, m.context_tags, m.relationships
                FROM memory_fts f
                JOIN memory_nodes m ON f.id = m.id
                WHERE memory_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, top_k))
            
            results = []
            for row in cursor:
                memory = MemoryNode(
                    id=row[0],
                    content=row[1],
                    embedding=pickle.loads(row[2]),
                    metadata=json.loads(row[3]),
                    timestamp=datetime.fromtimestamp(row[4]),
                    access_count=row[5],
                    attention_weight=row[6],
                    importance_score=row[7],
                    context_tags=json.loads(row[8]),
                    relationships=json.loads(row[9])
                )
                results.append(memory)
            
            return results
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    def update_access_stats(self, memory_id: str, attention_boost: float = 0.1):
        """Update access statistics for a memory"""
        try:
            self.conn.execute("""
                UPDATE memory_nodes 
                SET access_count = access_count + 1,
                    attention_weight = MIN(1.0, attention_weight + ?)
                WHERE id = ?
            """, (attention_boost, memory_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update access stats: {e}")

class AttentionBasedMemoryManager:
    """Attention-based memory management system"""
    
    def __init__(self, decay_factor: float = 0.95):
        self.decay_factor = decay_factor
        self.attention_history = deque(maxlen=1000)
        self.last_decay_time = time.time()
        
    def calculate_attention_score(self, memory: MemoryNode, query_context: str) -> float:
        """Calculate attention score for a memory"""
        base_score = memory.attention_weight
        
        # Recency boost
        age_hours = (datetime.now() - memory.timestamp).total_seconds() / 3600
        recency_score = np.exp(-age_hours / 24)  # Decay over 24 hours
        
        # Access frequency boost
        frequency_score = min(1.0, memory.access_count / 10)
        
        # Importance boost
        importance_score = memory.importance_score
        
        # Context relevance (simplified)
        context_score = 0.5  # Would be calculated based on query similarity
        
        # Combine scores
        attention_score = (
            base_score * 0.3 +
            recency_score * 0.2 +
            frequency_score * 0.2 +
            importance_score * 0.2 +
            context_score * 0.1
        )
        
        return min(1.0, attention_score)
    
    def decay_attention_weights(self, db: LocalVectorDatabase):
        """Decay attention weights over time"""
        current_time = time.time()
        if current_time - self.last_decay_time > 3600:  # Decay every hour
            try:
                db.conn.execute("""
                    UPDATE memory_nodes 
                    SET attention_weight = attention_weight * ?
                """, (self.decay_factor,))
                db.conn.commit()
                self.last_decay_time = current_time
                logger.info("[MEMORY] Attention weights decayed")
            except Exception as e:
                logger.error(f"Attention decay failed: {e}")

class StreamingMemoryProcessor:
    """Streaming memory processor for real-time context"""
    
    def __init__(self, buffer_size: int = 100):
        self.buffer = deque(maxlen=buffer_size)
        self.processing_queue = asyncio.Queue()
        self.compression_ratio = 0.3
        
    async def add_streaming_context(self, content: str, context: str):
        """Add content to streaming context"""
        await self.processing_queue.put({
            "content": content,
            "context": context,
            "timestamp": datetime.now(),
            "id": str(uuid.uuid4())
        })
    
    async def process_streaming_context(self, embedding_service: LocalEmbeddingService, 
                                      db: LocalVectorDatabase):
        """Process streaming context in background"""
        while True:
            try:
                # Get item from queue with timeout
                item = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=1.0
                )
                
                # Generate embedding
                embedding = await embedding_service.embed_text(item["content"])
                
                if embedding:
                    # Create memory node
                    memory = MemoryNode(
                        id=item["id"],
                        content=item["content"],
                        embedding=embedding,
                        metadata={"context": item["context"], "stream": True},
                        timestamp=item["timestamp"],
                        access_count=0,
                        attention_weight=0.5,  # Start with medium attention
                        importance_score=0.5,   # Will be calculated later
                        context_tags=[item["context"]],
                        relationships=[]
                    )
                    
                    # Store in database
                    db.store_memory(memory)
                    
                    # Add to buffer
                    self.buffer.append(item)
                
            except asyncio.TimeoutError:
                # No items to process, continue
                continue
            except Exception as e:
                logger.error(f"Streaming processing error: {e}")

class GeminiCLIIntegration:
    """Integration with Gemini 2.5 CLI for advanced analysis"""
    
    def __init__(self, gemini_cli_path: str = None):
        self.gemini_cli_path = gemini_cli_path or self._find_gemini_cli()
        self.context_window = 1000000  # 1M tokens for Gemini 2.5
        
    def _find_gemini_cli(self) -> Optional[str]:
        """Find Gemini CLI installation"""
        possible_paths = [
            "c:\\Workspace\\MCPVots\\gemini-cli\\packages\\cli\\dist\\index.js",
            "gemini-cli",
            "npx gemini-cli"
        ]
        
        for path in possible_paths:
            if Path(path).exists() or self._test_command(path):
                return path
        
        return None
    
    def _test_command(self, cmd: str) -> bool:
        """Test if command is available"""
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    async def analyze_with_gemini(self, content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze content using Gemini 2.5 CLI"""
        if not self.gemini_cli_path:
            return {"error": "Gemini CLI not available"}
        
        try:
            # Create temporary file with content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # Prepare Gemini CLI command
            cmd = [
                "node" if self.gemini_cli_path.endswith('.js') else self.gemini_cli_path,
                "analyze" if self.gemini_cli_path.endswith('.js') else "--analyze",
                "--file", tmp_path,
                "--type", analysis_type,
                "--format", "json",
                "--context-window", str(self.context_window)
            ]
            
            if self.gemini_cli_path.endswith('.js'):
                cmd[0] = "node"
                cmd[1] = self.gemini_cli_path
                cmd[2] = "analyze"
            
            # Run Gemini CLI
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)
            
            if process.returncode == 0:
                try:
                    return json.loads(stdout.decode())
                except json.JSONDecodeError:
                    return {"analysis": stdout.decode(), "raw": True}
            else:
                return {"error": stderr.decode()}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_memory_insights(self, memories: List[MemoryNode]) -> Dict[str, Any]:
        """Generate insights from memories using Gemini 2.5"""
        if not memories:
            return {"insights": []}
        
        # Combine memory contents
        combined_content = "\n\n".join([
            f"Memory {i+1}:\nContent: {mem.content}\nContext: {mem.metadata.get('context', 'N/A')}\nImportance: {mem.importance_score}\n"
            for i, mem in enumerate(memories[:50])  # Limit to avoid token overflow
        ])
        
        insights = await self.analyze_with_gemini(
            combined_content, 
            "memory_analysis"
        )
        
        return insights
    
    async def enhance_memory_relationships(self, memory: MemoryNode, context_memories: List[MemoryNode]) -> List[str]:
        """Use Gemini to identify relationships between memories"""
        if not context_memories:
            return []
        
        content = f"""
        Primary Memory: {memory.content}
        
        Related Memories:
        """ + "\n".join([f"{i+1}. {mem.content}" for i, mem in enumerate(context_memories[:20])])
        
        analysis = await self.analyze_with_gemini(content, "relationship_analysis")
        
        # Extract relationships from analysis
        relationships = []
        if "relationships" in analysis:
            relationships = analysis["relationships"]
        elif "analysis" in analysis:
            # Parse text analysis for relationships
            text = analysis["analysis"]
            # Simple extraction - would be more sophisticated in practice
            if "related to" in text.lower():
                relationships.append("conceptual_similarity")
            if "sequence" in text.lower() or "follows" in text.lower():
                relationships.append("temporal_sequence")
        
        return relationships

class KnowledgeGraphMemory:
    """Knowledge graph for memory relationships"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.temporal_edges = set()
        
    def add_memory_node(self, memory: MemoryNode):
        """Add memory as a node in the knowledge graph"""
        self.graph.add_node(
            memory.id,
            content=memory.content,
            timestamp=memory.timestamp,
            importance=memory.importance_score,
            attention=memory.attention_weight,
            tags=memory.context_tags
        )
    
    def add_relationship(self, from_memory_id: str, to_memory_id: str, 
                        relationship_type: str, strength: float = 1.0):
        """Add relationship between memories"""
        self.graph.add_edge(
            from_memory_id,
            to_memory_id,
            relationship=relationship_type,
            strength=strength,
            created=datetime.now()
        )
        
        if relationship_type == "temporal_sequence":
            self.temporal_edges.add((from_memory_id, to_memory_id))
    
    def find_memory_path(self, from_memory_id: str, to_memory_id: str) -> List[str]:
        """Find path between two memories"""
        try:
            path = nx.shortest_path(self.graph, from_memory_id, to_memory_id)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_related_memories(self, memory_id: str, max_distance: int = 2) -> List[str]:
        """Get memories related within max_distance"""
        try:
            # Get all nodes within max_distance
            related = set()
            for distance in range(1, max_distance + 1):
                paths = nx.single_source_shortest_path(
                    self.graph, memory_id, cutoff=distance
                )
                for target, path in paths.items():
                    if len(path) <= max_distance and target != memory_id:
                        related.add(target)
            
            return list(related)
            
        except Exception as e:
            logger.error(f"Failed to get related memories: {e}")
            return []
    
    def get_temporal_sequence(self, memory_id: str) -> List[str]:
        """Get temporal sequence of memories"""
        sequence = []
        
        # Find predecessors in temporal sequence
        predecessors = []
        for edge in self.temporal_edges:
            if edge[1] == memory_id:
                predecessors.append(edge[0])
        
        # Find successors in temporal sequence  
        successors = []
        for edge in self.temporal_edges:
            if edge[0] == memory_id:
                successors.append(edge[1])
        
        # Sort by timestamp
        all_nodes = predecessors + [memory_id] + successors
        node_times = []
        for node_id in all_nodes:
            if node_id in self.graph.nodes:
                timestamp = self.graph.nodes[node_id].get('timestamp')
                if timestamp:
                    node_times.append((node_id, timestamp))
        
        node_times.sort(key=lambda x: x[1])
        return [node_id for node_id, _ in node_times]

class LocalLongMemorySystem:
    """Comprehensive long-term memory system for MCPVots"""
    
    def __init__(self, workspace_path: str = "c:\\Workspace\\MCPVots"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "local_memory.db"
        
        # Initialize components
        self.embedding_service = LocalEmbeddingService()
        self.vector_db = LocalVectorDatabase(str(self.db_path))
        self.attention_manager = AttentionBasedMemoryManager()
        self.streaming_processor = StreamingMemoryProcessor()
        self.gemini_integration = GeminiCLIIntegration()
        self.knowledge_graph = KnowledgeGraphMemory()
        
        # Memory MCP client
        self.memory_mcp_client = None
        
        # Background tasks
        self.background_tasks = []
        
        logger.info("[MEMORY] Local Long Memory System initialized")
    
    async def initialize(self):
        """Initialize the memory system"""
        try:
            # Start background processing
            task = asyncio.create_task(
                self.streaming_processor.process_streaming_context(
                    self.embedding_service, 
                    self.vector_db
                )
            )
            self.background_tasks.append(task)
            
            # Initialize Memory MCP client if available
            await self._init_memory_mcp()
            
            logger.info("[MEMORY] Memory system fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
    
    async def _init_memory_mcp(self):
        """Initialize Memory MCP client"""
        try:
            # This would connect to your existing Memory MCP
            # For now, we'll skip if not available
            pass
        except Exception as e:
            logger.warning(f"Memory MCP not available: {e}")
    
    async def store_memory(self, content: str, context: str, 
                          importance: float = 0.5, tags: List[str] = None) -> str:
        """Store a new memory"""
        try:
            # Generate embedding
            embedding = await self.embedding_service.embed_text(content)
            if not embedding:
                return ""
            
            # Create memory node
            memory_id = str(uuid.uuid4())
            memory = MemoryNode(
                id=memory_id,
                content=content,
                embedding=embedding,
                metadata={"context": context, "source": "user"},
                timestamp=datetime.now(),
                access_count=0,
                attention_weight=0.5,
                importance_score=importance,
                context_tags=tags or [context],
                relationships=[]
            )
            
            # Store in vector database
            if self.vector_db.store_memory(memory):
                # Add to knowledge graph
                self.knowledge_graph.add_memory_node(memory)
                
                # Find and add relationships using Gemini
                await self._add_intelligent_relationships(memory)
                
                # Store in Memory MCP if available
                if self.memory_mcp_client:
                    try:
                        await self.memory_mcp_client.create_entities([{
                            "name": memory_id,
                            "entityType": "memory",
                            "observations": [content]
                        }])
                    except:
                        pass  # Silent fallback
                
                logger.info(f"[STORE] Memory stored: {memory_id}")
                return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
        
        return ""
    
    async def retrieve_memories(self, query: str, context: str = None, 
                               max_results: int = 10, max_tokens: int = 32000) -> List[Dict[str, Any]]:
        """Retrieve relevant memories with context awareness"""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_text(query)
            if not query_embedding:
                return []
            
            # Multi-modal retrieval
            results = []
            
            # 1. Vector similarity search
            vector_results = self.vector_db.similarity_search(
                query_embedding, 
                top_k=max_results * 2
            )
            
            # 2. Full-text search
            text_results = self.vector_db.text_search(query, top_k=max_results)
            
            # 3. Combine and deduplicate
            all_memories = {}
            
            for memory, similarity in vector_results:
                all_memories[memory.id] = {
                    "memory": memory,
                    "similarity": similarity,
                    "source": "vector"
                }
            
            for memory in text_results:
                if memory.id in all_memories:
                    all_memories[memory.id]["source"] = "hybrid"
                else:
                    all_memories[memory.id] = {
                        "memory": memory,
                        "similarity": 0.5,  # Default for text matches
                        "source": "text"
                    }
            
            # 4. Apply attention-based reranking
            ranked_memories = []
            for mem_data in all_memories.values():
                memory = mem_data["memory"]
                attention_score = self.attention_manager.calculate_attention_score(
                    memory, query
                )
                
                # Combined score
                combined_score = (
                    mem_data["similarity"] * 0.6 + 
                    attention_score * 0.4
                )
                
                ranked_memories.append({
                    "memory": memory,
                    "similarity": mem_data["similarity"],
                    "attention": attention_score,
                    "combined_score": combined_score,
                    "source": mem_data["source"]
                })
            
            # 5. Sort by combined score
            ranked_memories.sort(key=lambda x: x["combined_score"], reverse=True)
            
            # 6. Apply context filtering if specified
            if context:
                filtered_memories = []
                for item in ranked_memories:
                    if context.lower() in item["memory"].metadata.get("context", "").lower():
                        filtered_memories.append(item)
                    elif context in item["memory"].context_tags:
                        filtered_memories.append(item)
                
                if filtered_memories:
                    ranked_memories = filtered_memories
            
            # 7. Token-aware truncation
            results = self._truncate_to_token_limit(
                ranked_memories[:max_results], 
                max_tokens
            )
            
            # 8. Update access statistics
            for item in results:
                self.vector_db.update_access_stats(item["memory"].id)
            
            # 9. Generate Gemini insights if we have results
            if results and len(results) > 3:
                insights = await self.gemini_integration.generate_memory_insights(
                    [item["memory"] for item in results]
                )
                
                # Add insights to first result
                if insights and "error" not in insights:
                    results[0]["gemini_insights"] = insights
            
            return results
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []
    
    async def _add_intelligent_relationships(self, memory: MemoryNode):
        """Add intelligent relationships using Gemini analysis"""
        try:
            # Find similar memories
            similar_memories = self.vector_db.similarity_search(
                memory.embedding, 
                top_k=10, 
                min_similarity=0.6
            )
            
            if similar_memories:
                context_memories = [mem for mem, _ in similar_memories]
                
                # Use Gemini to identify relationships
                relationships = await self.gemini_integration.enhance_memory_relationships(
                    memory, context_memories
                )
                
                # Add relationships to knowledge graph
                for i, (related_memory, similarity) in enumerate(similar_memories):
                    if i < len(relationships):
                        self.knowledge_graph.add_relationship(
                            memory.id,
                            related_memory.id,
                            relationships[i],
                            similarity
                        )
                    else:
                        # Default relationship based on similarity
                        rel_type = "conceptual_similarity" if similarity > 0.8 else "weak_association"
                        self.knowledge_graph.add_relationship(
                            memory.id,
                            related_memory.id,
                            rel_type,
                            similarity
                        )
        
        except Exception as e:
            logger.error(f"Failed to add intelligent relationships: {e}")
    
    def _truncate_to_token_limit(self, memories: List[Dict], max_tokens: int) -> List[Dict]:
        """Truncate memories to fit within token limit"""
        # Simplified token counting (4 chars ≈ 1 token)
        total_tokens = 0
        results = []
        
        for item in memories:
            content_tokens = len(item["memory"].content) // 4
            if total_tokens + content_tokens <= max_tokens:
                results.append(item)
                total_tokens += content_tokens
            else:
                break
        
        return results
    
    async def add_streaming_context(self, content: str, context: str):
        """Add content to streaming memory context"""
        await self.streaming_processor.add_streaming_context(content, context)
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        try:
            cursor = self.vector_db.conn.execute("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(attention_weight) as avg_attention,
                    AVG(importance_score) as avg_importance,
                    MAX(access_count) as max_access_count,
                    COUNT(DISTINCT json_extract(metadata, '$.context')) as unique_contexts
                FROM memory_nodes
            """)
            
            stats = cursor.fetchone()
            embedding_stats = self.embedding_service.get_cache_stats()
            
            return {
                "total_memories": stats[0],
                "average_attention": stats[1],
                "average_importance": stats[2],
                "max_access_count": stats[3],
                "unique_contexts": stats[4],
                "embedding_cache": embedding_stats,
                "knowledge_graph_nodes": self.knowledge_graph.graph.number_of_nodes(),
                "knowledge_graph_edges": self.knowledge_graph.graph.number_of_edges(),
                "temporal_relationships": len(self.knowledge_graph.temporal_edges),
                "streaming_buffer_size": len(self.streaming_processor.buffer)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    async def cleanup_old_memories(self, days_old: int = 30, min_importance: float = 0.3):
        """Clean up old, low-importance memories"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor = self.vector_db.conn.execute("""
                DELETE FROM memory_nodes 
                WHERE timestamp < ? AND importance_score < ? AND access_count < 2
            """, (cutoff_date.timestamp(), min_importance))
            
            deleted_count = cursor.rowcount
            self.vector_db.conn.commit()
            
            logger.info(f"[CLEANUP] Deleted {deleted_count} old memories")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            return 0
    
    async def shutdown(self):
        """Shutdown the memory system"""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Close database connection
            if self.vector_db.conn:
                self.vector_db.conn.close()
            
            logger.info("[MEMORY] Memory system shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# Example usage and testing
async def test_local_memory_system():
    """Test the local memory system"""
    logger.info("[TEST] Starting local memory system test...")
    
    # Initialize system
    memory_system = LocalLongMemorySystem()
    await memory_system.initialize()
    
    try:
        # Store some test memories
        memory_id_1 = await memory_system.store_memory(
            "Implemented autonomous AGI development pipeline with Trilogy stack",
            "development",
            importance=0.9,
            tags=["agi", "development", "trilogy"]
        )
        
        memory_id_2 = await memory_system.store_memory(
            "Integrated Gemini CLI for advanced code analysis and generation",
            "ai_tools",
            importance=0.8,
            tags=["gemini", "cli", "analysis"]
        )
        
        memory_id_3 = await memory_system.store_memory(
            "Created local vector database using SQLite and embeddings",
            "infrastructure",
            importance=0.7,
            tags=["database", "vectors", "embeddings"]
        )
        
        # Add streaming context
        await memory_system.add_streaming_context(
            "User is working on long memory integration",
            "current_session"
        )
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Test retrieval
        results = await memory_system.retrieve_memories(
            "AGI development with AI tools",
            max_results=5
        )
        
        logger.info(f"[TEST] Retrieved {len(results)} memories")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result['memory'].content[:100]}... (score: {result['combined_score']:.3f})")
        
        # Get statistics
        stats = await memory_system.get_memory_statistics()
        logger.info(f"[TEST] Memory statistics: {json.dumps(stats, indent=2)}")
        
        logger.info("[TEST] Local memory system test completed successfully!")
        
    except Exception as e:
        logger.error(f"[TEST] Test failed: {e}")
    
    finally:
        await memory_system.shutdown()

if __name__ == "__main__":
    asyncio.run(test_local_memory_system())
