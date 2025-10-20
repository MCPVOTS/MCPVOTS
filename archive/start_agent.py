"""
Start script for MAXX token trading agent with storage integration
Sets up environment and runs the agent
"""
import os
import sys
import asyncio
from storage_integrated_main import main as agent_main

def set_environment_vars():
    """
    Set environment variables for the agent
    """
    # Set the private key for the wallet if not already set
    # Security Warning: In production, never hardcode private keys
    if not os.getenv("ETHEREUM_PRIVATE_KEY"):
        print("IMPORTANT: ETHEREUM_PRIVATE_KEY not set in environment. Using default for testing only.")
        print("For production, set ETHEREUM_PRIVATE_KEY environment variable before running.")
        os.environ.setdefault("ETHEREUM_PRIVATE_KEY", "0x21d095de57588dce6233047a0d558df9c6d032750331f657a1ec58d07a678432")
    
    # Set other configuration values
    os.environ.setdefault("BUY_THRESHOLD", "0.02")
    os.environ.setdefault("SELL_THRESHOLD", "0.05")
    os.environ.setdefault("MAX_POSITION_SIZE", "0.1")
    os.environ.setdefault("STOP_LOSS_PCT", "0.03")
    os.environ.setdefault("TRADING_CYCLE_INTERVAL", "30")
    
    # Storage configuration
    os.environ.setdefault("DB_PATH", "pumpfun_ecosystem.db")
    os.environ.setdefault("VECTOR_STORE_PATH", "vector_store.pkl")
    os.environ.setdefault("MARKET_DATA_RETENTION_DAYS", "90")
    os.environ.setdefault("TRADES_RETENTION_DAYS", "365")
    os.environ.setdefault("SENTIMENT_RETENTION_DAYS", "90")
    
    print("Environment variables set for MAXX token agent with storage integration")


def main():
    """
    Main entry point
    """
    print("Starting Storage-Integrated MAXX Token Trading Agent...")
    print("Wallet Address: 0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9")
    print("MAXX Token Contract: 0xFB7a83abe4F4A4E51c77B92E521390B769ff6467")
    print("-" * 60)
    
    # Set environment variables
    set_environment_vars()
    
    # Run the agent
    try:
        asyncio.run(agent_main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()