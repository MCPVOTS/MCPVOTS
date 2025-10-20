"""
Transaction Analyzer for MAXX Token
Analyzes historical transactions, identifies cluster/swarm bots, and monitors money flow
to predict high-volume periods and price changes
"""
import asyncio
import aiohttp
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from collections import defaultdict, Counter
from contextlib import contextmanager
import json
from config import Config
from base_utils import BaseBlockchainUtils
from db_vector_storage import DatabaseConnection


class TransactionAnalyzer:
    """
    Analyzes MAXX token transactions to identify cluster/swarm bots and money flow patterns
    """

    def __init__(self, db_path: str = "data/pumpfun_ecosystem.db"):
        self.db = DatabaseConnection(db_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_utils = BaseBlockchainUtils()
        self.contract_address = Config.MAXX_CONTRACT_ADDRESS
        self._init_transaction_db()

    def _init_transaction_db(self):
        """Initialize database tables for transaction analysis"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()

            # Create table for tracked transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyzed_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_hash TEXT UNIQUE,
                    block_number INTEGER,
                    timestamp REAL,
                    from_address TEXT,
                    to_address TEXT,
                    value TEXT,  -- in wei
                    gas_used INTEGER,
                    gas_price INTEGER,
                    is_swarm_transaction INTEGER DEFAULT 0,
                    is_cluster_transaction INTEGER DEFAULT 0,
                    swarm_id TEXT,
                    cluster_id TEXT,
                    calculated_profit REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create table for identified swarms/bots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS identified_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE,
                    bot_type TEXT,  -- 'swarm', 'cluster', 'whale', 'sniper'
                    first_seen REAL,
                    last_seen REAL,
                    transaction_count INTEGER DEFAULT 0,
                    total_volume TEXT,
                    profit_margin REAL,
                    is_active INTEGER DEFAULT 1,
                    pattern_signature TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create table for swarm patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS swarm_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE,
                    pattern_type TEXT,  -- 'bundle', 'coordinated', 'drip_feed'
                    participants TEXT,  -- JSON array of addresses
                    total_volume TEXT,
                    start_time REAL,
                    end_time REAL,
                    peak_activity REAL,
                    profit_potential REAL,
                    detected_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create table for money flow tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS money_flow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_address TEXT,
                    to_address TEXT,
                    token_address TEXT,
                    value TEXT,
                    timestamp REAL,
                    flow_type TEXT,  -- 'inflow', 'outflow', 'internal'
                    source_type TEXT,  -- 'whale', 'bot', 'retail'
                    destination_type TEXT,  -- 'whale', 'bot', 'retail'
                    transaction_hash TEXT,
                    calculated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            conn.commit()
            conn.close()
            self.logger.info("Transaction analysis database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing transaction database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            conn.close()

    async def analyze_historical_transactions(self, from_block: Optional[int] = None, to_block: Optional[int] = None) -> List[Dict]:
        """
        Analyze historical transactions for the MAXX token to identify patterns
        """
        self.logger.info("Starting historical transaction analysis for MAXX token...")

        # Fetch historical transactions from Base blockchain
        transactions = await self.base_utils.get_token_transfers(
            self.contract_address,
            from_block,
            to_block
        )

        if not transactions:
            self.logger.warning("No transactions found for analysis")
            return []

        # Process each transaction to identify patterns
        analyzed_data = []

        for tx in transactions:
            try:
                # Convert transaction data to our format
                processed_tx = {
                    'transaction_hash': tx.get('transactionHash', ''),
                    'from_address': tx.get('from', '').lower(),
                    'to_address': tx.get('to', '').lower(),
                    'value': tx.get('value', '0'),
                    'timestamp': tx.get('timestamp', 0),
                    'block_number': tx.get('blockNumber', 0)
                }

                # Analyze for cluster/swarm patterns
                pattern_analysis = await self._analyze_transaction_patterns(processed_tx)

                # Update with pattern analysis
                processed_tx.update(pattern_analysis)

                analyzed_data.append(processed_tx)

                # Store in database
                await self._store_transaction_data(processed_tx)

            except Exception as e:
                self.logger.error(f"Error processing transaction {tx.get('transactionHash', 'N/A')}: {e}")
                continue

        self.logger.info(f"Analyzed {len(analyzed_data)} transactions for MAXX token")
        return analyzed_data

    async def _analyze_transaction_patterns(self, transaction: Dict) -> Dict:
        """
        Analyze transaction patterns to identify swarm/cluster behavior
        """
        analysis_result = {
            'is_swarm_transaction': 0,
            'is_cluster_transaction': 0,
            'swarm_id': None,
            'cluster_id': None,
            'pattern_confidence': 0.0
        }

        # Check for swarm patterns (multiple addresses coordinating on same block/timestamp)
        swarm_check = await self._check_swarm_pattern(transaction)
        if swarm_check['is_swarm']:
            analysis_result['is_swarm_transaction'] = 1
            analysis_result['swarm_id'] = swarm_check['swarm_id']
            analysis_result['pattern_confidence'] = swarm_check['confidence']

        # Check for cluster patterns (related addresses making coordinated moves)
        cluster_check = await self._check_cluster_pattern(transaction)
        if cluster_check['is_cluster']:
            analysis_result['is_cluster_transaction'] = 1
            analysis_result['cluster_id'] = cluster_check['cluster_id']
            analysis_result['pattern_confidence'] = max(
                analysis_result['pattern_confidence'],
                cluster_check['confidence']
            )

        return analysis_result

    async def _check_swarm_pattern(self, transaction: Dict) -> Dict:
        """
        Check if transaction is part of a swarm pattern
        """
        # Look for multiple transactions from different addresses to same destination
        # within a short time window (same block or few blocks)

        from_address = transaction['from_address']
        to_address = transaction['to_address']
        timestamp = transaction['timestamp']
        block_number = transaction['block_number']

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Query for other transactions in the same block/short time window
            cursor.execute("""
                SELECT DISTINCT from_address, to_address, value, timestamp, block_number
                FROM analyzed_transactions
                WHERE (block_number = ? OR block_number = ? OR block_number = ?)
                AND from_address != ?
                AND to_address = ?
                AND is_swarm_transaction = 0
            """, (block_number, block_number-1, block_number+1, from_address, to_address))

            similar_transactions = cursor.fetchall()

        # Check if we have enough similar transactions to constitute a swarm
        if len(similar_transactions) >= 3:  # Adjust threshold as needed
            # Calculate time clustering
            timestamps = [tx['timestamp'] for tx in similar_transactions]
            timestamps.append(timestamp)

            # Check if transactions are within 10 seconds of each other
            time_diffs = [abs(t - timestamp) for t in timestamps]
            if max(time_diffs) <= 10:  # Within 10 seconds
                swarm_id = f"swarm_{to_address[:10]}_{int(timestamp)}"
                return {
                    'is_swarm': True,
                    'swarm_id': swarm_id,
                    'confidence': min(0.95, len(similar_transactions) * 0.1)  # Higher confidence with more participants
                }

        # Check for coordinated buying (multiple addresses buying within short time)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Query for transactions to same token address within time window
            time_window_start = timestamp - 30  # 30 seconds before
            time_window_end = timestamp + 30   # 30 seconds after

            cursor.execute("""
                SELECT DISTINCT from_address, to_address, value, timestamp
                FROM analyzed_transactions
                WHERE timestamp BETWEEN ? AND ?
                AND from_address != ?
                AND to_address = ?
            """, (time_window_start, time_window_end, from_address, self.contract_address))

            concurrent_transactions = cursor.fetchall()

        if len(concurrent_transactions) >= 5:  # Threshold for coordinated activity
            swarm_id = f"coord_buy_{int(timestamp)}"
            return {
                'is_swarm': True,
                'swarm_id': swarm_id,
                'confidence': min(0.90, len(concurrent_transactions) * 0.05)
            }

        return {'is_swarm': False, 'swarm_id': None, 'confidence': 0.0}

    async def _check_cluster_pattern(self, transaction: Dict) -> Dict:
        """
        Check if transaction is part of a cluster pattern
        """
        from_address = transaction['from_address']
        to_address = transaction['to_address']

        # Check if from_address has been identified as part of a cluster/bot before
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bot_type, pattern_signature
                FROM identified_bots
                WHERE address = ? AND is_active = 1
            """, (from_address,))
            existing_bot = cursor.fetchone()

        if existing_bot:
            return {
                'is_cluster': True,
                'cluster_id': existing_bot['pattern_signature'],
                'confidence': 0.85
            }

        # Check for round-trip patterns (arbitrage or profit-taking)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if the same address has had recent significant transactions
            recent_time = transaction['timestamp'] - 3600  # 1 hour ago
            cursor.execute("""
                SELECT COUNT(*) as transaction_count, SUM(CAST(value AS REAL)) as total_volume
                FROM analyzed_transactions
                WHERE from_address = ? AND timestamp > ?
            """, (from_address, recent_time))

            addr_stats = cursor.fetchone()

        if addr_stats and addr_stats['transaction_count'] > 5:
            cluster_id = f"active_{from_address[:10]}"
            confidence = min(0.8, addr_stats['transaction_count'] * 0.05)
            return {
                'is_cluster': True,
                'cluster_id': cluster_id,
                'confidence': confidence
            }

        return {'is_cluster': False, 'cluster_id': None, 'confidence': 0.0}

    async def _store_transaction_data(self, transaction_data: Dict):
        """
        Store analyzed transaction data in the database
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO analyzed_transactions
                    (transaction_hash, block_number, timestamp, from_address, to_address, value,
                     is_swarm_transaction, is_cluster_transaction, swarm_id, cluster_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_data['transaction_hash'],
                    transaction_data.get('block_number', 0),
                    transaction_data['timestamp'],
                    transaction_data['from_address'],
                    transaction_data['to_address'],
                    transaction_data['value'],
                    transaction_data['is_swarm_transaction'],
                    transaction_data['is_cluster_transaction'],
                    transaction_data['swarm_id'],
                    transaction_data['cluster_id']
                ))

                conn.commit()

                # Update bot identification if pattern detected
                if transaction_data['is_swarm_transaction'] or transaction_data['is_cluster_transaction']:
                    await self._identify_and_track_bot(transaction_data)

            except sqlite3.IntegrityError:
                # Transaction hash already exists, update instead
                cursor.execute("""
                    UPDATE analyzed_transactions
                    SET block_number = ?, timestamp = ?, from_address = ?, to_address = ?,
                        value = ?, is_swarm_transaction = ?, is_cluster_transaction = ?,
                        swarm_id = ?, cluster_id = ?
                    WHERE transaction_hash = ?
                """, (
                    transaction_data.get('block_number', 0),
                    transaction_data['timestamp'],
                    transaction_data['from_address'],
                    transaction_data['to_address'],
                    transaction_data['value'],
                    transaction_data['is_swarm_transaction'],
                    transaction_data['is_cluster_transaction'],
                    transaction_data['swarm_id'],
                    transaction_data['cluster_id'],
                    transaction_data['transaction_hash']
                ))
                conn.commit()

    async def _identify_and_track_bot(self, transaction_data: Dict):
        """
        Identify and track bot/swarm addresses
        """
        address = transaction_data['from_address']
        bot_type = 'swarm' if transaction_data['is_swarm_transaction'] else 'cluster'

        # Get existing bot record
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, transaction_count, total_volume
                FROM identified_bots
                WHERE address = ?
            """, (address,))
            existing_bot = cursor.fetchone()

        current_time = transaction_data['timestamp']
        value = int(transaction_data['value']) if transaction_data['value'] else 0

        if existing_bot:
            # Update existing bot record
            new_count = existing_bot['transaction_count'] + 1
            new_volume = int(existing_bot['total_volume']) + value if existing_bot['total_volume'] else value

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE identified_bots
                    SET last_seen = ?, transaction_count = ?, total_volume = ?
                    WHERE address = ?
                """, (current_time, new_count, str(new_volume), address))
                conn.commit()
        else:
            # Create new bot record
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO identified_bots
                    (address, bot_type, first_seen, last_seen, transaction_count, total_volume, pattern_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    address, bot_type, current_time, current_time, 1, str(value),
                    transaction_data.get('swarm_id') or transaction_data.get('cluster_id')
                ))
                conn.commit()

    async def identify_swarms_and_clusters(self) -> List[Dict]:
        """
        Identify all swarms and clusters in the transaction history
        """
        self.logger.info("Identifying swarms and clusters...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Find addresses that frequently transact together or in patterns
            cursor.execute("""
                SELECT
                    from_address,
                    COUNT(*) as transaction_count,
                    SUM(CAST(value AS REAL)) as total_volume,
                    MIN(timestamp) as first_transaction,
                    MAX(timestamp) as last_transaction
                FROM analyzed_transactions
                WHERE is_swarm_transaction = 1 OR is_cluster_transaction = 1
                GROUP BY from_address
                ORDER BY transaction_count DESC, total_volume DESC
                LIMIT 100
            """)

            swarm_addresses = cursor.fetchall()

        swarms_info = []
        for addr in swarm_addresses:
            # Get more detailed information about the address behavior
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Find recent swarm patterns associated with this address
                cursor.execute("""
                    SELECT DISTINCT swarm_id, cluster_id, COUNT(*) as pattern_count
                    FROM analyzed_transactions
                    WHERE from_address = ? AND (is_swarm_transaction = 1 OR is_cluster_transaction = 1)
                    GROUP BY swarm_id, cluster_id
                """, (addr['from_address'],))

                patterns = cursor.fetchall()

            swarm_info = {
                'address': addr['from_address'],
                'transaction_count': addr['transaction_count'],
                'total_volume': addr['total_volume'],
                'first_seen': addr['first_transaction'],
                'last_seen': addr['last_transaction'],
                'associated_patterns': [dict(pattern) for pattern in patterns],
                'activity_score': self._calculate_activity_score(addr)
            }

            swarms_info.append(swarm_info)

        self.logger.info(f"Identified {len(swarms_info)} swarm/cluster addresses")
        return swarms_info

    def _calculate_activity_score(self, addr_info: sqlite3.Row) -> float:
        """
        Calculate an activity score based on transaction frequency and volume
        """
        # Score based on transaction count and volume
        volume_score = min(1.0, (int(addr_info['total_volume']) or 0) / 10**20)  # Normalize large numbers
        count_score = min(1.0, addr_info['transaction_count'] / 100)  # Normalize count

        # Time-based decay (more recent activity scores higher)
        time_diff = time.time() - (addr_info['last_transaction'] or 0)
        recency_score = max(0.1, 1.0 - (time_diff / (7 * 24 * 3600)))  # 1 week decay

        return (volume_score * 0.4 + count_score * 0.4 + recency_score * 0.2)

    async def monitor_money_flow(self) -> Dict[str, Any]:
        """
        Monitor money flow patterns to identify large inflows/outflows
        """
        self.logger.info("Monitoring money flow patterns...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Analyze recent transactions for money flow patterns
            one_hour_ago = time.time() - 3600
            cursor.execute("""
                SELECT
                    from_address,
                    to_address,
                    SUM(CAST(value AS REAL)) as total_flow,
                    COUNT(*) as transaction_count
                FROM analyzed_transactions
                WHERE timestamp > ?
                GROUP BY from_address, to_address
                ORDER BY total_flow DESC
                LIMIT 50
            """, (one_hour_ago,))

            flow_data = cursor.fetchall()

        # Categorize addresses by type (whale, bot, retail)
        categorized_flows = []
        for flow in flow_data:
            flow_info = dict(flow)
            flow_info['from_address_type'] = await self._categorize_address(flow['from_address'])
            flow_info['to_address_type'] = await self._categorize_address(flow['to_address'])

            # Calculate flow direction and significance
            flow_info['is_large_flow'] = flow_info['total_flow'] > 10**18  # More than 1 full token
            flow_info['flow_significance'] = self._calculate_flow_significance(flow_info)

            categorized_flows.append(flow_info)

        # Store money flow data
        await self._store_money_flow_data(categorized_flows)

        # Identify potential high-volume periods
        volume_prediction = await self._predict_volume_periods(categorized_flows)

        result = {
            'money_flow_summary': categorized_flows[:10],  # Top 10 flows
            'large_flow_alerts': [f for f in categorized_flows if f['is_large_flow']],
            'volume_prediction': volume_prediction,
            'timestamp': time.time()
        }

        self.logger.info(f"Money flow analysis complete. Found {len(categorized_flows)} flow patterns")
        return result

    async def _categorize_address(self, address: str) -> str:
        """
        Categorize an address as whale, bot, or retail based on transaction history
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as transaction_count,
                    SUM(CAST(value AS REAL)) as total_volume,
                    COUNT(DISTINCT to_address) as unique_recipients
                FROM analyzed_transactions
                WHERE from_address = ?
            """, (address,))

            stats = cursor.fetchone()

        if not stats or stats['transaction_count'] == 0:
            return 'retail'

        # Define thresholds for different categories
        is_high_volume = stats['total_volume'] > 10**19  # 10 tokens or more
        is_frequent_trader = stats['transaction_count'] > 10
        is_diverse_trader = stats['unique_recipients'] > 5

        if is_high_volume and is_frequent_trader:
            return 'whale'
        elif is_frequent_trader and is_diverse_trader:
            # Check if it's identified as a bot
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT bot_type FROM identified_bots WHERE address = ?", (address,))
                bot_info = cursor.fetchone()

            return bot_info['bot_type'] if bot_info else 'bot'
        else:
            return 'retail'

    def _calculate_flow_significance(self, flow_info: Dict) -> float:
        """
        Calculate the significance of a money flow
        """
        # Higher significance for larger flows and bot-to-bot or whale-to-bot transactions
        base_significance = min(1.0, flow_info['total_flow'] / 10**20)

        # Boost significance if it's a bot or whale transaction
        multipliers = {
            'whale': 2.0,
            'bot': 1.5,
            'swarm': 2.5,
            'cluster': 2.0,
            'retail': 1.0
        }

        from_mult = multipliers.get(flow_info['from_address_type'], 1.0)
        to_mult = multipliers.get(flow_info['to_address_type'], 1.0)

        return base_significance * from_mult * to_mult

    async def _store_money_flow_data(self, flow_data: List[Dict]):
        """
        Store money flow data in the database
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for flow in flow_data:
                cursor.execute("""
                    INSERT INTO money_flow
                    (from_address, to_address, token_address, value, timestamp,
                     flow_type, source_type, destination_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    flow['from_address'],
                    flow['to_address'],
                    self.contract_address,
                    str(flow['total_flow']),
                    time.time(),  # Current timestamp
                    'internal',  # Will determine actual type based on addresses
                    flow['from_address_type'],
                    flow['to_address_type']
                ))

            conn.commit()

    async def _predict_volume_periods(self, flow_data: List[Dict]) -> Dict[str, Any]:
        """
        Predict potential high-volume periods based on flow patterns
        """
        # Analyze the flow data to predict high-volume periods

        # Count large flows by source type
        large_flow_by_type = defaultdict(int)
        for flow in flow_data:
            if flow['is_large_flow']:
                key = f"{flow['from_address_type']}_to_{flow['to_address_type']}"
                large_flow_by_type[key] += 1

        # Identify the most active patterns
        active_patterns = dict(large_flow_by_type)

        # Calculate volume momentum
        recent_time = time.time() - 1800  # 30 minutes ago

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as recent_transactions,
                       SUM(CAST(value AS REAL)) as recent_volume
                FROM analyzed_transactions
                WHERE timestamp > ?
            """, (recent_time,))

            recent_stats = cursor.fetchone()

        # Calculate volume prediction score
        if recent_stats:
            volume_trend = recent_stats['recent_transactions'] > 10  # More than 10 transactions in 30 min
            momentum_score = min(1.0, recent_stats['recent_volume'] / 10**20)
        else:
            volume_trend = False
            momentum_score = 0.0

        prediction = {
            'is_high_volume_coming': volume_trend,
            'momentum_score': momentum_score,
            'active_patterns': active_patterns,
            'expected_duration_minutes': 30 if volume_trend else 5,
            'confidence_level': momentum_score,
            'trigger_alerts': volume_trend
        }

        return prediction

    async def get_alerts_for_trading(self) -> List[Dict[str, Any]]:
        """
        Get trading alerts based on transaction analysis
        """
        alerts = []

        # Get current swarm/cluster activity
        swarms = await self.identify_swarms_and_clusters()
        money_flow_data = await self.monitor_money_flow()

        # Generate alerts based on swarm activity
        for swarm in swarms[:5]:  # Top 5 swarms
            if swarm['activity_score'] > 0.7:
                alerts.append({
                    'type': 'swarm_activity',
                    'address': swarm['address'],
                    'activity_score': swarm['activity_score'],
                    'transaction_count': swarm['transaction_count'],
                    'volume': swarm['total_volume'],
                    'timestamp': time.time(),
                    'severity': 'high' if swarm['activity_score'] > 0.8 else 'medium'
                })

        # Generate alerts based on money flow
        if money_flow_data['volume_prediction']['trigger_alerts']:
            alerts.append({
                'type': 'volume_spike_prediction',
                'prediction': money_flow_data['volume_prediction'],
                'timestamp': time.time(),
                'severity': 'high'
            })

        # Check for large individual transactions
        with self.get_connection() as conn:
            cursor = conn.cursor()
            recent_time = time.time() - 300  # 5 minutes ago
            cursor.execute("""
                SELECT from_address, to_address, value, timestamp
                FROM analyzed_transactions
                WHERE timestamp > ? AND CAST(value AS REAL) > ?
                ORDER BY CAST(value AS REAL) DESC
                LIMIT 5
            """, (recent_time, 10**18))  # More than 1 token

            large_transactions = cursor.fetchall()

        for tx in large_transactions:
            alerts.append({
                'type': 'large_transaction',
                'from_address': tx['from_address'],
                'to_address': tx['to_address'],
                'value': tx['value'],
                'timestamp': tx['timestamp'],
                'severity': 'high'
            })

        return alerts


# Global instance for use across the system
transaction_analyzer = TransactionAnalyzer()


# Real transaction analysis utilities - no demo functions
# Use TransactionAnalyzer class directly for real trading analysis
# Available methods:
# - analyze_historical_transactions()
# - identify_swarms_and_clusters()
# - monitor_money_flow()
# - get_alerts_for_trading()
