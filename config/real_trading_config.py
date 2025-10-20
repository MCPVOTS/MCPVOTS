"""
Static Configuration for Real MAXX Token Trading
No environment variables - all configuration is static
"""

# Blockchain Configuration
PROVIDER_URL = "https://mainnet.base.org"
CHAIN_ID = 8453

# Wallet Configuration (REPLACE WITH YOUR ACTUAL PRIVATE KEY)
ETHEREUM_PRIVATE_KEY = "your_private_key_here"

# MAXX Token Configuration
MAXX_CONTRACT_ADDRESS = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"

# DEX Configuration (Base Chain)
# Uniswap V2 Router on Base
UNISWAP_V2_ROUTER = "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24"
# Uniswap V2 Factory on Base
UNISWAP_V2_FACTORY = "0x8909dc15e40173ff4699343b6eb8132c65e18ec6"
# WETH on Base
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
# MAXX/ETH Pool Address (provided by user)
MAXX_ETH_POOL = "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148"

# Trading Configuration
TRADING_MODE = "real"
SLIPPAGE_TOLERANCE = 0.5  # 0.5% slippage tolerance
GAS_LIMIT = 300000
GAS_PRICE_GWEI = 0.1

# Logging Configuration
LOG_LEVEL = "INFO"
TRANSACTION_LOG_FILE = "real_trading_transactions.log"

# Risk Management
MAX_POSITION_SIZE_USD = 10.0  # Maximum $10 per trade
MIN_LIQUIDITY_USD = 1000.0    # Minimum liquidity requirement

# Test Configuration
TEST_ETH_AMOUNT = 0.0003  # ~$1 USD worth of ETH (assuming ETH ~$3300)
TEST_SLIPPAGE = 1.0  # 1% slippage for test trades

# Safety Checks
ENABLE_SAFETY_CHECKS = True
REQUIRE_BALANCE_CHECK = True
REQUIRE_LIQUIDITY_CHECK = True
MAX_GAS_PRICE_GWEI = 1.0  # Maximum gas price to pay