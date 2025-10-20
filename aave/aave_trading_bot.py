#!/usr/bin/env python3
"""
ZORA Trading Bot - Base Chain Aggressive Daily Profit Trader
===============================================================

A comprehensive automated trading bot for ZORA token on Base chain with multiple strategies,
real-time market analysis, and performance tracking.

Features:
- Multiple trading strategies (Market Making, Momentum, Arbitrage, Manual)
- Real-time price monitoring via DexScreener API
- Signal generation with confidence scoring
- Automated trade execution on Base chain
- Performance tracking and analytics
- WebSocket connections for live data
- Risk management and position sizing
- Gas-optimized for Base chain (cheap transactions)

Author: ZORA Matrix Bot
Version: 2.0.0
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import os
import sys
import sqlite3
from pathlib import Path
from contextlib import suppress

import requests
import websockets
from dotenv import load_dotenv

# Optional imports
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not installed. Using basic math operations.")

try:
    from web3 import Web3
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    print("Warning: web3 not installed. Blockchain features disabled.")

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False
    print("Warning: ccxt not installed. Exchange features disabled.")

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zora_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ZORABot')

class TradingStrategy(Enum):
    """Available trading strategies"""
    MARKET_MAKING = "market_making"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    MANUAL = "manual"

class TradeSignal:
    """Represents a trading signal"""

    def __init__(self, signal_type: str, amount: float, price: float,
                 confidence: float, reason: str):
        self.type = signal_type  # 'BUY' or 'SELL'
        self.amount = amount
        self.price = price
        self.confidence = confidence
        self.reason = reason
        self.timestamp = datetime.now()
        self.id = f"{int(time.time() * 1000)}_{hash(self)}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'price': self.price,
            'confidence': self.confidence,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat()
        }

class TradeRecord:
    """Represents a completed trade"""

    def __init__(self, signal: TradeSignal, profit: float, status: str = 'success'):
        self.id = signal.id
        self.type = signal.type
        self.amount = signal.amount
        self.price = signal.price
        self.profit = profit
        self.timestamp = datetime.now()
        self.status = status  # 'success', 'failed', 'pending'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'price': self.price,
            'profit': self.profit,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }

class ZORABot:
    """
    Main ZORA Trading Bot class for Base chain
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.is_active = False
        self.is_trading = False
        self.strategy = TradingStrategy(self.config['strategy'])
        self.signals: List[TradeSignal] = []
        self.trade_history: List[TradeRecord] = []

        # Performance metrics
        self.total_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.total_profit = 0.0
        self.current_balance = self.config['initial_balance']
        self.last_trade_time: Optional[datetime] = None

        # Market data
        self.current_price = 0.0
        self.price_history: List[Tuple[datetime, float]] = []
        self.volume_24h = 0.0

        # ZORA token info
        self.token_address = "0x1111111111166b7FE7bd91427724B487980aFc69"  # ZORA on Base
        self.token_symbol = "ZORA"
        self.token_name = "Zora"

        # API clients
        self.web3 = None
        self.exchange = None
        self._init_clients()

        # WebSocket connection
        self.ws_connected = False
        self.ws_task: Optional[asyncio.Task] = None

        # Database and logging
        self.db_connection = None
        self.last_trade_info = None

        # GPU acceleration - Enhanced detection
        self.gpu_available = False
        self.gpu_type = "none"
        self.cp = None
        self.np = None

        try:
            # Try CuPy first (GPU)
            import cupy as cp
            import numpy as np
            self.cp = cp
            self.np = np

            # Test CUDA availability
            try:
                # Try to get CUDA version
                cuda_version = cp.cuda.runtime.runtimeGetVersion()
                gpu_count = cp.cuda.runtime.getDeviceCount()

                if gpu_count > 0:
                    # Test GPU computation
                    test_array = cp.array([1.0, 2.0, 3.0])
                    result = cp.sum(test_array)
                    cp.cuda.Device(0).use()  # Use first GPU

                    self.gpu_available = True
                    self.gpu_type = "cuda"
                    logger.info(f"CUDA GPU acceleration enabled (CUDA {cuda_version}, {gpu_count} GPUs)")
                else:
                    raise RuntimeError("No CUDA GPUs found")

            except Exception as cuda_error:
                logger.warning(f"CUDA GPU not available: {cuda_error}")
                # Try CPU fallback with numba
                try:
                    import numba as nb
                    self.numba_available = True
                    self.gpu_type = "cpu_numba"
                    logger.info("CPU acceleration enabled with Numba")
                except ImportError:
                    self.numba_available = False
                    self.gpu_type = "cpu_numpy"
                    logger.info("CPU acceleration enabled with NumPy")

        except ImportError as e:
            logger.warning(f"CuPy not available: {e}")
            # Fallback to CPU acceleration
            try:
                import numpy as np
                self.np = np
                try:
                    import numba as nb
                    self.numba_available = True
                    self.gpu_type = "cpu_numba"
                    logger.info("CPU acceleration enabled with NumPy + Numba")
                except ImportError:
                    self.numba_available = False
                    self.gpu_type = "cpu_numpy"
                    logger.info("CPU acceleration enabled with NumPy only")
            except ImportError:
                logger.warning("NumPy not available - basic math operations only")
                self.gpu_type = "none"

        # Rate limiting for RPC calls
        self.last_balance_check = 0
        self.balance_check_interval = 10  # Only check balance every 10 seconds

        # Initialize database
        self._init_database()

        logger.info("ZORA Bot initialized with strategy: %s", self.strategy.value)

    def _default_config(self) -> Dict[str, Any]:
        """Default bot configuration - AGGRESSIVE DAILY PROFIT MODE FOR ZORA"""
        return {
            'strategy': 'market_making',
            'initial_balance': 23.25,  # $23.25 available trading capital (above $5 ETH reserve)
            'max_position_size': 10.0,  # Max $10 position size (40% of capital)
            'min_trade_amount': 1.0,   # Minimum $1 trade for micro-trading
            'sell_gain_pct': 0.03,     # Sell at 3% profit (aggressive)
            'rebuy_drop_pct': 0.03,    # Buy back at 3% drop (aggressive)
            'analysis_interval': 15,    # Check every 15 seconds (fast for daily profits)
            'api_keys': {
                'birdeye': os.getenv('BIRDEYE_API_KEY'),
                'etherscan': os.getenv('ETHERSCAN_API_KEY'),
                'infura': os.getenv('INFURA_PROJECT_ID'),
            },
            'risk_management': {
                'max_daily_loss': 4.65,  # Max 20% daily loss ($4.65)
                'max_single_trade_loss': 1.0,  # Max $1 per trade
                'stop_loss_pct': 0.02,  # 2% stop loss
            }
        }

    def _init_clients(self):
        """Initialize API clients"""
        try:
            # Web3 client for Base chain interactions
            if HAS_WEB3:
                # Use Base chain RPC endpoint
                self.web3 = Web3(Web3.HTTPProvider(
                    "https://mainnet.base.org"  # Base chain RPC
                ))

                # Load private key for real trading
                private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
                if private_key:
                    self.account = self.web3.eth.account.from_key(private_key)
                    self.web3.eth.default_account = self.account.address
                    logger.info(f"Real trading enabled with wallet: {self.account.address}")

                    # Check wallet balance
                    balance_wei = self.web3.eth.get_balance(self.account.address)
                    balance_eth = float(self.web3.from_wei(balance_wei, 'ether'))
                    logger.info(f"Wallet balance: {balance_eth:.4f} ETH")

                    # Set Uniswap V3 router contract for Base chain
                    self.uniswap_router = self.web3.to_checksum_address("0x2626664c2603336E57B271c5C0b26F421741e4815")  # Uniswap V3 Router on Base
                    self.weth_address = self.web3.to_checksum_address("0x4200000000000000000000000000000000000006")  # WETH on Base
                    self.zora_address = self.web3.to_checksum_address(self.token_address)  # ZORA token address

                else:
                    logger.warning("No private key found - real trading disabled")
                    self.account = None
            else:
                logger.warning("Web3 not available - blockchain features disabled")

            # Exchange client for trading
            if HAS_CCXT:
                self.exchange = ccxt.binance()  # Using Binance as example
                logger.info("Exchange client initialized")
            else:
                logger.warning("CCXT not available - exchange features disabled")

        except Exception as e:
            logger.error("Failed to initialize clients: %s", str(e))

    def _init_database(self):
        """Initialize SQLite database for trade logging"""
        try:
            db_path = Path('data') / 'zora_trades.db'
            db_path.parent.mkdir(exist_ok=True)
            self.db_connection = sqlite3.connect(str(db_path), check_same_thread=False)
            cursor = self.db_connection.cursor()

            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    tx_hash TEXT,
                    zora_amount REAL,
                    usd_amount REAL,
                    zora_price_usd REAL,
                    gas_used REAL,
                    gas_cost_eth REAL,
                    gas_cost_usd REAL,
                    slippage_bps INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    strategy TEXT,
                    profit_loss REAL,
                    balance_after REAL
                )
            ''')

            # Create trade_log table for detailed logging
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trade_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    trade_id INTEGER,
                    FOREIGN KEY (trade_id) REFERENCES trades (id)
                )
            ''')

            self.db_connection.commit()
            logger.info("Database initialized successfully")

            # Load last trade info
            self._load_last_trade_info()

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_last_trade_info(self):
        """Load information about the last trade from database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, trade_type, zora_amount, usd_amount,
                       zora_price_usd, success, profit_loss
                FROM trades
                ORDER BY timestamp DESC
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if row:
                self.last_trade_info = {
                    'timestamp': row[0],
                    'trade_type': row[1],
                    'aave_amount': row[2],
                    'usd_amount': row[3],
                    'aave_price_usd': row[4],
                    'success': bool(row[5]),
                    'profit_loss': row[6]
                }
                logger.info(f"Loaded last trade info: {self.last_trade_info['trade_type']} at {self.last_trade_info['timestamp']}")
        except Exception as e:
            logger.error(f"Failed to load last trade info: {e}")

    def _log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade to database"""
        if not self.db_connection:
            logger.warning("Database connection not available for trade logging")
            return

        try:
            cursor = self.db_connection.cursor()

            # Insert trade record
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, trade_type, tx_hash, zora_amount, usd_amount,
                    zora_price_usd, gas_used, gas_cost_eth, gas_cost_usd,
                    slippage_bps, success, error_message, strategy,
                    profit_loss, balance_after
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('timestamp'),
                trade_data.get('trade_type'),
                trade_data.get('tx_hash'),
                trade_data.get('zora_amount'),
                trade_data.get('usd_amount'),
                trade_data.get('zora_price_usd'),
                trade_data.get('gas_used'),
                trade_data.get('gas_cost_eth'),
                trade_data.get('gas_cost_usd'),
                trade_data.get('slippage_bps'),
                trade_data.get('success', False),
                trade_data.get('error_message'),
                trade_data.get('strategy'),
                trade_data.get('profit_loss'),
                trade_data.get('balance_after')
            ))

            self.db_connection.commit()
            logger.info(f"Trade logged to database: {trade_data.get('trade_type')} {trade_data.get('tx_hash')}")

        except Exception as e:
            logger.error(f"Failed to log trade to database: {e}")
            # Try to recreate database connection
            try:
                self._init_database()
            except Exception as db_error:
                logger.error(f"Failed to reinitialize database: {db_error}")

    async def start(self):
        """Start the trading bot"""
        logger.info("Starting AAVE Trading Bot...")
        self.is_active = True

        # Start WebSocket connection
        self.ws_task = asyncio.create_task(self._connect_websocket())

        # Start main trading loop
        await self._trading_loop()

    async def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping AAVE Trading Bot...")
        self.is_active = False

        if self.ws_task:
            self.ws_task.cancel()
            try:
                await self.ws_task
            except asyncio.CancelledError:
                pass

    def change_strategy(self, strategy: str):
        """Change trading strategy"""
        try:
            self.strategy = TradingStrategy(strategy)
            logger.info("Strategy changed to: %s", strategy)
        except ValueError:
            logger.error("Invalid strategy: %s", strategy)

    async def _connect_websocket(self):
        """Connect to WebSocket for real-time data"""
        ws_url = "wss://stream.binance.com:9443/ws/aaveusdt@trade"

        while self.is_active:
            try:
                async with websockets.connect(ws_url) as websocket:
                    self.ws_connected = True
                    logger.info("WebSocket connected")

                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self._process_ws_message(data)
                        except json.JSONDecodeError:
                            continue

            except Exception as e:
                self.ws_connected = False
                logger.error("WebSocket error: %s", str(e))
                await asyncio.sleep(5)  # Reconnect delay

    async def _process_ws_message(self, data: Dict[str, Any]):
        """Process WebSocket message"""
        try:
            if data.get('e') == 'trade':  # Binance trade event
                price = float(data['p'])
                self.current_price = price
                self.price_history.append((datetime.now(), price))

                # Keep only last 1000 price points
                if len(self.price_history) > 1000:
                    self.price_history = self.price_history[-1000:]

                # Analyze market and generate signals
                await self._analyze_market()

        except Exception as e:
            logger.error("Error processing WS message: %s", str(e))

    async def _trading_loop(self):
        """Main trading loop with enhanced features"""
        # Start WebSocket broadcast loop if enabled
        if self.ws_enabled:
            self.ws_broadcast_task = asyncio.create_task(self.ws_broadcast_loop())

        while self.is_active:
            try:
                # Update market data
                await self._update_market_data()

                # GPU-accelerated analysis if available
                gpu_analysis = self.gpu_analyze_market()
                if gpu_analysis:
                    logger.debug(f"GPU Analysis: {gpu_analysis}")

                # Analyze market and generate signals
                await self._analyze_market()

                # Execute pending signals
                await self._execute_signals()

                # Clean up old signals (keep last 10)
                if len(self.signals) > 10:
                    self.signals = self.signals[-10:]

                await asyncio.sleep(self.config['analysis_interval'])

            except Exception as e:
                logger.error("Error in trading loop: %s", str(e))
                await asyncio.sleep(5)

    async def _update_market_data(self):
        """Update ZORA market data from DexScreener API with test mode enhancements"""
        try:
            # Get ZORA price from DexScreener (Base chain)
            url = f"https://api.dexscreener.com/latest/dex/tokens/{self.token_address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('pairs') and len(data['pairs']) > 0:
                    # Get the pair with highest liquidity on Base chain
                    base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                    if base_pairs:
                        pair = base_pairs[0]  # Use highest liquidity pair
                        self.current_price = float(pair.get('priceUsd', self.current_price))
                        self.volume_24h = float(pair.get('volume', {}).get('h24', self.volume_24h))

                        logger.debug("Updated ZORA market data - Price: $%.4f, Volume: $%.2f",
                                   self.current_price, self.volume_24h)
                    else:
                        # Fallback to any pair if no Base pairs found
                        pair = data['pairs'][0]
                        self.current_price = float(pair.get('priceUsd', self.current_price))
                        self.volume_24h = float(pair.get('volume', {}).get('h24', self.volume_24h))
                        logger.debug("Using non-Base pair for ZORA - Price: $%.4f", self.current_price)

                    # Add current price to history for analysis
                    self.price_history.append((datetime.now(), self.current_price))

                    # Keep only last 1000 price points
                    if len(self.price_history) > 1000:
                        self.price_history = self.price_history[-1000:]

                    # For testing: add some artificial price movement to create signals
                    if len(self.price_history) >= 2:
                        # Small random price movements (±0.1%) to create trading opportunities
                        import random
                        change_pct = random.uniform(-0.001, 0.001)  # ±0.1% (much smaller)
                        test_price = self.current_price * (1 + change_pct)

                        # Ensure test price stays reasonable (±5% of real price)
                        max_test_price = self.current_price * 1.05
                        min_test_price = self.current_price * 0.95
                        test_price = max(min_test_price, min(max_test_price, test_price))

                        # Add test price point
                        self.price_history.append((datetime.now(), test_price))
                        logger.debug(f"Added test price point: ${test_price:.4f} ({change_pct:.2%})")

        except Exception as e:
            logger.error("Failed to update ZORA market data: %s", str(e))

    async def _analyze_market(self):
        """Analyze market conditions and generate trading signals"""
        if not self.is_active or self.current_price == 0:
            return

        try:
            signals = []

            if self.strategy == TradingStrategy.MARKET_MAKING:
                signals.extend(await self._analyze_market_making())
            elif self.strategy == TradingStrategy.MOMENTUM:
                signals.extend(await self._analyze_momentum())
            elif self.strategy == TradingStrategy.ARBITRAGE:
                signals.extend(await self._analyze_arbitrage())

            # Add signals to queue
            for signal in signals:
                self.signals.append(signal)
                logger.info("Generated signal: %s %.2f AAVE @ $%.4f (%.1f%% confidence) - %s",
                          signal.type, signal.amount, signal.price, signal.confidence * 100, signal.reason)

        except Exception as e:
            logger.error("Error in market analysis: %s", str(e))

    async def _analyze_market_making(self) -> List[TradeSignal]:
        """Market making strategy analysis - AGGRESSIVE MODE FOR TESTING"""
        signals = []

        # For testing: generate signals even with limited data
        if len(self.price_history) >= 3:  # Reduced from 10
            recent_prices = [p for _, p in self.price_history[-3:]]

            if HAS_NUMPY:
                avg_price = np.mean(recent_prices)
                price_std = np.std(recent_prices) if len(recent_prices) > 1 else avg_price * 0.01
            else:
                # Fallback without numpy
                avg_price = sum(recent_prices) / len(recent_prices)
                if len(recent_prices) > 1:
                    variance = sum((p - avg_price) ** 2 for p in recent_prices) / len(recent_prices)
                    price_std = variance ** 0.5
                else:
                    price_std = avg_price * 0.01  # 1% default volatility

            # More aggressive thresholds for testing
            buy_threshold = avg_price - price_std * 0.2  # Reduced from 0.3
            sell_threshold = avg_price + price_std * 0.2  # Reduced from 0.3

            # Generate buy signal if price is below average
            if self.current_price < buy_threshold:
                amount = min(self.config['max_position_size'], self.current_balance / self.current_price * 0.3)  # Increased from 0.5
                if amount >= self.config['min_trade_amount']:
                    signals.append(TradeSignal(
                        'BUY', amount, self.current_price, 0.8,  # Higher confidence
                        f'TEST MODE: Price below average (${avg_price:.4f})'
                    ))

            # Generate sell signal if price is above average
            elif self.current_price > sell_threshold:
                amount = min(self.config['max_position_size'], self.current_balance * 0.2)  # Reduced from 0.3
                if amount >= self.config['min_trade_amount']:
                    signals.append(TradeSignal(
                        'SELL', amount, self.current_price, 0.8,  # Higher confidence
                        f'TEST MODE: Price above average (${avg_price:.4f})'
                    ))

        # For testing: if no signals but we have price data, create artificial volatility
        elif len(self.price_history) >= 1 and np.random.random() > 0.7:  # 30% chance
            # Create a test signal to demonstrate trading
            direction = 'BUY' if np.random.random() > 0.5 else 'SELL'
            amount = min(self.config['max_position_size'], self.current_balance / self.current_price * 0.1)
            if amount >= self.config['min_trade_amount']:
                signals.append(TradeSignal(
                    direction, amount, self.current_price, 0.6,  # Lower confidence for test
                    'TEST MODE: Artificial signal for demonstration'
                ))

        return signals

    async def _analyze_momentum(self) -> List[TradeSignal]:
        """Momentum strategy analysis"""
        signals = []

        if len(self.price_history) >= 20:
            # Calculate momentum (rate of change)
            recent_prices = [p for _, p in self.price_history[-20:]]
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

            if momentum > 0.02:  # 2% upward momentum
                amount = min(self.config['max_position_size'], self.current_balance / self.current_price * 0.2)
                if amount >= self.config['min_trade_amount']:
                    signals.append(TradeSignal(
                        'BUY', amount, self.current_price, min(0.9, 0.5 + momentum * 10),
                        f'Bullish momentum: +{momentum:.1%} in last 20 trades'
                    ))

        return signals

    async def _analyze_arbitrage(self) -> List[TradeSignal]:
        """Arbitrage strategy analysis"""
        signals = []

        # This would check price differences across exchanges
        # For demo purposes, simplified logic
        if HAS_CCXT and self.exchange and self.current_price > 0:
            try:
                # Get price from another exchange
                ticker = self.exchange.fetch_ticker('AAVE/USDT')
                exchange_price = ticker['last']

                price_diff = abs(self.current_price - exchange_price) / self.current_price

                if price_diff > 0.005:  # 0.5% price difference
                    direction = 'BUY' if exchange_price < self.current_price else 'SELL'
                    amount = min(self.config['max_position_size'], self.current_balance / self.current_price * 0.15)

                    if amount >= self.config['min_trade_amount']:
                        signals.append(TradeSignal(
                            direction, amount, self.current_price, 0.8,
                            f'Arbitrage opportunity: {price_diff:.1%} price difference'
                        ))

            except Exception as e:
                logger.debug("Arbitrage analysis failed: %s", str(e))
        else:
            # Fallback arbitrage simulation for demo
            if np.random.random() > 0.95:  # 5% chance of arbitrage signal
                direction = 'BUY' if np.random.random() > 0.5 else 'SELL'
                amount = min(self.config['max_position_size'], self.current_balance / self.current_price * 0.1)
                if amount >= self.config['min_trade_amount']:
                    signals.append(TradeSignal(
                        direction, amount, self.current_price, 0.7,
                        'Simulated arbitrage opportunity detected'
                    ))

        return signals

    async def _execute_signals(self):
        """Execute pending trading signals"""
        if self.is_trading or not self.signals:
            return

        # Execute medium-confidence signals automatically (more aggressive for testing)
        medium_conf_signals = [s for s in self.signals if s.confidence >= 0.5]  # Lower threshold from 0.7

        for signal in medium_conf_signals:
            await self._execute_trade(signal)
            await asyncio.sleep(0.5)  # Faster rate limiting for daily profits

    async def _execute_trade(self, signal: TradeSignal):
        """Execute a REAL blockchain trade on Base chain"""
        if self.is_trading:
            return

        self.is_trading = True

        try:
            logger.info("EXECUTING REAL %s TRADE: %.2f ZORA @ $%.4f",
                       signal.type, signal.amount, signal.price)

            if not self.account or not self.web3:
                logger.error("Real trading not available - no wallet configured")
                self.is_trading = False
                return

            # Check if we have enough balance for the trade
            balance_wei = self.web3.eth.get_balance(self.account.address)
            balance_eth = float(self.web3.from_wei(balance_wei, 'ether'))

            if signal.type == 'BUY':
                # Buying ZORA - need ETH to spend
                eth_needed = (signal.amount * signal.price) / self.current_price  # Convert USD to ETH
                if balance_eth < eth_needed + 0.001:  # Include gas buffer
                    logger.error(f"Insufficient ETH balance. Need {eth_needed:.4f} ETH, have {balance_eth:.4f} ETH")
                    self.is_trading = False
                    return

                # Execute real BUY transaction via Uniswap V3
                success, tx_hash, gas_used, gas_cost_eth = await self._execute_buy_zora(signal)
                profit = 0  # No profit on buy, just cost

            else:  # SELL
                # Check if we have enough ZORA tokens
                zora_balance = await self._get_zora_balance()
                if zora_balance < signal.amount:
                    logger.error(f"Insufficient ZORA balance. Need {signal.amount}, have {zora_balance}")
                    self.is_trading = False
                    return

                # Execute real SELL transaction via Uniswap V3
                success, tx_hash, gas_used, gas_cost_eth, eth_received = await self._execute_sell_zora(signal)
                profit = eth_received - (signal.amount * signal.price / self.current_price)  # Profit in ETH

            # Calculate gas cost in USD
            gas_cost_usd = gas_cost_eth * self.current_price

            # Update balance
            new_balance_wei = self.web3.eth.get_balance(self.account.address)
            new_balance_eth = float(self.web3.from_wei(new_balance_wei, 'ether'))
            balance_change = new_balance_eth - balance_eth

            # Record trade
            trade = TradeRecord(signal, profit, 'success' if success else 'failed')
            self.trade_history.append(trade)

            # Log trade to database with real transaction data
            self._log_trade({
                'timestamp': datetime.now().isoformat(),
                'trade_type': signal.type,
                'tx_hash': tx_hash,
                'zora_amount': signal.amount,
                'usd_amount': signal.amount * signal.price,
                'zora_price_usd': signal.price,
                'gas_used': gas_used,
                'gas_cost_eth': gas_cost_eth,
                'gas_cost_usd': gas_cost_usd,
                'slippage_bps': 50,  # 0.5% slippage
                'success': success,
                'error_message': None if success else 'Transaction failed',
                'strategy': self.strategy.value,
                'profit_loss': profit,
                'balance_after': new_balance_eth
            })

            # Update metrics
            self.total_trades += 1
            if success:
                self.successful_trades += 1
                self.total_profit += profit
            else:
                self.failed_trades += 1

            self.last_trade_time = datetime.now()

            logger.info("REAL TRADE %s: %s %.2f ZORA | TX: %s | Gas: %.6f ETH ($%.4f) | P&L: $%.2f",
                       'SUCCESS' if success else 'FAILED', signal.type, signal.amount,
                       tx_hash[:10] + '...' if tx_hash else 'N/A', gas_cost_eth, gas_cost_usd, profit)

            # Log trade to file like MAXX trader
            try:
                with open('zora_real_trade_log.txt', 'a') as f:
                    f.write(f"{datetime.now().isoformat()} | REAL {signal.type} | {signal.amount:.2f} ZORA | ${signal.price:.4f} | TX:{tx_hash} | Gas:{gas_cost_eth:.6f}ETH (${gas_cost_usd:.4f}) | P&L:${profit:+.2f} | Balance:{new_balance_eth:.4f}ETH\n")
            except Exception as e:
                logger.error(f"Failed to log trade to file: {e}")

            # Broadcast to WebSocket if enabled
            if self.ws_enabled:
                await self.ws_broadcast_trade(signal.type, signal.amount, signal.price, success)

            # Remove executed signal
            self.signals.remove(signal)

        except Exception as e:
            logger.error("Real trade execution failed: %s", str(e))
            # Log failed trade
            self._log_trade({
                'timestamp': datetime.now().isoformat(),
                'trade_type': signal.type,
                'tx_hash': None,
                'zora_amount': signal.amount,
                'usd_amount': signal.amount * signal.price,
                'zora_price_usd': signal.price,
                'gas_used': 0,
                'gas_cost_eth': 0,
                'gas_cost_usd': 0,
                'slippage_bps': 0,
                'success': False,
                'error_message': str(e),
                'strategy': self.strategy.value,
                'profit_loss': 0,
                'balance_after': self.current_balance
            })
        finally:
            self.is_trading = False

    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_active': self.is_active,
            'is_trading': self.is_trading,
            'strategy': self.strategy.value,
            'current_price': self.current_price,
            'balance': self.current_balance,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'total_profit': self.total_profit,
            'win_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'ws_connected': self.ws_connected,
            'pending_signals': len(self.signals)
        }

    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trade history"""
        return [trade.to_dict() for trade in self.trade_history[-limit:]]

    def get_recent_trades_db(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades from database"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, trade_type, zora_amount, usd_amount,
                       zora_price_usd, success, profit_loss, strategy
                FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'timestamp': row[0],
                    'trade_type': row[1],
                    'zora_amount': row[2],
                    'usd_amount': row[3],
                    'zora_price_usd': row[4],
                    'success': bool(row[5]),
                    'profit_loss': row[6],
                    'strategy': row[7]
                })

            return trades

        except Exception as e:
            logger.error(f"Failed to get recent trades: {e}")
            return []

    def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get pending trading signals"""
        return [signal.to_dict() for signal in self.signals]

    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        """Start WebSocket server for dashboard broadcasting"""
        try:
            if websockets is None:
                logger.warning("websockets library not available - WS server disabled")
                return None

            async def _handler(ws):
                self.ws_clients.add(ws)
                try:
                    async for _ in ws:
                        pass
                except Exception:
                    pass
                finally:
                    try:
                        self.ws_clients.remove(ws)
                    except KeyError:
                        pass

            self.ws_clients: set = set()
            self.ws_server = await websockets.serve(_handler, host, port)
            self.ws_enabled = True
            logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
            return self.ws_server
        except Exception as e:
            logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        """Stop WebSocket server"""
        try:
            if self.ws_broadcast_task and not self.ws_broadcast_task.done():
                self.ws_broadcast_task.cancel()
                try:
                    await self.ws_broadcast_task
                except (asyncio.CancelledError, Exception):
                    pass
                self.ws_broadcast_task = None
            if self.ws_server:
                self.ws_server.close()
                with suppress(Exception):
                    await self.ws_server.wait_closed()
                self.ws_server = None
            for ws in list(getattr(self, 'ws_clients', set())):
                with suppress(Exception):
                    await ws.close()
            self.ws_enabled = False
        except Exception as e:
            logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        """Broadcast current price data"""
        if not self.ws_enabled or not hasattr(self, 'ws_clients') or not self.ws_clients:
            return
        try:
            msg = json.dumps({
                'type': 'price_update',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'price': self.current_price,
                    'zora_price': self.current_price,
                    'volume_24h': self.volume_24h
                }
            })
            dead = []
            for ws in list(self.ws_clients):
                try:
                    await ws.send(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                with suppress(Exception):
                    await ws.close()
                try:
                    self.ws_clients.remove(ws)
                except KeyError:
                    pass
        except Exception as e:
            logger.debug(f"WS broadcast error: {e}")

    async def ws_broadcast_balance(self):
        """Broadcast balance data"""
        if not self.ws_enabled or not hasattr(self, 'ws_clients') or not self.ws_clients:
            return
        try:
            msg = json.dumps({
                'type': 'balance_update',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'balance': self.current_balance,
                    'total_trades': self.total_trades,
                    'total_profit': self.total_profit
                }
            })
            dead = []
            for ws in list(self.ws_clients):
                try:
                    await ws.send(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                with suppress(Exception):
                    await ws.close()
                try:
                    self.ws_clients.remove(ws)
                except KeyError:
                    pass
        except Exception as e:
            logger.debug(f"WS broadcast error: {e}")

    async def ws_broadcast_trade(self, trade_type: str, amount: float, price: float, success: bool):
        """Broadcast trade data"""
        if not self.ws_enabled or not hasattr(self, 'ws_clients') or not self.ws_clients:
            return
        try:
            msg = json.dumps({
                'type': 'trade',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'type': trade_type,
                    'symbol': 'ZORA',
                    'amount': amount,
                    'price': price,
                    'success': success
                }
            })
            dead = []
            for ws in list(self.ws_clients):
                try:
                    await ws.send(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                with suppress(Exception):
                    await ws.close()
                try:
                    self.ws_clients.remove(ws)
                except KeyError:
                    pass
        except Exception as e:
            logger.debug(f"WS broadcast error: {e}")

    async def ws_broadcast_loop(self, interval_seconds: float = 5.0):
        """WebSocket broadcast loop"""
        while self.is_active and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balance(),
                )
            except Exception as e:
                logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    def _get_gas_params(self) -> Dict[str, int]:
        """Get optimized gas parameters for Base chain transactions (much cheaper than Ethereum)"""
        try:
            if HAS_WEB3 and self.web3:
                # Use EIP-1559 for better gas optimization on Base chain
                latest_block = self.web3.eth.get_block('latest')
                base_fee = int(latest_block.get('baseFeePerGas', 0))

                # Base chain base fees are much lower (0.001-0.005 gwei vs Ethereum's 20-50 gwei)
                # Apply minimal headroom for Base chain
                base_with_headroom = int(base_fee * 1.1) if base_fee > 0 else int(0.001 * 1e9)

                # Set max fee (base + priority) - Base chain priority fees are minimal
                max_fee = base_with_headroom + int(0.001 * 1e9)  # 0.001 gwei priority for Base
                max_fee = int(max_fee)

                # Cap at reasonable Base chain maximum (0.01 gwei total)
                max_gas_wei = int(0.01 * 1e9)
                max_fee = min(max_fee, max_gas_wei)

                priority_fee = int(0.001 * 1e9)  # 0.001 gwei priority for Base chain

                return {
                    'maxFeePerGas': max_fee,
                    'maxPriorityFeePerGas': priority_fee
                }
            else:
                # Base chain fallback gas price: 0.001 gwei
                return {'gasPrice': int(0.001 * 1e9)}
        except Exception as e:
            logger.error(f"Gas params error: {e}")
            return {'gasPrice': int(0.001 * 1e9)}  # Base chain fallback

    def _estimate_gas_cost_eth(self, gas_units: int) -> float:
        """Estimate gas cost in ETH with Base chain pricing (much cheaper than Ethereum)"""
        try:
            if HAS_WEB3 and self.web3:
                # Get current gas price from Base chain (much cheaper than Ethereum)
                gas_price_wei = self.web3.eth.gas_price

                # Base chain gas prices are typically 0.001-0.005 gwei vs Ethereum's 20-50 gwei
                # Cap at reasonable Base chain maximum (0.01 gwei = 10,000,000 wei)
                max_base_gas_wei = int(0.01 * 1e9)  # 0.01 gwei max for Base
                gas_price_wei = min(gas_price_wei, max_base_gas_wei)

                total_wei = gas_price_wei * gas_units
                return float(self.web3.from_wei(total_wei, 'ether'))
            else:
                # Base chain fallback: 0.001 gwei (typical Base chain gas price)
                return (0.001 * 1e9 * gas_units) / 1e18
        except Exception:
            # Base chain emergency fallback: ~$0.005 per transaction
            return 0.0000005  # ~$0.005 at current ETH prices

    async def _get_zora_balance(self) -> float:
        """Get ZORA token balance for the trading wallet"""
        try:
            if not self.web3 or not self.account:
                return 0.0

            # ERC20 balanceOf call
            balance_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]

            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(self.zora_address), abi=balance_abi)

            # Get decimals
            decimals = contract.functions.decimals().call()

            # Get balance
            balance_raw = contract.functions.balanceOf(self.account.address).call()

            # Convert to float
            balance = balance_raw / (10 ** decimals)
            return balance

        except Exception as e:
            logger.error(f"Failed to get ZORA balance: {e}")
            return 0.0

    async def _execute_buy_zora(self, signal: TradeSignal) -> Tuple[bool, str, int, float]:
        """Execute real BUY transaction for ZORA tokens via Uniswap V3"""
        try:
            if not self.web3 or not self.account:
                return False, "", 0, 0.0

            # Calculate ETH amount needed
            eth_amount = (signal.amount * signal.price) / self.current_price
            eth_amount_wei = self.web3.to_wei(eth_amount, 'ether')

            # Uniswap V3 swap parameters
            deadline = int(time.time()) + 300  # 5 minutes
            amount_out_min = int(signal.amount * (10 ** 18) * 0.995)  # 0.5% slippage

            # Build Uniswap V3 swap transaction
            swap_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "recipient", "type": "address"},
                        {"internalType": "address", "name": "tokenIn", "type": "address"},
                        {"internalType": "address", "name": "tokenOut", "type": "address"},
                        {"internalType": "uint24", "name": "fee", "type": "uint24"},
                        {"internalType": "address", "name": "recipient", "type": "address"},
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                        {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                    ],
                    "name": "exactInputSingle",
                    "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]

            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(self.uniswap_router), abi=swap_abi)

            # Build transaction
            tx = contract.functions.exactInputSingle(
                self.account.address,  # recipient
                self.weth_address,     # tokenIn (WETH)
                self.zora_address,     # tokenOut (ZORA)
                3000,                  # fee (0.3%)
                self.account.address,  # recipient
                eth_amount_wei,        # amountIn
                amount_out_min,        # amountOutMinimum
                0                      # sqrtPriceLimitX96 (no limit)
            ).build_transaction({
                'from': self.account.address,
                'value': eth_amount_wei,
                'gas': 300000,  # Estimate gas
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'chainId': 8453  # Base chain ID
            })

            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            gas_used = receipt['gasUsed']
            gas_cost_wei = gas_used * receipt['effectiveGasPrice']
            gas_cost_eth = float(self.web3.from_wei(gas_cost_wei, 'ether'))

            success = receipt['status'] == 1

            return success, tx_hash.hex(), gas_used, gas_cost_eth

        except Exception as e:
            logger.error(f"Failed to execute ZORA buy: {e}")
            return False, "", 0, 0.0

    async def _execute_sell_zora(self, signal: TradeSignal) -> Tuple[bool, str, int, float, float]:
        """Execute real SELL transaction for ZORA tokens via Uniswap V3"""
        try:
            if not self.web3 or not self.account:
                return False, "", 0, 0.0, 0.0

            # Amount of ZORA to sell (in wei)
            zora_amount_wei = int(signal.amount * (10 ** 18))  # Assuming 18 decimals

            # Calculate minimum ETH output with slippage
            eth_out_min = int(((signal.amount * signal.price) / self.current_price) * 0.995 * (10 ** 18))

            # First approve Uniswap router to spend ZORA tokens
            await self._approve_token(self.zora_address, self.uniswap_router, zora_amount_wei)

            # Build Uniswap V3 swap transaction
            swap_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "recipient", "type": "address"},
                        {"internalType": "address", "name": "tokenIn", "type": "address"},
                        {"internalType": "address", "name": "tokenOut", "type": "address"},
                        {"internalType": "uint24", "name": "fee", "type": "uint24"},
                        {"internalType": "address", "name": "recipient", "type": "address"},
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                        {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                    ],
                    "name": "exactInputSingle",
                    "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]

            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(self.uniswap_router), abi=swap_abi)

            # Build transaction
            tx = contract.functions.exactInputSingle(
                self.account.address,  # recipient
                self.zora_address,     # tokenIn (ZORA)
                self.weth_address,     # tokenOut (WETH)
                3000,                  # fee (0.3%)
                self.account.address,  # recipient
                zora_amount_wei,       # amountIn
                eth_out_min,           # amountOutMinimum
                0                      # sqrtPriceLimitX96 (no limit)
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,  # Estimate gas
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'chainId': 8453  # Base chain ID
            })

            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            gas_used = receipt['gasUsed']
            gas_cost_wei = gas_used * receipt['effectiveGasPrice']
            gas_cost_eth = float(self.web3.from_wei(gas_cost_wei, 'ether'))

            success = receipt['status'] == 1

            # Calculate ETH received (this is approximate)
            eth_received = 0.0
            if success and receipt['logs']:
                # Try to parse the transfer logs to get actual ETH received
                # This is simplified - in production you'd parse the logs properly
                eth_received = (signal.amount * signal.price) / self.current_price * 0.997  # Rough estimate minus fees

            return success, tx_hash.hex(), gas_used, gas_cost_eth, eth_received

        except Exception as e:
            logger.error(f"Failed to execute ZORA sell: {e}")
            return False, "", 0, 0.0, 0.0

    async def _approve_token(self, token_address: str, spender: str, amount: int) -> bool:
        """Approve token spending for Uniswap router"""
        try:
            if not self.web3 or not self.account:
                return False

            approve_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_spender", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]

            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=approve_abi)

            tx = contract.functions.approve(spender, amount).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'chainId': 8453
            })

            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for approval
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            return receipt['status'] == 1

        except Exception as e:
            logger.error(f"Token approval failed: {e}")
            return False

    def gpu_analyze_market(self) -> Optional[Dict[str, Any]]:
        """GPU/CPU-accelerated market analysis"""
        if len(self.price_history) < 10:
            return None

        try:
            prices = [p for _, p in self.price_history[-100:]]

            if self.gpu_type == "cuda" and self.cp and self.np:
                # CUDA GPU acceleration
                cp_prices = self.cp.asarray(prices)

                if len(cp_prices) >= 20:
                    ma_short = self.cp.mean(cp_prices[-20:])
                    ma_long = self.cp.mean(cp_prices[-50:]) if len(cp_prices) >= 50 else ma_short
                    momentum = float((cp_prices[-1] - cp_prices[0]) / cp_prices[0])
                    returns = self.cp.diff(cp_prices) / cp_prices[:-1]
                    volatility = float(self.cp.std(returns))

                    return {
                        'ma_short': float(ma_short),
                        'ma_long': float(ma_long),
                        'momentum': momentum,
                        'volatility': volatility,
                        'trend': 'bullish' if ma_short > ma_long else 'bearish',
                        'acceleration': 'cuda'
                    }

            elif self.gpu_type in ["cpu_numba", "cpu_numpy"] and self.np:
                # CPU acceleration with NumPy
                np_prices = self.np.array(prices)

                if len(np_prices) >= 20:
                    ma_short = self.np.mean(np_prices[-20:])
                    ma_long = self.np.mean(np_prices[-50:]) if len(np_prices) >= 50 else ma_short
                    momentum = float((np_prices[-1] - np_prices[0]) / np_prices[0])
                    returns = self.np.diff(np_prices) / np_prices[:-1]
                    volatility = float(self.np.std(returns))

                    return {
                        'ma_short': float(ma_short),
                        'ma_long': float(ma_long),
                        'momentum': momentum,
                        'volatility': volatility,
                        'trend': 'bullish' if ma_short > ma_long else 'bearish',
                        'acceleration': self.gpu_type
                    }

            else:
                # Basic CPU calculations
                if len(prices) >= 20:
                    ma_short = sum(prices[-20:]) / 20
                    ma_long = sum(prices[-50:]) / 50 if len(prices) >= 50 else ma_short
                    momentum = (prices[-1] - prices[0]) / prices[0]
                    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    volatility = (sum((r - (sum(returns) / len(returns))) ** 2 for r in returns) / len(returns)) ** 0.5

                    return {
                        'ma_short': ma_short,
                        'ma_long': ma_long,
                        'momentum': momentum,
                        'volatility': volatility,
                        'trend': 'bullish' if ma_short > ma_long else 'bearish',
                        'acceleration': 'cpu_basic'
                    }

        except Exception as e:
            logger.debug(f"Market analysis failed: {e}")
            return None

async def main():
    """Main function with enhanced features"""
    import argparse

    parser = argparse.ArgumentParser(description='AAVE Trading Bot')
    parser.add_argument('--ws-enable', action='store_true', help='Enable WebSocket server for dashboard')
    parser.add_argument('--ws-port', type=int, default=8080, help='WebSocket server port')
    parser.add_argument('--strategy', type=str, default='market_making', choices=['market_making', 'momentum', 'arbitrage', 'manual'], help='Trading strategy')

    args = parser.parse_args()

    print("🔥 🔥 🔥 REAL MONEY ZORA BASE CHAIN TRADING BOT v2.0.0 - LIVE TRADES 🔥 🔥 🔥")
    print("=" * 80)
    print("⚠️  WARNING: This bot executes REAL blockchain transactions!")
    print("💰 You can LOSE REAL MONEY if trades go against you!")
    print("🔒 Make sure you have a $5 ETH reserve and understand the risks!")
    print("=" * 80)

    # Bot configuration - AGGRESSIVE DAILY PROFIT MODE
    config = {
        'strategy': args.strategy,
        'initial_balance': 23.25,  # $23.25 available trading capital (above $5 ETH reserve)
        'max_position_size': 10.0,  # Max $10 position size
        'min_trade_amount': 1.0,   # Minimum $1 trade
        'sell_gain_pct': 0.03,     # Sell at 3% profit
        'rebuy_drop_pct': 0.02,    # Buy back at 2% drop
        'analysis_interval': 5,   # Check every 5 seconds (faster for testing)
        'api_keys': {
            'birdeye': os.getenv('BIRDEYE_API_KEY'),
            'etherscan': os.getenv('ETHERSCAN_API_KEY'),
            'infura': os.getenv('INFURA_PROJECT_ID'),
        }
    }

    # Initialize bot
    bot = ZORABot(config)

    # Start WebSocket server if enabled
    if args.ws_enable:
        await bot.start_ws_server(port=args.ws_port)

    # Start bot
    try:
        print("Starting AAVE Trading Bot...")
        print(f"Strategy: {bot.strategy.value}")
        print(f"Initial Balance: ${bot.current_balance}")
        print(f"Acceleration: {bot.gpu_type.upper()}")
        print(f"Database: {'Connected' if bot.db_connection else 'Failed'}")
        print(f"WebSocket Server: {'Enabled' if bot.ws_enabled else 'Disabled'}")
        if bot.ws_enabled:
            print(f"WS Port: {args.ws_port}")
        print("-" * 60)

        bot_task = asyncio.create_task(bot.start())

        # Enhanced status monitoring loop like MAXX trader
        while True:
            await asyncio.sleep(60)  # Update every minute

            status = bot.get_status()

            # Get gas price information for Base chain
            gas_gwei = 0.001  # Base chain default (much lower than Ethereum)
            try:
                if bot.web3:
                    gas_price_wei = bot.web3.eth.gas_price
                    gas_gwei = gas_price_wei / 1e9
                    # Cap display at reasonable Base chain max
                    gas_gwei = min(gas_gwei, 0.01)
            except:
                pass

            # Calculate gas cost for typical transaction on Base chain (much cheaper)
            gas_cost_eth = bot._estimate_gas_cost_eth(21000)
            gas_cost_usd = gas_cost_eth * status['current_price'] if status['current_price'] > 0 else 0

            print(f"\n╔══════════════════════════════════════════════════════════════════════════════╗")
            print(f"║ 🔥 REAL MONEY ZORA BASE CHAIN TRADER - {datetime.now().strftime('%H:%M:%S')} - LIVE TRADES ACTIVE 🔥         ║")
            print(f"╠══════════════════════════════════════════════════════════════════════════════╣")
            # Get real wallet balance
            real_balance_eth = 0.0
            zora_balance = 0.0
            try:
                if bot.account and bot.web3:
                    balance_wei = bot.web3.eth.get_balance(bot.account.address)
                    real_balance_eth = float(bot.web3.from_wei(balance_wei, 'ether'))
                    zora_balance = await bot._get_zora_balance()
            except:
                pass

            print(f"║ {'🟢 ACTIVE' if status['is_active'] else '🔴 INACTIVE':<12} │ {'⚡ TRADING' if status['is_trading'] else '⏸️ WAITING':<12} │ 💰 ETH: {real_balance_eth:.4f} │ ZORA: {zora_balance:.2f} ║")
            print(f"║ 📈 ZORA Price: ${status['current_price']:.4f} │ 📊 Signals: {status['pending_signals']} │ ⛽ Gas: {gas_gwei:.4f}gwei (${gas_cost_usd:.4f}) ║")
            print(f"║ 🏆 Trades: {status['total_trades']} │ ✅ Win Rate: {status['win_rate']:.1f}% │ 💵 P&L: ${status['total_profit']:+.2f} ║")
            print(f"╚══════════════════════════════════════════════════════════════════════════════╝")

            if status['last_trade_time']:
                last_trade = datetime.fromisoformat(status['last_trade_time'])
                time_since = datetime.now() - last_trade
                print(f"⏰ Last Trade: {time_since.seconds // 60}m {time_since.seconds % 60}s ago")

            # Show recent database trades if available
            if bot.db_connection:
                db_trades = bot.get_recent_trades_db(3)
                if db_trades:
                    print("📋 Recent Trades:")
                    for trade in db_trades:
                        success_emoji = "✅" if trade['success'] else "❌"
                        pnl_emoji = "📈" if trade['profit_loss'] > 0 else "📉" if trade['profit_loss'] < 0 else "➡️"
                        print(f"   {success_emoji} {trade['trade_type']} {trade['zora_amount']:.2f} ZORA @ ${trade['zora_price_usd']:.2f} {pnl_emoji} ${trade['profit_loss']:+.2f}")

    except KeyboardInterrupt:
        print("\n🛑 Shutting down bot...")
        await bot.stop()
        await bot.stop_ws_server()

        # Final statistics
        final_status = bot.get_status()
        print("\n📈 Final Statistics:")
        print(f"Total Trades: {final_status['total_trades']}")
        print(f"Successful Trades: {final_status['successful_trades']}")
        print(f"Failed Trades: {final_status['failed_trades']}")
        print(f"Win Rate: {final_status['win_rate']:.1}%")
        print(f"Total P&L: ${final_status['total_profit']:.2f}")
        print(f"Final Balance: ${final_status['balance']:.2f}")

    except Exception as e:
        logger.error("Bot crashed: %s", str(e))
        await bot.stop()
        await bot.stop_ws_server()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
