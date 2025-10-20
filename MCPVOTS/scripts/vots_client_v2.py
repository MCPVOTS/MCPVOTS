#!/usr/bin/env python3
"""
VOTS Agent Client Library v2.0

Modern Python client for interacting with the VOTS Agent MCP Server.
Supports Base Pay integration and real-time streaming.

Features:
- Async/await support for modern Python
- Base Pay USDC payments (3 lines of code)
- WebSocket streaming for real-time updates
- Automatic retry and error handling
- Service marketplace integration
- Agent reputation tracking

Usage:
    from vots_client_v2 import VOTSAgentClient

    async with VOTSAgentClient() as client:
        # Register agent
        agent_id = await client.register_agent(
            name="My Trading Agent",
            agent_type="trading",
            capabilities=["price_analysis", "market_data"],
            payment_address="0x..."
        )

        # Send payment
        await client.send_payment(
            to_agent="agent-123",
            amount_vots=0.1,
            service_type="analysis"
        )
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator, Union, Callable
import logging
from contextlib import asynccontextmanager
from enum import Enum
from dataclasses import dataclass

import aiohttp
try:
    import websockets
    from websockets.exceptions import ConnectionClosedError, WebSocketException
except ImportError:
    websockets = None
    ConnectionClosedError = Exception
    WebSocketException = Exception

# Environment and configuration
from dotenv import load_dotenv
import os
load_dotenv()

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

class VOTSClientError(Exception):
    """Base exception for VOTS client errors"""
    pass

class ConnectionError(VOTSClientError):
    """Connection-related errors"""
    pass

class ValidationError(VOTSClientError):
    """Data validation errors"""
    pass

class PaymentError(VOTSClientError):
    """Payment processing errors"""
    pass

@dataclass
class AgentInfo:
    id: str
    name: str
    agent_type: str
    capabilities: List[str]
    payment_address: str
    base_pay_enabled: bool
    status: str
    reputation_score: float
    total_earnings_vots: float
    total_earnings_usdc: float
    services_provided: int
    success_rate: float
    registered_at: str
    last_active: str
    metadata: Dict[str, Any]

@dataclass
class ServiceInfo:
    id: str
    agent_id: str
    name: str
    description: str
    price_vots: float
    price_usdc: Optional[float]
    service_type: str
    capabilities: List[str]
    delivery_time_minutes: int
    success_rate: float
    total_deliveries: int
    rating: float
    reviews: List[Dict[str, Any]]
    listed_at: str
    status: str

@dataclass
class TransactionInfo:
    id: str
    from_agent: Optional[str]
    to_agent: str
    amount_vots: float
    amount_usdc: Optional[float]
    payment_method: str
    service_type: str
    memo: Optional[str]
    status: str
    blockchain_tx: Optional[str]
    base_pay_id: Optional[str]
    escrow_id: Optional[str]
    created_at: str
    completed_at: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class EcosystemStats:
    total_agents: int
    active_agents: int
    total_services: int
    total_transactions: int
    completed_transactions: int
    success_rate: float
    total_volume_vots: float
    total_volume_usdc: float
    average_reputation: float
    active_connections: int
    timestamp: str

class VOTSAgentClient:
    """
    Modern async client for VOTS Agent MCP Server v2.0

    Supports:
    - Agent registration and management
    - Multi-method payments (VOTS, Base Pay USDC, Escrow)
    - Real-time WebSocket streaming
    - Service marketplace
    - Automatic retries and error handling
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3001",
        ws_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.base_url = base_url.rstrip('/')
        self.ws_url = ws_url or f"ws://localhost:3001/ws"
        self.api_key = api_key or os.getenv('VOTS_API_KEY')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None

        # WebSocket connection
        self.ws: Optional[Any] = None
        self.ws_connected = False

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Request headers
        self.headers = {'Content-Type': 'application/json'}
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establish HTTP session and optional WebSocket connection"""
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

        logger.info(f"Connected to VOTS server at {self.base_url}")

    async def disconnect(self):
        """Close all connections"""
        if self.ws and self.ws_connected:
            await self.ws.close()
            self.ws_connected = False

        if self.session:
            await self.session.close()
            self.session = None

        logger.info("Disconnected from VOTS server")

    async def connect_websocket(self):
        """Establish WebSocket connection for real-time updates"""
        if not self.session:
            raise ConnectionError("HTTP session not established. Call connect() first.")

        if websockets is None:
            raise ConnectionError("websockets package not installed")

        try:
            self.ws = await websockets.connect(
                self.ws_url,
                extra_headers=self.headers,
                close_timeout=self.timeout
            )
            self.ws_connected = True

            # Start message handler
            asyncio.create_task(self._handle_websocket_messages())

            logger.info(f"WebSocket connected to {self.ws_url}")

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise ConnectionError(f"Failed to connect WebSocket: {e}")

    async def _handle_websocket_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.ws_connected and self.ws:
                try:
                    message = await self.ws.recv()
                    data = json.loads(message)

                    # Handle different message types
                    if data.get('type') == 'welcome':
                        logger.info("WebSocket welcome received")
                    elif data.get('type') in self.event_handlers:
                        # Trigger event handlers
                        for handler in self.event_handlers[data['type']]:
                            try:
                                await handler(data['data'])
                            except Exception as e:
                                logger.error(f"Event handler error: {e}")
                    else:
                        logger.debug(f"Unhandled WebSocket message: {data}")

                except ConnectionClosedError:
                    logger.warning("WebSocket connection closed")
                    self.ws_connected = False
                    break

        except Exception as e:
            logger.error(f"WebSocket message handler error: {e}")
            self.ws_connected = False

    def on_event(self, event_type: str):
        """Decorator to register event handlers"""
        def decorator(func):
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(func)
            return func
        return decorator

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        if not self.session:
            raise ConnectionError("Client not connected. Use async context manager or call connect().")

        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                request_data = None
                if data:
                    request_data = json.dumps(data)

                async with self.session.request(
                    method,
                    url,
                    data=request_data,
                    params=params,
                    headers=self.headers
                ) as response:
                    response_data = await response.json()

                    if response.status >= 400:
                        error_msg = response_data.get('detail', f'HTTP {response.status}')
                        if response.status == 400:
                            raise ValidationError(error_msg)
                        elif response.status == 404:
                            raise VOTSClientError(f"Resource not found: {error_msg}")
                        else:
                            raise VOTSClientError(f"Server error: {error_msg}")

                    return response_data

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Request failed after {self.max_retries} attempts: {e}")

                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

    # Agent Management
    async def register_agent(
        self,
        name: str,
        agent_type: AgentType,
        capabilities: List[str],
        payment_address: str,
        base_pay_enabled: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new agent in the VOTS ecosystem

        Args:
            name: Agent name (2-100 characters)
            agent_type: Type of agent
            capabilities: List of agent capabilities
            payment_address: Ethereum address for payments
            base_pay_enabled: Enable Base Pay USDC payments
            metadata: Additional agent metadata

        Returns:
            Agent ID

        Raises:
            ValidationError: If agent data is invalid
            VOTSClientError: If registration fails
        """
        data = {
            "name": name,
            "agent_type": agent_type.value,
            "capabilities": capabilities,
            "payment_address": payment_address,
            "base_pay_enabled": base_pay_enabled,
            "metadata": metadata or {}
        }

        response = await self._make_request("POST", "/agents/register", data)
        return response["agent_id"]

    async def get_agent(self, agent_id: str) -> AgentInfo:
        """Get agent information"""
        response = await self._make_request("GET", f"/agents/{agent_id}")
        return AgentInfo(**response)

    async def list_agents(
        self,
        agent_type: Optional[AgentType] = None,
        capability: Optional[str] = None,
        min_reputation: float = 0.0,
        limit: int = 50
    ) -> List[AgentInfo]:
        """List agents with filtering"""
        params = {
            "agent_type": agent_type.value if agent_type else None,
            "capability": capability,
            "min_reputation": min_reputation,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request("GET", "/agents", params=params)
        return [AgentInfo(**agent) for agent in response["agents"]]

    # Payment Methods
    async def send_payment(
        self,
        to_agent: str,
        amount_vots: float,
        service_type: str,
        payment_method: PaymentMethod = PaymentMethod.VOTS_DIRECT,
        amount_usdc: Optional[float] = None,
        memo: Optional[str] = None,
        escrow_enabled: bool = False,
        from_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Send payment to another agent

        Args:
            to_agent: Recipient agent ID
            amount_vots: Amount in VOTS tokens (max 1.0 per transaction)
            service_type: Type of service being paid for
            payment_method: Payment method to use
            amount_usdc: USDC amount for Base Pay (optional)
            memo: Payment memo
            escrow_enabled: Use escrow for this payment
            from_agent: Sender agent ID (optional)
            metadata: Additional payment metadata

        Returns:
            Transaction ID

        Raises:
            PaymentError: If payment fails
            ValidationError: If payment data is invalid
        """
        if amount_vots > 1.0:
            raise ValidationError("Maximum 1 VOTS per transaction")

        data = {
            "to_agent": to_agent,
            "amount_vots": amount_vots,
            "service_type": service_type,
            "payment_method": payment_method.value,
            "amount_usdc": amount_usdc,
            "memo": memo,
            "escrow_enabled": escrow_enabled,
            "metadata": metadata or {}
        }

        if from_agent:
            data["metadata"]["from_agent"] = from_agent

        try:
            response = await self._make_request("POST", "/payments/send", data)
            return response["transaction_id"]
        except Exception as e:
            raise PaymentError(f"Payment failed: {e}")

    async def get_payment_history(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[TransactionInfo]:
        """Get payment transaction history"""
        params = {
            "agent_id": agent_id,
            "status": status,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request("GET", "/payments/history", params=params)
        return [TransactionInfo(**tx) for tx in response["transactions"]]

    # Base Pay Integration (Simplified)
    async def send_base_pay_usdc(
        self,
        to_agent: str,
        amount_usdc: float,
        service_type: str,
        memo: Optional[str] = None,
        from_agent: Optional[str] = None
    ) -> str:
        """
        Send USDC payment using Base Pay (3 lines of code!)

        This demonstrates the simplicity of Base Pay integration.
        In production, this would use the actual @base-org/account SDK.
        """
        return await self.send_payment(
            to_agent=to_agent,
            amount_vots=0.0,  # No VOTS needed for Base Pay
            amount_usdc=amount_usdc,
            service_type=service_type,
            payment_method=PaymentMethod.BASE_PAY_USDC,
            memo=memo,
            from_agent=from_agent
        )

    # Service Marketplace
    async def list_service(
        self,
        agent_id: str,
        name: str,
        description: str,
        price_vots: float,
        service_type: str,
        capabilities: List[str],
        price_usdc: Optional[float] = None,
        delivery_time_minutes: int = 60
    ) -> str:
        """List a service in the marketplace"""
        data = {
            "name": name,
            "description": description,
            "price_vots": price_vots,
            "price_usdc": price_usdc,
            "service_type": service_type,
            "capabilities": capabilities,
            "delivery_time_minutes": delivery_time_minutes
        }

        response = await self._make_request("POST", f"/services?agent_id={agent_id}", data)
        return response["service_id"]

    async def get_services(
        self,
        service_type: Optional[str] = None,
        capability: Optional[str] = None,
        max_price_vots: Optional[float] = None,
        limit: int = 50
    ) -> List[ServiceInfo]:
        """Get available services"""
        params = {
            "service_type": service_type,
            "capability": capability,
            "max_price_vots": max_price_vots,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request("GET", "/services", params=params)
        return [ServiceInfo(**service) for service in response["services"]]

    # Real-time Streaming
    async def stream_transactions(self) -> AsyncGenerator[TransactionInfo, None]:
        """Stream transaction events in real-time"""
        if not self.session:
            raise ConnectionError("Client not connected")

        async with self.session.get(f"{self.base_url}/stream/transactions") as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if data.get('type') == 'transaction':
                        yield TransactionInfo(**data)

    # Ecosystem Analytics
    async def get_ecosystem_stats(self) -> EcosystemStats:
        """Get comprehensive ecosystem statistics"""
        response = await self._make_request("GET", "/stats/ecosystem")
        return EcosystemStats(**response)

    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Check server health and capabilities"""
        return await self._make_request("GET", "/health")

    # Leaderboard System
    async def get_leaderboard(
        self,
        category: str = "overall",
        timeframe: str = "all",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get leaderboard rankings for MCPVOTS users

        Args:
            category: Ranking category ("overall", "transactions", "earnings", "reputation", "services", "staking", "governance")
            timeframe: Time period ("all", "month", "week", "day")
            limit: Maximum number of results to return

        Returns:
            Dict containing leaderboard data
        """
        params = {
            "category": category,
            "timeframe": timeframe,
            "limit": limit
        }

        return await self._make_request("GET", "/leaderboard", params=params)

    async def get_agent_rank(
        self,
        agent_id: str,
        category: str = "overall"
    ) -> Dict[str, Any]:
        """
        Get specific agent's ranking and stats

        Args:
            agent_id: ID of the agent to get ranking for
            category: Ranking category

        Returns:
            Dict containing agent's ranking data
        """
        params = {"category": category}

        return await self._make_request("GET", f"/leaderboard/{agent_id}/rank", params=params)

    async def claim_leaderboard_rewards(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Claim leaderboard rewards for an agent

        Args:
            agent_id: ID of the agent claiming rewards

        Returns:
            Dict containing reward claim results
        """
        return await self._make_request("POST", f"/leaderboard/claim-rewards/{agent_id}")

    async def get_leaderboard_categories(self) -> List[str]:
        """
        Get available leaderboard categories

        Returns:
            List of available ranking categories
        """
        return [
            "overall",
            "transactions",
            "earnings",
            "reputation",
            "services",
            "staking",
            "governance"
        ]

    async def get_leaderboard_timeframes(self) -> List[str]:
        """
        Get available leaderboard timeframes

        Returns:
            List of available time periods
        """
        return ["all", "month", "week", "day"]

    # Unique Data Offerings - What Makes MCPVOTS Stand Out
    async def get_base_network_insights(self) -> Dict[str, Any]:
        """
        Get real-time Base network analytics and insights

        Returns:
            Dict containing network health metrics, gas prices, TPS, etc.
        """
        return await self._make_request("GET", "/data/base-network-insights")

    async def get_agent_performance_analytics(
        self,
        agent_type: Optional[str] = None,
        timeframe: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get advanced agent performance analytics and insights

        Args:
            agent_type: Filter by agent type (optional)
            timeframe: Analysis timeframe ("1d", "7d", "30d")

        Returns:
            Dict containing performance analytics for agents
        """
        params = {"timeframe": timeframe}
        if agent_type:
            params["agent_type"] = agent_type

        return await self._make_request("GET", "/data/agent-performance-analytics", params=params)

    async def get_market_intelligence(self) -> Dict[str, Any]:
        """
        Get AI-powered market intelligence for agents and users

        Returns:
            Dict containing service demand analysis, market opportunities, and price insights
        """
        return await self._make_request("GET", "/data/market-intelligence")

    async def get_social_sentiment_analysis(self) -> Dict[str, Any]:
        """
        Get on-chain social sentiment analysis from agent interactions

        Returns:
            Dict containing sentiment scores, reputation trends, and community health
        """
        return await self._make_request("GET", "/data/social-sentiment-analysis")

    async def get_predictive_analytics(self) -> Dict[str, Any]:
        """
        Get AI-powered predictive analytics for agent behavior and market trends

        Returns:
            Dict containing demand predictions, performance forecasts, and market opportunities
        """
        return await self._make_request("GET", "/data/predictive-analytics")

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get comprehensive economic indicators for the VOTS ecosystem

        Returns:
            Dict containing ecosystem economics, token metrics, and market indicators
        """
        return await self._make_request("GET", "/data/economic-indicators")

    async def get_agent_discovery(
        self,
        user_type: str = "human",
        preferences: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get smart agent discovery with personalized recommendations

        Args:
            user_type: Type of user ("human" or "agent")
            preferences: User preferences for filtering

        Returns:
            Dict containing personalized agent and service recommendations
        """
        params = {"user_type": user_type}
        if preferences:
            params["preferences"] = preferences

        return await self._make_request("GET", "/data/agent-discovery", params=params)# Convenience functions for quick usage
async def quick_register_agent(
    name: str,
    agent_type: AgentType,
    capabilities: List[str],
    payment_address: str,
    base_url: str = "http://localhost:3001"
) -> str:
    """Quick agent registration (no context manager needed)"""
    async with VOTSAgentClient(base_url=base_url) as client:
        return await client.register_agent(name, agent_type, capabilities, payment_address)

async def quick_send_payment(
    to_agent: str,
    amount_vots: float,
    service_type: str,
    base_url: str = "http://localhost:3001"
) -> str:
    """Quick payment sending"""
    async with VOTSAgentClient(base_url=base_url) as client:
        return await client.send_payment(to_agent, amount_vots, service_type)

async def quick_base_pay_usdc(
    to_agent: str,
    amount_usdc: float,
    service_type: str,
    base_url: str = "http://localhost:3001"
) -> str:
    """Quick Base Pay USDC payment (3 lines of code!)"""
    async with VOTSAgentClient(base_url=base_url) as client:
        return await client.send_base_pay_usdc(to_agent, amount_usdc, service_type)

# Example usage and testing
async def example_usage():
    """Example of how to use the VOTS client"""
    async with VOTSAgentClient() as client:
        try:
            # Register an agent
            agent_id = await client.register_agent(
                name="Example Trading Agent",
                agent_type=AgentType.TRADING,
                capabilities=["price_analysis", "market_data", "trading_signals"],
                payment_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                base_pay_enabled=True
            )
            print(f"Agent registered: {agent_id}")

            # Send a Base Pay USDC payment (3 lines!)
            tx_id = await client.send_base_pay_usdc(
                to_agent="some-other-agent-id",
                amount_usdc=1.0,
                service_type="analysis"
            )
            print(f"Base Pay transaction: {tx_id}")

            # List available services
            services = await client.get_services(service_type="analysis", limit=10)
            print(f"Found {len(services)} analysis services")

            # Get ecosystem stats
            stats = await client.get_ecosystem_stats()
            print(f"Ecosystem: {stats.total_agents} agents, {stats.total_transactions} transactions")

            # Get leaderboard rankings
            leaderboard = await client.get_leaderboard(category="overall", limit=10)
            print(f"Top 10 agents: {len(leaderboard['leaderboard'])} ranked")

            # Get agent's rank
            agent_rank = await client.get_agent_rank(agent_id)
            print(f"Agent rank: #{agent_rank.get('rank', 'Unranked')} in {agent_rank.get('category')}")

            # Check for available rewards
            if agent_rank.get('rewards_available'):
                rewards = await client.claim_leaderboard_rewards(agent_id)
                print(f"Claimed {rewards.get('rewards_claimed', 0)} VOTS in rewards")

            # Get unique MCPVOTS data offerings
            print("\n🔥 MCPVOTS EXCLUSIVE DATA OFFERINGS")
            print("=" * 50)

            # Base network insights
            network_insights = await client.get_base_network_insights()
            print(f"🌐 Base Network: Block {network_insights.get('current_block', 'N/A')}, "
                  f"Gas {network_insights.get('gas_price_gwei', 0):.1f} gwei, "
                  f"TPS {network_insights.get('average_tps', 0):.1f}")

            # Agent performance analytics
            performance_analytics = await client.get_agent_performance_analytics()
            top_performers = performance_analytics.get('analytics', [])[:3]
            print(f"📊 Top Performing Agents:")
            for i, agent in enumerate(top_performers, 1):
                print(f"  {i}. {agent.get('agent_name', 'Unknown')}: {agent.get('performance_score', 0):.1f}%")

            # Market intelligence
            market_intel = await client.get_market_intelligence()
            opportunities = market_intel.get('market_opportunities', [])
            if opportunities:
                print(f"💡 Market Opportunity: {opportunities[0].get('description', 'N/A')}")

            # Social sentiment
            sentiment = await client.get_social_sentiment_analysis()
            print(f"😊 Community Sentiment: {sentiment.get('sentiment_score', 0):.1f}% - "
                  f"{sentiment.get('community_health', {}).get('overall_sentiment', 'unknown')}")

            # Predictive analytics
            predictions = await client.get_predictive_analytics()
            forecast = predictions.get('market_forecast', {})
            print(f"🔮 Market Forecast: {forecast.get('overall_growth', 'N/A')} growth expected")

            # Economic indicators
            economics = await client.get_economic_indicators()
            ecosystem = economics.get('ecosystem_economics', {})
            print(f"💰 Ecosystem: {ecosystem.get('total_agents', 0)} agents, "
                  f"${ecosystem.get('total_transaction_volume_usdc', 0):.2f} USDC volume")

            # Smart agent discovery
            discovery = await client.get_agent_discovery(user_type="human")
            recommendations = discovery.get('personalized_recommendations', [])
            if recommendations:
                print(f"🎯 Recommended Agent: {recommendations[0].get('agent_name', 'N/A')} - "
                      f"{recommendations[0].get('why_recommended', 'N/A')}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
