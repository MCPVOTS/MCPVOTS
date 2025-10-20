"""
Main execution script for the MAXX token trading agent
"""
import asyncio
import os
import logging
from typing import Dict, Any

from MAXX_token_agent import MAXXTokenAgent, MAXXTokenBot
from maxx_network_utils import MAXXMarketDataFeed, MAXXSocialSentimentFeed, MAXXNotificationService
from config import Config


class MAXXTokenSystem:
    """
    Main system class that orchestrates the MAXX token trading agent
    """

    def __init__(self, private_key: str = None):
        self.private_key = private_key
        self.agent = MAXXTokenAgent()
        self.market_feed = MAXXMarketDataFeed()
        self.sentiment_feed = MAXXSocialSentimentFeed()
        self.notification_service = MAXXNotificationService(
            webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "")
        )
        self.running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """
        Initialize the entire MAXX token system
        """
        self.logger.info("Initializing MAXX Token Trading System...")

        try:
            # Initialize the bot with private key if provided
            if self.private_key:
                self.agent.maxx_bot = MAXXTokenBot(
                    account_private_key=self.private_key
                )

            # Initialize the bot
            await self.agent.maxx_bot.initialize()

            # Connect to data feeds
            await self.market_feed.connect()
            await self.sentiment_feed.connect()
            await self.notification_service.connect()

            self.logger.info("MAXX Token Trading System initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing MAXX Token Trading System: {e}")
            raise

    async def run_trading_cycle(self):
        """
        Run a single trading cycle - get data, make decisions, execute trades
        """
        if not self.running:
            return

        self.logger.info("\n--- Starting Trading Cycle ---")

        try:
            # Get market data
            market_data = await self.market_feed.fetch_maxx_data()
            if not market_data:
                self.logger.warning("Failed to get market data, skipping cycle")
                return

            # Get sentiment data
            sentiment_data = await self.sentiment_feed.get_sentiment_data()
            if not sentiment_data:
                self.logger.warning("Failed to get sentiment data, using neutral")
                sentiment_data = {'sentiment_score': 0.5}

            # Combine market and sentiment data for enhanced decision making
            enhanced_market_data = market_data.copy()
            enhanced_market_data['sentiment_score'] = sentiment_data['sentiment_score']
            enhanced_market_data['positive_sentiment'] = sentiment_data.get('positive_mentions', 0)
            enhanced_market_data['negative_sentiment'] = sentiment_data.get('negative_mentions', 0)

            # Execute trading task
            trade_task = {
                'type': 'trade',
                'market_data': enhanced_market_data
            }

            result = await self.agent.execute_task(trade_task)
            orders = result['result']['orders']

            if orders:
                for order in orders:
                    order_type = order['side'].upper()
                    quantity = order['quantity']
                    price = order['price']
                    self.logger.info(f"EXECUTED {order_type} order for {quantity} MAXX at ${price}")

                    # Send notification about the trade
                    await self.notification_service.send_notification(
                        f"Executed {order_type} order for {quantity:.2f} MAXX at ${price:.6f}",
                        "trade"
                    )
            else:
                self.logger.info("No trading signals generated in this cycle")
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")

        self.logger.info("--- Trading Cycle Completed ---\n")

    async def run_monitoring_cycle(self):
        """
        Run a monitoring cycle to track token metrics
        """
        if not self.running:
            return

        self.logger.info("--- Starting Monitoring Cycle ---")

        try:
            # Get token info
            info_task = {
                'type': 'monitor'
            }
            result = await self.agent.execute_task(info_task)

            token_info = result['result']
            self.logger.info(f"MAXX Token Info: {token_info}")

            # Update metrics
            metrics_task = {
                'type': 'update_metrics'
            }
            await self.agent.execute_task(metrics_task)

            # Send notification if significant changes detected
            current_price = token_info.get('current_price', 0)
            if current_price > 0.002:  # Example threshold
                await self.notification_service.send_notification(
                    f"MAXX token price reached significant level: ${current_price:.6f}",
                    "alert"
                )
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")

        self.logger.info("--- Monitoring Cycle Completed ---\n")

    async def start(self):
        """
        Start the MAXX token trading system
        """
        self.logger.info("Starting MAXX Token Trading System...")
        await self.initialize()

        self.running = True
        self.logger.info("MAXX Token Trading System started successfully")

        # Run the system continuously
        cycle_count = 0
        while self.running:
            cycle_count += 1
            self.logger.info(f"\n======= Trading Cycle #{cycle_count} =======")

            # Run trading cycle
            await self.run_trading_cycle()

            # Run monitoring cycle every 5 cycles
            if cycle_count % 5 == 0:
                await self.run_monitoring_cycle()

            # Wait before next cycle
            await asyncio.sleep(30)  # Wait 30 seconds between cycles

    async def stop(self):
        """
        Stop the MAXX token trading system
        """
        self.logger.info("Stopping MAXX Token Trading System...")
        self.running = False


# Real MAXX token trading system - no demo functions
# To use the real trading system:
# 1. Set ETHEREUM_PRIVATE_KEY environment variable
# 2. Set DISCORD_WEBHOOK_URL environment variable (optional)
# 3. Import and use MAXXTokenSystem class directly
#
# Example usage:
# import os
# from main_maxx_agent import MAXXTokenSystem
#
# async def run_real_trading():
#     private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
#     if not private_key:
#         raise ValueError("ETHEREUM_PRIVATE_KEY environment variable must be set")
#
#     system = MAXXTokenSystem(private_key=private_key)
#     await system.start()
#
# Available methods:
# - MAXXTokenSystem.initialize()
# - MAXXTokenSystem.start()
# - MAXXTokenSystem.stop()
# - MAXXTokenSystem.run_trading_cycle()
# - MAXXTokenSystem.run_monitoring_cycle()