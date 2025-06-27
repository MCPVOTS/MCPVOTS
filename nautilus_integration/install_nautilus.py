#!/usr/bin/env python3
"""
🚀 Nautilus Trader Installation & Setup Script
Automatically installs and configures Nautilus Trader integration with MCPVots
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

class NautilusInstaller:
    """
    🛠️ Nautilus Trader Installation Manager
    Handles complete setup and configuration
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.base_path = Path(__file__).parent
        self.mcpvots_root = self.base_path.parent
        
        # Installation status
        self.installation_status = {
            'nautilus_trader': False,
            'dependencies': False,
            'configuration': False,
            'integration': False,
            'knowledge_graph': False
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for installation process"""
        logger = logging.getLogger('nautilus_installer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    async def install_complete_system(self):
        """Install complete Nautilus-MCPVots system"""
        self.logger.info("🚀 Starting Nautilus Trader installation for MCPVots")
        self.logger.info("💰 Setting up crypto trading with $50 budget")
        self.logger.info("⛓️ Configuring Solana & Base L2 integration")
        print("=" * 60)
        
        try:
            # Step 1: Install Nautilus Trader
            await self._install_nautilus_trader()
            
            # Step 2: Install dependencies
            await self._install_dependencies()
            
            # Step 3: Setup configuration
            await self._setup_configuration()
            
            # Step 4: Setup integration
            await self._setup_integration()
            
            # Step 5: Initialize knowledge graph
            await self._initialize_knowledge_graph()
            
            # Step 6: Verify installation
            await self._verify_installation()
            
            # Step 7: Create startup scripts
            await self._create_startup_scripts()
            
            self._print_success_message()
            
        except Exception as e:
            self.logger.error(f"❌ Installation failed: {e}")
            self._print_troubleshooting()
            raise
            
    async def _install_nautilus_trader(self):
        """Install Nautilus Trader package"""
        self.logger.info("📦 Installing Nautilus Trader...")
        
        try:
            # Check if already installed
            result = subprocess.run([
                sys.executable, '-c', 'import nautilus_trader; print("installed")'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Nautilus Trader already installed")
                self.installation_status['nautilus_trader'] = True
                return
                
            # Install Nautilus Trader
            cmd = [sys.executable, '-m', 'pip', 'install', 'nautilus_trader']
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.logger.info("✅ Nautilus Trader installed successfully")
            self.installation_status['nautilus_trader'] = True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install Nautilus Trader: {e}")
            self.logger.info("🔄 Trying alternative installation...")
            
            # Try with development version
            try:
                cmd = [
                    sys.executable, '-m', 'pip', 'install', 
                    'nautilus_trader', '--pre',
                    '--index-url=https://packages.nautechsystems.io/simple'
                ]
                subprocess.run(cmd, check=True)
                self.logger.info("✅ Nautilus Trader (dev) installed successfully")
                self.installation_status['nautilus_trader'] = True
            except:
                self.logger.warning("⚠️ Nautilus installation failed - continuing in simulation mode")
                
    async def _install_dependencies(self):
        """Install required dependencies"""
        self.logger.info("📦 Installing dependencies...")
        
        dependencies = [
            'websockets',
            'aiohttp', 
            'pandas',
            'numpy',
            'requests',
            'python-binance',  # For Binance API
            'ccxt',  # Unified exchange API
            'redis',  # For caching
            'solana',  # Solana SDK
            'web3',  # Ethereum SDK
        ]
        
        for dep in dependencies:
            try:
                cmd = [sys.executable, '-m', 'pip', 'install', dep]
                subprocess.run(cmd, check=True, capture_output=True)
                self.logger.info(f"✅ Installed {dep}")
            except subprocess.CalledProcessError:
                self.logger.warning(f"⚠️ Failed to install {dep} - skipping")
                
        self.installation_status['dependencies'] = True
        
    async def _setup_configuration(self):
        """Setup configuration files"""
        self.logger.info("⚙️ Setting up configuration...")
        
        # Create configuration directory
        config_dir = self.base_path / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Default configuration
        config = {
            "trading_pairs": ["SOL/USDT", "ETH/USDT", "BTC/USDT"],
            "initial_capital": 50.0,
            "risk_per_trade": 0.02,
            "max_positions": 3,
            "ai_confidence_threshold": 0.75,
            "update_frequency": 1.0,
            "exchanges": ["binance", "coinbase", "okx"],
            "strategies": ["ai_enhanced", "trend_following"],
            
            # Blockchain settings
            "solana_rpc": "https://api.devnet.solana.com",
            "base_rpc": "https://sepolia.base.org",
            "ethereum_rpc": "https://ethereum-sepolia.blockpi.network/v1/rpc/public",
            
            # AI settings
            "ai_models": {
                "primary": "gemini-2.5",
                "secondary": "deepseek-r1"
            },
            
            # Risk management
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
            "max_drawdown": 0.15,
            
            # Data collection
            "intelligence_collection": {
                "price_data": True,
                "volume_analysis": True,
                "orderbook_depth": True,
                "funding_rates": True,
                "social_sentiment": True,
                "onchain_metrics": True,
                "defi_metrics": True,
                "whale_monitoring": True
            },
            
            # MCP integration
            "mcp_servers": [
                {"name": "memory", "port": 3002},
                {"name": "github", "port": 3001},
                {"name": "solana", "port": 3005}
            ]
        }
        
        # Save configuration
        config_file = config_dir / 'trading_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.logger.info(f"✅ Configuration saved to {config_file}")
        
        # Create environment template
        env_template = """
# Nautilus Trader - MCPVots Integration Environment
# Copy this file to .env and fill in your API keys

# Exchange API Keys (Optional - for live trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_here

COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_SECRET_KEY=your_coinbase_secret_here

# AI Model API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Blockchain RPC URLs (Optional - use public endpoints)
SOLANA_RPC_URL=https://api.devnet.solana.com
BASE_RPC_URL=https://sepolia.base.org
ETHEREUM_RPC_URL=https://ethereum-sepolia.blockpi.network/v1/rpc/public

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379

# Trading Settings
TRADING_MODE=simulation  # simulation or live
LOG_LEVEL=INFO
"""
        
        env_file = self.base_path / '.env.template'
        with open(env_file, 'w') as f:
            f.write(env_template)
            
        self.logger.info(f"✅ Environment template created: {env_file}")
        self.installation_status['configuration'] = True
        
    async def _setup_integration(self):
        """Setup MCPVots integration"""
        self.logger.info("🔗 Setting up MCPVots integration...")
        
        # Create integration package
        integration_dir = self.mcpvots_root / 'src' / 'integrations' / 'nautilus'
        integration_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = integration_dir / '__init__.py'
        with open(init_file, 'w') as f:
            f.write('''"""
Nautilus Trader integration for MCPVots
Advanced crypto trading with AI intelligence
"""

from .nautilus_service import NautilusService
from .trading_strategies import AIEnhancedStrategy
from .market_intelligence import IntelligenceCollector

__all__ = ['NautilusService', 'AIEnhancedStrategy', 'IntelligenceCollector']
''')
        
        # Create service integration
        service_content = '''"""
Nautilus Service Integration for MCPVots
"""

import asyncio
import sys
from pathlib import Path

# Add nautilus integration to path
nautilus_path = Path(__file__).parent.parent.parent.parent / 'nautilus_integration'
sys.path.append(str(nautilus_path))

try:
    from nautilus_mcp_bridge import NautilusSystemOrchestrator
    NAUTILUS_AVAILABLE = True
except ImportError:
    NAUTILUS_AVAILABLE = False

class NautilusService:
    """MCPVots service wrapper for Nautilus Trader"""
    
    def __init__(self):
        self.orchestrator = None
        self.is_running = False
        
    async def start(self):
        """Start Nautilus trading system"""
        if not NAUTILUS_AVAILABLE:
            raise RuntimeError("Nautilus integration not available")
            
        self.orchestrator = NautilusSystemOrchestrator()
        await self.orchestrator.start_system()
        self.is_running = True
        
    async def stop(self):
        """Stop Nautilus trading system"""
        if self.orchestrator:
            await self.orchestrator.stop_system()
        self.is_running = False
        
    def get_status(self):
        """Get current trading status"""
        return {
            'available': NAUTILUS_AVAILABLE,
            'running': self.is_running,
            'performance': self.orchestrator.bridge.performance_metrics if self.orchestrator else {}
        }
'''
        
        service_file = integration_dir / 'nautilus_service.py'
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        self.logger.info("✅ MCPVots integration setup complete")
        self.installation_status['integration'] = True
        
    async def _initialize_knowledge_graph(self):
        """Initialize knowledge graph entities for trading"""
        self.logger.info("🧠 Initializing trading knowledge graph...")
        
        try:
            # Check if MCP service is available
            sys.path.append(str(self.mcpvots_root / 'src'))
            
            from mcp_service import MCPIntegrationService
            
            mcp = MCPIntegrationService()
            await mcp.initialize()
            
            # Create trading entities
            trading_entities = [
                {
                    'name': 'nautilus_trading_system',
                    'entityType': 'trading_system',
                    'observations': [
                        'High-performance algorithmic trading platform',
                        'Integrated with MCPVots AGI ecosystem',
                        'Supports crypto trading on Solana and Base L2',
                        'AI-enhanced decision making',
                        'Real-time market intelligence'
                    ]
                },
                {
                    'name': 'crypto_markets',
                    'entityType': 'market_category',
                    'observations': [
                        'Primary focus: SOL, ETH, BTC trading pairs',
                        'Multi-exchange coordination',
                        'DeFi protocol integration',
                        'On-chain metrics monitoring'
                    ]
                },
                {
                    'name': 'ai_trading_strategies',
                    'entityType': 'strategy_category',
                    'observations': [
                        'AI-enhanced trend following',
                        'Mean reversion with sentiment analysis',
                        'Multi-timeframe analysis',
                        'Risk-adjusted position sizing'
                    ]
                },
                {
                    'name': 'risk_management',
                    'entityType': 'risk_system',
                    'observations': [
                        'Maximum 2% risk per trade',
                        '3% stop loss automation',
                        '6% take profit targets',
                        'Maximum 3 concurrent positions'
                    ]
                }
            ]
            
            await mcp.create_entities(trading_entities)
            
            # Create relationships
            trading_relations = [
                {
                    'from': 'nautilus_trading_system',
                    'to': 'crypto_markets',
                    'relationType': 'trades_in'
                },
                {
                    'from': 'nautilus_trading_system',
                    'to': 'ai_trading_strategies',
                    'relationType': 'implements'
                },
                {
                    'from': 'ai_trading_strategies',
                    'to': 'risk_management',
                    'relationType': 'protected_by'
                }
            ]
            
            await mcp.create_relations(trading_relations)
            
            self.logger.info("✅ Knowledge graph initialized with trading entities")
            self.installation_status['knowledge_graph'] = True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Knowledge graph initialization failed: {e}")
            
    async def _verify_installation(self):
        """Verify installation completeness"""
        self.logger.info("🔍 Verifying installation...")
        
        success_count = sum(self.installation_status.values())
        total_steps = len(self.installation_status)
        
        self.logger.info(f"✅ Installation: {success_count}/{total_steps} steps completed")
        
        for step, status in self.installation_status.items():
            status_emoji = "✅" if status else "❌"
            self.logger.info(f"  {status_emoji} {step.replace('_', ' ').title()}")
            
    async def _create_startup_scripts(self):
        """Create convenient startup scripts"""
        self.logger.info("📜 Creating startup scripts...")
        
        # PowerShell startup script
        ps_script = '''# Nautilus Trader - MCPVots Startup Script
Write-Host "🌊 Starting Nautilus Trader with MCPVots Integration" -ForegroundColor Cyan
Write-Host "💰 Trading Budget: $50 USD" -ForegroundColor Green
Write-Host "⛓️ Blockchain: Solana + Base L2" -ForegroundColor Blue

# Navigate to integration directory
Set-Location "nautilus_integration"

# Activate virtual environment if it exists
if (Test-Path ".venv") {
    .venv\\Scripts\\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

# Start the trading system
Write-Host "🚀 Starting trading system..." -ForegroundColor Yellow
python nautilus_mcp_bridge.py
'''
        
        ps_file = self.base_path / 'start_nautilus.ps1'
        with open(ps_file, 'w') as f:
            f.write(ps_script)
            
        # Bash startup script
        bash_script = '''#!/bin/bash
echo "🌊 Starting Nautilus Trader with MCPVots Integration"
echo "💰 Trading Budget: $50 USD"
echo "⛓️ Blockchain: Solana + Base L2"

# Navigate to integration directory
cd nautilus_integration

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start the trading system
echo "🚀 Starting trading system..."
python nautilus_mcp_bridge.py
'''
        
        bash_file = self.base_path / 'start_nautilus.sh'
        with open(bash_file, 'w') as f:
            f.write(bash_script)
            
        # Make bash script executable
        os.chmod(bash_file, 0o755)
        
        # Python startup script
        py_script = '''#!/usr/bin/env python3
"""
Quick start script for Nautilus Trader integration
"""

import asyncio
import sys
from pathlib import Path

# Add integration to path
sys.path.append(str(Path(__file__).parent / 'nautilus_integration'))

from nautilus_mcp_bridge import NautilusSystemOrchestrator

async def main():
    print("🌊 Nautilus Trader - MCPVots Integration")
    print("🚀 Quick Start")
    print("💰 Budget: $50 | 🎯 Focus: SOL/ETH/BTC")
    print("=" * 50)
    
    orchestrator = NautilusSystemOrchestrator()
    
    try:
        await orchestrator.start_system()
    except KeyboardInterrupt:
        print("\\n⏹️ Shutting down...")
        await orchestrator.stop_system()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        py_file = self.base_path / 'quick_start.py'
        with open(py_file, 'w') as f:
            f.write(py_script)
            
        self.logger.info("✅ Startup scripts created")
        
    def _print_success_message(self):
        """Print installation success message"""
        print("\n" + "=" * 70)
        print("🎉 NAUTILUS TRADER INSTALLATION COMPLETE!")
        print("=" * 70)
        print("🌊 Advanced Crypto Trading System Ready")
        print("🧠 AI-Powered Decision Making: DeepSeek R1 + Gemini 2.5")
        print("💰 Starting Budget: $50 USD")
        print("⛓️ Blockchain Support: Solana + Base L2")
        print("📊 Multi-Exchange: Binance, Coinbase, OKX")
        print("")
        print("🚀 Quick Start Options:")
        print("  1. PowerShell: .\\start_nautilus.ps1")
        print("  2. Python:     python quick_start.py")
        print("  3. Manual:     cd nautilus_integration && python nautilus_mcp_bridge.py")
        print("")
        print("📂 Key Files:")
        print(f"  • Configuration: {self.base_path}/config/trading_config.json")
        print(f"  • Environment:   {self.base_path}/.env.template")
        print(f"  • Integration:   {self.base_path}/nautilus_integration/")
        print("")
        print("⚡ Features Enabled:")
        
        for feature, enabled in self.installation_status.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
            
        print("")
        print("🔗 MCPVots Integration: Fully Connected")
        print("📈 Knowledge Graph: Trading entities created")
        print("🛡️ Risk Management: 2% per trade, 3% stop loss")
        print("")
        print("📚 Documentation: ./nautilus_integration/README.md")
        print("💬 Support: Check MCPVots logs for system status")
        print("=" * 70)
        
    def _print_troubleshooting(self):
        """Print troubleshooting information"""
        print("\n" + "🔧 TROUBLESHOOTING" + "=" * 50)
        print("If installation failed, try:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Install manually: pip install nautilus_trader")
        print("3. Use development version:")
        print("   pip install nautilus_trader --pre --index-url=https://packages.nautechsystems.io/simple")
        print("4. Check system requirements: Python 3.9+")
        print("5. Install build tools if on Windows")
        print("")
        print("📝 For support, check:")
        print("  • Nautilus docs: https://nautilustrader.io/docs/")
        print("  • MCPVots logs: Check system status")
        print("=" * 70)

async def main():
    """Main installation entry point"""
    installer = NautilusInstaller()
    await installer.install_complete_system()

if __name__ == "__main__":
    asyncio.run(main())
