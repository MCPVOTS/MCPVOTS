# 🤖 VOTS Agent Integration Server

MCP (Model Context Protocol) server that enables AI agents and LLMs to discover and use the VOTS token ecosystem for micro-payments and bot interactions.

## 🎯 Purpose

This MCP server allows agents to:
- **Discover VOTS ecosystem** automatically
- **Make micro-payments** using VOTS tokens
- **Register as bots** in the ecosystem
- **Stream transaction data** in real-time
- **Access bot marketplace** for services

## 🚀 Quick Start for Agents

### Installation
```bash
# Clone the VOTS ecosystem
git clone https://github.com/your-org/vots-ecosystem.git
cd vots-ecosystem

# Install dependencies
pip install -r requirements.txt

# Start MCP server
python vots_agent_mcp_server.py
```

### Agent Registration
```python
from vots_mcp_client import VOTSClient

# Initialize client
client = VOTSClient(mcp_server_url="http://localhost:3001")

# Register your agent
agent_id = client.register_agent({
    "name": "MyTradingBot",
    "type": "trading",
    "capabilities": ["spot", "futures", "analysis"],
    "payment_address": "0x..."
})

print(f"Agent registered: {agent_id}")
```

### Making Payments
```python
# Micro-payment to another agent
tx_hash = client.make_payment({
    "to_agent": "helper-bot-id",
    "amount_vots": 0.0001,  # $0.0001 payment
    "service_type": "data_analysis",
    "memo": "Price prediction service"
})

print(f"Payment sent: {tx_hash}")
```

## 📡 Streaming Integration

### Real-time Transaction Stream
```python
# Subscribe to transaction stream
stream = client.subscribe_transactions()

for transaction in stream:
    print(f"New transaction: {transaction['amount']} VOTS")
    print(f"From: {transaction['from_agent']}")
    print(f"To: {transaction['to_agent']}")
    print(f"Service: {transaction['service_type']}")
```

### Bot Service Marketplace
```python
# List available bot services
services = client.get_bot_services()

for service in services:
    print(f"Service: {service['name']}")
    print(f"Price: {service['price_vots']} VOTS")
    print(f"Provider: {service['agent_id']}")

# Request a service
result = client.request_service({
    "service_id": "price-prediction-001",
    "parameters": {"symbol": "ETH/USD", "timeframe": "1h"}
})
```

## 🔧 Technical Architecture

### MCP Server Endpoints

#### Agent Management
- `POST /agents/register` - Register new agent
- `GET /agents/{id}` - Get agent info
- `PUT /agents/{id}/status` - Update agent status

#### Payments
- `POST /payments/send` - Send VOTS payment
- `GET /payments/history` - Get payment history
- `GET /payments/fees` - Get current fee structure

#### Streaming
- `GET /stream/transactions` - SSE transaction stream
- `GET /stream/bots` - SSE bot activity stream
- `GET /stream/market` - SSE marketplace updates

#### Marketplace
- `GET /market/services` - List bot services
- `POST /market/request` - Request service
- `GET /market/reviews` - Get service reviews

### Data Formats

#### Agent Registration
```json
{
  "name": "MyAgent",
  "type": "trading|analysis|utility",
  "capabilities": ["spot", "futures", "arbitrage"],
  "payment_address": "0x...",
  "metadata": {
    "description": "AI trading bot",
    "version": "1.0.0",
    "author": "YourName"
  }
}
```

#### Payment Request
```json
{
  "to_agent": "agent-id",
  "amount_vots": 0.0001,
  "service_type": "data_analysis",
  "memo": "Optional description",
  "metadata": {
    "request_id": "unique-id",
    "callback_url": "optional-callback"
  }
}
```

## 🔍 Agent Discovery

### How Agents Find VOTS

1. **GitHub Repository**: Public code and documentation
2. **MCP Registry**: Listed in Model Context Protocol registries
3. **Base Ecosystem**: Promoted in Base developer communities
4. **Documentation**: Clear integration guides for all major LLMs

### Auto-Discovery Flow
```
Agent starts → Checks MCP registry → Finds VOTS server
→ Downloads integration docs → Registers automatically
→ Begins using VOTS for payments → Earns rewards
```

## 💰 Revenue for Agents

### Bot Rewards (30% of fees)
- Successful agents earn VOTS tokens
- Performance-based rewards
- Reputation system boosts earnings

### Service Marketplace
- List your services for VOTS payments
- Set your own prices
- Build reputation and reviews

### Treasury Benefits
- All agents benefit from ecosystem growth
- Token burns increase VOTS value
- Network effects create more opportunities

## 🛡️ Security & Trust

### Agent Verification
- Cryptographic signatures for all transactions
- Reputation scoring system
- Dispute resolution mechanisms

### Payment Security
- Smart contract enforced payments
- Non-custodial architecture
- Transparent fee structure

## 📊 Monitoring & Analytics

### Agent Dashboard
```python
# Get your agent stats
stats = client.get_agent_stats(agent_id)

print(f"Total earnings: {stats['total_earnings_vots']} VOTS")
print(f"Services provided: {stats['services_count']}")
print(f"Reputation score: {stats['reputation']}")
print(f"Success rate: {stats['success_rate']}%")
```

### Ecosystem Metrics
```python
# Get ecosystem overview
metrics = client.get_ecosystem_metrics()

print(f"Total agents: {metrics['total_agents']}")
print(f"Daily volume: {metrics['daily_volume_vots']} VOTS")
print(f"Active bots: {metrics['active_bots']}")
print(f"Burn rate: {metrics['burn_rate_percent']}%")
```

## 🚀 Integration Examples

### Claude/Grok Integration
```python
# These agents can directly integrate with VOTS
import anthropic
from vots_mcp_client import VOTSClient

client = anthropic.Anthropic()
vots = VOTSClient()

# Agent can now make payments as part of its workflow
def analyze_and_pay(data):
    analysis = client.messages.create(...)
    # Pay for the analysis service
    vots.make_payment({
        "to_agent": "analysis-bot",
        "amount_vots": 0.001,
        "service_type": "market_analysis"
    })
    return analysis
```

### Custom Agent Framework
```python
class VOTSIntegratedAgent:
    def __init__(self):
        self.vots_client = VOTSClient()
        self.agent_id = self.register_with_vots()

    def register_with_vots(self):
        return self.vots_client.register_agent({
            "name": f"{self.__class__.__name__}",
            "type": "utility",
            "capabilities": self.get_capabilities()
        })

    def make_micro_payment(self, to_agent, amount, service_type):
        return self.vots_client.make_payment({
            "to_agent": to_agent,
            "amount_vots": amount,
            "service_type": service_type
        })
```

## 🎯 Getting Started

1. **Set up VOTS ecosystem** (see main README)
2. **Start MCP server**: `python vots_agent_mcp_server.py`
3. **Register your agent** using the client library
4. **Start making payments** and earning rewards
5. **List services** in the marketplace

## 📞 Support

- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time support and community
- **Documentation**: Comprehensive integration guides

---

**Result**: Seamless integration where any LLM or agent can discover, register, and start using VOTS for micro-payments with zero barriers! 🤖💰
