"""
Enhanced Ethermax Analyzer for MAXX Ecosystem
Advanced tools for analyzing token history, top wallets, and swarm patterns
"""
import asyncio
import time
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from core.config import get_app_config
from core.logging import get_logger, log_performance
from core.database import get_database_manager
from core.network import get_network_manager
from core.analytics import get_analytics_manager
import json
from dataclasses import asdict


@dataclass
class TokenHolder:
    """Token holder information"""
    address: str
    balance: Decimal
    percentage: float
    first_seen: float
    last_activity: float
    transaction_count: int
    is_contract: bool = False


@dataclass
class SwarmPattern:
    """Swarm trading pattern"""
    swarm_id: str
    addresses: List[str]
    start_time: float
    end_time: float
    transaction_count: int
    total_volume: Decimal
    avg_transaction_size: Decimal
    coordination_score: float


@dataclass
class WalletAnalysis:
    """Wallet analysis results"""
    address: str
    maxx_balance: Decimal
    eth_balance: Decimal
    total_value_usd: Decimal
    profit_loss: Decimal
    hold_time: float
    transaction_count: int
    is_whale: bool = False
    is_bot: bool = False
    risk_score: float = 0.0


class EthermaxAnalyzer:
    """
    Advanced analyzer for MAXX token data including top wallets,
    transaction history, and swarm pattern detection
    """

    def __init__(self, contract_address: Optional[str] = None):
        self.config = get_app_config()
        self.logger = get_logger(self.__class__.__name__)
        self.db_manager = None
        self.network_manager = None
        self.analytics_manager = None

        # Contract configuration
        self.contract_address = contract_address or os.getenv('MAXX_CONTRACT_ADDRESS', '')
        self.token_decimals = 18  # Standard ERC20

        # Analysis parameters
        self.swarm_threshold = 5  # Minimum transactions for swarm detection
        self.swarm_time_window = 3600  # 1 hour window for swarm detection
        self.whale_threshold = Decimal('1000000')  # 1M tokens for whale detection

        # Cache
        self._holder_cache: Dict[str, TokenHolder] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes

    async def initialize(self):
        """Initialize the analyzer"""
        self.db_manager = await get_database_manager()
        self.network_manager = await get_network_manager()
        self.analytics_manager = await get_analytics_manager()

        # Create necessary database tables if they don't exist
        await self._ensure_database_schema()

        self.logger.info("Ethermax analyzer initialized")

    async def _ensure_database_schema(self):
        """Ensure database schema exists"""
        try:
            # Create token holders table
            await self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS token_holders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE NOT NULL,
                    balance TEXT NOT NULL,
                    percentage REAL,
                    first_seen REAL,
                    last_activity REAL,
                    transaction_count INTEGER DEFAULT 0,
                    is_contract INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create swarm patterns table
            await self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS swarm_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    swarm_id TEXT UNIQUE NOT NULL,
                    addresses TEXT NOT NULL,
                    start_time REAL,
                    end_time REAL,
                    transaction_count INTEGER,
                    total_volume TEXT,
                    avg_transaction_size TEXT,
                    coordination_score REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create wallet analyses table
            await self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS wallet_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE NOT NULL,
                    maxx_balance TEXT NOT NULL,
                    eth_balance TEXT,
                    total_value_usd TEXT,
                    profit_loss TEXT,
                    hold_time REAL,
                    transaction_count INTEGER,
                    is_whale INTEGER DEFAULT 0,
                    is_bot INTEGER DEFAULT 0,
                    risk_score REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)

        except Exception as e:
            self.logger.error(f"Failed to create database schema: {e}")

    @log_performance("analyzer.get_top_holders")
    async def get_top_token_holders(self, limit: int = 100) -> List[TokenHolder]:
        """
        Get the top token holders for the MAXX token with real data
        """
        self.logger.info(f"Fetching top {limit} MAXX token holders")

        try:
            # Check cache first
            if time.time() - self._cache_timestamp < self._cache_ttl and self._holder_cache:
                self.logger.debug("Using cached holder data")
                return sorted(self._holder_cache.values(),
                             key=lambda h: h.balance, reverse=True)[:limit]

            # Try to get data from BaseScan API
            holders = await self._fetch_holders_from_basescan(limit)

            if not holders:
                # Fallback to analyzing transfers
                holders = await self._analyze_holders_from_transfers(limit)

            # Update cache
            self._holder_cache = {h.address: h for h in holders}
            self._cache_timestamp = time.time()

            # Store in database
            await self._store_holders(holders)

            self.logger.info(f"Retrieved {len(holders)} token holders")
            return holders[:limit]

        except Exception as e:
            self.logger.error(f"Error fetching top token holders: {e}")
            return []

    async def _fetch_holders_from_basescan(self, limit: int) -> List[TokenHolder]:
        """Fetch holder data from BaseScan API"""
        api_key = os.getenv('BASESCAN_API_KEY')
        if not api_key or not self.contract_address:
            self.logger.warning("BaseScan API key or contract address not configured")
            return []

        try:
            http_client = self.network_manager.get_http_client("https://api.basescan.org")

            params = {
                'module': 'token',
                'action': 'tokenholderlist',
                'contractaddress': self.contract_address,
                'page': 1,
                'offset': limit,
                'apikey': api_key
            }

            response = await http_client.get('/api', params=params)

            if response.success and response.data.get('status') == '1':
                holders = []
                total_supply = await self._get_total_supply()

                for holder_data in response.data.get('result', []):
                    balance = int(holder_data.get('tokenBalance', 0))
                    if balance > 0:
                        holder = TokenHolder(
                            address=holder_data.get('address', ''),
                            balance=Decimal(balance) / (10 ** self.token_decimals),
                            percentage=(balance / total_supply * 100) if total_supply > 0 else 0,
                            first_seen=0,  # Would need additional API calls
                            last_activity=time.time(),
                            transaction_count=0,  # Would need additional API calls
                            is_contract=holder_data.get('address', '').startswith('0x') and
                                         len(holder_data.get('address', '')) == 42
                        )
                        holders.append(holder)

                return holders

        except Exception as e:
            self.logger.error(f"BaseScan API error: {e}")

        return []

    async def _analyze_holders_from_transfers(self, limit: int) -> List[TokenHolder]:
        """Analyze holders from transfer data"""
        try:
            # Get recent transfers from database
            transfers = await self.db_manager.execute_query("""
                SELECT from_address, to_address, value, timestamp
                FROM analyzed_transactions
                WHERE to_address IS NOT NULL AND from_address IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 10000
            """)

            holder_balances = {}
            holder_activity = {}

            for transfer in transfers:
                from_addr = transfer['from_address'].lower()
                to_addr = transfer['to_address'].lower()
                value = Decimal(transfer['value']) / (10 ** self.token_decimals)
                timestamp = transfer['timestamp']

                # Update balances
                holder_balances[to_addr] = holder_balances.get(to_addr, Decimal('0')) + value
                holder_balances[from_addr] = holder_balances.get(from_addr, Decimal('0')) - value

                # Update activity
                for addr in [from_addr, to_addr]:
                    if addr not in holder_activity:
                        holder_activity[addr] = {'first': timestamp, 'last': timestamp, 'count': 0}
                    holder_activity[addr]['last'] = max(holder_activity[addr]['last'], timestamp)
                    holder_activity[addr]['count'] += 1

            # Convert to TokenHolder objects
            holders = []
            total_supply = await self._get_total_supply()

            for address, balance in holder_balances.items():
                if balance > 0:
                    activity = holder_activity.get(address, {})
                    holder = TokenHolder(
                        address=address,
                        balance=balance,
                        percentage=float(balance) / float(total_supply) * 100 if total_supply > 0 else 0,
                        first_seen=activity.get('first', 0),
                        last_activity=activity.get('last', 0),
                        transaction_count=activity.get('count', 0),
                        is_contract=address.startswith('0x') and len(address) == 42
                    )
                    holders.append(holder)

            # Sort by balance and limit
            holders.sort(key=lambda h: h.balance, reverse=True)
            return holders[:limit]

        except Exception as e:
            self.logger.error(f"Error analyzing holders from transfers: {e}")
            return []

    async def _get_total_supply(self) -> int:
        """Get total token supply"""
        try:
            # This would typically come from the token contract
            # For now, return a reasonable default
            return 1000000000 * (10 ** self.token_decimals)  # 1B tokens
        except Exception:
            return 0

    async def _store_holders(self, holders: List[TokenHolder]):
        """Store holder data in database"""
        try:
            for holder in holders:
                await self.db_manager.execute_query("""
                    INSERT OR REPLACE INTO token_holders
                    (address, balance, percentage, first_seen, last_activity,
                     transaction_count, is_contract, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    holder.address, str(holder.balance), holder.percentage,
                    holder.first_seen, holder.last_activity,
                    holder.transaction_count, int(holder.is_contract), time.time()
                ))

        except Exception as e:
            self.logger.error(f"Failed to store holders: {e}")

    @log_performance("analyzer.detect_swarms")
    async def detect_swarms(self, time_window: int = 3600) -> List[SwarmPattern]:
        """
        Detect coordinated trading patterns (swarms) in recent transactions
        """
        self.logger.info(f"Detecting swarm patterns in {time_window}s time window")

        try:
            # Get recent transactions
            cutoff_time = time.time() - time_window
            transfers = await self.db_manager.execute_query("""
                SELECT from_address, to_address, value, timestamp, block_number
                FROM analyzed_transactions
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            """, (cutoff_time,))

            if not transfers:
                return []

            # Analyze for coordinated patterns
            swarm_patterns = await self._analyze_swarm_patterns(transfers)

            # Store detected patterns
            await self._store_swarm_patterns(swarm_patterns)

            self.logger.info(f"Detected {len(swarm_patterns)} swarm patterns")
            return swarm_patterns

        except Exception as e:
            self.logger.error(f"Error detecting swarms: {e}")
            return []

    async def _analyze_swarm_patterns(self, transfers: List[Dict]) -> List[SwarmPattern]:
        """Analyze transfers for swarm patterns"""
        swarm_patterns = []

        # Group transactions by time windows
        time_windows = {}
        for transfer in transfers:
            timestamp = transfer['timestamp']
            window_key = int(timestamp // 300) * 300  # 5-minute windows

            if window_key not in time_windows:
                time_windows[window_key] = []
            time_windows[window_key].append(transfer)

        # Analyze each time window for patterns
        for window_start, window_transfers in time_windows.items():
            if len(window_transfers) < self.swarm_threshold:
                continue

            # Look for addresses with multiple transactions
            address_activity = {}
            for transfer in window_transfers:
                for addr in [transfer['from_address'], transfer['to_address']]:
                    if addr not in address_activity:
                        address_activity[addr] = []
                    address_activity[addr].append(transfer)

            # Find potential swarm groups
            active_addresses = [addr for addr, txs in address_activity.items()
                              if len(txs) >= 3]  # At least 3 transactions

            if len(active_addresses) >= 3:  # At least 3 active addresses
                total_volume = sum(
                    Decimal(t['value']) / (10 ** self.token_decimals)
                    for t in window_transfers
                )

                avg_tx_size = total_volume / len(window_transfers)

                # Calculate coordination score based on timing similarity
                timestamps = [t['timestamp'] for t in window_transfers]
                time_variance = max(timestamps) - min(timestamps)
                coordination_score = max(0, 1 - (time_variance / 300))  # Higher score for tighter timing

                swarm = SwarmPattern(
                    swarm_id=f"swarm_{window_start}_{len(active_addresses)}",
                    addresses=active_addresses,
                    start_time=window_start,
                    end_time=window_start + 300,
                    transaction_count=len(window_transfers),
                    total_volume=total_volume,
                    avg_transaction_size=avg_tx_size,
                    coordination_score=coordination_score
                )

                swarm_patterns.append(swarm)

        return swarm_patterns

    async def _store_swarm_patterns(self, patterns: List[SwarmPattern]):
        """Store swarm patterns in database"""
        try:
            for pattern in patterns:
                await self.db_manager.execute_query("""
                    INSERT OR REPLACE INTO swarm_patterns
                    (swarm_id, addresses, start_time, end_time, transaction_count,
                     total_volume, avg_transaction_size, coordination_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.swarm_id, json.dumps(pattern.addresses),
                    pattern.start_time, pattern.end_time,
                    pattern.transaction_count, str(pattern.total_volume),
                    str(pattern.avg_transaction_size), pattern.coordination_score
                ))

        except Exception as e:
            self.logger.error(f"Failed to store swarm patterns: {e}")

    @log_performance("analyzer.analyze_wallet")
    async def analyze_wallet(self, address: str) -> WalletAnalysis:
        """
        Perform comprehensive analysis of a wallet
        """
        self.logger.info(f"Analyzing wallet: {address}")

        try:
            # Get token balances
            maxx_balance = await self._get_token_balance(address)
            eth_balance = await self._get_eth_balance(address)

            # Get transaction history
            transactions = await self._get_wallet_transactions(address)

            # Calculate metrics
            total_value_usd = await self._calculate_portfolio_value(address, maxx_balance, eth_balance)
            profit_loss = await self._calculate_profit_loss(address, transactions)
            hold_time = await self._calculate_average_hold_time(address, transactions)

            # Determine wallet characteristics
            is_whale = maxx_balance > self.whale_threshold
            is_bot = await self._detect_bot_behavior(address, transactions)
            risk_score = await self._calculate_risk_score(address, maxx_balance, transactions)

            analysis = WalletAnalysis(
                address=address,
                maxx_balance=maxx_balance,
                eth_balance=eth_balance,
                total_value_usd=total_value_usd,
                profit_loss=profit_loss,
                hold_time=hold_time,
                transaction_count=len(transactions),
                is_whale=is_whale,
                is_bot=is_bot,
                risk_score=risk_score
            )

            # Store analysis
            await self._store_wallet_analysis(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing wallet {address}: {e}")
            return WalletAnalysis(
                address=address,
                maxx_balance=Decimal('0'),
                eth_balance=Decimal('0'),
                total_value_usd=Decimal('0'),
                profit_loss=Decimal('0'),
                hold_time=0,
                transaction_count=0
            )

    async def _get_token_balance(self, address: str) -> Decimal:
        """Get MAXX token balance for address"""
        try:
            # This would query the actual token contract
            # For now, return from our holder cache
            if address.lower() in self._holder_cache:
                return self._holder_cache[address.lower()].balance
            return Decimal('0')
        except Exception:
            return Decimal('0')

    async def _get_eth_balance(self, address: str) -> Decimal:
        """Get ETH balance for address"""
        try:
            # This would query an ETH API
            # For now, return a placeholder
            return Decimal('0')
        except Exception:
            return Decimal('0')

    async def _get_wallet_transactions(self, address: str) -> List[Dict]:
        """Get transaction history for wallet"""
        try:
            return await self.db_manager.execute_query("""
                SELECT * FROM analyzed_transactions
                WHERE from_address = ? OR to_address = ?
                ORDER BY timestamp DESC
                LIMIT 1000
            """, (address.lower(), address.lower()))
        except Exception:
            return []

    async def _calculate_portfolio_value(self, address: str, maxx_balance: Decimal,
                                        eth_balance: Decimal) -> Decimal:
        """Calculate total portfolio value in USD"""
        try:
            # Get current prices
            maxx_price = await self._get_current_token_price()
            eth_price = await self._get_eth_price()

            return (maxx_balance * maxx_price) + (eth_balance * eth_price)
        except Exception:
            return Decimal('0')

    async def _get_current_token_price(self) -> Decimal:
        """Get current MAXX token price in USD"""
        try:
            # This would fetch from a price API
            # For now, return a placeholder
            return Decimal('0.01')
        except Exception:
            return Decimal('0')

    async def _get_eth_price(self) -> Decimal:
        """Get current ETH price in USD"""
        try:
            # This would fetch from a price API
            return Decimal('2000')  # Placeholder
        except Exception:
            return Decimal('0')

    async def _calculate_profit_loss(self, address: str, transactions: List[Dict]) -> Decimal:
        """Calculate profit/loss for wallet"""
        try:
            # Simplified P&L calculation
            # In production, this would track actual purchase/sale prices
            return Decimal('0')
        except Exception:
            return Decimal('0')

    async def _calculate_average_hold_time(self, address: str, transactions: List[Dict]) -> float:
        """Calculate average hold time for tokens"""
        try:
            if len(transactions) < 2:
                return 0

            # Calculate time between first and last transaction
            timestamps = [t['timestamp'] for t in transactions]
            return max(timestamps) - min(timestamps)
        except Exception:
            return 0

    async def _detect_bot_behavior(self, address: str, transactions: List[Dict]) -> bool:
        """Detect if wallet exhibits bot-like behavior"""
        try:
            if len(transactions) < 10:
                return False

            # Look for patterns indicative of bots
            # 1. Very consistent timing
            timestamps = [t['timestamp'] for t in transactions]
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]

            # Calculate variance in intervals
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)

                # Low variance suggests bot behavior
                if variance < 60:  # Less than 1 minute variance
                    return True

            # 2. Round number amounts
            round_amounts = sum(1 for t in transactions
                              if float(t['value']) % 1000000000000000000 == 0)  # Whole tokens

            if round_amounts / len(transactions) > 0.8:  # 80% round amounts
                return True

            return False

        except Exception:
            return False

    async def _calculate_risk_score(self, address: str, balance: Decimal,
                                  transactions: List[Dict]) -> float:
        """Calculate risk score for wallet (0-100)"""
        try:
            risk_score = 0

            # Balance-based risk
            if balance > self.whale_threshold:
                risk_score += 30  # Whale risk

            # Activity-based risk
            if len(transactions) > 1000:
                risk_score += 20  # High activity risk

            # Time-based risk (new wallet)
            if transactions:
                first_tx = min(t['timestamp'] for t in transactions)
                wallet_age = time.time() - first_tx

                if wallet_age < 86400 * 30:  # Less than 30 days old
                    risk_score += 25  # New wallet risk

            # Bot behavior risk
            if await self._detect_bot_behavior(address, transactions):
                risk_score += 25

            return min(risk_score, 100)

        except Exception:
            return 50  # Medium risk as default

    async def _store_wallet_analysis(self, analysis: WalletAnalysis):
        """Store wallet analysis in database"""
        try:
            await self.db_manager.execute_query("""
                INSERT OR REPLACE INTO wallet_analyses
                (address, maxx_balance, eth_balance, total_value_usd, profit_loss,
                 hold_time, transaction_count, is_whale, is_bot, risk_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.address, str(analysis.maxx_balance), str(analysis.eth_balance),
                str(analysis.total_value_usd), str(analysis.profit_loss),
                analysis.hold_time, analysis.transaction_count,
                int(analysis.is_whale), int(analysis.is_bot),
                analysis.risk_score, time.time()
            ))

        except Exception as e:
            self.logger.error(f"Failed to store wallet analysis: {e}")

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        try:
            # Get top holders
            top_holders = await self.get_top_token_holders(10)

            # Get recent swarms
            recent_swarms = await self.detect_swarms(3600)

            # Get holder distribution
            holder_stats = await self._get_holder_distribution_stats()

            # Get trading activity
            trading_stats = await self._get_trading_stats()

            overview = {
                'contract_address': self.contract_address,
                'top_holders': [asdict(h) for h in top_holders],
                'recent_swarms': [asdict(s) for s in recent_swarms[:5]],
                'holder_distribution': holder_stats,
                'trading_activity': trading_stats,
                'timestamp': time.time()
            }

            return overview

        except Exception as e:
            self.logger.error(f"Error generating market overview: {e}")
            return {}

    async def _get_holder_distribution_stats(self) -> Dict[str, Any]:
        """Get holder distribution statistics"""
        try:
            result = await self.db_manager.execute_query("""
                SELECT
                    COUNT(*) as total_holders,
                    SUM(CASE WHEN balance > 1000000 THEN 1 ELSE 0 END) as whale_count,
                    SUM(CASE WHEN balance > 10000 AND balance <= 1000000 THEN 1 ELSE 0 END) as large_holder_count,
                    SUM(CASE WHEN balance > 1000 AND balance <= 10000 THEN 1 ELSE 0 END) as medium_holder_count,
                    SUM(CASE WHEN balance <= 1000 THEN 1 ELSE 0 END) as small_holder_count,
                    AVG(percentage) as avg_percentage,
                    MAX(percentage) as max_percentage
                FROM token_holders
                WHERE balance > 0
            """)

            if result:
                return dict(result[0])

            return {}

        except Exception as e:
            self.logger.error(f"Error getting holder stats: {e}")
            return {}

    async def _get_trading_stats(self) -> Dict[str, Any]:
        """Get trading activity statistics"""
        try:
            # Get last 24 hours of activity
            cutoff_time = time.time() - 86400

            result = await self.db_manager.execute_query("""
                SELECT
                    COUNT(*) as transaction_count,
                    SUM(CASE WHEN is_swarm_transaction = 1 THEN 1 ELSE 0 END) as swarm_transactions,
                    SUM(CASE WHEN is_cluster_transaction = 1 THEN 1 ELSE 0 END) as cluster_transactions,
                    AVG(calculated_profit) as avg_profit,
                    SUM(value) as total_volume
                FROM analyzed_transactions
                WHERE timestamp > ?
            """, (cutoff_time,))

            if result:
                return dict(result[0])

            return {}

        except Exception as e:
            self.logger.error(f"Error getting trading stats: {e}")
            return {}

    async def close(self):
        """Close analyzer resources"""
        self.logger.info("Ethermax analyzer closed")


# Global analyzer instance
_analyzer: Optional[EthermaxAnalyzer] = None


async def get_ethermax_analyzer() -> EthermaxAnalyzer:
    """Get global Ethermax analyzer instance"""
    global _analyzer

    if _analyzer is None:
        _analyzer = EthermaxAnalyzer()
        await _analyzer.initialize()

    return _analyzer


async def close_ethermax_analyzer():
    """Close global Ethermax analyzer"""
    global _analyzer

    if _analyzer:
        await _analyzer.close()
        _analyzer = None


if __name__ == "__main__":
    import asyncio

    async def main():
        analyzer = await get_ethermax_analyzer()

        # Test analysis
        holders = await analyzer.get_top_token_holders(10)
        print(f"Top holders: {len(holders)}")

        swarms = await analyzer.detect_swarms()
        print(f"Detected swarms: {len(swarms)}")

        overview = await analyzer.get_market_overview()
        print(f"Market overview keys: {list(overview.keys())}")

        await close_ethermax_analyzer()

    asyncio.run(main())
