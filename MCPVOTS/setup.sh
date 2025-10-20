#!/bin/bash
# MCPVOTS Setup Script
# Installs dependencies and sets up the VOTS agent ecosystem

echo "🚀 Setting up MCPVOTS Agent Ecosystem"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "contracts" ]; then
    echo "❌ Please run this script from the MCPVOTS directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check for Node.js (for contract compilation if needed)
if command -v node &> /dev/null; then
    echo "📦 Node.js found - you can compile contracts if needed"
else
    echo "⚠️  Node.js not found - install it for contract compilation"
fi

# Check for Foundry (for contract deployment)
if command -v forge &> /dev/null; then
    echo "🔨 Foundry found - ready for contract deployment"
else
    echo "⚠️  Foundry not found - install it for contract deployment"
    echo "   Visit: https://book.getfoundry.sh/getting-started/installation"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Set up environment file template
if [ ! -f ".env" ]; then
    cat > .env << EOF
# MCPVOTS Environment Configuration

# Network Configuration
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453

# Contract Addresses (after deployment)
VOTS_TOKEN_ADDRESS=
POOL_MANAGER_ADDRESS=
BOOTSTRAP_HOOK_ADDRESS=

# Server Configuration
MCP_SERVER_PORT=3001
MCP_SERVER_HOST=0.0.0.0

# Private Key (NEVER commit this!)
PRIVATE_KEY=your_private_key_here

# Optional: External APIs
ETHERSCAN_API_KEY=
EOF
    echo "📝 Created .env template - configure your settings"
fi

echo ""
echo "✅ MCPVOTS setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your .env file with private key and settings"
echo "2. Deploy contracts: python scripts/deploy_vots.py"
echo "3. Start MCP server: python scripts/vots_agent_mcp_server.py"
echo "4. Register agents and start making micro-payments!"
echo ""
echo "📚 Documentation: See docs/ folder for detailed guides"
echo "🆘 Support: Check GitHub issues for help"
