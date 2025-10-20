#!/usr/bin/env python3
"""
Flaunch Wallet Setup Helper
===========================

Helps you set up your separate Flaunch trading wallet
and configure it properly for independent trading.
"""

import os
import re
import json
from pathlib import Path

def create_flaunch_wallet_config():
    """Create the Flaunch wallet configuration file"""

    print("🔑 FLAUNCH WALLET SETUP")
    print("=" * 40)
    print("This will create a separate wallet for Flaunch trading")
    print("⚠️  NEVER reuse your main trading wallet!")
    print()

    # Get wallet information
    while True:
        private_key = input("Enter your Flaunch wallet PRIVATE KEY (0x...): ").strip()
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key

        if re.match(r"^0x[0-9a-fA-F]{64}$", private_key):
            break
        else:
            print("❌ Invalid private key format. Must be 64 hex characters after 0x")

    while True:
        wallet_address = input("Enter your Flaunch wallet ADDRESS (0x...): ").strip()
        if re.match(r"^0x[0-9a-fA-F]{40}$", wallet_address):
            break
        else:
            print("❌ Invalid wallet address format. Must be 40 hex characters after 0x")

    capital = input("Enter starting capital in USD (default 20.0): ").strip()
    try:
        capital = float(capital) if capital else 20.0
    except ValueError:
        capital = 20.0

    # Create configuration content
    config_content = f'''#!/usr/bin/env python3
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
FLAUNCH_PRIVATE_KEY = "{private_key}"

# Flaunch trading wallet address
FLAUNCH_WALLET_ADDRESS = "{wallet_address}"

# ================ BLOCKCHAIN CONFIGURATION ================
# Base network RPC (same as main system)
PROVIDER_URL = "https://mainnet.base.org"
CHAIN_ID = 8453

# ================ FLAUNCH TRADING PARAMETERS ================
# Capital allocation for Flaunch trading
FLAUNCH_CAPITAL_USD = {capital}  # ${capital} starting capital

# Trading limits (smaller than main system)
MAX_POSITION_SIZE_USD = 5.0   # Max $5 per trade
MAX_CONCURRENT_TRADES = 2    # Max 2 trades at once
DAILY_TRADE_LIMIT = 3        # Max 3 trades per day

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
REQUIRE_MANUAL_APPROVAL = True  # Set to True for first few runs

# ================ INTEGRATION SETTINGS ================
# Don't interfere with main trading system
ISOLATE_FROM_MAXX_TRADER = True
USE_SEPARATE_DATABASE = True
FLAUNCH_DB_FILE = "flaunch_trades.db"

# ================ EMERGENCY SETTINGS ================
EMERGENCY_STOP_LOSS = 0.8    # Stop all trading if wallet loses 80%
CIRCUIT_BREAKER_ENABLED = True
MAX_DAILY_LOSS_USD = {capital * 0.2}     # Stop trading after ${capital * 0.2:.1f} daily loss

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
        print("\\nPlease fix these issues before running the Flaunch trader.")
    else:
        print("✅ Flaunch wallet configuration is valid!")
        print(f"Wallet: {{FLAUNCH_WALLET_ADDRESS}}")
        print(f"Capital: ${{FLAUNCH_CAPITAL_USD}}")
        print("Ready to start Flaunch trading!")
'''

    # Write configuration file
    config_path = Path("flaunch_wallet_config.py")
    with open(config_path, "w") as f:
        f.write(config_content)

    print(f"✅ Configuration saved to {config_path}")
    print()
    print("🔐 SECURITY REMINDERS:")
    print("- Never share your private key")
    print("- Keep this wallet separate from main trading")
    print("- Fund only with the amount you can afford to lose")
    print("- Monitor transactions on BaseScan regularly")
    print()

    # Validate the configuration
    print("🔍 Validating configuration...")
    issues = []
    if not re.match(r"^0x[0-9a-fA-F]{64}$", private_key):
        issues.append("Private key format invalid")
    if not re.match(r"^0x[0-9a-fA-F]{40}$", wallet_address):
        issues.append("Wallet address format invalid")

    if issues:
        print("❌ Validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Configuration validated successfully!")
        return True

def show_setup_instructions():
    """Show setup instructions"""
    print()
    print("📋 FLAUNCH WALLET SETUP INSTRUCTIONS")
    print("=" * 50)
    print()
    print("1. 🔑 CREATE A NEW WALLET:")
    print("   - Open MetaMask or another wallet")
    print("   - Create a NEW wallet (don't reuse existing one!)")
    print("   - Fund it with exactly $20 worth of ETH")
    print("   - Copy the wallet address and private key")
    print()
    print("2. ⚙️ RUN SETUP SCRIPT:")
    print("   python flaunch_wallet_setup.py")
    print()
    print("3. 🧪 TEST WITH SMALL AMOUNTS:")
    print("   - Start with very small trades")
    print("   - Verify everything works")
    print("   - Monitor on BaseScan")
    print()
    print("4. 🚀 START TRADING:")
    print("   python flaunch_separate_trader.py")
    print()
    print("5. 📊 MONITOR BOTH SYSTEMS:")
    print("   - Main MAXX trader: existing dashboard")
    print("   - Flaunch trader: check flaunch_trading.log")
    print()
    print("6. 🛑 EMERGENCY STOP:")
    print("   - Close the Flaunch trader window")
    print("   - Or modify config to disable trading")
    print()

def main():
    """Main setup function"""
    print("🎯 FLAUNCH SEPARATE WALLET SETUP")
    print("This helps you create a separate wallet for Flaunch trading")
    print()

    # Show instructions first
    show_setup_instructions()

    # Ask if user wants to proceed
    response = input("Do you have a separate wallet ready? (y/n): ").strip().lower()
    if response != 'y':
        print("Please create a separate wallet first, then run this setup again.")
        return

    # Create configuration
    if create_flaunch_wallet_config():
        print()
        print("🎉 SETUP COMPLETE!")
        print()
        print("Next steps:")
        print("1. Fund your Flaunch wallet with $20 ETH")
        print("2. Test: python flaunch_separate_trader.py")
        print("3. Run both: run_both_traders.bat")
        print()
        print("💡 Remember: Start small, monitor closely, and never risk more than you can afford!")

if __name__ == "__main__":
    main()
