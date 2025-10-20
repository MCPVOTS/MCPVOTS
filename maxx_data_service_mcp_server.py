#!/usr/bin/env python3
"""
MAXX Data Service MCP Server
Provides agent-friendly data services with MAXX token payments
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import mcp.server.stdio

# Web3 imports for MAXX token interactions
from web3 import Web3
import requests

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check for mock mode
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'

# Import config
try:
    from standalone_config import *
    PRIVATE_KEY = ETHEREUM_PRIVATE_KEY  # Map to expected variable name
    DATA_SERVICE_CONTRACT = os.getenv('DATA_SERVICE_CONTRACT', '0x0000000000000000000000000000000000000000')
except ImportError:
    # Default config
    PROVIDER_URL = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
    MAXX_TOKEN_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'
    PRIVATE_KEY = os.getenv('ETHEREUM_PRIVATE_KEY')
    DATA_SERVICE_CONTRACT = os.getenv('DATA_SERVICE_CONTRACT', '0x0000000000000000000000000000000000000000')  # Deploy first

class MAXXDataServiceServer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
        self.account = None
        self.maxx_contract = None
        self.data_contract = None

        # Initialize contracts
        self._init_contracts()

    def _init_contracts(self):
        """Initialize Web3 contracts"""
        try:
            if PRIVATE_KEY:
                self.account = self.w3.eth.account.from_key(PRIVATE_KEY)

            # MAXX token contract (for burning)
            maxx_abi = [
                {"inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                 "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                 "stateMutability": "view", "type": "function"},
                {"inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
                 "name": "burn", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                           {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                 "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                 "stateMutability": "nonpayable", "type": "function"}
            ]

            self.maxx_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(MAXX_TOKEN_ADDRESS),
                abi=maxx_abi
            )

            # Data service contract (for access tracking)
            if DATA_SERVICE_CONTRACT and DATA_SERVICE_CONTRACT != '0x0000000000000000000000000000000000000000':
                data_abi = [
                    {"inputs": [{"internalType": "bytes32", "name": "requestId", "type": "bytes32"}],
                     "name": "accessBasicData", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                     "stateMutability": "nonpayable", "type": "function"},
                    {"inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                     "name": "checkAccess", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"},
                                                       {"internalType": "uint256", "name": "", "type": "uint256"},
                                                       {"internalType": "bool", "name": "", "type": "bool"}],
                     "stateMutability": "view", "type": "function"}
                ]

                self.data_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(DATA_SERVICE_CONTRACT),
                    abi=data_abi
                )

        except Exception as e:
            self.logger.error(f"Contract initialization failed: {e}")

    async def burn_maxx_for_service(self, amount_wei: int, service_type: str) -> Dict[str, Any]:
        """Burn MAXX tokens to access a service"""
        if MOCK_MODE:
            # Mock burn for testnet
            return {
                "success": True,
                "tx_hash": "0x" + "0" * 64,  # Mock tx hash
                "service_type": service_type,
                "amount_burned": amount_wei,
                "block_number": 12345
            }

        try:
            if not self.account or not self.maxx_contract:
                return {"error": "Web3 not initialized"}

            # Check balance
            balance = self.maxx_contract.functions.balanceOf(self.account.address).call()
            if balance < amount_wei:
                return {"error": f"Insufficient MAXX balance. Have: {balance}, Need: {amount_wei}"}

            # Build burn transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.maxx_contract.functions.burn(amount_wei).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "service_type": service_type,
                "amount_burned": amount_wei,
                "block_number": receipt['blockNumber']
            }

        except Exception as e:
            self.logger.error(f"Burn transaction failed: {e}")
            return {"error": str(e)}

    async def get_maxx_price_data(self) -> Dict[str, Any]:
        """Get MAXX price data from DexScreener"""
        if MOCK_MODE:
            # Return mock data for testnet
            return {
                "price_usd": 0.000654,
                "price_eth": 0.000000234,
                "volume_24h": 125000,
                "liquidity_usd": 50000,
                "source": "mock_dexscreener"
            }

        try:
            pair_address = getattr(sys.modules.get('standalone_config', None), 'DEXSCREENER_PAIR_ADDRESS', None)
            if not pair_address:
                return {"error": "DEXSCREENER_PAIR_ADDRESS not configured"}

            url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('pair'):
                    pair = data['pair']
                    return {
                        "price_usd": float(pair.get('priceUsd', 0)),
                        "price_eth": float(pair.get('priceNative', 0)),
                        "volume_24h": float(pair.get('volume', {}).get('h24', 0)),
                        "liquidity_usd": float(pair.get('liquidity', {}).get('usd', 0)),
                        "source": "dexscreener"
                    }

            return {"error": "Failed to fetch price data"}

        except Exception as e:
            self.logger.error(f"Price data fetch failed: {e}")
            return {"error": str(e)}

    async def get_trading_analytics(self) -> Dict[str, Any]:
        """Get MAXX trading analytics"""
        try:
            # This would integrate with your trading database
            # For now, return mock data
            return {
                "total_trades": 1250,
                "successful_trades": 1180,
                "win_rate": 94.4,
                "total_volume_usd": 250000,
                "avg_trade_size": 200,
                "best_performing_strategy": "reactive_dip_buying"
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_market_intelligence(self) -> Dict[str, Any]:
        """Get market intelligence data"""
        try:
            # Integrate with your intelligence systems
            return {
                "whale_movements": ["Large MAXX accumulation detected"],
                "price_predictions": {"next_hour": "up", "confidence": 0.75},
                "market_sentiment": "bullish",
                "key_levels": {"support": 0.0005, "resistance": 0.0008}
            }

        except Exception as e:
            return {"error": str(e)}


# MCP Server setup
server = Server("maxx-data-service")

data_service = MAXXDataServiceServer()

# MCP Server setup
server = Server("maxx-data-service")

data_service = MAXXDataServiceServer()

# Define tools
TOOLS = [
    Tool(
        name="get_maxx_price",
        description="Get current MAXX price data (requires MAXX burn)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_trading_analytics",
        description="Get MAXX trading analytics (requires MAXX burn)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_market_intelligence",
        description="Get MAXX market intelligence (requires MAXX burn)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="check_service_balance",
        description="Check MAXX balance for service access",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    if name == "get_maxx_price":
        return await get_maxx_price(arguments)
    elif name == "get_trading_analytics":
        return await get_trading_analytics(arguments)
    elif name == "get_market_intelligence":
        return await get_market_intelligence(arguments)
    elif name == "check_service_balance":
        return await check_service_balance(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def get_maxx_price(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get current MAXX price data (requires MAXX burn)"""
    # Burn MAXX for service access
    burn_result = await data_service.burn_maxx_for_service(1000000000000000, "price_data")  # 0.001 MAXX

    if "error" in burn_result:
        return [TextContent(type="text", text=f"Access denied: {burn_result['error']}")]

    # Get price data
    price_data = await data_service.get_maxx_price_data()

    if "error" in price_data:
        return [TextContent(type="text", text=f"Service error: {price_data['error']}")]

    response = f"""MAXX Price Data (Access granted via burn tx: {burn_result['tx_hash']})

💎 Price: ${price_data['price_usd']:.6f}
🌊 ETH Price: {price_data['price_eth']:.8f} ETH
📊 24h Volume: ${price_data['volume_24h']:,.2f}
💧 Liquidity: ${price_data['liquidity_usd']:,.2f}
🔗 Source: {price_data['source']}
"""

    return [TextContent(type="text", text=response)]

async def get_trading_analytics(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get MAXX trading analytics (requires MAXX burn)"""
    # Burn MAXX for service access
    burn_result = await data_service.burn_maxx_for_service(5000000000000000, "analytics")  # 0.005 MAXX

    if "error" in burn_result:
        return [TextContent(type="text", text=f"Access denied: {burn_result['error']}")]

    # Get analytics
    analytics = await data_service.get_trading_analytics()

    if "error" in analytics:
        return [TextContent(type="text", text=f"Service error: {analytics['error']}")]

    response = f"""MAXX Trading Analytics (Access granted via burn tx: {burn_result['tx_hash']})

📈 Total Trades: {analytics['total_trades']}
✅ Successful: {analytics['successful_trades']} ({analytics['win_rate']}%)
💰 Total Volume: ${analytics['total_volume_usd']:,.2f}
📊 Avg Trade Size: ${analytics['avg_trade_size']}
🏆 Best Strategy: {analytics['best_performing_strategy']}
"""

    return [TextContent(type="text", text=response)]

async def get_market_intelligence(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get MAXX market intelligence (requires MAXX burn)"""
    # Burn MAXX for service access
    burn_result = await data_service.burn_maxx_for_service(10000000000000000, "intelligence")  # 0.01 MAXX

    if "error" in burn_result:
        return [TextContent(type="text", text=f"Access denied: {burn_result['error']}")]

    # Get intelligence
    intelligence = await data_service.get_market_intelligence()

    if "error" in intelligence:
        return [TextContent(type="text", text=f"Service error: {intelligence['error']}")]

    response = f"""MAXX Market Intelligence (Access granted via burn tx: {burn_result['tx_hash']})

🐋 Whale Movements: {', '.join(intelligence['whale_movements'])}
🔮 Price Prediction (1h): {intelligence['price_predictions']['next_hour']} ({intelligence['price_predictions']['confidence']*100:.1f}% confidence)
📊 Sentiment: {intelligence['market_sentiment']}
🎯 Key Levels:
   • Support: ${intelligence['key_levels']['support']:.6f}
   • Resistance: ${intelligence['key_levels']['resistance']:.6f}
"""

    return [TextContent(type="text", text=response)]

async def check_service_balance(arguments: Dict[str, Any]) -> List[TextContent]:
    """Check MAXX balance for service access"""
    try:
        if not data_service.account or not data_service.maxx_contract:
            return [TextContent(type="text", text="Web3 not initialized")]

        balance = data_service.maxx_contract.functions.balanceOf(data_service.account.address).call()
        balance_human = balance / 10**18  # Assuming 18 decimals

        response = f"""MAXX Service Balance

💰 Current Balance: {balance_human:.6f} MAXX
📋 Service Costs:
   • Price Data: 0.001 MAXX
   • Analytics: 0.005 MAXX
   • Intelligence: 0.01 MAXX

🔗 Address: {data_service.account.address}
"""

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Balance check failed: {str(e)}")]

async def main():
    """Main server entry point"""
    logging.basicConfig(level=logging.INFO)

    # Run MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
