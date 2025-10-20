"""
Storage Integration Module for MAXX Token Trading Agent
Integrates database and vector storage with the existing trading system
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from db_vector_storage import storage_manager
from MAXX_token_agent import MAXXTokenBot, MAXXTokenAgent
from market_data_service import MAXXMarketDataService, MAXXSocialDataService
from config import Config


class StorageIntegratedMAXXTokenBot(MAXXTokenBot):
    """
    MAXX Token Bot with integrated storage capabilities
    """

    def __init__(self, bot_id: str = None, name: str = "StorageIntegratedMAXXTokenBot",
                 provider_url: str = None,
                 account_private_key: str = None):
        super().__init__(bot_id, name, provider_url, account_private_key)

    async def initialize(self):
        """
        Initialize the bot with storage integration
        """
        await super().initialize()
        import logging
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"Storage integration enabled for {self.name}")

    async def execute_strategy(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the trading strategy with storage of results
        """
        # First, store the incoming market data
        await storage_manager.store_market_data(
            symbol=self.symbol,
            price=market_data.get('current_price', 0),
            volume=market_data.get('volume_24h', 0),
            liquidity=market_data.get('liquidity', 0),
            additional_data=market_data
        )

        # Execute the original strategy
        orders = await super().execute_strategy(market_data)

        # Store the orders as trades if they exist
        for order in orders:
            await storage_manager.store_trade(
                bot_id=self.bot_id,
                symbol=order['symbol'],
                side=order['side'],
                quantity=order['quantity'],
                price=order['price'],
                strategy=order['strategy'],
                timestamp=order.get('timestamp', datetime.now().timestamp())
            )

        # Store performance metrics
        await storage_manager.store_bot_performance(
            bot_id=self.bot_id,
            metric_name='active_orders_count',
            value=len(orders),
            timestamp=datetime.now().timestamp()
        )

        return orders

    async def update_position(self, symbol: str, quantity: float, price: float, side: str):
        """
        Update position with storage of position data
        """
        # Store the position change as a trade
        await storage_manager.store_trade(
            bot_id=self.bot_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            strategy='position_update',
            timestamp=datetime.now().timestamp()
        )

        # Call the parent method
        await super().update_position(symbol, quantity, price, side)

    async def close_position(self, symbol: str) -> float:
        """
        Close position with storage of outcome
        """
        pnl = await super().close_position(symbol)

        # Store the PnL as a performance metric
        await storage_manager.store_bot_performance(
            bot_id=self.bot_id,
            metric_name='pnl',
            value=pnl,
            timestamp=datetime.now().timestamp()
        )

        return pnl

    async def store_market_vector(self, market_conditions: Dict[str, Any]):
        """
        Store current market conditions as a vector for analysis
        """
        # Create a vector representation of current market conditions
        vector_data = [
            market_conditions.get('current_price', 0),
            market_conditions.get('price_change_24h', 0),
            market_conditions.get('volume_24h', 0),
            market_conditions.get('liquidity', 0),
            market_conditions.get('holders', 0),
            market_conditions.get('sentiment_score', 0.5),
            market_conditions.get('rsi', 50),
            market_conditions.get('volatility', 0),
            market_conditions.get('positive_sentiment', 0),
            market_conditions.get('negative_sentiment', 0)
        ]

        market_vector = [float(x) if x is not None else 0.0 for x in vector_data]
        try:
            import numpy as np
            np_market_vector = np.array(market_vector)
        except ImportError:
            # Fallback if numpy is not available
            np_market_vector = market_vector

        # Generate a unique vector ID
        vector_id = f"market_state_{self.bot_id}_{datetime.now().timestamp()}"

        # Store the market state as a vector
        await storage_manager.store_market_vector(vector_id, market_conditions, np_market_vector)


class StorageIntegratedMAXXTokenAgent(MAXXTokenAgent):
    """
    MAXX Token Agent with integrated storage capabilities
    """

    def __init__(self, agent_id: str = None, name: str = "StorageIntegratedMAXXTokenAgent"):
        super().__init__(agent_id, name)
        # Use the storage-integrated bot
        self.maxx_bot = StorageIntegratedMAXXTokenBot()

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with storage of relevant data
        """
        task_type = task.get('type', 'generic')

        if task_type == 'trade':
            # Store market data before executing trade
            market_data = task.get('market_data', {})
            if market_data:
                await storage_manager.store_market_data(
                    symbol='MAXX',
                    price=market_data.get('current_price', 0),
                    volume=market_data.get('volume_24h', 0),
                    liquidity=market_data.get('liquidity', 0),
                    additional_data=market_data
                )

                # Store social sentiment data if available
                if 'sentiment_score' in market_data:
                    await storage_manager.store_social_sentiment(
                        symbol='MAXX',
                        sentiment_score=market_data['sentiment_score'],
                        mentions_count=market_data.get('positive_sentiment', 0) + market_data.get('negative_sentiment', 0),
                        positive_mentions=market_data.get('positive_sentiment', 0),
                        negative_mentions=market_data.get('negative_sentiment', 0),
                        additional_data=market_data
                    )

        # Execute the original task
        result = await super().execute_task(task)

        return result


class StorageIntegratedMarketDataService(MAXXMarketDataService):
    """
    Market data service with storage integration
    """

    async def fetch_market_data(self) -> Dict[str, Any]:
        """
        Fetch market data with storage of results
        """
        # Fetch the original market data
        market_data = await super().fetch_market_data()

        # Store the fetched data in the database
        await storage_manager.store_market_data(
            symbol='MAXX',
            price=market_data.get('current_price', 0),
            volume=market_data.get('volume_24h', 0),
            liquidity=market_data.get('liquidity', 0),
            additional_data=market_data
        )

        return market_data


class StorageIntegratedSocialDataService(MAXXSocialDataService):
    """
    Social data service with storage integration
    """

    async def fetch_social_data(self) -> Dict[str, Any]:
        """
        Fetch social data with storage of results
        """
        # Fetch the original social data
        social_data = await super().fetch_social_data()

        # Store the social sentiment in the database
        await storage_manager.store_social_sentiment(
            symbol='MAXX',
            sentiment_score=social_data['sentiment_score'],
            mentions_count=social_data['mentions_24h'],
            positive_mentions=social_data['positive_mentions'],
            negative_mentions=social_data['negative_mentions'],
            additional_data=social_data
        )

        return social_data


# Real storage integration utilities - no demo functions
# Use StorageIntegratedMAXXTokenBot, StorageIntegratedMAXXTokenAgent,
# StorageIntegratedMarketDataService, and StorageIntegratedSocialDataService directly