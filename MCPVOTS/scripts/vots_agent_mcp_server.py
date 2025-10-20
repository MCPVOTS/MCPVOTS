#!/usr/bin/env python3
"""
VOTS Agent MCP Server

Model Context Protocol server that enables AI agents and LLMs to discover,
register, and interact with the VOTS token ecosystem for micro-payments and
bot services.

Features:
- Agent registration and management
- Micro-payment processing
- Real-time streaming of transactions
- Bot service marketplace
- Reputation and reward system

Usage:
    python vots_agent_mcp_server.py --port 3001 --vots-contract 0x...
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys
import argparse
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import websockets
from web3 import Web3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRegistration(BaseModel):
    name: str
    agent_type: str  # trading, analysis, utility, etc.
    capabilities: List[str]
    payment_address: str
    metadata: Optional[Dict[str, Any]] = None

class PaymentRequest(BaseModel):
    to_agent: str
    amount_vots: float
    service_type: str
    memo: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ServiceListing(BaseModel):
    name: str
    description: str
    price_vots: float
    service_type: str
    capabilities: List[str]
    metadata: Optional[Dict[str, Any]] = None

class VOTSAgentMCPServer:
    def __init__(self, vots_contract_address: str, rpc_url: str = "https://mainnet.base.org"):
        self.app = FastAPI(title="VOTS Agent MCP Server", version="1.0.0")

        # Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.vots_contract_address = self.w3.to_checksum_address(vots_contract_address)

        # Agent registry
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_stats: Dict[str, Dict[str, Any]] = {}

        # Active connections for streaming
        self.active_connections: List[websockets.WebSocketServerProtocol] = []

        # Service marketplace
        self.services: Dict[str, Dict[str, Any]] = {}
        self.service_requests: Dict[str, Dict[str, Any]] = {}

        # Transaction history
        self.transactions: List[Dict[str, Any]] = []

        self.setup_routes()

    def setup_routes(self):
        """Set up all API routes"""

        @self.app.post("/agents/register")
        async def register_agent(registration: AgentRegistration):
            """Register a new agent in the VOTS ecosystem"""
            agent_id = str(uuid.uuid4())

            agent_data = {
                "id": agent_id,
                "name": registration.name,
                "type": registration.agent_type,
                "capabilities": registration.capabilities,
                "payment_address": registration.payment_address,
                "metadata": registration.metadata or {},
                "registered_at": datetime.now().isoformat(),
                "status": "active",
                "reputation_score": 100,  # Start with neutral reputation
                "total_earnings_vots": 0.0,
                "services_provided": 0,
                "success_rate": 100.0
            }

            self.agents[agent_id] = agent_data
            self.agent_stats[agent_id] = {
                "total_transactions": 0,
                "successful_payments": 0,
                "failed_payments": 0,
                "services_completed": 0,
                "reputation_history": [100]
            }

            logger.info(f"Agent registered: {agent_id} - {registration.name}")

            # Broadcast new agent to streams
            await self.broadcast_event("agent_registered", agent_data)

            return {"agent_id": agent_id, "status": "registered"}

        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent information"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")

            return self.agents[agent_id]

        @self.app.get("/agents")
        async def list_agents(agent_type: Optional[str] = None, capability: Optional[str] = None):
            """List all registered agents with optional filtering"""
            agents = list(self.agents.values())

            if agent_type:
                agents = [a for a in agents if a["type"] == agent_type]

            if capability:
                agents = [a for a in agents if capability in a["capabilities"]]

            return {"agents": agents, "total": len(agents)}

        @self.app.post("/payments/send")
        async def send_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
            """Send a VOTS micro-payment"""
            from_agent = payment.metadata.get("from_agent") if payment.metadata else None

            if not from_agent or from_agent not in self.agents:
                raise HTTPException(status_code=400, detail="Invalid from_agent")

            if payment.to_agent not in self.agents:
                raise HTTPException(status_code=404, detail="Recipient agent not found")

            # Validate payment amount
            if payment.amount_vots <= 0 or payment.amount_vots > 1.0:  # Max 1 VOTS per transaction
                raise HTTPException(status_code=400, detail="Invalid payment amount")

            # Create transaction record
            transaction = {
                "id": str(uuid.uuid4()),
                "from_agent": from_agent,
                "to_agent": payment.to_agent,
                "amount_vots": payment.amount_vots,
                "service_type": payment.service_type,
                "memo": payment.memo,
                "timestamp": datetime.now().isoformat(),
                "status": "processing",
                "blockchain_tx": None
            }

            self.transactions.append(transaction)

            # Update agent stats
            self.agent_stats[from_agent]["total_transactions"] += 1
            self.agents[payment.to_agent]["total_earnings_vots"] += payment.amount_vots

            # Process payment asynchronously
            background_tasks.add_task(self.process_payment, transaction)

            logger.info(f"Payment initiated: {payment.amount_vots} VOTS from {from_agent} to {payment.to_agent}")

            return {
                "transaction_id": transaction["id"],
                "status": "processing",
                "estimated_completion": "30 seconds"
            }

        @self.app.get("/payments/history")
        async def get_payment_history(agent_id: Optional[str] = None, limit: int = 50):
            """Get payment history"""
            history = self.transactions[-limit:]  # Most recent first

            if agent_id:
                history = [tx for tx in history if tx["from_agent"] == agent_id or tx["to_agent"] == agent_id]

            return {"transactions": history, "total": len(history)}

        @self.app.get("/stream/transactions")
        async def stream_transactions():
            """Server-Sent Events stream for transactions"""
            async def event_generator():
                # Send recent transactions
                recent_txs = self.transactions[-10:]  # Last 10 transactions
                for tx in recent_txs:
                    yield f"data: {json.dumps(tx)}\n\n"
                    await asyncio.sleep(0.1)

                # Keep connection alive
                while True:
                    await asyncio.sleep(30)
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )

        @self.app.post("/market/services")
        async def list_service(service: ServiceListing, agent_id: str):
            """List a service in the marketplace"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")

            service_id = str(uuid.uuid4())

            service_data = {
                "id": service_id,
                "agent_id": agent_id,
                "name": service.name,
                "description": service.description,
                "price_vots": service.price_vots,
                "service_type": service.service_type,
                "capabilities": service.capabilities,
                "metadata": service.metadata or {},
                "listed_at": datetime.now().isoformat(),
                "status": "active",
                "reviews": [],
                "rating": 0.0,
                "total_requests": 0
            }

            self.services[service_id] = service_data

            logger.info(f"Service listed: {service.name} by agent {agent_id}")

            # Broadcast to streams
            await self.broadcast_event("service_listed", service_data)

            return {"service_id": service_id, "status": "listed"}

        @self.app.get("/market/services")
        async def get_services(service_type: Optional[str] = None, capability: Optional[str] = None):
            """Get available services"""
            services = list(self.services.values())

            if service_type:
                services = [s for s in services if s["service_type"] == service_type]

            if capability:
                services = [s for s in services if capability in s["capabilities"]]

            return {"services": services, "total": len(services)}

        @self.app.post("/market/request/{service_id}")
        async def request_service(service_id: str, request_data: Dict[str, Any], from_agent: str):
            """Request a service from the marketplace"""
            if service_id not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")

            if from_agent not in self.agents:
                raise HTTPException(status_code=400, detail="Invalid requesting agent")

            service = self.services[service_id]
            request_id = str(uuid.uuid4())

            service_request = {
                "id": request_id,
                "service_id": service_id,
                "from_agent": from_agent,
                "to_agent": service["agent_id"],
                "price_vots": service["price_vots"],
                "parameters": request_data,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }

            self.service_requests[request_id] = service_request

            logger.info(f"Service requested: {service_id} by agent {from_agent}")

            return {"request_id": request_id, "status": "pending"}

        @self.app.get("/stats/ecosystem")
        async def get_ecosystem_stats():
            """Get ecosystem-wide statistics"""
            total_agents = len(self.agents)
            total_services = len(self.services)
            total_transactions = len(self.transactions)

            # Calculate volume
            daily_volume = sum(
                tx["amount_vots"] for tx in self.transactions
                if datetime.fromisoformat(tx["timestamp"]) > datetime.now() - timedelta(days=1)
            )

            # Calculate burn rate (simplified)
            burn_rate = 0.01  # 0.01% from contract

            return {
                "total_agents": total_agents,
                "total_services": total_services,
                "total_transactions": total_transactions,
                "daily_volume_vots": daily_volume,
                "burn_rate_percent": burn_rate,
                "active_bots": len([a for a in self.agents.values() if a["status"] == "active"]),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agents_registered": len(self.agents),
                "services_listed": len(self.services)
            }

    async def process_payment(self, transaction: Dict[str, Any]):
        """Process a payment transaction (simplified - would integrate with actual blockchain)"""
        try:
            # Simulate blockchain interaction delay
            await asyncio.sleep(2)

            # In real implementation, this would:
            # 1. Check VOTS balance
            # 2. Execute microPayment on contract
            # 3. Wait for confirmation
            # 4. Update transaction status

            transaction["status"] = "completed"
            transaction["blockchain_tx"] = f"0x{uuid.uuid4().hex}"  # Mock tx hash

            # Update agent stats
            from_agent = transaction["from_agent"]
            to_agent = transaction["to_agent"]

            self.agent_stats[from_agent]["successful_payments"] += 1
            self.agent_stats[to_agent]["services_provided"] += 1

            # Broadcast completion
            await self.broadcast_event("payment_completed", transaction)

            logger.info(f"Payment completed: {transaction['id']}")

        except Exception as e:
            transaction["status"] = "failed"
            transaction["error"] = str(e)

            from_agent = transaction["from_agent"]
            self.agent_stats[from_agent]["failed_payments"] += 1

            await self.broadcast_event("payment_failed", transaction)

            logger.error(f"Payment failed: {transaction['id']} - {e}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all connected streaming clients"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        # In a real implementation, you'd maintain WebSocket connections
        # and broadcast to them. For now, we'll just log the event.
        logger.info(f"Broadcasting event: {event_type}")

    def run_server(self, host: str = "0.0.0.0", port: int = 3001):
        """Run the MCP server"""
        logger.info(f"Starting VOTS Agent MCP Server on {host}:{port}")
        logger.info(f"VOTS Contract: {self.vots_contract_address}")

        uvicorn.run(self.app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="VOTS Agent MCP Server")
    parser.add_argument("--port", type=int, default=3001, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--vots-contract", required=True, help="VOTS contract address")
    parser.add_argument("--rpc-url", default="https://mainnet.base.org", help="Base RPC URL")

    args = parser.parse_args()

    server = VOTSAgentMCPServer(args.vots_contract, args.rpc_url)
    server.run_server(args.host, args.port)

if __name__ == "__main__":
    main()
