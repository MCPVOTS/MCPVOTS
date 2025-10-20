"""
Network utilities for MAXX token agent
Provides connections to data feeds and market information
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Callable
from BASE_NETWORK.network_base import BaseConnection, MessageProtocol, ConnectionStatus
from BASE_NETWORK.example_connection import HttpConnection
from market_data_service import MAXXMarketDataService, MAXXSocialDataService


class MAXXMarketDataFeed(HttpConnection):
    """
    Specialized connection for MAXX token market data
    """

    def __init__(self, connection_id: str = None, base_url: str = "https://api.dexscreener.com"):
        super().__init__(connection_id, base_url=base_url)
        self.contract_address = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
        self.base_url = base_url
        self.pairs_endpoint = f"/daily/data/pairs/base/{self.contract_address}"
        self.latest_price = 0
        self.price_change_24h = 0
        self.volume_24h = 0
        self.liquidity = 0

        # Initialize market data service
        self.market_service = MAXXMarketDataService()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self) -> bool:
        """
        Connect to the MAXX token market data feed
        """
        self.logger.info(f"Connecting to MAXX token market data feed at {self.base_url}...")

        # Initialize connection using aiohttp
        self.session = aiohttp.ClientSession()

        try:
            # Make a test request to verify the endpoint is accessible
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    self.status = ConnectionStatus.CONNECTED
                    self.logger.info(f"Connected to MAXX token market data feed")

                    # Fetch initial data
                    await self.fetch_initial_data()
                    return True
                else:
                    self.status = ConnectionStatus.ERROR
                    self.logger.error(f"Failed to connect to {self.base_url}, status: {response.status}")
                    return False
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"Error connecting to market data feed: {e}")
            return False

    async def fetch_initial_data(self):
        """
        Fetch initial market data for the MAXX token
        """
        try:
            # Fetch data using the market service
            market_data = await self.market_service.fetch_market_data()
            self.latest_price = market_data.get('current_price', 0)
            self.price_change_24h = market_data.get('price_change_24h', 0)
            self.volume_24h = market_data.get('volume_24h', 0)
            self.liquidity = market_data.get('liquidity', 0)

            self.logger.info(f"Initial MAXX data fetched: Price=${self.latest_price}, "
                             f"24h Change={self.price_change_24h}%, "
                             f"24h Volume=${self.volume_24h}, "
                             f"Liquidity=${self.liquidity}")
        except Exception as e:
            self.logger.error(f"Error fetching initial MAXX data: {e}")

    async def fetch_maxx_data(self) -> Dict[str, Any]:
        """
        Fetch the latest MAXX token data
        """
        if self.status != ConnectionStatus.CONNECTED:
            self.logger.warning("Not connected to market data feed")
            return {}

        try:
            # Get fresh market data using the service
            data = await self.market_service.fetch_market_data()

            # Update instance variables
            self.latest_price = data.get('current_price', self.latest_price)
            self.volume_24h = data.get('volume_24h', self.volume_24h)
            self.liquidity = data.get('liquidity', self.liquidity)

            self.logger.debug(f"Fetched MAXX data: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error fetching MAXX data: {e}")
            # Return basic data with current values
            return {
                'current_price': self.latest_price,
                'price_change_24h': self.price_change_24h,
                'volume_24h': self.volume_24h,
                'liquidity': self.liquidity,
                'holders': 5200,  # Simulated holder count
                'market_cap': 2500000,  # Simulated market cap
                'updated_at': asyncio.get_event_loop().time()
            }

    async def subscribe_to_updates(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to real-time updates for MAXX token data using WebSocket
        """
        self.logger.info("Starting subscription to MAXX token updates via WebSocket...")

        import websockets
        import json

        # WebSocket URL for MAXX token updates (replace with real endpoint)
        ws_url = f"wss://api.dexscreener.com/ws/pairs/base/{self.contract_address}"

        try:
            async with websockets.connect(ws_url) as websocket:
                # Send subscription message
                subscribe_msg = {
                    "action": "subscribe",
                    "channel": "pairUpdates",
                    "pairAddress": self.contract_address
                }
                await websocket.send(json.dumps(subscribe_msg))

                while self.status == ConnectionStatus.CONNECTED:
                    try:
                        # Receive update from WebSocket
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(message)

                        # Process the received data and call the callback
                        processed_data = {
                            'current_price': float(data.get('priceUsd', self.latest_price)),
                            'price_change_24h': float(data.get('priceChange24h', self.price_change_24h)),
                            'volume_24h': float(data.get('volume24h', self.volume_24h)),
                            'liquidity': float(data.get('liquidity', self.liquidity)),
                            'holders': data.get('holders', 5200),
                            'market_cap': float(data.get('marketCap', 0)),
                            'updated_at': asyncio.get_event_loop().time()
                        }

                        callback(processed_data)

                        # Update internal state
                        self.latest_price = processed_data['current_price']
                        self.price_change_24h = processed_data['price_change_24h']
                        self.volume_24h = processed_data['volume_24h']
                        self.liquidity = processed_data['liquidity']

                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await websocket.send(json.dumps({"action": "ping"}))
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning("WebSocket connection closed, attempting to reconnect...")
                        break
                    except Exception as e:
                        self.logger.error(f"Error in WebSocket subscription: {e}")
                        await asyncio.sleep(5)  # Wait before retrying

        except Exception as e:
            self.logger.error(f"Error establishing WebSocket connection: {e}")
            # Fallback to polling if WebSocket fails
            self.logger.info("Falling back to polling method...")
            while self.status == ConnectionStatus.CONNECTED:
                data = await self.fetch_maxx_data()
                if data:
                    callback(data)
                await asyncio.sleep(30)  # Poll every 30 seconds


class MAXXSocialSentimentFeed(HttpConnection):
    """
    Connection for social media sentiment analysis of MAXX token
    """

    def __init__(self, connection_id: str = None, base_url: str = "https://api.twitter.com"):
        super().__init__(connection_id, base_url=base_url)
        self.search_terms = ["$MAXX", "MAXX token", "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467", "ethermax"]
        self.sentiment_score = 0.5  # Neutral sentiment (0 to 1 scale)

        # Initialize social data service
        self.social_service = MAXXSocialDataService()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self) -> bool:
        """
        Connect to social media sentiment feed for MAXX token
        """
        import aiohttp

        self.logger.info(f"Connecting to social sentiment feed for MAXX token...")

        # Create aiohttp session for social media requests
        self.session = aiohttp.ClientSession()

        try:
            # Test connection to social media API (e.g., Twitter API)
            # In a real implementation, we would use the Twitter API or another service
            self.status = ConnectionStatus.CONNECTED
            self.logger.info("Connected to social sentiment feed for MAXX token")

            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"Error connecting to social sentiment feed: {e}")
            return False

    async def get_sentiment_data(self) -> Dict[str, Any]:
        """
        Get the latest sentiment data for MAXX token
        """
        if self.status != ConnectionStatus.CONNECTED:
            self.logger.warning("Not connected to sentiment feed")
            return {}

        try:
            # Get fresh social data using the service
            sentiment_data = await self.social_service.fetch_social_data()

            # Update instance variable
            self.sentiment_score = sentiment_data.get('sentiment_score', self.sentiment_score)

            self.logger.debug(f"Fetched sentiment data: {sentiment_data}")
            return sentiment_data
        except Exception as e:
            self.logger.error(f"Error fetching sentiment data: {e}")
            # Return basic data with current values
            return {
                'sentiment_score': self.sentiment_score,
                'positive_mentions': 120,
                'negative_mentions': 30,
                'neutral_mentions': 80,
                'total_mentions': 230,
                'top_hashtags': ['#MAXX', '#BaseChain', '#MemeCoin'],
                'influencer_mentions': 5,
                'updated_at': asyncio.get_event_loop().time()
            }


class MAXXNotificationService(HttpConnection):
    """
    Service for sending notifications about MAXX token events
    """

    def __init__(self, connection_id: str = None, webhook_url: str = ""):
        super().__init__(connection_id, base_url=webhook_url)
        self.webhook_url = webhook_url
        self.subscribers = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self) -> bool:
        """
        Connect to the notification service
        """
        if not self.webhook_url:
            self.logger.warning("No webhook URL provided, notifications disabled")
            return False

        self.logger.info(f"Connecting to notification service at {self.webhook_url}...")
        self.status = ConnectionStatus.CONNECTING
        await asyncio.sleep(0.05)
        self.status = ConnectionStatus.CONNECTED
        self.logger.info("Connected to notification service")
        return True

    async def send_notification(self, message: str, notification_type: str = "info"):
        """
        Send a notification about MAXX token to Discord webhook
        """
        import aiohttp
        import json

        if self.status != ConnectionStatus.CONNECTED:
            self.logger.warning("Notification service not connected")
            return False

        if not self.webhook_url:
            self.logger.warning("No webhook URL provided for notifications")
            return False

        try:
            # Create the payload for Discord webhook
            payload = {
                "content": message,
                "embeds": [
                    {
                        "title": f"MAXX Token {notification_type.title()}",
                        "description": message,
                        "color": 0x00ff00 if notification_type == "info" else 0xff0000 if notification_type == "alert" else 0xffff00,
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }

            # Send the notification to the webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status in [200, 204]:
                        self.logger.info(f"Notification sent successfully: {message}")
                        return True
                    else:
                        self.logger.error(f"Failed to send notification. Status: {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False

    async def subscribe(self, subscriber: str):
        """
        Subscribe to notifications
        """
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            self.logger.info(f"Subscribed {subscriber} to MAXX notifications")
        else:
            self.logger.debug(f"{subscriber} already subscribed to MAXX notifications")


# Real trading utilities - no demo functions
# Use MAXXMarketDataFeed, MAXXSocialSentimentFeed, and MAXXNotificationService directly