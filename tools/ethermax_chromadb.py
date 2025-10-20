#!/usr/bin/env python3
"""
ETHERMAX ChromaDB Integration Module
Comprehensive ChromaDB integration for identity tracking, funding connections, and trade history
"""

import asyncio
import json
import logging
import time
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from decimal import Decimal
import re
import numpy as np
from pathlib import Path

# ChromaDB imports (optional)
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    _CHROMA_AVAILABLE = True
except Exception:
    chromadb = None  # type: ignore
    Settings = object  # type: ignore
    embedding_functions = None  # type: ignore
    _CHROMA_AVAILABLE = False

# Import configuration
import standalone_config as config

# Configure logging
logger = logging.getLogger(__name__)

class EthermaxChromaDB:
    """Main ChromaDB integration class for ETHERMAX tracking"""

    def __init__(self) -> None:
        # Basic attributes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = None
        self.identity_collection = None
        self.funding_collection = None
        self.trade_collection = None
        self.embedding_function = None
        # Fallback local store when ChromaDB is missing/unavailable
        self._sqlite_store = None  # type: ignore[assignment]
        self.is_initialized = False


    async def initialize(self) -> bool:
        """Initialize vector store (ChromaDB or SQLite fallback)"""
        try:
            self.logger.info("Initializing ChromaDB integration...")

            if _CHROMA_AVAILABLE:
                try:
                    # Initialize ChromaDB client
                    self.client = chromadb.PersistentClient(
                        path=getattr(config, "CHROMADB_PERSIST_DIRECTORY", ".chroma"),
                        settings=Settings(**getattr(config, "CHROMADB_SETTINGS", {}))
                    )

                    # Initialize embedding function
                    self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name=getattr(config, "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
                    )

                    # Create or get collections
                    await self._setup_collections()
                    self.logger.info("ChromaDB integration initialized successfully")
                except Exception as e:
                    self.logger.warning(f"ChromaDB init failed, falling back to SQLite: {e}")
                    from sqlite_vector_store import SQLiteVectorStore
                    db_path = os.path.join(os.getcwd(), "data", "local_vectors.db")
                    self._sqlite_store = SQLiteVectorStore(db_path)
            else:
                from sqlite_vector_store import SQLiteVectorStore
                db_path = os.path.join(os.getcwd(), "data", "local_vectors.db")
                self._sqlite_store = SQLiteVectorStore(db_path)
                self.logger.warning("ChromaDB unavailable; using SQLiteVectorStore fallback")

            self.is_initialized = True
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            return False

    async def _setup_collections(self):
        """Setup ChromaDB collections with proper configuration"""
        try:
            # Identity tracking collection
            try:
                self.identity_collection = self.client.get_collection(
                    name=config.CHROMADB_IDENTITY_COLLECTION,
                    embedding_function=self.embedding_function
                )
                self.logger.info(f"Loaded existing identity collection: {config.CHROMADB_IDENTITY_COLLECTION}")
            except Exception:
                self.identity_collection = self.client.create_collection(
                    name=config.CHROMADB_IDENTITY_COLLECTION,
                    embedding_function=self.embedding_function,
                    metadata={
                        "description": "Identity tracking for ethermax pattern discovery",
                        "version": "1.0.0",
                        "embedding_model": config.EMBEDDING_MODEL
                    }
                )
                self.logger.info(f"Created new identity collection: {config.CHROMADB_IDENTITY_COLLECTION}")

            # Funding connections collection
            try:
                self.funding_collection = self.client.get_collection(
                    name=config.CHROMADB_FUNDING_COLLECTION,
                    embedding_function=self.embedding_function
                )
                self.logger.info(f"Loaded existing funding collection: {config.CHROMADB_FUNDING_COLLECTION}")
            except Exception:
                self.funding_collection = self.client.create_collection(
                    name=config.CHROMADB_FUNDING_COLLECTION,
                    embedding_function=self.embedding_function,
                    metadata={
                        "description": "Funding relationships and money flow patterns",
                        "version": "1.0.0",
                        "embedding_model": config.EMBEDDING_MODEL
                    }
                )
                self.logger.info(f"Created new funding collection: {config.CHROMADB_FUNDING_COLLECTION}")

            # MAXX trade history collection
            try:
                self.trade_collection = self.client.get_collection(
                    name=config.CHROMADB_TRADE_COLLECTION,
                    embedding_function=self.embedding_function
                )
                self.logger.info(f"Loaded existing trade collection: {config.CHROMADB_TRADE_COLLECTION}")
            except Exception:
                self.trade_collection = self.client.create_collection(
                    name=config.CHROMADB_TRADE_COLLECTION,
                    embedding_function=self.embedding_function,
                    metadata={
                        "description": "MAXX trading patterns and performance metrics",
                        "version": "1.0.0",
                        "embedding_model": config.EMBEDDING_MODEL
                    }
                )
                self.logger.info(f"Created new trade collection: {config.CHROMADB_TRADE_COLLECTION}")

        except Exception as e:
            self.logger.error(f"Failed to setup collections: {e}")
            raise

    def _validate_wallet_address(self, address: str) -> bool:
        """Validate Ethereum wallet address"""
        return re.match(r'^0x[a-fA-F0-9]{40}$', address) is not None

    def _validate_amount(self, amount: Union[int, float, Decimal]) -> bool:
        """Validate amount is non-negative"""
        try:
            return float(amount) >= 0
        except (ValueError, TypeError):
            return False

    def _generate_behavioral_embedding(self, behavioral_data: Dict[str, Any]) -> List[float]:
        """Generate behavioral embedding for identity tracking"""
        try:
            # Extract key behavioral features
            features = []

            # Trading frequency and patterns
            features.append(behavioral_data.get('trading_frequency', 0))
            features.append(behavioral_data.get('avg_transaction_size', 0))
            features.append(len(behavioral_data.get('preferred_tokens', [])))

            # Timing patterns
            timing_patterns = behavioral_data.get('timing_patterns', {})
            features.append(len(timing_patterns.get('most_active_hours', [])))
            features.append(len(timing_patterns.get('day_of_week_patterns', [])))
            features.append(1 if timing_patterns.get('coordination_timing') == 'synchronized' else 0)

            # Coordination score
            features.append(behavioral_data.get('coordination_score', 0))

            # Normalize and pad to required dimension
            features = np.array(features, dtype=float)
            features = features / (np.linalg.norm(features) + 1e-8)

            # Pad to required dimension
            if len(features) < config.EMBEDDING_DIMENSION:
                padding = np.zeros(config.EMBEDDING_DIMENSION - len(features))
                features = np.concatenate([features, padding])

            return features.tolist()

        except Exception as e:
            self.logger.error(f"Failed to generate behavioral embedding: {e}")
            return [0.0] * config.EMBEDDING_DIMENSION

    def _generate_funding_embedding(self, funding_data: Dict[str, Any]) -> List[float]:
        """Generate funding pattern embedding"""
        try:
            features = []

            # Relationship metrics
            relationship_metrics = funding_data.get('relationship_metrics', {})
            features.append(relationship_metrics.get('relationship_strength', 0))
            features.append(relationship_metrics.get('frequency_score', 0))
            features.append(relationship_metrics.get('amount_consistency', 0))

            # Transaction details
            transaction_details = funding_data.get('transaction_details', {})
            features.append(float(transaction_details.get('amount_eth', 0)))
            features.append(float(transaction_details.get('gas_used', 0)) / 1000000)  # Normalize gas

            # Pattern indicators
            features.append(1 if funding_data.get('manipulation_indicators', {}).get('circular_funding') else 0)
            features.append(funding_data.get('manipulation_indicators', {}).get('wash_trading_score', 0))

            # Normalize and pad
            features = np.array(features, dtype=float)
            features = features / (np.linalg.norm(features) + 1e-8)

            if len(features) < config.EMBEDDING_DIMENSION:
                padding = np.zeros(config.EMBEDDING_DIMENSION - len(features))
                features = np.concatenate([features, padding])

            return features.tolist()

        except Exception as e:
            self.logger.error(f"Failed to generate funding embedding: {e}")
            return [0.0] * config.EMBEDDING_DIMENSION

    def _generate_trade_embedding(self, trade_data: Dict[str, Any]) -> List[float]:
        """Generate trade pattern embedding"""
        try:
            features = []

            # Trade details
            trade_details = trade_data.get('trade_details', {})
            features.append(float(trade_details.get('amount_maxx', 0)))
            features.append(float(trade_details.get('amount_eth', 0)))
            features.append(float(trade_details.get('slippage_percent', 0)))

            # Performance metrics
            performance_metrics = trade_data.get('performance_metrics', {})
            features.append(float(performance_metrics.get('pnl_percent', 0)))
            features.append(float(performance_metrics.get('holding_period_minutes', 0)) / 60)  # Normalize to hours

            # Market conditions
            market_conditions = trade_data.get('market_conditions', {})
            features.append(float(market_conditions.get('price_impact_percent', 0)))
            features.append(float(market_conditions.get('volume_24h', 0)) / 1000000)  # Normalize volume

            # Manipulation indicators
            manipulation_analysis = trade_data.get('manipulation_analysis', {})
            features.append(1 if manipulation_analysis.get('coordinated_buying') else 0)
            features.append(1 if manipulation_analysis.get('volume_spike') else 0)

            # Normalize and pad
            features = np.array(features, dtype=float)
            features = features / (np.linalg.norm(features) + 1e-8)

            if len(features) < config.EMBEDDING_DIMENSION:
                padding = np.zeros(config.EMBEDDING_DIMENSION - len(features))
                features = np.concatenate([features, padding])

            return features.tolist()

        except Exception as e:
            self.logger.error(f"Failed to generate trade embedding: {e}")
            return [0.0] * config.EMBEDDING_DIMENSION

    async def add_identity_tracking(self, wallet_address: str, identity_data: Dict[str, Any]) -> bool:
        """Add identity tracking data to ChromaDB"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return False

        try:
            # Validate wallet address
            if not self._validate_wallet_address(wallet_address):
                self.logger.error(f"Invalid wallet address: {wallet_address}")
                return False

            # Generate document ID
            timestamp = datetime.now(timezone.utc).isoformat()
            document_id = f"identity_{wallet_address}_{int(time.time())}"

            # Generate content for embedding
            content = f"Identity analysis for wallet {wallet_address}: {json.dumps(identity_data, default=str)}"

            # Generate embedding
            if self._sqlite_store:
                from sqlite_vector_store import hash_embed
                embedding = hash_embed(content)
            else:
                embedding = self._generate_behavioral_embedding(identity_data.get('behavioral_patterns', {}))

            # Prepare metadata
            metadata = {
                "wallet_address": wallet_address,
                "identity_type": identity_data.get('identity_type', 'unknown'),
                "confidence_score": identity_data.get('confidence_score', 0.0),
                "risk_level": identity_data.get('risk_level', 'medium'),
                "timestamp": timestamp,
                **identity_data
            }

            # Add to collection with retry logic
            if self._sqlite_store:
                self._sqlite_store.add(
                    collection=getattr(config, "CHROMADB_IDENTITY_COLLECTION", "identity"),
                    ids=[document_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                )
                self.logger.info(f"[SQLite] Added identity tracking for {wallet_address}")
                return True
            else:
                for attempt in range(getattr(config, "MAX_RETRIES", 3)):
                    try:
                        self.identity_collection.add(
                            ids=[document_id],
                            embeddings=[embedding],
                            documents=[content],
                            metadatas=[metadata]
                        )
                        self.logger.info(f"Added identity tracking for {wallet_address}")
                        return True
                    except Exception as e:
                        if attempt < getattr(config, "MAX_RETRIES", 3) - 1:
                            self.logger.warning(f"Retry {attempt + 1} for identity tracking: {e}")
                            await asyncio.sleep(getattr(config, "RETRY_DELAY", 1.0) * (attempt + 1))
                        else:
                            raise e

        except Exception as e:
            self.logger.error(f"Failed to add identity tracking: {e}")
            return False

    async def add_funding_connection(self, source_wallet: str, target_wallet: str,
                                   funding_data: Dict[str, Any]) -> bool:
        """Add funding connection data to ChromaDB"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return False

        try:
            # Validate wallet addresses
            if not self._validate_wallet_address(source_wallet) or not self._validate_wallet_address(target_wallet):
                self.logger.error(f"Invalid wallet addresses: {source_wallet}, {target_wallet}")
                return False

            # Generate document ID
            timestamp = datetime.now(timezone.utc).isoformat()
            document_id = f"funding_{source_wallet}_{target_wallet}_{int(time.time())}"

            # Generate content for embedding
            content = f"Funding relationship from {source_wallet} to {target_wallet}: {json.dumps(funding_data, default=str)}"

            # Generate embedding
            if self._sqlite_store:
                from sqlite_vector_store import hash_embed
                embedding = hash_embed(content)
            else:
                embedding = self._generate_funding_embedding(funding_data)

            # Prepare metadata
            metadata = {
                "source_wallet": source_wallet,
                "target_wallet": target_wallet,
                "relationship_type": funding_data.get('relationship_type', 'unknown'),
                "timestamp": timestamp,
                **funding_data
            }

            # Add to collection with retry logic
            if self._sqlite_store:
                self._sqlite_store.add(
                    collection=getattr(config, "CHROMADB_FUNDING_COLLECTION", "funding"),
                    ids=[document_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                )
                self.logger.info(f"[SQLite] Added funding connection from {source_wallet} to {target_wallet}")
                return True
            else:
                for attempt in range(getattr(config, "MAX_RETRIES", 3)):
                    try:
                        self.funding_collection.add(
                            ids=[document_id],
                            embeddings=[embedding],
                            documents=[content],
                            metadatas=[metadata]
                        )
                        self.logger.info(f"Added funding connection from {source_wallet} to {target_wallet}")
                        return True
                    except Exception as e:
                        if attempt < getattr(config, "MAX_RETRIES", 3) - 1:
                            self.logger.warning(f"Retry {attempt + 1} for funding connection: {e}")
                            await asyncio.sleep(getattr(config, "RETRY_DELAY", 1.0) * (attempt + 1))
                        else:
                            raise e

        except Exception as e:
            self.logger.error(f"Failed to add funding connection: {e}")
            return False

    async def add_trade_history(self, wallet_address: str, trade_data: Dict[str, Any]) -> bool:
        """Add trade history data to ChromaDB"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return False

        try:
            # Validate wallet address
            if not self._validate_wallet_address(wallet_address):
                self.logger.error(f"Invalid wallet address: {wallet_address}")
                return False

            # Generate document ID
            timestamp = datetime.now(timezone.utc).isoformat()
            trade_id = trade_data.get('trade_id', str(uuid.uuid4()))
            document_id = f"trade_{wallet_address}_{trade_id}_{int(time.time())}"

            # Generate content for embedding
            content = f"MAXX trade for wallet {wallet_address}: {json.dumps(trade_data, default=str)}"

            # Generate embedding
            if self._sqlite_store:
                from sqlite_vector_store import hash_embed
                embedding = hash_embed(content)
            else:
                embedding = self._generate_trade_embedding(trade_data)

            # Prepare metadata
            metadata = {
                "wallet_address": wallet_address,
                "trade_id": trade_id,
                "trade_type": trade_data.get('trade_details', {}).get('trade_type', 'unknown'),
                "timestamp": timestamp,
                **trade_data
            }

            # Add to collection with retry logic
            if self._sqlite_store:
                self._sqlite_store.add(
                    collection=getattr(config, "CHROMADB_TRADE_COLLECTION", "trade"),
                    ids=[document_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                )
                self.logger.info(f"[SQLite] Added trade history for {wallet_address}")
                return True
            else:
                for attempt in range(getattr(config, "MAX_RETRIES", 3)):
                    try:
                        self.trade_collection.add(
                            ids=[document_id],
                            embeddings=[embedding],
                            documents=[content],
                            metadatas=[metadata]
                        )
                        self.logger.info(f"Added trade history for {wallet_address}")
                        return True
                    except Exception as e:
                        if attempt < getattr(config, "MAX_RETRIES", 3) - 1:
                            self.logger.warning(f"Retry {attempt + 1} for trade history: {e}")
                            await asyncio.sleep(getattr(config, "RETRY_DELAY", 1.0) * (attempt + 1))
                        else:
                            raise e

        except Exception as e:
            self.logger.error(f"Failed to add trade history: {e}")
            return False

    async def query_similar_identities(self, query_text: str,
                                     where_filter: Optional[Dict] = None,
                                     n_results: int = 10) -> Dict[str, Any]:
        """Query for similar identities"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return {}

        try:
            if self._sqlite_store:
                qr = self._sqlite_store.query(
                    collection=getattr(config, "CHROMADB_IDENTITY_COLLECTION", "identity"),
                    query_texts=[query_text],
                    where=where_filter or {},
                    n_results=n_results,
                )
                return {"ids": qr.ids, "metadatas": qr.metadatas, "documents": qr.documents, "distances": qr.distances}
            else:
                results = self.identity_collection.query(
                    query_texts=[query_text],
                    where=where_filter,
                    n_results=n_results
                )
                return results
        except Exception as e:
            self.logger.error(f"Failed to query similar identities: {e}")
            return {}

    async def query_funding_network(self, wallet_address: str,
                                  depth: int = 1,
                                  n_results: int = 50) -> Dict[str, Any]:
        """Query funding network for a wallet"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return {}

        try:
            if self._sqlite_store:
                # SQLite fallback: run simple equality filters (source or target) and merge
                qr_src = self._sqlite_store.query(
                    collection=getattr(config, "CHROMADB_FUNDING_COLLECTION", "funding"),
                    query_texts=["funding relationship"],
                    where={"source_wallet": wallet_address},
                    n_results=n_results,
                )
                qr_dst = self._sqlite_store.query(
                    collection=getattr(config, "CHROMADB_FUNDING_COLLECTION", "funding"),
                    query_texts=["funding relationship"],
                    where={"target_wallet": wallet_address},
                    n_results=n_results,
                )
                ids = [list(dict.fromkeys((qr_src.ids[0] if qr_src.ids else []) + (qr_dst.ids[0] if qr_dst.ids else [])))]
                metas = [ (qr_src.metadatas[0] if qr_src.metadatas else []) + (qr_dst.metadatas[0] if qr_dst.metadatas else []) ]
                docs = [ (qr_src.documents[0] if qr_src.documents else []) + (qr_dst.documents[0] if qr_dst.documents else []) ]
                return {"ids": ids, "metadatas": metas, "documents": docs}
            else:
                # Find all connections where wallet is source or target
                where_filter = {
                    "$or": [
                        {"source_wallet": wallet_address},
                        {"target_wallet": wallet_address}
                    ]
                }

                results = self.funding_collection.query(
                    query_texts=["funding relationship"],
                    where=where_filter,
                    n_results=n_results
                )
                return results
        except Exception as e:
            self.logger.error(f"Failed to query funding network: {e}")
            return {}

    async def query_trade_patterns(self, query_text: str,
                                 where_filter: Optional[Dict] = None,
                                 n_results: int = 50) -> Dict[str, Any]:
        """Query trade patterns"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return {}

        try:
            if self._sqlite_store:
                qr = self._sqlite_store.query(
                    collection=getattr(config, "CHROMADB_TRADE_COLLECTION", "trade"),
                    query_texts=[query_text],
                    where=where_filter or {},
                    n_results=n_results,
                )
                return {"ids": qr.ids, "metadatas": qr.metadatas, "documents": qr.documents, "distances": qr.distances}
            else:
                results = self.trade_collection.query(
                    query_texts=[query_text],
                    where=where_filter,
                    n_results=n_results
                )
                return results
        except Exception as e:
            self.logger.error(f"Failed to query trade patterns: {e}")
            return {}

    async def analyze_ethermax_patterns(self, wallet_address: str) -> Dict[str, Any]:
        """Analyze ethermax patterns for a specific wallet"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return {}

        try:
            analysis = {
                "wallet_address": wallet_address,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "identity_analysis": {},
                "funding_analysis": {},
                "trade_analysis": {},
                "ethermax_indicators": {}
            }

            # Analyze identity patterns
            identity_results = await self.query_similar_identities(
                "ethermax pattern coordinated trading",
                where_filter={"wallet_address": wallet_address},
                n_results=5
            )

            if identity_results.get('metadatas'):
                analysis["identity_analysis"] = {
                    "confidence_score": max([m.get('confidence_score', 0) for m in identity_results['metadatas'][0]]),
                    "risk_level": identity_results['metadatas'][0][0].get('risk_level', 'unknown'),
                    "identity_type": identity_results['metadatas'][0][0].get('identity_type', 'unknown')
                }

            # Analyze funding connections
            funding_results = await self.query_funding_network(wallet_address, n_results=20)

            if funding_results.get('metadatas'):
                funding_metas = funding_results['metadatas'][0]
                analysis["funding_analysis"] = {
                    "total_connections": len(funding_metas),
                    "circular_funding": any(m.get('manipulation_indicators', {}).get('circular_funding') for m in funding_metas),
                    "avg_relationship_strength": np.mean([m.get('relationship_metrics', {}).get('relationship_strength', 0) for m in funding_metas])
                }

            # Analyze trade patterns
            trade_results = await self.query_trade_patterns(
                "MAXX trading coordinated buying",
                where_filter={"wallet_address": wallet_address},
                n_results=50
            )

            if trade_results.get('metadatas'):
                trade_metas = trade_results['metadatas'][0]
                analysis["trade_analysis"] = {
                    "total_trades": len(trade_metas),
                    "coordinated_trades": sum(1 for m in trade_metas if m.get('manipulation_analysis', {}).get('coordinated_buying')),
                    "avg_pnl_percent": np.mean([m.get('performance_metrics', {}).get('pnl_percent', 0) for m in trade_metas])
                }

            # Calculate overall ethermax indicators
            identity_confidence = analysis["identity_analysis"].get("confidence_score", 0)
            funding_circular = analysis["funding_analysis"].get("circular_funding", False)
            trade_coordination = analysis["trade_analysis"].get("coordinated_trades", 0) / max(1, analysis["trade_analysis"].get("total_trades", 1))

            ethermax_score = (identity_confidence * 0.4 +
                            (1.0 if funding_circular else 0.0) * 0.3 +
                            trade_coordination * 0.3)

            analysis["ethermax_indicators"] = {
                "ethermax_score": ethermax_score,
                "is_ethermax_candidate": ethermax_score > config.IDENTITY_CONFIDENCE_THRESHOLD,
                "risk_level": "high" if ethermax_score > 0.8 else "medium" if ethermax_score > 0.5 else "low"
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze ethermax patterns: {e}")
            return {}

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        if not self.is_initialized:
            self.logger.error("ChromaDB not initialized")
            return {}

        try:
            stats = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "identity_collection": {},
                "funding_collection": {},
                "trade_collection": {}
            }

            # Collection counts
            if self._sqlite_store:
                identity_count = self._sqlite_store.count(getattr(config, "CHROMADB_IDENTITY_COLLECTION", "identity"))
                funding_count = self._sqlite_store.count(getattr(config, "CHROMADB_FUNDING_COLLECTION", "funding"))
                trade_count = self._sqlite_store.count(getattr(config, "CHROMADB_TRADE_COLLECTION", "trade"))
            else:
                identity_count = self.identity_collection.count()
                funding_count = self.funding_collection.count()
                trade_count = self.trade_collection.count()
            stats["identity_collection"]["document_count"] = identity_count
            stats["funding_collection"]["document_count"] = funding_count
            stats["trade_collection"]["document_count"] = trade_count

            stats["total_documents"] = identity_count + funding_count + trade_count

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {e}")
            return {}

    async def close(self):
        """Close ChromaDB connection"""
        if self.client:
            self.logger.info("Closing ChromaDB connection")
            # ChromaDB doesn't have explicit close method for persistent client
            self.client = None
        if self._sqlite_store:
            try:
                self._sqlite_store.close()
            except Exception:
                pass
        self.is_initialized = False

# Singleton instance
_chromadb_instance = None

async def get_chromadb_instance() -> EthermaxChromaDB:
    """Get or create ChromaDB instance"""
    global _chromadb_instance
    if _chromadb_instance is None:
        _chromadb_instance = EthermaxChromaDB()
        await _chromadb_instance.initialize()
    return _chromadb_instance

# Utility functions for common operations
async def log_trade_execution(wallet_address: str, trade_data: Dict[str, Any]) -> bool:
    """Log trade execution to ChromaDB"""
    chromadb = await get_chromadb_instance()
    return await chromadb.add_trade_history(wallet_address, trade_data)

async def log_funding_pattern(source_wallet: str, target_wallet: str,
                            funding_data: Dict[str, Any]) -> bool:
    """Log funding pattern to ChromaDB"""
    chromadb = await get_chromadb_instance()
    return await chromadb.add_funding_connection(source_wallet, target_wallet, funding_data)

async def update_identity_tracking(wallet_address: str, identity_data: Dict[str, Any]) -> bool:
    """Update identity tracking in ChromaDB"""
    chromadb = await get_chromadb_instance()
    return await chromadb.add_identity_tracking(wallet_address, identity_data)

async def analyze_wallet_patterns(wallet_address: str) -> Dict[str, Any]:
    """Analyze wallet patterns for ethermax detection"""
    chromadb = await get_chromadb_instance()
    return await chromadb.analyze_ethermax_patterns(wallet_address)
