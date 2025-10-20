#!/usr/bin/env python3
"""
Standalone Configuration for Real MAXX Token Trading
Completely independent - no imports from other config systems

✅ VERIFIED WORKING CONFIGURATION - October 3, 2025
⚠️ DO NOT MODIFY THESE ADDRESSES - They are proven to work

POOL INFO (Confirmed via DexScreener):
Pool Address: 0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148
Liquidity: $55K (8.87 ETH + 4,465,930 MAXX)
DEX: Uniswap V4 pool (routes via KyberSwap aggregator)
Price: 0.051117 ETH per MAXX
24h Volume: $12K

WORKING ADDRESSES (DO NOT CHANGE):
- MAXX Contract: 0xFB7a83abe4F4A4E51c77B92E521390B769ff6467
- KyberSwap Router (Aggregator): 0x6131B5fae19EA4f9D964eAc0408E4408b66337b5
- WETH: 0x4200000000000000000000000000000000000006
- Trading Account: 0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9
"""

# Blockchain Configuration
PROVIDER_URL = "https://mainnet.base.org"
CHAIN_ID = 8453

# Wallet Configuration (Using the private key from start_agent.py)
ETHEREUM_PRIVATE_KEY = "0x21d095de57588dce6233047a0d558df9c6d032750331f657a1ec58d07a678432"



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

# ChromaDB Configuration - DISABLED (causes errors, not needed for trading)
# ChromaDB requires server setup and has compatibility issues
# Trading works perfectly without it - logs go to SQLite and JSON instead
CHROMADB_ENABLED = False  # Set to True only if you fix the server setup
CHROMADB_HOST = "localhost"
CHROMADB_PORT = 8000
CHROMADB_PERSIST_DIRECTORY = "./chroma_db"
CHROMADB_SETTINGS = {
    "allow_reset": True,
    "anonymized_telemetry": False,
    "chroma_db_impl": "duckdb+parquet"
}

# ChromaDB Collection Names
CHROMADB_IDENTITY_COLLECTION = "ethermax_identity_tracking"
CHROMADB_FUNDING_COLLECTION = "ethermax_funding_connections"
CHROMADB_TRADE_COLLECTION = "ethermax_maxx_trade_history"

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 100
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# ChromaDB Analysis Configuration
IDENTITY_CONFIDENCE_THRESHOLD = 0.7
COORDINATION_SCORE_THRESHOLD = 0.6
MANIPULATION_PROBABILITY_THRESHOLD = 0.7
SIMILARITY_THRESHOLD = 0.8
MAX_QUERY_RESULTS = 100

# Trading Account for Analysis
TRADING_ACCOUNT_ADDRESS = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"
MAXX_TOKEN_ADDRESS = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"

# Contract Addresses
MAXX_CONTRACT_ADDRESS = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
KYBER_ROUTER = "0x6131B5fae19EA4f9D964eAc0408E4408b66337b5"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
MAXX_ETH_POOL = "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148"

# DexScreener Configuration
DEXSCREENER_PAIR_ADDRESS = "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148"

print("SUCCESS: Standalone configuration loaded")
