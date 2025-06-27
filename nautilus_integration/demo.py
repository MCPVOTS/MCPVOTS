#!/usr/bin/env python3
"""
Quick Test and Demo for MCPVots Nautilus Integration
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcpvots_nautilus_integration import MCPVotsNautilusIntegration, TradingSignal, MarketAnalysis
    integration_available = True
except ImportError as e:
    print(f"⚠️ Integration module not available: {e}")
    integration_available = False

async def test_ai_analysis():
    """Test AI market analysis"""
    print("🤖 Testing AI Market Analysis...")
    
    if not integration_available:
        print("❌ Integration not available, using mock data")
        return
    
    try:
        integration = MCPVotsNautilusIntegration()
        
        # Test multiple symbols
        symbols = ["SOL/USDT", "ETH/USDT", "BTC/USDT"]
        
        for symbol in symbols:
            print(f"\n📊 Analyzing {symbol}...")
            analysis = await integration.get_ai_market_analysis(symbol)
            
            print(f"   Signal: {analysis.signal.value}")
            print(f"   Confidence: {analysis.confidence:.2f}")
            print(f"   Price Target: {analysis.price_target}")
            print(f"   Stop Loss: {analysis.stop_loss}")
            print(f"   Reasoning: {analysis.reasoning[:100]}...")
            
            # Test trade execution
            if analysis.confidence > 0.5:
                print(f"   📈 Trade would be executed (confidence > 0.5)")
                result = await integration.execute_trade(analysis)
                print(f"   Result: {'✅ Success' if result else '❌ Failed'}")
            else:
                print(f"   ⚠️ Trade skipped (low confidence)")
        
    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")

async def test_trading_metrics():
    """Test trading metrics"""
    print("\n📊 Testing Trading Metrics...")
    
    if not integration_available:
        print("❌ Integration not available")
        return
    
    try:
        integration = MCPVotsNautilusIntegration()
        metrics = await integration.get_trading_metrics()
        
        print(f"   Portfolio Value: ${metrics.portfolio_value:.2f}")
        print(f"   Total Trades: {metrics.total_trades}")
        print(f"   Win Rate: {metrics.win_rate:.1f}%")
        print(f"   Total P&L: ${metrics.total_pnl:.2f}")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {metrics.max_drawdown:.1f}%")
        print(f"   Current Positions: {len(metrics.current_positions)}")
        
    except Exception as e:
        print(f"❌ Trading metrics test failed: {e}")

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration...")
    
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        print("❌ Configuration file not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        print(f"   Symbols: {len(config['symbols'])} configured")
        print(f"   Starting Budget: ${config['risk_management']['starting_budget']}")
        print(f"   Max Position Size: {config['risk_management']['max_position_size_pct']}%")
        print(f"   Confidence Threshold: {config['ai_analysis']['confidence_threshold']}")
        print(f"   Analysis Interval: {config['ai_analysis']['analysis_interval']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def display_integration_status():
    """Display integration status"""
    print("🌊 MCPVots Nautilus Trader Integration Status")
    print("=" * 60)
    
    # Check files
    files_to_check = [
        "mcpvots_nautilus_integration.py",
        "config.json",
        "setup.py",
        ".env"
    ]
    
    for file in files_to_check:
        file_path = Path(__file__).parent / file
        status = "✅" if file_path.exists() else "❌"
        print(f"{status} {file}")
    
    # Check if Nautilus Trader is available
    nautilus_path = Path(__file__).parent.parent / "nautilus_trader"
    status = "✅" if nautilus_path.exists() else "❌"
    print(f"{status} nautilus_trader/ directory")
    
    # Check Python packages
    packages_to_check = [
        "json", "sqlite3", "asyncio", "requests", "pathlib"
    ]
    
    print(f"\n📦 Python Packages:")
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")

async def run_demo():
    """Run the full demo"""
    print(f"🚀 MCPVots Nautilus Trader Demo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Display status
    display_integration_status()
    
    # Test configuration
    if not test_configuration():
        print("❌ Demo stopped due to configuration issues")
        return
    
    # Test AI analysis
    await test_ai_analysis()
    
    # Test trading metrics
    await test_trading_metrics()
    
    print("\n🎉 Demo completed!")
    print("\n📋 Next Steps:")
    print("1. Configure exchange API keys in .env file")
    print("2. Start MCPVots AGI services (DeepSeek, Gemini, MCP)")
    print("3. Run full trading loop with: python mcpvots_nautilus_integration.py")
    print("4. Monitor trades and performance in real-time")
    
    print(f"\n💰 Ready to start AI-enhanced crypto trading with $50 budget!")

if __name__ == "__main__":
    asyncio.run(run_demo())
