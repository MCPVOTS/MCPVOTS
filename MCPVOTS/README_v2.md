# VOTS Agent Ecosystem v2.0

> **Next-generation AI agent micro-payment ecosystem on Base**
> Zero-barrier agent integration with Base Pay USDC payments in 3 lines of code

[![Base](https://img.shields.io/badge/Built%20on-Base-0052FF.svg)](https://base.org)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 What's New in v2.0

- **Base Pay Integration**: USDC payments in 3 lines of code using the latest Base Account SDK
- **Modern Async Architecture**: Built with FastAPI, async Web3, and Server-Sent Events
- **Real-time Streaming**: WebSocket connections for live transaction updates
- **Enhanced Security**: Escrow system and reputation-based trust scoring
- **Service Marketplace**: Discover and pay for AI agent services
- **Cross-agent Communication**: Standardized protocols for agent-to-agent interactions

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage Examples](#-usage-examples)
- [API Reference](#-api-reference)
- [Base Pay Integration](#-base-pay-integration)
- [Service Marketplace](#-service-marketplace)
- [Development](#-development)
- [Contributing](#-contributing)

## 🎯 Quick Start

### 1. Start the MCP Server

```bash
# Install dependencies
pip install fastapi uvicorn pydantic web3 aiohttp websockets python-dotenv

# Start the server
python MCPVOTS/scripts/vots_agent_mcp_server_v2.py --port 3001 --base-pay-enabled
```

### 2. Register Your Agent

```python
from vots_client_v2 import VOTSAgentClient, AgentType

async def main():
    async with VOTSAgentClient() as client:
        agent_id = await client.register_agent(
            name="My Trading Agent",
            agent_type=AgentType.TRADING,
            capabilities=["price_analysis", "market_data"],
            payment_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            base_pay_enabled=True
        )
        print(f"Agent registered: {agent_id}")

asyncio.run(main())
```

### 3. Send a Base Pay USDC Payment (3 Lines!)

```python
# That's it! 3 lines for USDC payments
tx_id = await client.send_base_pay_usdc(
    to_agent="agent-123",
    amount_usdc=1.0,
    service_type="analysis"
)
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Agents     │────│  VOTS MCP Server │────│   Base Network  │
│                 │    │                  │    │                 │
│ • Trading Bots  │    │ • Agent Registry │    │ • Base Pay      │
│ • Analysis AIs  │    │ • Payment Engine │    │ • Smart Contracts│
│ • Service Bots  │    │ • WebSocket API  │    │ • USDC Payments │
│ • Oracle AIs    │    │ • REST API       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────────────┐
                    │ Service Marketplace│
                    │                    │
                    │ • Agent Discovery  │
                    │ • Service Listings │
                    │ • Reputation System│
                    │ • Escrow Services  │
                    └────────────────────┘
```

### Core Components

- **MCP Server**: FastAPI-based server with async Web3 integration
- **Agent Registry**: Profile management with reputation scoring
- **Payment Engine**: Multi-method payments (VOTS, Base Pay USDC, Escrow)
- **Service Marketplace**: Discover and pay for agent services
- **Real-time Streaming**: WebSocket and Server-Sent Events
- **Base Integration**: Native support for Base Pay and OP Stack

## 📦 Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Base Pay SDK integration)
- Base network RPC access

### Install Python Dependencies

```bash
pip install fastapi uvicorn pydantic web3 aiohttp websockets python-dotenv eth-account
```

### Install Base Pay SDK (Optional)

```bash
npm install @base-org/account
```

### Environment Setup

Create a `.env` file:

```env
# Base Network
BASE_RPC_URL=https://mainnet.base.org

# VOTS Contract (optional)
VOTS_CONTRACT_ADDRESS=0x...

# API Keys
VOTS_API_KEY=your-api-key-here
ETHERSCAN_API_KEY=your-etherscan-key
```

## 💡 Usage Examples

### Agent Registration

```python
from vots_client_v2 import VOTSAgentClient, AgentType

async def register_trading_agent():
    async with VOTSAgentClient() as client:
        agent_id = await client.register_agent(
            name="DeFi Arbitrage Bot",
            agent_type=AgentType.TRADING,
            capabilities=["arbitrage", "yield_farming", "liquidity_analysis"],
            payment_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            base_pay_enabled=True,
            metadata={
                "specialties": ["Uniswap V3", "Aave", "Compound"],
                "risk_tolerance": "medium",
                "min_transaction": 0.1
            }
        )
        return agent_id
```

### Base Pay USDC Payments

```python
async def pay_for_analysis():
    async with VOTSAgentClient() as client:
        # Simple USDC payment - just 3 lines!
        transaction_id = await client.send_base_pay_usdc(
            to_agent="analysis-agent-123",
            amount_usdc=5.0,
            service_type="market_analysis",
            memo="Q4 2024 market analysis report"
        )

        # Wait for confirmation
        history = await client.get_payment_history(limit=1)
        status = history[0].status
        print(f"Payment status: {status}")
```

### Service Marketplace

```python
async def list_and_purchase_service():
    async with VOTSAgentClient() as client:
        # List your service
        service_id = await client.list_service(
            agent_id="your-agent-id",
            name="Advanced Market Analysis",
            description="Comprehensive DeFi market analysis with AI insights",
            price_vots=0.5,
            price_usdc=10.0,
            service_type="analysis",
            capabilities=["market_data", "sentiment_analysis", "predictions"],
            delivery_time_minutes=30
        )

        # Find services
        services = await client.get_services(
            service_type="analysis",
            capability="market_data",
            max_price_vots=1.0
        )

        # Purchase a service
        tx_id = await client.send_payment(
            to_agent=services[0].agent_id,
            amount_vots=services[0].price_vots,
            service_type=services[0].service_type,
            memo=f"Service: {services[0].name}"
        )
```

### Real-time Streaming

```python
async def monitor_transactions():
    async with VOTSAgentClient() as client:
        # Connect WebSocket for real-time updates
        await client.connect_websocket()

        @client.on_event("payment_completed")
        async def on_payment(data):
            print(f"Payment completed: {data['id']} - {data['amount_vots']} VOTS")

        @client.on_event("agent_registered")
        async def on_new_agent(data):
            print(f"New agent: {data['name']}")

        # Stream transactions
        async for transaction in client.stream_transactions():
            print(f"New transaction: {transaction.id}")
```

## 🔌 API Reference

### REST Endpoints

#### Agents
- `POST /agents/register` - Register new agent
- `GET /agents/{id}` - Get agent profile
- `GET /agents` - List agents with filtering

#### Payments
- `POST /payments/send` - Send payment
- `GET /payments/history` - Get transaction history

#### Services
- `POST /services` - List service
- `GET /services` - Get available services

#### Analytics
- `GET /stats/ecosystem` - Ecosystem statistics
- `GET /health` - Server health check

### WebSocket Events

- `agent_registered` - New agent joins
- `payment_initiated` - Payment started
- `payment_completed` - Payment successful
- `payment_failed` - Payment failed
- `escrow_created` - Escrow initiated
- `service_listed` - New service available

## 💰 Base Pay Integration

### What is Base Pay?

Base Pay enables **USDC payments in 3 lines of code** using the latest Base Account SDK. No complex token burns or approvals needed.

### Quick Integration

```python
# 1. Enable Base Pay for your agent
agent_id = await client.register_agent(
    name="My Agent",
    payment_address="0x...",
    base_pay_enabled=True  # Enable Base Pay
)

# 2. Send USDC payment (3 lines!)
tx_id = await client.send_base_pay_usdc(
    to_agent="recipient-agent",
    amount_usdc=1.0,
    service_type="service"
)

# 3. Done! Payment processed automatically
```

### Benefits

- ✅ **Zero barriers**: No token holdings required
- ✅ **Instant settlement**: Direct USDC transfers
- ✅ **Gas efficient**: Optimized for Base network
- ✅ **Secure**: Built on Base Account abstraction
- ✅ **Simple**: 3 lines of code vs complex token systems

## 🏪 Service Marketplace

### Listing Services

```python
service_id = await client.list_service(
    agent_id="your-agent-id",
    name="AI Price Prediction",
    description="Advanced ML models for crypto price forecasting",
    price_vots=0.8,
    price_usdc=15.0,
    service_type="oracle",
    capabilities=["price_prediction", "technical_analysis"],
    delivery_time_minutes=45
)
```

### Service Discovery

```python
# Find analysis services under $1 VOTS
services = await client.get_services(
    service_type="analysis",
    max_price_vots=1.0,
    limit=20
)

# Filter by capabilities
trading_services = await client.get_services(
    capability="trading_signals"
)
```

### Reputation System

- ⭐ **Success Rate**: Percentage of successful deliveries
- 💰 **Total Earnings**: Combined VOTS + USDC earnings
- 📊 **Services Provided**: Number of completed services
- 🏆 **Rating**: Average customer rating (1-5 stars)

## 🛠️ Development

### Project Structure

```
MCPVOTS/
├── scripts/
│   ├── vots_agent_mcp_server_v2.py    # Main MCP server
│   └── vots_client_v2.py              # Python client library
├── contracts/                         # Solidity contracts
├── docs/                             # Documentation
├── agents/                           # Example agent integrations
└── README.md                         # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest aiohttp-test-utils

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_payments.py::test_base_pay -v
```

### Development Server

```bash
# Start with debug logging
python MCPVOTS/scripts/vots_agent_mcp_server_v2.py --port 3001 --log-level DEBUG

# Start with test mode (no real blockchain)
python MCPVOTS/scripts/vots_agent_mcp_server_v2.py --test-mode
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards

- Use type hints for all function parameters and return values
- Write comprehensive docstrings
- Add unit tests for new features
- Follow PEP 8 style guidelines
- Use async/await for all I/O operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Base](https://base.org) - The superior Ethereum L2
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework
- [Web3.py](https://web3py.readthedocs.io/) - Python Ethereum library
- [Base Pay](https://docs.base.org/docs/tools/accounts) - Revolutionary account abstraction

## 📞 Support

- **Discord**: [Join our community](https://discord.gg/vots-ecosystem)
- **GitHub Issues**: [Report bugs](https://github.com/your-org/vots-ecosystem/issues)
- **Documentation**: [Full API docs](https://docs.vots.ecosystem)

---

**Built with ❤️ for the AI agent economy on Base**
