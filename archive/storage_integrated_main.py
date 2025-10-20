"""
Updated main execution script for the MAXX token trading agent with storage integration
"""
import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from storage_integration import StorageIntegratedMAXXTokenAgent, StorageIntegratedMarketDataService, StorageIntegratedSocialDataService
from maxx_network_utils import MAXXNotificationService
from config import Config
from db_vector_storage import storage_manager


class StorageIntegratedMAXXTokenSystem:
    """
    Main system class that orchestrates the MAXX token trading agent with storage integration
    """
    
    def __init__(self, private_key: str = None):
        self.private_key = private_key
        self.agent = StorageIntegratedMAXXTokenAgent()
        self.market_service = StorageIntegratedMarketDataService()
        self.sentiment_service = StorageIntegratedSocialDataService()
        self.notification_service = MAXXNotificationService(
            webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "")
        )
        self.running = False
        
    async def initialize(self):
        """
        Initialize the entire MAXX token system with storage
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing Storage-Integrated MAXX Token Trading System...")
        
        # Initialize the bot with private key if provided
        if self.private_key:
            self.agent.maxx_bot = StorageIntegratedMAXXTokenBot(
                account_private_key=self.private_key
            )
        
        # Initialize the bot
        await self.agent.maxx_bot.initialize()
        
        # Connect to data feeds (already integrated with storage)
        await self.notification_service.connect()
        
        self.logger.info("Storage-Integrated MAXX Token Trading System initialized successfully")
        
        # Store system initialization in database
        await storage_manager.store_bot_performance(
            bot_id=self.agent.maxx_bot.bot_id,
            metric_name='system_initialized',
            value=1,
            timestamp=asyncio.get_event_loop().time()
        )
    
    async def run_trading_cycle(self):
        """
        Run a single trading cycle - get data, make decisions, execute trades
        """
        if not self.running:
            return
        
        self.logger.info("\n--- Starting Trading Cycle ---")
        
        # Get market data (automatically stored via integration)
        market_data = await self.market_service.fetch_market_data()
        if not market_data:
            self.logger.warning("Failed to get market data, skipping cycle")
            return
        
        # Get sentiment data (automatically stored via integration)
        sentiment_data = await self.sentiment_service.fetch_social_data()
        if not sentiment_data:
            self.logger.info("Failed to get sentiment data, using neutral")
            sentiment_data = {'sentiment_score': 0.5}
        
        # Combine market and sentiment data for enhanced decision making
        enhanced_market_data = market_data.copy()
        enhanced_market_data['sentiment_score'] = sentiment_data['sentiment_score']
        enhanced_market_data['positive_sentiment'] = sentiment_data['positive_mentions']
        enhanced_market_data['negative_sentiment'] = sentiment_data['negative_mentions']
        
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
                
                # Store the completed trade in the database through the agent integration
                await storage_manager.store_trade(
                    bot_id=self.agent.maxx_bot.bot_id,
                    symbol=order['symbol'],
                    side=order['side'],
                    quantity=order['quantity'],
                    price=order['price'],
                    strategy=order['strategy'],
                    timestamp=order.get('timestamp', asyncio.get_event_loop().time())
                )
        else:
            self.logger.info("No trading signals generated in this cycle")
        
        # Store the market vector for analysis
        await self.agent.maxx_bot.store_market_vector(enhanced_market_data)
        
        self.logger.info("--- Trading Cycle Completed ---\n")
    
    async def run_monitoring_cycle(self):
        """
        Run a monitoring cycle to track token metrics
        """
        if not self.running:
            return
        
        self.logger.info("--- Starting Monitoring Cycle ---")
        
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
        
        # Store performance metrics
        await storage_manager.store_bot_performance(
            bot_id=self.agent.maxx_bot.bot_id,
            metric_name='current_price',
            value=current_price,
            timestamp=asyncio.get_event_loop().time()
        )
        
        self.logger.info("--- Monitoring Cycle Completed ---\n")
    
    async def run_analysis_cycle(self):
        """
        Run an analysis cycle to look for patterns in stored data
        """
        if not self.running:
            return
        
        print("--- Starting Analysis Cycle ---")
        
        # Get recent market data
        recent_data = await storage_manager.get_recent_market_data('MAXX', limit=100)
        if len(recent_data) < 10:
            print("Not enough data for analysis yet")
            return
        
        # Perform basic analysis
        prices = [item['price'] for item in recent_data]
        avg_price = sum(prices) / len(prices)
        current_price = prices[0]  # Most recent price
        price_volatility = max(prices) - min(prices)
        
        print(f"Market Analysis - Avg Price: ${avg_price:.6f}, Volatility: ${price_volatility:.6f}")
        
        # Look for similar market conditions in the vector store
        current_conditions = recent_data[0]
        if 'additional_data' in current_conditions and current_conditions['additional_data']:
            additional_data = current_conditions['additional_data']
            # Create a simple vector for similarity search
            vector_data = [
                current_conditions.get('price', 0),
                current_conditions.get('volume', 0) or 0,
                current_conditions.get('liquidity', 0) or 0,
                additional_data.get('holders', 0) if isinstance(additional_data, dict) else 0,
                additional_data.get('sentiment_score', 0.5) if isinstance(additional_data, dict) else 0.5
            ]
            
            try:
                import numpy as np
                query_vector = np.array([float(x) if x is not None else 0.0 for x in vector_data])
            except ImportError:
                # Fallback if numpy is not available
                query_vector = [float(x) if x is not None else 0.0 for x in vector_data]
                self.logger.warning("NumPy not available, using list instead of numpy array")
            
            similar_markets = await storage_manager.find_similar_markets(query_vector, top_k=3)
            if similar_markets:
                self.logger.info(f"Found {len(similar_markets)} similar market conditions in history:")
                for market_id, similarity in similar_markets:
                    self.logger.info(f"  - {market_id}: {similarity:.3f} similarity")
        
        # Store analysis results
        await storage_manager.store_bot_performance(
            bot_id=self.agent.maxx_bot.bot_id,
            metric_name='avg_price_100_intervals',
            value=avg_price,
            timestamp=asyncio.get_event_loop().time()
        )
        
        await storage_manager.store_bot_performance(
            bot_id=self.agent.maxx_bot.bot_id,
            metric_name='price_volatility',
            value=price_volatility,
            timestamp=asyncio.get_event_loop().time()
        )
        
        print("--- Analysis Cycle Completed ---\n")
    
    async def start(self):
        """
        Start the MAXX token trading system
        """
        self.logger.info("Starting Storage-Integrated MAXX Token Trading System...")
        await self.initialize()
        
        self.running = True
        
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
            
            # Run analysis cycle every 10 cycles
            if cycle_count % 10 == 0:
                await self.run_analysis_cycle()
            
            # Wait before next cycle
            await asyncio.sleep(Config.TRADING_CYCLE_INTERVAL)  # Configurable interval
    
    async def stop(self):
        """
        Stop the MAXX token trading system
        """
        self.logger.info("Stopping MAXX Token Trading System...")
        self.running = False
        
        # Store system shutdown in database
        await storage_manager.store_bot_performance(
            bot_id=self.agent.maxx_bot.bot_id,
            metric_name='system_shutdown',
            value=1,
            timestamp=asyncio.get_event_loop().time()
        )


async def main():
    """
    Main function to run the MAXX token trading system
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Get private key from environment variable or use the provided one
    private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
    if not private_key:
        logger.warning("No private key found in environment variable.")
        logger.info("Using the default private key for testing purposes.")
        # For security reasons, in a real implementation you should never hardcode private keys
        # The following line should only be used for testing
        private_key = "0x21d095de57588dce6233047a0d558df9c6d032750331f657a1ec58d07a678432"
        logger.warning("WARNING: Private key hardcoded in script. For production use, set ETHEREUM_PRIVATE_KEY environment variable.")
    
    else:
        logger.info("Using private key from environment variable.")
    
    # Create and start the system
    system = StorageIntegratedMAXXTokenSystem(private_key=private_key)
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received. Shutting down...")
    finally:
        await system.stop()
        logger.info("MAXX Token Trading System shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())