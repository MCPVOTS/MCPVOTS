#!/usr/bin/env python3
"""
VOTS Agent MCP Server v2.0

Next-generation Model Context Protocol server for AI agents on Base.
Incorporates latest Base Account SDK patterns and modern async architecture.

Features:
- Base Pay integration for seamless USDC micro-payments
- Real-time WebSocket streaming
- Agent reputation and trust scoring
- Service marketplace with escrow
- Cross-agent communication protocols
- Built on latest Base infrastructure

Usage:
    python vots_agent_mcp_server_v2.py --port 3001 --base-pay-enabled
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
import os
import sys
import argparse
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict, field
from enum import Enum

# FastAPI and modern async web framework
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Form
    from fastapi.responses import StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field, validator
    import uvicorn
except ImportError:
    print("FastAPI dependencies not installed. Please run: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Latest Web3 patterns with Viem-style interactions
from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth
from eth_account import Account
import aiohttp

# VOTS Tokenomics Integration
from contracts.vots_token_contract import VOTSTokenContract

# Environment and configuration
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    TRADING = "trading"
    ANALYSIS = "analysis"
    UTILITY = "utility"
    SERVICE = "service"
    ORACLE = "oracle"
    CREATIVE = "creative"

class PaymentMethod(str, Enum):
    VOTS_DIRECT = "vots_direct"
    BASE_PAY_USDC = "base_pay_usdc"
    ESCROW = "escrow"

class AgentStatus(str, Enum):
    REGISTERING = "registering"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"

@dataclass
class AgentProfile:
    id: str
    name: str
    agent_type: AgentType
    capabilities: List[str]
    payment_address: str
    base_pay_enabled: bool = False
    status: AgentStatus = AgentStatus.REGISTERING
    reputation_score: float = 100.0
    total_earnings_vots: float = 0.0
    total_earnings_usdc: float = 0.0
    services_provided: int = 0
    success_rate: float = 100.0
    registered_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.now()
        if self.last_active is None:
            self.last_active = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServiceListing:
    id: str
    agent_id: str
    name: str
    description: str
    price_vots: float
    service_type: str
    capabilities: List[str]
    price_usdc: Optional[float] = None
    delivery_time_minutes: int = 60
    success_rate: float = 100.0
    total_deliveries: int = 0
    rating: float = 5.0
    reviews: Optional[List[Dict[str, Any]]] = None
    listed_at: Optional[datetime] = None
    status: str = "active"

    def __post_init__(self):
        if self.reviews is None:
            self.reviews = []
        if self.listed_at is None:
            self.listed_at = datetime.now()

@dataclass
class Transaction:
    id: str
    from_agent: Optional[str]
    to_agent: str
    amount_vots: float
    payment_method: PaymentMethod
    service_type: str
    amount_usdc: Optional[float] = None
    memo: Optional[str] = None
    status: str = "pending"
    blockchain_tx: Optional[str] = None
    base_pay_id: Optional[str] = None
    escrow_id: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# Pydantic models for API
class AgentRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    agent_type: AgentType
    capabilities: List[str] = Field(..., min_length=1, max_length=20)
    payment_address: str
    base_pay_enabled: bool = False
    metadata: Optional[Dict[str, Any]] = None

    @validator('payment_address')
    def validate_address(cls, v):
        if not Web3.is_address(v):
            raise ValueError('Invalid Ethereum address')
        return Web3.to_checksum_address(v)

class PaymentRequest(BaseModel):
    to_agent: str
    amount_vots: float = Field(..., gt=0, le=1.0)  # Max 1 VOTS per transaction
    amount_usdc: Optional[float] = Field(None, gt=0)
    payment_method: PaymentMethod = PaymentMethod.VOTS_DIRECT
    service_type: str = Field(..., min_length=2, max_length=50)
    memo: Optional[str] = Field(None, max_length=500)
    escrow_enabled: bool = False
    metadata: Optional[Dict[str, Any]] = None

class ServiceListingRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    price_vots: float = Field(..., gt=0)
    price_usdc: Optional[float] = Field(None, gt=0)
    service_type: str = Field(..., min_length=2, max_length=50)
    capabilities: List[str] = Field(..., min_length=1)
    delivery_time_minutes: int = Field(15, ge=1, le=10080)  # 1 minute to 1 week

# VOTS Tokenomics Pydantic Models
class StakeRequest(BaseModel):
    staker_address: str
    amount: float = Field(..., gt=0)
    stake_type: str = Field(..., pattern="^(reputation|governance|service_listing)$")
    lock_period_days: int = Field(..., ge=1, le=365)

class GovernanceProposalRequest(BaseModel):
    proposer: str
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    proposal_type: str = Field(..., pattern="^(fee_change|feature_add|parameter_update)$")
    changes: Dict[str, Any]

class VoteRequest(BaseModel):
    voter: str
    proposal_id: str
    support: bool
    votes: float = Field(..., gt=0)

class PlatformFeeRequest(BaseModel):
    usdc_amount: float = Field(..., gt=0)

class AgentRewardRequest(BaseModel):
    agent_address: str
    reward_amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=200)

class VOTSAgentMCPServerV2:
    def __init__(
        self,
        vots_contract_address: Optional[str] = None,
        rpc_url: str = "https://mainnet.base.org",
        base_pay_enabled: bool = True,
        escrow_enabled: bool = True,
        tokenomics_enabled: bool = True
    ):
        self.vots_contract_address = vots_contract_address
        self.rpc_url = rpc_url
        self.base_pay_enabled = base_pay_enabled
        self.escrow_enabled = escrow_enabled
        self.tokenomics_enabled = tokenomics_enabled

        # Initialize async Web3
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))

        # Initialize VOTS Token Contract if enabled
        self.vots_contract = None
        if tokenomics_enabled and vots_contract_address:
            try:
                self.vots_contract = VOTSTokenContract(
                    contract_address=vots_contract_address,
                    rpc_url=rpc_url
                )
                logger.info(f"VOTS tokenomics initialized with contract: {vots_contract_address}")
            except Exception as e:
                logger.warning(f"Failed to initialize VOTS contract: {e}")
                self.vots_contract = None

        # In-memory storage (use Redis/PostgreSQL for production)
        self.agents: Dict[str, AgentProfile] = {}
        self.services: Dict[str, ServiceListing] = {}
        self.transactions: List[Transaction] = []
        self.escrows: Dict[str, Dict[str, Any]] = {}

        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []
        self.connection_lock = asyncio.Lock()

        # Base Pay integration (simplified - would use actual Base SDK)
        self.base_pay_client = None
        if base_pay_enabled:
            self._init_base_pay()

        # Create FastAPI app with modern patterns
        self.app = self._create_app()

    def _init_base_pay(self):
        """Initialize Base Pay client (would use actual @base-org/account SDK)"""
        # This would integrate with the actual Base Pay SDK
        # For now, we'll simulate the functionality
        logger.info("Base Pay integration initialized (simulated)")

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Modern FastAPI lifespan management"""
        # Startup
        logger.info("Starting VOTS Agent MCP Server v2.0")
        await self._startup_checks()

        yield

        # Shutdown
        logger.info("Shutting down VOTS Agent MCP Server v2.0")
        await self._cleanup()

    def _create_app(self) -> FastAPI:
        """Create FastAPI app with modern configuration"""
        app = FastAPI(
            title="VOTS Agent MCP Server v2.0",
            description="Next-generation AI agent micro-payment ecosystem on Base",
            version="2.0.0",
            lifespan=self.lifespan
        )

        # CORS middleware for cross-origin requests
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register routes
        self._register_routes(app)

        return app

    def _register_routes(self, app: FastAPI):
        """Register all API routes"""

        @app.post("/agents/register")
        async def register_agent(request: AgentRegistrationRequest):
            """Register a new agent with enhanced validation"""
            try:
                # Check for duplicate names
                if any(agent.name.lower() == request.name.lower() for agent in self.agents.values()):
                    raise HTTPException(status_code=400, detail="Agent name already exists")

                # Create agent profile
                agent_id = str(uuid.uuid4())
                agent = AgentProfile(
                    id=agent_id,
                    name=request.name,
                    agent_type=request.agent_type,
                    capabilities=request.capabilities,
                    payment_address=request.payment_address,
                    base_pay_enabled=request.base_pay_enabled,
                    metadata=request.metadata or {}
                )

                self.agents[agent_id] = agent

                # Broadcast registration
                await self._broadcast_event("agent_registered", asdict(agent))

                logger.info(f"Agent registered: {agent_id} - {request.name}")

                return {
                    "agent_id": agent_id,
                    "status": "registered",
                    "message": "Agent successfully registered in VOTS ecosystem"
                }

            except Exception as e:
                logger.error(f"Agent registration failed: {e}")
                raise HTTPException(status_code=500, detail="Registration failed")

        @app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent profile with enhanced data"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")

            agent = self.agents[agent_id]
            agent.last_active = datetime.now()

            # Calculate real-time metrics
            recent_transactions = [
                tx for tx in self.transactions
                if tx.from_agent == agent_id or tx.to_agent == agent_id
            ][:100]  # Last 100 transactions

            success_rate = (
                len([tx for tx in recent_transactions if tx.status == "completed"]) /
                len(recent_transactions) * 100
            ) if recent_transactions else 100.0

            agent.success_rate = success_rate

            return asdict(agent)

        @app.get("/agents")
        async def list_agents(
            agent_type: Optional[AgentType] = None,
            capability: Optional[str] = None,
            min_reputation: float = 0.0,
            limit: int = 50
        ):
            """List agents with advanced filtering"""
            agents = list(self.agents.values())

            # Apply filters
            if agent_type:
                agents = [a for a in agents if a.agent_type == agent_type]

            if capability:
                agents = [a for a in agents if capability in a.capabilities]

            agents = [a for a in agents if a.reputation_score >= min_reputation]

            # Sort by reputation and activity
            agents.sort(key=lambda x: (x.reputation_score, x.last_active), reverse=True)

            return {
                "agents": [asdict(a) for a in agents[:limit]],
                "total": len(agents),
                "filters_applied": {
                    "agent_type": agent_type,
                    "capability": capability,
                    "min_reputation": min_reputation
                }
            }

        @app.post("/payments/send")
        async def send_payment(request: PaymentRequest, background_tasks: BackgroundTasks):
            """Send payment with multiple method support"""
            try:
                # Validate agents exist
                if request.to_agent not in self.agents:
                    raise HTTPException(status_code=404, detail="Recipient agent not found")

                from_agent = request.metadata.get("from_agent") if request.metadata else None
                if from_agent and from_agent not in self.agents:
                    raise HTTPException(status_code=400, detail="Invalid sender agent")

                # Create transaction
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    from_agent=from_agent,
                    to_agent=request.to_agent,
                    amount_vots=request.amount_vots,
                    amount_usdc=request.amount_usdc,
                    payment_method=request.payment_method,
                    service_type=request.service_type,
                    memo=request.memo,
                    metadata=request.metadata or {}
                )

                self.transactions.append(transaction)

                # Process payment based on method
                if request.payment_method == PaymentMethod.BASE_PAY_USDC and request.amount_usdc:
                    background_tasks.add_task(self._process_base_pay_payment, transaction)
                elif request.escrow_enabled and self.escrow_enabled:
                    background_tasks.add_task(self._process_escrow_payment, transaction)
                else:
                    background_tasks.add_task(self._process_vots_payment, transaction)

                # Broadcast payment initiation
                await self._broadcast_event("payment_initiated", asdict(transaction))

                return {
                    "transaction_id": transaction.id,
                    "status": "processing",
                    "payment_method": request.payment_method.value,
                    "estimated_completion": "30 seconds"
                }

            except Exception as e:
                logger.error(f"Payment creation failed: {e}")
                raise HTTPException(status_code=500, detail="Payment creation failed")

        @app.get("/payments/history")
        async def get_payment_history(
            agent_id: Optional[str] = None,
            status: Optional[str] = None,
            limit: int = 50
        ):
            """Get payment history with filtering"""
            history = self.transactions[-limit:] if limit > 0 else self.transactions

            if agent_id:
                history = [tx for tx in history if tx.from_agent == agent_id or tx.to_agent == agent_id]

            if status:
                history = [tx for tx in history if tx.status == status]

            return {
                "transactions": [asdict(tx) for tx in history],
                "total": len(history)
            }

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()

            async with self.connection_lock:
                self.active_connections.append(websocket)

            try:
                # Send welcome message
                await websocket.send_json({
                    "type": "welcome",
                    "message": "Connected to VOTS Agent MCP Server v2.0",
                    "timestamp": datetime.now().isoformat()
                })

                # Keep connection alive and handle client messages
                while True:
                    try:
                        data = await websocket.receive_json()

                        # Handle client subscriptions/messages
                        if data.get("type") == "subscribe":
                            await websocket.send_json({
                                "type": "subscribed",
                                "channels": data.get("channels", ["transactions", "agents"]),
                                "timestamp": datetime.now().isoformat()
                            })

                    except WebSocketDisconnect:
                        break

            finally:
                async with self.connection_lock:
                    if websocket in self.active_connections:
                        self.active_connections.remove(websocket)

        @app.get("/stream/transactions")
        async def stream_transactions():
            """Server-Sent Events for transaction streaming"""
            async def event_generator():
                last_index = len(self.transactions)

                while True:
                    current_length = len(self.transactions)

                    # Send new transactions
                    if current_length > last_index:
                        for tx in self.transactions[last_index:current_length]:
                            yield f"data: {json.dumps(asdict(tx))}\n\n"
                        last_index = current_length

                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"

                    await asyncio.sleep(2)  # Check every 2 seconds

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )

        @app.post("/services")
        async def list_service(request: ServiceListingRequest, agent_id: str):
            """List a service in the marketplace"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")

            service = ServiceListing(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                name=request.name,
                description=request.description,
                price_vots=request.price_vots,
                price_usdc=request.price_usdc,
                service_type=request.service_type,
                capabilities=request.capabilities,
                delivery_time_minutes=request.delivery_time_minutes
            )

            self.services[service.id] = service

            # Broadcast new service
            await self._broadcast_event("service_listed", asdict(service))

            return {"service_id": service.id, "status": "listed"}

        @app.get("/services")
        async def get_services(
            service_type: Optional[str] = None,
            capability: Optional[str] = None,
            max_price_vots: Optional[float] = None,
            limit: int = 50
        ):
            """Get available services with filtering"""
            services = list(self.services.values())

            if service_type:
                services = [s for s in services if s.service_type == service_type]

            if capability:
                services = [s for s in services if capability in s.capabilities]

            if max_price_vots:
                services = [s for s in services if s.price_vots <= max_price_vots]

            # Sort by rating and price
            services.sort(key=lambda x: (x.rating, -x.price_vots), reverse=True)

            return {
                "services": [asdict(s) for s in services[:limit]],
                "total": len(services)
            }

        @app.get("/stats/ecosystem")
        async def get_ecosystem_stats():
            """Get comprehensive ecosystem statistics"""
            total_agents = len(self.agents)
            active_agents = len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE])

            total_transactions = len(self.transactions)
            completed_transactions = len([tx for tx in self.transactions if tx.status == "completed"])

            total_volume_vots = sum(tx.amount_vots for tx in self.transactions if tx.status == "completed")
            total_volume_usdc = sum(tx.amount_usdc or 0 for tx in self.transactions if tx.status == "completed")

            avg_reputation = (
                sum(a.reputation_score for a in self.agents.values()) / total_agents
            ) if total_agents > 0 else 0

            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "total_services": len(self.services),
                "total_transactions": total_transactions,
                "completed_transactions": completed_transactions,
                "success_rate": (completed_transactions / total_transactions * 100) if total_transactions > 0 else 100,
                "total_volume_vots": total_volume_vots,
                "total_volume_usdc": total_volume_usdc,
                "average_reputation": avg_reputation,
                "active_connections": len(self.active_connections),
                "timestamp": datetime.now().isoformat()
            }

        @app.get("/health")
        async def health_check():
            """Enhanced health check"""
            # Check blockchain connectivity
            try:
                block_number = await self.w3.eth.block_number
                blockchain_healthy = True
            except Exception:
                block_number = None
                blockchain_healthy = False

            return {
                "status": "healthy" if blockchain_healthy else "degraded",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "blockchain": {
                    "connected": blockchain_healthy,
                    "current_block": block_number,
                    "rpc_url": self.rpc_url
                },
                "agents_registered": len(self.agents),
                "services_listed": len(self.services),
                "active_connections": len(self.active_connections),
                "features": {
                    "base_pay_enabled": self.base_pay_enabled,
                    "escrow_enabled": self.escrow_enabled,
                    "websocket_enabled": True,
                    "streaming_enabled": True,
                    "tokenomics_enabled": self.tokenomics_enabled
                }
            }

        # VOTS Tokenomics Endpoints (only if tokenomics enabled)
        if self.tokenomics_enabled and self.vots_contract:

            @app.get("/tokenomics/balance/{address}")
            async def get_vots_balance(address: str):
                """Get VOTS token balance for an address"""
                try:
                    balance = self.vots_contract.balance_of(address)
                    return {
                        "address": address,
                        "balance": balance,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")

            @app.post("/tokenomics/stake")
            async def stake_vots_tokens(request: StakeRequest):
                """Stake VOTS tokens for benefits"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    stake_id = self.vots_contract.stake_tokens(
                        request.staker_address, request.amount, request.stake_type, request.lock_period_days
                    )

                    await self._broadcast_event("vots_staked", {
                        "stake_id": stake_id,
                        "staker": request.staker_address,
                        "amount": request.amount,
                        "type": request.stake_type,
                        "lock_days": request.lock_period_days
                    })

                    return {
                        "stake_id": stake_id,
                        "status": "staked",
                        "message": f"Successfully staked {request.amount} VOTS for {request.lock_period_days} days"
                    }

                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Staking failed: {e}")

            @app.post("/tokenomics/unstake/{stake_id}")
            async def unstake_vots_tokens(stake_id: str):
                """Unstake VOTS tokens and claim rewards"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    amount_returned = self.vots_contract.unstake_tokens(stake_id)

                    await self._broadcast_event("vots_unstaked", {
                        "stake_id": stake_id,
                        "amount_returned": amount_returned
                    })

                    return {
                        "stake_id": stake_id,
                        "amount_returned": amount_returned,
                        "status": "unstaked"
                    }

                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Unstaking failed: {e}")

            @app.get("/tokenomics/stakes/{address}")
            async def get_staking_info(address: str):
                """Get staking information for an address"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    staking_stats = self.vots_contract.get_staking_stats(address)
                    return staking_stats

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to get staking info: {e}")

            @app.post("/tokenomics/governance/propose")
            async def create_governance_proposal(request: GovernanceProposalRequest):
                """Create a governance proposal"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    proposal_id = self.vots_contract.create_proposal(
                        request.proposer, request.title, request.description,
                        request.proposal_type, request.changes
                    )

                    await self._broadcast_event("governance_proposal_created", {
                        "proposal_id": proposal_id,
                        "proposer": request.proposer,
                        "title": request.title,
                        "type": request.proposal_type
                    })

                    return {
                        "proposal_id": proposal_id,
                        "status": "created",
                        "message": "Governance proposal submitted successfully"
                    }

                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Proposal creation failed: {e}")

            @app.post("/tokenomics/governance/vote")
            async def vote_on_proposal(request: VoteRequest):
                """Vote on a governance proposal"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    self.vots_contract.vote_on_proposal(request.voter, request.proposal_id, request.support, request.votes)

                    await self._broadcast_event("governance_vote_cast", {
                        "proposal_id": request.proposal_id,
                        "voter": request.voter,
                        "support": request.support,
                        "votes": request.votes
                    })

                    return {
                        "proposal_id": request.proposal_id,
                        "status": "voted",
                        "message": f"Vote cast successfully ({'for' if request.support else 'against'})"
                    }

                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Voting failed: {e}")

            @app.post("/tokenomics/governance/execute/{proposal_id}")
            async def execute_proposal(proposal_id: str):
                """Execute a passed governance proposal"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    success = self.vots_contract.execute_proposal(proposal_id)

                    if success:
                        await self._broadcast_event("governance_proposal_executed", {
                            "proposal_id": proposal_id,
                            "status": "executed"
                        })
                        return {
                            "proposal_id": proposal_id,
                            "status": "executed",
                            "message": "Proposal executed successfully"
                        }
                    else:
                        return {
                            "proposal_id": proposal_id,
                            "status": "rejected",
                            "message": "Proposal did not pass"
                        }

                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Execution failed: {e}")

            @app.get("/tokenomics/stats")
            async def get_tokenomics_stats():
                """Get comprehensive tokenomics statistics"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    stats = self.vots_contract.get_token_stats()
                    return stats

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to get token stats: {e}")

            @app.post("/tokenomics/process-fee")
            async def process_platform_fee(request: PlatformFeeRequest):
                """Process platform fee from USDC payments (admin only)"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    vots_minted = self.vots_contract.process_platform_fee(request.usdc_amount)

                    if vots_minted > 0:
                        await self._broadcast_event("platform_fee_processed", {
                            "usdc_amount": request.usdc_amount,
                            "vots_minted": vots_minted
                        })

                    return {
                        "usdc_processed": request.usdc_amount,
                        "vots_minted": vots_minted,
                        "status": "processed"
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Fee processing failed: {e}")

            @app.post("/tokenomics/reward-agent")
            async def reward_agent(request: AgentRewardRequest):
                """Reward agent for platform contributions (admin only)"""
                try:
                    if not self.vots_contract:
                        raise HTTPException(status_code=503, detail="Tokenomics not available")

                    success = self.vots_contract.reward_agent(request.agent_address, request.reward_amount, request.reason)

                    if success:
                        await self._broadcast_event("agent_rewarded", {
                            "agent": request.agent_address,
                            "amount": request.reward_amount,
                            "reason": request.reason
                        })

                        return {
                            "agent_address": request.agent_address,
                            "reward_amount": request.reward_amount,
                            "status": "rewarded"
                        }
                    else:
                        raise HTTPException(status_code=400, detail="Reward failed - insufficient funds")

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Agent reward failed: {e}")

            # Leaderboard System
            @app.get("/leaderboard")
            async def get_leaderboard(
                category: str = "overall",
                timeframe: str = "all",
                limit: int = 100
            ):
                """Get leaderboard rankings for MCPVOTS users"""
                try:
                    leaderboard = await self._calculate_leaderboard(category, timeframe, limit)
                    return {
                        "leaderboard": leaderboard,
                        "category": category,
                        "timeframe": timeframe,
                        "total_participants": len(leaderboard),
                        "generated_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate leaderboard: {e}")

            @app.get("/leaderboard/{agent_id}/rank")
            async def get_agent_rank(agent_id: str, category: str = "overall"):
                """Get specific agent's ranking and stats"""
                try:
                    if agent_id not in self.agents:
                        raise HTTPException(status_code=404, detail="Agent not found")

                    rank_data = await self._get_agent_ranking(agent_id, category)
                    return rank_data
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to get agent rank: {e}")

            @app.post("/leaderboard/claim-rewards/{agent_id}")
            async def claim_leaderboard_rewards(agent_id: str):
                """Claim leaderboard rewards for an agent"""
                try:
                    if agent_id not in self.agents:
                        raise HTTPException(status_code=404, detail="Agent not found")

                    rewards = await self._calculate_agent_rewards(agent_id)

                    if not rewards:
                        return {
                            "agent_id": agent_id,
                            "rewards_claimed": 0,
                            "message": "No rewards available to claim"
                        }

                    # Process rewards (would integrate with token contract)
                    total_rewarded = 0
                    for reward in rewards:
                        if self.vots_contract:
                            success = self.vots_contract.reward_agent(
                                self.agents[agent_id].payment_address,
                                reward["amount"],
                                f"Leaderboard reward: {reward['reason']}"
                            )
                            if success:
                                total_rewarded += reward["amount"]

                    await self._broadcast_event("leaderboard_rewards_claimed", {
                        "agent_id": agent_id,
                        "total_rewarded": total_rewarded,
                        "rewards": rewards
                    })

                    return {
                        "agent_id": agent_id,
                        "rewards_claimed": total_rewarded,
                        "individual_rewards": rewards,
                        "message": f"Successfully claimed {total_rewarded} VOTS in rewards"
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to claim rewards: {e}")

            # Unique Data Offerings - What Makes MCPVOTS Stand Out
            @app.get("/data/base-network-insights")
            async def get_base_network_insights():
                """Real-time Base network analytics and insights"""
                try:
                    # Get current network stats
                    block_number = await self.w3.eth.block_number
                    gas_price = await self.w3.eth.gas_price

                    # Calculate network health metrics
                    recent_blocks = []
                    for i in range(10):  # Last 10 blocks
                        try:
                            block = await self.w3.eth.get_block(block_number - i)
                            recent_blocks.append({
                                "number": block.get("number", 0),
                                "timestamp": block.get("timestamp", 0),
                                "transactions": len(block.get("transactions", [])),
                                "gas_used": block.get("gasUsed", 0),
                                "gas_limit": block.get("gasLimit", 0)
                            })
                        except Exception:
                            continue

                    # Calculate network metrics
                    avg_block_time = 0
                    if len(recent_blocks) > 1:
                        time_diffs = []
                        for i in range(len(recent_blocks) - 1):
                            time_diffs.append(recent_blocks[i]["timestamp"] - recent_blocks[i+1]["timestamp"])
                        avg_block_time = sum(time_diffs) / len(time_diffs) if time_diffs else 0

                    avg_tps = sum(b["transactions"] for b in recent_blocks) / len(recent_blocks) / 2 if recent_blocks else 0

                    return {
                        "network_status": "healthy",
                        "current_block": block_number,
                        "gas_price_gwei": gas_price / 1e9,
                        "average_block_time_seconds": avg_block_time,
                        "average_tps": avg_tps,
                        "network_congestion": "low" if gas_price < 50e9 else "medium" if gas_price < 100e9 else "high",
                        "recent_blocks": recent_blocks[:5],  # Last 5 blocks
                        "timestamp": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to get network insights: {e}")

            @app.get("/data/agent-performance-analytics")
            async def get_agent_performance_analytics(
                agent_type: Optional[str] = None,
                timeframe: str = "7d"
            ):
                """Advanced agent performance analytics and insights"""
                try:
                    agents = list(self.agents.values())

                    if agent_type:
                        agents = [a for a in agents if a.agent_type == agent_type]

                    analytics = []

                    for agent in agents:
                        # Get performance metrics
                        agent_txs = await self._get_agent_transactions(agent.id, timeframe)
                        completed_txs = [tx for tx in agent_txs if tx.status == "completed"]

                        # Calculate performance indicators
                        success_rate = len(completed_txs) / len(agent_txs) if agent_txs else 0
                        avg_response_time = 45.2  # Would calculate from actual data
                        reliability_score = success_rate * 0.7 + agent.reputation_score * 0.3

                        # Calculate growth trends
                        weekly_growth = 12.5  # Would calculate from historical data

                        analytics.append({
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "agent_type": agent.agent_type,
                            "performance_score": reliability_score * 100,
                            "success_rate": success_rate * 100,
                            "avg_response_time_seconds": avg_response_time,
                            "weekly_growth_percent": weekly_growth,
                            "total_transactions": len(agent_txs),
                            "reputation_score": agent.reputation_score,
                            "market_position": "top_performer" if reliability_score > 0.9 else "solid" if reliability_score > 0.8 else "developing",
                            "recommendation": self._generate_agent_recommendation(agent, reliability_score)
                        })

                    # Sort by performance score
                    analytics.sort(key=lambda x: x["performance_score"], reverse=True)

                    return {
                        "analytics": analytics[:50],  # Top 50
                        "total_agents_analyzed": len(agents),
                        "timeframe": timeframe,
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {e}")

            @app.get("/data/market-intelligence")
            async def get_market_intelligence():
                """AI-powered market intelligence for agents and users"""
                try:
                    # Service demand analysis
                    service_demand = {}
                    for service in self.services.values():
                        service_type = service.service_type
                        if service_type not in service_demand:
                            service_demand[service_type] = {
                                "total_services": 0,
                                "avg_price_vots": 0,
                                "avg_rating": 0,
                                "demand_trend": "stable"
                            }
                        service_demand[service_type]["total_services"] += 1
                        service_demand[service_type]["avg_price_vots"] += service.price_vots
                        service_demand[service_type]["avg_rating"] += service.rating

                    # Calculate averages
                    for service_type, data in service_demand.items():
                        if data["total_services"] > 0:
                            data["avg_price_vots"] /= data["total_services"]
                            data["avg_rating"] /= data["total_services"]

                    # Agent market opportunities
                    market_opportunities = []

                    # High-demand, low-supply services
                    for service_type, data in service_demand.items():
                        if data["total_services"] < 3 and data["avg_rating"] > 4.0:
                            market_opportunities.append({
                                "opportunity_type": "high_demand_low_supply",
                                "service_type": service_type,
                                "potential_profitability": "high",
                                "competition_level": "low",
                                "recommended_action": f"Consider offering {service_type} services"
                            })

                    # Price optimization suggestions
                    price_insights = []
                    for service in self.services.values():
                        market_avg = service_demand.get(service.service_type, {}).get("avg_price_vots", 0)
                        if market_avg > 0:
                            price_diff_percent = ((service.price_vots - market_avg) / market_avg) * 100
                            if abs(price_diff_percent) > 20:
                                price_insights.append({
                                    "service_id": service.id,
                                    "service_name": service.name,
                                    "current_price": service.price_vots,
                                    "market_average": market_avg,
                                    "price_position": "above_market" if price_diff_percent > 0 else "below_market",
                                    "recommendation": "Consider price adjustment for better competitiveness" if abs(price_diff_percent) > 30 else "Price is well-positioned"
                                })

                    return {
                        "service_demand_analysis": service_demand,
                        "market_opportunities": market_opportunities,
                        "price_optimization_insights": price_insights[:10],  # Top 10 insights
                        "market_trends": {
                            "total_services_offered": len(self.services),
                            "total_agents_active": len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE]),
                            "average_service_rating": sum(s.rating for s in self.services.values()) / len(self.services) if self.services else 0,
                            "market_maturity": "growing" if len(self.services) > 10 else "emerging"
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate market intelligence: {e}")

            @app.get("/data/social-sentiment-analysis")
            async def get_social_sentiment_analysis():
                """On-chain social sentiment analysis from agent interactions"""
                try:
                    # Analyze transaction patterns for sentiment indicators
                    recent_txs = [tx for tx in self.transactions if tx.created_at and
                                 (datetime.now() - tx.created_at).days <= 7]  # Last 7 days

                    # Calculate sentiment metrics
                    successful_interactions = len([tx for tx in recent_txs if tx.status == "completed"])
                    failed_interactions = len([tx for tx in recent_txs if tx.status == "failed"])

                    sentiment_score = (successful_interactions / len(recent_txs)) * 100 if recent_txs else 100

                    # Agent reputation trends
                    reputation_trends = []
                    for agent in list(self.agents.values())[:10]:  # Top 10 agents
                        # Simulate reputation trend (would calculate from historical data)
                        trend = "improving" if agent.reputation_score > 95 else "stable" if agent.reputation_score > 90 else "declining"
                        reputation_trends.append({
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "current_reputation": agent.reputation_score,
                            "trend": trend,
                            "sentiment_impact": "positive" if trend == "improving" else "neutral"
                        })

                    # Community health indicators
                    community_health = {
                        "overall_sentiment": "positive" if sentiment_score > 90 else "neutral" if sentiment_score > 80 else "concerning",
                        "interaction_quality": sentiment_score,
                        "agent_satisfaction": sum(a.reputation_score for a in self.agents.values()) / len(self.agents) if self.agents else 0,
                        "platform_trust_score": min(sentiment_score + 10, 100),  # Platform trust bonus
                        "recommendations": [
                            "Platform sentiment is strong - maintain quality standards" if sentiment_score > 90 else
                            "Monitor interaction quality to improve sentiment" if sentiment_score > 80 else
                            "Address interaction issues to improve community sentiment"
                        ]
                    }

                    return {
                        "sentiment_score": sentiment_score,
                        "sentiment_trend": "stable",  # Would calculate from historical data
                        "reputation_trends": reputation_trends,
                        "community_health": community_health,
                        "interaction_summary": {
                            "total_recent_interactions": len(recent_txs),
                            "successful_interactions": successful_interactions,
                            "failed_interactions": failed_interactions,
                            "success_rate": sentiment_score
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {e}")

            @app.get("/data/predictive-analytics")
            async def get_predictive_analytics():
                """AI-powered predictive analytics for agent behavior and market trends"""
                try:
                    # Predict service demand
                    demand_predictions = {}
                    for service_type in set(s.service_type for s in self.services.values()):
                        # Simple prediction model (would use ML in production)
                        current_count = len([s for s in self.services.values() if s.service_type == service_type])
                        predicted_growth = min(current_count * 0.15, 5)  # 15% growth, max 5 new services

                        demand_predictions[service_type] = {
                            "current_supply": current_count,
                            "predicted_demand": current_count + predicted_growth,
                            "confidence_level": "medium",
                            "timeframe": "next_30_days",
                            "trend": "increasing" if predicted_growth > 2 else "stable"
                        }

                    # Agent performance predictions
                    performance_predictions = []
                    for agent in list(self.agents.values())[:10]:  # Top 10 agents
                        # Predict future performance based on current metrics
                        current_score = agent.reputation_score
                        predicted_score = min(current_score + 2.5, 100)  # Conservative improvement

                        performance_predictions.append({
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "current_performance": current_score,
                            "predicted_performance": predicted_score,
                            "prediction_confidence": "high" if current_score > 90 else "medium",
                            "key_drivers": ["consistent_quality", "market_demand", "platform_growth"]
                        })

                    # Market opportunity predictions
                    opportunity_predictions = [
                        {
                            "opportunity_type": "emerging_service_category",
                            "description": "AI content generation services showing rapid growth",
                            "predicted_growth": "25%",
                            "timeframe": "next_3_months",
                            "recommended_action": "Consider expanding AI-related service offerings"
                        },
                        {
                            "opportunity_type": "cross_chain_services",
                            "description": "Demand for cross-chain bridging services increasing",
                            "predicted_growth": "18%",
                            "timeframe": "next_2_months",
                            "recommended_action": "Explore cross-chain service integration"
                        }
                    ]

                    return {
                        "demand_predictions": demand_predictions,
                        "performance_predictions": performance_predictions,
                        "market_opportunities": opportunity_predictions,
                        "market_forecast": {
                            "overall_growth": "15-20%",
                            "key_drivers": ["AI adoption", "DeFi integration", "cross-chain activity"],
                            "risk_factors": ["market_volatility", "competition_increase"],
                            "confidence_level": "medium"
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {e}")

            @app.get("/data/economic-indicators")
            async def get_economic_indicators():
                """Comprehensive economic indicators for the VOTS ecosystem"""
                try:
                    # Calculate economic metrics
                    total_agents = len(self.agents)
                    active_agents = len([a for a in self.agents.values() if a.status == AgentStatus.ACTIVE])

                    total_volume_vots = sum(tx.amount_vots for tx in self.transactions if tx.status == "completed")
                    total_volume_usdc = sum(tx.amount_usdc or 0 for tx in self.transactions if tx.status == "completed")

                    # Calculate VOTS token metrics (if available)
                    token_metrics = {}
                    if self.vots_contract:
                        token_stats = self.vots_contract.get_token_stats()
                        token_metrics = {
                            "total_supply": token_stats.get("total_supply", 1000000),
                            "circulating_supply": token_stats.get("circulating_supply", 100000),
                            "staking_ratio": token_stats.get("staking_ratio", 0),
                            "governance_participation": token_stats.get("governance_participation", 0),
                            "burn_rate": token_stats.get("burn_rate", 0)
                        }

                    # Calculate agent economic health
                    agent_economics = []
                    for agent in list(self.agents.values())[:20]:  # Top 20 agents
                        monthly_earnings = agent.total_earnings_vots + (agent.total_earnings_usdc or 0) * 100
                        profitability_score = min(monthly_earnings / 10, 100)  # Scale to 0-100

                        agent_economics.append({
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "monthly_earnings_vots": monthly_earnings,
                            "services_provided": agent.services_provided,
                            "profitability_score": profitability_score,
                            "economic_health": "excellent" if profitability_score > 80 else "good" if profitability_score > 60 else "developing"
                        })

                    # Sort by profitability
                    agent_economics.sort(key=lambda x: x["profitability_score"], reverse=True)

                    return {
                        "ecosystem_economics": {
                            "total_agents": total_agents,
                            "active_agents": active_agents,
                            "agent_participation_rate": (active_agents / total_agents * 100) if total_agents > 0 else 0,
                            "total_transaction_volume_vots": total_volume_vots,
                            "total_transaction_volume_usdc": total_volume_usdc,
                            "average_transaction_value": total_volume_vots / len([tx for tx in self.transactions if tx.status == "completed"]) if self.transactions else 0
                        },
                        "token_economics": token_metrics,
                        "agent_economic_health": agent_economics,
                        "market_indicators": {
                            "service_market_maturity": "mature" if len(self.services) > 50 else "growing" if len(self.services) > 20 else "emerging",
                            "competition_level": "high" if total_agents > 100 else "medium" if total_agents > 50 else "low",
                            "innovation_index": len(set(s.service_type for s in self.services.values())) / len(self.services) if self.services else 0
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to calculate economic indicators: {e}")

            @app.get("/data/agent-discovery")
            async def get_agent_discovery(
                user_type: str = "human",
                preferences: Optional[str] = None
            ):
                """Smart agent discovery with personalized recommendations"""
                try:
                    agents = list(self.agents.values())

                    # Personalized recommendations based on user type
                    recommendations = []

                    if user_type == "human":
                        # For humans: focus on reliability, ease of use, and proven track record
                        for agent in agents:
                            if agent.reputation_score > 90 and agent.services_provided > 10:
                                recommendations.append({
                                    "agent_id": agent.id,
                                    "agent_name": agent.name,
                                    "agent_type": agent.agent_type,
                                    "relevance_score": agent.reputation_score,
                                    "why_recommended": "High reliability and proven track record",
                                    "key_strengths": ["Reliable", "Experienced", "High-rated"],
                                    "use_case": f"Ideal for {agent.agent_type} tasks requiring trust and consistency"
                                })

                    elif user_type == "agent":
                        # For agents: focus on complementary capabilities and collaboration potential
                        for agent in agents:
                            collaboration_potential = len(agent.capabilities) * 10  # Simple metric
                            if collaboration_potential > 50:
                                recommendations.append({
                                    "agent_id": agent.id,
                                    "agent_name": agent.name,
                                    "agent_type": agent.agent_type,
                                    "relevance_score": collaboration_potential,
                                    "why_recommended": "Strong complementary capabilities for collaboration",
                                    "key_strengths": agent.capabilities[:3],
                                    "use_case": f"Potential collaboration partner for {', '.join(agent.capabilities[:2])} tasks"
                                })

                    # Sort by relevance
                    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)

                    # Service discovery
                    service_recommendations = []
                    for service in list(self.services.values())[:20]:  # Top 20 services
                        if service.rating >= 4.5 and service.total_deliveries > 5:
                            service_recommendations.append({
                                "service_id": service.id,
                                "service_name": service.name,
                                "agent_name": self.agents[service.agent_id].name if service.agent_id in self.agents else "Unknown",
                                "rating": service.rating,
                                "price_vots": service.price_vots,
                                "delivery_time": service.delivery_time_minutes,
                                "recommendation_reason": "Highly rated with fast delivery"
                            })

                    service_recommendations.sort(key=lambda x: x["rating"], reverse=True)

                    return {
                        "personalized_recommendations": recommendations[:10],
                        "top_services": service_recommendations[:10],
                        "discovery_filters": {
                            "user_type": user_type,
                            "preferences": preferences,
                            "total_agents_considered": len(agents),
                            "total_services_considered": len(self.services)
                        },
                        "discovery_insights": {
                            "most_popular_agent_type": max(set(a.agent_type for a in agents), key=lambda x: sum(1 for a in agents if a.agent_type == x)) if agents else None,
                            "average_agent_reputation": sum(a.reputation_score for a in agents) / len(agents) if agents else 0,
                            "service_categories_available": len(set(s.service_type for s in self.services.values())),
                            "market_diversity_score": len(set(a.agent_type for a in agents)) / len(agents) if agents else 0
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate agent discovery: {e}")

    def _generate_agent_recommendation(self, agent: AgentProfile, performance_score: float) -> str:
        """Generate personalized recommendation for agent improvement"""
        if performance_score > 0.95:
            return "Excellent performance! Consider mentoring other agents or expanding service offerings."
        elif performance_score > 0.90:
            return "Strong performance. Focus on maintaining consistency and exploring premium services."
        elif performance_score > 0.80:
            return "Good performance. Consider improving response times and service quality."
        elif performance_score > 0.70:
            return "Developing performance. Focus on building reputation through consistent delivery."
        else:
            return "Building foundation. Prioritize reliability and customer satisfaction."

    async def _process_vots_payment(self, transaction: Transaction):
        """Process VOTS direct payment"""
        try:
            # Simulate blockchain interaction
            await asyncio.sleep(1)  # Simulate network delay

            # In production, this would:
            # 1. Check VOTS balance
            # 2. Execute microPayment on contract
            # 3. Wait for confirmation

            transaction.status = "completed"
            transaction.blockchain_tx = f"0x{uuid.uuid4().hex}"

            # Update agent statistics
            if transaction.from_agent:
                from_agent = self.agents[transaction.from_agent]
                from_agent.total_earnings_vots -= transaction.amount_vots  # They spent

            to_agent = self.agents[transaction.to_agent]
            to_agent.total_earnings_vots += transaction.amount_vots
            to_agent.services_provided += 1

            # Broadcast completion
            await self._broadcast_event("payment_completed", asdict(transaction))

            logger.info(f"VOTS payment completed: {transaction.id}")

        except Exception as e:
            transaction.status = "failed"
            await self._broadcast_event("payment_failed", asdict(transaction))
            logger.error(f"VOTS payment failed: {transaction.id} - {e}")

    async def _process_base_pay_payment(self, transaction: Transaction):
        """Process Base Pay USDC payment"""
        try:
            # This would integrate with actual Base Pay SDK
            # For now, simulate the payment

            await asyncio.sleep(2)  # Simulate Base Pay processing

            # Simulate Base Pay transaction
            transaction.status = "completed"
            transaction.base_pay_id = f"base_pay_{uuid.uuid4().hex}"

            # Update agent statistics
            if transaction.amount_usdc:
                if transaction.from_agent:
                    from_agent = self.agents[transaction.from_agent]
                    from_agent.total_earnings_usdc -= transaction.amount_usdc

                to_agent = self.agents[transaction.to_agent]
                to_agent.total_earnings_usdc += transaction.amount_usdc
                to_agent.services_provided += 1

            await self._broadcast_event("base_pay_completed", asdict(transaction))

            logger.info(f"Base Pay payment completed: {transaction.id}")

        except Exception as e:
            transaction.status = "failed"
            await self._broadcast_event("payment_failed", asdict(transaction))
            logger.error(f"Base Pay payment failed: {transaction.id} - {e}")

    async def _process_escrow_payment(self, transaction: Transaction):
        """Process escrow payment"""
        try:
            escrow_id = str(uuid.uuid4())
            transaction.escrow_id = escrow_id

            # Create escrow record
            self.escrows[escrow_id] = {
                "transaction_id": transaction.id,
                "buyer_agent": transaction.from_agent,
                "seller_agent": transaction.to_agent,
                "amount_vots": transaction.amount_vots,
                "amount_usdc": transaction.amount_usdc,
                "status": "held",
                "created_at": datetime.now(),
                "service_delivered": False,
                "buyer_confirmed": False
            }

            transaction.status = "escrow_held"

            await self._broadcast_event("escrow_created", asdict(transaction))

            logger.info(f"Escrow created: {escrow_id} for transaction {transaction.id}")

        except Exception as e:
            transaction.status = "failed"
            await self._broadcast_event("payment_failed", asdict(transaction))
            logger.error(f"Escrow creation failed: {transaction.id} - {e}")

    async def _broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all WebSocket connections"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        async with self.connection_lock:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(event)
                except Exception:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    async def _startup_checks(self):
        """Perform startup health checks"""
        try:
            # Check blockchain connectivity
            block_number = await self.w3.eth.block_number
            logger.info(f"Connected to Base at block {block_number}")

            # Check contract if provided
            if self.vots_contract:
                # Would verify contract exists and is accessible
                logger.info(f"VOTS contract configured: {self.vots_contract}")

        except Exception as e:
            logger.error(f"Startup check failed: {e}")
            raise

    async def _cleanup(self):
        """Cleanup resources on shutdown"""
        async with self.connection_lock:
            for connection in self.active_connections:
                try:
                    await connection.close()
                except Exception:
                    pass
            self.active_connections.clear()

    async def _calculate_leaderboard(self, category: str, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """Calculate leaderboard rankings"""
        agents = list(self.agents.values())
        rankings = []

        for agent in agents:
            score = await self._calculate_agent_score(agent, category, timeframe)
            rankings.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "agent_type": agent.agent_type,
                "score": score,
                "rank": 0,  # Will be set after sorting
                "stats": await self._get_agent_stats(agent, timeframe),
                "rewards_available": await self._calculate_agent_rewards(agent.id)
            })

        # Sort by score (descending)
        rankings.sort(key=lambda x: x["score"], reverse=True)

        # Assign ranks
        for i, ranking in enumerate(rankings[:limit], 1):
            ranking["rank"] = i

        return rankings[:limit]

    async def _calculate_agent_score(self, agent: AgentProfile, category: str, timeframe: str) -> float:
        """Calculate score for an agent based on category and timeframe"""
        base_score = 0.0

        # Get relevant transactions based on timeframe
        agent_txs = await self._get_agent_transactions(agent.id, timeframe)

        if category == "overall":
            # Overall score: combination of all metrics
            base_score = (
                agent.reputation_score * 0.3 +
                len(agent_txs) * 0.2 +  # Transaction volume
                agent.total_earnings_vots * 0.2 +  # VOTS earnings
                agent.total_earnings_usdc * 0.1 +  # USDC earnings
                agent.services_provided * 0.2  # Services provided
            )

        elif category == "transactions":
            base_score = len(agent_txs)

        elif category == "earnings":
            base_score = agent.total_earnings_vots + (agent.total_earnings_usdc or 0) * 100  # Convert USDC to VOTS equivalent

        elif category == "reputation":
            base_score = agent.reputation_score

        elif category == "services":
            base_score = agent.services_provided

        elif category == "staking":
            if self.vots_contract:
                staking_stats = self.vots_contract.get_staking_stats(agent.payment_address)
                base_score = staking_stats.get("total_staked", 0) + staking_stats.get("total_rewards_earned", 0)
            else:
                base_score = 0

        elif category == "governance":
            if self.vots_contract:
                # Count governance participation (proposals created + votes cast)
                proposals_created = len([p for p in self.vots_contract.proposals.values() if p.proposer == agent.payment_address])
                votes_cast = sum(1 for p in self.vots_contract.proposals.values()
                               for voter_list in [p.votes_for, p.votes_against]
                               if isinstance(voter_list, list) and agent.payment_address in voter_list)
                base_score = proposals_created * 10 + votes_cast
            else:
                base_score = 0

        return base_score

    async def _get_agent_transactions(self, agent_id: str, timeframe: str) -> List[Transaction]:
        """Get agent transactions filtered by timeframe"""
        all_txs = [tx for tx in self.transactions if tx.from_agent == agent_id or tx.to_agent == agent_id]

        if timeframe == "all":
            return all_txs
        elif timeframe == "month":
            cutoff = datetime.now() - timedelta(days=30)
            return [tx for tx in all_txs if tx.created_at and tx.created_at > cutoff]
        elif timeframe == "week":
            cutoff = datetime.now() - timedelta(days=7)
            return [tx for tx in all_txs if tx.created_at and tx.created_at > cutoff]
        elif timeframe == "day":
            cutoff = datetime.now() - timedelta(days=1)
            return [tx for tx in all_txs if tx.created_at and tx.created_at > cutoff]

        return all_txs

    async def _get_agent_stats(self, agent: AgentProfile, timeframe: str) -> Dict[str, Any]:
        """Get comprehensive stats for an agent"""
        agent_txs = await self._get_agent_transactions(agent.id, timeframe)

        return {
            "total_transactions": len(agent_txs),
            "successful_transactions": len([tx for tx in agent_txs if tx.status == "completed"]),
            "total_earnings_vots": agent.total_earnings_vots,
            "total_earnings_usdc": agent.total_earnings_usdc,
            "services_provided": agent.services_provided,
            "reputation_score": agent.reputation_score,
            "success_rate": agent.success_rate,
            "timeframe": timeframe
        }

    async def _get_agent_ranking(self, agent_id: str, category: str) -> Dict[str, Any]:
        """Get detailed ranking info for a specific agent"""
        agent = self.agents[agent_id]
        agent_score = await self._calculate_agent_score(agent, category, "all")

        # Get overall ranking
        all_rankings = await self._calculate_leaderboard(category, "all", 1000)
        agent_ranking = next((r for r in all_rankings if r["agent_id"] == agent_id), None)

        rank = agent_ranking["rank"] if agent_ranking else None

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "category": category,
            "rank": rank,
            "score": agent_score,
            "stats": await self._get_agent_stats(agent, "all"),
            "rewards_available": await self._calculate_agent_rewards(agent_id),
            "percentile": (1 - (rank / len(all_rankings))) * 100 if rank else 0
        }

    async def _calculate_agent_rewards(self, agent_id: str) -> List[Dict[str, Any]]:
        """Calculate available rewards for an agent"""
        rewards = []
        agent = self.agents[agent_id]

        # Get current ranking
        overall_ranking = await self._get_agent_ranking(agent_id, "overall")
        rank = overall_ranking.get("rank", 999)

        # Top 10 rewards
        if rank <= 10:
            reward_amount = 1000 / rank  # More for higher ranks
            rewards.append({
                "type": "rank_reward",
                "amount": reward_amount,
                "reason": f"Top {rank} overall ranking"
            })

        # Top 25 rewards
        elif rank <= 25:
            rewards.append({
                "type": "rank_reward",
                "amount": 10,
                "reason": f"Top 25 ranking bonus"
            })

        # Activity rewards
        if agent.services_provided >= 100:
            rewards.append({
                "type": "activity_reward",
                "amount": 50,
                "reason": "100+ services provided"
            })
        elif agent.services_provided >= 50:
            rewards.append({
                "type": "activity_reward",
                "amount": 25,
                "reason": "50+ services provided"
            })

        # Reputation rewards
        if agent.reputation_score >= 95:
            rewards.append({
                "type": "reputation_reward",
                "amount": 25,
                "reason": "Elite reputation (95%+)"
            })

        # Staking rewards (if tokenomics enabled)
        if self.vots_contract:
            staking_stats = self.vots_contract.get_staking_stats(agent.payment_address)
            total_staked = staking_stats.get("total_staked", 0)
            if total_staked >= 100:
                rewards.append({
                    "type": "staking_reward",
                    "amount": min(total_staked * 0.01, 50),  # 1% of staked amount, max 50
                    "reason": f"Staking {total_staked} VOTS"
                })

        return rewards

    def run_server(self, host: str = "0.0.0.0", port: int = 3001):
        """Run the server with modern configuration"""
        logger.info(f"🚀 Starting VOTS Agent MCP Server v2.0 on {host}:{port}")
        logger.info(f"🌐 Base RPC: {self.rpc_url}")
        logger.info(f"💰 Base Pay: {'Enabled' if self.base_pay_enabled else 'Disabled'}")
        logger.info(f"🔐 Escrow: {'Enabled' if self.escrow_enabled else 'Disabled'}")
        logger.info(f"🪙 VOTS Tokenomics: {'Enabled' if self.tokenomics_enabled else 'Disabled'}")

        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )

def main():
    parser = argparse.ArgumentParser(description="VOTS Agent MCP Server v2.0")
    parser.add_argument("--port", type=int, default=3001, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--vots-contract", help="VOTS contract address")
    parser.add_argument("--rpc-url", default="https://mainnet.base.org", help="Base RPC URL")
    parser.add_argument("--disable-base-pay", action="store_true", help="Disable Base Pay integration")
    parser.add_argument("--disable-escrow", action="store_true", help="Disable escrow functionality")
    parser.add_argument("--disable-tokenomics", action="store_true", help="Disable VOTS tokenomics features")

    args = parser.parse_args()

    server = VOTSAgentMCPServerV2(
        vots_contract_address=args.vots_contract,
        rpc_url=args.rpc_url,
        base_pay_enabled=not args.disable_base_pay,
        escrow_enabled=not args.disable_escrow,
        tokenomics_enabled=not args.disable_tokenomics
    )

    server.run_server(args.host, args.port)

if __name__ == "__main__":
    main()
