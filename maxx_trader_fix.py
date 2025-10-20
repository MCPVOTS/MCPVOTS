import asyncio
import time
import json
import logging
import argparse
import signal
import sys
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from decimal import Decimal
from contextlib import suppress

# Web3 imports
from web3 import Web3
import requests

# Load environment from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# WebSocket import
try:
    import websockets
except ImportError:
    websockets = None

# Load environment from .env if present
try:
    import standalone_config as config
except Exception as _e:
    config = None

try:
    from kyber_client import KyberClient
except Exception:
    KyberClient = None

try:
    from basescan_client import EtherscanV2Client
except Exception:
    EtherscanV2Client = None

# Optional ChromaDB integration flag
try:
    import standalone_config as _sc
    CHROMADB_AVAILABLE = bool(getattr(_sc, 'CHROMADB_ENABLED', False))
    if CHROMADB_AVAILABLE:
        import tools.ethermax_chromadb as chromadb_integration
except Exception:
    CHROMADB_AVAILABLE = False


class RateLimiter:
    def __init__(self, max_calls: int = 10):
        self.max_calls = max_calls


class RPCManager:
    """Minimal RPC manager for Base chain with simple rotation stub."""
    def __init__(self):
        default_url = None
        try:
            default_url = os.getenv('BASE_RPC_URL') or (getattr(config, 'PROVIDER_URL', None) if config else None)
        except Exception:
            default_url = None
        self.rpc_endpoints = [u for u in [default_url] if u]
        if not self.rpc_endpoints:
            self.rpc_endpoints = ["https://mainnet.base.org"]
        self.current_rpc_index = 0
        self._w3: Optional[Web3] = None
        self.rate_limiter = RateLimiter(10)

    async def get_w3_instance(self) -> Web3:
        url = self.rpc_endpoints[self.current_rpc_index]
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 30}))
        return self._w3


class DashboardWebSocketServer:
    """Lightweight WS broadcaster (no HTTP)."""
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self._server = None
        self._clients: set = set()

    async def start(self):
        if websockets is None:
            return None

        async def _handler(ws):
            self._clients.add(ws)
            try:
                async for _ in ws:
                    pass
            except Exception:
                pass
            finally:
                try:
                    self._clients.remove(ws)
                except KeyError:
                    pass

        self._server = await websockets.serve(_handler, self.host, self.port)
        return self._server

    async def stop(self):
        if self._server:
            self._server.close()
            with suppress(Exception):
                await self._server.wait_closed()
            self._server = None
        for ws in list(self._clients):
            with suppress(Exception):
                await ws.close()
        self._clients.clear()

    async def broadcast(self, payload: Dict[str, Any]):
        if not self._clients:
            return
        try:
            msg = json.dumps(payload, default=str)
        except Exception:
            return
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            with suppress(Exception):
                await ws.close()
            try:
                self._clients.remove(ws)
            except KeyError:
                pass


class MasterTradingSystem:
    """Unified MAXX trading system with all functionality consolidated"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize GPU acceleration
        self.gpu_available = False
        try:
            import cupy as cp
            import numpy as np
            self.cp = cp
            self.np = np
            # Test GPU availability with a simple operation
            test_array = cp.array([1.0, 2.0, 3.0])
            cp.sum(test_array)  # Simple test
            cp.cuda.Device(0).use()  # Use first GPU
            self.gpu_available = True
            self.logger.info("GPU acceleration enabled with CuPy")
        except Exception as e:
            self.cp = None
            self.np = None
            self.gpu_available = False
            self.logger.info(f"GPU acceleration not available: {e}")
            self.logger.info("System will run with CPU-only operations (GPU can be enabled by installing CUDA runtime)")

        self.rpc_manager = RPCManager()
        self.w3 = None
        self.account = None
        self.router = None
        self.maxx_contract = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # ChromaDB integration
        self.chromadb = None
        self.chromadb_enabled = CHROMADB_AVAILABLE

        # WebSocket integration for dashboard (optional; disabled by default)
        self.ws_enabled = False
        self.ws_server = None
        self.ws_broadcast_task = None

        # Trading state
        self.trading_stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_gas_used': 0,
            'total_eth_spent': Decimal('0'),
            'start_time': None
        }

        # Load persisted trading stats
        persisted_stats = self._load_trading_stats()
        if persisted_stats:
            self.trading_stats.update(persisted_stats)
            self.logger.info(f"Loaded trading stats: {self.trading_stats['total_trades']} total trades")

        # ERC20 ABI (for MAXX)
        self.erc20_abi = [
            {
                "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "spender", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        # Transaction config defaults
        self.use_eip1559 = bool(getattr(config, 'USE_EIP1559', True))
        self.max_fee_gwei = float(getattr(config, 'MAX_FEE_GWEI', 0.001))
        self.priority_fee_gwei = float(getattr(config, 'PRIORITY_FEE_GWEI', 0.0))
        self.wait_for_receipt = bool(getattr(config, 'TX_WAIT_FOR_RECEIPT', True))
        self.receipt_timeout_secs = int(getattr(config, 'TX_RECEIPT_TIMEOUT', 120))
        self.base_fee_headroom_pct = float(getattr(config, 'BASE_FEE_HEADROOM_PCT', 0.0))
        self.forced_gas_limit = None

        # Balance cache
        self._balance_cache_time = 0.0
        self._cached_eth = Decimal('0')
        self._cached_maxx = Decimal('0')

        # Database and logging
        self.db_connection = None
        self.last_trade_info = None

        # GPU test method
        self._gpu_test_completed = False

    # ==============================
    # GPU acceleration methods
    # ==============================
    def gpu_test_acceleration(self) -> bool:
        """Test GPU acceleration with a simple computation"""
        if not self.gpu_available or not self.cp or not self.np:
            self.logger.warning("GPU acceleration not available for testing")
            return False

        try:
            # Create test data
            size = 10000
            np_data = self.np.random.random(size).astype(self.np.float32)
            cp_data = self.cp.asarray(np_data)

            # Perform computation on GPU
            result = self.cp.sum(cp_data ** 2)

            # Transfer back to CPU
            cpu_result = self.cp.asnumpy(result)

            self.logger.info(f"GPU test successful: computed sum of squares = {cpu_result:.2f}")
            self._gpu_test_completed = True
            return True

        except Exception as e:
            self.logger.error(f"GPU test failed: {e}")
            # Mark GPU as unavailable if runtime fails
            self.gpu_available = False
            self.cp = None
            self.np = None
            return False

    # ==============================
    # Initialization
    # ==============================
    async def initialize(self):
        """Initialize Web3, account, and contracts"""
        try:
            self.w3 = await self.rpc_manager.get_w3_instance()

            # Load private key
            # Prefer environment variable; fallback to standalone_config.PRIVATE_KEY or standalone_config.ETHEREUM_PRIVATE_KEY
            private_key = (
                os.getenv('ETHEREUM_PRIVATE_KEY')
                or getattr(config, 'PRIVATE_KEY', None)
                or getattr(config, 'ETHEREUM_PRIVATE_KEY', None)
            )
            if not private_key:
                raise ValueError("ETHEREUM_PRIVATE_KEY not found in environment or config")

            self.account = self.w3.eth.account.from_key(private_key)
            self.logger.info(f"Initialized account: {self.account.address}")

            # Load MAXX contract
            maxx_address = getattr(config, 'MAXX_TOKEN_ADDRESS', '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')
            if maxx_address:
                self.maxx_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(maxx_address),
                    abi=self.erc20_abi
                )
                self.logger.info(f"Loaded MAXX contract: {maxx_address}")

            self.is_running = True
            self.trading_stats['start_time'] = datetime.now(timezone.utc).isoformat()

            # Initialize database
            self._init_database()

            return True
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False

    # ==============================
    # Database and logging
    # ==============================
    def _init_database(self):
        """Initialize SQLite database for trade logging"""
        try:
            db_path = os.path.join(os.getcwd(), 'data', 'trades.db')
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()

            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    tx_hash TEXT,
                    maxx_amount REAL,
                    eth_amount REAL,
                    maxx_price_usd REAL,
                    eth_price_usd REAL,
                    gas_used REAL,
                    gas_cost_eth REAL,
                    gas_cost_usd REAL,
                    slippage_bps INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    strategy TEXT,
                    anchor_price_usd REAL,
                    pnl_eth REAL,
                    pnl_usd REAL
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
            self.logger.info("Database initialized successfully")

            # Load last trade info
            self._load_last_trade_info()

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _load_last_trade_info(self):
        """Load information about the last trade from database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, trade_type, tx_hash, maxx_amount, eth_amount,
                       maxx_price_usd, eth_price_usd, success, pnl_usd
                FROM trades
                ORDER BY timestamp DESC
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if row:
                self.last_trade_info = {
                    'timestamp': row[0],
                    'trade_type': row[1],
                    'tx_hash': row[2],
                    'maxx_amount': row[3],
                    'eth_amount': row[4],
                    'maxx_price_usd': row[5],
                    'eth_price_usd': row[6],
                    'success': bool(row[7]),
                    'pnl_usd': row[8]
                }
                self.logger.info(f"Loaded last trade info: {self.last_trade_info['trade_type']} at {self.last_trade_info['timestamp']}")
        except Exception as e:
            self.logger.error(f"Failed to load last trade info: {e}")

    def _log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade to database and file"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Insert trade record
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, trade_type, tx_hash, maxx_amount, eth_amount,
                    maxx_price_usd, eth_price_usd, gas_used, gas_cost_eth,
                    gas_cost_usd, slippage_bps, success, error_message,
                    strategy, anchor_price_usd, pnl_eth, pnl_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('timestamp'),
                trade_data.get('trade_type'),
                trade_data.get('tx_hash'),
                trade_data.get('maxx_amount'),
                trade_data.get('eth_amount'),
                trade_data.get('maxx_price_usd'),
                trade_data.get('eth_price_usd'),
                trade_data.get('gas_used'),
                trade_data.get('gas_cost_eth'),
                trade_data.get('gas_cost_usd'),
                trade_data.get('slippage_bps'),
                trade_data.get('success', False),
                trade_data.get('error_message'),
                trade_data.get('strategy'),
                trade_data.get('anchor_price_usd'),
                trade_data.get('pnl_eth'),
                trade_data.get('pnl_usd')
            ))

            trade_id = cursor.lastrowid
            self.db_connection.commit()

            # Update last trade info
            self.last_trade_info = {
                'timestamp': trade_data.get('timestamp'),
                'trade_type': trade_data.get('trade_type'),
                'tx_hash': trade_data.get('tx_hash'),
                'maxx_amount': trade_data.get('maxx_amount'),
                'eth_amount': trade_data.get('eth_amount'),
                'maxx_price_usd': trade_data.get('maxx_price_usd'),
                'eth_price_usd': trade_data.get('eth_price_usd'),
                'success': trade_data.get('success', False),
                'pnl_usd': trade_data.get('pnl_usd')
            }

            # Log to file as well
            self._log_trade_to_file(trade_data)

            self.logger.info(f"Trade logged to database: {trade_data.get('trade_type')} {trade_data.get('tx_hash')}")

        except Exception as e:
            self.logger.error(f"Failed to log trade to database: {e}")

    def _log_trade_to_file(self, trade_data: Dict[str, Any]):
        """Log trade to a text file for easy reading"""
        try:
            log_file = os.path.join(os.getcwd(), 'trade_log.txt')
            timestamp = trade_data.get('timestamp', datetime.now(timezone.utc).isoformat())

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TRADE LOG - {timestamp}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Type: {trade_data.get('trade_type', 'UNKNOWN')}\n")
                f.write(f"TX Hash: {trade_data.get('tx_hash', 'N/A')}\n")
                f.write(f"MAXX Amount: {trade_data.get('maxx_amount', 0):,.2f}\n")
                f.write(f"ETH Amount: {trade_data.get('eth_amount', 0):.6f}\n")
                f.write(f"MAXX Price: ${trade_data.get('maxx_price_usd', 0):.6f}\n")
                f.write(f"ETH Price: ${trade_data.get('eth_price_usd', 0):.2f}\n")
                f.write(f"Gas Cost: {trade_data.get('gas_cost_eth', 0):.6f} ETH (${trade_data.get('gas_cost_usd', 0):.4f})\n")
                f.write(f"Slippage: {trade_data.get('slippage_bps', 0)} bps\n")
                f.write(f"Success: {trade_data.get('success', False)}\n")
                f.write(f"Strategy: {trade_data.get('strategy', 'N/A')}\n")
                f.write(f"Anchor Price: ${trade_data.get('anchor_price_usd', 0):.6f}\n")
                f.write(f"P&L ETH: {trade_data.get('pnl_eth', 0):.6f}\n")
                f.write(f"P&L USD: ${trade_data.get('pnl_usd', 0):.4f}\n")
                if trade_data.get('error_message'):
                    f.write(f"Error: {trade_data.get('error_message')}\n")
                f.write(f"{'='*80}\n")

        except Exception as e:
            self.logger.error(f"Failed to log trade to file: {e}")

    def get_last_trade_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the last trade"""
        return self.last_trade_info

    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades from database"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, trade_type, tx_hash, maxx_amount, eth_amount,
                       maxx_price_usd, eth_price_usd, success, pnl_usd, strategy
                FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'timestamp': row[0],
                    'trade_type': row[1],
                    'tx_hash': row[2],
                    'maxx_amount': row[3],
                    'eth_amount': row[4],
                    'maxx_price_usd': row[5],
                    'eth_price_usd': row[6],
                    'success': bool(row[7]),
                    'pnl_usd': row[8],
                    'strategy': row[9]
                })

            return trades

        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []

    def get_recent_maxx_transfers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent MAXX token transfers for the account using Etherscan V2"""
        if not self.account:
            return []

        maxx_address = getattr(config, 'MAXX_TOKEN_ADDRESS', None)
        if not maxx_address:
            return []

        transfers = self._get_etherscan_token_transfers(
            address=self.account.address,
            contract_address=maxx_address,
            limit=limit
        )

        # Format for easier reading
        formatted = []
        for tx in transfers:
            formatted.append({
                'hash': tx.get('hash'),
                'timestamp': int(tx.get('timeStamp', 0)),
                'from': tx.get('from'),
                'to': tx.get('to'),
                'value': Decimal(tx.get('value', '0')) / Decimal(10**int(tx.get('tokenDecimal', 18))),
                'gas_used': int(tx.get('gasUsed', 0)),
                'gas_price': int(tx.get('gasPrice', 0)),
                'block': int(tx.get('blockNumber', 0))
            })

        return formatted

    def get_global_maxx_transfers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent global MAXX token transfers (all wallets) using Etherscan V2"""
        maxx_address = getattr(config, 'MAXX_TOKEN_ADDRESS', None)
        if not maxx_address:
            return []

        transfers = self._get_etherscan_token_transfers(
            address=None,  # Get all transfers for this contract
            contract_address=maxx_address,
            limit=limit
        )

        # Format for easier reading
        formatted = []
        for tx in transfers:
            formatted.append({
                'hash': tx.get('hash'),
                'timestamp': int(tx.get('timeStamp', 0)),
                'from': tx.get('from'),
                'to': tx.get('to'),
                'value': Decimal(tx.get('value', '0')) / Decimal(10**int(tx.get('tokenDecimal', 18))),
                'gas_used': int(tx.get('gasUsed', 0)),
                'gas_price': int(tx.get('gasPrice', 0)),
                'block': int(tx.get('blockNumber', 0))
            })

        return formatted

    def get_ethermax_intelligence_alerts(self) -> List[Dict[str, Any]]:
        """Get recent Ethermax intelligence alerts from the system"""
        try:
            # Try to read from ethermax alerts file if it exists
            alerts_file = os.path.join(os.getcwd(), 'ethermax_alerts.json')
            if os.path.exists(alerts_file):
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
                    if isinstance(alerts, list):
                        # Return last 5 alerts
                        return alerts[-5:] if len(alerts) > 5 else alerts
        except Exception as e:
            self.logger.debug(f"Could not read Ethermax alerts: {e}")

        return []

    def log_recent_activity(self):
        """Log recent MAXX transfers and Ethermax alerts for monitoring"""
        # Log wallet-specific transfers
        if self.account and self.account.address:
            transfers = self.get_recent_maxx_transfers(limit=3)
            if transfers:
                self.logger.info("Recent MAXX Activity (Wallet):")
                for tx in transfers:
                    direction = "→" if tx['to'].lower() == self.account.address.lower() else "←"
                    self.logger.info(f"  {direction} {tx['value']:.2f} MAXX | {tx['hash'][:10]}... | Block {tx['block']}")
            else:
                self.logger.debug("No recent wallet MAXX transfers found")

            # Log global MAXX transfers
            global_transfers = self.get_global_maxx_transfers(limit=5)
            if global_transfers:
                self.logger.info("Recent MAXX Activity (Global):")
                for tx in global_transfers:
                    # Skip our own transactions to avoid duplication
                    if (tx['from'].lower() == self.account.address.lower() or
                        tx['to'].lower() == self.account.address.lower()):
                        continue
                    direction = "BUY" if tx['to'].lower() == getattr(config, 'MAXX_TOKEN_ADDRESS', '').lower() else "SELL"
                    self.logger.info(f"  {direction} {tx['value']:.2f} MAXX | {tx['from'][:6]}... → {tx['to'][:6]}... | {tx['hash'][:8]}...")
        else:
            self.logger.debug("Account not initialized - skipping transfer logs")
        ethermax_alerts = self.get_ethermax_intelligence_alerts()
        if ethermax_alerts:
            self.logger.info("Ethermax Intelligence Alerts:")
            for alert in ethermax_alerts:
                alert_type = alert.get('type', 'UNKNOWN')
                timestamp = alert.get('timestamp', 'N/A')
                data = alert.get('data', {})
                if alert_type == 'WHALE_BUY':
                    self.logger.info(f"  🐋 WHALE BUY: ${data.get('amount', 0):.2f} | {data.get('from', '')[:8]}...")
                elif alert_type == 'PRICE_PUMP':
                    self.logger.info(f"  📈 PRICE PUMP: {data.get('change', 0):+.2f}% to ${data.get('price', 0):.6f}")
                elif alert_type == 'PRICE_DUMP':
                    self.logger.info(f"  📉 PRICE DUMP: {data.get('change', 0):+.2f}% to ${data.get('price', 0):.6f}")
                else:
                    self.logger.info(f"  ⚠️ {alert_type}: {str(data)[:50]}...")
        else:
            self.logger.debug("No recent Ethermax alerts")

    # ==============================
    # Price fetching with Etherscan backup
    # ==============================
    def _get_prices(self) -> Optional[Dict[str, Any]]:
        """Fetch MAXX and ETH prices from DexScreener with Birdeye fallback"""
        try:
            # Primary: DexScreener
            maxx_pair_address = getattr(config, 'DEXSCREENER_PAIR_ADDRESS', None)
            if not maxx_pair_address:
                self.logger.warning("DEXSCREENER_PAIR_ADDRESS not configured")
                return None

            url = f"https://api.dexscreener.com/latest/dex/pairs/base/{maxx_pair_address}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                self.logger.warning(f"DexScreener API returned {resp.status_code}")
                return None

            data = resp.json()
            if not data.get('pair'):
                self.logger.warning("No pair data from DexScreener")
                return None

            pair = data['pair']
            maxx_usd = Decimal(str(pair.get('priceUsd', '0')))
            maxx_native = Decimal(str(pair.get('priceNative', '0')))

            # Calculate ETH price from MAXX prices
            eth_usd = Decimal('3300')  # Default fallback
            if maxx_native > 0 and maxx_usd > 0:
                eth_usd = maxx_usd / maxx_native

            result = {
                'maxx_usd': float(maxx_usd),
                'maxx_eth': float(maxx_native),
                'eth_usd': float(eth_usd),
                'source': 'dexscreener'
            }

            # Secondary: Cross-verify with Etherscan gas data if available
            gas_data = self._get_etherscan_gas_oracle()
            if gas_data:
                result['etherscan_gas'] = gas_data
                self.logger.debug(f"Etherscan gas data: {gas_data}")

            return result

        except requests.exceptions.Timeout:
            self.logger.warning("DexScreener API timeout, trying Birdeye fallback")
        except Exception as e:
            self.logger.error(f"DexScreener price fetch error: {e}")

        # Fallback: Birdeye API
        try:
            self.logger.info("Attempting Birdeye price fallback")
            maxx_contract = getattr(config, 'MAXX_TOKEN_ADDRESS', None)
            if not maxx_contract:
                self.logger.warning("MAXX_TOKEN_ADDRESS not configured for Birdeye fallback")
                return None

            birdeye_api_key = os.getenv('BIRDEYE_API_KEY')
            if not birdeye_api_key:
                self.logger.warning("BIRDEYE_API_KEY not configured")
                return None

            url = "https://public-api.birdeye.so/defi/price"
            params = {'address': maxx_contract}
            headers = {'X-API-KEY': birdeye_api_key}

            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                self.logger.warning(f"Birdeye API returned {resp.status_code}")
                return None

            data = resp.json()
            if not data.get('success') or not data.get('data'):
                self.logger.warning("No price data from Birdeye")
                return None

            maxx_usd = Decimal(str(data['data']['price']))

            # For ETH price, try to get it from another Birdeye call or use default
            eth_usd = Decimal('3300')  # Default ETH price

            result = {
                'maxx_usd': float(maxx_usd),
                'maxx_eth': 0.0,  # Birdeye doesn't provide native price directly
                'eth_usd': float(eth_usd),
                'source': 'birdeye'
            }

            self.logger.info(f"Successfully got price from Birdeye: ${maxx_usd:.6f}")
            return result

        except Exception as e:
            self.logger.error(f"Birdeye fallback failed: {e}")
            return None

    # ==============================
    # Balance management
    # ==============================
    async def get_balances(self) -> Tuple[Decimal, Decimal]:
        """Get current ETH and MAXX balances with Etherscan cross-verification"""
        try:
            if not self.w3 or not self.account:
                return Decimal('0'), Decimal('0')

            # Get ETH balance
            eth_wei = self.w3.eth.get_balance(self.account.address)
            eth_balance = Decimal(eth_wei) / Decimal(10**18)

            # Get MAXX balance
            maxx_balance = Decimal('0')
            if self.maxx_contract:
                try:
                    decimals = self.maxx_contract.functions.decimals().call()
                    maxx_wei = self.maxx_contract.functions.balanceOf(self.account.address).call()
                    maxx_balance = Decimal(maxx_wei) / Decimal(10**decimals)
                except Exception as e:
                    self.logger.debug(f"MAXX balance fetch error: {e}")

            # Cross-verify ETH balance with Etherscan if available
            etherscan_eth = self._get_etherscan_balance_verification(self.account.address)
            if etherscan_eth is not None:
                eth_diff = abs(eth_balance - etherscan_eth)
                if eth_diff > Decimal('0.001'):  # More than 0.001 ETH difference
                    self.logger.warning(f"ETH balance mismatch! RPC: {eth_balance:.6f}, Etherscan: {etherscan_eth:.6f} (diff: {eth_diff:.6f})")
                else:
                    self.logger.debug(f"ETH balance verified: {eth_balance:.6f} ETH")

            return eth_balance, maxx_balance
        except Exception as e:
            self.logger.error(f"Balance fetch error: {e}")
            return Decimal('0'), Decimal('0')

    async def get_balances_cached(self, min_interval_seconds: int = 5) -> Tuple[Decimal, Decimal]:
        """Get balances with caching to reduce RPC calls"""
        now = time.time()
        if (now - self._balance_cache_time) >= min_interval_seconds:
            self._cached_eth, self._cached_maxx = await self.get_balances()
            self._balance_cache_time = now
        return self._cached_eth, self._cached_maxx

    # ==============================
    # Gas estimation
    # ==============================
    def _get_gas_params(self, w3: Web3) -> Dict[str, int]:
        """Get gas parameters for transaction"""
        try:
            if self.use_eip1559:
                latest_block = w3.eth.get_block('latest')
                base_fee = int(latest_block.get('baseFeePerGas', 0))

                # Apply headroom to base fee
                base_with_headroom = int(base_fee * (1 + self.base_fee_headroom_pct))

                # Set max fee
                max_fee = int(self.max_fee_gwei * 1e9)
                if max_fee == 0 or max_fee < base_with_headroom:
                    max_fee = base_with_headroom + int(self.priority_fee_gwei * 1e9)

                priority_fee = int(self.priority_fee_gwei * 1e9)

                return {
                    'maxFeePerGas': max_fee,
                    'maxPriorityFeePerGas': priority_fee
                }
            else:
                gas_price = w3.eth.gas_price
                return {'gasPrice': gas_price}
        except Exception as e:
            self.logger.error(f"Gas params error: {e}")
            return {'gasPrice': int(0.001 * 1e9)}

    def _estimate_gas_cost_eth(self, w3: Web3, gas_units: int) -> Decimal:
        """Estimate gas cost in ETH"""
        try:
            params = self._get_gas_params(w3)
            fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
            total_wei = fee_wei * gas_units
            return Decimal(total_wei) / Decimal(10**18)
        except Exception:
            return Decimal('0.001')

    # ==============================
    # Trading methods
    # ==============================
    async def buy_maxx(self,
                       eth_amount: Decimal,
                       gas_limit: Optional[int] = None,
                       min_maxx_out_wei: int = 0,
                       slippage_bps: int = 75) -> Optional[str]:
        """Buy MAXX with ETH via Kyber"""
        try:
            if not KyberClient:
                self.logger.error("KyberClient not available")
                return None

            if not self.w3 or not self.account:
                self.logger.error("Web3 or account not initialized")
                return None

            kyber = KyberClient(self.w3, self.account, self)
            eth_wei = int(eth_amount * Decimal(10**18))

            self.logger.info(f"Buying MAXX with {eth_amount} ETH")
            tx_hash = kyber.buy_eth_to_maxx(
                eth_wei,
                slippage_bps=slippage_bps
            )

            # Get current prices for logging
            prices = self._get_prices() or {}
            maxx_usd = float(prices.get('maxx_usd') or 0)
            eth_usd = float(prices.get('eth_usd') or 3300)

            # Estimate gas cost
            w3 = await self.rpc_manager.get_w3_instance()
            gas_units = gas_limit or getattr(config, 'GAS_LIMIT', 300000)
            gas_cost_eth = self._estimate_gas_cost_eth(w3, gas_units)
            gas_cost_usd = float(gas_cost_eth * Decimal(str(eth_usd)))

            if tx_hash:
                self.trading_stats['total_trades'] += 1
                self.trading_stats['successful_trades'] += 1
                self._save_trading_stats()

                # Log successful trade
                trade_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'trade_type': 'BUY',
                    'tx_hash': tx_hash,
                    'maxx_amount': None,  # Will be calculated after confirmation
                    'eth_amount': float(eth_amount),
                    'maxx_price_usd': maxx_usd,
                    'eth_price_usd': eth_usd,
                    'gas_used': None,  # Will be updated with actual gas used
                    'gas_cost_eth': float(gas_cost_eth),
                    'gas_cost_usd': gas_cost_usd,
                    'slippage_bps': slippage_bps,
                    'success': True,
                    'strategy': 'reactive',
                    'anchor_price_usd': None,  # Will be set by caller
                    'pnl_eth': 0.0,
                    'pnl_usd': 0.0
                }
                self._log_trade(trade_data)

            return tx_hash
        except Exception as e:
            self.logger.error(f"Buy MAXX error: {e}")
            self.trading_stats['total_trades'] += 1
            self.trading_stats['failed_trades'] += 1
            self._save_trading_stats()

            # Log failed trade
            prices = self._get_prices() or {}
            maxx_usd = float(prices.get('maxx_usd') or 0)
            eth_usd = float(prices.get('eth_usd') or 3300)

            trade_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'trade_type': 'BUY',
                'tx_hash': None,
                'maxx_amount': 0.0,
                'eth_amount': float(eth_amount),
                'maxx_price_usd': maxx_usd,
                'eth_price_usd': eth_usd,
                'gas_used': 0,
                'gas_cost_eth': 0.0,
                'gas_cost_usd': 0.0,
                'slippage_bps': slippage_bps,
                'success': False,
                'error_message': str(e),
                'strategy': 'reactive',
                'pnl_eth': 0.0,
                'pnl_usd': 0.0
            }
            self._log_trade(trade_data)

            return None

    async def sell_maxx(self,
                        maxx_amount: Decimal,
                        gas_limit: Optional[int] = None,
                        min_eth_out_wei: int = 0,
                        slippage_bps: int = 75) -> Optional[str]:
        """Sell MAXX for ETH via Kyber"""
        try:
            if not KyberClient:
                self.logger.error("KyberClient not available")
                return None

            if not self.w3 or not self.account:
                self.logger.error("Web3 or account not initialized")
                return None

            kyber = KyberClient(self.w3, self.account, self)

            # Get decimals
            try:
                if self.maxx_contract:
                    decimals = self.maxx_contract.functions.decimals().call()
                else:
                    decimals = 18
            except Exception:
                decimals = 18

            maxx_wei = int(maxx_amount * Decimal(10**decimals))

            self.logger.info(f"Selling {maxx_amount} MAXX")
            tx_hash = kyber.sell_maxx_to_eth(
                maxx_wei,
                slippage_bps=slippage_bps
            )

            if tx_hash:
                self.trading_stats['total_trades'] += 1
                self.trading_stats['successful_trades'] += 1
                self._save_trading_stats()

            return tx_hash
        except Exception as e:
            self.logger.error(f"Sell MAXX error: {e}")
            self.trading_stats['total_trades'] += 1
            self.trading_stats['failed_trades'] += 1
            self._save_trading_stats()
            return None

    async def _transfer_eth(self, to_address: str, amount_eth: Decimal) -> Optional[str]:
        """Transfer ETH to specified address"""
        try:
            if not self.w3 or not self.account:
                return None

            w3 = await self.rpc_manager.get_w3_instance()
            amount_wei = int(amount_eth * Decimal(10**18))

            # Build transaction
            tx = {
                'from': self.account.address,
                'to': Web3.to_checksum_address(to_address),
                'value': amount_wei,
                'nonce': w3.eth.get_transaction_count(self.account.address),
                'chainId': w3.eth.chain_id,
            }

            # Add gas parameters
            gas_params = self._get_gas_params(w3)
            tx.update(gas_params)

            # Estimate gas
            try:
                gas_estimate = w3.eth.estimate_gas(tx)  # type: ignore
                tx['gas'] = gas_estimate
            except Exception:
                tx['gas'] = 21000  # Standard ETH transfer gas limit

            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for confirmation
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            return tx_hash.hex()

        except Exception as e:
            self.logger.error(f"ETH transfer failed: {e}")
            return None

    async def run_single_test(self):
        """Run a single buy/sell test"""
        print("\n" + "="*60)
        print("SINGLE TRADING TEST")
        print("="*60)

        # Get initial balances
        initial_eth, initial_maxx = await self.get_balances()
        print(f"Initial ETH: {initial_eth:.6f}")
        print(f"Initial MAXX: {initial_maxx:,.2f}")

        # Buy test
        print(f"\nExecuting buy test with {getattr(config, 'TEST_ETH_AMOUNT', 0.001)} ETH...")
        buy_tx = await self.buy_maxx(Decimal(str(getattr(config, 'TEST_ETH_AMOUNT', 0.001))))

        if buy_tx:
            print(f"Buy successful: {buy_tx}")

            # Wait for confirmation
            await asyncio.sleep(5)

            # Check post-buy balances
            post_buy_eth, post_buy_maxx = await self.get_balances()
            print(f"Post-buy ETH: {post_buy_eth:.6f}")
            print(f"Post-buy MAXX: {post_buy_maxx:,.2f}")

            # Sell test
            maxx_received = post_buy_maxx - initial_maxx
            if maxx_received > 0:
                print(f"\nExecuting sell test with {maxx_received} MAXX...")
                sell_tx = await self.sell_maxx(maxx_received)

                if sell_tx:
                    print(f"Sell successful: {sell_tx}")

                    # Wait for confirmation
                    await asyncio.sleep(5)

                    # Check final balances
                    final_eth, final_maxx = await self.get_balances()
                    print(f"Final ETH: {final_eth:.6f}")
                    print(f"Final MAXX: {final_maxx:,.2f}")

                    # Calculate results
                    eth_cost = initial_eth - final_eth
                    print(f"\nTotal ETH cost: {eth_cost:.6f}")
                    print(f"Test completed successfully!")
                else:
                    print("Sell test failed")
            else:
                print("No MAXX received from buy")
        else:
            print("Buy test failed")

    # ==============================
    # State persistence (SINGLE COPY ONLY)
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'data/reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'data/trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast (SINGLE COPY ONLY)
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task and not self.ws_broadcast_task.done():
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    if hasattr(self.ws_broadcast_task, '__await__'):
                        await self.ws_broadcast_task  # type: ignore
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Trading strategies
    # ==============================
    async def run_reactive_strategy(
        self,
        usd_to_spend: Decimal = Decimal('7'),
        usd_reserve: Decimal = Decimal('10'),
        sell_gain_pct: Decimal = Decimal('0.12'),
        rebuy_drop_pct: Decimal = Decimal('0.10'),
        gas_limit_override: Optional[int] = None,
        slippage_bps: int = 75,
        gas_usd_cap: Optional[Decimal] = None,
        spend_all: bool = False,
    ):
        """Reactive loop that anchors from last action price and only trades in profitable directions"""
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        # Initial setup
        prices = self._get_prices() or {}
        eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
        reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

        _, maxx_balance = await self.get_balances_cached(min_interval_seconds=10)
        cur_price_usd = Decimal(str(prices.get('maxx_usd') or '0'))
        holding = bool(maxx_balance) and Decimal(maxx_balance) > 0

        anchor_price_usd: Decimal = cur_price_usd
        last_action_type: Optional[str] = None
        last_action_price_usd: Decimal = cur_price_usd
        last_buy_eth: Decimal = Decimal('0')

        # Load persisted state
        st = self._load_reactive_state()
        if st:
            try:
                st_anchor = Decimal(str(st.get('anchor_price_usd') or '0'))
                st_type = st.get('last_action_type') or None
                st_last_buy_eth = Decimal(str(st.get('last_buy_eth') or '0'))
                if st_anchor > 0:
                    anchor_price_usd = st_anchor
                    last_action_type = st_type
                    last_buy_eth = st_last_buy_eth
                    self.logger.info(
                        f"Resuming from state: anchor=${anchor_price_usd:.6f} last_action={last_action_type} last_buy={last_buy_eth:.6f} ETH"
                    )
            except Exception as e:
                self.logger.debug(f"Persisted state parse issue: {e}")

        if holding and (last_action_type is None):
            if anchor_price_usd <= 0:
                pnow = self._get_prices() or {}
                anchor_price_usd = Decimal(str(pnow.get('maxx_usd') or '0'))
            self.logger.info(
                f"Resuming HOLDING mode: anchor=${anchor_price_usd:.6f}"
            )
            last_action_type = 'buy'

        if (not holding) and (last_action_type is None):
            self.logger.info("No MAXX holdings. Monitoring for re-entry.")
            if anchor_price_usd > 0:
                last_action_type = 'sell'

        tick = 0
        while not self.shutdown_event.is_set():
            try:
                p = self._get_prices()
                if not p:
                    await asyncio.sleep(3)
                    continue

                maxx_usd = Decimal(str(p.get('maxx_usd') or '0'))
                eth_usd = Decimal(str(p.get('eth_usd') or '0'))

                if holding:
                    # Last action was BUY, only SELL if price > anchor + gain% (PROFIT TAKING)
                    if anchor_price_usd > 0 and maxx_usd >= anchor_price_usd * (Decimal('1.0') + sell_gain_pct):
                        cur_eth, maxx_now = await self.get_balances_cached(min_interval_seconds=5)
                        if Decimal(maxx_now) > 0:
                            w3 = await self.rpc_manager.get_w3_instance()
                            gas_units = int(gas_limit_override or getattr(config, 'GAS_LIMIT', 300000))
                            est_approval_eth = self._estimate_gas_cost_eth(w3, 120000)
                            est_sell_eth = self._estimate_gas_cost_eth(w3, gas_units)
                            total_gas_eth = est_approval_eth + est_sell_eth

                            if gas_usd_cap is not None:
                                if (total_gas_eth * eth_usd) > gas_usd_cap:
                                    self.logger.info(f"SELL skip: gas ${(total_gas_eth*eth_usd):.4f} > cap ${gas_usd_cap}")
                                    await asyncio.sleep(2)
                                    continue

                            if Decimal(cur_eth) < total_gas_eth:
                                self.logger.warning(f"Skip SELL: not enough ETH for gas")
                                await asyncio.sleep(2)
                                continue

                            self.logger.info(f"PROFIT SELL: +{int(sell_gain_pct*100)}% reached. Selling {Decimal(maxx_now):.2f} MAXX")
                            txh = await self.sell_maxx(Decimal(str(maxx_now)), gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"SELL_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")

                            # Calculate and transfer profit to target address
                            if txh and last_buy_eth > 0:
                                await asyncio.sleep(2)  # Wait for sell tx to be mined
                                post_sell_eth, _ = await self.get_balances_cached(min_interval_seconds=2)

                                # Estimate profit transfer gas cost
                                gas_estimate = self._estimate_gas_cost_eth(w3, 21000)  # Standard ETH transfer

                                # Calculate profit (current ETH - original investment - gas costs)
                                profit_eth = post_sell_eth - last_buy_eth - gas_estimate

                                if profit_eth > Decimal('0.001'):  # Only transfer if profit > 0.001 ETH
                                    profit_address = "0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70"
                                    transfer_tx = await self._transfer_eth(profit_address, profit_eth)
                                    if transfer_tx:
                                        self.logger.info(f"PROFIT TRANSFER: {profit_eth:.6f} ETH to {profit_address} | TX: {transfer_tx}")
                                    else:
                                        self.logger.error("Failed to transfer profit")
                                else:
                                    self.logger.info(f"No significant profit to transfer: {profit_eth:.6f} ETH")

                            holding = False
                            anchor_price_usd = maxx_usd
                            last_action_type = 'sell'
                            last_action_price_usd = maxx_usd
                            last_buy_eth = Decimal('0')  # Reset after sell

                            self._save_reactive_state({
                                'holding': holding,
                                'anchor_price_usd': float(anchor_price_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                                'last_buy_eth': float(last_buy_eth),
                            })
                else:
                    # Last action was SELL, only BUY if price < anchor - drop% (BUYING DIPS)
                    if anchor_price_usd > 0 and maxx_usd <= anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct):
                        cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                        w3 = await self.rpc_manager.get_w3_instance()
                        gas_units = int(gas_limit_override or getattr(config, 'GAS_LIMIT', 300000))
                        est_buy_eth = self._estimate_gas_cost_eth(w3, gas_units)

                        if gas_usd_cap is not None and eth_usd > 0 and (est_buy_eth * eth_usd) > gas_usd_cap:
                            self.logger.info(f"BUY skip: gas ${(est_buy_eth*eth_usd):.4f} > cap ${gas_usd_cap}")
                            await asyncio.sleep(2)
                            continue

                        avail_eth = Decimal(cur_eth) - reserve_eth - est_buy_eth
                        if avail_eth <= 0:
                            self.logger.info("BUY skip: not enough ETH beyond reserve+gas")
                        else:
                            if spend_all or usd_to_spend <= 0:
                                spend_eth = avail_eth
                            else:
                                max_budget_eth = (usd_to_spend / eth_usd) if eth_usd > 0 else avail_eth
                                spend_eth = min(avail_eth, max_budget_eth)

                            self.logger.info(f"DIP BUY: -{int(rebuy_drop_pct*100)}% from anchor. Buying with {spend_eth:.6f} ETH")
                            txh = await self.buy_maxx(spend_eth, gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"BUY_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")

                            holding = True
                            anchor_price_usd = maxx_usd
                            last_action_type = 'buy'
                            last_action_price_usd = maxx_usd
                            last_buy_eth = spend_eth

                            self._save_reactive_state({
                                'holding': holding,
                                'anchor_price_usd': float(anchor_price_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                                'last_buy_eth': float(last_buy_eth),
                            })

                tick += 1
                eth_bal, maxx_bal = await self.get_balances_cached(min_interval_seconds=20)
                avail_eth_hb = max(Decimal(eth_bal) - reserve_eth, Decimal('0'))

                # Log comprehensive trade activity every 10 ticks (every ~30 seconds)
                if tick % 10 == 0:
                    with suppress(Exception):
                        self.log_recent_activity()

                # Compute delta relative to anchor
                delta_anchor = ((maxx_usd / anchor_price_usd) - 1) * 100 if (anchor_price_usd and anchor_price_usd > 0) else Decimal('0')
                delta_since_action = ((maxx_usd / last_action_price_usd) - 1) * 100 if (last_action_price_usd and last_action_price_usd > 0) else Decimal('0')

                ent_sign = '+' if delta_anchor > 0 else ('-' if delta_anchor < 0 else '0')
                ent_abs = abs(delta_anchor)
                act_sign = '+' if delta_since_action > 0 else ('-' if delta_since_action < 0 else '0')
                act_abs = abs(delta_since_action)
                state = 'HOLD' if holding else 'FLAT'

                target_txt = ''
                if holding and anchor_price_usd > 0:
                    target_sell = anchor_price_usd * (Decimal('1.0') + sell_gain_pct)  # PROFIT SELL: sell when price rises
                    target_txt = f" | profit_sell ${target_sell:.6f}"
                elif (not holding) and anchor_price_usd > 0:
                    target_buy = anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct)  # DIP BUY: buy when price drops
                    target_txt = f" | dip_buy ${target_buy:.6f}"

                # Get gas info
                w3 = await self.rpc_manager.get_w3_instance()
                params = self._get_gas_params(w3)
                fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                fee_gwei = Decimal(fee_wei) / Decimal(1e9)

                # Calculate total portfolio value in USD
                total_portfolio_usd = (Decimal(eth_bal) * eth_usd) + (Decimal(maxx_bal) * maxx_usd)

                # Check Etherscan connectivity
                etherscan_status = "✓" if EtherscanV2Client and EtherscanV2Client().is_configured() else "✗"

                # Get recent trade activity for dashboard
                recent_wallet_trades = self.get_recent_maxx_transfers(limit=2)
                recent_global_trades = self.get_global_maxx_transfers(limit=3)
                ethermax_alerts = self.get_ethermax_intelligence_alerts()

                # Format trade activity for display
                trade_activity = []
                if recent_wallet_trades:
                    for tx in recent_wallet_trades[:1]:  # Show only most recent wallet trade
                        direction = "→" if tx['to'].lower() == self.account.address.lower() else "←"
                        trade_activity.append(f"Wallet: {direction}{tx['value']:.1f}M {tx['hash'][:6]}...")

                if recent_global_trades:
                    external_trades = [tx for tx in recent_global_trades if
                                     tx['from'].lower() != self.account.address.lower() and
                                     tx['to'].lower() != self.account.address.lower()]
                    if external_trades:
                        tx = external_trades[0]  # Show most recent external trade
                        direction = "BUY" if tx['to'].lower() == getattr(config, 'MAXX_TOKEN_ADDRESS', '').lower() else "SELL"
                        trade_activity.append(f"Global: {direction} {tx['value']:.1f}M")

                if ethermax_alerts:
                    alert = ethermax_alerts[-1]  # Show most recent alert
                    alert_type = alert.get('type', 'UNKNOWN')
                    if alert_type == 'WHALE_BUY':
                        trade_activity.append(f"🐋 ${alert['data'].get('amount', 0):.0f}")
                    elif alert_type in ['PRICE_PUMP', 'PRICE_DUMP']:
                        change = alert['data'].get('change', 0)
                        trade_activity.append(f"{'📈' if change > 0 else '📉'} {change:+.1f}%")

                activity_str = " | ".join(trade_activity) if trade_activity else "No recent activity"

                self.logger.info(f"""
┌─ 🚀 MAXX Dashboard ──────────────────────────────┐
│ 💎 MAXX: ${maxx_usd:.6f}  |  ETH: ${eth_usd:.2f}     │
│ 💰 ETH Balance: {Decimal(eth_bal):.6f} (avail {avail_eth_hb:.6f}) │
│ 📊 MAXX Balance: {Decimal(maxx_bal):,.2f}              │
│ 💵 Total USD: ${total_portfolio_usd:.2f}                 │
│ 📈 Anchor: ${anchor_price_usd:.6f}  |  Gas: {fee_gwei:.4f} gwei │
│ {'📈' if ent_sign == '+' else ('📉' if ent_sign == '-' else '➡️')} {ent_abs:.2f}% from anchor │
│ {'📈' if act_sign == '+' else ('📉' if act_sign == '-' else '➡️')} {act_abs:.2f}% since {last_action_type or 'action'} │
│ {'🟢 HOLD' if state == 'HOLD' else '🔴 FLAT'}  | {target_txt} │
│ 🔍 Etherscan: {etherscan_status}  |  📊 {activity_str} │
└─────────────────────────────────────────────────┘
""")

                # Broadcast tick for dashboards
                with suppress(Exception):
                    tick_payload = {
                        'maxx_usd': float(maxx_usd),
                        'eth_usd': float(eth_usd),
                        'eth_balance': float(Decimal(eth_bal)),
                        'eth_avail': float(avail_eth_hb),
                        'maxx_balance': float(Decimal(maxx_bal)),
                        'anchor_price_usd': float(anchor_price_usd) if anchor_price_usd else 0.0,
                        'delta_anchor': float(delta_anchor),
                        'last_action_type': last_action_type or 'action',
                        'last_action_usd': float(last_action_price_usd) if last_action_price_usd else 0.0,
                        'delta_since_last': float(delta_since_action),
                        'state': state,
                        'target_sell_usd': float(anchor_price_usd * (Decimal('1.0') + sell_gain_pct)) if (state=='HOLD' and anchor_price_usd>0) else None,  # PROFIT SELL
                        'target_buy_usd': float(anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct)) if (state=='FLAT' and anchor_price_usd>0) else None,  # DIP BUY
                        'gas_price_gwei': float(fee_gwei),
                        'gas_limit': gas_limit_override or getattr(config, 'GAS_LIMIT', 300000),
                        'recent_wallet_trades': recent_wallet_trades[:2],  # Last 2 wallet trades
                        'recent_global_trades': [tx for tx in recent_global_trades if tx['from'].lower() != self.account.address.lower() and tx['to'].lower() != self.account.address.lower()][:3],  # Last 3 external trades
                        'ethermax_alerts': ethermax_alerts[-3:] if ethermax_alerts else []  # Last 3 alerts
                    }
                    await self.ws_broadcast_tick(tick_payload)

                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"Reactive loop error: {e}")
                await asyncio.sleep(3)

    async def run_sell_all(self, gas_limit: Optional[int] = None) -> Optional[str]:
        """Sell all MAXX holdings for ETH via Kyber aggregator"""
        try:
            _, maxx_balance = await self.get_balances()
            if maxx_balance <= 0:
                print("No MAXX tokens to sell")
                return None
            self.logger.info(f"Selling ALL MAXX: {maxx_balance}")
            txh = await self.sell_maxx(maxx_balance, gas_limit=gas_limit, min_eth_out_wei=0)
            if txh:
                print(f"SUCCESS! Sell transaction: https://basescan.org/tx/{txh}")
            else:
                print("FAILED! Sell transaction failed")
            return txh
        except Exception as e:
            self.logger.error(f"run_sell_all error: {e}")
            return None

    async def run_burst_cycle(self,
                              duration_minutes: int = 10,
                              interval_minutes: int = 1,
                              usd_reserve: Decimal = Decimal('10'),
                              lower_gas_limit: Optional[int] = None):
        """Alternate SELL-ALL and BUY-ALL every interval for duration.

        - Keeps usd_reserve worth of ETH aside when buying.
        - Uses a slightly lower gas limit if provided.
        - Uses Kyber aggregator for routing to Uniswap V4 pool.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        start = time.time()
        end = start + duration_minutes * 60

        # Determine reserve in ETH from USD
        prices = self._get_prices() or {}
        eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
        reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0.0004')

        toggle_sell = True  # start with SELL-ALL as requested
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                eth_balance, maxx_balance = await self.get_balances_cached(min_interval_seconds=5)

                if toggle_sell:
                    # SELL ALL MAXX if any
                    if maxx_balance > 0:
                        self.logger.info(f"BURST SELL-ALL | MAXX {maxx_balance:,.2f}")
                        tx = await self.sell_maxx(Decimal(maxx_balance), gas_limit=lower_gas_limit)
                        self.logger.info(f"BURST SELL_TX: {tx}")
                    else:
                        self.logger.info("BURST SELL-ALL | No MAXX to sell")
                else:
                    # BUY with all ETH minus reserve
                    spend_eth = Decimal(eth_balance) - reserve_eth
                    if spend_eth > Decimal('0.0'):
                        # Small safety floor
                        spend_eth = max(spend_eth, Decimal('0'))
                        self.logger.info(f"BURST BUY-ALL | Spending {spend_eth:.6f} ETH (reserve {reserve_eth:.6f})")
                        tx = await self.buy_maxx(spend_eth, gas_limit=lower_gas_limit)
                        self.logger.info(f"BURST BUY_TX: {tx}")
                    else:
                        self.logger.info("BURST BUY-ALL | Not enough ETH beyond reserve")

                # Flip action and wait interval
                toggle_sell = not toggle_sell
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                self.logger.error(f"Burst cycle error: {e}")
                await asyncio.sleep(5)

    async def run_usd_pingpong(self,
                               duration_minutes: int = 10,
                               usd_amount: Decimal = Decimal('1'),
                               gas_limit: Optional[int] = None,
                               slippage_bps: int = 75,
                               gas_usd_cap: Optional[Decimal] = None):
        """Alternate buy $usd_amount and then sell $usd_amount for duration via Kyber.

        - Uses DexScreener prices to convert USD -> ETH for buys and USD -> MAXX for sells.
        - Waits for each tx confirmation (system default) before proceeding.
        - Skips an action if insufficient balance for trade + gas.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        end = time.time() + (duration_minutes * 60)
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                prices = self._get_prices()
                if not prices:
                    self.logger.warning("Price fetch failed; retrying...")
                    await asyncio.sleep(3)
                    continue
                eth_usd = Decimal(prices['eth_usd'])
                maxx_usd = Decimal(prices['maxx_usd']) if prices.get('maxx_usd') else Decimal('0')

                # 1) BUY $usd_amount worth
                if eth_usd > 0:
                    buy_eth = usd_amount / eth_usd
                    cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                    # Estimate gas for buy
                    w3 = await self.rpc_manager.get_w3_instance()
                    gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                    params = self._get_gas_params(w3)
                    fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                    fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                    est_buy_eth = self._estimate_gas_cost_eth(w3, gas_units)
                    if gas_usd_cap is not None:
                        est_buy_usd = est_buy_eth * eth_usd
                        if est_buy_usd > gas_usd_cap:
                            self.logger.info(f"PINGPONG BUY skip: gas ${est_buy_usd:.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                            await asyncio.sleep(5)
                            continue
                    if Decimal(cur_eth) < (buy_eth + est_buy_eth):
                        self.logger.info(f"PINGPONG BUY skip: need {buy_eth+est_buy_eth:.6f} ETH incl gas; have {Decimal(cur_eth):.6f} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                    else:
                        self.logger.info(f"PINGPONG BUY | USD ${usd_amount} (~{buy_eth:.8f} ETH)")
                        txb = await self.buy_maxx(buy_eth, gas_limit=gas_limit, min_maxx_out_wei=0, slippage_bps=slippage_bps)
                        self.logger.info(f"PINGPONG BUY_TX: {txb}")
                else:
                    self.logger.warning("ETH/USD invalid; skipping buy")

                # 2) SELL $usd_amount worth (use latest price)
                prices2 = self._get_prices() or prices
                maxx_usd2 = Decimal(prices2['maxx_usd']) if prices2 and prices2.get('maxx_usd') else maxx_usd
                if maxx_usd2 > 0:
                    _, cur_maxx = await self.get_balances_cached(min_interval_seconds=3)
                    target_maxx = usd_amount / maxx_usd2
                    sell_amt = min(Decimal(cur_maxx), target_maxx)
                    if sell_amt > 0:
                        # Estimate gas for sell (approx using same gas units)
                        w3 = await self.rpc_manager.get_w3_instance()
                        params = self._get_gas_params(w3)
                        fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                        fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                        est_sell_eth = self._estimate_gas_cost_eth(w3, gas_units)
                        if gas_usd_cap is not None:
                            est_sell_usd = est_sell_eth * eth_usd
                            if est_sell_usd > gas_usd_cap:
                                self.logger.info(f"PINGPONG SELL skip: gas ${est_sell_usd:.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                                await asyncio.sleep(5)
                                continue
                        self.logger.info(f"PINGPONG SELL | USD ${usd_amount} (~{sell_amt:.6f} MAXX)")
                        txs = await self.sell_maxx(sell_amt, gas_limit=gas_limit, min_eth_out_wei=0, slippage_bps=slippage_bps)
                        self.logger.info(f"PINGPONG SELL_TX: {txs}")
                    else:
                        self.logger.info("PINGPONG SELL skip: insufficient MAXX balance")
                else:
                    self.logger.warning("MAXX/USD invalid; skipping sell")

                await asyncio.sleep(5)  # Brief pause between cycles
            except Exception as e:
                self.logger.error(f"USD pingpong error: {e}")
                await asyncio.sleep(5)

    # ==============================
    # Etherscan V2 integration for additional data
    # ==============================
    def _get_etherscan_balance_verification(self, address: str) -> Optional[Decimal]:
        """Get balance from Etherscan V2 as verification"""
        if not EtherscanV2Client:
            return None

        try:
            client = EtherscanV2Client()
            if not client.is_configured():
                return None

            balance_wei = client.get_balance(chainid=8453, address=address)
            if balance_wei:
                return Decimal(balance_wei) / Decimal(10**18)
        except Exception as e:
            self.logger.debug(f"Etherscan balance check failed: {e}")
        return None

    def _get_etherscan_token_transfers(self, address: Optional[str] = None, contract_address: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ERC20 token transfers from Etherscan V2"""
        if not EtherscanV2Client:
            return []

        try:
            client = EtherscanV2Client()
            if not client.is_configured():
                return []

            transfers = client.get_tokentx(
                chainid=8453,
                address=address,
                contractaddress=contract_address,
                offset=limit,
                sort='desc'
            )
            return transfers
        except Exception as e:
            self.logger.debug(f"Etherscan token transfers failed: {e}")
        return []

    def _get_etherscan_gas_oracle(self) -> Optional[Dict[str, Any]]:
        """Get gas price data from Etherscan V2"""
        if not EtherscanV2Client:
            return None

        try:
            client = EtherscanV2Client()
            if not client.is_configured():
                return None

            # Etherscan V2 gas oracle endpoint
            url = "https://api.etherscan.io/api"
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': client.api_key
            }

            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == '1' and data.get('result'):
                    return data['result']
        except Exception as e:
            self.logger.debug(f"Etherscan gas oracle failed: {e}")
        return None

    # ==============================
    # Cleanup
    # ==============================
    async def shutdown(self):
        """Clean shutdown"""
        self.logger.info("Shutting down...")
        self.shutdown_event.set()
        await self.stop_ws_server()
        self._save_trading_stats()
        self.is_running = False

    def print_system_status(self):
        """Print comprehensive system status with live gas prices"""
        try:
            # Get current prices
            prices = self._get_prices() or {}
            maxx_usd = float(prices.get('maxx_usd') or 0)
            eth_usd = float(prices.get('eth_usd') or 3300)

            # Get balances
            eth_balance, maxx_balance = self._cached_eth, self._cached_maxx

            # Get gas price
            w3 = self.w3 or self.rpc_manager._w3
            if w3:
                params = self._get_gas_params(w3)
                fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                fee_gwei = float(Decimal(fee_wei) / Decimal(1e9))
            else:
                fee_gwei = 0.0

            # Trading stats
            stats = self.trading_stats
            total_trades = stats.get('total_trades', 0)
            successful_trades = stats.get('successful_trades', 0)
            failed_trades = stats.get('failed_trades', 0)
            total_gas_used = stats.get('total_gas_used', 0)
            total_eth_spent = float(stats.get('total_eth_spent', 0))

            # Calculate success rate
            success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0

            # Runtime
            start_time = stats.get('start_time')
            runtime_str = "N/A"
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    runtime = datetime.now(timezone.utc) - start_dt
                    hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    runtime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                except Exception:
                    pass

            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🚀 MAXX TRADING SYSTEM                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 💎 MAXX Price: ${maxx_usd:.6f}  |  ETH Price: ${eth_usd:.2f}                   ║
║ 💰 ETH Balance: {eth_balance:.6f}  |  MAXX Balance: {maxx_balance:,.2f}         ║
║ ⛽ Gas Price: {fee_gwei:.4f} gwei                                           ║
║                                                                              ║
║ 📊 TRADING STATISTICS                                                       ║
║ Total Trades: {total_trades}  |  Successful: {successful_trades}  |  Failed: {failed_trades} ║
║ Success Rate: {success_rate:.1f}%                                             ║
║ Total Gas Used: {total_gas_used}  |  Total ETH Spent: {total_eth_spent:.6f}    ║
║ Runtime: {runtime_str}                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        except Exception as e:
            print(f"Error printing system status: {e}")


# ==============================
# Main entry point
# ==============================
async def main():
    """Main entry point for the trading system"""
    parser = argparse.ArgumentParser(description='MAXX Trading System')
    parser.add_argument('--mode', type=str, default='reactive',
                       choices=['reactive', 'test', 'sell-all'],
                       help='Trading mode to run')
    parser.add_argument('--sell-gain-pct', type=float, default=0.12,
                       help='Sell gain percentage (default: 0.12 = 12 percent)')
    parser.add_argument('--rebuy-drop-pct', type=float, default=0.10,
                       help='Rebuy drop percentage (default: 0.10 = 10 percent)')
    parser.add_argument('--spend-all', action='store_true',
                       help='Spend all available ETH on buys')
    parser.add_argument('--usd-reserve', type=float, default=10.0,
                       help='USD reserve to keep (default: 10.0)')
    parser.add_argument('--reactive-slippage-bps', type=int, default=75,
                       help='Slippage in basis points (default: 75 = 0.75 percent)')
    parser.add_argument('--reactive-gas-usd-cap', type=float, default=None,
                       help='Gas USD cap for reactive strategy')
    parser.add_argument('--ws-enable', action='store_true',
                       help='Enable WebSocket server for dashboard connectivity')
    parser.add_argument('--ws-port', type=int, default=8080,
                       help='WebSocket server port (default: 8080)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create system instance
    system = MasterTradingSystem()

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal...")
        asyncio.create_task(system.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize system
    if not await system.initialize():
        print("Failed to initialize trading system")
        return 1

    print(f"Trading system initialized successfully")
    print(f"Mode: {args.mode}")
    if system.account:
        print(f"Account: {system.account.address}")
    else:
        print("Account: Not initialized")

    # Run selected mode
    try:
        if args.mode == 'reactive':
            print(f"\nStarting REACTIVE strategy:")
            print(f"  Sell gain: {args.sell_gain_pct*100:.1f}%")
            print(f"  Rebuy drop: {args.rebuy_drop_pct*100:.1f}%")
            print(f"  USD reserve: ${args.usd_reserve:.2f}")
            print(f"  Slippage: {args.reactive_slippage_bps} bps")
            if args.ws_enable:
                print(f"  WebSocket: Enabled on port {args.ws_port}")
            if args.reactive_gas_usd_cap:
                print(f"  Gas cap: ${args.reactive_gas_usd_cap:.4f}")
            print()

            # Start WebSocket server if enabled
            if args.ws_enable:
                await system.start_ws_server(port=args.ws_port)

            await system.run_reactive_strategy(
                usd_reserve=Decimal(str(args.usd_reserve)),
                sell_gain_pct=Decimal(str(args.sell_gain_pct)),
                rebuy_drop_pct=Decimal(str(args.rebuy_drop_pct)),
                spend_all=args.spend_all,
                slippage_bps=args.reactive_slippage_bps,
                gas_usd_cap=Decimal(str(args.reactive_gas_usd_cap)) if args.reactive_gas_usd_cap else None
            )

        elif args.mode == 'test':
            print("\nRunning single test trade...")
            await system.run_single_test()

        elif args.mode == 'sell-all':
            print("\nSelling all MAXX...")
            txh = await system.run_sell_all()
            if txh:
                print(f"Success! TX: {txh}")
            else:
                print("Sell failed")

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nError in main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await system.shutdown()
        print("System shut down successfully")

    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
