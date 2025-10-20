"""
Base bot implementation for the autonomous bot system.
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import logging
import time


class BotStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class TradingSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class BaseBot(ABC):
    """
    Abstract base class for all trading bots in the system.
    """
    
    def __init__(self, bot_id: Optional[str] = None, name: str = "BaseBot", **kwargs):
        self.bot_id = bot_id or str(uuid.uuid4())
        self.name = name
        self.status = BotStatus.STOPPED
        self.created_at = time.time()
        self.last_updated = time.time()
        self.metadata = kwargs
        self.balance = 0.0
        self.positions = {}
        self.logger = logging.getLogger(self.name)
        self.strategy_params = {}
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0
        }
    
    @abstractmethod
    async def initialize(self):
        """
        Initialize the bot before starting.
        """
        pass
    
    @abstractmethod
    async def execute_strategy(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the trading strategy based on market data.
        
        Args:
            market_data: Current market data
            
        Returns:
            List of orders to execute
        """
        pass
    
    @abstractmethod
    async def calculate_indicators(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate technical indicators for trading decisions.
        
        Args:
            data: Historical market data
            
        Returns:
            Dictionary of calculated indicators
        """
        pass
    
    @abstractmethod
    async def manage_risk(self, position: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """
        Apply risk management to position.
        
        Args:
            position: Current position
            market_data: Market data
            
        Returns:
            True if risk is acceptable, False otherwise
        """
        pass
    
    async def start(self):
        """
        Start the bot.
        """
        self.status = BotStatus.STARTING
        await self.initialize()
        self.status = BotStatus.RUNNING
        self.logger.info(f"Bot {self.name} started with ID {self.bot_id}")
    
    async def stop(self):
        """
        Stop the bot.
        """
        self.status = BotStatus.STOPPED
        self.logger.info(f"Bot {self.name} stopped")
    
    async def pause(self):
        """
        Pause the bot.
        """
        self.status = BotStatus.PAUSED
        self.logger.info(f"Bot {self.name} paused")
    
    async def resume(self):
        """
        Resume the bot.
        """
        if self.status == BotStatus.PAUSED:
            self.status = BotStatus.RUNNING
            self.logger.info(f"Bot {self.name} resumed")
    
    async def update_balance(self, amount: float):
        """
        Update the bot's balance.
        
        Args:
            amount: Amount to add to balance (can be negative)
        """
        self.balance += amount
        self.last_updated = time.time()
    
    async def update_position(self, symbol: str, quantity: float, price: float, side: TradingSide):
        """
        Update a position for a symbol.
        
        Args:
            symbol: Trading symbol
            quantity: Quantity of the position
            price: Price at which position was opened
            side: Side of the trade (buy/sell)
        """
        self.positions[symbol] = {
            "quantity": quantity,
            "price": price,
            "side": side,
            "timestamp": time.time()
        }
        self.last_updated = time.time()
    
    async def close_position(self, symbol: str) -> float:
        """
        Close a position and return PnL.
        
        Args:
            symbol: Symbol to close position for
            
        Returns:
            Profit or loss from the trade
        """
        if symbol not in self.positions:
            return 0.0
            
        position = self.positions[symbol]
        # Placeholder for current market price - this would come from market data
        current_price = 0.0  # Should be replaced with actual market price
        pnl = (current_price - position["price"]) * position["quantity"]
        
        # Update performance metrics
        self.performance_metrics["total_trades"] += 1
        self.performance_metrics["total_pnl"] += pnl
        if pnl > 0:
            self.performance_metrics["winning_trades"] += 1
            
        if self.performance_metrics["total_trades"] > 0:
            self.performance_metrics["win_rate"] = (
                self.performance_metrics["winning_trades"] / 
                self.performance_metrics["total_trades"]
            )
        
        del self.positions[symbol]
        self.last_updated = time.time()
        
        return pnl
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the bot.
        
        Returns:
            Dictionary of performance metrics
        """
        return self.performance_metrics.copy()
    
    async def set_strategy_param(self, key: str, value: Any):
        """
        Set a strategy parameter.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        self.strategy_params[key] = value
    
    async def get_strategy_param(self, key: str) -> Any:
        """
        Get a strategy parameter.
        
        Args:
            key: Parameter name
            
        Returns:
            Parameter value or None if not found
        """
        return self.strategy_params.get(key)


class BotManager:
    """
    Manages multiple bots, their lifecycle and coordination.
    """
    
    def __init__(self):
        self.bots: Dict[str, BaseBot] = {}
        self.logger = logging.getLogger("BotManager")
    
    async def register_bot(self, bot: BaseBot) -> str:
        """
        Register a bot with the manager.
        
        Args:
            bot: Bot to register
            
        Returns:
            Bot ID
        """
        self.bots[bot.bot_id] = bot
        self.logger.info(f"Registered bot {bot.name} with ID {bot.bot_id}")
        return bot.bot_id
    
    async def get_bot(self, bot_id: str) -> Optional[BaseBot]:
        """
        Get a bot by ID.
        
        Args:
            bot_id: ID of the bot to retrieve
            
        Returns:
            Bot instance or None if not found
        """
        return self.bots.get(bot_id)
    
    async def remove_bot(self, bot_id: str):
        """
        Remove a bot from management.
        
        Args:
            bot_id: ID of the bot to remove
        """
        if bot_id in self.bots:
            bot = self.bots[bot_id]
            if bot.status == BotStatus.RUNNING:
                await bot.stop()
            del self.bots[bot_id]
            self.logger.info(f"Removed bot with ID {bot_id}")
    
    async def start_all_bots(self):
        """
        Start all registered bots.
        """
        for bot_id, bot in self.bots.items():
            if bot.status != BotStatus.RUNNING:
                await bot.start()
    
    async def stop_all_bots(self):
        """
        Stop all registered bots.
        """
        for bot_id, bot in self.bots.items():
            if bot.status in [BotStatus.RUNNING, BotStatus.STARTING, BotStatus.PAUSED]:
                await bot.stop()
    
    async def get_all_bot_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for all bots.
        
        Returns:
            Dictionary mapping bot ID to its performance metrics
        """
        performance = {}
        for bot_id, bot in self.bots.items():
            performance[bot_id] = await bot.get_performance_metrics()
        return performance