#!/usr/bin/env python3
"""
Distributed Trading Swarm for MCPVots
Advanced swarm intelligence system for coordinated trading across multiple agents

This system provides:
- Swarm intelligence with multiple trading agents
- Emergent collective behavior optimization
- Decentralized decision making and coordination
- Load balancing and fault tolerance
- Cross-agent learning and knowledge sharing
- Real-time swarm performance monitoring
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
from collections import deque, defaultdict
import aiohttp
import zmq
import zmq.asyncio
import threading
import time


class AgentRole(Enum):
    EXPLORER = "explorer"      # Explores new strategies
    EXPLOITER = "exploiter"    # Exploits known good strategies
    COORDINATOR = "coordinator" # Coordinates swarm behavior
    MONITOR = "monitor"        # Monitors market conditions
    LEARNER = "learner"        # Learns from other agents


class SwarmState(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    COORDINATING = "coordinating"
    CONVERGING = "converging"
    ADAPTING = "adapting"
    EMERGENCY = "emergency"


@dataclass
class AgentStatus:
    """Status information for a trading agent"""
    agent_id: str
    role: AgentRole
    performance_score: float
    active_trades: int
    profit_loss: float
    last_heartbeat: datetime
    current_strategy: str
    coordination_weight: float
    learning_rate: float
    exploration_factor: float


@dataclass
class SwarmCoordination:
    """Coordination message between agents"""
    sender_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    requires_response: bool = False


@dataclass
class SwarmPerformance:
    """Overall swarm performance metrics"""
    total_agents: int
    active_agents: int
    total_profit_loss: float
    avg_performance: float
    best_agent_id: str
    worst_agent_id: str
    coordination_efficiency: float
    swarm_coherence: float
    adaptation_speed: float
    fault_tolerance: float


class TradingAgent:
    """Individual trading agent in the swarm"""
    
    def __init__(self, agent_id: str, role: AgentRole, coordinator_port: int = 5555):
        self.agent_id = agent_id
        self.role = role
        self.coordinator_port = coordinator_port
        self.logger = self._setup_logging()
        
        # Agent state
        self.performance_score = 0.0
        self.active_trades = 0
        self.profit_loss = 0.0
        self.current_strategy = "default"
        self.coordination_weight = self._get_initial_coordination_weight()
        self.learning_rate = 0.01
        self.exploration_factor = self._get_initial_exploration_factor()
        
        # Communication setup
        self.context = zmq.asyncio.Context()
        self.coordinator_socket = None
        self.subscriber_socket = None
        
        # Knowledge and memory
        self.shared_knowledge = {}
        self.local_knowledge = {}
        self.message_history = deque(maxlen=1000)
        
        # Performance tracking
        self.performance_history = deque(maxlen=100)
        self.trade_history = []
        
        # Coordination state
        self.last_coordination = datetime.now(timezone.utc)
        self.pending_coordinations = {}
        
        self.logger.info(f"🤖 Agent {agent_id} ({role.value}) initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for trading agent"""
        logger = logging.getLogger(f"TradingAgent_{self.agent_id}")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(f"agent_{self.agent_id}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _get_initial_coordination_weight(self) -> float:
        """Get initial coordination weight based on role"""
        role_weights = {
            AgentRole.EXPLORER: 0.3,
            AgentRole.EXPLOITER: 0.7,
            AgentRole.COORDINATOR: 1.0,
            AgentRole.MONITOR: 0.5,
            AgentRole.LEARNER: 0.6
        }
        return role_weights.get(self.role, 0.5)
    
    def _get_initial_exploration_factor(self) -> float:
        """Get initial exploration factor based on role"""
        role_exploration = {
            AgentRole.EXPLORER: 0.8,
            AgentRole.EXPLOITER: 0.2,
            AgentRole.COORDINATOR: 0.4,
            AgentRole.MONITOR: 0.1,
            AgentRole.LEARNER: 0.5
        }
        return role_exploration.get(self.role, 0.4)
    
    async def connect_to_swarm(self, coordinator_address: str = "tcp://localhost"):
        """Connect to swarm coordinator"""
        
        try:
            # Connect to coordinator
            self.coordinator_socket = self.context.socket(zmq.REQ)
            self.coordinator_socket.connect(f"{coordinator_address}:{self.coordinator_port}")
            
            # Subscribe to broadcasts
            self.subscriber_socket = self.context.socket(zmq.SUB)
            self.subscriber_socket.connect(f"{coordinator_address}:{self.coordinator_port + 1}")
            self.subscriber_socket.setsockopt(zmq.SUBSCRIBE, b"")  # Subscribe to all messages
            
            # Register with coordinator
            registration = {
                "action": "register",
                "agent_id": self.agent_id,
                "role": self.role.value,
                "capabilities": self._get_capabilities()
            }
            
            await self.coordinator_socket.send_json(registration)
            response = await self.coordinator_socket.recv_json()
            
            if response.get("status") == "success":
                self.logger.info(f"✅ Connected to swarm coordinator")
                return True
            else:
                self.logger.error(f"❌ Failed to register with coordinator: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to swarm: {e}")
            return False
    
    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities based on role"""
        base_capabilities = ["trading", "analysis", "communication"]
        
        role_capabilities = {
            AgentRole.EXPLORER: ["strategy_discovery", "risk_taking", "innovation"],
            AgentRole.EXPLOITER: ["strategy_optimization", "profit_maximization", "efficiency"],
            AgentRole.COORDINATOR: ["swarm_coordination", "consensus_building", "conflict_resolution"],
            AgentRole.MONITOR: ["market_monitoring", "anomaly_detection", "early_warning"],
            AgentRole.LEARNER: ["pattern_learning", "adaptation", "knowledge_synthesis"]
        }
        
        return base_capabilities + role_capabilities.get(self.role, [])
    
    async def execute_trading_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Execute role-specific trading logic"""
        
        if self.role == AgentRole.EXPLORER:
            return await self._explorer_logic(market_data)
        elif self.role == AgentRole.EXPLOITER:
            return await self._exploiter_logic(market_data)
        elif self.role == AgentRole.COORDINATOR:
            return await self._coordinator_logic(market_data)
        elif self.role == AgentRole.MONITOR:
            return await self._monitor_logic(market_data)
        elif self.role == AgentRole.LEARNER:
            return await self._learner_logic(market_data)
        else:
            return await self._default_logic(market_data)
    
    async def _explorer_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Explorer agent trading logic - focuses on discovering new strategies"""
        
        # High exploration, experimental strategies
        volatility = market_data.get('volatility', 0.5)
        
        # Explore unusual market conditions
        if volatility > 0.8:
            # High risk, high reward exploration
            action = "buy" if random.random() > 0.6 else "sell"
            confidence = 0.4 + random.random() * 0.3
            size = 0.05 + random.random() * 0.10  # 5-15% position
        elif volatility < 0.2:
            # Low volatility exploration for breakouts
            action = "buy" if random.random() > 0.5 else "hold"
            confidence = 0.3 + random.random() * 0.4
            size = 0.02 + random.random() * 0.05  # 2-7% position
        else:
            # Medium volatility - experimental strategies
            action = random.choice(["buy", "sell", "hold"])
            confidence = 0.2 + random.random() * 0.5
            size = 0.03 + random.random() * 0.08  # 3-11% position
        
        return {
            "action": action,
            "confidence": confidence,
            "position_size": size,
            "strategy": "exploration",
            "reasoning": f"Exploring {volatility:.2f} volatility conditions",
            "innovation_factor": 0.8
        }
    
    async def _exploiter_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Exploiter agent trading logic - focuses on proven strategies"""
        
        # Low exploration, optimize known strategies
        trend = market_data.get('trend_strength', 0.0)
        
        # Follow proven trend-following strategies
        if abs(trend) > 0.6:
            action = "buy" if trend > 0 else "sell"
            confidence = 0.7 + abs(trend) * 0.2
            size = 0.08 + abs(trend) * 0.12  # 8-20% position
        elif abs(trend) < 0.2:
            # Mean reversion strategy
            recent_change = market_data.get('recent_change', 0.0)
            if recent_change > 0.05:
                action = "sell"
                confidence = 0.6
            elif recent_change < -0.05:
                action = "buy"
                confidence = 0.6
            else:
                action = "hold"
                confidence = 0.8
            size = 0.05 + abs(recent_change) * 20  # 5-15% position
        else:
            action = "hold"
            confidence = 0.9
            size = 0.0
        
        return {
            "action": action,
            "confidence": confidence,
            "position_size": size,
            "strategy": "exploitation",
            "reasoning": f"Exploiting {trend:.2f} trend strength",
            "optimization_factor": 0.9
        }
    
    async def _coordinator_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Coordinator agent logic - balances and coordinates other agents"""
        
        # Aggregate inputs from other agents
        swarm_sentiment = await self._get_swarm_sentiment()
        
        # Calculate consensus
        buy_weight = swarm_sentiment.get('buy_signals', 0)
        sell_weight = swarm_sentiment.get('sell_signals', 0)
        hold_weight = swarm_sentiment.get('hold_signals', 0)
        
        total_weight = buy_weight + sell_weight + hold_weight
        
        if total_weight > 0:
            buy_prob = buy_weight / total_weight
            sell_prob = sell_weight / total_weight
            hold_prob = hold_weight / total_weight
            
            # Consensus-based decision
            if buy_prob > 0.6:
                action = "buy"
                confidence = buy_prob
            elif sell_prob > 0.6:
                action = "sell"
                confidence = sell_prob
            else:
                action = "hold"
                confidence = hold_prob
                
            size = 0.05 + confidence * 0.10  # 5-15% based on confidence
        else:
            action = "hold"
            confidence = 0.5
            size = 0.0
        
        return {
            "action": action,
            "confidence": confidence,
            "position_size": size,
            "strategy": "coordination",
            "reasoning": f"Consensus: buy={buy_prob:.2f}, sell={sell_prob:.2f}, hold={hold_prob:.2f}",
            "coordination_factor": 1.0
        }
    
    async def _monitor_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Monitor agent logic - focuses on risk monitoring and alerts"""
        
        # Monitor for anomalies and risks
        volatility = market_data.get('volatility', 0.5)
        volume = market_data.get('volume', 1.0)
        
        # Risk assessment
        risk_factors = []
        
        if volatility > 0.9:
            risk_factors.append("extreme_volatility")
        if volume > 3.0:
            risk_factors.append("unusual_volume")
        if market_data.get('spread', 0.01) > 0.05:
            risk_factors.append("wide_spread")
        
        # Conservative trading based on risk assessment
        if len(risk_factors) >= 2:
            action = "hold"  # High risk - avoid trading
            confidence = 0.9
            size = 0.0
        elif len(risk_factors) == 1:
            action = "hold"  # Medium risk - small position
            confidence = 0.7
            size = 0.02
        else:
            # Normal conditions - moderate trading
            action = "buy" if random.random() > 0.5 else "hold"
            confidence = 0.6
            size = 0.05
        
        return {
            "action": action,
            "confidence": confidence,
            "position_size": size,
            "strategy": "monitoring",
            "reasoning": f"Risk factors: {risk_factors}",
            "risk_assessment": len(risk_factors)
        }
    
    async def _learner_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Learner agent logic - adapts based on other agents' performance"""
        
        # Learn from best performing agents
        best_performers = await self._get_best_performers()
        
        if best_performers:
            # Mimic best performing strategy
            best_strategy = best_performers[0].get('last_action', {})
            
            # Add some variation to avoid exact copying
            action = best_strategy.get('action', 'hold')
            confidence = best_strategy.get('confidence', 0.5) * (0.8 + random.random() * 0.4)
            size = best_strategy.get('position_size', 0.05) * (0.7 + random.random() * 0.6)
            
            reasoning = f"Learning from agent {best_performers[0].get('agent_id', 'unknown')}"
        else:
            # No data to learn from - use conservative approach
            action = "hold"
            confidence = 0.5
            size = 0.03
            reasoning = "No learning data available"
        
        return {
            "action": action,
            "confidence": confidence,
            "position_size": size,
            "strategy": "learning",
            "reasoning": reasoning,
            "learning_factor": 0.7
        }
    
    async def _default_logic(self, market_data: Dict) -> Dict[str, Any]:
        """Default trading logic"""
        
        return {
            "action": "hold",
            "confidence": 0.5,
            "position_size": 0.0,
            "strategy": "default",
            "reasoning": "Default conservative approach"
        }
    
    async def _get_swarm_sentiment(self) -> Dict[str, float]:
        """Get aggregated sentiment from swarm"""
        
        # Request sentiment data from coordinator
        try:
            request = {
                "action": "get_sentiment",
                "agent_id": self.agent_id
            }
            
            await self.coordinator_socket.send_json(request)
            response = await self.coordinator_socket.recv_json()
            
            return response.get('sentiment', {'buy_signals': 0, 'sell_signals': 0, 'hold_signals': 0})
            
        except Exception as e:
            self.logger.error(f"Failed to get swarm sentiment: {e}")
            return {'buy_signals': 0, 'sell_signals': 0, 'hold_signals': 0}
    
    async def _get_best_performers(self) -> List[Dict]:
        """Get best performing agents from swarm"""
        
        try:
            request = {
                "action": "get_best_performers",
                "agent_id": self.agent_id,
                "limit": 3
            }
            
            await self.coordinator_socket.send_json(request)
            response = await self.coordinator_socket.recv_json()
            
            return response.get('performers', [])
            
        except Exception as e:
            self.logger.error(f"Failed to get best performers: {e}")
            return []
    
    async def send_heartbeat(self):
        """Send heartbeat to coordinator"""
        
        try:
            heartbeat = {
                "action": "heartbeat",
                "agent_id": self.agent_id,
                "status": self.get_status_dict(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.coordinator_socket.send_json(heartbeat)
            response = await self.coordinator_socket.recv_json()
            
            if response.get("status") != "acknowledged":
                self.logger.warning(f"Heartbeat not acknowledged: {response}")
                
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")
    
    def get_status_dict(self) -> Dict[str, Any]:
        """Get current agent status as dictionary"""
        
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "performance_score": self.performance_score,
            "active_trades": self.active_trades,
            "profit_loss": self.profit_loss,
            "current_strategy": self.current_strategy,
            "coordination_weight": self.coordination_weight,
            "learning_rate": self.learning_rate,
            "exploration_factor": self.exploration_factor,
            "last_heartbeat": datetime.now(timezone.utc).isoformat()
        }
    
    def update_performance(self, trade_result: Dict):
        """Update agent performance based on trade result"""
        
        profit_loss = trade_result.get('profit_loss', 0.0)
        self.profit_loss += profit_loss
        
        # Update performance score (exponential moving average)
        if profit_loss > 0:
            self.performance_score = 0.9 * self.performance_score + 0.1 * 1.0
        else:
            self.performance_score = 0.9 * self.performance_score + 0.1 * 0.0
        
        # Track in history
        self.performance_history.append({
            'timestamp': datetime.now(timezone.utc),
            'profit_loss': profit_loss,
            'performance_score': self.performance_score
        })
        
        self.trade_history.append(trade_result)


class SwarmCoordinator:
    """Coordinator for the distributed trading swarm"""
    
    def __init__(self, port: int = 5555):
        self.port = port
        self.logger = self._setup_logging()
        
        # Swarm state
        self.agents = {}  # agent_id -> AgentStatus
        self.swarm_state = SwarmState.INITIALIZING
        self.coordination_messages = deque(maxlen=1000)
        
        # Communication setup
        self.context = zmq.asyncio.Context()
        self.response_socket = None
        self.publisher_socket = None
        
        # Performance tracking
        self.swarm_performance_history = deque(maxlen=100)
        self.coordination_efficiency = 0.0
        
        # Database for tracking
        self.db_path = Path(__file__).parent / "distributed_swarm.db"
        self._init_database()
        
        self.logger.info("🎛️ Swarm Coordinator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for swarm coordinator"""
        logger = logging.getLogger("SwarmCoordinator")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("swarm_coordinator.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize database for swarm tracking"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS swarm_sessions (
                    session_id TEXT PRIMARY KEY,
                    total_agents INTEGER NOT NULL,
                    active_agents INTEGER NOT NULL,
                    total_profit_loss REAL NOT NULL,
                    avg_performance REAL NOT NULL,
                    coordination_efficiency REAL NOT NULL,
                    swarm_coherence REAL NOT NULL,
                    session_duration REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    record_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    profit_loss REAL NOT NULL,
                    active_trades INTEGER NOT NULL,
                    coordination_weight REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coordination_events (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    participants TEXT NOT NULL,
                    coordination_outcome TEXT NOT NULL,
                    efficiency_score REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def start_coordinator(self):
        """Start the swarm coordinator"""
        
        try:
            # Setup response socket for agent requests
            self.response_socket = self.context.socket(zmq.REP)
            self.response_socket.bind(f"tcp://*:{self.port}")
            
            # Setup publisher socket for broadcasts
            self.publisher_socket = self.context.socket(zmq.PUB)
            self.publisher_socket.bind(f"tcp://*:{self.port + 1}")
            
            self.swarm_state = SwarmState.ACTIVE
            self.logger.info(f"🚀 Swarm coordinator started on port {self.port}")
            
            # Start coordination loop
            asyncio.create_task(self._coordination_loop())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start coordinator: {e}")
            return False
    
    async def _coordination_loop(self):
        """Main coordination loop"""
        
        while self.swarm_state != SwarmState.EMERGENCY:
            try:
                # Handle agent requests
                if self.response_socket:
                    try:
                        # Non-blocking receive
                        message = await asyncio.wait_for(
                            self.response_socket.recv_json(zmq.NOBLOCK), timeout=0.1
                        )
                        response = await self._handle_agent_request(message)
                        await self.response_socket.send_json(response)
                    except (zmq.Again, asyncio.TimeoutError):
                        # No message received
                        pass
                
                # Periodic coordination tasks
                await self._perform_periodic_coordination()
                
                # Brief sleep to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _handle_agent_request(self, message: Dict) -> Dict:
        """Handle requests from agents"""
        
        action = message.get("action")
        agent_id = message.get("agent_id")
        
        if action == "register":
            return await self._handle_registration(message)
        elif action == "heartbeat":
            return await self._handle_heartbeat(message)
        elif action == "get_sentiment":
            return await self._handle_sentiment_request(message)
        elif action == "get_best_performers":
            return await self._handle_performance_request(message)
        elif action == "coordinate":
            return await self._handle_coordination_request(message)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    async def _handle_registration(self, message: Dict) -> Dict:
        """Handle agent registration"""
        
        agent_id = message.get("agent_id")
        role = message.get("role")
        capabilities = message.get("capabilities", [])
        
        if not agent_id or not role:
            return {"status": "error", "message": "Missing agent_id or role"}
        
        # Create agent status
        agent_status = AgentStatus(
            agent_id=agent_id,
            role=AgentRole(role),
            performance_score=0.0,
            active_trades=0,
            profit_loss=0.0,
            last_heartbeat=datetime.now(timezone.utc),
            current_strategy="default",
            coordination_weight=0.5,
            learning_rate=0.01,
            exploration_factor=0.5
        )
        
        self.agents[agent_id] = agent_status
        
        self.logger.info(f"📋 Registered agent {agent_id} with role {role}")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} registered successfully",
            "swarm_size": len(self.agents)
        }
    
    async def _handle_heartbeat(self, message: Dict) -> Dict:
        """Handle agent heartbeat"""
        
        agent_id = message.get("agent_id")
        status_data = message.get("status", {})
        
        if agent_id in self.agents:
            # Update agent status
            agent_status = self.agents[agent_id]
            agent_status.performance_score = status_data.get("performance_score", agent_status.performance_score)
            agent_status.active_trades = status_data.get("active_trades", agent_status.active_trades)
            agent_status.profit_loss = status_data.get("profit_loss", agent_status.profit_loss)
            agent_status.current_strategy = status_data.get("current_strategy", agent_status.current_strategy)
            agent_status.last_heartbeat = datetime.now(timezone.utc)
            
            return {"status": "acknowledged"}
        else:
            return {"status": "error", "message": "Agent not registered"}
    
    async def _handle_sentiment_request(self, message: Dict) -> Dict:
        """Handle swarm sentiment request"""
        
        # Aggregate sentiment from recent agent actions
        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        
        for agent_id, agent_status in self.agents.items():
            if agent_status.current_strategy in ["buy", "long"]:
                buy_signals += agent_status.coordination_weight
            elif agent_status.current_strategy in ["sell", "short"]:
                sell_signals += agent_status.coordination_weight
            else:
                hold_signals += agent_status.coordination_weight
        
        return {
            "status": "success",
            "sentiment": {
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "hold_signals": hold_signals
            }
        }
    
    async def _handle_performance_request(self, message: Dict) -> Dict:
        """Handle best performers request"""
        
        limit = message.get("limit", 5)
        
        # Sort agents by performance
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: x[1].performance_score,
            reverse=True
        )[:limit]
        
        performers = []
        for agent_id, agent_status in sorted_agents:
            performers.append({
                "agent_id": agent_id,
                "role": agent_status.role.value,
                "performance_score": agent_status.performance_score,
                "profit_loss": agent_status.profit_loss,
                "last_action": {"action": agent_status.current_strategy}
            })
        
        return {
            "status": "success",
            "performers": performers
        }
    
    async def _handle_coordination_request(self, message: Dict) -> Dict:
        """Handle coordination request between agents"""
        
        # Implement coordination logic
        coordination_type = message.get("coordination_type", "consensus")
        participants = message.get("participants", [])
        
        if coordination_type == "consensus":
            # Build consensus among specified agents
            consensus_result = await self._build_consensus(participants)
            return {"status": "success", "consensus": consensus_result}
        elif coordination_type == "load_balance":
            # Redistribute load among agents
            balance_result = await self._rebalance_load(participants)
            return {"status": "success", "rebalancing": balance_result}
        else:
            return {"status": "error", "message": f"Unknown coordination type: {coordination_type}"}
    
    async def _perform_periodic_coordination(self):
        """Perform periodic coordination tasks"""
        
        # Update swarm state
        await self._update_swarm_state()
        
        # Check for inactive agents
        await self._check_agent_health()
        
        # Broadcast swarm status
        await self._broadcast_swarm_status()
        
        # Update performance metrics
        await self._update_performance_metrics()
    
    async def _update_swarm_state(self):
        """Update overall swarm state"""
        
        active_agents = sum(1 for agent in self.agents.values() 
                          if (datetime.now(timezone.utc) - agent.last_heartbeat).seconds < 30)
        
        if active_agents == 0:
            self.swarm_state = SwarmState.EMERGENCY
        elif active_agents < len(self.agents) * 0.5:
            self.swarm_state = SwarmState.ADAPTING
        elif len(self.agents) > 10:
            self.swarm_state = SwarmState.COORDINATING
        else:
            self.swarm_state = SwarmState.ACTIVE
    
    async def _check_agent_health(self):
        """Check health of all agents"""
        
        current_time = datetime.now(timezone.utc)
        inactive_agents = []
        
        for agent_id, agent_status in self.agents.items():
            if (current_time - agent_status.last_heartbeat).seconds > 60:
                inactive_agents.append(agent_id)
        
        # Remove inactive agents
        for agent_id in inactive_agents:
            del self.agents[agent_id]
            self.logger.warning(f"⚠️ Removed inactive agent: {agent_id}")
    
    async def _broadcast_swarm_status(self):
        """Broadcast swarm status to all agents"""
        
        if self.publisher_socket:
            status_message = {
                "message_type": "swarm_status",
                "swarm_state": self.swarm_state.value,
                "total_agents": len(self.agents),
                "active_agents": sum(1 for agent in self.agents.values() 
                                   if (datetime.now(timezone.utc) - agent.last_heartbeat).seconds < 30),
                "avg_performance": np.mean([agent.performance_score for agent in self.agents.values()]) if self.agents else 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.publisher_socket.send_json(status_message)
    
    async def _update_performance_metrics(self):
        """Update swarm performance metrics"""
        
        if not self.agents:
            return
        
        # Calculate metrics
        performance_scores = [agent.performance_score for agent in self.agents.values()]
        profit_losses = [agent.profit_loss for agent in self.agents.values()]
        
        avg_performance = np.mean(performance_scores)
        total_profit_loss = sum(profit_losses)
        
        # Find best and worst performers
        best_agent_id = max(self.agents.items(), key=lambda x: x[1].performance_score)[0]
        worst_agent_id = min(self.agents.items(), key=lambda x: x[1].performance_score)[0]
        
        # Calculate coordination efficiency (simplified)
        coordination_efficiency = min(1.0, avg_performance * len(self.agents) / 10)
        
        # Calculate swarm coherence
        performance_std = np.std(performance_scores) if len(performance_scores) > 1 else 0
        swarm_coherence = max(0.0, 1.0 - performance_std)
        
        # Store performance
        performance = SwarmPerformance(
            total_agents=len(self.agents),
            active_agents=sum(1 for agent in self.agents.values() 
                            if (datetime.now(timezone.utc) - agent.last_heartbeat).seconds < 30),
            total_profit_loss=total_profit_loss,
            avg_performance=avg_performance,
            best_agent_id=best_agent_id,
            worst_agent_id=worst_agent_id,
            coordination_efficiency=coordination_efficiency,
            swarm_coherence=swarm_coherence,
            adaptation_speed=0.8,  # Placeholder
            fault_tolerance=0.9    # Placeholder
        )
        
        self.swarm_performance_history.append(performance)
    
    async def _build_consensus(self, participants: List[str]) -> Dict[str, Any]:
        """Build consensus among specified agents"""
        
        if not participants:
            participants = list(self.agents.keys())
        
        # Collect votes from participants
        votes = {}
        for agent_id in participants:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                votes[agent_id] = {
                    "strategy": agent.current_strategy,
                    "weight": agent.coordination_weight,
                    "performance": agent.performance_score
                }
        
        # Calculate weighted consensus
        strategy_weights = defaultdict(float)
        for vote in votes.values():
            strategy = vote["strategy"]
            weight = vote["weight"] * (1 + vote["performance"])  # Performance bonus
            strategy_weights[strategy] += weight
        
        # Find consensus strategy
        if strategy_weights:
            consensus_strategy = max(strategy_weights.items(), key=lambda x: x[1])[0]
            consensus_strength = strategy_weights[consensus_strategy] / sum(strategy_weights.values())
        else:
            consensus_strategy = "hold"
            consensus_strength = 0.0
        
        return {
            "strategy": consensus_strategy,
            "strength": consensus_strength,
            "participants": len(votes),
            "votes": votes
        }
    
    async def _rebalance_load(self, participants: List[str]) -> Dict[str, Any]:
        """Rebalance load among agents"""
        
        if not participants:
            participants = list(self.agents.keys())
        
        # Calculate current load distribution
        total_trades = sum(self.agents[agent_id].active_trades 
                          for agent_id in participants if agent_id in self.agents)
        
        if total_trades == 0:
            return {"message": "No active trades to rebalance"}
        
        target_trades_per_agent = total_trades // len(participants)
        
        # Suggest rebalancing
        rebalancing_suggestions = {}
        for agent_id in participants:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                current_trades = agent.active_trades
                suggested_trades = target_trades_per_agent
                
                if current_trades > suggested_trades + 1:
                    rebalancing_suggestions[agent_id] = "reduce_load"
                elif current_trades < suggested_trades - 1:
                    rebalancing_suggestions[agent_id] = "increase_load"
                else:
                    rebalancing_suggestions[agent_id] = "maintain_load"
        
        return {
            "total_trades": total_trades,
            "target_per_agent": target_trades_per_agent,
            "suggestions": rebalancing_suggestions
        }
    
    async def get_swarm_performance(self) -> SwarmPerformance:
        """Get current swarm performance"""
        
        if self.swarm_performance_history:
            return self.swarm_performance_history[-1]
        else:
            return SwarmPerformance(
                total_agents=0, active_agents=0, total_profit_loss=0.0,
                avg_performance=0.0, best_agent_id="", worst_agent_id="",
                coordination_efficiency=0.0, swarm_coherence=0.0,
                adaptation_speed=0.0, fault_tolerance=0.0
            )


# Demo function for testing
async def demo_distributed_swarm():
    """Demo the distributed trading swarm"""
    
    print("🤖 Demo: Distributed Trading Swarm")
    print("=" * 60)
    
    # Start coordinator
    coordinator = SwarmCoordinator(port=5555)
    await coordinator.start_coordinator()
    
    print(f"🎛️ Swarm coordinator started")
    
    # Create and start agents
    agents = []
    agent_roles = [
        AgentRole.EXPLORER,
        AgentRole.EXPLOITER,
        AgentRole.COORDINATOR,
        AgentRole.MONITOR,
        AgentRole.LEARNER
    ]
    
    for i, role in enumerate(agent_roles):
        agent = TradingAgent(f"agent_{i+1}", role)
        agents.append(agent)
    
    # Connect agents to coordinator
    print(f"\n🔗 Connecting {len(agents)} agents to swarm...")
    
    connected_agents = []
    for agent in agents:
        try:
            success = await agent.connect_to_swarm()
            if success:
                connected_agents.append(agent)
                print(f"   ✅ {agent.agent_id} ({agent.role.value}) connected")
            else:
                print(f"   ❌ {agent.agent_id} failed to connect")
        except Exception as e:
            print(f"   ❌ {agent.agent_id} connection error: {e}")
    
    if not connected_agents:
        print("❌ No agents connected successfully")
        return
    
    # Simulate market data and trading
    print(f"\n📊 Starting swarm trading simulation...")
    
    for round_num in range(5):
        print(f"\n--- Trading Round {round_num + 1} ---")
        
        # Generate market data
        market_data = {
            "symbol": "SOL/USDT",
            "price": 100.0 + random.uniform(-10, 10),
            "volatility": random.uniform(0.1, 1.0),
            "trend_strength": random.uniform(-0.8, 0.8),
            "volume": random.uniform(0.5, 3.0),
            "spread": random.uniform(0.01, 0.06),
            "recent_change": random.uniform(-0.1, 0.1)
        }
        
        print(f"📈 Market: Price=${market_data['price']:.2f}, Vol={market_data['volatility']:.2f}, Trend={market_data['trend_strength']:.2f}")
        
        # Execute trading logic for each agent
        agent_actions = {}
        for agent in connected_agents:
            try:
                action = await agent.execute_trading_logic(market_data)
                agent_actions[agent.agent_id] = action
                
                # Update agent performance (simulate trade result)
                simulated_result = {
                    "profit_loss": random.uniform(-0.05, 0.05),
                    "action": action["action"],
                    "success": random.random() > 0.3
                }
                agent.update_performance(simulated_result)
                
                print(f"   🤖 {agent.agent_id}: {action['action']} (conf: {action['confidence']:.2f}, size: {action['position_size']:.3f})")
                
            except Exception as e:
                print(f"   ❌ {agent.agent_id} trading error: {e}")
        
        # Send heartbeats
        for agent in connected_agents:
            try:
                await agent.send_heartbeat()
            except Exception as e:
                print(f"   ⚠️ {agent.agent_id} heartbeat failed: {e}")
        
        # Get swarm performance
        performance = await coordinator.get_swarm_performance()
        print(f"   📊 Swarm Performance: Avg={performance.avg_performance:.3f}, Total P&L=${performance.total_profit_loss:.2f}")
        
        # Brief delay between rounds
        await asyncio.sleep(2)
    
    # Final swarm statistics
    print(f"\n📈 Final Swarm Statistics:")
    final_performance = await coordinator.get_swarm_performance()
    
    print(f"   Total Agents: {final_performance.total_agents}")
    print(f"   Active Agents: {final_performance.active_agents}")
    print(f"   Total P&L: ${final_performance.total_profit_loss:.2f}")
    print(f"   Average Performance: {final_performance.avg_performance:.4f}")
    print(f"   Best Agent: {final_performance.best_agent_id}")
    print(f"   Coordination Efficiency: {final_performance.coordination_efficiency:.4f}")
    print(f"   Swarm Coherence: {final_performance.swarm_coherence:.4f}")
    
    # Individual agent performance
    print(f"\n🏆 Individual Agent Performance:")
    for agent in connected_agents:
        print(f"   {agent.agent_id} ({agent.role.value}): Score={agent.performance_score:.4f}, P&L=${agent.profit_loss:.2f}")
    
    print(f"\n🎉 Distributed Swarm Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_distributed_swarm())
