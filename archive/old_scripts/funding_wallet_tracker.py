#!/usr/bin/env python3
"""
Funding Wallet Connection Tracking System for ETHERMAX Identity Analysis
Advanced funding source detection, multi-hop analysis, and network topology mapping
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from decimal import Decimal
import re
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict, Counter, deque
import pickle
import hashlib

# Network analysis imports
import networkx as nx
from networkx.algorithms import community, centrality, shortest_path, connectivity
import igraph as ig

# Machine learning imports
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats
from scipy.spatial.distance import euclidean

# Visualization imports
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns

# ChromaDB integration
from ethermax_chromadb import get_chromadb_instance, log_funding_pattern

# Configuration
import sys
sys.path.append('../../ECOSYSTEM_UNIFIED')
import standalone_config as config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FundingConnection:
    """Data class for funding connections"""
    connection_id: str
    source_wallet: str
    target_wallet: str
    amount: float
    timestamp: datetime
    transaction_hash: str
    block_number: int
    gas_used: int
    gas_price: float
    relationship_type: str
    confidence_score: float
    risk_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FundingPattern:
    """Data class for funding patterns"""
    pattern_id: str
    pattern_type: str
    confidence_score: float
    description: str
    wallets_involved: List[str]
    total_amount: float
    transaction_count: int
    time_span_hours: float
    risk_level: str
    indicators: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkMetrics:
    """Data class for network analysis metrics"""
    wallet_address: str
    centrality_score: float
    betweenness_centrality: float
    closeness_centrality: float
    eigenvector_centrality: float
    pagerank_score: float
    clustering_coefficient: float
    degree_centrality: float
    community_id: int
    influence_score: float
    risk_level: str

class FundingWalletTracker:
    """Main funding wallet tracking system for ethermax identity analysis"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.chromadb = None
        self.is_initialized = False

        # Network graphs
        self.funding_network = nx.DiGraph()
        self.undirected_network = nx.Graph()
        self.igraph_network = None

        # Analysis components
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = DBSCAN(eps=0.5, min_samples=3)

        # Caching
        self.cache_dir = Path("./funding_tracker_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.analysis_cache = {}
        self.connection_cache = {}

        # Real-time monitoring
        self.monitoring_active = False
        self.monitored_wallets = set()
        self.alert_queue = asyncio.Queue()

        # Analysis parameters
        self.analysis_config = {
            "min_funding_amount": 0.01,  # ETH
            "max_hop_distance": 5,
            "circular_funding_threshold": 0.8,
            "coordination_threshold": 0.7,
            "temporal_window_hours": 24,
            "similarity_threshold": 0.8,
            "risk_threshold": 0.6,
            "influence_threshold": 0.5,
            "community_detection_resolution": 1.0
        }

        # Pattern detection thresholds
        self.pattern_thresholds = {
            "layered_funding": {"min_layers": 3, "min_amount_per_layer": 0.1},
            "mixing_pattern": {"min_transactions": 5, "amount_variance_threshold": 0.3},
            "timing_coordination": {"time_window_minutes": 10, "min_wallets": 3},
            "amount_pattern": {"similarity_threshold": 0.9, "min_occurrences": 3},
            "source_pattern": {"repeated_sources": 2, "min_total_amount": 1.0}
        }

    async def initialize(self) -> bool:
        """Initialize the funding wallet tracker"""
        try:
            self.logger.info("Initializing Funding Wallet Tracker...")

            # Initialize ChromaDB connection
            self.chromadb = await get_chromadb_instance()
            if not self.chromadb:
                self.logger.error("Failed to initialize ChromaDB connection")
                return False

            # Load cached data
            await self._load_cached_data()

            # Build initial network from existing data
            await self._build_initial_network()

            # Initialize analysis models
            await self._initialize_analysis_models()

            self.is_initialized = True
            self.logger.info("Funding Wallet Tracker initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize funding wallet tracker: {e}")
            return False

    async def _load_cached_data(self):
        """Load cached analysis data"""
        try:
            # Load connection cache
            connection_cache_file = self.cache_dir / "connection_cache.pkl"
            if connection_cache_file.exists():
                with open(connection_cache_file, 'rb') as f:
                    self.connection_cache = pickle.load(f)
                self.logger.info(f"Loaded {len(self.connection_cache)} cached connections")

            # Load analysis cache
            analysis_cache_file = self.cache_dir / "analysis_cache.pkl"
            if analysis_cache_file.exists():
                with open(analysis_cache_file, 'rb') as f:
                    self.analysis_cache = pickle.load(f)
                self.logger.info(f"Loaded {len(self.analysis_cache)} cached analysis results")

        except Exception as e:
            self.logger.warning(f"Failed to load cached data: {e}")
            self.connection_cache = {}
            self.analysis_cache = {}

    async def _save_cached_data(self):
        """Save analysis data to cache"""
        try:
            # Save connection cache
            connection_cache_file = self.cache_dir / "connection_cache.pkl"
            with open(connection_cache_file, 'wb') as f:
                pickle.dump(self.connection_cache, f)

            # Save analysis cache
            analysis_cache_file = self.cache_dir / "analysis_cache.pkl"
            with open(analysis_cache_file, 'wb') as f:
                pickle.dump(self.analysis_cache, f)

            self.logger.info("Saved cached data")

        except Exception as e:
            self.logger.warning(f"Failed to save cached data: {e}")

    async def _build_initial_network(self):
        """Build initial funding network from existing data"""
        try:
            self.logger.info("Building initial funding network...")

            # Query existing funding connections
            funding_results = await self.chromadb.query_funding_network("", n_results=1000)

            if funding_results.get('metadatas'):
                connections = funding_results['metadatas'][0]

                for conn_data in connections:
                    await self._add_connection_to_network(conn_data)

                self.logger.info(f"Built initial network with {len(connections)} connections")

        except Exception as e:
            self.logger.error(f"Failed to build initial network: {e}")

    async def _initialize_analysis_models(self):
        """Initialize machine learning models"""
        try:
            # Get historical funding data for training
            funding_results = await self.chromadb.query_funding_network("", n_results=500)

            if funding_results.get('metadatas') and len(funding_results['metadatas'][0]) > 50:
                # Extract features for training
                features = []
                for conn_data in funding_results['metadatas'][0]:
                    feature_vector = self._extract_funding_features(conn_data)
                    features.append(feature_vector)

                if len(features) > 10:
                    # Train models
                    features_scaled = self.scaler.fit_transform(features)
                    self.isolation_forest.fit(features_scaled)

                    self.logger.info("ML models trained successfully")

        except Exception as e:
            self.logger.warning(f"Failed to initialize ML models: {e}")

    def _extract_funding_features(self, funding_data: Dict[str, Any]) -> List[float]:
        """Extract features from funding data for ML analysis"""
        try:
            features = []

            # Amount features
            features.append(float(funding_data.get('amount_eth', 0)))
            features.append(float(funding_data.get('gas_used', 0)) / 1000000)  # Normalize gas
            features.append(float(funding_data.get('gas_price', 0)) / 1e9)  # Convert to Gwei

            # Relationship features
            relationship_metrics = funding_data.get('relationship_metrics', {})
            features.append(relationship_metrics.get('relationship_strength', 0))
            features.append(relationship_metrics.get('frequency_score', 0))
            features.append(relationship_metrics.get('amount_consistency', 0))

            # Temporal features
            timestamp = funding_data.get('timestamp', '')
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                features.append(dt.hour)
                features.append(dt.weekday())
            else:
                features.extend([0, 0])

            # Pattern indicators
            features.append(1 if funding_data.get('manipulation_indicators', {}).get('circular_funding') else 0)
            features.append(funding_data.get('manipulation_indicators', {}).get('wash_trading_score', 0))

            return features

        except Exception as e:
            self.logger.error(f"Failed to extract funding features: {e}")
            return [0.0] * 12

    async def add_funding_connection(self, source_wallet: str, target_wallet: str,
                                   amount: float, transaction_hash: str,
                                   block_number: int, gas_used: int, gas_price: float,
                                   additional_metadata: Dict[str, Any] = None) -> bool:
        """Add a new funding connection to the tracking system"""
        try:
            # Validate inputs
            if not self._validate_wallet_address(source_wallet) or not self._validate_wallet_address(target_wallet):
                self.logger.error(f"Invalid wallet addresses: {source_wallet}, {target_wallet}")
                return False

            if amount < self.analysis_config["min_funding_amount"]:
                self.logger.debug(f"Amount {amount} below minimum threshold")
                return False

            # Create connection data
            connection_data = {
                "source_wallet": source_wallet,
                "target_wallet": target_wallet,
                "amount_eth": amount,
                "transaction_hash": transaction_hash,
                "block_number": block_number,
                "gas_used": gas_used,
                "gas_price": gas_price,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "relationship_type": "direct_funding",
                "confidence_score": 1.0,
                "risk_level": "medium"
            }

            # Add analysis metadata
            relationship_metrics = self._analyze_relationship_metrics(source_wallet, target_wallet, amount)
            connection_data["relationship_metrics"] = relationship_metrics

            manipulation_indicators = self._detect_manipulation_indicators(source_wallet, target_wallet, amount)
            connection_data["manipulation_indicators"] = manipulation_indicators

            if additional_metadata:
                connection_data.update(additional_metadata)

            # Store in ChromaDB
            success = await self.chromadb.add_funding_connection(source_wallet, target_wallet, connection_data)
            if not success:
                self.logger.error("Failed to store funding connection in ChromaDB")
                return False

            # Add to network
            await self._add_connection_to_network(connection_data)

            # Update cache
            cache_key = f"{source_wallet}_{target_wallet}_{transaction_hash}"
            self.connection_cache[cache_key] = connection_data

            # Check for alerts
            await self._check_funding_alerts(connection_data)

            self.logger.info(f"Added funding connection: {source_wallet} -> {target_wallet} ({amount} ETH)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add funding connection: {e}")
            return False

    def _validate_wallet_address(self, address: str) -> bool:
        """Validate Ethereum wallet address"""
        return re.match(r'^0x[a-fA-F0-9]{40}$', address) is not None

    def _analyze_relationship_metrics(self, source_wallet: str, target_wallet: str, amount: float) -> Dict[str, Any]:
        """Analyze relationship metrics between wallets"""
        try:
            metrics = {
                "relationship_strength": 0.0,
                "frequency_score": 0.0,
                "amount_consistency": 0.0,
                "total_transacted": 0.0,
                "transaction_count": 0
            }

            # Check existing connections
            if self.funding_network.has_edge(source_wallet, target_wallet):
                edge_data = self.funding_network[source_wallet][target_wallet]
                metrics["total_transacted"] = edge_data.get("total_amount", 0) + amount
                metrics["transaction_count"] = edge_data.get("transaction_count", 0) + 1

                # Calculate relationship strength based on total amount and frequency
                metrics["relationship_strength"] = min(1.0, metrics["total_transacted"] / 10.0)  # Normalize to 10 ETH
                metrics["frequency_score"] = min(1.0, metrics["transaction_count"] / 10.0)  # Normalize to 10 transactions

                # Calculate amount consistency
                previous_amounts = edge_data.get("amounts", [])
                if previous_amounts:
                    amount_variance = np.var(previous_amounts + [amount])
                    metrics["amount_consistency"] = max(0.0, 1.0 - amount_variance)
            else:
                metrics["total_transacted"] = amount
                metrics["transaction_count"] = 1
                metrics["relationship_strength"] = min(1.0, amount / 10.0)
                metrics["frequency_score"] = 0.1  # Base score for first transaction
                metrics["amount_consistency"] = 1.0  # Perfect consistency for first transaction

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to analyze relationship metrics: {e}")
            return {"relationship_strength": 0.0, "frequency_score": 0.0, "amount_consistency": 0.0}

    def _detect_manipulation_indicators(self, source_wallet: str, target_wallet: str, amount: float) -> Dict[str, Any]:
        """Detect manipulation indicators in funding"""
        try:
            indicators = {
                "circular_funding": False,
                "wash_trading_score": 0.0,
                "mixing_pattern": False,
                "timing_anomaly": False,
                "amount_anomaly": False
            }

            # Check for circular funding
            if self.funding_network.has_edge(target_wallet, source_wallet):
                indicators["circular_funding"] = True

            # Check for wash trading patterns
            if self.funding_network.has_edge(source_wallet, target_wallet):
                edge_data = self.funding_network[source_wallet][target_wallet]
                previous_amounts = edge_data.get("amounts", [])

                if previous_amounts:
                    # Check for similar amounts (possible wash trading)
                    similarity_count = sum(1 for prev_amount in previous_amounts
                                         if abs(prev_amount - amount) / max(prev_amount, amount, 1) < 0.1)
                    if similarity_count > 0:
                        indicators["wash_trading_score"] = min(1.0, similarity_count / len(previous_amounts))

            # Check for mixing patterns (multiple small transactions)
            recent_transactions = self._get_recent_transactions(source_wallet, hours=1)
            if len(recent_transactions) > 5:
                total_amount = sum(tx.get("amount", 0) for tx in recent_transactions)
                if total_amount > amount * 2:  # Total much larger than single transaction
                    indicators["mixing_pattern"] = True

            # Check for timing anomalies
            recent_source_transactions = self._get_recent_transactions(source_wallet, hours=1)
            if len(recent_source_transactions) > 10:  # High frequency
                indicators["timing_anomaly"] = True

            # Check for amount anomalies
            all_amounts = [edge_data.get("amount", 0) for _, _, edge_data in self.funding_network.edges(data=True)]
            if all_amounts:
                amount_z_score = abs((amount - np.mean(all_amounts)) / np.std(all_amounts))
                if amount_z_score > 3:  # More than 3 standard deviations
                    indicators["amount_anomaly"] = True

            return indicators

        except Exception as e:
            self.logger.error(f"Failed to detect manipulation indicators: {e}")
            return {"circular_funding": False, "wash_trading_score": 0.0}

    def _get_recent_transactions(self, wallet_address: str, hours: int = 24) -> List[Dict]:
        """Get recent transactions for a wallet"""
        try:
            recent_transactions = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Check outgoing transactions
            if wallet_address in self.funding_network:
                for _, target, edge_data in self.funding_network.out_edges(wallet_address, data=True):
                    tx_time = datetime.fromisoformat(edge_data.get("timestamp", "").replace('Z', '+00:00'))
                    if tx_time > cutoff_time:
                        recent_transactions.append({
                            "target": target,
                            "amount": edge_data.get("amount", 0),
                            "timestamp": edge_data.get("timestamp")
                        })

            return recent_transactions

        except Exception as e:
            self.logger.error(f"Failed to get recent transactions: {e}")
            return []

    async def _add_connection_to_network(self, connection_data: Dict[str, Any]):
        """Add connection to network graphs"""
        try:
            source = connection_data["source_wallet"]
            target = connection_data["target_wallet"]
            amount = connection_data["amount_eth"]
            timestamp = connection_data["timestamp"]

            # Add to directed network
            if self.funding_network.has_edge(source, target):
                edge_data = self.funding_network[source][target]
                edge_data["total_amount"] = edge_data.get("total_amount", 0) + amount
                edge_data["transaction_count"] = edge_data.get("transaction_count", 0) + 1
                edge_data["amounts"] = edge_data.get("amounts", []) + [amount]
                edge_data["timestamps"] = edge_data.get("timestamps", []) + [timestamp]
            else:
                self.funding_network.add_edge(source, target,
                                             amount=amount,
                                             total_amount=amount,
                                             transaction_count=1,
                                             amounts=[amount],
                                             timestamps=[timestamp],
                                             **connection_data)

            # Add to undirected network for community detection
            self.undirected_network.add_edge(source, target, weight=amount)

            # Update igraph network
            await self._update_igraph_network()

        except Exception as e:
            self.logger.error(f"Failed to add connection to network: {e}")

    async def _update_igraph_network(self):
        """Update igraph network for advanced analysis"""
        try:
            # Convert NetworkX to igraph
            edges = [(u, v, data.get('weight', 1)) for u, v, data in self.undirected_network.edges(data=True)]
            vertices = list(self.undirected_network.nodes())

            self.igraph_network = ig.Graph()
            self.igraph_network.add_vertices(len(vertices))
            self.igraph_network.add_edges([(vertices.index(u), vertices.index(v)) for u, v, _ in edges])

            # Add edge weights
            self.igraph_network.es["weight"] = [weight for _, _, weight in edges]

        except Exception as e:
            self.logger.error(f"Failed to update igraph network: {e}")

    async def analyze_funding_sources(self, target_wallet: str, max_depth: int = 5) -> Dict[str, Any]:
        """Analyze funding sources for a target wallet"""
        try:
            self.logger.info(f"Analyzing funding sources for {target_wallet}")

            if target_wallet not in self.funding_network:
                return {"error": "Wallet not found in funding network"}

            # Multi-hop funding chain analysis
            funding_chains = await self._trace_funding_chains(target_wallet, max_depth)

            # Source detection
            original_sources = await self._detect_original_sources(funding_chains)

            # Pattern analysis
            funding_patterns = await self._detect_funding_patterns(target_wallet, funding_chains)

            # Risk assessment
            risk_assessment = await self._assess_funding_risk(target_wallet, funding_chains, funding_patterns)

            # Network metrics
            network_metrics = await self._calculate_network_metrics(target_wallet)

            analysis_result = {
                "target_wallet": target_wallet,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "funding_chains": funding_chains,
                "original_sources": original_sources,
                "funding_patterns": funding_patterns,
                "risk_assessment": risk_assessment,
                "network_metrics": network_metrics,
                "summary": {
                    "total_sources": len(original_sources),
                    "max_chain_depth": max(chain["depth"] for chain in funding_chains) if funding_chains else 0,
                    "total_amount_received": sum(chain["total_amount"] for chain in funding_chains),
                    "high_risk_sources": sum(1 for source in original_sources if source["risk_level"] == "high"),
                    "suspicious_patterns": len([p for p in funding_patterns if p["risk_level"] in ["high", "critical"]])
                }
            }

            # Cache results
            cache_key = f"funding_analysis_{target_wallet}"
            self.analysis_cache[cache_key] = analysis_result
            await self._save_cached_data()

            return analysis_result

        except Exception as e:
            self.logger.error(f"Failed to analyze funding sources: {e}")
            return {"error": str(e)}

    async def _trace_funding_chains(self, target_wallet: str, max_depth: int) -> List[Dict]:
        """Trace multi-hop funding chains"""
        try:
            chains = []
            visited = set()
            queue = deque([(target_wallet, [], 0, 0)])  # (wallet, path, depth, total_amount)

            while queue and len(chains) < 100:  # Limit to prevent explosion
                current_wallet, path, depth, total_amount = queue.popleft()

                if depth >= max_depth or current_wallet in visited:
                    continue

                visited.add(current_wallet)

                # Get incoming transactions
                if current_wallet in self.funding_network:
                    for source, _, edge_data in self.funding_network.in_edges(current_wallet, data=True):
                        amount = edge_data.get("amount", 0)
                        new_path = path + [{
                            "source": source,
                            "target": current_wallet,
                            "amount": amount,
                            "timestamp": edge_data.get("timestamp"),
                            "transaction_hash": edge_data.get("transaction_hash")
                        }]
                        new_total = total_amount + amount

                        if depth == max_depth - 1 or source not in self.funding_network:
                            # End of chain
                            chains.append({
                                "chain_id": str(uuid.uuid4()),
                                "path": new_path,
                                "depth": depth + 1,
                                "total_amount": new_total,
                                "original_source": source,
                                "final_target": target_wallet
                            })
                        else:
                            queue.append((source, new_path, depth + 1, new_total))

            return chains

        except Exception as e:
            self.logger.error(f"Failed to trace funding chains: {e}")
            return []

    async def _detect_original_sources(self, funding_chains: List[Dict]) -> List[Dict]:
        """Detect original funding sources"""
        try:
            sources = defaultdict(lambda: {
                "wallet_address": "",
                "total_amount": 0,
                "transaction_count": 0,
                "first_seen": None,
                "last_seen": None,
                "risk_level": "medium",
                "source_type": "unknown"
            })

            for chain in funding_chains:
                if chain["path"]:
                    first_transaction = chain["path"][0]
                    source_wallet = first_transaction["source"]

                    sources[source_wallet]["wallet_address"] = source_wallet
                    sources[source_wallet]["total_amount"] += chain["total_amount"]
                    sources[source_wallet]["transaction_count"] += 1

                    timestamp = first_transaction["timestamp"]
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if sources[source_wallet]["first_seen"] is None or dt < sources[source_wallet]["first_seen"]:
                            sources[source_wallet]["first_seen"] = dt
                        if sources[source_wallet]["last_seen"] is None or dt > sources[source_wallet]["last_seen"]:
                            sources[source_wallet]["last_seen"] = dt

            # Classify source types and assess risk
            for source_wallet, source_data in sources.items():
                source_data["source_type"] = await self._classify_source_type(source_wallet)
                source_data["risk_level"] = await self._assess_source_risk(source_wallet, source_data)

            return list(sources.values())

        except Exception as e:
            self.logger.error(f"Failed to detect original sources: {e}")
            return []

    async def _classify_source_type(self, wallet_address: str) -> str:
        """Classify the type of funding source"""
        try:
            # Check if it's an exchange
            if self._is_exchange_wallet(wallet_address):
                return "exchange"

            # Check if it's a known mixer
            if self._is_mixer_wallet(wallet_address):
                return "mixer"

            # Check if it's a smart contract
            if self._is_contract_wallet(wallet_address):
                return "contract"

            # Check if it's a mining pool
            if self._is_mining_pool_wallet(wallet_address):
                return "mining_pool"

            # Analyze transaction patterns
            out_degree = self.funding_network.out_degree(wallet_address)
            in_degree = self.funding_network.in_degree(wallet_address)

            if out_degree > 50 and in_degree < 10:
                return "distributor"
            elif in_degree > 50 and out_degree < 10:
                return "collector"
            elif out_degree > 10 and in_degree > 10:
                return "hub"
            else:
                return "individual"

        except Exception as e:
            self.logger.error(f"Failed to classify source type: {e}")
            return "unknown"

    def _is_exchange_wallet(self, wallet_address: str) -> bool:
        """Check if wallet belongs to an exchange"""
        # Known exchange hot wallets (simplified list)
        exchange_wallets = {
            "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance
            "0xD551234Ae421E3BCBA99A0Da6d736074f22192FF",  # Coinbase
            "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap Router
            # Add more exchange wallets as needed
        }
        return wallet_address.lower() in [w.lower() for w in exchange_wallets]

    def _is_mixer_wallet(self, wallet_address: str) -> bool:
        """Check if wallet belongs to a mixer service"""
        # Known mixer contracts (simplified list)
        mixer_wallets = {
            "0x915D55A30891022d3168C817653806b7e0C1d62F",  # Tornado Cash
            # Add more mixer wallets as needed
        }
        return wallet_address.lower() in [w.lower() for w in mixer_wallets]

    def _is_contract_wallet(self, wallet_address: str) -> bool:
        """Check if wallet is a smart contract"""
        # This would typically involve checking if the address has code
        # For now, return False as a placeholder
        return False

    def _is_mining_pool_wallet(self, wallet_address: str) -> bool:
        """Check if wallet belongs to a mining pool"""
        # Known mining pool wallets (simplified list)
        mining_pool_wallets = {
            # Add mining pool wallets as needed
        }
        return wallet_address.lower() in [w.lower() for w in mining_pool_wallets]

    async def _assess_source_risk(self, wallet_address: str, source_data: Dict) -> str:
        """Assess risk level of a funding source"""
        try:
            risk_score = 0.0

            # Source type risk
            source_type = source_data["source_type"]
            type_risk_scores = {
                "exchange": 0.2,
                "individual": 0.3,
                "contract": 0.4,
                "hub": 0.6,
                "distributor": 0.7,
                "collector": 0.8,
                "mining_pool": 0.5,
                "mixer": 0.9,
                "unknown": 0.6
            }
            risk_score += type_risk_scores.get(source_type, 0.6)

            # Transaction pattern risk
            transaction_count = source_data["transaction_count"]
            if transaction_count > 100:
                risk_score += 0.3
            elif transaction_count > 50:
                risk_score += 0.2
            elif transaction_count > 20:
                risk_score += 0.1

            # Amount risk
            total_amount = source_data["total_amount"]
            if total_amount > 100:  # > 100 ETH
                risk_score += 0.3
            elif total_amount > 10:  # > 10 ETH
                risk_score += 0.2
            elif total_amount > 1:  # > 1 ETH
                risk_score += 0.1

            # Network position risk
            if wallet_address in self.funding_network:
                out_degree = self.funding_network.out_degree(wallet_address)
                if out_degree > 100:
                    risk_score += 0.2

            # Normalize to 0-1 and determine risk level
            risk_score = min(1.0, risk_score)

            if risk_score > 0.8:
                return "critical"
            elif risk_score > 0.6:
                return "high"
            elif risk_score > 0.4:
                return "medium"
            else:
                return "low"

        except Exception as e:
            self.logger.error(f"Failed to assess source risk: {e}")
            return "medium"

    async def _detect_funding_patterns(self, target_wallet: str, funding_chains: List[Dict]) -> List[Dict]:
        """Detect funding patterns"""
        try:
            patterns = []

            # Layered funding detection
            layered_pattern = await self._detect_layered_funding(funding_chains)
            if layered_pattern:
                patterns.append(layered_pattern)

            # Mixing pattern detection
            mixing_pattern = await self._detect_mixing_patterns(target_wallet)
            if mixing_pattern:
                patterns.append(mixing_pattern)

            # Timing coordination detection
            timing_pattern = await self._detect_timing_coordination(target_wallet)
            if timing_pattern:
                patterns.append(timing_pattern)

            # Amount pattern detection
            amount_pattern = await self._detect_amount_patterns(funding_chains)
            if amount_pattern:
                patterns.append(amount_pattern)

            # Source pattern detection
            source_pattern = await self._detect_source_patterns(funding_chains)
            if source_pattern:
                patterns.append(source_pattern)

            # Circular funding detection
            circular_pattern = await self._detect_circular_funding(target_wallet)
            if circular_pattern:
                patterns.append(circular_pattern)

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to detect funding patterns: {e}")
            return []

    async def _detect_layered_funding(self, funding_chains: List[Dict]) -> Optional[Dict]:
        """Detect layered funding patterns"""
        try:
            # Group chains by depth
            depth_groups = defaultdict(list)
            for chain in funding_chains:
                depth_groups[chain["depth"]].append(chain)

            # Check for multiple layers
            if len(depth_groups) >= self.pattern_thresholds["layered_funding"]["min_layers"]:
                total_amount_per_layer = {}
                for depth, chains in depth_groups.items():
                    total_amount_per_layer[depth] = sum(chain["total_amount"] for chain in chains)

                # Check if each layer has significant amount
                significant_layers = sum(1 for amount in total_amount_per_layer.values()
                                       if amount >= self.pattern_thresholds["layered_funding"]["min_amount_per_layer"])

                if significant_layers >= len(depth_groups):
                    return {
                        "pattern_id": str(uuid.uuid4()),
                        "pattern_type": "layered_funding",
                        "confidence_score": min(1.0, significant_layers / len(depth_groups)),
                        "description": f"Multi-layered funding detected across {len(depth_groups)} layers",
                        "layers": len(depth_groups),
                        "total_amount": sum(total_amount_per_layer.values()),
                        "amount_per_layer": total_amount_per_layer,
                        "risk_level": "high" if len(depth_groups) > 5 else "medium"
                    }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect layered funding: {e}")
            return None

    async def _detect_mixing_patterns(self, target_wallet: str) -> Optional[Dict]:
        """Detect fund mixing patterns"""
        try:
            # Get incoming transactions to target
            incoming_transactions = []
            if target_wallet in self.funding_network:
                for source, _, edge_data in self.funding_network.in_edges(target_wallet, data=True):
                    incoming_transactions.append({
                        "source": source,
                        "amount": edge_data.get("amount", 0),
                        "timestamp": edge_data.get("timestamp")
                    })

            if len(incoming_transactions) >= self.pattern_thresholds["mixing_pattern"]["min_transactions"]:
                amounts = [tx["amount"] for tx in incoming_transactions]
                amount_variance = np.var(amounts)
                amount_mean = np.mean(amounts)

                # Check for low variance (similar amounts)
                if amount_variance > 0:
                    coefficient_of_variation = np.sqrt(amount_variance) / amount_mean
                    if coefficient_of_variation < self.pattern_thresholds["mixing_pattern"]["amount_variance_threshold"]:
                        return {
                            "pattern_id": str(uuid.uuid4()),
                            "pattern_type": "mixing_pattern",
                            "confidence_score": 1.0 - coefficient_of_variation,
                            "description": f"Fund mixing detected with {len(incoming_transactions)} similar transactions",
                            "transaction_count": len(incoming_transactions),
                            "amount_variance": amount_variance,
                            "coefficient_of_variation": coefficient_of_variation,
                            "total_amount": sum(amounts),
                            "risk_level": "high"
                        }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect mixing patterns: {e}")
            return None

    async def _detect_timing_coordination(self, target_wallet: str) -> Optional[Dict]:
        """Detect timing coordination patterns"""
        try:
            # Get incoming transactions with timestamps
            incoming_transactions = []
            if target_wallet in self.funding_network:
                for source, _, edge_data in self.funding_network.in_edges(target_wallet, data=True):
                    timestamp_str = edge_data.get("timestamp")
                    if timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        incoming_transactions.append({
                            "source": source,
                            "amount": edge_data.get("amount", 0),
                            "timestamp": dt
                        })

            if len(incoming_transactions) >= self.pattern_thresholds["timing_coordination"]["min_wallets"]:
                # Sort by timestamp
                incoming_transactions.sort(key=lambda x: x["timestamp"])

                # Look for clusters of transactions in short time windows
                time_window = timedelta(minutes=self.pattern_thresholds["timing_coordination"]["time_window_minutes"])
                coordinated_groups = []

                i = 0
                while i < len(incoming_transactions):
                    window_start = incoming_transactions[i]["timestamp"]
                    window_end = window_start + time_window
                    window_transactions = [incoming_transactions[i]]

                    j = i + 1
                    while j < len(incoming_transactions) and incoming_transactions[j]["timestamp"] <= window_end:
                        window_transactions.append(incoming_transactions[j])
                        j += 1

                    if len(window_transactions) >= self.pattern_thresholds["timing_coordination"]["min_wallets"]:
                        unique_sources = set(tx["source"] for tx in window_transactions)
                        if len(unique_sources) >= self.pattern_thresholds["timing_coordination"]["min_wallets"]:
                            coordinated_groups.append({
                                "start_time": window_start,
                                "end_time": window_end,
                                "transaction_count": len(window_transactions),
                                "unique_sources": len(unique_sources),
                                "total_amount": sum(tx["amount"] for tx in window_transactions)
                            })

                    i = j

                if coordinated_groups:
                    return {
                        "pattern_id": str(uuid.uuid4()),
                        "pattern_type": "timing_coordination",
                        "confidence_score": min(1.0, len(coordinated_groups) / 5),
                        "description": f"Timing coordination detected with {len(coordinated_groups)} coordinated groups",
                        "coordinated_groups": coordinated_groups,
                        "total_groups": len(coordinated_groups),
                        "risk_level": "high" if len(coordinated_groups) > 3 else "medium"
                    }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect timing coordination: {e}")
            return None

    async def _detect_amount_patterns(self, funding_chains: List[Dict]) -> Optional[Dict]:
        """Detect amount-based patterns"""
        try:
            # Extract all amounts from chains
            all_amounts = []
            for chain in funding_chains:
                for transaction in chain["path"]:
                    all_amounts.append(transaction["amount"])

            if len(all_amounts) >= self.pattern_thresholds["amount_pattern"]["min_occurrences"]:
                # Find recurring amounts
                amount_counts = Counter(round(amount, 6) for amount in all_amounts)  # Round to handle precision
                recurring_amounts = [(amount, count) for amount, count in amount_counts.items()
                                   if count >= self.pattern_thresholds["amount_pattern"]["min_occurrences"]]

                if recurring_amounts:
                    # Calculate similarity score
                    total_recurring = sum(count for _, count in recurring_amounts)
                    similarity_score = total_recurring / len(all_amounts)

                    if similarity_score >= self.pattern_thresholds["amount_pattern"]["similarity_threshold"]:
                        return {
                            "pattern_id": str(uuid.uuid4()),
                            "pattern_type": "amount_pattern",
                            "confidence_score": similarity_score,
                            "description": f"Recurring amount pattern detected with {len(recurring_amounts)} unique amounts",
                            "recurring_amounts": [{"amount": amount, "count": count} for amount, count in recurring_amounts],
                            "total_transactions": len(all_amounts),
                            "recurring_transactions": total_recurring,
                            "risk_level": "high" if similarity_score > 0.95 else "medium"
                        }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect amount patterns: {e}")
            return None

    async def _detect_source_patterns(self, funding_chains: List[Dict]) -> Optional[Dict]:
        """Detect source-based patterns"""
        try:
            # Extract all original sources
            original_sources = [chain["original_source"] for chain in funding_chains]
            source_counts = Counter(original_sources)

            # Find repeated sources
            repeated_sources = [(source, count) for source, count in source_counts.items()
                              if count >= self.pattern_thresholds["source_pattern"]["repeated_sources"]]

            if repeated_sources:
                # Calculate total amount from repeated sources
                total_from_repeated = 0
                for source, count in repeated_sources:
                    for chain in funding_chains:
                        if chain["original_source"] == source:
                            total_from_repeated += chain["total_amount"]

                if total_from_repeated >= self.pattern_thresholds["source_pattern"]["min_total_amount"]:
                    return {
                        "pattern_id": str(uuid.uuid4()),
                        "pattern_type": "source_pattern",
                        "confidence_score": min(1.0, len(repeated_sources) / 5),
                        "description": f"Repeated source pattern detected with {len(repeated_sources)} recurring sources",
                        "repeated_sources": [{"source": source, "count": count} for source, count in repeated_sources],
                        "total_amount_from_repeated": total_from_repeated,
                        "risk_level": "high" if len(repeated_sources) > 5 else "medium"
                    }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect source patterns: {e}")
            return None

    async def _detect_circular_funding(self, target_wallet: str) -> Optional[Dict]:
        """Detect circular funding patterns"""
        try:
            # Find cycles in the funding network
            cycles = list(nx.simple_cycles(self.funding_network.to_undirected()))

            # Filter cycles that include the target wallet
            target_cycles = [cycle for cycle in cycles if target_wallet in cycle]

            if target_cycles:
                # Analyze cycles
                cycle_details = []
                for cycle in target_cycles:
                    cycle_amount = 0
                    cycle_transactions = 0

                    for i in range(len(cycle)):
                        source = cycle[i]
                        target = cycle[(i + 1) % len(cycle)]

                        if self.funding_network.has_edge(source, target):
                            edge_data = self.funding_network[source][target]
                            cycle_amount += edge_data.get("total_amount", 0)
                            cycle_transactions += edge_data.get("transaction_count", 0)

                    cycle_details.append({
                        "cycle_length": len(cycle),
                        "total_amount": cycle_amount,
                        "transaction_count": cycle_transactions,
                        "wallets": cycle
                    })

                return {
                    "pattern_id": str(uuid.uuid4()),
                    "pattern_type": "circular_funding",
                    "confidence_score": min(1.0, len(target_cycles) / 3),
                    "description": f"Circular funding detected with {len(target_cycles)} cycles",
                    "cycles": cycle_details,
                    "total_cycles": len(target_cycles),
                    "risk_level": "critical"
                }

            return None

        except Exception as e:
            self.logger.error(f"Failed to detect circular funding: {e}")
            return None

    async def _assess_funding_risk(self, target_wallet: str, funding_chains: List[Dict],
                                 funding_patterns: List[Dict]) -> Dict[str, Any]:
        """Assess overall funding risk"""
        try:
            risk_assessment = {
                "overall_risk_score": 0.0,
                "risk_level": "low",
                "risk_factors": {},
                "high_risk_indicators": [],
                "mitigation_recommendations": []
            }

            # Source risk
            original_sources = await self._detect_original_sources(funding_chains)
            high_risk_sources = sum(1 for source in original_sources if source["risk_level"] in ["high", "critical"])
            source_risk_score = high_risk_sources / len(original_sources) if original_sources else 0

            # Pattern risk
            high_risk_patterns = [p for p in funding_patterns if p["risk_level"] in ["high", "critical"]]
            pattern_risk_score = len(high_risk_patterns) / len(funding_patterns) if funding_patterns else 0

            # Chain depth risk
            max_depth = max(chain["depth"] for chain in funding_chains) if funding_chains else 0
            depth_risk_score = min(1.0, max_depth / 5)

            # Amount risk
            total_amount = sum(chain["total_amount"] for chain in funding_chains)
            amount_risk_score = min(1.0, total_amount / 100)  # Normalize to 100 ETH

            # Calculate overall risk score
            risk_assessment["overall_risk_score"] = (
                source_risk_score * 0.3 +
                pattern_risk_score * 0.3 +
                depth_risk_score * 0.2 +
                amount_risk_score * 0.2
            )

            # Determine risk level
            if risk_assessment["overall_risk_score"] > 0.8:
                risk_assessment["risk_level"] = "critical"
            elif risk_assessment["overall_risk_score"] > 0.6:
                risk_assessment["risk_level"] = "high"
            elif risk_assessment["overall_risk_score"] > 0.4:
                risk_assessment["risk_level"] = "medium"
            else:
                risk_assessment["risk_level"] = "low"

            # Detailed risk factors
            risk_assessment["risk_factors"] = {
                "source_risk": {
                    "score": source_risk_score,
                    "description": f"{high_risk_sources} high-risk sources out of {len(original_sources)}",
                    "level": "high" if source_risk_score > 0.5 else "medium" if source_risk_score > 0.2 else "low"
                },
                "pattern_risk": {
                    "score": pattern_risk_score,
                    "description": f"{len(high_risk_patterns)} high-risk patterns out of {len(funding_patterns)}",
                    "level": "high" if pattern_risk_score > 0.5 else "medium" if pattern_risk_score > 0.2 else "low"
                },
                "depth_risk": {
                    "score": depth_risk_score,
                    "description": f"Maximum funding chain depth: {max_depth}",
                    "level": "high" if max_depth > 4 else "medium" if max_depth > 2 else "low"
                },
                "amount_risk": {
                    "score": amount_risk_score,
                    "description": f"Total funding amount: {total_amount:.2f} ETH",
                    "level": "high" if total_amount > 50 else "medium" if total_amount > 10 else "low"
                }
            }

            # High-risk indicators
            if high_risk_sources > 0:
                risk_assessment["high_risk_indicators"].append("High-risk funding sources detected")

            if len(high_risk_patterns) > 0:
                risk_assessment["high_risk_indicators"].append("Suspicious funding patterns detected")

            if max_depth > 4:
                risk_assessment["high_risk_indicators"].append("Deep funding chains detected")

            if total_amount > 50:
                risk_assessment["high_risk_indicators"].append("Large funding amounts detected")

            # Mitigation recommendations
            if risk_assessment["risk_level"] in ["high", "critical"]:
                risk_assessment["mitigation_recommendations"].extend([
                    "Enhanced monitoring of wallet activity",
                    "Investigate funding sources thoroughly",
                    "Consider transaction limits"
                ])

            if high_risk_sources > 0:
                risk_assessment["mitigation_recommendations"].append("Block or limit transactions from high-risk sources")

            if len(high_risk_patterns) > 0:
                risk_assessment["mitigation_recommendations"].append("Implement pattern detection alerts")

            return risk_assessment

        except Exception as e:
            self.logger.error(f"Failed to assess funding risk: {e}")
            return {"overall_risk_score": 0.0, "risk_level": "low"}

    async def _calculate_network_metrics(self, wallet_address: str) -> Dict[str, Any]:
        """Calculate network metrics for a wallet"""
        try:
            if wallet_address not in self.funding_network:
                return {"error": "Wallet not found in network"}

            # Basic centrality measures
            degree_centrality = nx.degree_centrality(self.funding_network)
            betweenness_centrality = nx.betweenness_centrality(self.funding_network)
            closeness_centrality = nx.closeness_centrality(self.funding_network)
            eigenvector_centrality = nx.eigenvector_centrality(self.funding_network, max_iter=1000)
            pagerank = nx.pagerank(self.funding_network)

            # Clustering coefficient
            clustering_coefficient = nx.clustering(self.undirected_network, wallet_address)

            # Community detection
            communities = community.louvain_communities(self.undirected_network)
            community_id = None
            for i, comm in enumerate(communities):
                if wallet_address in comm:
                    community_id = i
                    break

            # Influence score (composite metric)
            influence_score = (
                degree_centrality.get(wallet_address, 0) * 0.3 +
                betweenness_centrality.get(wallet_address, 0) * 0.3 +
                pagerank.get(wallet_address, 0) * 0.4
            )

            # Risk level based on network position
            network_risk = "low"
            if influence_score > 0.1:
                network_risk = "high"
            elif influence_score > 0.05:
                network_risk = "medium"

            metrics = {
                "wallet_address": wallet_address,
                "degree_centrality": degree_centrality.get(wallet_address, 0),
                "betweenness_centrality": betweenness_centrality.get(wallet_address, 0),
                "closeness_centrality": closeness_centrality.get(wallet_address, 0),
                "eigenvector_centrality": eigenvector_centrality.get(wallet_address, 0),
                "pagerank_score": pagerank.get(wallet_address, 0),
                "clustering_coefficient": clustering_coefficient,
                "community_id": community_id,
                "influence_score": influence_score,
                "network_risk": network_risk,
                "network_position": {
                    "in_degree": self.funding_network.in_degree(wallet_address),
                    "out_degree": self.funding_network.out_degree(wallet_address),
                    "total_connections": self.funding_network.degree(wallet_address)
                }
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to calculate network metrics: {e}")
            return {"error": str(e)}

    async def detect_circular_funding_patterns(self, wallet_address: str = None) -> List[Dict]:
        """Detect circular funding patterns in the network"""
        try:
            self.logger.info(f"Detecting circular funding patterns for wallet: {wallet_address or 'all wallets'}")

            circular_patterns = []

            # Find all cycles in the network
            if wallet_address:
                # Find cycles involving specific wallet
                subgraph = nx.ego_graph(self.funding_network, wallet_address, radius=3)
                cycles = list(nx.simple_cycles(subgraph))
            else:
                # Find all cycles in the network
                cycles = list(nx.simple_cycles(self.funding_network.to_undirected()))

            # Analyze each cycle
            for cycle in cycles:
                if len(cycle) < 3:  # Skip trivial cycles
                    continue

                cycle_analysis = await self._analyze_funding_cycle(cycle)
                if cycle_analysis:
                    circular_patterns.append(cycle_analysis)

            # Sort by risk score
            circular_patterns.sort(key=lambda x: x["risk_score"], reverse=True)

            self.logger.info(f"Found {len(circular_patterns)} circular funding patterns")
            return circular_patterns

        except Exception as e:
            self.logger.error(f"Failed to detect circular funding patterns: {e}")
            return []

    async def _analyze_funding_cycle(self, cycle: List[str]) -> Optional[Dict]:
        """Analyze a specific funding cycle"""
        try:
            cycle_data = {
                "cycle_id": str(uuid.uuid4()),
                "wallets": cycle,
                "cycle_length": len(cycle),
                "total_amount": 0.0,
                "transaction_count": 0,
                "risk_score": 0.0,
                "risk_level": "medium",
                "transactions": [],
                "timing_patterns": [],
                "amount_patterns": []
            }

            # Analyze each edge in the cycle
            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]

                if self.funding_network.has_edge(source, target):
                    edge_data = self.funding_network[source][target]

                    cycle_data["total_amount"] += edge_data.get("total_amount", 0)
                    cycle_data["transaction_count"] += edge_data.get("transaction_count", 0)

                    # Add transaction details
                    for j, amount in enumerate(edge_data.get("amounts", [])):
                        cycle_data["transactions"].append({
                            "source": source,
                            "target": target,
                            "amount": amount,
                            "timestamp": edge_data.get("timestamps", [])[j] if j < len(edge_data.get("timestamps", [])) else None
                        })

            # Calculate timing patterns
            timestamps = [tx["timestamp"] for tx in cycle_data["transactions"] if tx["timestamp"]]
            if timestamps:
                # Convert to datetime objects
                datetimes = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
                time_span = (max(datetimes) - min(datetimes)).total_seconds() / 3600  # Hours

                cycle_data["timing_patterns"] = {
                    "time_span_hours": time_span,
                    "first_transaction": min(datetimes).isoformat(),
                    "last_transaction": max(datetimes).isoformat(),
                    "transaction_frequency": len(timestamps) / max(time_span, 1)
                }

            # Calculate amount patterns
            amounts = [tx["amount"] for tx in cycle_data["transactions"]]
            if amounts:
                cycle_data["amount_patterns"] = {
                    "total_amount": sum(amounts),
                    "average_amount": np.mean(amounts),
                    "amount_variance": np.var(amounts),
                    "min_amount": min(amounts),
                    "max_amount": max(amounts)
                }

            # Calculate risk score
            risk_factors = []

            # Cycle length risk
            if len(cycle) > 5:
                risk_factors.append(0.3)
            elif len(cycle) > 3:
                risk_factors.append(0.2)

            # Amount risk
            if cycle_data["total_amount"] > 10:
                risk_factors.append(0.3)
            elif cycle_data["total_amount"] > 1:
                risk_factors.append(0.2)

            # Transaction frequency risk
            if cycle_data["timing_patterns"]:
                freq = cycle_data["timing_patterns"]["transaction_frequency"]
                if freq > 10:  # More than 10 transactions per hour
                    risk_factors.append(0.3)
                elif freq > 5:
                    risk_factors.append(0.2)

            # Amount consistency risk (possible wash trading)
            if cycle_data["amount_patterns"]:
                variance = cycle_data["amount_patterns"]["amount_variance"]
                mean = cycle_data["amount_patterns"]["average_amount"]
                if mean > 0:
                    cv = np.sqrt(variance) / mean
                    if cv < 0.1:  # Very consistent amounts
                        risk_factors.append(0.4)

            # Calculate overall risk score
            cycle_data["risk_score"] = sum(risk_factors)

            # Determine risk level
            if cycle_data["risk_score"] > 0.8:
                cycle_data["risk_level"] = "critical"
            elif cycle_data["risk_score"] > 0.6:
                cycle_data["risk_level"] = "high"
            elif cycle_data["risk_score"] > 0.3:
                cycle_data["risk_level"] = "medium"
            else:
                cycle_data["risk_level"] = "low"

            return cycle_data

        except Exception as e:
            self.logger.error(f"Failed to analyze funding cycle: {e}")
            return None

    async def build_funding_topology(self, wallet_address: str = None, depth: int = 3) -> Dict[str, Any]:
        """Build funding network topology map"""
        try:
            self.logger.info(f"Building funding topology for wallet: {wallet_address or 'network overview'}")

            topology = {
                "topology_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "center_wallet": wallet_address,
                "depth": depth,
                "network_stats": {},
                "communities": [],
                "influential_nodes": [],
                "bridges": [],
                "isolated_clusters": [],
                "visualization_data": {}
            }

            # Build subgraph
            if wallet_address:
                subgraph = nx.ego_graph(self.funding_network, wallet_address, radius=depth)
            else:
                subgraph = self.funding_network

            # Network statistics
            topology["network_stats"] = {
                "total_nodes": subgraph.number_of_nodes(),
                "total_edges": subgraph.number_of_edges(),
                "density": nx.density(subgraph),
                "is_connected": nx.is_weakly_connected(subgraph),
                "average_clustering": nx.average_clustering(subgraph.to_undirected()),
                "strongly_connected_components": nx.number_strongly_connected_components(subgraph)
            }

            # Community detection
            communities = community.louvain_communities(subgraph.to_undirected())
            for i, comm in enumerate(communities):
                if len(comm) > 2:  # Only include communities with more than 2 nodes
                    topology["communities"].append({
                        "community_id": i,
                        "size": len(comm),
                        "members": list(comm),
                        "internal_density": nx.density(subgraph.subgraph(comm)),
                        "modularity": self._calculate_modularity(subgraph.to_undirected(), comm)
                    })

            # Influential nodes (high centrality)
            centrality_measures = {
                "degree": nx.degree_centrality(subgraph),
                "betweenness": nx.betweenness_centrality(subgraph),
                "closeness": nx.closeness_centrality(subgraph),
                "eigenvector": nx.eigenvector_centrality(subgraph, max_iter=1000)
            }

            # Find top influential nodes
            influence_scores = {}
            for node in subgraph.nodes():
                influence_scores[node] = (
                    centrality_measures["degree"].get(node, 0) * 0.3 +
                    centrality_measures["betweenness"].get(node, 0) * 0.3 +
                    centrality_measures["closeness"].get(node, 0) * 0.2 +
                    centrality_measures["eigenvector"].get(node, 0) * 0.2
                )

            top_influential = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            for node, score in top_influential:
                topology["influential_nodes"].append({
                    "wallet_address": node,
                    "influence_score": score,
                    "degree_centrality": centrality_measures["degree"].get(node, 0),
                    "betweenness_centrality": centrality_measures["betweenness"].get(node, 0),
                    "closeness_centrality": centrality_measures["closeness"].get(node, 0),
                    "eigenvector_centrality": centrality_measures["eigenvector"].get(node, 0)
                })

            # Find bridge nodes (high betweenness centrality)
            bridge_threshold = np.mean(list(centrality_measures["betweenness"].values())) + np.std(list(centrality_measures["betweenness"].values()))
            for node, score in centrality_measures["betweenness"].items():
                if score > bridge_threshold:
                    topology["bridges"].append({
                        "wallet_address": node,
                        "betweenness_score": score,
                        "bridge_strength": score / bridge_threshold
                    })

            # Find isolated clusters
            if not nx.is_weakly_connected(subgraph):
                weakly_connected_components = list(nx.weakly_connected_components(subgraph))
                for component in weakly_connected_components:
                    if len(component) > 1 and (wallet_address is None or wallet_address not in component):
                        topology["isolated_clusters"].append({
                            "cluster_id": str(uuid.uuid4()),
                            "size": len(component),
                            "members": list(component),
                            "isolation_reason": "disconnected_from_main_network"
                        })

            # Prepare visualization data
            topology["visualization_data"] = await self._prepare_topology_visualization(subgraph, influence_scores)

            self.logger.info(f"Built topology with {topology['network_stats']['total_nodes']} nodes and {topology['network_stats']['total_edges']} edges")
            return topology

        except Exception as e:
            self.logger.error(f"Failed to build funding topology: {e}")
            return {"error": str(e)}

    def _calculate_modularity(self, graph: nx.Graph, community: Set) -> float:
        """Calculate modularity for a community"""
        try:
            # Simplified modularity calculation
            internal_edges = 0
            total_degree = 0

            for node in community:
                total_degree += graph.degree(node)
                for neighbor in graph.neighbors(node):
                    if neighbor in community:
                        internal_edges += 1

            internal_edges //= 2  # Each edge counted twice
            total_possible_edges = len(community) * (len(community) - 1) // 2

            if total_possible_edges == 0:
                return 0.0

            return internal_edges / total_possible_edges

        except Exception as e:
            self.logger.error(f"Failed to calculate modularity: {e}")
            return 0.0

    async def _prepare_topology_visualization(self, subgraph: nx.DiGraph, influence_scores: Dict) -> Dict[str, Any]:
        """Prepare data for network visualization"""
        try:
            # Node positions using spring layout
            pos = nx.spring_layout(subgraph, k=1, iterations=50)

            # Prepare nodes data
            nodes = []
            for node in subgraph.nodes():
                nodes.append({
                    "id": node,
                    "label": node[:8] + "...",  # Shortened address
                    "x": pos[node][0],
                    "y": pos[node][1],
                    "size": 5 + influence_scores.get(node, 0) * 20,  # Size based on influence
                    "color": self._get_node_color(influence_scores.get(node, 0)),
                    "influence_score": influence_scores.get(node, 0),
                    "degree": subgraph.degree(node)
                })

            # Prepare edges data
            edges = []
            for source, target, edge_data in subgraph.edges(data=True):
                edges.append({
                    "source": source,
                    "target": target,
                    "weight": edge_data.get("weight", 1),
                    "amount": edge_data.get("total_amount", 0),
                    "transaction_count": edge_data.get("transaction_count", 1)
                })

            return {
                "nodes": nodes,
                "edges": edges,
                "layout": "spring",
                "metrics": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "max_influence": max(influence_scores.values()) if influence_scores else 0,
                    "avg_influence": np.mean(list(influence_scores.values())) if influence_scores else 0
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to prepare topology visualization: {e}")
            return {"nodes": [], "edges": []}

    def _get_node_color(self, influence_score: float) -> str:
        """Get color based on influence score"""
        if influence_score > 0.1:
            return "#ff0000"  # Red for high influence
        elif influence_score > 0.05:
            return "#ff7f00"  # Orange for medium-high influence
        elif influence_score > 0.02:
            return "#ffff00"  # Yellow for medium influence
        elif influence_score > 0.01:
            return "#00ff00"  # Green for low-medium influence
        else:
            return "#0000ff"  # Blue for low influence

    async def start_real_time_monitoring(self, wallet_addresses: List[str] = None) -> bool:
        """Start real-time funding flow monitoring"""
        try:
            self.logger.info("Starting real-time funding flow monitoring...")

            if wallet_addresses:
                self.monitored_wallets.update(wallet_addresses)
            else:
                # Monitor all wallets in current network
                self.monitored_wallets.update(self.funding_network.nodes())

            self.monitoring_active = True

            # Start monitoring task
            monitoring_task = asyncio.create_task(self._monitoring_loop())

            self.logger.info(f"Started real-time monitoring for {len(self.monitored_wallets)} wallets")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start real-time monitoring: {e}")
            return False

    async def _monitoring_loop(self):
        """Main monitoring loop for real-time funding flow"""
        try:
            while self.monitoring_active:
                for wallet in list(self.monitored_wallets):
                    # Check for new funding connections
                    await self._check_new_funding(wallet)

                    # Analyze funding patterns
                    await self._analyze_real_time_patterns(wallet)

                # Process alerts
                await self._process_alerts()

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            self.logger.error(f"Monitoring loop error: {e}")

    async def _check_new_funding(self, wallet_address: str):
        """Check for new funding connections"""
        try:
            # This would typically involve querying blockchain data
            # For now, we'll simulate with existing data
            pass

        except Exception as e:
            self.logger.error(f"Failed to check new funding: {e}")

    async def _analyze_real_time_patterns(self, wallet_address: str):
        """Analyze patterns in real-time"""
        try:
            # Get recent funding activity
            recent_analysis = await self.analyze_funding_sources(wallet_address)

            # Check for suspicious patterns
            if recent_analysis.get("funding_patterns"):
                for pattern in recent_analysis["funding_patterns"]:
                    if pattern["risk_level"] in ["high", "critical"]:
                        await self._queue_alert({
                            "type": "suspicious_pattern",
                            "wallet": wallet_address,
                            "pattern": pattern,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

        except Exception as e:
            self.logger.error(f"Failed to analyze real-time patterns: {e}")

    async def _queue_alert(self, alert: Dict):
        """Queue an alert for processing"""
        await self.alert_queue.put(alert)

    async def _process_alerts(self):
        """Process queued alerts"""
        try:
            while not self.alert_queue.empty():
                alert = await self.alert_queue.get()
                await self._handle_alert(alert)

        except Exception as e:
            self.logger.error(f"Failed to process alerts: {e}")

    async def _handle_alert(self, alert: Dict):
        """Handle individual alert"""
        try:
            self.logger.warning(f"FUNDING ALERT: {alert['type']} for wallet {alert['wallet']}")

            # Save alert to file
            alert_file = self.cache_dir / f"funding_alert_{int(time.time())}.json"
            with open(alert_file, 'w') as f:
                json.dump(alert, f, indent=2)

            # Here you could add additional alert handling:
            # - Send notifications
            # - Trigger automated responses
            # - Update monitoring systems

        except Exception as e:
            self.logger.error(f"Failed to handle alert: {e}")

    async def _check_funding_alerts(self, connection_data: Dict[str, Any]):
        """Check for alerts in new funding connections"""
        try:
            alerts = []

            # Check manipulation indicators
            manipulation_indicators = connection_data.get("manipulation_indicators", {})
            if manipulation_indicators.get("circular_funding"):
                alerts.append({
                    "type": "circular_funding",
                    "severity": "high",
                    "description": "Circular funding detected"
                })

            if manipulation_indicators.get("wash_trading_score", 0) > 0.7:
                alerts.append({
                    "type": "wash_trading",
                    "severity": "high",
                    "description": "Potential wash trading detected"
                })

            # Check amount anomalies
            amount = connection_data.get("amount_eth", 0)
            if amount > 10:  # Large amount
                alerts.append({
                    "type": "large_amount",
                    "severity": "medium",
                    "description": f"Large funding amount: {amount} ETH"
                })

            # Queue alerts
            for alert in alerts:
                await self._queue_alert({
                    **alert,
                    "source_wallet": connection_data["source_wallet"],
                    "target_wallet": connection_data["target_wallet"],
                    "amount": amount,
                    "timestamp": connection_data["timestamp"]
                })

        except Exception as e:
            self.logger.error(f"Failed to check funding alerts: {e}")

    async def generate_funding_report(self, wallet_address: str = None, format_type: str = "json") -> Dict[str, Any]:
        """Generate comprehensive funding analysis report"""
        try:
            self.logger.info(f"Generating funding report for wallet: {wallet_address or 'network overview'}")

            # Get funding analysis
            if wallet_address:
                funding_analysis = await self.analyze_funding_sources(wallet_address)
                circular_patterns = await self.detect_circular_funding_patterns(wallet_address)
                topology = await self.build_funding_topology(wallet_address)
            else:
                funding_analysis = {"error": "Wallet address required for detailed analysis"}
                circular_patterns = await self.detect_circular_funding_patterns()
                topology = await self.build_funding_topology()

            # Generate report structure
            report = {
                "report_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "wallet_address": wallet_address,
                    "report_type": "funding_analysis",
                    "format": format_type,
                    "version": "1.0.0"
                },
                "executive_summary": self._generate_funding_executive_summary(funding_analysis, circular_patterns, topology),
                "funding_analysis": funding_analysis,
                "circular_patterns": circular_patterns,
                "network_topology": topology,
                "recommendations": self._generate_funding_recommendations(funding_analysis, circular_patterns),
                "risk_assessment": funding_analysis.get("risk_assessment", {}),
                "appendix": {
                    "methodology": "Advanced funding source detection using graph theory and pattern recognition",
                    "data_sources": "ChromaDB funding connections, network analysis, real-time monitoring",
                    "confidence_level": self._calculate_funding_confidence(funding_analysis)
                }
            }

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate funding report: {e}")
            return {"error": str(e)}

    def _generate_funding_executive_summary(self, funding_analysis: Dict, circular_patterns: List[Dict], topology: Dict) -> Dict[str, Any]:
        """Generate executive summary for funding analysis"""
        try:
            summary = {
                "key_findings": [],
                "risk_level": "low",
                "suspicious_indicators": [],
                "network_health": "healthy",
                "critical_alerts": []
            }

            # Extract key findings from funding analysis
            if funding_analysis.get("summary"):
                funding_summary = funding_analysis["summary"]
                summary["key_findings"].append(f"Total funding sources: {funding_summary.get('total_sources', 0)}")
                summary["key_findings"].append(f"Maximum chain depth: {funding_summary.get('max_chain_depth', 0)}")
                summary["key_findings"].append(f"Total amount received: {funding_summary.get('total_amount_received', 0):.2f} ETH")

                if funding_summary.get("high_risk_sources", 0) > 0:
                    summary["key_findings"].append(f"High-risk sources detected: {funding_summary['high_risk_sources']}")

                if funding_summary.get("suspicious_patterns", 0) > 0:
                    summary["key_findings"].append(f"Suspicious patterns detected: {funding_summary['suspicious_patterns']}")

            # Risk level
            risk_assessment = funding_analysis.get("risk_assessment", {})
            summary["risk_level"] = risk_assessment.get("risk_level", "low")

            # Suspicious indicators
            if circular_patterns:
                summary["suspicious_indicators"].append(f"Circular funding patterns: {len(circular_patterns)}")

            high_risk_patterns = [p for p in funding_analysis.get("funding_patterns", []) if p.get("risk_level") in ["high", "critical"]]
            if high_risk_patterns:
                summary["suspicious_indicators"].append(f"High-risk patterns: {len(high_risk_patterns)}")

            # Network health
            if topology.get("network_stats"):
                network_stats = topology["network_stats"]
                if not network_stats.get("is_connected", True):
                    summary["network_health"] = "fragmented"
                elif network_stats.get("density", 0) > 0.1:
                    summary["network_health"] = "dense"
                elif network_stats.get("density", 0) > 0.05:
                    summary["network_health"] = "moderate"

            # Critical alerts
            if summary["risk_level"] == "critical":
                summary["critical_alerts"].append("CRITICAL: High-risk funding activity detected")

            if len(circular_patterns) > 5:
                summary["critical_alerts"].append("CRITICAL: Extensive circular funding detected")

            return summary

        except Exception as e:
            self.logger.error(f"Failed to generate funding executive summary: {e}")
            return {"key_findings": [], "risk_level": "low"}

    def _generate_funding_recommendations(self, funding_analysis: Dict, circular_patterns: List[Dict]) -> Dict[str, List[str]]:
        """Generate recommendations based on funding analysis"""
        try:
            recommendations = {
                "immediate_actions": [],
                "monitoring_actions": [],
                "investigative_actions": [],
                "preventive_measures": []
            }

            risk_assessment = funding_analysis.get("risk_assessment", {})
            risk_level = risk_assessment.get("risk_level", "low")

            # Immediate actions
            if risk_level == "critical":
                recommendations["immediate_actions"].extend([
                    "Freeze wallet activity pending investigation",
                    "Report to compliance and regulatory authorities",
                    "Enhanced monitoring of all related wallets"
                ])
            elif risk_level == "high":
                recommendations["immediate_actions"].extend([
                    "Increase monitoring frequency",
                    "Require additional verification for transactions",
                    "Review recent funding sources"
                ])

            # Monitoring actions
            if circular_patterns:
                recommendations["monitoring_actions"].append("Monitor for circular funding patterns")

            high_risk_sources = funding_analysis.get("summary", {}).get("high_risk_sources", 0)
            if high_risk_sources > 0:
                recommendations["monitoring_actions"].append("Track transactions from high-risk sources")

            # Investigative actions
            if funding_analysis.get("funding_patterns"):
                recommendations["investigative_actions"].append("Investigate identified funding patterns")

            if funding_analysis.get("original_sources"):
                recommendations["investigative_actions"].append("Analyze original funding sources")

            # Preventive measures
            recommendations["preventive_measures"].extend([
                "Implement funding source verification",
                "Add pattern detection alerts",
                "Enhance network analysis capabilities"
            ])

            return recommendations

        except Exception as e:
            self.logger.error(f"Failed to generate funding recommendations: {e}")
            return {"immediate_actions": [], "monitoring_actions": [], "investigative_actions": [], "preventive_measures": []}

    def _calculate_funding_confidence(self, funding_analysis: Dict) -> str:
        """Calculate confidence level in funding analysis"""
        try:
            # Get data completeness indicators
            summary = funding_analysis.get("summary", {})
            total_sources = summary.get("total_sources", 0)
            total_amount = summary.get("total_amount_received", 0)

            # Calculate confidence based on data volume
            if total_sources > 10 and total_amount > 1:
                return "high"
            elif total_sources > 5 and total_amount > 0.1:
                return "medium"
            else:
                return "low"

        except Exception as e:
            self.logger.error(f"Failed to calculate funding confidence: {e}")
            return "low"

    async def create_funding_visualizations(self, funding_analysis: Dict) -> Dict[str, str]:
        """Create visualizations for funding analysis"""
        try:
            visualizations = {}

            # Create funding chain visualization
            chain_chart = self._create_funding_chain_chart(funding_analysis.get("funding_chains", []))
            if chain_chart:
                visualizations["funding_chains"] = chain_chart

            # Create pattern visualization
            pattern_chart = self._create_pattern_chart(funding_analysis.get("funding_patterns", []))
            if pattern_chart:
                visualizations["patterns"] = pattern_chart

            # Create risk visualization
            risk_chart = self._create_risk_chart(funding_analysis.get("risk_assessment", {}))
            if risk_chart:
                visualizations["risk"] = risk_chart

            # Create network visualization
            network_chart = self._create_network_chart(funding_analysis.get("network_metrics", {}))
            if network_chart:
                visualizations["network"] = network_chart

            return visualizations

        except Exception as e:
            self.logger.error(f"Failed to create funding visualizations: {e}")
            return {}

    def _create_funding_chain_chart(self, funding_chains: List[Dict]) -> str:
        """Create funding chain visualization"""
        try:
            if not funding_chains:
                return ""

            # Create a Sankey-style diagram for funding chains
            fig = go.Figure()

            # Process chains for visualization
            all_sources = set()
            all_targets = set()

            for chain in funding_chains[:10]:  # Limit to top 10 chains
                if chain["path"]:
                    for tx in chain["path"]:
                        all_sources.add(tx["source"])
                        all_targets.add(tx["target"])

            # Create nodes
            nodes = list(all_sources.union(all_targets))
            node_indices = {node: i for i, node in enumerate(nodes)}

            # Create links
            links = []
            for chain in funding_chains[:10]:
                if chain["path"]:
                    for tx in chain["path"]:
                        source_idx = node_indices[tx["source"]]
                        target_idx = node_indices[tx["target"]]
                        links.append({
                            "source": source_idx,
                            "target": target_idx,
                            "value": tx["amount"],
                            "label": f"{tx['amount']:.4f} ETH"
                        })

            # Create Sankey diagram
            fig.add_trace(go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=[node[:8] + "..." for node in nodes]
                ),
                link=dict(
                    source=[link["source"] for link in links],
                    target=[link["target"] for link in links],
                    value=[link["value"] for link in links],
                    label=[link["label"] for link in links]
                )
            ))

            fig.update_layout(
                title_text="Funding Chain Analysis",
                font_size=10
            )

            # Save chart
            chart_path = self.cache_dir / "funding_chains_chart.html"
            fig.write_html(str(chart_path))

            return str(chart_path)

        except Exception as e:
            self.logger.error(f"Failed to create funding chain chart: {e}")
            return ""

    def _create_pattern_chart(self, funding_patterns: List[Dict]) -> str:
        """Create pattern analysis chart"""
        try:
            if not funding_patterns:
                return ""

            # Count patterns by type and risk level
            pattern_counts = defaultdict(lambda: defaultdict(int))
            for pattern in funding_patterns:
                pattern_type = pattern.get("pattern_type", "unknown")
                risk_level = pattern.get("risk_level", "low")
                pattern_counts[pattern_type][risk_level] += 1

            # Create grouped bar chart
            fig = go.Figure()

            risk_levels = ["low", "medium", "high", "critical"]
            colors = ["green", "yellow", "orange", "red"]

            for i, risk_level in enumerate(risk_levels):
                counts = [pattern_counts[pattern_type][risk_level] for pattern_type in pattern_counts.keys()]
                fig.add_trace(go.Bar(
                    name=risk_level.capitalize(),
                    x=list(pattern_counts.keys()),
                    y=counts,
                    marker_color=colors[i]
                ))

            fig.update_layout(
                title="Funding Pattern Analysis by Risk Level",
                xaxis_title="Pattern Type",
                yaxis_title="Count",
                barmode="group"
            )

            # Save chart
            chart_path = self.cache_dir / "funding_patterns_chart.html"
            fig.write_html(str(chart_path))

            return str(chart_path)

        except Exception as e:
            self.logger.error(f"Failed to create pattern chart: {e}")
            return ""

    def _create_risk_chart(self, risk_assessment: Dict) -> str:
        """Create risk assessment chart"""
        try:
            if not risk_assessment or "risk_factors" not in risk_assessment:
                return ""

            risk_factors = risk_assessment["risk_factors"]

            # Extract risk data
            factor_names = list(risk_factors.keys())
            risk_scores = [risk_factors[factor]["score"] * 100 for factor in factor_names]

            # Create radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=risk_scores,
                theta=factor_names,
                fill='toself',
                name='Risk Profile'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Funding Risk Assessment Profile"
            )

            # Save chart
            chart_path = self.cache_dir / "funding_risk_chart.html"
            fig.write_html(str(chart_path))

            return str(chart_path)

        except Exception as e:
            self.logger.error(f"Failed to create risk chart: {e}")
            return ""

    def _create_network_chart(self, network_metrics: Dict) -> str:
        """Create network metrics chart"""
        try:
            if not network_metrics:
                return ""

            # Extract network metrics
            metrics = {
                "Degree Centrality": network_metrics.get("degree_centrality", 0) * 100,
                "Betweenness Centrality": network_metrics.get("betweenness_centrality", 0) * 100,
                "Closeness Centrality": network_metrics.get("closeness_centrality", 0) * 100,
                "Eigenvector Centrality": network_metrics.get("eigenvector_centrality", 0) * 100,
                "PageRank Score": network_metrics.get("pagerank_score", 0) * 100,
                "Clustering Coefficient": network_metrics.get("clustering_coefficient", 0) * 100,
                "Influence Score": network_metrics.get("influence_score", 0) * 100
            }

            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=list(metrics.keys()),
                    y=list(metrics.values()),
                    marker_color='lightblue'
                )
            ])

            fig.update_layout(
                title="Network Metrics Analysis",
                xaxis_title="Metric",
                yaxis_title="Score (%)",
                yaxis=dict(range=[0, 100])
            )

            # Save chart
            chart_path = self.cache_dir / "network_metrics_chart.html"
            fig.write_html(str(chart_path))

            return str(chart_path)

        except Exception as e:
            self.logger.error(f"Failed to create network chart: {e}")
            return ""

    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        try:
            self.monitoring_active = False
            self.monitored_wallets.clear()
            self.logger.info("Stopped real-time monitoring")

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")

    async def close(self):
        """Close the funding wallet tracker"""
        try:
            self.logger.info("Closing Funding Wallet Tracker...")

            # Stop monitoring
            await self.stop_monitoring()

            # Save cached data
            await self._save_cached_data()

            # Close ChromaDB connection
            if self.chromadb:
                await self.chromadb.close()

            self.is_initialized = False
            self.logger.info("Funding Wallet Tracker closed")

        except Exception as e:
            self.logger.error(f"Failed to close funding wallet tracker: {e}")

# Singleton instance
_funding_tracker_instance = None

async def get_funding_tracker_instance() -> FundingWalletTracker:
    """Get or create funding tracker instance"""
    global _funding_tracker_instance
    if _funding_tracker_instance is None:
        _funding_tracker_instance = FundingWalletTracker()
        await _funding_tracker_instance.initialize()
    return _funding_tracker_instance

# Utility functions for common operations
async def track_funding_connection(source_wallet: str, target_wallet: str, amount: float,
                                 transaction_hash: str, block_number: int, gas_used: int, gas_price: float) -> bool:
    """Track a funding connection"""
    tracker = await get_funding_tracker_instance()
    return await tracker.add_funding_connection(source_wallet, target_wallet, amount,
                                              transaction_hash, block_number, gas_used, gas_price)

async def analyze_wallet_funding(wallet_address: str) -> Dict[str, Any]:
    """Analyze funding sources for a wallet"""
    tracker = await get_funding_tracker_instance()
    return await tracker.analyze_funding_sources(wallet_address)

async def detect_circular_funding(wallet_address: str = None) -> List[Dict]:
    """Detect circular funding patterns"""
    tracker = await get_funding_tracker_instance()
    return await tracker.detect_circular_funding_patterns(wallet_address)

async def build_funding_topology(wallet_address: str = None, depth: int = 3) -> Dict[str, Any]:
    """Build funding network topology"""
    tracker = await get_funding_tracker_instance()
    return await tracker.build_funding_topology(wallet_address, depth)

async def generate_funding_report(wallet_address: str = None, format_type: str = "json") -> Dict[str, Any]:
    """Generate funding analysis report"""
    tracker = await get_funding_tracker_instance()
    return await tracker.generate_funding_report(wallet_address, format_type)

async def start_funding_monitoring(wallet_addresses: List[str] = None) -> bool:
    """Start real-time funding monitoring"""
    tracker = await get_funding_tracker_instance()
    return await tracker.start_real_time_monitoring(wallet_addresses)

if __name__ == "__main__":
    # Example usage
    async def main():
        tracker = await get_funding_tracker_instance()

        # Analyze specific wallet
        wallet_address = config.TRADING_ACCOUNT_ADDRESS
        funding_analysis = await tracker.analyze_funding_sources(wallet_address)

        # Detect circular patterns
        circular_patterns = await tracker.detect_circular_funding_patterns(wallet_address)

        # Build topology
        topology = await tracker.build_funding_topology(wallet_address)

        # Generate report
        report = await tracker.generate_funding_report(wallet_address)

        # Create visualizations
        visualizations = await tracker.create_funding_visualizations(funding_analysis)

        print(f"Funding analysis complete for wallet: {wallet_address}")
        print(f"Risk level: {funding_analysis.get('risk_assessment', {}).get('risk_level', 'unknown')}")
        print(f"Circular patterns found: {len(circular_patterns)}")

        await tracker.close()

    asyncio.run(main())