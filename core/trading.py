"""
Advanced Trading System for MAXX Ecosystem
Provides trading strategies, order management, and portfolio analytics
"""
import asyncio
import time
import math
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import json
from decimal import Decimal, getcontext

from .config import get_trading_config
from .logging import get_logger, log_performance
from .database import get_database_manager
from .network import get_network_manager

# Set decimal precision for financial calculations
getcontext().prec = 28


class OrderSide(Enum):
    """Order side types"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(Enum):
    """Order status types"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class StrategyType(Enum):
    """Trading strategy types"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    GRID = "grid"
    DCA = "dca"
    SCALPING = "scalping"
    SWING = "swing"


class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class TradingPair:
    """Trading pair information"""
    symbol: str
    base_asset: str
    quote_asset: str
    min_quantity: Decimal
    max_quantity: Decimal
    quantity_precision: int
    price_precision: int
    min_notional: Decimal
    is_active: bool = True


@dataclass
class Price:
    """Price information"""
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    volume: Decimal
    timestamp: float
    exchange: str


@dataclass
class Order:
    """Trading order"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    exchange_order_id: Optional[str] = None
    fees: Decimal = Decimal('0')
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Convert string values to Decimal if needed
        if isinstance(self.quantity, str):
            self.quantity = Decimal(self.quantity)
        if self.price and isinstance(self.price, str):
            self.price = Decimal(self.price)
        if self.stop_price and isinstance(self.stop_price, str):
            self.stop_price = Decimal(self.stop_price)
        if isinstance(self.filled_quantity, str):
            self.filled_quantity = Decimal(self.filled_quantity)
        if self.fees and isinstance(self.fees, str):
            self.fees = Decimal(self.fees)

    @property
    def remaining_quantity(self) -> Decimal:
        """Get remaining quantity to fill"""
        return self.quantity - self.filled_quantity

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.filled_quantity >= self.quantity

    @property
    def is_active(self) -> bool:
        """Check if order is still active"""
        return self.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]


@dataclass
class Position:
    """Trading position"""
    symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Decimal = Decimal('0')
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self):
        # Convert string values to Decimal if needed
        if isinstance(self.quantity, str):
            self.quantity = Decimal(self.quantity)
        if isinstance(self.average_price, str):
            self.average_price = Decimal(self.average_price)
        if isinstance(self.current_price, str):
            self.current_price = Decimal(self.current_price)

    def update_unrealized_pnl(self):
        """Update unrealized PnL based on current price"""
        if self.quantity != 0:
            self.unrealized_pnl = (self.current_price - self.average_price) * self.quantity

    @property
    def market_value(self) -> Decimal:
        """Get market value of position"""
        return abs(self.quantity) * self.current_price

    @property
    def is_long(self) -> bool:
        """Check if position is long"""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if position is short"""
        return self.quantity < 0


@dataclass
class Portfolio:
    """Trading portfolio"""
    balance: Dict[str, Decimal] = field(default_factory=dict)
    positions: Dict[str, Position] = field(default_factory=dict)
    total_value: Decimal = Decimal('0')
    total_pnl: Decimal = Decimal('0')
    updated_at: float = field(default_factory=time.time)

    def update_total_value(self, prices: Dict[str, Decimal]):
        """Update total portfolio value"""
        total = Decimal('0')

        # Add cash balances
        for asset, balance in self.balance.items():
            if asset in prices:
                total += balance * prices[asset]

        # Add position values
        for position in self.positions.values():
            if position.symbol in prices:
                position.current_price = prices[position.symbol]
                position.update_unrealized_pnl()
                total += position.market_value

        self.total_value = total
        self.updated_at = time.time()


class RiskManager:
    """Risk management system"""

    def __init__(self):
        self.config = get_trading_config()
        self.logger = get_logger(self.__class__.__name__)
        self.daily_pnl_limit = Decimal(str(self.config.daily_pnl_limit))
        self.max_position_size = Decimal(str(self.config.max_position_size))
        self.max_leverage = Decimal(str(self.config.max_leverage))
        self.stop_loss_pct = Decimal(str(self.config.stop_loss_percentage))

    def check_order_risk(self, order: Order, portfolio: Portfolio,
                        current_price: Decimal) -> Tuple[bool, str]:
        """Check if order passes risk checks"""
        try:
            # Check position size limit
            current_position = portfolio.positions.get(order.symbol,
                                                      Position(order.symbol, Decimal('0'),
                                                              Decimal('0'), current_price))

            new_quantity = current_position.quantity
            if order.side == OrderSide.BUY:
                new_quantity += order.quantity
            else:
                new_quantity -= order.quantity

            if abs(new_quantity * current_price) > self.max_position_size:
                return False, f"Position size exceeds limit: {self.max_position_size}"

            # Check leverage
            total_value = portfolio.total_value
            if total_value > 0:
                position_value = abs(new_quantity * current_price)
                leverage = position_value / total_value

                if leverage > self.max_leverage:
                    return False, f"Leverage exceeds limit: {self.max_leverage}"

            # Check daily PnL limit
            if portfolio.total_pnl < -self.daily_pnl_limit:
                return False, f"Daily PnL limit reached: {self.daily_pnl_limit}"

            return True, "Risk check passed"

        except Exception as e:
            self.logger.error(f"Risk check error: {e}")
            return False, f"Risk check error: {e}"

    def calculate_position_size(self, symbol: str, current_price: Decimal,
                              portfolio: Portfolio, risk_level: RiskLevel) -> Decimal:
        """Calculate optimal position size based on risk"""
        try:
            # Base position size on portfolio value and risk level
            risk_multipliers = {
                RiskLevel.LOW: Decimal('0.1'),
                RiskLevel.MEDIUM: Decimal('0.25'),
                RiskLevel.HIGH: Decimal('0.5'),
                RiskLevel.EXTREME: Decimal('1.0')
            }

            risk_multiplier = risk_multipliers.get(risk_level, Decimal('0.25'))
            base_size = portfolio.total_value * risk_multiplier

            # Apply stop loss to calculate position size
            if self.stop_loss_pct > 0:
                max_loss_per_share = current_price * self.stop_loss_pct
                if max_loss_per_share > 0:
                    position_size = base_size / max_loss_per_share
                else:
                    position_size = base_size / current_price
            else:
                position_size = base_size / current_price

            # Apply maximum position size limit
            max_shares = self.max_position_size / current_price
            position_size = min(position_size, max_shares)

            return position_size

        except Exception as e:
            self.logger.error(f"Position size calculation error: {e}")
            return Decimal('0')


class OrderManager:
    """Order management system"""

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.active_orders: Dict[str, Order] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.risk_manager = RiskManager()
        self.order_counter = 0

    def generate_order_id(self) -> str:
        """Generate unique order ID"""
        self.order_counter += 1
        timestamp = int(time.time() * 1000)
        return f"ORDER_{timestamp}_{self.order_counter}"

    @log_performance("order.create")
    async def create_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                          quantity: Union[Decimal, str], price: Optional[Union[Decimal, str]] = None,
                          stop_price: Optional[Union[Decimal, str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Order:
        """Create a new order"""
        order_id = self.generate_order_id()

        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)) if price else None,
            stop_price=Decimal(str(stop_price)) if stop_price else None,
            metadata=metadata or {}
        )

        self.orders[order_id] = order
        self.active_orders[order_id] = order

        self.logger.info(f"Created order: {order_id} {side.value} {quantity} {symbol}")
        return order

    async def submit_order(self, order: Order, portfolio: Portfolio,
                          current_price: Decimal) -> Tuple[bool, str]:
        """Submit order to exchange"""
        try:
            # Risk check
            risk_passed, risk_message = self.risk_manager.check_order_risk(
                order, portfolio, current_price
            )

            if not risk_passed:
                order.status = OrderStatus.REJECTED
                return False, risk_message

            # Submit to exchange (simulated)
            order.status = OrderStatus.SUBMITTED
            order.updated_at = time.time()

            self.logger.info(f"Submitted order: {order.id}")
            return True, "Order submitted successfully"

        except Exception as e:
            self.logger.error(f"Order submission error: {e}")
            order.status = OrderStatus.REJECTED
            return False, f"Submission error: {e}"

    async def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Cancel an order"""
        order = self.orders.get(order_id)
        if not order:
            return False, "Order not found"

        if not order.is_active:
            return False, f"Cannot cancel order with status: {order.status.value}"

        try:
            # Cancel on exchange (simulated)
            order.status = OrderStatus.CANCELLED
            order.updated_at = time.time()

            # Remove from active orders
            self.active_orders.pop(order_id, None)

            self.logger.info(f"Cancelled order: {order_id}")
            return True, "Order cancelled successfully"

        except Exception as e:
            self.logger.error(f"Order cancellation error: {e}")
            return False, f"Cancellation error: {e}"

    def update_order_status(self, order_id: str, status: OrderStatus,
                          filled_quantity: Optional[Decimal] = None,
                          average_price: Optional[Decimal] = None):
        """Update order status"""
        order = self.orders.get(order_id)
        if not order:
            return

        order.status = status
        order.updated_at = time.time()

        if filled_quantity is not None:
            order.filled_quantity = filled_quantity

        if average_price is not None:
            order.average_price = average_price

        # Remove from active orders if no longer active
        if not order.is_active:
            self.active_orders.pop(order_id, None)

        self.logger.debug(f"Updated order {order_id} status to {status.value}")

    def get_active_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get active orders"""
        orders = list(self.active_orders.values())

        if symbol:
            orders = [o for o in orders if o.symbol == symbol]

        return orders

    def get_order_history(self, symbol: Optional[str] = None,
                         limit: int = 100) -> List[Order]:
        """Get order history"""
        orders = list(self.orders.values())

        if symbol:
            orders = [o for o in orders if o.symbol == symbol]

        # Sort by creation time (newest first)
        orders.sort(key=lambda o: o.created_at, reverse=True)

        return orders[:limit]


class TradingStrategy:
    """Base trading strategy"""

    def __init__(self, name: str, strategy_type: StrategyType):
        self.name = name
        self.strategy_type = strategy_type
        self.logger = get_logger(self.__class__.__name__)
        self.is_active = False
        self.positions: Dict[str, Position] = {}
        self.indicators: Dict[str, Any] = {}
        self.last_update = 0

    async def initialize(self):
        """Initialize strategy"""
        self.is_active = True
        self.logger.info(f"Initialized strategy: {self.name}")

    async def analyze(self, prices: Dict[str, Price],
                     portfolio: Portfolio) -> Dict[str, Any]:
        """Analyze market conditions and generate signals"""
        raise NotImplementedError("Subclasses must implement analyze method")

    async def execute_signals(self, signals: Dict[str, Any],
                            order_manager: OrderManager,
                            portfolio: Portfolio) -> List[Order]:
        """Execute trading signals"""
        raise NotImplementedError("Subclasses must implement execute_signals method")

    async def update_indicators(self, prices: Dict[str, Price]):
        """Update technical indicators"""
        raise NotImplementedError("Subclasses must implement update_indicators method")

    async def cleanup(self):
        """Cleanup strategy resources"""
        self.is_active = False
        self.logger.info(f"Cleaned up strategy: {self.name}")


class MomentumStrategy(TradingStrategy):
    """Momentum trading strategy"""

    def __init__(self, name: str = "Momentum", lookback_period: int = 20,
                 momentum_threshold: float = 0.02):
        super().__init__(name, StrategyType.MOMENTUM)
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        self.price_history: Dict[str, List[float]] = {}

    async def analyze(self, prices: Dict[str, Price],
                     portfolio: Portfolio) -> Dict[str, Any]:
        """Analyze momentum for all symbols"""
        signals = {}

        for symbol, price in prices.items():
            if symbol not in self.price_history:
                self.price_history[symbol] = []

            # Update price history
            self.price_history[symbol].append(float(price.last))

            # Keep only lookback period
            if len(self.price_history[symbol]) > self.lookback_period:
                self.price_history[symbol] = self.price_history[symbol][-self.lookback_period:]

            # Calculate momentum
            if len(self.price_history[symbol]) >= self.lookback_period:
                current_price = self.price_history[symbol][-1]
                old_price = self.price_history[symbol][0]
                momentum = (current_price - old_price) / old_price

                # Generate signal
                if momentum > self.momentum_threshold:
                    signals[symbol] = {
                        'action': 'buy',
                        'strength': min(abs(momentum) / self.momentum_threshold, 3.0),
                        'momentum': momentum
                    }
                elif momentum < -self.momentum_threshold:
                    signals[symbol] = {
                        'action': 'sell',
                        'strength': min(abs(momentum) / self.momentum_threshold, 3.0),
                        'momentum': momentum
                    }

        return signals

    async def execute_signals(self, signals: Dict[str, Any],
                            order_manager: OrderManager,
                            portfolio: Portfolio) -> List[Order]:
        """Execute momentum signals"""
        orders = []

        for symbol, signal in signals.items():
            try:
                action = signal['action']
                strength = signal['strength']

                # Calculate position size based on signal strength
                base_quantity = Decimal('0.1') * Decimal(str(strength))

                if action == 'buy':
                    order = await order_manager.create_order(
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=base_quantity,
                        metadata={'strategy': self.name, 'signal': signal}
                    )
                    orders.append(order)

                elif action == 'sell':
                    # Check if we have position to sell
                    position = portfolio.positions.get(symbol)
                    if position and position.quantity > 0:
                        quantity = min(base_quantity, position.quantity)
                        order = await order_manager.create_order(
                            symbol=symbol,
                            side=OrderSide.SELL,
                            order_type=OrderType.MARKET,
                            quantity=quantity,
                            metadata={'strategy': self.name, 'signal': signal}
                        )
                        orders.append(order)

            except Exception as e:
                self.logger.error(f"Error executing signal for {symbol}: {e}")

        return orders

    async def update_indicators(self, prices: Dict[str, Price]):
        """Update momentum indicators"""
        # Momentum is calculated in analyze method
        pass


class TradingEngine:
    """Main trading engine"""

    def __init__(self):
        self.config = get_trading_config()
        self.logger = get_logger(self.__class__.__name__)
        self.order_manager = OrderManager()
        self.portfolio = Portfolio()
        self.strategies: List[TradingStrategy] = []
        self.is_running = False
        self.prices: Dict[str, Price] = {}
        self.trading_pairs: Dict[str, TradingPair] = {}

        # Initialize default strategy
        self.strategies.append(MomentumStrategy())

    async def initialize(self):
        """Initialize trading engine"""
        # Initialize strategies
        for strategy in self.strategies:
            await strategy.initialize()

        self.is_running = True
        self.logger.info("Trading engine initialized")

    async def start(self):
        """Start trading engine"""
        if not self.is_running:
            await self.initialize()

        self.logger.info("Starting trading engine...")

        # Main trading loop
        while self.is_running:
            try:
                await self.trading_loop()
                await asyncio.sleep(self.config.trading_interval)

            except Exception as e:
                self.logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop trading engine"""
        self.is_running = False

        # Cancel all active orders
        for order_id in list(self.order_manager.active_orders.keys()):
            await self.order_manager.cancel_order(order_id)

        # Cleanup strategies
        for strategy in self.strategies:
            await strategy.cleanup()

        self.logger.info("Trading engine stopped")

    async def trading_loop(self):
        """Main trading loop"""
        # Update prices
        await self.update_prices()

        # Update portfolio
        price_dict = {symbol: price.last for symbol, price in self.prices.items()}
        self.portfolio.update_total_value(price_dict)

        # Run strategies
        for strategy in self.strategies:
            if not strategy.is_active:
                continue

            try:
                # Update indicators
                await strategy.update_indicators(self.prices)

                # Analyze market
                signals = await strategy.analyze(self.prices, self.portfolio)

                # Execute signals
                if signals:
                    orders = await strategy.execute_signals(
                        signals, self.order_manager, self.portfolio
                    )

                    # Submit orders
                    for order in orders:
                        current_price = self.prices.get(order.symbol)
                        if current_price:
                            success, message = await self.order_manager.submit_order(
                                order, self.portfolio, current_price.last
                            )
                            if not success:
                                self.logger.warning(f"Order submission failed: {message}")

            except Exception as e:
                self.logger.error(f"Strategy {strategy.name} error: {e}")

    async def update_prices(self):
        """Update price data"""
        # This would connect to real price feeds
        # For now, simulate price updates
        for symbol in self.trading_pairs.keys():
            if symbol not in self.prices:
                self.prices[symbol] = Price(
                    symbol=symbol,
                    bid=Decimal('100'),
                    ask=Decimal('101'),
                    last=Decimal('100.5'),
                    volume=Decimal('1000'),
                    timestamp=time.time(),
                    exchange='simulated'
                )
            else:
                # Simulate price movement
                current_price = self.prices[symbol].last
                change = Decimal(str((math.random() - 0.5) * 2))  # -1 to 1
                new_price = current_price * (Decimal('1') + change * Decimal('0.01'))

                self.prices[symbol].bid = new_price * Decimal('0.995')
                self.prices[symbol].ask = new_price * Decimal('1.005')
                self.prices[symbol].last = new_price
                self.prices[symbol].timestamp = time.time()

    def add_strategy(self, strategy: TradingStrategy):
        """Add trading strategy"""
        self.strategies.append(strategy)
        self.logger.info(f"Added strategy: {strategy.name}")

    def remove_strategy(self, strategy_name: str):
        """Remove trading strategy"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        self.logger.info(f"Removed strategy: {strategy_name}")

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        return {
            'total_value': float(self.portfolio.total_value),
            'total_pnl': float(self.portfolio.total_pnl),
            'balance': {k: float(v) for k, v in self.portfolio.balance.items()},
            'positions': {k: asdict(v) for k, v in self.portfolio.positions.items()},
            'active_orders': len(self.order_manager.active_orders),
            'total_orders': len(self.order_manager.orders)
        }


# Global trading engine
_trading_engine: Optional[TradingEngine] = None


async def get_trading_engine() -> TradingEngine:
    """Get global trading engine instance"""
    global _trading_engine

    if _trading_engine is None:
        _trading_engine = TradingEngine()
        await _trading_engine.initialize()

    return _trading_engine


async def close_trading_engine():
    """Close global trading engine"""
    global _trading_engine

    if _trading_engine:
        await _trading_engine.stop()
        _trading_engine = None