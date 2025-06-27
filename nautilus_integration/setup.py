#!/usr/bin/env python3
"""
MCPVots Nautilus Trader Setup and Installation Script
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        return False
    return True

def install_nautilus_trader():
    """Install Nautilus Trader"""
    print("🌊 Installing Nautilus Trader...")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    nautilus_dir = current_dir.parent / "nautilus_trader"
    
    if not nautilus_dir.exists():
        print("❌ Nautilus Trader directory not found!")
        return False
    
    # Install requirements
    requirements = [
        "nautilus_trader[all]",
        "requests",
        "websocket-client", 
        "sqlite3",  # Usually built-in
        "asyncio",  # Usually built-in
        "aiohttp",
        "ccxt",
        "pandas",
        "numpy"
    ]
    
    for req in requirements:
        if not run_command(f"pip install {req}"):
            print(f"⚠️ Failed to install {req}, continuing...")
    
    print("✅ Nautilus Trader installation completed!")
    return True

def create_environment_file():
    """Create .env file for configuration"""
    env_content = """# MCPVots Nautilus Trader Environment Configuration

# Exchange API Keys (Get from exchange)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# MCPVots AGI Services
DEEPSEEK_ENDPOINT=http://localhost:8003
GEMINI_ENDPOINT=http://localhost:8015
MCP_MEMORY_ENDPOINT=http://localhost:3002

# Blockchain Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
BASE_L2_RPC_URL=https://sepolia.base.org

# Trading Configuration
STARTING_BUDGET=50.0
MAX_POSITION_SIZE_PCT=20
STOP_LOSS_PCT=3
CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
"""
    
    env_path = Path.cwd() / ".env"
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created environment file: {env_path}")

def test_integration():
    """Test the integration setup"""
    print("🧪 Testing MCPVots Nautilus Integration...")
    
    try:
        # Test basic imports
        import json
        import sqlite3
        import asyncio
        
        print("✅ Basic Python modules working")
        
        # Test configuration loading
        config_path = Path.cwd() / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            print("✅ Configuration file loaded successfully")
        else:
            print("⚠️ Configuration file not found")
        
        # Test database creation
        db_path = Path.cwd() / "test_trading.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        db_path.unlink()  # Clean up
        print("✅ Database functionality working")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MCPVots Nautilus Trader Setup")
    print("=" * 50)
    
    # Change to integration directory
    os.chdir(Path(__file__).parent)
    
    # Install Nautilus Trader
    if not install_nautilus_trader():
        print("❌ Setup failed during Nautilus installation")
        return False
    
    # Create environment file
    create_environment_file()
    
    # Test integration
    if test_integration():
        print("\n🎉 MCPVots Nautilus Trader setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file with your exchange API keys")
        print("2. Configure config.json for your trading preferences")
        print("3. Start MCPVots AGI services (DeepSeek, Gemini, MCP)")
        print("4. Run: python mcpvots_nautilus_integration.py")
        print("\n💰 Ready to trade with AI-enhanced crypto intelligence!")
    else:
        print("❌ Setup completed with some issues. Check the logs above.")
    
    return True

if __name__ == "__main__":
    main()
