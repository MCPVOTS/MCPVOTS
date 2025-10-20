"""
Enhanced Market Data Service for MAXX Ecosystem
Provides real-time market data with caching and analytics
"""
import asyncio
import aiohttp
import json
import time
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_network_config
from core.logging import get_logger, log_performance
from core.database import get_database_manager
from core.network import get_network_manager


@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: Decimal
    volume: Decimal
    high_24h: Decimal
    low_24h: Decimal
    change_24h: Decimal
    timestamp: float
    exchange: str
    additional_data: Dict[str, Any] = None

    def __post_init__(self):
        # Convert to Decimal for precision
        if isinstance(self.price, (int, float, str)):
            self.price = Decimal(str(self.price))
        if isinstance(self.volume, (int, float, str)):
            self.volume = Decimal(str(self.volume))
        if isinstance(self.high_24h, (int, float, str)):
            self.high_24h = Decimal(str(self.high_24h))
        if isinstance(self.low_24h, (int, float, str)):
            self.low_24h = Decimal(str(self.low_24h))
        if isinstance(self.change_24h, (int, float, str)):
            self.change_24h = Decimal(str(self.change_24h))


class MAXXMarketDataService:
    """
    Enhanced service to fetch real market data for MAXX token on Base
    with proper error handling, caching, and storage integration
    """

    def __init__(self):
        self.config = get_network_config()
        self.logger = get_logger(self.__class__.__name__)
        self.db_manager = None
        self.network_manager = None
        self.cache_ttl = 60  # 1 minute TTL for price data
        self.token_data = {}
        self.last_updated = 0
        self.subscribers: Dict[str, List[Callable]] = {}
        self.is_running = False

        # API endpoints
        self.dexscreener_endpoint = "https://api.dexscreener.com/latest/dex/tokens/"
        self.basescan_api = "https://api.basescan.org/api"
        self.coinGecko_api = "https://api.coingecko.com/api/v3"

        # Contract addresses (move to config in production)
        self.maxx_contract_address = os.getenv('MAXX_CONTRACT_ADDRESS', '0x...')

    async def initialize(self):
        """Initialize the market data service"""
        self.db_manager = await get_database_manager()
        self.network_manager = await get_network_manager()

        # Load cached data from database
        await self._load_cached_data()

        self.logger.info("MAXX market data service initialized")

    async def start(self):
        """Start real-time data updates"""
        if self.is_running:
            return

        self.is_running = True
        self.logger.info("Starting MAXX market data service...")

        # Start update loop
        asyncio.create_task(self._update_loop())

        self.logger.info("MAXX market data service started")

    async def stop(self):
        """Stop the market data service"""
        self.is_running = False
        self.logger.info("MAXX market data service stopped")

    @log_performance("market_data.load_cache")
    async def _load_cached_data(self):
        """Load cached data from database"""
        try:
            # Get latest market data for MAXX
            query = """
                SELECT symbol, price, volume, high_24h, low_24h,
                       change_24h, timestamp, exchange, additional_data
                FROM market_data
                WHERE symbol = 'MAXX' AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 1
            """

            cutoff_time = time.time() - 3600  # Last hour
            results = await self.db_manager.execute_query(query, (cutoff_time,))

            if results:
                row = results[0]
                self.token_data = {
                    'current_price': Decimal(str(row['price'])),
                    'price_change_24h': Decimal(str(row['change_24h'])),
                    'volume_24h': Decimal(str(row['volume'])),
                    'high_24h': Decimal(str(row['high_24h'])),
                    'low_24h': Decimal(str(row['low_24h'])),
                    'timestamp': row['timestamp'],
                    'exchange': row['exchange'],
                    'additional_data': json.loads(row['additional_data']) if row['additional_data'] else {}
                }
                self.last_updated = row['timestamp']

            self.logger.info("Loaded cached MAXX data from database")

        except Exception as e:
            self.logger.error(f"Failed to load cached data: {e}")

    async def _update_loop(self):
        """Main update loop for real-time data"""
        while self.is_running:
            try:
                await self.fetch_market_data()
                await asyncio.sleep(self.cache_ttl)

            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                await asyncio.sleep(30)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def fetch_dexscreener_data(self) -> Dict[str, Any]:
        """Fetch real data from DexScreener for MAXX token"""
        if not self.maxx_contract_address or self.maxx_contract_address == '0x...':
            self.logger.warning("MAXX contract address not configured")
            return {}

        endpoint = f"{self.dexscreener_endpoint}{self.maxx_contract_address}"
        http_client = self.network_manager.get_http_client()

        try:
            response = await http_client.get(endpoint)
            if response.success:
                self.logger.info("DexScreener data fetched successfully")
                return response.data
            else:
                self.logger.error(f"DexScreener API request failed: {response.error_message}")
                return {}
        except Exception as e:
            self.logger.error(f"Error fetching DexScreener data: {e}")
            return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def fetch_token_transfers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent token transfers for MAXX token using BaseScan API"""
        self.logger.info("Fetching token transfers for MAXX token")

        api_key = os.getenv('BASESCAN_API_KEY')
        if not api_key:
            self.logger.warning("BASESCAN_API_KEY not set; skipping transfers fetch")
            return []

        if not self.maxx_contract_address or self.maxx_contract_address == '0x...':
            self.logger.warning("MAXX contract address not configured")
            return []

        try:
            http_client = self.network_manager.get_http_client(self.basescan_api)
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': self.maxx_contract_address,
                'page': 1,
                'offset': limit,
                'apikey': api_key
            }

            response = await http_client.get('', params=params)
            if response.success:
                data = response.data

                if data.get('status') == '1':
                    transfers = []
                    for tx in data.get('result', [])[:limit]:
                        transfers.append({
                            'transactionHash': tx.get('hash', ''),
                            'from': tx.get('from', ''),
                            'to': tx.get('to', ''),
                            'value': tx.get('value', '0'),
                            'timestamp': int(tx.get('timeStamp', 0)),
                            'blockNumber': int(tx.get('blockNumber', 0))
                        })

                    self.logger.info(f"Fetched {len(transfers)} token transfers")

                    # Store summary
                    await self._store_market_data(
                        symbol='MAXX',
                        price=Decimal('0'),  # No price here
                        volume=Decimal(str(sum(int(t.get('value', 0)) for t in transfers))),
                        additional_data={'transfers_count': len(transfers)}
                    )

                    return transfers
                else:
                    self.logger.error(f"BaseScan API error: {data.get('message', 'Unknown')}")
                    return []
            else:
                self.logger.error(f"BaseScan API request failed: {response.error_message}")
                return []

        except Exception as e:
            self.logger.error(f"Error fetching transfers: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def fetch_coingecko_data(self) -> Dict[str, Any]:
        """Fetch data from CoinGecko as backup source"""
        try:
            http_client = self.network_manager.get_http_client(self.coinGecko_api)

            # Try to get MAXX token data (would need actual CoinGecko ID)
            response = await http_client.get('/simple/price', params={
                'ids': 'maxx-finance',  # This would be the actual CoinGecko ID
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            })

            if response.success:
                data = response.data
                if 'maxx-finance' in data:
                    coin_data = data['maxx-finance']
                    return {
                        'price': coin_data.get('usd', 0),
                        'change_24h': coin_data.get('usd_24h_change', 0),
                        'volume_24h': coin_data.get('usd_24h_vol', 0)
                    }

        except Exception as e:
            self.logger.debug(f"CoinGecko API error: {e}")

        return {}

    @log_performance("market_data.fetch")
    async def fetch_market_data(self) -> Dict[str, Any]:
        """Fetch comprehensive real market data for MAXX token and store it"""
        self.logger.info("Fetching comprehensive market data for MAXX token...")

        # Check cache
        if time.time() - self.last_updated < self.cache_ttl and self.token_data:
            self.logger.debug("Using cached market data")
            return self.token_data

        # Try DexScreener first
        dex_data = await self.fetch_dexscreener_data()

        if dex_data and 'pairs' in dex_data and dex_data['pairs']:
            # Find the pair with highest liquidity
            pairs = dex_data['pairs']
            top_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0) or 0)

            price_usd = Decimal(str(top_pair.get('priceUsd', 0) or 0))
            price_change_24h = Decimal(str(top_pair.get('priceChange', {}).get('h24', 0) or 0))
            liquidity_usd = Decimal(str(top_pair.get('liquidity', {}).get('usd', 0) or 0))
            volume_24h = Decimal(str(top_pair.get('volume', {}).get('h24', 0) or 0))
            high_24h = Decimal(str(top_pair.get('highPrice', 0) or 0))
            low_24h = Decimal(str(top_pair.get('lowPrice', 0) or 0))
            fdv = Decimal(str(top_pair.get('fdv', 0) or 0))

            market_data = {
                'current_price': price_usd,
                'price_change_24h': price_change_24h,
                'liquidity': liquidity_usd,
                'volume_24h': volume_24h,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'pair_address': top_pair.get('pairAddress', ''),
                'base_token': top_pair.get('baseToken', {}),
                'quote_token': top_pair.get('quoteToken', {}),
                'dex_id': top_pair.get('dexId', ''),
                'market_cap': fdv,
                'timestamp': time.time(),
                'exchange': 'dexscreener'
            }
        else:
            # Fallback to CoinGecko
            gecko_data = await self.fetch_coingecko_data()
            if gecko_data:
                market_data = {
                    'current_price': Decimal(str(gecko_data['price'])),
                    'price_change_24h': Decimal(str(gecko_data['change_24h'])),
                    'volume_24h': Decimal(str(gecko_data['volume_24h'])),
                    'high_24h': Decimal('0'),
                    'low_24h': Decimal('0'),
                    'liquidity': Decimal('0'),
                    'pair_address': '',
                    'base_token': {},
                    'quote_token': {},
                    'dex_id': '',
                    'market_cap': Decimal('0'),
                    'timestamp': time.time(),
                    'exchange': 'coingecko'
                }
            else:
                # No data available
                self.logger.warning("No market data available from any source")
                return self.token_data or {}

        # Store to database
        await self._store_market_data(
            symbol='MAXX',
            price=market_data['current_price'],
            volume=market_data['volume_24h'],
            high_24h=market_data['high_24h'],
            low_24h=market_data['low_24h'],
            change_24h=market_data['price_change_24h'],
            exchange=market_data['exchange'],
            additional_data=market_data
        )

        self.token_data = market_data
        self.last_updated = time.time()

        # Notify subscribers
        await self._notify_subscribers('MAXX', market_data)

        self.logger.info(f"Fetched market data: price=${market_data['current_price']}, 24h change={market_data['price_change_24h']}%")
        return market_data

    async def _store_market_data(self, symbol: str, price: Decimal, volume: Decimal,
                                high_24h: Decimal = None, low_24h: Decimal = None,
                                change_24h: Decimal = None, exchange: str = 'unknown',
                                additional_data: Dict[str, Any] = None):
        """Store market data in database"""
        try:
            from core.database import QueryType

            await self.db_manager.execute_query(
                """
                INSERT INTO market_data
                (symbol, price, volume, high_24h, low_24h, change_24h,
                 timestamp, exchange, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, float(price), float(volume),
                    float(high_24h) if high_24h else 0,
                    float(low_24h) if low_24h else 0,
                    float(change_24h) if change_24h else 0,
                    time.time(), exchange, json.dumps(additional_data or {})
                ),
                query_type=QueryType.INSERT
            )

        except Exception as e:
            self.logger.error(f"Failed to store market data: {e}")

    async def _notify_subscribers(self, symbol: str, data: Dict[str, Any]):
        """Notify all subscribers of a symbol"""
        if symbol in self.subscribers:
            for callback in self.subscribers[symbol]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    self.logger.error(f"Subscriber callback error: {e}")

    def subscribe(self, symbol: str, callback: Callable):
        """Subscribe to market data updates for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []

        self.subscribers[symbol].append(callback)
        self.logger.info(f"Subscribed to {symbol} market data")

    def unsubscribe(self, symbol: str, callback: Callable):
        """Unsubscribe from market data updates for a symbol"""
        if symbol in self.subscribers:
            try:
                self.subscribers[symbol].remove(callback)
                if not self.subscribers[symbol]:
                    del self.subscribers[symbol]

                self.logger.info(f"Unsubscribed from {symbol} market data")
            except ValueError:
                pass  # Callback not found

    async def get_market_data(self) -> Dict[str, Any]:
        """Get latest market data for MAXX token"""
        if not self.token_data or time.time() - self.last_updated > self.cache_ttl:
            await self.fetch_market_data()

        return self.token_data

    async def get_price_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get price history from database"""
        self.logger.info(f"Getting price history for last {hours} hours")

        try:
            # Calculate time range
            end_time = time.time()
            start_time = end_time - (hours * 3600)

            query = """
                SELECT symbol, price, volume, high_24h, low_24h,
                       change_24h, timestamp, exchange, additional_data
                FROM market_data
                WHERE symbol = 'MAXX' AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """

            results = await self.db_manager.execute_query(query, (start_time, end_time))

            history = []
            for row in results:
                history.append({
                    'symbol': row['symbol'],
                    'price': Decimal(str(row['price'])),
                    'volume': Decimal(str(row['volume'])),
                    'high_24h': Decimal(str(row['high_24h'])),
                    'low_24h': Decimal(str(row['low_24h'])),
                    'change_24h': Decimal(str(row['change_24h'])),
                    'timestamp': row['timestamp'],
                    'exchange': row['exchange'],
                    'additional_data': json.loads(row['additional_data']) if row['additional_data'] else {}
                })

            self.logger.info(f"Retrieved {len(history)} historical price points")
            return history

        except Exception as e:
            self.logger.error(f"Failed to get price history: {e}")
            return []


class MAXXSocialDataService:
    """
    Service to fetch social data for MAXX token with real API integrations
    """

    def __init__(self):
        self.search_terms = ["$MAXX", "MAXX token", "ethermax"]
        self.logger = get_logger(self.__class__.__name__)
        self.network_manager = None
        self.cache_ttl = 300  # 5 minutes TTL for social data
        self.last_updated = 0
        self.social_data = {}

    async def initialize(self):
        """Initialize the social data service"""
        self.network_manager = await get_network_manager()
        self.logger.info("MAXX social data service initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def fetch_twitter_data(self) -> Dict[str, Any]:
        """Fetch data from Twitter API v2"""
        # This would require Twitter API v2 credentials
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            self.logger.warning("Twitter API credentials not configured")
            return {}

        try:
            # Search for recent tweets about MAXX
            query = " OR ".join(self.search_terms)
            url = "https://api.twitter.com/2/tweets/search/recent"

            http_client = self.network_manager.get_http_client()
            headers = {'Authorization': f'Bearer {bearer_token}'}

            response = await http_client.get(url, params={
                'query': query,
                'tweet.fields': 'created_at,public_metrics,author_id',
                'max_results': 100
            }, headers=headers)

            if response.success:
                tweets = response.data.get('data', [])

                # Analyze sentiment (would need NLP integration)
                positive_count = 0
                negative_count = 0
                neutral_count = len(tweets)

                return {
                    'mentions_24h': len(tweets),
                    'positive_mentions': positive_count,
                    'negative_mentions': negative_count,
                    'neutral_mentions': neutral_count,
                    'top_tweets': tweets[:5],  # Top 5 tweets
                    'updated_at': time.time()
                }

        except Exception as e:
            self.logger.error(f"Twitter API error: {e}")

        return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def fetch_reddit_data(self) -> Dict[str, Any]:
        """Fetch data from Reddit API"""
        # This would require Reddit API credentials
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.logger.warning("Reddit API credentials not configured")
            return {}

        try:
            # Search for mentions in relevant subreddits
            # Implementation would go here
            return {
                'reddit_mentions': 0,
                'subreddits': [],
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        except Exception as e:
            self.logger.error(f"Reddit API error: {e}")

        return {}

    async def fetch_social_data(self) -> Dict[str, Any]:
        """Fetch comprehensive social data for MAXX token"""
        self.logger.info("Fetching social data for MAXX token")

        # Check cache
        if time.time() - self.last_updated < self.cache_ttl and self.social_data:
            self.logger.debug("Using cached social data")
            return self.social_data

        # Fetch from various sources
        twitter_data = await self.fetch_twitter_data()
        reddit_data = await self.fetch_reddit_data()

        # Combine data
        social_data = {
            'mentions_24h': twitter_data.get('mentions_24h', 0) + reddit_data.get('reddit_mentions', 0),
            'positive_mentions': twitter_data.get('positive_mentions', 0) + reddit_data.get('sentiment_breakdown', {}).get('positive', 0),
            'negative_mentions': twitter_data.get('negative_mentions', 0) + reddit_data.get('sentiment_breakdown', {}).get('negative', 0),
            'neutral_mentions': twitter_data.get('neutral_mentions', 0) + reddit_data.get('sentiment_breakdown', {}).get('neutral', 0),
            'top_hashtags': [],  # Would extract from tweets
            'sentiment_score': 0.0,  # Would calculate from sentiment analysis
            'influencer_mentions': 0,  # Would identify influencer accounts
            'community_growth': 0.0,  # Would track follower growth
            'twitter_data': twitter_data,
            'reddit_data': reddit_data,
            'updated_at': time.time()
        }

        # Calculate sentiment score
        total_mentions = social_data['mentions_24h']
        if total_mentions > 0:
            positive_ratio = social_data['positive_mentions'] / total_mentions
            social_data['sentiment_score'] = (positive_ratio * 2 - 1) * 100  # -100 to +100 scale

        self.social_data = social_data
        self.last_updated = time.time()

        self.logger.info(f"Fetched social data: {total_mentions} mentions, sentiment score: {social_data['sentiment_score']:.2f}")
        return social_data


# Global service instances
_maxx_market_service: Optional[MAXXMarketDataService] = None
_maxx_social_service: Optional[MAXXSocialDataService] = None


async def get_maxx_market_service() -> MAXXMarketDataService:
    """Get global MAXX market data service instance"""
    global _maxx_market_service

    if _maxx_market_service is None:
        _maxx_market_service = MAXXMarketDataService()
        await _maxx_market_service.initialize()

    return _maxx_market_service


async def get_maxx_social_service() -> MAXXSocialDataService:
    """Get global MAXX social data service instance"""
    global _maxx_social_service

    if _maxx_social_service is None:
        _maxx_social_service = MAXXSocialDataService()
        await _maxx_social_service.initialize()

    return _maxx_social_service


async def close_market_data_services():
    """Close global market data services"""
    global _maxx_market_service, _maxx_social_service

    if _maxx_market_service:
        await _maxx_market_service.stop()
        _maxx_market_service = None

    if _maxx_social_service:
        _maxx_social_service = None


if __name__ == "__main__":
    import asyncio
    from core.logging import logging_manager

    async def main():
        # Initialize services
        market_service = await get_maxx_market_service()
        social_service = await get_maxx_social_service()

        # Start market service
        await market_service.start()

        # Fetch some data
        market_data = await market_service.fetch_market_data()
        print(f"Market Data: {market_data}")

        social_data = await social_service.fetch_social_data()
        print(f"Social Data: {social_data}")

        # Get price history
        history = await market_service.get_price_history(24)
        print(f"Price History Points: {len(history)}")

        # Stop services
        await close_market_data_services()

    asyncio.run(main())
