#!/usr/bin/env python3
"""
AAVE MONITORING SYSTEM
Real-time monitoring and database logging for AAVE token on Base chain
Similar to MAXX monitoring but focused on AAVE trading and analysis
"""

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
            default_url = os.getenv('BASE_RPC_URL') or "https://mainnet.base.org"
        except Exception:
            default_url = "https://mainnet.base.org"
        self.rpc_endpoints = [default_url]
        self.current_rpc_index = 0
        self._w3: Optional[Web3] = None
        self.rate_limiter = RateLimiter(10)

    async def get_w3_instance(self) -> Web3:
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(self.rpc_endpoints[self.current_rpc_index], request_kwargs={'timeout': 30}))
        return self._w3


class DashboardWebSocketServer:
    """Lightweight WS broadcaster for AAVE monitoring."""
    def __init__(self, host: str = 'localhost', port: int = 8081):  # Different port from MAXX
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


class AAVEMonitoringSystem:
    """Real-time AAVE monitoring system with database logging"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize GPU acceleration (optional)
        self.gpu_available = False
        try:
            import cupy as cp
            import numpy as np
            self.cp = cp
            self.np = np
            test_array = cp.array([1.0, 2.0, 3.0])
            cp.sum(test_array)
            cp.cuda.Device(0).use()
            self.gpu_available = True
            self.logger.info("GPU acceleration enabled for AAVE monitoring")
        except Exception as e:
            self.cp = None
            self.np = None
            self.gpu_available = False
            self.logger.info(f"GPU acceleration not available: {e}")

        self.rpc_manager = RPCManager()
        self.w3 = None

        # AAVE contract details
        self.aave_address = "0x63706e401c06ac8513145b7687A14804d17f814b"
        self.aave_contract = None

        # Monitoring state
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # WebSocket integration
        self.ws_enabled = False
        self.ws_server = None
        self.ws_broadcast_task = None

        # Price and volume tracking
        self.current_price = 0.0
        self.price_history = []
        self.volume_history = []
        self.transaction_history = []

        # Database connection
        self.db_connection = None

        # Monitoring stats
        self.monitoring_stats = {
            'start_time': None,
            'total_price_updates': 0,
            'total_volume_updates': 0,
            'total_transaction_updates': 0,
            'last_price_update': None,
            'last_volume_update': None,
            'last_transaction_update': None
        }

    # ==============================
    # Initialization
    # ==============================
    async def initialize(self):
        """Initialize Web3 and AAVE contract"""
        try:
            self.w3 = await self.rpc_manager.get_w3_instance()

            # Initialize AAVE contract
            aave_abi = [
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
                }
            ]

            self.aave_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.aave_address),
                abi=aave_abi
            )

            self.is_running = True
            self.monitoring_stats['start_time'] = datetime.now(timezone.utc).isoformat()

            # Initialize database
            self._init_database()

            return True
        except Exception as e:
            self.logger.error(f"AAVE monitoring initialization failed: {e}")
            return False

    # ==============================
    # Database setup
    # ==============================
    def _init_database(self):
        """Initialize SQLite database for AAVE monitoring"""
        try:
            db_path = os.path.join(os.getcwd(), 'data', 'aave_monitoring.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.db_connection.cursor()

            # Create price history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aave_price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    price_usd REAL NOT NULL,
                    price_change_24h REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    source TEXT DEFAULT 'dexscreener'
                )
            ''')

            # Create transaction history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aave_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    tx_hash TEXT,
                    transaction_type TEXT,
                    amount REAL,
                    price_usd REAL,
                    volume_usd REAL,
                    buyer_address TEXT,
                    seller_address TEXT,
                    dex TEXT,
                    source TEXT DEFAULT 'dexscreener'
                )
            ''')

            # Create volume analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aave_volume_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    buy_volume REAL,
                    sell_volume REAL,
                    total_volume REAL,
                    buy_tx_count INTEGER,
                    sell_tx_count INTEGER,
                    total_tx_count INTEGER,
                    buy_sell_ratio REAL
                )
            ''')

            # Create monitoring log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aave_monitoring_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    price_usd REAL,
                    volume_24h REAL
                )
            ''')

            self.db_connection.commit()
            self.logger.info("AAVE monitoring database initialized successfully")

        except Exception as e:
            self.logger.error(f"AAVE database initialization failed: {e}")
            self.db_connection = None

    # ==============================
    # Price monitoring
    # ==============================
    def _get_aave_price_data(self) -> Optional[Dict[str, Any]]:
        """Get AAVE price data from DexScreener"""
        try:
            # Use the pair address we found earlier
            pair_address = "0x31F207bccc4604A51FA099071C72cd025cc823E5"

            url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('pair'):
                    pair = data['pair']

                    price_data = {
                        'price_usd': float(pair.get('priceUsd', 0)),
                        'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                        'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                        'market_cap': float(pair.get('marketCap', 0)),
                        'fdv': float(pair.get('fdv', 0)),
                        'txns': pair.get('txns', {}),
                        'source': 'dexscreener'
                    }

                    return price_data

        except Exception as e:
            self.logger.error(f"AAVE price data fetch failed: {e}")

        return None

    def _log_price_update(self, price_data: Dict[str, Any]):
        """Log price update to database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO aave_price_history (
                    timestamp, price_usd, price_change_24h, volume_24h,
                    market_cap, source
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                price_data.get('price_usd', 0),
                price_data.get('price_change_24h', 0),
                price_data.get('volume_24h', 0),
                price_data.get('market_cap', 0),
                price_data.get('source', 'dexscreener')
            ))

            self.db_connection.commit()
            self.monitoring_stats['total_price_updates'] += 1
            self.monitoring_stats['last_price_update'] = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            self.logger.error(f"Failed to log price update: {e}")

    # ==============================
    # Transaction monitoring
    # ==============================
    def _analyze_transaction_patterns(self, txns: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction patterns from DexScreener data"""
        analysis = {}

        for timeframe in ['h1', 'h6', 'h24']:
            if timeframe in txns:
                tx_data = txns[timeframe]
                buys = tx_data.get('buys', 0)
                sells = tx_data.get('sells', 0)
                total = buys + sells

                analysis[timeframe] = {
                    'buys': buys,
                    'sells': sells,
                    'total': total,
                    'buy_ratio': (buys / total * 100) if total > 0 else 0,
                    'sell_ratio': (sells / total * 100) if total > 0 else 0,
                    'sentiment': 'bullish' if buys > sells else 'bearish' if sells > buys else 'neutral'
                }

        return analysis

    def _log_transaction_analysis(self, analysis: Dict[str, Any]):
        """Log transaction analysis to database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            for timeframe, data in analysis.items():
                cursor.execute('''
                    INSERT INTO aave_volume_analysis (
                        timestamp, timeframe, buy_volume, sell_volume, total_volume,
                        buy_tx_count, sell_tx_count, total_tx_count, buy_sell_ratio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(timezone.utc).isoformat(),
                    timeframe,
                    0,  # We don't have volume breakdown from DexScreener
                    0,
                    0,
                    data['buys'],
                    data['sells'],
                    data['total'],
                    data['buy_ratio'] / data['sell_ratio'] if data['sell_ratio'] > 0 else 0
                ))

            self.db_connection.commit()
            self.monitoring_stats['total_transaction_updates'] += 1
            self.monitoring_stats['last_transaction_update'] = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            self.logger.error(f"Failed to log transaction analysis: {e}")

    # ==============================
    # Monitoring loop
    # ==============================
    async def run_monitoring_loop(self, interval_seconds: int = 30):
        """Main monitoring loop for AAVE data"""
        self.logger.info("Starting AAVE monitoring loop...")

        while not self.shutdown_event.is_set():
            try:
                # Get current AAVE data
                price_data = self._get_aave_price_data()

                if price_data:
                    # Log price update
                    self._log_price_update(price_data)

                    # Analyze and log transactions
                    if 'txns' in price_data:
                        tx_analysis = self._analyze_transaction_patterns(price_data['txns'])
                        self._log_transaction_analysis(tx_analysis)

                    # Update current price
                    self.current_price = price_data.get('price_usd', 0)

                    # Log monitoring update
                    self._log_monitoring_message(
                        'INFO',
                        f"AAVE Price: ${self.current_price:.6f} | Vol: ${price_data.get('volume_24h', 0):,.0f} | Change: {price_data.get('price_change_24h', 0):+.2f}%"
                    )

                    # Broadcast to WebSocket clients
                    await self._broadcast_monitoring_update(price_data, tx_analysis)

                else:
                    self._log_monitoring_message('WARNING', 'Failed to fetch AAVE price data')

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval_seconds)

    def _log_monitoring_message(self, level: str, message: str):
        """Log monitoring message to database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO aave_monitoring_log (
                    timestamp, level, message, price_usd, volume_24h
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                level,
                message,
                self.current_price,
                None  # Could add volume tracking here
            ))

            self.db_connection.commit()

        except Exception as e:
            self.logger.error(f"Failed to log monitoring message: {e}")

    async def _broadcast_monitoring_update(self, price_data: Dict[str, Any], tx_analysis: Dict[str, Any]):
        """Broadcast monitoring update to WebSocket clients"""
        if not self.ws_enabled or not self.ws_server:
            return

        try:
            update_data = {
                'type': 'aave_monitoring_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'price_data': price_data,
                'transaction_analysis': tx_analysis,
                'monitoring_stats': self.monitoring_stats
            }

            await self.ws_server.broadcast(update_data)

        except Exception as e:
            self.logger.error(f"WebSocket broadcast failed: {e}")

    # ==============================
    # WebSocket management
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8081):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"AAVE monitoring WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start AAVE WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task and not self.ws_broadcast_task.done():
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    if hasattr(self.ws_broadcast_task, '__await__'):
                        await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop AAVE WS server: {e}")

    # ==============================
    # Data retrieval methods
    # ==============================
    def get_recent_price_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent price history from database"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, price_usd, price_change_24h, volume_24h, market_cap
                FROM aave_price_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            prices = []
            for row in cursor.fetchall():
                prices.append({
                    'timestamp': row[0],
                    'price_usd': row[1],
                    'price_change_24h': row[2],
                    'volume_24h': row[3],
                    'market_cap': row[4]
                })

            return prices

        except Exception as e:
            self.logger.error(f"Failed to get price history: {e}")
            return []

    def get_transaction_analysis_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent transaction analysis from database"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, timeframe, buy_tx_count, sell_tx_count, total_tx_count, buy_sell_ratio
                FROM aave_volume_analysis
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            analyses = []
            for row in cursor.fetchall():
                analyses.append({
                    'timestamp': row[0],
                    'timeframe': row[1],
                    'buy_tx_count': row[2],
                    'sell_tx_count': row[3],
                    'total_tx_count': row[4],
                    'buy_sell_ratio': row[5]
                })

            return analyses

        except Exception as e:
            self.logger.error(f"Failed to get transaction analysis: {e}")
            return []

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics"""
        return self.monitoring_stats.copy()

    # ==============================
    # Cleanup
    # ==============================
    async def shutdown(self):
        """Clean shutdown"""
        self.logger.info("Shutting down AAVE monitoring...")
        self.shutdown_event.set()
        await self.stop_ws_server()
        self.is_running = False

    def print_monitoring_status(self):
        """Print comprehensive monitoring status"""
        try:
            stats = self.monitoring_stats

            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🚀 AAVE MONITORING SYSTEM                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 💎 Current AAVE Price: ${self.current_price:.6f}                              ║
║ 📊 Total Price Updates: {stats.get('total_price_updates', 0)}                   ║
║ 📈 Total Transaction Updates: {stats.get('total_transaction_updates', 0)}       ║
║ 🕐 Last Price Update: {stats.get('last_price_update', 'N/A')}             ║
║ 🕐 Last TX Update: {stats.get('last_transaction_update', 'N/A')}          ║
║ 🌐 WebSocket: {'Enabled' if self.ws_enabled else 'Disabled'}                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        except Exception as e:
            print(f"Error printing monitoring status: {e}")


# ==============================
# Main entry point
# ==============================
async def main():
    """Main entry point for AAVE monitoring system"""
    parser = argparse.ArgumentParser(description='AAVE Monitoring System')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in seconds (default: 30)')
    parser.add_argument('--ws-enable', action='store_true',
                       help='Enable WebSocket server for dashboard connectivity')
    parser.add_argument('--ws-port', type=int, default=8081,
                       help='WebSocket server port (default: 8081)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create monitoring system
    monitor = AAVEMonitoringSystem()

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal...")
        asyncio.create_task(monitor.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize system
    if not await monitor.initialize():
        print("Failed to initialize AAVE monitoring system")
        return 1

    print("AAVE monitoring system initialized successfully")
    print(f"Monitoring interval: {args.interval} seconds")
    if args.ws_enable:
        print(f"WebSocket: Enabled on port {args.ws_port}")

    # Start WebSocket server if enabled
    if args.ws_enable:
        await monitor.start_ws_server(port=args.ws_port)

    # Run monitoring loop
    try:
        await monitor.run_monitoring_loop(interval_seconds=args.interval)

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nError in monitoring loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await monitor.shutdown()
        print("AAVE monitoring system shut down successfully")

    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
