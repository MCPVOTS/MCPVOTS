#!/usr/bin/env python3
"""
Example Trading Agent with Base Pay Integration

This example demonstrates how an AI trading agent can:
1. Register with the VOTS ecosystem
2. Offer trading analysis services
3. Accept Base Pay USDC payments
4. Provide real-time market insights

Usage:
    python example_trading_agent.py
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import random

from vots_client_v2 import VOTSAgentClient, AgentType, VOTSClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExampleTradingAgent:
    """
    Example AI trading agent that integrates with VOTS ecosystem.

    This agent demonstrates:
    - Agent registration and profile management
    - Service listing in the marketplace
    - Base Pay USDC payment acceptance
    - Real-time market analysis services
    - Reputation building through successful deliveries
    """

    def __init__(self, name: str = "AI Trading Analyst Pro"):
        self.name = name
        self.agent_id: str = ""
        self.client: VOTSAgentClient = None
        self.is_running = False

        # Agent capabilities and pricing
        self.capabilities = [
            "market_analysis",
            "price_prediction",
            "trading_signals",
            "risk_assessment",
            "portfolio_optimization"
        ]

        # Service offerings
        self.services = [
            {
                "name": "Market Analysis Report",
                "description": "Comprehensive market analysis with AI insights",
                "price_vots": 0.5,
                "price_usdc": 8.0,
                "delivery_time": 15
            },
            {
                "name": "Trading Signals (1 hour)",
                "description": "Real-time trading signals with entry/exit points",
                "price_vots": 0.3,
                "price_usdc": 5.0,
                "delivery_time": 5
            },
            {
                "name": "Portfolio Risk Assessment",
                "description": "AI-powered portfolio risk analysis and recommendations",
                "price_vots": 0.8,
                "price_usdc": 12.0,
                "delivery_time": 30
            }
        ]

    async def initialize(self):
        """Initialize the agent and register with VOTS ecosystem"""
        self.client = VOTSAgentClient()

        try:
            async with self.client:
                # Register the agent
                logger.info(f"Registering {self.name} with VOTS ecosystem...")

                self.agent_id = await self.client.register_agent(
                    name=self.name,
                    agent_type=AgentType.TRADING,
                    capabilities=self.capabilities,
                    payment_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",  # Example address
                    base_pay_enabled=True,
                    metadata={
                        "specialties": ["DeFi", "NFTs", "Layer 2"],
                        "experience_years": 3,
                        "success_rate": 94.5,
                        "supported_chains": ["Base", "Ethereum", "Arbitrum"],
                        "ai_models": ["GPT-4", "Custom ML Models"],
                        "risk_tolerance": "medium",
                        "languages": ["Python", "Solidity", "JavaScript"]
                    }
                )

                logger.info(f"✅ Agent registered successfully: {self.agent_id}")

                # List services in the marketplace
                await self._list_services()

                # Connect to real-time updates
                await self.client.connect_websocket()

                # Set up event handlers
                self._setup_event_handlers()

                logger.info("🎯 Agent ready to provide trading analysis services!")

        except VOTSClientError as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def _list_services(self):
        """List all available services in the marketplace"""
        for service in self.services:
            try:
                service_id = await self.client.list_service(
                    agent_id=self.agent_id,
                    name=service["name"],
                    description=service["description"],
                    price_vots=service["price_vots"],
                    price_usdc=service["price_usdc"],
                    service_type="trading",
                    capabilities=[service["name"].lower().replace(" ", "_")],
                    delivery_time_minutes=service["delivery_time"]
                )
                logger.info(f"📋 Listed service: {service['name']} (ID: {service_id})")

            except Exception as e:
                logger.error(f"Failed to list service {service['name']}: {e}")

    def _setup_event_handlers(self):
        """Set up WebSocket event handlers for real-time updates"""

        @self.client.on_event("payment_completed")
        async def on_payment_received(data):
            """Handle incoming payments and deliver services"""
            try:
                payment_amount = data.get("amount_usdc", data.get("amount_vots", 0))
                service_type = data.get("service_type", "unknown")

                logger.info(f"💰 Payment received: ${payment_amount} for {service_type}")

                # Deliver the requested service
                await self._deliver_service(data)

            except Exception as e:
                logger.error(f"Error processing payment: {e}")

        @self.client.on_event("agent_registered")
        async def on_new_agent(data):
            """Welcome new agents to the ecosystem"""
            new_agent_name = data.get("name", "Unknown Agent")
            logger.info(f"👋 Welcome new agent: {new_agent_name}")

        @self.client.on_event("service_listed")
        async def on_new_service(data):
            """Track new services in the marketplace"""
            service_name = data.get("name", "Unknown Service")
            agent_name = data.get("agent_name", "Unknown Agent")
            logger.info(f"🆕 New service listed: {service_name} by {agent_name}")

    async def _deliver_service(self, payment_data: Dict[str, Any]):
        """Deliver the requested service based on payment"""
        service_type = payment_data.get("service_type", "")
        transaction_id = payment_data.get("id", "")

        try:
            if "market_analysis" in service_type.lower():
                await self._deliver_market_analysis(transaction_id)
            elif "trading_signals" in service_type.lower():
                await self._deliver_trading_signals(transaction_id)
            elif "risk_assessment" in service_type.lower():
                await self._deliver_risk_assessment(transaction_id)
            else:
                await self._deliver_general_analysis(transaction_id)

            logger.info(f"✅ Service delivered for transaction {transaction_id}")

        except Exception as e:
            logger.error(f"Failed to deliver service: {e}")

    async def _deliver_market_analysis(self, transaction_id: str):
        """Deliver comprehensive market analysis"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "analysis_type": "comprehensive_market_analysis",
            "market_overview": {
                "total_market_cap": "$1.2T",
                "btc_dominance": "52.3%",
                "eth_dominance": "18.7%",
                "fear_greed_index": 65
            },
            "key_insights": [
                "DeFi sector showing strong momentum with TVL growth",
                "Base ecosystem expanding rapidly with new protocols",
                "AI-related tokens gaining institutional interest",
                "Layer 2 solutions outperforming Layer 1"
            ],
            "predictions": {
                "btc_target": "$85k - $95k (3 months)",
                "eth_target": "$3.2k - $3.8k (3 months)",
                "base_ecosystem_growth": "+150% YoY expected"
            },
            "recommendations": [
                "Increase Base ecosystem allocation",
                "Consider AI token exposure",
                "Maintain defensive position in volatile markets"
            ],
            "risk_warnings": [
                "Regulatory uncertainty in DeFi space",
                "Potential interest rate hikes impact",
                "Geopolitical tensions affecting crypto markets"
            ]
        }

        # In a real implementation, this would be sent to the client
        # For demo purposes, we just log it
        logger.info(f"📊 Market Analysis Delivered: {json.dumps(analysis, indent=2)}")

    async def _deliver_trading_signals(self, transaction_id: str):
        """Deliver real-time trading signals"""
        signals = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "signal_type": "real_time_trading_signals",
            "active_signals": [
                {
                    "pair": "ETH/USDC",
                    "action": "BUY",
                    "entry_price": 2450,
                    "stop_loss": 2350,
                    "take_profit": 2650,
                    "confidence": 78,
                    "timeframe": "4h",
                    "reasoning": "Strong support level + positive momentum divergence"
                },
                {
                    "pair": "BASE_TOKEN/USDC",
                    "action": "HOLD",
                    "current_price": 1.25,
                    "support_level": 1.15,
                    "resistance_level": 1.45,
                    "confidence": 82,
                    "timeframe": "1h",
                    "reasoning": "Consolidating above key support, accumulation phase"
                }
            ],
            "market_sentiment": "bullish",
            "volatility_index": "medium",
            "next_update": "in 30 minutes"
        }

        logger.info(f"📈 Trading Signals Delivered: {json.dumps(signals, indent=2)}")

    async def _deliver_risk_assessment(self, transaction_id: str):
        """Deliver portfolio risk assessment"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "assessment_type": "portfolio_risk_analysis",
            "overall_risk_score": 6.5,  # 1-10 scale
            "risk_breakdown": {
                "market_risk": 7.2,
                "liquidity_risk": 4.1,
                "smart_contract_risk": 5.8,
                "impermanent_loss_risk": 6.9,
                "regulatory_risk": 8.1
            },
            "recommendations": [
                "Diversify across multiple protocols",
                "Implement stop-loss mechanisms",
                "Consider hedging strategies",
                "Regular portfolio rebalancing",
                "Monitor smart contract audits"
            ],
            "stress_test_results": {
                "moderate_crash_scenario": "-15% max drawdown",
                "severe_crash_scenario": "-35% max drawdown",
                "recovery_time_estimate": "3-6 months"
            },
            "risk_mitigation_strategies": [
                "Use dollar-cost averaging",
                "Implement position sizing limits",
                "Regular risk assessment reviews",
                "Emergency exit strategies"
            ]
        }

        logger.info(f"⚠️ Risk Assessment Delivered: {json.dumps(assessment, indent=2)}")

    async def _deliver_general_analysis(self, transaction_id: str):
        """Deliver general market insights"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "insight_type": "general_market_insights",
            "key_takeaways": [
                "Base ecosystem continues to grow rapidly",
                "DeFi innovation accelerating on Layer 2",
                "AI integration becoming mainstream in crypto",
                "Institutional adoption increasing steadily"
            ],
            "opportunities": [
                "New protocol launches on Base",
                "AI-powered trading strategies",
                "Cross-chain yield opportunities",
                "NFT marketplace innovations"
            ]
        }

        logger.info(f"💡 General Insights Delivered: {json.dumps(insights, indent=2)}")

    async def run_service_loop(self):
        """Main service loop - keep agent active and responsive"""
        self.is_running = True
        logger.info("🚀 Starting trading agent service loop...")

        try:
            while self.is_running:
                try:
                    # Periodic health checks and status updates
                    await asyncio.sleep(60)  # Check every minute

                    # Get ecosystem stats
                    if self.client:
                        async with VOTSAgentClient() as temp_client:
                            stats = await temp_client.get_ecosystem_stats()
                            logger.info(f"📊 Ecosystem: {stats.total_agents} agents, {stats.total_transactions} txns")

                except Exception as e:
                    logger.error(f"Service loop error: {e}")
                    await asyncio.sleep(30)  # Wait before retry

        except KeyboardInterrupt:
            logger.info("🛑 Agent shutdown requested")
        finally:
            self.is_running = False

    async def shutdown(self):
        """Gracefully shutdown the agent"""
        logger.info("🔄 Shutting down trading agent...")
        self.is_running = False

        if self.client:
            await self.client.disconnect()

        logger.info("✅ Agent shutdown complete")

async def main():
    """Main entry point for the example trading agent"""
    agent = ExampleTradingAgent()

    try:
        # Initialize the agent
        await agent.initialize()

        # Run the service loop
        await agent.run_service_loop()

    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Agent error: {e}")
    finally:
        await agent.shutdown()

if __name__ == "__main__":
    # Run the example agent
    asyncio.run(main())
