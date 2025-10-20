#!/usr/bin/env python3
"""
AAVE Trade History Monitor and Database System
Similar to MAXX trading system but for AAVE token monitoring on Base chain.

Features:
- SQLite database for storing AAVE trade history
- DexScreener API integration for transaction data
- Real-time monitoring and analytics
- WebSocket broadcasting for dashboards
- Comprehensive trade pattern analysis
"""

import os
import sys
import json
import time
import asyncio
import logging
import sqlite3
import argparse
import signal
import threading
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AAVE contract address on Base
AAVE_BASE_ADDRESS = "0x6374b2c0f24bA6D3bEF986b9F3e087ECD8Ac0bEA3"

class AaveTradeMonitor:
    """AAVE trade history monitoring system similar to MAXX trader"""

    def __init__(self):
        self.logger = logging.getLogger('AAVE_Monitor')
        self.db_connection = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        self.ws_server = None
        self.ws_enabled = False
        self.ws_broadcast_task = None

        # Monitoring stats
        self.monitoring_stats = {
            'start_time': None,
            'total_transactions': 0,
            'last_update': None,
            'api_calls': 0,
            'errors': 0
        }

        # Cache for API responses
        self._price_cache = {}
        self._price_cache_time = 0

    def _init_database(self):
        """Initialize SQLite database for AAVE trades"""
        try:
            # Create data directory if it doesn't exist
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)

            db_path = data_dir / 'aave_trades.db'
            self.db_connection = sqlite3.connect(str(db_path))

            cursor = self.db_connection.cursor()

            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    tx_hash TEXT UNIQUE,
                    block_number INTEGER,
                    trade_type TEXT,  -- 'BUY' or 'SELL' (inferred from DEX data)
                    amount_aave REAL,
                    amount_usd REAL,
                    price_usd REAL,
                    volume_usd REAL,
                    maker TEXT,
                    taker TEXT,
                    dex TEXT,
                    pair_address TEXT,
                    gas_used REAL,
                    gas_price REAL,
                    fee_usd REAL,
                    source TEXT DEFAULT 'dexscreener'
                )
            ''')

            # Create price_history table for price tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    price_usd REAL,
                    volume_24h REAL,
                    price_change_24h REAL,
                    market_cap REAL,
                    source TEXT DEFAULT 'dexscreener'
                )
            ''')

            # Create monitoring_stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_transactions INTEGER,
                    api_calls INTEGER,
                    errors INTEGER,
                    last_tx_hash TEXT
                )
            ''')

            self.db_connection.commit()
            self.logger.info("AAVE database initialized successfully")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.db_connection = None

    def _get_dexscreener_data(self, pair_address: str) -> Optional[Dict[str, Any]]:
        """Fetch AAVE pair data from DexScreener"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}"
            self.monitoring_stats['api_calls'] += 1

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"DexScreener API returned {response.status_code}")
                return None

            data = response.json()
            if not data.get('pair'):
                self.logger.warning("No pair data from DexScreener")
                return None

            return data['pair']

        except Exception as e:
            self.logger.error(f"DexScreener API error: {e}")
            self.monitoring_stats['errors'] += 1
            return None

    def _get_aave_transactions(self, pair_address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent AAVE transactions from DexScreener"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair_address}"
            self.monitoring_stats['api_calls'] += 1

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []

            data = response.json()
            pair = data.get('pair', {})

            # Get transaction data
            txns = pair.get('txns', {})

            # Combine all transaction types
            all_txns = []
            for tx_type, tx_list in txns.items():
                for tx in tx_list[:limit//4]:  # Distribute limit across types
                    tx['type'] = tx_type
                    all_txns.append(tx)

            # Sort by time (most recent first)
            all_txns.sort(key=lambda x: x.get('time', 0), reverse=True)

            return all_txns[:limit]

        except Exception as e:
            self.logger.error(f"Transaction fetch error: {e}")
            self.monitoring_stats['errors'] += 1
            return []

    def _store_transaction(self, tx_data: Dict[str, Any], pair_address: str):
        """Store transaction in database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Check if transaction already exists
            cursor.execute("SELECT id FROM trades WHERE tx_hash = ?", (tx_data.get('hash'),))
            if cursor.fetchone():
                return  # Already exists

            # Extract transaction data
            tx_hash = tx_data.get('hash')
            timestamp = datetime.fromtimestamp(tx_data.get('time', 0), tz=timezone.utc).isoformat()
            block_number = tx_data.get('block', 0)

            # Determine trade type (simplified - in reality would need more analysis)
            tx_type = tx_data.get('type', 'unknown').upper()

            # Extract amounts (this is simplified - real DEX data has more complex structure)
            amount_aave = tx_data.get('amount', 0)
            amount_usd = tx_data.get('value', 0)
            price_usd = tx_data.get('price', 0)

            # Additional data
            volume_usd = amount_usd
            maker = tx_data.get('from', '')
            taker = tx_data.get('to', '')
            dex = tx_data.get('dex', 'unknown')

            # Gas data (if available)
            gas_used = tx_data.get('gasUsed')
            gas_price = tx_data.get('gasPrice')
            fee_usd = tx_data.get('fee', 0)

            # Insert transaction
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, tx_hash, block_number, trade_type, amount_aave,
                    amount_usd, price_usd, volume_usd, maker, taker, dex,
                    pair_address, gas_used, gas_price, fee_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, tx_hash, block_number, tx_type, amount_aave,
                amount_usd, price_usd, volume_usd, maker, taker, dex,
                pair_address, gas_used, gas_price, fee_usd
            ))

            self.db_connection.commit()
            self.monitoring_stats['total_transactions'] += 1

        except Exception as e:
            self.logger.error(f"Failed to store transaction: {e}")
            self.monitoring_stats['errors'] += 1

    def _store_price_data(self, price_data: Dict[str, Any]):
        """Store price history data"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            timestamp = datetime.now(timezone.utc).isoformat()
            price_usd = price_data.get('priceUsd', 0)
            volume_24h = price_data.get('volume', {}).get('h24', 0)
            price_change_24h = price_data.get('priceChange', {}).get('h24', 0)
            market_cap = price_data.get('marketCap', 0)

            cursor.execute('''
                INSERT INTO price_history (
                    timestamp, price_usd, volume_24h, price_change_24h, market_cap
                ) VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, price_usd, volume_24h, price_change_24h, market_cap))

            self.db_connection.commit()

        except Exception as e:
            self.logger.error(f"Failed to store price data: {e}")

    def _update_monitoring_stats(self):
        """Update monitoring statistics in database"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Get latest transaction hash
            cursor.execute("SELECT tx_hash FROM trades ORDER BY timestamp DESC LIMIT 1")
            latest_tx = cursor.fetchone()
            last_tx_hash = latest_tx[0] if latest_tx else None

            cursor.execute('''
                INSERT INTO monitoring_stats (
                    timestamp, total_transactions, api_calls, errors, last_tx_hash
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                self.monitoring_stats['total_transactions'],
                self.monitoring_stats['api_calls'],
                self.monitoring_stats['errors'],
                last_tx_hash
            ))

            self.db_connection.commit()

        except Exception as e:
            self.logger.error(f"Failed to update monitoring stats: {e}")

    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AAVE trades from database"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, tx_hash, trade_type, amount_aave, amount_usd,
                       price_usd, volume_usd, dex
                FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'timestamp': row[0],
                    'tx_hash': row[1],
                    'trade_type': row[2],
                    'amount_aave': row[3],
                    'amount_usd': row[4],
                    'price_usd': row[5],
                    'volume_usd': row[6],
                    'dex': row[7]
                })

            return trades

        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []

    def get_price_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get price history for the last N hours"""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            since_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            cursor.execute('''
                SELECT timestamp, price_usd, volume_24h, price_change_24h
                FROM price_history
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (since_time.isoformat(),))

            prices = []
            for row in cursor.fetchall():
                prices.append({
                    'timestamp': row[0],
                    'price_usd': row[1],
                    'volume_24h': row[2],
                    'price_change_24h': row[3]
                })

            return prices

        except Exception as e:
            self.logger.error(f"Failed to get price history: {e}")
            return []

    def get_trading_stats(self) -> Dict[str, Any]:
        """Get comprehensive trading statistics"""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Get total transactions
            cursor.execute("SELECT COUNT(*) FROM trades")
            total_txns = cursor.fetchone()[0]

            # Get transactions in last 24h
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            cursor.execute("SELECT COUNT(*) FROM trades WHERE timestamp >= ?", (yesterday.isoformat(),))
            txns_24h = cursor.fetchone()[0]

            # Get volume stats
            cursor.execute("SELECT SUM(volume_usd) FROM trades")
            total_volume = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(volume_usd) FROM trades WHERE timestamp >= ?", (yesterday.isoformat(),))
            volume_24h = cursor.fetchone()[0] or 0

            # Get price stats
            cursor.execute("SELECT AVG(price_usd), MIN(price_usd), MAX(price_usd) FROM price_history WHERE timestamp >= ?", (yesterday.isoformat(),))
            price_stats = cursor.fetchone()
            avg_price_24h = price_stats[0] or 0
            min_price_24h = price_stats[1] or 0
            max_price_24h = price_stats[2] or 0

            return {
                'total_transactions': total_txns,
                'transactions_24h': txns_24h,
                'total_volume_usd': total_volume,
                'volume_24h_usd': volume_24h,
                'avg_price_24h': avg_price_24h,
                'min_price_24h': min_price_24h,
                'max_price_24h': max_price_24h
            }

        except Exception as e:
            self.logger.error(f"Failed to get trading stats: {e}")
            return {}

    async def monitor_aave_trades(self, pair_address: str, interval_seconds: int = 60):
        """Main monitoring loop for AAVE trades"""
        self.logger.info(f"Starting AAVE trade monitoring for pair: {pair_address}")

        while not self.shutdown_event.is_set():
            try:
                # Fetch current price data
                price_data = self._get_dexscreener_data(pair_address)
                if price_data:
                    self._store_price_data(price_data)

                    # Log current price
                    price_usd = price_data.get('priceUsd', 0)
                    volume_24h = price_data.get('volume', {}).get('h24', 0)
                    price_change = price_data.get('priceChange', {}).get('h24', 0)

                    self.logger.info(f"AAVE Price: ${price_usd:.6f} | 24h Vol: ${volume_24h:,.0f} | Change: {price_change:+.2f}%")

                # Fetch recent transactions
                transactions = self._get_aave_transactions(pair_address, limit=50)
                for tx in transactions:
                    self._store_transaction(tx, pair_address)

                # Update monitoring stats
                self._update_monitoring_stats()

                # Log summary
                stats = self.get_trading_stats()
                self.logger.info(f"Monitoring: {stats.get('transactions_24h', 0)} txns/24h | Vol: ${stats.get('volume_24h_usd', 0):,.0f}")

                # Broadcast to WebSocket if enabled
                if self.ws_enabled and price_data:
                    await self._ws_broadcast_price(price_data)

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                self.monitoring_stats['errors'] += 1
                await asyncio.sleep(10)

    async def _ws_broadcast_price(self, price_data: Dict[str, Any]):
        """Broadcast price data via WebSocket"""
        if not self.ws_enabled or not hasattr(self, 'ws_server') or not self.ws_server:
            return

        try:
            await self.ws_server.broadcast({
                'type': 'aave_price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price_usd': price_data.get('priceUsd', 0),
                    'volume_24h': price_data.get('volume', {}).get('h24', 0),
                    'price_change_24h': price_data.get('priceChange', {}).get('h24', 0),
                    'market_cap': price_data.get('marketCap', 0)
                }
            })
        except Exception as e:
            self.logger.debug(f"WS broadcast error: {e}")

    def print_monitoring_status(self):
        """Print comprehensive monitoring status"""
        try:
            # Get current price data
            pair_address = self._get_aave_pair_address()
            if pair_address:
                price_data = self._get_dexscreener_data(pair_address)
                if price_data:
                    price_usd = price_data.get('priceUsd', 0)
                    volume_24h = price_data.get('volume', {}).get('h24', 0)
                    price_change = price_data.get('priceChange', {}).get('h24', 0)
                    market_cap = price_data.get('marketCap', 0)
                else:
                    price_usd = volume_24h = price_change = market_cap = 0
            else:
                price_usd = volume_24h = price_change = market_cap = 0

            # Get trading stats
            stats = self.get_trading_stats()

            # Monitoring stats
            runtime_str = "N/A"
            if self.monitoring_stats.get('start_time'):
                try:
                    start_dt = datetime.fromisoformat(self.monitoring_stats['start_time'].replace('Z', '+00:00'))
                    runtime = datetime.now(timezone.utc) - start_dt
                    hours, remainder = divmod(int(runtime.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    runtime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                except Exception:
                    pass

            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🚀 AAVE TRADE MONITOR                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 💎 AAVE Price: ${price_usd:.6f}  |  Market Cap: ${market_cap:,.0f}            ║
║ 📊 24h Volume: ${volume_24h:,.0f}  |  Change: {price_change:+.2f}%             ║
║                                                                              ║
║ 📈 TRADING STATISTICS                                                       ║
║ Total Transactions: {stats.get('total_transactions', 0):,}                    ║
║ 24h Transactions: {stats.get('transactions_24h', 0)}                          ║
║ Total Volume: ${stats.get('total_volume_usd', 0):,.0f}                         ║
║ 24h Volume: ${stats.get('volume_24h_usd', 0):,.0f}                             ║
║                                                                              ║
║ 🔍 MONITORING STATUS                                                        ║
║ Runtime: {runtime_str}  |  API Calls: {self.monitoring_stats.get('api_calls', 0)} ║
║ Errors: {self.monitoring_stats.get('errors', 0)}                                ║
║ WebSocket: {'Enabled' if self.ws_enabled else 'Disabled'}                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

        except Exception as e:
            print(f"Error printing monitoring status: {e}")

    def _get_aave_pair_address(self) -> Optional[str]:
        """Find AAVE pair address on Base chain"""
        try:
            # Search for AAVE pairs on Base
            url = "https://api.dexscreener.com/latest/dex/search"
            params = {
                'q': f'{AAVE_BASE_ADDRESS}',
                'chainId': 'base'
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])

                # Find the pair with highest liquidity
                if pairs:
                    # Sort by liquidity
                    pairs.sort(key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
                    return pairs[0].get('pairAddress')

        except Exception as e:
            self.logger.error(f"Failed to find AAVE pair: {e}")

        return None

    async def start_monitoring(self, pair_address: Optional[str] = None, ws_enable: bool = False, ws_port: int = 8081):
        """Start the AAVE monitoring system"""
        # Initialize database
        self._init_database()

        # Find AAVE pair if not provided
        if not pair_address:
            self.logger.info("Searching for AAVE pair on Base chain...")
            pair_address = self._get_aave_pair_address()
            if not pair_address:
                self.logger.error("Could not find AAVE pair address")
                return False

        self.logger.info(f"Using AAVE pair: {pair_address}")

        # Start WebSocket server if enabled
        if ws_enable:
            try:
                # Import WebSocket server from MAXX system
                from maxx_trader_fix import DashboardWebSocketServer
                self.ws_server = DashboardWebSocketServer(host='localhost', port=ws_port)
                await self.ws_server.start()
                self.ws_enabled = True
                self.logger.info(f"AAVE Dashboard WS enabled at ws://localhost:{ws_port}/ws")
            except ImportError:
                self.logger.warning("WebSocket server not available")
            except Exception as e:
                self.logger.error(f"Failed to start WS server: {e}")

        # Set start time
        self.monitoring_stats['start_time'] = datetime.now(timezone.utc).isoformat()
        self.is_running = True

        # Start monitoring loop
        await self.monitor_aave_trades(pair_address)

        return True

    async def shutdown(self):
        """Clean shutdown"""
        self.logger.info("Shutting down AAVE monitor...")
        self.shutdown_event.set()
        self.is_running = False

        # Stop WebSocket server
        if self.ws_server:
            try:
                await self.ws_server.stop()
            except Exception as e:
                self.logger.error(f"Error stopping WS server: {e}")

        # Close database
        if self.db_connection:
            self.db_connection.close()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AAVE Trade History Monitor')
    parser.add_argument('--pair-address', type=str, help='AAVE pair address (auto-discovered if not provided)')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--ws-enable', action='store_true', help='Enable WebSocket server for dashboard')
    parser.add_argument('--ws-port', type=int, default=8081, help='WebSocket server port (default: 8081)')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create monitor instance
    monitor = AaveTradeMonitor()

    # Setup signal handlers
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal...")
        asyncio.create_task(monitor.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        print("Starting AAVE Trade Monitor...")
        success = await monitor.start_monitoring(
            pair_address=args.pair_address,
            ws_enable=args.ws_enable,
            ws_port=args.ws_port
        )

        if not success:
            print("Failed to start monitoring")
            return 1

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await monitor.shutdown()
        print("AAVE Monitor shut down successfully")

    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
