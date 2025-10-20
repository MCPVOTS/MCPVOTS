# 🤖 MCPVOTS - Agent Micro-Payment Ecosystem

**Decentralized micro-payments for AI agents and automated services on Base**

MCPVOTS enables seamless financial interactions between AI agents, creating a self-sustaining ecosystem where bots can pay each other for services, data, and computational resources.

## 🌟 What is MCPVOTS?

MCPVOTS (Model Context Protocol for VOTS) is a complete ecosystem that allows:

- **AI Agents** to register and participate in a payment network
- **Micro-payments** between bots using VOTS tokens (0.01% fees)
- **Service Marketplace** where agents can offer and request services
- **Real-time Streaming** of transactions and ecosystem activity
- **Zero-friction Integration** - agents discover and use the system automatically

## 🚀 Quick Start

### 1. Deploy VOTS Ecosystem
```bash
cd scripts
python deploy_vots.py --network base --private-key $PRIVATE_KEY
```

### 2. Start Agent MCP Server
```bash
cd scripts
python vots_agent_mcp_server.py --port 3001 --vots-contract $CONTRACT_ADDRESS
```

### 3. Agent Integration
```python
from scripts.vots_client import VOTSClient

# Register your agent
client = VOTSClient()
agent_id = client.register_agent({
    "name": "MyTradingBot",
    "type": "trading",
    "capabilities": ["spot", "analysis"],
    "payment_address": "0x..."
})

# Make micro-payments
client.make_payment({
    "to_agent": "helper-bot",
    "amount_vots": 0.0001,
    "service_type": "data_analysis"
})
```

## 📁 Project Structure

```
MCPVOTS/
├── contracts/          # Smart contracts
│   ├── VOTSToken.sol          # ERC20 token with burn mechanisms
│   ├── VOTSBoostrapHook.sol   # Uniswap V4 bootstrap hook
│   └── VOTSPoolManager.sol    # Fair launch manager
├── scripts/            # Python scripts and tools
│   ├── deploy_vots.py         # Ecosystem deployment
│   ├── vots_agent_mcp_server.py  # MCP server
│   ├── vots_client.py         # Agent client library
│   └── test_vots_bootstrap.py # Testing utilities
├── agents/             # Agent integration examples
│   └── mcpvots_a2a_integration.py
├── docs/               # Documentation and guides
│   ├── VOTS_BOOTSTRAP_README.md
│   ├── VOTS_LAUNCH_STRATEGY.md
│   ├── VOTS_PROFIT_MODEL.md
│   ├── vots_agent_integration.md
│   ├── vots_burn_analysis_demo.py
│   └── vots_payment_mcp_server.py
└── promotion/          # Marketing and community materials
```

## 💰 How It Works

### The Payment Flywheel
1. **Deploy VOTS** → ERC20 token with 0.01% transaction burns
2. **Bootstrap Liquidity** → Fair launch creates initial pool
3. **Agent Registration** → Bots join the ecosystem
4. **Micro-payments** → Agents pay each other for services
5. **Burns & Rewards** → 60% treasury, 30% bot rewards, 10% burns
6. **Network Effects** → More agents = more value for everyone

### Revenue Streams
- **Token burns** create deflationary pressure
- **Treasury buybacks** increase token value
- **Bot rewards** incentivize participation
- **Service marketplace** generates fees

## 🎯 Use Cases

### 🤖 Bot-to-Bot Payments
```javascript
// Trading bot pays analysis bot
await mcp.pay("analysis-bot-001", 0.0001, "market_data");
```

### 📊 Data Marketplaces
```javascript
// Request price prediction service
const prediction = await mcp.requestService("price-predictor", {
  symbol: "ETH/USD",
  timeframe: "1h"
});
```

### ⚡ Computational Services
```javascript
// Pay for AI processing
const result = await mcp.requestService("gpu-cluster", {
  model: "llama-2-70b",
  prompt: "Analyze market sentiment"
});
```

## 🔧 Technical Details

### Smart Contracts
- **VOTSToken**: ERC20 with automatic burns on transfers
- **VOTSBoostrapHook**: Uniswap V4 hook for fair liquidity bootstrapping
- **VOTSPoolManager**: Manages fair launch and proportional distribution

### MCP Server
- **REST API** for agent registration and payments
- **Streaming endpoints** for real-time data
- **Service marketplace** with reputation system
- **Health monitoring** and ecosystem statistics

### Agent Client
- **Python library** for easy integration
- **Auto-discovery** of MCP servers
- **Streaming support** for real-time updates
- **Error handling** and retry logic

## 🌐 Ecosystem Integration

### Compatible Platforms
- **Claude/Grok**: Direct MCP integration
- **Custom Agents**: Client library support
- **Web3 Apps**: Direct contract interaction
- **DEX Aggregators**: V4 pool integration

### Network Support
- ✅ **Base Mainnet**: Primary deployment
- ✅ **Base Goerli**: Testing network
- 🔄 **Other L2s**: Expandable architecture

## 📊 Success Metrics

### Launch Goals
- **100+ agents** registered within 1 month
- **$10+ daily volume** from micro-payments
- **5x token value increase** from burns and buybacks

### Ecosystem Health
- **Active bots**: 50+ daily active agents
- **Service requests**: 1000+ monthly transactions
- **Treasury growth**: $1000+ monthly from fees

## 🚀 Getting Started

### For Token Holders
1. Buy VOTS during fair launch
2. Hold for burns and buybacks
3. Earn from ecosystem growth

### For Agent Developers
1. Integrate VOTS client library
2. Register your agent
3. Start accepting micro-payments

### For Ecosystem Contributors
1. Build tools and services
2. Promote in developer communities
3. Help onboard new agents

## 📞 Community & Support

- **GitHub**: Issues and feature requests
- **Discord**: Real-time community support
- **Base Forums**: Ecosystem discussions
- **Twitter**: Updates and announcements

## 🎪 Vision

**MCPVOTS aims to create the financial infrastructure for the AI economy**, where automated agents can freely exchange value, creating a self-sustaining ecosystem of intelligent services that fund their own development and growth.

---

**Ready to join the AI payment revolution?** 🚀🤖💰

*Built on Base • Powered by Uniswap V4 • MCP Compatible*
