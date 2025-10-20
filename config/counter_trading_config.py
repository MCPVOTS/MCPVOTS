"""
Configuration for Counter-Trading Strategy
"""
# Trading Parameters
COUNTER_POSITION_SIZE_ETH = 0.0003  # Position size in ETH
PROFIT_TARGET_PERCENT = 0.02        # 2% profit target
LOSS_STOP_PERCENT = 0.05            # 5% stop loss
MAX_POSITION_USD = 10.0             # Maximum position size in USD

# Market Monitoring
PRICE_CHANGE_THRESHOLD = 0.01       # 1% price change for signal
VOLUME_THRESHOLD = 1000             # Minimum volume in USD
SIGNAL_STRENGTH_MINIMUM = 0.005    # Minimum signal strength (0.5%)

# Timing
CHECK_INTERVAL_SECONDS = 30         # Check interval in seconds
WAIT_AFTER_TRADE_SECONDS = 60       # Wait time after successful trade

# Risk Management
MAX_TRADES_PER_HOUR = 10            # Maximum trades per hour
MAX_DAILY_TRADES = 100              # Maximum daily trades
MIN_BALANCE_ETH = 0.001            # Minimum ETH balance to keep

# Strategy Settings
STRATEGY_TYPE = "counter_trading"   # Buy on sells, sell on buys
ENABLE_PROFIT_TAKING = True         # Enable automatic profit taking
ENABLE_STOP_LOSS = True             # Enable stop loss
ENABLE_VOLUME_FILTER = True         # Filter low volume signals