#!/usr/bin/env python3
"""
Flaunch Trading Wallet Configuration
Separate wallet configuration for Flaunch trading operations
Independent from main MAXX trading system

✅ FLAUNCH TRADING WALLET - October 19, 2025
⚠️ This wallet is used ONLY for Flaunch token trading
⚠️ Keep separate from your main trading wallet
"""

# ================ FLAUNCH TRADING WALLET ================
# Private key for Flaunch trading wallet (SEPARATE FROM MAIN WALLET)
FLAUNCH_PRIVATE_KEY = "0x49f9954734b7c91bcbcfb101411b678cf9d8eb83e5c2b6303bb51544fa825501"

# Flaunch trading wallet address
FLAUNCH_WALLET_ADDRESS = "0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70"

# ================ BLOCKCHAIN CONFIGURATION ================
# Base network RPC (same as main system)
PROVIDER_URL = "https://mainnet.base.org"
CHAIN_ID = 8453

# ================ FLAUNCH TRADING PARAMETERS ================
# Capital allocation for Flaunch trading
FLAUNCH_CAPITAL_USD = 15.0  # $15 trading capital (leaving $5 ETH reserve)

# ETH Reserve (ALWAYS MAINTAIN)
ETH_RESERVE_USD = 5.0  # Always keep $5 worth of ETH in wallet

# Trading limits (smaller than main system)
MAX_POSITION_SIZE_USD = 3.0   # Max $3 per trade (conservative)
MAX_CONCURRENT_TRADES = 1    # Max 1 trade at a time (very conservative)
DAILY_TRADE_LIMIT = 2        # Max 2 trades per day

# Risk management (conservative)
STOP_LOSS_PCT = 0.5          # 50% stop loss
PROFIT_TARGET_PCT = 2.5      # 250% profit target
SLIPPAGE_TOLERANCE = 1.0     # 1% slippage

# ================ FLAUNCH API CONFIGURATION ================
FLAUNCH_API_BASE_URL = "https://web2-api.flaunch.gg"
FLAUNCH_API_TIMEOUT = 30     # API timeout in seconds

# ================ MONITORING & LOGGING ================
FLAUNCH_LOG_LEVEL = "INFO"
FLAUNCH_LOG_FILE = "flaunch_trading.log"
FLAUNCH_TRANSACTION_LOG = "flaunch_transactions.log"

# ================ SAFETY CHECKS ================
ENABLE_FLAUNCH_SAFETY_CHECKS = True
CONFIRM_LARGE_TRADES = True   # Confirm trades > $2
REQUIRE_MANUAL_APPROVAL = False  # Set to True for first few runs

# ================ INTEGRATION SETTINGS ================
# Don't interfere with main trading system
ISOLATE_FROM_MAXX_TRADER = True
USE_SEPARATE_DATABASE = True
FLAUNCH_DB_FILE = "flaunch_trades.db"

# ================ EMERGENCY SETTINGS ================
EMERGENCY_STOP_LOSS = 0.6    # Stop all trading if wallet loses 60% of trading capital
CIRCUIT_BREAKER_ENABLED = True
MAX_DAILY_LOSS_USD = 3.0     # Stop trading after $3 daily loss (20% of capital)
ETH_RESERVE_PROTECTION = True  # Never touch the $5 ETH reserve

# ================ SETUP INSTRUCTIONS ================
"""
TO SET UP YOUR FLAUNCH TRADING WALLET:

1. Create a new wallet in MetaMask or similar (NEVER reuse main wallet!)
2. Fund it with exactly $20 worth of ETH
3. Get your private key (export carefully, keep secure)
4. Replace FLAUNCH_PRIVATE_KEY above with your new wallet's private key
5. Replace FLAUNCH_WALLET_ADDRESS with your new wallet's address
6. Save this file as flaunch_wallet_config.py
7. Run: python flaunch_separate_trader.py

⚠️ SECURITY NOTES:
- Never share your private key
- Keep this wallet separate from your main trading wallet
- Start with small amounts while testing
- Monitor transactions on BaseScan regularly
"""

# ================ VALIDATION ================
def validate_config():
    """Validate that configuration is properly set up"""
    issues = []

    if FLAUNCH_PRIVATE_KEY == "0xYOUR_FLAUNCH_WALLET_PRIVATE_KEY_HERE":
        issues.append("FLAUNCH_PRIVATE_KEY not set - replace with real private key")

    if FLAUNCH_WALLET_ADDRESS == "0xYOUR_FLAUNCH_WALLET_ADDRESS_HERE":
        issues.append("FLAUNCH_WALLET_ADDRESS not set - replace with real wallet address")

    if not FLAUNCH_PRIVATE_KEY.startswith("0x"):
        issues.append("FLAUNCH_PRIVATE_KEY must start with 0x")

    if not FLAUNCH_WALLET_ADDRESS.startswith("0x"):
        issues.append("FLAUNCH_WALLET_ADDRESS must start with 0x")

    return issues

# Run validation when imported
if __name__ == "__main__":
    issues = validate_config()
    if issues:
        print("❌ Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues before running the Flaunch trader.")
    else:
        print("✅ Flaunch wallet configuration is valid!")
        print(f"Wallet: {FLAUNCH_WALLET_ADDRESS}")
        print(f"Capital: ${FLAUNCH_CAPITAL_USD}")
        print("Ready to start Flaunch trading!")
