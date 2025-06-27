#!/usr/bin/env python3
"""
Temporal Knowledge Graph with Causal Reasoning for MCPVots
Advanced temporal graph system for capturing market dynamics and causal relationships

This system provides:
- Temporal knowledge graph with time-aware relationships
- Causal reasoning and inference
- Event-driven market knowledge capture
- Temporal pattern recognition
- Predictive causal modeling
- Integration with quantum strategies and meta-learning
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple, Union, Set
import sqlite3
import random
from enum import Enum
import hashlib
import pickle
import uuid
from collections import deque, defaultdict, namedtuple
import networkx as nx
from scipy import stats
import itertools


class TemporalRelationType(Enum):
    CAUSES = "causes"
    PRECEDES = "precedes"
    CORRELATES = "correlates"
    INFLUENCES = "influences"
    TRIGGERS = "triggers"
    INHIBITS = "inhibits"
    AMPLIFIES = "amplifies"
    FOLLOWS = "follows"


class EntityType(Enum):
    MARKET_EVENT = "market_event"
    PRICE_MOVEMENT = "price_movement"
    VOLUME_SPIKE = "volume_spike"
    NEWS_EVENT = "news_event"
    TECHNICAL_INDICATOR = "technical_indicator"
    TRADING_SIGNAL = "trading_signal"
    STRATEGY_OUTPUT = "strategy_output"
    ECONOMIC_DATA = "economic_data"


@dataclass
class TemporalEntity:
    """Entity in the temporal knowledge graph"""
    entity_id: str
    entity_type: EntityType
    properties: Dict[str, Any]
    timestamp: datetime
    duration: timedelta
    confidence: float
    source: str
    metadata: Dict[str, Any]


@dataclass
class TemporalRelation:
    """Temporal relationship between entities"""
    relation_id: str
    source_entity: str
    target_entity: str
    relation_type: TemporalRelationType
    start_time: datetime
    end_time: Optional[datetime]
    strength: float
    confidence: float
    causal_lag: timedelta
    evidence: List[str]
    metadata: Dict[str, Any]


@dataclass
class CausalChain:
    """Chain of causal relationships"""
    chain_id: str
    entities: List[str]
    relations: List[str]
    total_strength: float
    chain_confidence: float
    temporal_span: timedelta
    prediction_power: float


@dataclass
class TemporalPattern:
    """Temporal pattern discovered in the graph"""
    pattern_id: str
    pattern_type: str
    entities_involved: List[str]
    temporal_signature: Dict[str, Any]
    frequency: float
    predictive_accuracy: float
    last_occurrence: datetime
    next_predicted: Optional[datetime]


CausalHypothesis = namedtuple('CausalHypothesis', ['cause', 'effect', 'mechanism', 'strength', 'evidence'])


class TemporalKnowledgeGraph:
    """Temporal knowledge graph with causal reasoning capabilities"""
    
    def __init__(self, max_entities: int = 10000, retention_days: int = 30):
        self.max_entities = max_entities
        self.retention_days = retention_days
        self.logger = self._setup_logging()
        
        # Graph storage
        self.entities = {}  # entity_id -> TemporalEntity
        self.relations = {}  # relation_id -> TemporalRelation
        self.temporal_index = defaultdict(list)  # timestamp -> [entity_ids]
        
        # NetworkX graph for analysis
        self.graph = nx.DiGraph()
        
        # Causal reasoning components
        self.causal_chains = {}  # chain_id -> CausalChain
        self.causal_hypotheses = []
        self.causal_models = {}
        
        # Pattern recognition
        self.temporal_patterns = {}  # pattern_id -> TemporalPattern
        self.pattern_frequency = defaultdict(int)
        
        # Database for persistence
        self.db_path = Path(__file__).parent / "temporal_knowledge_graph.db"
        self._init_database()
        
        # Performance metrics
        self.prediction_accuracy = 0.0
        self.causal_inference_count = 0
        
        self.logger.info("Temporal Knowledge Graph initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for temporal knowledge graph"""
        logger = logging.getLogger("TemporalKnowledgeGraph")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("temporal_knowledge_graph.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize database for temporal graph persistence"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    duration_seconds REAL NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_relations (
                    relation_id TEXT PRIMARY KEY,
                    source_entity TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    causal_lag_seconds REAL NOT NULL,
                    evidence TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS causal_chains (
                    chain_id TEXT PRIMARY KEY,
                    entities TEXT NOT NULL,
                    relations TEXT NOT NULL,
                    total_strength REAL NOT NULL,
                    chain_confidence REAL NOT NULL,
                    temporal_span_seconds REAL NOT NULL,
                    prediction_power REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    entities_involved TEXT NOT NULL,
                    temporal_signature TEXT NOT NULL,
                    frequency REAL NOT NULL,
                    predictive_accuracy REAL NOT NULL,
                    last_occurrence DATETIME NOT NULL,
                    next_predicted DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def add_entity(self, entity: TemporalEntity) -> bool:
        """Add entity to temporal knowledge graph"""
        
        try:
            # Check if entity already exists
            if entity.entity_id in self.entities:
                self.logger.warning(f"Entity {entity.entity_id} already exists")
                return False
            
            # Add to graph storage
            self.entities[entity.entity_id] = entity
            self.temporal_index[entity.timestamp].append(entity.entity_id)
            
            # Add to NetworkX graph
            self.graph.add_node(entity.entity_id, **{
                'type': entity.entity_type.value,
                'timestamp': entity.timestamp,
                'properties': entity.properties,
                'confidence': entity.confidence
            })
            
            # Store in database
            await self._store_entity(entity)
            
            # Cleanup old entities if needed
            await self._cleanup_old_entities()
            
            self.logger.debug(f"Added entity {entity.entity_id} of type {entity.entity_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add entity {entity.entity_id}: {e}")
            return False
    
    async def add_relation(self, relation: TemporalRelation) -> bool:
        """Add temporal relation to knowledge graph"""
        
        try:
            # Check if entities exist
            if relation.source_entity not in self.entities:
                self.logger.warning(f"Source entity {relation.source_entity} not found")
                return False
            
            if relation.target_entity not in self.entities:
                self.logger.warning(f"Target entity {relation.target_entity} not found")
                return False
            
            # Add relation
            self.relations[relation.relation_id] = relation
            
            # Add to NetworkX graph
            self.graph.add_edge(
                relation.source_entity,
                relation.target_entity,
                relation_type=relation.relation_type.value,
                strength=relation.strength,
                confidence=relation.confidence,
                causal_lag=relation.causal_lag.total_seconds(),
                start_time=relation.start_time,
                end_time=relation.end_time
            )
            
            # Store in database
            await self._store_relation(relation)
            
            self.logger.debug(f"Added relation {relation.relation_id}: {relation.source_entity} -> {relation.target_entity}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add relation {relation.relation_id}: {e}")
            return False
    
    async def discover_causal_relationships(self, time_window: timedelta = timedelta(hours=24)) -> List[CausalHypothesis]:
        """Discover causal relationships using temporal analysis"""
        
        self.logger.info("Discovering causal relationships...")
        
        causal_hypotheses = []
        current_time = datetime.now(timezone.utc)
        start_time = current_time - time_window
        
        # Get entities in time window
        relevant_entities = []
        for entity_id, entity in self.entities.items():
            if start_time <= entity.timestamp <= current_time:
                relevant_entities.append(entity)
        
        # Sort by timestamp
        relevant_entities.sort(key=lambda x: x.timestamp)
        
        # Analyze temporal patterns for causality
        for i in range(len(relevant_entities)):
            for j in range(i + 1, len(relevant_entities)):
                entity_a = relevant_entities[i]
                entity_b = relevant_entities[j]
                
                # Check temporal precedence
                time_diff = entity_b.timestamp - entity_a.timestamp
                if time_diff.total_seconds() <= 0:
                    continue
                
                # Analyze potential causal relationship
                causal_strength = await self._analyze_causal_strength(entity_a, entity_b, time_diff)
                
                if causal_strength > 0.5:  # Threshold for causal hypothesis
                    hypothesis = CausalHypothesis(
                        cause=entity_a.entity_id,
                        effect=entity_b.entity_id,
                        mechanism=self._infer_causal_mechanism(entity_a, entity_b),
                        strength=causal_strength,
                        evidence=[f"temporal_precedence_{time_diff.total_seconds()}s"]
                    )
                    
                    causal_hypotheses.append(hypothesis)
        
        # Validate hypotheses using statistical tests
        validated_hypotheses = await self._validate_causal_hypotheses(causal_hypotheses)
        
        # Store validated hypotheses
        self.causal_hypotheses.extend(validated_hypotheses)
        
        self.logger.info(f"Discovered {len(validated_hypotheses)} causal relationships")
        return validated_hypotheses
    
    async def _analyze_causal_strength(self, entity_a: TemporalEntity, entity_b: TemporalEntity, time_diff: timedelta) -> float:
        """Analyze causal strength between two entities"""
        
        strength = 0.0
        
        # Temporal proximity factor
        max_lag = timedelta(hours=1)
        if time_diff <= max_lag:
            temporal_factor = 1.0 - (time_diff.total_seconds() / max_lag.total_seconds())
            strength += temporal_factor * 0.3
        
        # Entity type compatibility
        causal_compatibility = self._get_causal_compatibility(entity_a.entity_type, entity_b.entity_type)
        strength += causal_compatibility * 0.4
        
        # Property correlation
        property_correlation = self._calculate_property_correlation(entity_a.properties, entity_b.properties)
        strength += property_correlation * 0.3
        
        return min(1.0, strength)
    
    def _get_causal_compatibility(self, type_a: EntityType, type_b: EntityType) -> float:
        """Get causal compatibility between entity types"""
        
        # Define causal compatibility matrix
        compatibility_matrix = {
            (EntityType.NEWS_EVENT, EntityType.PRICE_MOVEMENT): 0.9,
            (EntityType.ECONOMIC_DATA, EntityType.MARKET_EVENT): 0.8,
            (EntityType.TECHNICAL_INDICATOR, EntityType.TRADING_SIGNAL): 0.7,
            (EntityType.VOLUME_SPIKE, EntityType.PRICE_MOVEMENT): 0.6,
            (EntityType.TRADING_SIGNAL, EntityType.STRATEGY_OUTPUT): 0.8,
            (EntityType.MARKET_EVENT, EntityType.VOLUME_SPIKE): 0.5,
        }
        
        return compatibility_matrix.get((type_a, type_b), 0.2)
    
    def _calculate_property_correlation(self, props_a: Dict, props_b: Dict) -> float:
        """Calculate correlation between entity properties"""
        
        # Extract numerical properties
        numerical_a = {k: v for k, v in props_a.items() if isinstance(v, (int, float))}
        numerical_b = {k: v for k, v in props_b.items() if isinstance(v, (int, float))}
        
        if not numerical_a or not numerical_b:
            return 0.0
        
        # Calculate correlation for common properties
        common_props = set(numerical_a.keys()) & set(numerical_b.keys())
        if not common_props:
            return 0.0
        
        correlations = []
        for prop in common_props:
            # Simple correlation based on value similarity
            val_a = numerical_a[prop]
            val_b = numerical_b[prop]
            
            if val_a == 0 and val_b == 0:
                correlation = 1.0
            elif val_a == 0 or val_b == 0:
                correlation = 0.0
            else:
                correlation = 1.0 - abs(val_a - val_b) / max(abs(val_a), abs(val_b))
            
            correlations.append(correlation)
        
        return np.mean(correlations) if correlations else 0.0
    
    def _infer_causal_mechanism(self, entity_a: TemporalEntity, entity_b: TemporalEntity) -> str:
        """Infer causal mechanism between entities"""
        
        mechanisms = {
            (EntityType.NEWS_EVENT, EntityType.PRICE_MOVEMENT): "information_impact",
            (EntityType.ECONOMIC_DATA, EntityType.MARKET_EVENT): "fundamental_analysis",
            (EntityType.TECHNICAL_INDICATOR, EntityType.TRADING_SIGNAL): "technical_analysis",
            (EntityType.VOLUME_SPIKE, EntityType.PRICE_MOVEMENT): "liquidity_impact",
            (EntityType.TRADING_SIGNAL, EntityType.STRATEGY_OUTPUT): "algorithmic_execution",
            (EntityType.MARKET_EVENT, EntityType.VOLUME_SPIKE): "market_reaction",
        }
        
        return mechanisms.get((entity_a.entity_type, entity_b.entity_type), "unknown_mechanism")
    
    async def _validate_causal_hypotheses(self, hypotheses: List[CausalHypothesis]) -> List[CausalHypothesis]:
        """Validate causal hypotheses using statistical tests"""
        
        validated = []
        
        for hypothesis in hypotheses:
            # Get historical data for cause and effect
            cause_data = await self._get_entity_time_series(hypothesis.cause)
            effect_data = await self._get_entity_time_series(hypothesis.effect)
            
            if len(cause_data) < 3 or len(effect_data) < 3:
                continue  # Insufficient data
            
            # Perform Granger causality test (simplified)
            granger_p_value = self._granger_causality_test(cause_data, effect_data)
            
            # Cross-correlation analysis
            correlation, lag = self._cross_correlation_analysis(cause_data, effect_data)
            
            # Validate based on statistical significance
            if granger_p_value < 0.1 and abs(correlation) > 0.3:
                # Update hypothesis strength based on statistical evidence
                statistical_strength = (1 - granger_p_value) * abs(correlation)
                updated_strength = (hypothesis.strength + statistical_strength) / 2
                
                validated_hypothesis = CausalHypothesis(
                    cause=hypothesis.cause,
                    effect=hypothesis.effect,
                    mechanism=hypothesis.mechanism,
                    strength=updated_strength,
                    evidence=hypothesis.evidence + [f"granger_p={granger_p_value:.3f}", f"correlation={correlation:.3f}"]
                )
                
                validated.append(validated_hypothesis)
        
        return validated
    
    async def _get_entity_time_series(self, entity_id: str) -> List[float]:
        """Get time series data for entity"""
        
        # Get entity
        if entity_id not in self.entities:
            return []
        
        entity = self.entities[entity_id]
        
        # Extract numerical value for time series
        if 'value' in entity.properties:
            return [entity.properties['value']]
        elif 'price' in entity.properties:
            return [entity.properties['price']]
        elif 'volume' in entity.properties:
            return [entity.properties['volume']]
        else:
            # Use confidence as fallback
            return [entity.confidence]
    
    def _granger_causality_test(self, cause_data: List[float], effect_data: List[float]) -> float:
        """Perform simplified Granger causality test"""
        
        if len(cause_data) < 2 or len(effect_data) < 2:
            return 1.0  # No causality
        
        # Simplified test: correlation between lagged cause and current effect
        try:
            # Align data (simplified)
            min_len = min(len(cause_data), len(effect_data))
            if min_len < 2:
                return 1.0
            
            cause_lagged = cause_data[:-1][:min_len-1]
            effect_current = effect_data[1:][:min_len-1]
            
            if len(cause_lagged) == 0 or len(effect_current) == 0:
                return 1.0
            
            # Calculate correlation
            correlation = np.corrcoef(cause_lagged, effect_current)[0, 1]
            
            # Convert correlation to p-value (simplified)
            if np.isnan(correlation):
                return 1.0
            
            p_value = 1.0 - abs(correlation)
            return max(0.0, min(1.0, p_value))
            
        except Exception:
            return 1.0
    
    def _cross_correlation_analysis(self, cause_data: List[float], effect_data: List[float]) -> Tuple[float, int]:
        """Perform cross-correlation analysis"""
        
        if len(cause_data) < 2 or len(effect_data) < 2:
            return 0.0, 0
        
        try:
            # Normalize data
            cause_norm = (np.array(cause_data) - np.mean(cause_data)) / (np.std(cause_data) + 1e-8)
            effect_norm = (np.array(effect_data) - np.mean(effect_data)) / (np.std(effect_data) + 1e-8)
            
            # Calculate cross-correlation
            max_lag = min(len(cause_norm), len(effect_norm)) // 2
            correlations = []
            lags = []
            
            for lag in range(-max_lag, max_lag + 1):
                if lag == 0:
                    correlation = np.corrcoef(cause_norm, effect_norm)[0, 1]
                elif lag > 0:
                    if len(cause_norm[:-lag]) > 0 and len(effect_norm[lag:]) > 0:
                        correlation = np.corrcoef(cause_norm[:-lag], effect_norm[lag:])[0, 1]
                    else:
                        correlation = 0.0
                else:
                    if len(cause_norm[-lag:]) > 0 and len(effect_norm[:lag]) > 0:
                        correlation = np.corrcoef(cause_norm[-lag:], effect_norm[:lag])[0, 1]
                    else:
                        correlation = 0.0
                
                if not np.isnan(correlation):
                    correlations.append(correlation)
                    lags.append(lag)
            
            if not correlations:
                return 0.0, 0
            
            # Find maximum correlation and corresponding lag
            max_idx = np.argmax(np.abs(correlations))
            return correlations[max_idx], lags[max_idx]
            
        except Exception:
            return 0.0, 0
    
    async def build_causal_chains(self, max_chain_length: int = 5) -> List[CausalChain]:
        """Build causal chains from validated relationships"""
        
        self.logger.info("Building causal chains...")
        
        chains = []
        
        # Convert causal hypotheses to graph edges
        causal_graph = nx.DiGraph()
        
        for hypothesis in self.causal_hypotheses:
            if hypothesis.strength > 0.6:  # High confidence threshold
                causal_graph.add_edge(
                    hypothesis.cause, 
                    hypothesis.effect,
                    strength=hypothesis.strength,
                    mechanism=hypothesis.mechanism
                )
        
        # Find causal chains using path analysis
        for source in causal_graph.nodes():
            # Find all paths from this source
            for target in causal_graph.nodes():
                if source != target:
                    try:
                        # Find all simple paths (no cycles)
                        paths = list(nx.all_simple_paths(
                            causal_graph, source, target, cutoff=max_chain_length
                        ))
                        
                        for path in paths:
                            if len(path) >= 2:  # At least one causal link
                                chain = await self._create_causal_chain(path, causal_graph)
                                if chain:
                                    chains.append(chain)
                                    
                    except nx.NetworkXNoPath:
                        continue
        
        # Filter and rank chains
        chains.sort(key=lambda x: x.total_strength * x.chain_confidence, reverse=True)
        
        # Store top chains
        top_chains = chains[:100]  # Keep top 100 chains
        for chain in top_chains:
            self.causal_chains[chain.chain_id] = chain
            await self._store_causal_chain(chain)
        
        self.logger.info(f"Built {len(top_chains)} causal chains")
        return top_chains
    
    async def _create_causal_chain(self, path: List[str], causal_graph: nx.DiGraph) -> Optional[CausalChain]:
        """Create causal chain from path"""
        
        try:
            entities = path
            relations = []
            total_strength = 1.0
            
            # Get chain properties
            start_time = min(self.entities[entity_id].timestamp for entity_id in entities)
            end_time = max(self.entities[entity_id].timestamp for entity_id in entities)
            temporal_span = end_time - start_time
            
            # Build relations list and calculate total strength
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]
                
                if causal_graph.has_edge(source, target):
                    edge_data = causal_graph[source][target]
                    strength = edge_data.get('strength', 0.5)
                    total_strength *= strength
                    
                    relation_id = f"{source}->{target}"
                    relations.append(relation_id)
            
            # Calculate chain confidence
            chain_confidence = total_strength * (1.0 / len(entities))  # Penalize long chains
            
            # Calculate prediction power (placeholder)
            prediction_power = chain_confidence * 0.8
            
            chain_id = hashlib.sha256(f"{'->'.join(entities)}_{datetime.now()}".encode()).hexdigest()[:16]
            
            chain = CausalChain(
                chain_id=chain_id,
                entities=entities,
                relations=relations,
                total_strength=total_strength,
                chain_confidence=chain_confidence,
                temporal_span=temporal_span,
                prediction_power=prediction_power
            )
            
            return chain
            
        except Exception as e:
            self.logger.error(f"Failed to create causal chain: {e}")
            return None
    
    async def predict_future_events(self, prediction_horizon: timedelta = timedelta(hours=4)) -> List[Dict[str, Any]]:
        """Predict future events based on causal chains"""
        
        self.logger.info("Predicting future events...")
        
        predictions = []
        current_time = datetime.now(timezone.utc)
        
        # Analyze active causal chains
        for chain in self.causal_chains.values():
            if chain.prediction_power > 0.5:
                # Check if chain is currently active
                chain_activity = await self._assess_chain_activity(chain, current_time)
                
                if chain_activity > 0.3:
                    # Generate prediction
                    prediction = await self._generate_prediction_from_chain(
                        chain, current_time, prediction_horizon
                    )
                    
                    if prediction:
                        predictions.append(prediction)
        
        # Rank predictions by confidence
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.logger.info(f"Generated {len(predictions)} predictions")
        return predictions[:20]  # Return top 20 predictions
    
    async def _assess_chain_activity(self, chain: CausalChain, current_time: datetime) -> float:
        """Assess current activity level of causal chain"""
        
        activity_score = 0.0
        recent_window = timedelta(hours=2)
        
        # Check recent activity of entities in chain
        for entity_id in chain.entities:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                time_diff = current_time - entity.timestamp
                
                if time_diff <= recent_window:
                    # Recent activity boosts score
                    recency_factor = 1.0 - (time_diff.total_seconds() / recent_window.total_seconds())
                    activity_score += recency_factor * entity.confidence
        
        # Normalize by chain length
        if len(chain.entities) > 0:
            activity_score /= len(chain.entities)
        
        return min(1.0, activity_score)
    
    async def _generate_prediction_from_chain(self, chain: CausalChain, current_time: datetime, 
                                            horizon: timedelta) -> Optional[Dict[str, Any]]:
        """Generate prediction from active causal chain"""
        
        try:
            # Get the last entity in the chain (effect)
            last_entity_id = chain.entities[-1]
            
            if last_entity_id not in self.entities:
                return None
            
            last_entity = self.entities[last_entity_id]
            
            # Estimate time until effect occurs
            avg_lag = chain.temporal_span / max(1, len(chain.entities) - 1)
            predicted_time = current_time + avg_lag
            
            if predicted_time > current_time + horizon:
                return None  # Beyond prediction horizon
            
            # Generate prediction
            prediction = {
                'prediction_id': f"pred_{uuid.uuid4().hex[:8]}",
                'predicted_event': last_entity.entity_type.value,
                'predicted_time': predicted_time.isoformat(),
                'confidence': chain.prediction_power,
                'causal_chain_id': chain.chain_id,
                'reasoning': f"Causal chain with {len(chain.entities)} entities",
                'expected_properties': last_entity.properties.copy(),
                'risk_factors': self._identify_risk_factors(chain),
                'mitigation_strategies': self._suggest_mitigation_strategies(chain)
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to generate prediction: {e}")
            return None
    
    def _identify_risk_factors(self, chain: CausalChain) -> List[str]:
        """Identify risk factors for causal chain"""
        
        risk_factors = []
        
        # Chain length risk
        if len(chain.entities) > 3:
            risk_factors.append("long_causal_chain")
        
        # Low confidence risk
        if chain.chain_confidence < 0.7:
            risk_factors.append("low_confidence")
        
        # Temporal span risk
        if chain.temporal_span > timedelta(days=1):
            risk_factors.append("extended_temporal_span")
        
        return risk_factors
    
    def _suggest_mitigation_strategies(self, chain: CausalChain) -> List[str]:
        """Suggest mitigation strategies for causal chain risks"""
        
        strategies = []
        
        # General strategies
        strategies.append("monitor_early_indicators")
        strategies.append("diversify_exposure")
        
        # Chain-specific strategies
        if chain.total_strength > 0.8:
            strategies.append("prepare_for_high_probability_event")
        else:
            strategies.append("maintain_defensive_position")
        
        return strategies
    
    async def discover_temporal_patterns(self) -> List[TemporalPattern]:
        """Discover recurring temporal patterns in the graph"""
        
        self.logger.info("Discovering temporal patterns...")
        
        patterns = []
        
        # Group entities by type and analyze temporal patterns
        entity_groups = defaultdict(list)
        for entity in self.entities.values():
            entity_groups[entity.entity_type].append(entity)
        
        # Analyze each entity type
        for entity_type, entities in entity_groups.items():
            if len(entities) < 5:  # Need minimum entities for pattern analysis
                continue
            
            # Sort by timestamp
            entities.sort(key=lambda x: x.timestamp)
            
            # Analyze temporal intervals
            intervals = []
            for i in range(1, len(entities)):
                interval = entities[i].timestamp - entities[i-1].timestamp
                intervals.append(interval.total_seconds())
            
            if len(intervals) >= 3:
                # Look for periodic patterns
                pattern = await self._analyze_periodicity(intervals, entity_type, entities)
                if pattern:
                    patterns.append(pattern)
        
        # Store patterns
        for pattern in patterns:
            self.temporal_patterns[pattern.pattern_id] = pattern
            await self._store_temporal_pattern(pattern)
        
        self.logger.info(f"Discovered {len(patterns)} temporal patterns")
        return patterns
    
    async def _analyze_periodicity(self, intervals: List[float], entity_type: EntityType, 
                                 entities: List[TemporalEntity]) -> Optional[TemporalPattern]:
        """Analyze periodicity in temporal intervals"""
        
        try:
            # Calculate statistics
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            # Check for periodicity (low standard deviation relative to mean)
            if std_interval / mean_interval < 0.5:  # Relatively stable intervals
                # Calculate frequency
                frequency = 1.0 / mean_interval if mean_interval > 0 else 0.0
                
                # Estimate predictive accuracy (simplified)
                consistency = 1.0 - (std_interval / mean_interval)
                predictive_accuracy = min(0.9, consistency)
                
                # Calculate next predicted occurrence
                last_occurrence = entities[-1].timestamp
                next_predicted = last_occurrence + timedelta(seconds=mean_interval)
                
                pattern_id = f"pattern_{entity_type.value}_{hashlib.sha256(str(intervals).encode()).hexdigest()[:8]}"
                
                pattern = TemporalPattern(
                    pattern_id=pattern_id,
                    pattern_type=f"periodic_{entity_type.value}",
                    entities_involved=[entity.entity_id for entity in entities],
                    temporal_signature={
                        'mean_interval_seconds': mean_interval,
                        'std_interval_seconds': std_interval,
                        'frequency_hz': frequency,
                        'consistency_score': consistency
                    },
                    frequency=frequency,
                    predictive_accuracy=predictive_accuracy,
                    last_occurrence=last_occurrence,
                    next_predicted=next_predicted
                )
                
                return pattern
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to analyze periodicity: {e}")
            return None
    
    async def _store_entity(self, entity: TemporalEntity):
        """Store entity in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO temporal_entities 
                    (entity_id, entity_type, properties, timestamp, duration_seconds, 
                     confidence, source, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.entity_id,
                    entity.entity_type.value,
                    json.dumps(entity.properties),
                    entity.timestamp.isoformat(),
                    entity.duration.total_seconds(),
                    entity.confidence,
                    entity.source,
                    json.dumps(entity.metadata)
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store entity: {e}")
    
    async def _store_relation(self, relation: TemporalRelation):
        """Store relation in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO temporal_relations 
                    (relation_id, source_entity, target_entity, relation_type, start_time, 
                     end_time, strength, confidence, causal_lag_seconds, evidence, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    relation.relation_id,
                    relation.source_entity,
                    relation.target_entity,
                    relation.relation_type.value,
                    relation.start_time.isoformat(),
                    relation.end_time.isoformat() if relation.end_time else None,
                    relation.strength,
                    relation.confidence,
                    relation.causal_lag.total_seconds(),
                    json.dumps(relation.evidence),
                    json.dumps(relation.metadata)
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store relation: {e}")
    
    async def _store_causal_chain(self, chain: CausalChain):
        """Store causal chain in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO causal_chains 
                    (chain_id, entities, relations, total_strength, chain_confidence, 
                     temporal_span_seconds, prediction_power)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chain.chain_id,
                    json.dumps(chain.entities),
                    json.dumps(chain.relations),
                    chain.total_strength,
                    chain.chain_confidence,
                    chain.temporal_span.total_seconds(),
                    chain.prediction_power
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store causal chain: {e}")
    
    async def _store_temporal_pattern(self, pattern: TemporalPattern):
        """Store temporal pattern in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO temporal_patterns 
                    (pattern_id, pattern_type, entities_involved, temporal_signature, 
                     frequency, predictive_accuracy, last_occurrence, next_predicted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    json.dumps(pattern.entities_involved),
                    json.dumps(pattern.temporal_signature),
                    pattern.frequency,
                    pattern.predictive_accuracy,
                    pattern.last_occurrence.isoformat(),
                    pattern.next_predicted.isoformat() if pattern.next_predicted else None
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store temporal pattern: {e}")
    
    async def _cleanup_old_entities(self):
        """Clean up old entities beyond retention period"""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        
        entities_to_remove = []
        for entity_id, entity in self.entities.items():
            if entity.timestamp < cutoff_time:
                entities_to_remove.append(entity_id)
        
        # Remove entities
        for entity_id in entities_to_remove:
            del self.entities[entity_id]
            if self.graph.has_node(entity_id):
                self.graph.remove_node(entity_id)
        
        # Clean up temporal index
        for timestamp in list(self.temporal_index.keys()):
            if timestamp < cutoff_time:
                del self.temporal_index[timestamp]
        
        if entities_to_remove:
            self.logger.info(f"Cleaned up {len(entities_to_remove)} old entities")
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics"""
        
        try:
            stats = {
                'total_entities': len(self.entities),
                'total_relations': len(self.relations),
                'causal_chains': len(self.causal_chains),
                'temporal_patterns': len(self.temporal_patterns),
                'graph_density': nx.density(self.graph) if self.graph.nodes() else 0,
                'strongly_connected_components': len(list(nx.strongly_connected_components(self.graph))),
                'entity_types': defaultdict(int),
                'relation_types': defaultdict(int),
                'prediction_accuracy': self.prediction_accuracy,
                'causal_inference_count': self.causal_inference_count
            }
            
            # Count entity types
            for entity in self.entities.values():
                stats['entity_types'][entity.entity_type.value] += 1
            
            # Count relation types
            for relation in self.relations.values():
                stats['relation_types'][relation.relation_type.value] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get graph statistics: {e}")
            return {'error': str(e)}


# Demo function for testing
async def demo_temporal_knowledge_graph():
    """Demo the temporal knowledge graph system"""
    
    print("Demo: Temporal Knowledge Graph with Causal Reasoning")
    print("=" * 60)
    
    # Initialize temporal knowledge graph
    tkg = TemporalKnowledgeGraph(max_entities=1000, retention_days=7)
    
    # Generate synthetic market entities
    print("Creating synthetic market entities...")
    
    current_time = datetime.now(timezone.utc)
    entities = []
    
    for i in range(20):
        timestamp = current_time - timedelta(hours=20-i)
        
        if i % 4 == 0:
            # News event
            entity = TemporalEntity(
                entity_id=f"news_{i}",
                entity_type=EntityType.NEWS_EVENT,
                properties={
                    'sentiment': random.uniform(-1, 1),
                    'impact_score': random.uniform(0, 10),
                    'topic': random.choice(['regulation', 'adoption', 'technology'])
                },
                timestamp=timestamp,
                duration=timedelta(minutes=30),
                confidence=random.uniform(0.7, 0.95),
                source="news_feed",
                metadata={'category': 'market_news'}
            )
        elif i % 4 == 1:
            # Price movement
            entity = TemporalEntity(
                entity_id=f"price_{i}",
                entity_type=EntityType.PRICE_MOVEMENT,
                properties={
                    'price_change': random.uniform(-0.1, 0.1),
                    'volume': random.uniform(1000000, 10000000),
                    'volatility': random.uniform(0.1, 0.8)
                },
                timestamp=timestamp,
                duration=timedelta(minutes=5),
                confidence=0.99,
                source="price_feed",
                metadata={'symbol': 'SOL/USDT'}
            )
        elif i % 4 == 2:
            # Technical indicator
            entity = TemporalEntity(
                entity_id=f"indicator_{i}",
                entity_type=EntityType.TECHNICAL_INDICATOR,
                properties={
                    'rsi': random.uniform(20, 80),
                    'macd': random.uniform(-1, 1),
                    'signal_strength': random.uniform(0, 1)
                },
                timestamp=timestamp,
                duration=timedelta(minutes=1),
                confidence=random.uniform(0.6, 0.9),
                source="technical_analysis",
                metadata={'timeframe': '5m'}
            )
        else:
            # Trading signal
            entity = TemporalEntity(
                entity_id=f"signal_{i}",
                entity_type=EntityType.TRADING_SIGNAL,
                properties={
                    'action': random.choice(['buy', 'sell', 'hold']),
                    'strength': random.uniform(0, 1),
                    'risk_level': random.uniform(0, 1)
                },
                timestamp=timestamp,
                duration=timedelta(minutes=15),
                confidence=random.uniform(0.5, 0.8),
                source="trading_algorithm",
                metadata={'strategy': 'momentum'}
            )
        
        entities.append(entity)
    
    # Add entities to graph
    for entity in entities:
        await tkg.add_entity(entity)
    
    print(f"✅ Added {len(entities)} entities to temporal knowledge graph")
    
    # Discover causal relationships
    print(f"\nDiscovering causal relationships...")
    causal_hypotheses = await tkg.discover_causal_relationships(timedelta(hours=24))
    
    print(f"Discovered Causal Relationships:")
    for i, hypothesis in enumerate(causal_hypotheses[:5], 1):
        print(f"   {i}. {hypothesis.cause} -> {hypothesis.effect}")
        print(f"      Mechanism: {hypothesis.mechanism}")
        print(f"      Strength: {hypothesis.strength:.3f}")
        print(f"      Evidence: {', '.join(hypothesis.evidence)}")
    
    # Build causal chains
    print(f"\nBuilding causal chains...")
    causal_chains = await tkg.build_causal_chains(max_chain_length=4)
    
    print(f"Top Causal Chains:")
    for i, chain in enumerate(causal_chains[:3], 1):
        print(f"   {i}. Chain {chain.chain_id}")
        print(f"      Path: {' -> '.join(chain.entities)}")
        print(f"      Strength: {chain.total_strength:.3f}")
        print(f"      Confidence: {chain.chain_confidence:.3f}")
        print(f"      Temporal Span: {chain.temporal_span}")
    
    # Predict future events
    print(f"\nPredicting future events...")
    predictions = await tkg.predict_future_events(timedelta(hours=4))
    
    print(f"Future Event Predictions:")
    for i, prediction in enumerate(predictions[:3], 1):
        print(f"   {i}. Event: {prediction['predicted_event']}")
        print(f"      Time: {prediction['predicted_time']}")
        print(f"      Confidence: {prediction['confidence']:.3f}")
        print(f"      Reasoning: {prediction['reasoning']}")
        if prediction['risk_factors']:
            print(f"      Risk Factors: {', '.join(prediction['risk_factors'])}")
    
    # Discover temporal patterns
    print(f"\nDiscovering temporal patterns...")
    temporal_patterns = await tkg.discover_temporal_patterns()
    
    print(f"Temporal Patterns:")
    for i, pattern in enumerate(temporal_patterns[:3], 1):
        print(f"   {i}. Pattern: {pattern.pattern_type}")
        print(f"      Entities: {len(pattern.entities_involved)}")
        print(f"      Frequency: {pattern.frequency:.6f} Hz")
        print(f"      Accuracy: {pattern.predictive_accuracy:.3f}")
        if pattern.next_predicted:
            print(f"      Next Predicted: {pattern.next_predicted}")
    
    # Get graph statistics
    stats = await tkg.get_graph_statistics()
    
    print(f"\nGraph Statistics:")
    print(f"   Total Entities: {stats['total_entities']}")
    print(f"   Total Relations: {stats['total_relations']}")
    print(f"   Causal Chains: {stats['causal_chains']}")
    print(f"   Temporal Patterns: {stats['temporal_patterns']}")
    print(f"   Graph Density: {stats['graph_density']:.4f}")
    print(f"   Connected Components: {stats['strongly_connected_components']}")
    
    print(f"\n   Entity Types:")
    for entity_type, count in stats['entity_types'].items():
        print(f"     {entity_type}: {count}")
    
    if stats['relation_types']:
        print(f"\n   Relation Types:")
        for relation_type, count in stats['relation_types'].items():
            print(f"     {relation_type}: {count}")
    
    print(f"\nTemporal Knowledge Graph Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_temporal_knowledge_graph())
