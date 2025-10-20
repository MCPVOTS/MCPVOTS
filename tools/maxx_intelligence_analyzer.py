#!/usr/bin/env python3
"""
MAXX Token Intelligence Analyzer V2.0
====================================

Comprehensive trade tracking and intelligence system for MAXX token
- Tracks all trades since inception
- Detects massive pump patterns
- Optimizes gas usage
- Identifies big buy/sell opportunities
- Generates actionable trading signals
"""

import asyncio
import aiohttp
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
import time
from collections import defaultdict, Counter
import sqlite3
import pickle
import os
from env_loader import load_env_once

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"maxx_intelligence_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MAXXIntelligenceAnalyzer:
    """Advanced MAXX token intelligence analyzer"""

    def __init__(self):
        load_env_once()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self.config = {
            'maxx_contract': '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467',
            'base_chain_id': 8453,
            # Prefer BaseScan API (set BASESCAN_API_URL / BASESCAN_API_KEY via env); fall back to Etherscan v2 if provided
            'basescan_api': os.getenv('BASESCAN_API_URL', 'https://api.basescan.org/api'),
            'api_key': os.getenv('BASESCAN_API_KEY', os.getenv('ETHERSCAN_API_KEY', '')),

            # Analysis parameters
            'pump_threshold': 500.0,  # 500% price increase
            'big_buy_threshold': 10.0,  # $10+ worth of ETH
            'whale_threshold': 100.0,  # $100+ transactions
            'gas_optimization_level': 'AGGRESSIVE',

            # Time windows for analysis
            'time_windows': {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '6h': 21600,
                '24h': 86400
            }
        }

        # Data storage
        self.db_path = Path("data/maxx_intelligence.db")
        self.json_path = Path("maxx_trades_intelligence.json")
        self.cache_path = Path("maxx_cache.pkl")

        # Initialize database
        self._init_database()

        # Trading patterns
        self.patterns = {
            'accumulation': [],
            'distribution': [],
            'pump': [],
            'dump': [],
            'whale_movements': [],
            'coordinated_activity': []
        }

        # Active monitoring wallets
        self.monitored_wallets = set()
        self.whale_wallets = set()
        self.bot_wallets = set()

        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'total_volume': 0,
            'unique_wallets': 0,
            'avg_trade_size': 0,
            'pump_events': 0,
            'profitable_signals': 0
        }

        # Last scan summary for diagnostics
        self.last_scan_summary = {
            'start_block': 0,
            'end_block': 0,
            'batches': 0,
            'trades_collected': 0
        }
        # Caches
        self._price_cache = {}  # key -> (price_usd, fetched_at)
        self._block_ts_cache = {}
        # Token config
        self.maxx_decimals = int(os.getenv('MAXX_DECIMALS', '18'))
        # Optional: limit backward scan range to speed up logs fallback
        self.min_block_search = int(os.getenv('MAXX_DEPLOY_BLOCK', '0'))
        # Tuning for logs fallback progress/exit
        self.logs_max_empty_windows = int(os.getenv('LOGS_MAX_EMPTY_WINDOWS', '80'))  # ~80 windows
        self.logs_info_every = int(os.getenv('LOGS_INFO_EVERY', '10'))  # log every N windows

    def _init_database(self):
        """Initialize SQLite database for trade tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE,
                timestamp INTEGER,
                block_number INTEGER,
                from_address TEXT,
                to_address TEXT,
                value_eth REAL,
                value_usd REAL,
                gas_used INTEGER,
                gas_price_gwei REAL,
                transaction_type TEXT,
                price_at_time REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_profiles (
                address TEXT PRIMARY KEY,
                first_seen INTEGER,
                last_seen INTEGER,
                total_trades INTEGER,
                total_volume REAL,
                avg_trade_size REAL,
                wallet_type TEXT,
                profit_loss REAL,
                success_rate REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_patterns (
                address TEXT PRIMARY KEY,
                accumulation_score REAL,
                distribution_score REAL,
                whale_score REAL,
                burstiness REAL,
                avg_intertrade_sec REAL,
                trades_per_day REAL,
                time_of_day_json TEXT,
                last_updated INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pump_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time INTEGER,
                end_time INTEGER,
                start_price REAL,
                end_price REAL,
                price_change_pct REAL,
                volume_change_pct REAL,
                duration_minutes INTEGER,
                participants_count INTEGER,
                confidence_score REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                signal_type TEXT,
                confidence REAL,
                expected_return REAL,
                time_horizon TEXT,
                trigger_event TEXT,
                metadata TEXT
            )
        ''')

        conn.commit()
        # Migrate trades table to include token_amount & token_decimals if missing
        cursor.execute("PRAGMA table_info(trades)")
        cols = [row[1] for row in cursor.fetchall()]
        self.trades_has_token_cols = ('token_amount' in cols and 'token_decimals' in cols)
        if 'token_amount' not in cols:
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN token_amount REAL")
            except Exception:
                pass
        if 'token_decimals' not in cols:
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN token_decimals INTEGER")
            except Exception:
                pass
        conn.commit()
        conn.close()
        self.logger.info("Database initialized")

    async def collect_historical_trades(self, start_date=None):
        """Collect all MAXX trades since inception"""
        self.logger.info("=" * 80)
        self.logger.info("COLLECTING HISTORICAL MAXX TRADES")
        self.logger.info("=" * 80)

        all_trades: List[Dict] = []

        # Get current block and calculate start block
        current_block = await self._get_latest_block()

        # MAXX deployed around Oct 2024, calculate approximate block span
        blocks_per_day = 7200  # ~8 sec per block on Base

        if not start_date:
            days_back = 180  # 6 months back
            start_block = max(0, current_block - (blocks_per_day * days_back))
        else:
            # Calculate from specific date
            days_back = (datetime.now() - start_date).days
            start_block = max(0, current_block - (blocks_per_day * days_back))

        self.logger.info(f"Scanning blocks {start_block} to {current_block}")
        self.last_scan_summary.update({
            'start_block': start_block,
            'end_block': current_block,
            'batches': 0,
            'trades_collected': 0
        })

        # Collect trades in batches
        batch_size = 10000
        for from_block in range(start_block, current_block, batch_size):
            to_block = min(from_block + batch_size, current_block)

            self.logger.info(f"Fetching blocks {from_block} to {to_block}...")

            # Get MAXX transfer events
            trades = await self._fetch_trades_in_range(from_block, to_block)
            all_trades.extend(trades)

            # Update diagnostics
            self.last_scan_summary['batches'] += 1
            self.last_scan_summary['trades_collected'] += len(trades)
            self.logger.info(
                f"  -> Retrieved {len(trades)} transfers in this batch (total so far: {self.last_scan_summary['trades_collected']})"
            )

            # Save batch to database
            await self._save_trades_batch(trades)

            # Rate limiting
            await asyncio.sleep(1)

        self.logger.info(f"Collected {len(all_trades)} historical trades")
        return all_trades

    async def collect_recent_trades(self, limit: int = 1000, page_size: int = 100):
        """Collect most recent MAXX transfers using paginated API calls.

        limit: total records to fetch
        page_size: items per page (max 100 on most APIs)
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"COLLECTING RECENT MAXX TRADES (limit={limit})")
        self.logger.info("=" * 60)

        url = self.config['basescan_api']
        trades: List[Dict] = []
        pages = max(1, (limit + page_size - 1) // page_size)

        for page in range(1, pages + 1):
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': self.config['maxx_contract'],
                'page': page,
                'offset': page_size,
                'sort': 'desc',
                'apikey': self.config['api_key']
            }
            if '/v2/' in url:
                params['chainid'] = self.config['base_chain_id']
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        if str(data.get('status', '0')) == '1':
                            batch = []
                            for tx in data.get('result', []):
                                trade = {
                                    'tx_hash': tx.get('hash') or tx.get('transactionHash'),
                                    'timestamp': int(tx.get('timeStamp') or 0),
                                    'block_number': int(tx.get('blockNumber') or 0),
                                    'from_address': (tx.get('from') or '').lower(),
                                    'to_address': (tx.get('to') or '').lower(),
                                    'value_eth': 0.0,
                                    'gas_used': int(tx.get('gasUsed') or 0),
                                    'gas_price_gwei': float(tx.get('gasPrice') or 0) / 1e9 if tx.get('gasPrice') else 0.0,
                                    'transaction_type': 'TRANSFER'
                                }
                                raw_val = tx.get('value')
                                token_dec = int(tx.get('tokenDecimal') or self.maxx_decimals)
                                try:
                                    token_amount = (int(raw_val) / (10 ** token_dec)) if raw_val is not None else 0.0
                                except Exception:
                                    token_amount = 0.0
                                price_usd = await self._get_maxx_price_usd()
                                trade['value_usd'] = float(token_amount) * float(price_usd)
                                trade['token_amount'] = float(token_amount)
                                trade['token_decimals'] = token_dec
                                batch.append(trade)
                            self.logger.info(f"Page {page}: fetched {len(batch)} transfers")
                            trades.extend(batch)
                            await self._save_trades_batch(batch)
                            if len(trades) >= limit:
                                break
                        else:
                            self.logger.warning(f"recent tokentx page {page} returned status {data.get('status')}: {data.get('message')}")
            except Exception as e:
                self.logger.error(f"Error fetching recent page {page}: {e}")
            await asyncio.sleep(0.2)

        # Trim to limit
        if len(trades) > limit:
            trades = trades[:limit]
        self.logger.info(f"Collected {len(trades)} recent trades")
        return trades

    async def collect_recent_trades_via_logs(self, limit: int = 1000, step: int = 2000):
        """Collect most recent MAXX transfers by scanning logs backwards from latest block."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"COLLECTING RECENT MAXX TRADES VIA LOGS (limit={limit}, step={step})")
        self.logger.info("=" * 60)
        latest = await self._get_latest_block()
        if not latest or latest <= 0:
            self.logger.warning("Could not determine latest block; using default 15000000")
            latest = 15000000
        # Determine lower bound to avoid scanning entire chain
        min_block = self.min_block_search if self.min_block_search > 0 else max(0, latest - 2_000_000)
        collected = []
        to_block = latest
        empty_windows = 0
        windows_scanned = 0
        while len(collected) < limit and to_block > 0:
            from_block = max(min_block, to_block - step)
            self.logger.info(f"scan logs {from_block}-{to_block}...")
            logs_trades = await self._fetch_token_transfer_logs(from_block, to_block)
            if logs_trades:
                # Sort desc
                logs_trades.sort(key=lambda t: (t.get('block_number', 0), t.get('timestamp', 0)), reverse=True)
                for t in logs_trades:
                    collected.append(t)
                    if len(collected) >= limit:
                        break
                await self._save_trades_batch(logs_trades)
                self.logger.info(f"logs window {from_block}-{to_block}: +{len(logs_trades)} (total {len(collected)})")
                empty_windows = 0
            else:
                empty_windows += 1
                windows_scanned += 1
                if (windows_scanned % self.logs_info_every) == 0:
                    self.logger.info(f"No logs in last {self.logs_info_every} windows. Scanned down to block {from_block} (empty windows: {empty_windows})")
                if empty_windows >= self.logs_max_empty_windows:
                    self.logger.warning(f"Stopping early after {empty_windows} empty windows without results. Returning {len(collected)} trades collected so far.")
                    break
            # Move window down; stop if reached min_block
            if from_block <= min_block:
                if len(collected) < limit:
                    self.logger.info(f"Reached min scan block {min_block} with {len(collected)} trades collected. Stopping.")
                break
            to_block = from_block - 1
            await asyncio.sleep(0.2)
        if len(collected) > limit:
            collected = collected[:limit]
        self.logger.info(f"Collected {len(collected)} recent trades via logs")
        return collected

    async def import_trades_from_csv(self, csv_path: str, limit: Optional[int] = None) -> List[Dict]:
        """Import MAXX transfers from a BaseScan/Etherscan CSV export and persist them.

        Expected columns (flexible):
        - Txhash or Hash
        - UnixTimestamp or Timestamp or DateTime (UTC)
        - From, To
        - TokenValue or Value
        - TokenDecimal (optional)
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"IMPORTING TRADES FROM CSV: {csv_path}")
        self.logger.info("=" * 60)
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self.logger.error(f"Failed to read CSV {csv_path}: {e}")
            return []

        # Normalize column names (strip and lower for matching)
        cols_map = {c.strip().lower(): c for c in df.columns}
        def get_col(*names):
            for n in names:
                key = n.lower()
                if key in cols_map:
                    return cols_map[key]
            return None

        col_tx = get_col('txhash', 'hash', 'txn hash', 'transactionhash', 'tx hash')
        col_ts = get_col('unixtimestamp', 'timestamp', 'date', 'datetime (utc)', 'time', 'datetime')
        col_from = get_col('from', 'from_address', 'from address')
        col_to = get_col('to', 'to_address', 'to address')
        # Many CSVs use Quantity / Token Quantity for human-readable token amount
        col_val = get_col('tokenvalue', 'value', 'amount', 'quantity', 'token quantity', 'token amount', 'qty')
        col_dec = get_col('tokendecimal', 'token decimal', 'decimals')
        col_block = get_col('blocknumber', 'block')

        missing = [name for name, col in [('txhash', col_tx), ('timestamp', col_ts), ('from', col_from), ('to', col_to), ('value', col_val)] if col is None]
        if missing:
            self.logger.warning(f"CSV missing columns: {missing}. Will attempt best-effort import.")

        # Get one price for all rows to avoid per-row API calls
        price_usd = await self._get_maxx_price_usd()
        token_decimals_default = self.maxx_decimals

        trades: List[Dict] = []
        count = 0
        for i, r in enumerate(df.to_dict(orient='records')):
            txh = str(r.get(col_tx, '') or '').strip() if col_tx else ''
            # Timestamp: prefer Unix numeric, else parse datetime string
            ts_val = r.get(col_ts) if col_ts else None
            ts = 0
            if ts_val is not None and ts_val != '':
                try:
                    ts = int(ts_val)
                except Exception:
                    try:
                        ts = int(pd.to_datetime(str(ts_val), utc=True, errors='coerce').timestamp())
                    except Exception:
                        ts = 0
            from_addr = str(r.get(col_from, '') or '').lower() if col_from else ''
            to_addr = str(r.get(col_to, '') or '').lower() if col_to else ''
            block_number = 0
            if col_block:
                try:
                    block_number = int(r.get(col_block))
                except Exception:
                    block_number = 0

            # Value handling
            token_amount = 0.0
            if col_val:
                try:
                    raw = r.get(col_val)
                    # Some CSVs include commas or spaces
                    sval = str(raw).replace(',', '').strip()
                    token_amount = float(sval) if sval else 0.0
                except Exception:
                    token_amount = 0.0
            token_dec = token_decimals_default
            if col_dec:
                try:
                    token_dec = int(r.get(col_dec))
                except Exception:
                    token_dec = token_decimals_default

            # Ensure unique tx hash if missing to avoid UNIQUE constraint collisions
            if not txh:
                txh = f"csv:{ts}:{from_addr}:{to_addr}:{i}"

            trade = {
                'tx_hash': txh,
                'timestamp': ts,
                'block_number': block_number,
                'from_address': from_addr,
                'to_address': to_addr,
                'value_eth': 0.0,
                'value_usd': float(token_amount) * float(price_usd),
                'gas_used': 0,
                'gas_price_gwei': 0.0,
                'transaction_type': 'TRANSFER',
                'token_amount': float(token_amount),
                'token_decimals': token_dec
            }
            trades.append(trade)
            count += 1
            if limit and count >= limit:
                break

        await self._save_trades_batch(trades)
        self.logger.info(f"Imported {len(trades)} trades from CSV")
        return trades

    async def _fetch_trades_in_range(self, from_block, to_block):
        """Fetch MAXX trades in block range"""
        trades = []

    # Etherscan/BaseScan API to get token transfers
        url = self.config['basescan_api']
        # BaseScan expects chain via hostname; do not send chainid for BaseScan. Keep it generic for Etherscan v2 if used.
        params = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': self.config['maxx_contract'],
            'startblock': from_block,
            'endblock': to_block,
            'sort': 'asc',
            'apikey': self.config['api_key']
        }
        # If using Etherscan v2 multi-chain endpoint, include chainid
        if '/v2/' in url:
            params['chainid'] = self.config['base_chain_id']

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    status = str(data.get('status', '0'))
                    message = data.get('message') or ''

                    if status == '1':
                        for tx in data.get('result', []):
                            # Convert to standard format
                            # Note: tokentx 'value' is token amount (raw, decimals in tokenDecimal)
                            trade = {
                                'tx_hash': tx.get('hash') or tx.get('transactionHash'),
                                'timestamp': int(tx.get('timeStamp') or 0),
                                'block_number': int(tx.get('blockNumber') or 0),
                                'from_address': (tx.get('from') or '').lower(),
                                'to_address': (tx.get('to') or '').lower(),
                                'value_eth': 0.0,
                                'gas_used': int(tx.get('gasUsed') or 0),
                                'gas_price_gwei': float(tx.get('gasPrice') or 0) / 1e9 if tx.get('gasPrice') else 0.0,
                                'transaction_type': 'TRANSFER'
                            }

                            # Token amount & USD calc
                            raw_val = tx.get('value')
                            token_dec = int(tx.get('tokenDecimal') or self.maxx_decimals)
                            try:
                                token_amount = (int(raw_val) / (10 ** token_dec)) if raw_val is not None else 0.0
                            except Exception:
                                token_amount = 0.0
                            price_usd = await self._get_maxx_price_usd()
                            trade['value_usd'] = float(token_amount) * float(price_usd)
                            trade['token_amount'] = float(token_amount)
                            trade['token_decimals'] = token_dec

                            trades.append(trade)
                    else:
                        # Common: status '0' with 'No transactions found' or rate limit messages
                        if 'No transactions found' in message:
                            self.logger.debug(f"No transfers found in {from_block}-{to_block}.")
                        else:
                            self.logger.warning(f"Token tx query returned status {status}: {message} (range {from_block}-{to_block}) | result={data.get('result')}")
                            # Fallback to logs.getLogs which is often more reliable per range
                            logs_trades = await self._fetch_token_transfer_logs(from_block, to_block)
                            if logs_trades:
                                self.logger.info(f"Fallback logs.getLogs returned {len(logs_trades)} transfers")
                                trades.extend(logs_trades)

        except Exception as e:
            self.logger.error(f"Error fetching trades: {e}")

        return trades

    async def _fetch_token_transfer_logs(self, from_block: int, to_block: int):
        """Fallback: Use logs.getLogs on BaseScan/Etherscan to fetch ERC-20 Transfer events."""
        url = self.config['basescan_api']
        params = {
            'module': 'logs',
            'action': 'getLogs',
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': self.config['maxx_contract'],
            'topic0': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',  # Transfer(address,address,uint256)
            'apikey': self.config['api_key']
        }
        if '/v2/' in url:
            params['chainid'] = self.config['base_chain_id']

        out = []
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    result = data.get('result')
                    status = str(data.get('status', ''))
                    message = (data.get('message') or '').lower()
                    # Some endpoints may omit status but return a list result; treat list as success
                    if (isinstance(result, list) and len(result) >= 0) or status == '1':
                        for log in (result or []):
                            topics = log.get('topics', [])
                            if len(topics) < 3:
                                continue
                            # Topics are 32-byte hex values; extract last 20 bytes (40 hex chars)
                            t1 = (topics[1] or '').lower()
                            t2 = (topics[2] or '').lower()
                            from_addr = '0x' + t1[-40:]
                            to_addr = '0x' + t2[-40:]
                            # Timestamps: try log.timeStamp (hex), else fetch by block
                            ts_raw = log.get('timeStamp')
                            if isinstance(ts_raw, str) and ts_raw.startswith('0x'):
                                try:
                                    ts = int(ts_raw, 16)
                                except Exception:
                                    ts = 0
                            else:
                                ts = int(ts_raw or 0)
                            bl_raw = log.get('blockNumber')
                            if isinstance(bl_raw, str) and bl_raw.startswith('0x'):
                                try:
                                    bl = int(bl_raw, 16)
                                except Exception:
                                    bl = 0
                            else:
                                bl = int(bl_raw or 0)
                            if ts == 0 and bl:
                                ts = await self._get_block_timestamp(bl)
                            txh = log.get('transactionHash')
                            # Amount is uint256 in data; store as tokens (no USD here)
                            try:
                                amount = int(log.get('data', '0x0'), 16)
                            except Exception:
                                amount = 0
                            token_dec = self.maxx_decimals
                            token_amount = amount / (10 ** token_dec)
                            price_usd = await self._get_maxx_price_usd()
                            out.append({
                                'tx_hash': txh,
                                'timestamp': ts,
                                'block_number': bl,
                                'from_address': from_addr,
                                'to_address': to_addr,
                                'value_eth': 0.0,
                                'value_usd': float(token_amount) * float(price_usd),
                                'gas_used': 0,
                                'gas_price_gwei': 0.0,
                                'transaction_type': 'TRANSFER',
                                'token_amount': float(token_amount),
                                'token_decimals': token_dec
                            })
                    else:
                        # Rate limit or empty
                        if 'rate limit' in message or 'too many' in message:
                            self.logger.warning(f"Rate limited on logs.getLogs for {from_block}-{to_block}; backing off briefly")
                            await asyncio.sleep(1.0)
                        else:
                            self.logger.debug(f"logs.getLogs returned status {data.get('status')}: {data.get('message')} for {from_block}-{to_block}")
        except Exception as e:
            self.logger.error(f"Error fetching logs.getLogs: {e}")
        return out

    async def _get_block_timestamp(self, block_number: int) -> int:
        """Get block timestamp via proxy; cached to reduce API calls."""
        if block_number in self._block_ts_cache:
            return self._block_ts_cache[block_number]
        url = self.config['basescan_api']
        params = {
            'module': 'proxy',
            'action': 'eth_getBlockByNumber',
            'tag': hex(block_number),
            'boolean': 'false',
            'apikey': self.config['api_key']
        }
        if '/v2/' in url:
            params['chainid'] = self.config['base_chain_id']
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    result = data.get('result') or {}
                    ts_hex = result.get('timestamp')
                    if isinstance(ts_hex, str) and ts_hex.startswith('0x'):
                        ts = int(ts_hex, 16)
                        self._block_ts_cache[block_number] = ts
                        return ts
        except Exception as e:
            self.logger.debug(f"Block ts fetch failed for {block_number}: {e}")
        return 0

    async def _get_maxx_price_usd(self) -> float:
        """Fetch current MAXX price in USD via DexScreener; cache for 60s."""
        cache_key = 'maxx_price_usd'
        now = time.time()
        if cache_key in self._price_cache:
            price, asof = self._price_cache[cache_key]
            if now - asof < 60:
                return price
        token = self.config['maxx_contract']
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    pairs = data.get('pairs') or []
                    # Prefer Base pairs; pick highest liquidity
                    base_pairs = [p for p in pairs if (p.get('chainId') == 'base' or p.get('chainId') == 8453)]
                    use = base_pairs or pairs
                    if use:
                        use.sort(key=lambda p: float(p.get('liquidity', {}).get('usd', 0)) if isinstance(p.get('liquidity'), dict) else 0, reverse=True)
                        price = float(use[0].get('priceUsd') or 0)
                        if price > 0:
                            self._price_cache[cache_key] = (price, now)
                            return price
        except Exception as e:
            self.logger.debug(f"DexScreener price fetch failed: {e}")
        return 0.0

    async def analyze_pump_patterns(self, trades):
        """Analyze patterns for massive pump detection"""
        self.logger.info("\n" + "="*60)
        self.logger.info("ANALYZING PUMP PATTERNS")
        self.logger.info("="*60)

        # Convert to DataFrame for analysis
        df = pd.DataFrame(trades)
        if df.empty:
            return []

        # Sort by timestamp
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('datetime')

        pump_events = []

        # Sliding window analysis
        for window_minutes in [5, 15, 30, 60]:
            window_seconds = window_minutes * 60

            # Group trades into time windows
            df['time_window'] = df['timestamp'] // window_seconds
            grouped = df.groupby('time_window').agg({
                'value_usd': ['sum', 'mean', 'count'],
                'from_address': 'nunique',
                'timestamp': ['min', 'max']
            }).reset_index()

            # Detect pumps
            for _, group in grouped.iterrows():
                volume = group[('value_usd', 'sum')]
                avg_size = group[('value_usd', 'mean')]
                trade_count = group[('value_usd', 'count')]
                unique_addresses = group[('from_address', 'nunique')]

                # Pump criteria
                if volume > 1000 and trade_count > 10:  # High volume
                    if avg_size > 10 and unique_addresses < 20:  # Concentrated buying
                        pump_event = {
                            'timestamp': group[('timestamp', 'min')],
                            'window_minutes': window_minutes,
                            'volume_usd': volume,
                            'trade_count': trade_count,
                            'unique_addresses': unique_addresses,
                            'avg_trade_size': avg_size,
                            'pump_score': min(1.0, volume / 10000),
                            'type': 'PUMP_DETECTED'
                        }
                        pump_events.append(pump_event)
                        self.logger.info(f"PUMP DETECTED: {pump_event}")

        # Save pump events
        await self._save_pump_events(pump_events)

        return pump_events

    async def identify_whale_activity(self, trades):
        """Identify whale wallet activity"""
        self.logger.info("\n" + "="*60)
        self.logger.info("IDENTIFYING WHALE ACTIVITY")
        self.logger.info("="*60)

        # Group by wallet
        wallet_stats = defaultdict(lambda: {
            'total_volume': 0,
            'trade_count': 0,
            'first_trade': None,
            'last_trade': None,
            'avg_size': 0
        })

        for trade in trades:
            wallet = trade['from_address']
            stats = wallet_stats[wallet]

            stats['total_volume'] += trade['value_usd']
            stats['trade_count'] += 1
            stats['avg_size'] = stats['total_volume'] / stats['trade_count']

            if not stats['first_trade'] or trade['timestamp'] < stats['first_trade']:
                stats['first_trade'] = trade['timestamp']
            if not stats['last_trade'] or trade['timestamp'] > stats['last_trade']:
                stats['last_trade'] = trade['timestamp']

        # Identify whales
        whales = []
        for wallet, stats in wallet_stats.items():
            if stats['total_volume'] > 1000 or stats['avg_size'] > 50:
                whale_data = {
                    'address': wallet,
                    'total_volume': stats['total_volume'],
                    'trade_count': stats['trade_count'],
                    'avg_size': stats['avg_size'],
                    'activity_span_days': (stats['last_trade'] - stats['first_trade']) / 86400 if stats['first_trade'] and stats['last_trade'] else 0,
                    'first_trade': stats['first_trade'],
                    'last_trade': stats['last_trade'],
                    'whale_score': min(1.0, stats['total_volume'] / 10000)
                }
                whales.append(whale_data)
                self.whale_wallets.add(wallet)

        # Sort by whale score
        whales.sort(key=lambda x: x['whale_score'], reverse=True)

        self.logger.info(f"Found {len(whales)} whale wallets")
        for i, whale in enumerate(whales[:10]):  # Top 10
            self.logger.info(f"Whale #{i+1}: {whale['address'][:10]}... "
                          f"Volume: ${whale['total_volume']:.2f}, "
                          f"Trades: {whale['trade_count']}")

        return whales

    async def analyze_wallet_buy_patterns(self, trades):
        """Analyze per-wallet trading patterns and persist profiles and patterns.

        Heuristics (data is transfer-based, so we use trade count/size/time features):
        - accumulation_score: normalized trade_count with moderate avg size
        - distribution_score: low trade_count with very small holdings not tracked here (placeholder)
        - whale_score: reuse from volume-based whale detection
        - burstiness: stddev of inter-trade times / mean inter-trade times
        - time_of_day_json: histogram of hours UTC
        """
        if not trades:
            return {}

        # Aggregate by wallet
        wallets = {}
        by_wallet_times = defaultdict(list)
        by_wallet_values = defaultdict(list)

        for t in trades:
            w = t['from_address']
            ts = int(t['timestamp'])
            val = float(t.get('value_usd') or 0)
            rec = wallets.get(w) or {
                'address': w,
                'first_seen': ts,
                'last_seen': ts,
                'total_trades': 0,
                'total_volume': 0.0,
            }
            rec['total_trades'] += 1
            rec['total_volume'] += val
            rec['first_seen'] = min(rec['first_seen'], ts)
            rec['last_seen'] = max(rec['last_seen'], ts)
            wallets[w] = rec
            by_wallet_times[w].append(ts)
            by_wallet_values[w].append(val)

        # Compute pattern features and persist
        profiles = {}
        patterns = {}
        now = int(time.time())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        for addr, rec in wallets.items():
            total_trades = rec['total_trades']
            total_vol = rec['total_volume']
            avg_size = (total_vol / total_trades) if total_trades > 0 else 0.0
            span_sec = max(1, rec['last_seen'] - rec['first_seen'])
            trades_per_day = (total_trades / (span_sec / 86400.0)) if span_sec > 0 else total_trades

            # Inter-trade features
            times = sorted(by_wallet_times[addr])
            inter = [b - a for a, b in zip(times, times[1:])] if len(times) > 1 else []
            avg_intertrade = float(np.mean(inter)) if inter else float(span_sec)
            std_intertrade = float(np.std(inter)) if inter else 0.0
            burstiness = (std_intertrade / avg_intertrade) if avg_intertrade > 0 else 0.0

            # Time-of-day histogram (UTC hour)
            hours = [int(datetime.utcfromtimestamp(ts).hour) for ts in times] if times else []
            hour_counts = Counter(hours)
            time_of_day = {str(h): int(hour_counts.get(h, 0)) for h in range(24)}

            # Scores
            whale_score = min(1.0, total_vol / 10000.0)
            accumulation_score = min(1.0, (total_trades / 100.0) * (1.0 if avg_size <= 50 else 0.5))
            distribution_score = max(0.0, 1.0 - accumulation_score) * 0.5  # placeholder without sell labeling

            # Classify
            if whale_score > 0.6:
                wallet_type = 'whale'
            elif accumulation_score > 0.6:
                wallet_type = 'accumulator'
            else:
                wallet_type = 'regular'

            profiles[addr] = {
                'address': addr,
                'first_seen': rec['first_seen'],
                'last_seen': rec['last_seen'],
                'total_trades': total_trades,
                'total_volume': total_vol,
                'avg_trade_size': avg_size,
                'wallet_type': wallet_type,
                'profit_loss': 0.0,
                'success_rate': 0.0
            }

            patterns[addr] = {
                'accumulation_score': accumulation_score,
                'distribution_score': distribution_score,
                'whale_score': whale_score,
                'burstiness': burstiness,
                'avg_intertrade_sec': avg_intertrade,
                'trades_per_day': trades_per_day,
                'time_of_day': time_of_day
            }

            # Upsert DB: wallet_profiles
            cur.execute('''
                INSERT INTO wallet_profiles (address, first_seen, last_seen, total_trades, total_volume, avg_trade_size, wallet_type, profit_loss, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(address) DO UPDATE SET
                    first_seen=excluded.first_seen,
                    last_seen=excluded.last_seen,
                    total_trades=excluded.total_trades,
                    total_volume=excluded.total_volume,
                    avg_trade_size=excluded.avg_trade_size,
                    wallet_type=excluded.wallet_type
            ''', (
                addr, rec['first_seen'], rec['last_seen'], total_trades, total_vol, avg_size, wallet_type, 0.0, 0.0
            ))

            # Upsert DB: wallet_patterns
            cur.execute('''
                INSERT INTO wallet_patterns (address, accumulation_score, distribution_score, whale_score, burstiness, avg_intertrade_sec, trades_per_day, time_of_day_json, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(address) DO UPDATE SET
                    accumulation_score=excluded.accumulation_score,
                    distribution_score=excluded.distribution_score,
                    whale_score=excluded.whale_score,
                    burstiness=excluded.burstiness,
                    avg_intertrade_sec=excluded.avg_intertrade_sec,
                    trades_per_day=excluded.trades_per_day,
                    time_of_day_json=excluded.time_of_day_json,
                    last_updated=excluded.last_updated
            ''', (
                addr, accumulation_score, distribution_score, whale_score, burstiness, avg_intertrade, trades_per_day, json.dumps(time_of_day), now
            ))

        conn.commit()
        conn.close()

        # Export to JSON for easy consumption
        wallets_list = []
        for addr in profiles:
            entry = {**profiles[addr], **patterns[addr]}
            wallets_list.append(entry)
        wallets_list.sort(key=lambda x: (x['whale_score'], x['accumulation_score'], x['total_volume']), reverse=True)

        out = {
            'generated_at': datetime.now().isoformat(),
            'wallets': wallets_list,
            'total_wallets': len(wallets_list)
        }
        with open('maxx_wallets.json', 'w') as f:
            json.dump(out, f, indent=2)

        self.logger.info(f"Wallet patterns exported to maxx_wallets.json ({len(wallets_list)} wallets)")
        return out

    async def detect_coordinated_activity(self, trades):
        """Detect coordinated trading activity"""
        self.logger.info("\n" + "="*60)
        self.logger.info("DETECTING COORDINATED ACTIVITY")
        self.logger.info("="*60)

        # Time-based clustering
        time_clusters = defaultdict(list)

        # Group trades by 1-minute windows
        for trade in trades:
            time_window = trade['timestamp'] // 60
            time_clusters[time_window].append(trade)

        coordinated_events = []

        for time_window, cluster_trades in time_clusters.items():
            if len(cluster_trades) >= 5:  # Minimum 5 trades
                # Check for similar amounts
                amounts = [t['value_usd'] for t in cluster_trades]
                amount_std = np.std(amounts)
                amount_mean = np.mean(amounts)

                # Check for similar timing
                timestamps = [t['timestamp'] for t in cluster_trades]
                time_span = max(timestamps) - min(timestamps)

                # Coordination criteria
                mean_safe = amount_mean if amount_mean != 0 else 1.0
                if (amount_std / mean_safe < 0.2 and  # Similar amounts
                    time_span < 30 and  # Within 30 seconds
                    len(set(t['from_address'] for t in cluster_trades)) >= 3):  # Multiple wallets

                    event = {
                        'timestamp': min(timestamps),
                        'trade_count': len(cluster_trades),
                        'total_volume': sum(amounts),
                        'avg_amount': amount_mean,
                        'time_span_seconds': time_span,
                        'unique_wallets': len(set(t['from_address'] for t in cluster_trades)),
                        'coordination_score': min(1.0, len(cluster_trades) / 20)
                    }
                    coordinated_events.append(event)

                    self.logger.info(f"COORDINATED ACTIVITY: {event}")

        return coordinated_events

    async def generate_trading_signals(self, trades, pumps, whales, coordinated):
        """Generate actionable trading signals"""
        self.logger.info("\n" + "="*60)
        self.logger.info("GENERATING TRADING SIGNALS")
        self.logger.info("="*60)

        signals = []
        current_time = int(time.time())

        # Signal 1: Follow the whales
        for whale in whales[:5]:  # Top 5 whales
            last_trade_ts = whale.get('last_trade')
            if last_trade_ts and isinstance(last_trade_ts, (int, float)) and (current_time - int(last_trade_ts)) < 3600:
                signal = {
                    'type': 'WHALE_FOLLOW',
                    'confidence': whale['whale_score'],
                    'action': 'BUY',
                    'reason': f"Top whale {whale['address'][:10]}... active",
                    'expected_return': 0.05,  # 5%
                    'time_horizon': 'SHORT',
                    'gas_strategy': 'OPTIMAL'
                }
                signals.append(signal)

        # Signal 2: Pump continuation
        for pump in pumps:
            if (current_time - pump['timestamp']) < 300:  # Within 5 minutes
                signal = {
                    'type': 'PUMP_MOMENTUM',
                    'confidence': pump['pump_score'],
                    'action': 'BUY',
                    'reason': f"Pump detected - ${pump['volume_usd']:.2f} in {pump['window_minutes']}m",
                    'expected_return': 0.10,  # 10%
                    'time_horizon': 'VERY_SHORT',
                    'gas_strategy': 'FAST'
                }
                signals.append(signal)

        # Signal 3: Coordinated buy detection
        for coord in coordinated:
            if (current_time - coord['timestamp']) < 180:  # Within 3 minutes
                signal = {
                    'type': 'COORDINATED_BUY',
                    'confidence': coord['coordination_score'],
                    'action': 'BUY',
                    'reason': f"Coordinated buying - {coord['trade_count']} trades",
                    'expected_return': 0.08,  # 8%
                    'time_horizon': 'SHORT',
                    'gas_strategy': 'OPTIMAL'
                }
                signals.append(signal)

        # Sort signals by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)

        # Save signals
        await self._save_trading_signals(signals)

        self.logger.info(f"Generated {len(signals)} trading signals")
        for signal in signals[:5]:  # Top 5
            self.logger.info(f"SIGNAL: {signal}")

        return signals

    async def optimize_gas_strategy(self):
        """Optimize gas usage for maximum savings"""
        self.logger.info("\n" + "="*60)
        self.logger.info("OPTIMIZING GAS STRATEGY")
        self.logger.info("="*60)

        # Get current gas prices
        gas_prices = await self._get_gas_prices()

        if gas_prices:
            optimal_gas = {
                'standard': gas_prices['standard'],
                'fast': gas_prices['fast'],
                'optimal': max(0.1, gas_prices['standard'] * 0.8),  # 20% below standard
                'urgent': gas_prices['fast'] * 1.1
            }

            self.logger.info(f"Gas Prices (Gwei):")
            self.logger.info(f"  Standard: {gas_prices['standard']:.2f}")
            self.logger.info(f"  Fast: {gas_prices['fast']:.2f}")
            self.logger.info(f"  Optimal (our choice): {optimal_gas['optimal']:.2f}")
            self.logger.info(f"  Savings: {((gas_prices['standard'] - optimal_gas['optimal']) / gas_prices['standard'] * 100):.1f}%")

            return optimal_gas

        return {'optimal': 0.1}  # Fallback

    async def export_intelligence_report(self):
        """Export comprehensive intelligence report"""
        self.logger.info("\n" + "="*60)
        self.logger.info("EXPORTING INTELLIGENCE REPORT")
        self.logger.info("="*60)

        # Gather all data
        conn = sqlite3.connect(self.db_path)

        # Trade statistics
        trades_df = pd.read_sql_query('''
            SELECT
                COUNT(*) AS total_trades,
                COALESCE(SUM(value_usd), 0) AS total_volume,
                COALESCE(AVG(value_usd), 0) AS avg_trade_size,
                COUNT(DISTINCT from_address) AS unique_wallets
            FROM trades
        ''', conn)

        # Pump events
        pumps_df = pd.read_sql_query('SELECT * FROM pump_events ORDER BY start_time DESC', conn)

        # Top wallets
        wallets_df = pd.read_sql_query('''
            SELECT
                wp.address,
                wp.total_trades,
                wp.total_volume,
                wp.avg_trade_size,
                wp.wallet_type,
                coalesce(wpt.accumulation_score,0) as accumulation_score,
                coalesce(wpt.whale_score,0) as whale_score,
                coalesce(wpt.trades_per_day,0) as trades_per_day
            FROM wallet_profiles wp
            LEFT JOIN wallet_patterns wpt ON wpt.address = wp.address
            ORDER BY wp.total_volume DESC
            LIMIT 50
        ''', conn)

        # Recent signals
        signals_df = pd.read_sql_query('''
            SELECT * FROM trading_signals
            WHERE timestamp > strftime('%s', 'now', '-1 day')
            ORDER BY timestamp DESC
            LIMIT 20
        ''', conn)

        conn.close()

        # Build report
        # Safely extract summary numbers (guard against None)
        if not trades_df.empty:
            tt = int(trades_df['total_trades'].iloc[0] or 0)
            tv = float(trades_df['total_volume'].iloc[0] or 0)
            uw = int(trades_df['unique_wallets'].iloc[0] or 0)
            avg = float(trades_df['avg_trade_size'].iloc[0] or 0)
        else:
            tt, tv, uw, avg = 0, 0.0, 0, 0.0

        data_warnings = []
        if tt == 0:
            data_warnings.append("No trades found in the current database. Check API endpoint/key or increase scan window.")
        if self.last_scan_summary.get('trades_collected', 0) == 0:
            data_warnings.append("Historical scan returned 0 transfers. BaseScan may have rate-limited or the contract address/API is incorrect.")

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_trades': tt,
                'total_volume_usd': tv,
                'unique_wallets': uw,
                'avg_trade_size_usd': avg,
                'pump_events_detected': len(pumps_df),
                'whale_wallets_tracked': len(self.whale_wallets)
            },
            'pump_events': pumps_df.to_dict('records') if not pumps_df.empty else [],
            'top_wallets': wallets_df.to_dict('records') if not wallets_df.empty else [],
            'recent_signals': signals_df.to_dict('records') if not signals_df.empty else [],
            'patterns_detected': self.patterns,
            'scan_summary': self.last_scan_summary,
            'data_warnings': data_warnings,
            'gas_optimization': await self.optimize_gas_strategy(),
            'recommendations': self._generate_recommendations()
        }

        # Save to JSON
        with open(self.json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Intelligence report saved to {self.json_path}")
        self.logger.info(f"Total trades analyzed: {report['summary']['total_trades']}")
        self.logger.info(f"Total volume: ${report['summary']['total_volume_usd']:,.2f}")
        self.logger.info(f"Unique wallets: {report['summary']['unique_wallets']}")
        self.logger.info(f"Pump events: {report['summary']['pump_events_detected']}")

        return report

    def _generate_recommendations(self):
        """Generate trading recommendations"""
        recommendations = []

        # Based on analysis
        if len(self.patterns.get('pump', [])) > 0:
            recommendations.append({
                'type': 'ACTION',
                'priority': 'HIGH',
                'message': 'Pump patterns detected - Set buy orders at dips',
                'expected_roi': '15-30%'
            })

        if len(self.whale_wallets) > 0:
            recommendations.append({
                'type': 'STRATEGY',
                'priority': 'MEDIUM',
                'message': f'Monitor {len(self.whale_wallets)} whale wallets for entry signals',
                'expected_roi': '10-20%'
            })

        recommendations.append({
            'type': 'GAS',
            'priority': 'HIGH',
            'message': 'Use optimal gas pricing to save 20-30% on fees',
            'savings': '20-30%'
        })

        return recommendations

    # Helper methods
    async def _get_latest_block(self):
        """Get latest block number via BaseScan/Etherscan proxy."""
        url = self.config['basescan_api']
        params = {
            'module': 'proxy',
            'action': 'eth_blockNumber',
            'apikey': self.config['api_key']
        }
        if '/v2/' in url:
            params['chainid'] = self.config['base_chain_id']
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    result = data.get('result')
                    if isinstance(result, str):
                        return int(result, 16) if result.startswith('0x') else int(result)
        except Exception as e:
            self.logger.debug(f"Failed to get latest block: {e}")
        return 15000000

    async def _get_eth_price_at_timestamp(self, timestamp):
        """Get ETH price at specific timestamp"""
        # Simplified - would use price API
        return 3300  # Fixed price for demo

    async def _get_gas_prices(self):
        """Get current gas prices"""
        # Simplified - would use gas tracker API
        return {
            'standard': 0.5,
            'fast': 1.0
        }

    async def _save_trades_batch(self, trades):
        """Save batch of trades to database"""
        if not trades:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        has_token_cols = getattr(self, 'trades_has_token_cols', True)
        # Verify again in case of fresh DB
        try:
            cursor.execute("PRAGMA table_info(trades)")
            cols = [row[1] for row in cursor.fetchall()]
            has_token_cols = ('token_amount' in cols and 'token_decimals' in cols)
        except Exception:
            pass

        for trade in trades:
            if has_token_cols:
                cursor.execute('''
                    INSERT OR IGNORE INTO trades
                    (tx_hash, timestamp, block_number, from_address, to_address,
                     value_eth, value_usd, gas_used, gas_price_gwei, transaction_type,
                     token_amount, token_decimals)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.get('tx_hash'),
                    trade.get('timestamp'),
                    trade.get('block_number'),
                    trade.get('from_address'),
                    trade.get('to_address'),
                    trade.get('value_eth', 0.0),
                    trade.get('value_usd', 0.0),
                    trade.get('gas_used', 0),
                    trade.get('gas_price_gwei', 0.0),
                    trade.get('transaction_type', 'TRANSFER'),
                    float(trade.get('token_amount', 0.0)),
                    int(trade.get('token_decimals', self.maxx_decimals))
                ))
            else:
                cursor.execute('''
                    INSERT OR IGNORE INTO trades
                    (tx_hash, timestamp, block_number, from_address, to_address,
                     value_eth, value_usd, gas_used, gas_price_gwei, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.get('tx_hash'),
                    trade.get('timestamp'),
                    trade.get('block_number'),
                    trade.get('from_address'),
                    trade.get('to_address'),
                    trade.get('value_eth', 0.0),
                    trade.get('value_usd', 0.0),
                    trade.get('gas_used', 0),
                    trade.get('gas_price_gwei', 0.0),
                    trade.get('transaction_type', 'TRANSFER')
                ))

        conn.commit()
        conn.close()

    async def _save_pump_events(self, pumps):
        """Save pump events to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for pump in pumps:
            cursor.execute('''
                INSERT INTO pump_events
                (start_time, end_time, start_price, end_price, price_change_pct,
                 volume_change_pct, duration_minutes, participants_count, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pump['timestamp'],
                pump['timestamp'] + pump['window_minutes'] * 60,
                0,  # Would calculate actual prices
                0,
                pump['pump_score'] * 100,
                0,
                pump['window_minutes'],
                0,
                pump['pump_score']
            ))

        conn.commit()
        conn.close()

    async def _save_trading_signals(self, signals):
        """Save trading signals to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for signal in signals:
            cursor.execute('''
                INSERT INTO trading_signals
                (timestamp, signal_type, confidence, expected_return,
                 time_horizon, trigger_event, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(time.time()),
                signal['type'],
                signal['confidence'],
                signal['expected_return'],
                signal['time_horizon'],
                signal['reason'],
                json.dumps(signal)
            ))

        conn.commit()
        conn.close()

    async def run_continuous_monitoring(self):
        """Run continuous monitoring for new trades"""
        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING CONTINUOUS MONITORING")
        self.logger.info("="*80)

        last_checked = int(time.time())

        while True:
            try:
                current_time = int(time.time())

                # Check for new trades
                new_trades = await self._fetch_trades_in_range(
                    last_checked - 300,  # Check 5 minutes back
                    current_time
                )

                if new_trades:
                    self.logger.info(f"Found {len(new_trades)} new trades")

                    # Analyze for immediate signals
                    urgent_signals = []

                    for trade in new_trades:
                        if trade['value_usd'] > self.config['whale_threshold']:
                            urgent_signals.append({
                                'type': 'LARGE_TRADE',
                                'action': 'MONITOR',
                                'details': trade,
                                'urgency': 'HIGH'
                            })

                    if urgent_signals:
                        self.logger.warning(f"URGENT: {len(urgent_signals)} significant trades detected!")
                        for signal in urgent_signals:
                            self.logger.warning(f"  - ${signal['details']['value_usd']:.2f} "
                                             f"from {signal['details']['from_address'][:10]}...")

                last_checked = current_time

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)

async def main():
    """Main execution"""
    analyzer = MAXXIntelligenceAnalyzer()

    print("="*80)
    print("MAXX TOKEN INTELLIGENCE ANALYZER V2.0")
    print("="*80)
    print("Starting comprehensive MAXX analysis...")
    print()

    # Step 1: Collect historical data
    trades = await analyzer.collect_historical_trades()

    # Step 2: Analyze patterns
    pumps = await analyzer.analyze_pump_patterns(trades)
    whales = await analyzer.identify_whale_activity(trades)
    coordinated = await analyzer.detect_coordinated_activity(trades)

    # Step 3: Generate signals
    signals = await analyzer.generate_trading_signals(trades, pumps, whales, coordinated)

    # Step 4: Optimize gas
    gas_strategy = await analyzer.optimize_gas_strategy()

    # Step 5: Export report
    report = await analyzer.export_intelligence_report()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"Check {analyzer.json_path} for full intelligence report")
    print("\nTop Recommendations:")
    for rec in report['recommendations'][:3]:
        print(f"- {rec['message']}")

    # Optional: Start continuous monitoring
    print("\nStarting continuous monitoring (Ctrl+C to stop)...")
    await analyzer.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
