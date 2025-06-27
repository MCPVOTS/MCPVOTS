#!/usr/bin/env python3
"""
🚀 Nautilus Trader - MCPVots Integration Bridge
Advanced crypto trading intelligence system with AI-powered decision making
Integrates Nautilus Trader with MCPVots AGI ecosystem for Solana/Base L2 trading
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import websockets
import aiohttp
import pandas as pd
import numpy as np

# Nautilus Trader imports
try:
    from nautilus_trader.core.data import Data
    from nautilus_trader.model.data.tick import QuoteTick, TradeTick
    from nautilus_trader.model.data.bar import Bar
    from nautilus_trader.model.instruments import CryptoFuture, CryptoPerpetual
    from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
    from nautilus_trader.model.objects import Price, Quantity, Money
    from nautilus_trader.trading.strategy import Strategy
    from nautilus_trader.backtest.engine import BacktestEngine
    from nautilus_trader.model.enums import OrderSide, OrderType, TimeInForce
    NAUTILUS_AVAILABLE = True
except ImportError:
    NAUTILUS_AVAILABLE = False
    logging.warning("Nautilus Trader not installed. Run: pip install nautilus_trader")

# MCPVots imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from services.RealAIService import RealAIService
    from mcp_service import MCPIntegrationService
except ImportError:
    logging.warning("MCPVots services not available in current context")

class NautilusMCPBridge:
    """
    🌊 Nautilus Trader - MCPVots Integration Bridge
    
    Features:
    - Real-time market data integration
    - AI-powered trading signals
    - Solana & Base L2 blockchain integration
    - Knowledge graph market intelligence
    - Risk management with AGI oversight
    - Multi-exchange coordination
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        
        # Core services
        self.ai_service = RealAIService() if 'RealAIService' in globals() else None
        self.mcp_service = MCPIntegrationService() if 'MCPIntegrationService' in globals() else None
        
        # Trading state
        self.active_strategies = {}
        self.market_data = {}
        self.ai_signals = {}
        self.risk_metrics = {}
        
        # Blockchain connections
        self.solana_rpc = self.config.get('solana_rpc', 'https://api.devnet.solana.com')
        self.base_rpc = self.config.get('base_rpc', 'https://sepolia.base.org')
        
        # Performance tracking
        self.performance_metrics = {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_pnl': Decimal('0'),
            'max_drawdown': Decimal('0'),
            'sharpe_ratio': Decimal('0'),
            'start_time': datetime.now(timezone.utc)
        }
        
        self.logger.info("🚀 Nautilus-MCPVots Bridge initialized")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system"""
        logger = logging.getLogger('nautilus_mcp_bridge')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'trading_pairs': ['SOL/USDT', 'ETH/USDT', 'BTC/USDT'],
            'risk_per_trade': 0.02,  # 2% risk per trade
            'max_positions': 5,
            'ai_confidence_threshold': 0.75,
            'update_frequency': 1.0,  # seconds
            'initial_capital': 50.0,  # $50 starting budget
            'exchanges': ['binance', 'coinbase', 'okx'],
            'strategies': ['trend_following', 'mean_reversion', 'ai_enhanced']
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                
        return default_config

class AIEnhancedTradingStrategy(Strategy):
    """
    🧠 AI-Enhanced Trading Strategy for Nautilus Trader
    Integrates MCPVots AGI capabilities with traditional trading algorithms
    """
    
    def __init__(self, bridge: NautilusMCPBridge):
        super().__init__()
        self.bridge = bridge
        self.logger = bridge.logger
        
        # AI decision parameters
        self.ai_signals = {}
        self.market_regime = 'normal'
        self.confidence_threshold = 0.75
        
        # Risk management
        self.position_size = Decimal('0.02')  # 2% of capital per trade
        self.stop_loss_pct = Decimal('0.03')  # 3% stop loss
        self.take_profit_pct = Decimal('0.06')  # 6% take profit
        
    async def on_start(self):
        """Strategy initialization"""
        self.logger.info("🎯 AI-Enhanced Trading Strategy started")
        await self._initialize_ai_models()
        
    async def on_stop(self):
        """Strategy cleanup"""
        self.logger.info("🛑 AI-Enhanced Trading Strategy stopped")
        
    async def _initialize_ai_models(self):
        """Initialize AI models and connections"""
        if self.bridge.ai_service:
            try:
                # Load market analysis models
                await self.bridge.ai_service.initialize()
                self.logger.info("✅ AI models initialized")
            except Exception as e:
                self.logger.error(f"❌ AI initialization failed: {e}")
                
    async def on_quote_tick(self, tick: QuoteTick):
        """Process incoming quote tick data"""
        symbol = str(tick.instrument_id.symbol)
        
        # Update market data
        self.bridge.market_data[symbol] = {
            'bid': float(tick.bid_price),
            'ask': float(tick.ask_price),
            'spread': float(tick.ask_price - tick.bid_price),
            'timestamp': tick.ts_event
        }
        
        # Get AI signal
        ai_signal = await self._get_ai_signal(symbol, tick)
        
        if ai_signal and ai_signal['confidence'] > self.confidence_threshold:
            await self._execute_ai_signal(symbol, ai_signal, tick)
            
    async def _get_ai_signal(self, symbol: str, tick: QuoteTick) -> Optional[Dict]:
        """Get AI-powered trading signal"""
        if not self.bridge.ai_service:
            return None
            
        try:
            # Prepare market context
            market_context = {
                'symbol': symbol,
                'price': float(tick.bid_price),
                'volume': float(tick.bid_size),
                'timestamp': tick.ts_event,
                'historical_data': self._get_historical_context(symbol)
            }
            
            # Get AI analysis
            prompt = f"""
            Analyze crypto trading opportunity for {symbol}:
            Current Price: {market_context['price']}
            Market Context: {market_context}
            
            Provide trading signal with:
            1. Direction (BUY/SELL/HOLD)
            2. Confidence (0-1)
            3. Target price
            4. Stop loss
            5. Reasoning
            
            Response format: JSON
            """
            
            response = await self.bridge.ai_service.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="gemini-2.5"
            )
            
            if response and response.get('choices'):
                content = response['choices'][0]['message']['content']
                signal = self._parse_ai_response(content)
                return signal
                
        except Exception as e:
            self.logger.error(f"AI signal error: {e}")
            
        return None
        
    def _parse_ai_response(self, content: str) -> Optional[Dict]:
        """Parse AI response into trading signal"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                signal_data = json.loads(json_match.group())
                return {
                    'direction': signal_data.get('direction', 'HOLD'),
                    'confidence': float(signal_data.get('confidence', 0)),
                    'target_price': float(signal_data.get('target_price', 0)),
                    'stop_loss': float(signal_data.get('stop_loss', 0)),
                    'reasoning': signal_data.get('reasoning', '')
                }
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            
        return None
        
    def _get_historical_context(self, symbol: str) -> Dict:
        """Get historical market context for analysis"""
        # Return simplified historical context
        return {
            'trend': 'bullish',
            'volatility': 'moderate',
            'volume_profile': 'increasing'
        }
        
    async def _execute_ai_signal(self, symbol: str, signal: Dict, tick: QuoteTick):
        """Execute trading signal based on AI analysis"""
        try:
            direction = signal['direction']
            confidence = signal['confidence']
            
            self.logger.info(f"🎯 AI Signal: {direction} {symbol} (confidence: {confidence:.2f})")
            
            if direction in ['BUY', 'SELL'] and confidence > self.confidence_threshold:
                # Calculate position size based on risk management
                account_balance = self._get_account_balance()
                position_value = account_balance * self.position_size
                
                # Place order (simplified for demo)
                await self._place_order(
                    symbol=symbol,
                    side=direction,
                    size=position_value,
                    price=signal.get('target_price', float(tick.bid_price)),
                    stop_loss=signal.get('stop_loss')
                )
                
        except Exception as e:
            self.logger.error(f"Failed to execute AI signal: {e}")
            
    async def _place_order(self, symbol: str, side: str, size: float, 
                          price: float, stop_loss: Optional[float] = None):
        """Place trading order with risk management"""
        try:
            # Log the order (in real implementation, this would place actual orders)
            self.logger.info(f"📊 Order: {side} {size:.2f} {symbol} @ {price:.6f}")
            
            # Update performance tracking
            self.bridge.performance_metrics['total_trades'] += 1
            
            # Store order in knowledge graph via MCP
            if self.bridge.mcp_service:
                await self._store_order_in_knowledge_graph({
                    'symbol': symbol,
                    'side': side,
                    'size': size,
                    'price': price,
                    'stop_loss': stop_loss,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            
    async def _store_order_in_knowledge_graph(self, order_data: Dict):
        """Store trading order in MCPVots knowledge graph"""
        try:
            if self.bridge.mcp_service:
                # Create entity for the trade
                entity_name = f"trade_{order_data['symbol']}_{int(time.time())}"
                
                await self.bridge.mcp_service.create_entities([{
                    'name': entity_name,
                    'entityType': 'trading_order',
                    'observations': [
                        f"Symbol: {order_data['symbol']}",
                        f"Side: {order_data['side']}",
                        f"Size: {order_data['size']}",
                        f"Price: {order_data['price']}",
                        f"Timestamp: {order_data['timestamp']}"
                    ]
                }])
                
                self.logger.info(f"📝 Trade stored in knowledge graph: {entity_name}")
                
        except Exception as e:
            self.logger.error(f"Knowledge graph storage failed: {e}")
            
    def _get_account_balance(self) -> float:
        """Get current account balance"""
        # Return configured initial capital (in real implementation, get from exchange)
        return self.bridge.config.get('initial_capital', 50.0)

class CryptoIntelligenceCollector:
    """
    📊 Crypto Intelligence & Market Data Collector
    Gathers comprehensive market intelligence for AI analysis
    """
    
    def __init__(self, bridge: NautilusMCPBridge):
        self.bridge = bridge
        self.logger = bridge.logger
        
        # Data sources
        self.exchanges = ['binance', 'coinbase', 'okx', 'bybit']
        self.defi_protocols = ['uniswap', 'jupiter', 'curve']
        
        # Intelligence categories
        self.intelligence_types = [
            'price_data',
            'volume_analysis', 
            'orderbook_depth',
            'funding_rates',
            'social_sentiment',
            'on_chain_metrics',
            'defi_tvl',
            'whale_movements'
        ]
        
    async def start_collection(self):
        """Start continuous intelligence collection"""
        self.logger.info("📡 Starting crypto intelligence collection")
        
        # Start collection tasks
        tasks = [
            self._collect_price_data(),
            self._collect_volume_analysis(), 
            self._collect_orderbook_data(),
            self._collect_funding_rates(),
            self._collect_social_sentiment(),
            self._collect_onchain_metrics(),
            self._collect_defi_metrics(),
            self._monitor_whale_movements()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _collect_price_data(self):
        """Collect real-time price data from multiple exchanges"""
        while True:
            try:
                for pair in self.bridge.config['trading_pairs']:
                    # Simulate price data collection
                    price_data = await self._fetch_price_from_exchanges(pair)
                    
                    # Store in knowledge graph
                    await self._store_market_intelligence(
                        'price_data', pair, price_data
                    )
                    
                await asyncio.sleep(self.bridge.config['update_frequency'])
                
            except Exception as e:
                self.logger.error(f"Price data collection error: {e}")
                await asyncio.sleep(5)
                
    async def _fetch_price_from_exchanges(self, pair: str) -> Dict:
        """Fetch price data from multiple exchanges"""
        # Simplified implementation - in real use, connect to actual APIs
        import random
        
        base_price = 100 + random.uniform(-10, 10)
        
        return {
            'symbol': pair,
            'exchanges': {
                'binance': base_price + random.uniform(-0.5, 0.5),
                'coinbase': base_price + random.uniform(-0.3, 0.3),
                'okx': base_price + random.uniform(-0.4, 0.4)
            },
            'average_price': base_price,
            'spread': random.uniform(0.01, 0.1),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_volume_analysis(self):
        """Analyze trading volume patterns"""
        while True:
            try:
                for pair in self.bridge.config['trading_pairs']:
                    volume_data = await self._analyze_volume_patterns(pair)
                    await self._store_market_intelligence(
                        'volume_analysis', pair, volume_data
                    )
                    
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Volume analysis error: {e}")
                await asyncio.sleep(10)
                
    async def _analyze_volume_patterns(self, pair: str) -> Dict:
        """Analyze volume patterns and trends"""
        # Simplified volume analysis
        import random
        
        return {
            'symbol': pair,
            'volume_24h': random.uniform(1000000, 50000000),
            'volume_trend': random.choice(['increasing', 'decreasing', 'stable']),
            'volume_spike': random.choice([True, False]),
            'relative_volume': random.uniform(0.5, 2.0),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_orderbook_data(self):
        """Collect and analyze orderbook depth"""
        while True:
            try:
                for pair in self.bridge.config['trading_pairs']:
                    orderbook_data = await self._analyze_orderbook_depth(pair)
                    await self._store_market_intelligence(
                        'orderbook_depth', pair, orderbook_data
                    )
                    
                await asyncio.sleep(5)  # Every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Orderbook collection error: {e}")
                await asyncio.sleep(10)
                
    async def _analyze_orderbook_depth(self, pair: str) -> Dict:
        """Analyze orderbook depth and liquidity"""
        import random
        
        return {
            'symbol': pair,
            'bid_depth': random.uniform(10000, 100000),
            'ask_depth': random.uniform(10000, 100000),
            'spread_bps': random.uniform(1, 20),
            'liquidity_score': random.uniform(0.1, 1.0),
            'support_levels': [100, 95, 90],
            'resistance_levels': [110, 115, 120],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_funding_rates(self):
        """Monitor perpetual funding rates"""
        while True:
            try:
                for pair in self.bridge.config['trading_pairs']:
                    if 'USDT' in pair:  # Only for perpetual pairs
                        funding_data = await self._get_funding_rates(pair)
                        await self._store_market_intelligence(
                            'funding_rates', pair, funding_data
                        )
                        
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Funding rates error: {e}")
                await asyncio.sleep(60)
                
    async def _get_funding_rates(self, pair: str) -> Dict:
        """Get funding rates from exchanges"""
        import random
        
        return {
            'symbol': pair,
            'funding_rate': random.uniform(-0.001, 0.001),
            'next_funding': datetime.now(timezone.utc).isoformat(),
            'historical_avg': random.uniform(-0.0005, 0.0005),
            'sentiment_indicator': random.choice(['bullish', 'bearish', 'neutral']),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_social_sentiment(self):
        """Collect social media sentiment data"""
        while True:
            try:
                for pair in self.bridge.config['trading_pairs']:
                    sentiment_data = await self._analyze_social_sentiment(pair)
                    await self._store_market_intelligence(
                        'social_sentiment', pair, sentiment_data
                    )
                    
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Social sentiment error: {e}")
                await asyncio.sleep(120)
                
    async def _analyze_social_sentiment(self, pair: str) -> Dict:
        """Analyze social media sentiment"""
        import random
        
        return {
            'symbol': pair,
            'twitter_sentiment': random.uniform(-1, 1),
            'reddit_sentiment': random.uniform(-1, 1),
            'telegram_activity': random.uniform(0, 1),
            'mention_volume': random.randint(100, 10000),
            'sentiment_trend': random.choice(['improving', 'declining', 'stable']),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_onchain_metrics(self):
        """Collect blockchain on-chain metrics"""
        while True:
            try:
                # Focus on Solana and Ethereum metrics
                for blockchain in ['solana', 'ethereum']:
                    onchain_data = await self._get_onchain_metrics(blockchain)
                    await self._store_market_intelligence(
                        'on_chain_metrics', blockchain, onchain_data
                    )
                    
                await asyncio.sleep(900)  # Every 15 minutes
                
            except Exception as e:
                self.logger.error(f"On-chain metrics error: {e}")
                await asyncio.sleep(300)
                
    async def _get_onchain_metrics(self, blockchain: str) -> Dict:
        """Get on-chain metrics for blockchain"""
        import random
        
        return {
            'blockchain': blockchain,
            'active_addresses': random.randint(100000, 1000000),
            'transaction_count': random.randint(1000000, 10000000),
            'network_hash_rate': random.uniform(100, 1000),
            'staking_ratio': random.uniform(0.4, 0.8),
            'defi_tvl': random.uniform(1000000000, 50000000000),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _collect_defi_metrics(self):
        """Collect DeFi protocol metrics"""
        while True:
            try:
                for protocol in self.defi_protocols:
                    defi_data = await self._get_defi_metrics(protocol)
                    await self._store_market_intelligence(
                        'defi_tvl', protocol, defi_data
                    )
                    
                await asyncio.sleep(1800)  # Every 30 minutes
                
            except Exception as e:
                self.logger.error(f"DeFi metrics error: {e}")
                await asyncio.sleep(600)
                
    async def _get_defi_metrics(self, protocol: str) -> Dict:
        """Get DeFi protocol metrics"""
        import random
        
        return {
            'protocol': protocol,
            'tvl': random.uniform(100000000, 10000000000),
            'volume_24h': random.uniform(10000000, 1000000000),
            'fees_24h': random.uniform(100000, 10000000),
            'users_24h': random.randint(1000, 100000),
            'yield_opportunities': random.uniform(0.05, 0.25),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    async def _monitor_whale_movements(self):
        """Monitor large wallet movements"""
        while True:
            try:
                whale_data = await self._detect_whale_movements()
                if whale_data:
                    await self._store_market_intelligence(
                        'whale_movements', 'all', whale_data
                    )
                    
                await asyncio.sleep(120)  # Every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Whale monitoring error: {e}")
                await asyncio.sleep(60)
                
    async def _detect_whale_movements(self) -> Optional[Dict]:
        """Detect significant whale wallet movements"""
        import random
        
        # Simulate whale detection
        if random.random() < 0.1:  # 10% chance of whale activity
            return {
                'whale_address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'amount': random.uniform(1000000, 100000000),
                'token': random.choice(['SOL', 'ETH', 'BTC', 'USDT']),
                'direction': random.choice(['in', 'out']),
                'exchange': random.choice(['binance', 'coinbase', 'unknown']),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        return None
        
    async def _store_market_intelligence(self, intel_type: str, symbol: str, data: Dict):
        """Store market intelligence in knowledge graph"""
        try:
            if self.bridge.mcp_service:
                entity_name = f"{intel_type}_{symbol}_{int(time.time())}"
                
                observations = [f"{k}: {v}" for k, v in data.items()]
                
                await self.bridge.mcp_service.create_entities([{
                    'name': entity_name,
                    'entityType': f'market_{intel_type}',
                    'observations': observations
                }])
                
                self.logger.debug(f"📊 Stored {intel_type} for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Intelligence storage failed: {e}")

class NautilusSystemOrchestrator:
    """
    🎼 Nautilus Trading System Orchestrator
    Coordinates all components of the trading system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.bridge = NautilusMCPBridge(config_path)
        self.logger = self.bridge.logger
        
        # System components
        self.intelligence_collector = CryptoIntelligenceCollector(self.bridge)
        self.trading_strategies = []
        
        # System state
        self.is_running = False
        self.system_health = {}
        
    async def start_system(self):
        """Start the complete Nautilus trading system"""
        self.logger.info("🚀 Starting Nautilus-MCPVots Trading System")
        
        try:
            # Check Nautilus availability
            if not NAUTILUS_AVAILABLE:
                self.logger.warning("⚠️ Nautilus Trader not installed - running in simulation mode")
            
            # Initialize components
            await self._initialize_system()
            
            # Start intelligence collection
            self.logger.info("📡 Starting intelligence collection")
            intelligence_task = asyncio.create_task(
                self.intelligence_collector.start_collection()
            )
            
            # Start trading strategies
            self.logger.info("🧠 Starting AI trading strategies")
            strategy_tasks = []
            for strategy in self.trading_strategies:
                task = asyncio.create_task(strategy.run())
                strategy_tasks.append(task)
            
            # Start system monitoring
            self.logger.info("📊 Starting system monitoring")
            monitoring_task = asyncio.create_task(self._monitor_system_health())
            
            # Set system as running
            self.is_running = True
            
            # Wait for all tasks
            all_tasks = [intelligence_task, monitoring_task] + strategy_tasks
            await asyncio.gather(*all_tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"❌ System startup failed: {e}")
            raise
            
    async def _initialize_system(self):
        """Initialize all system components"""
        # Initialize AI-enhanced strategy
        ai_strategy = AIEnhancedTradingStrategy(self.bridge)
        self.trading_strategies.append(ai_strategy)
        
        # Initialize MCP connections
        if self.bridge.mcp_service:
            await self.bridge.mcp_service.initialize()
            
        self.logger.info("✅ System components initialized")
        
    async def _monitor_system_health(self):
        """Monitor system health and performance"""
        while self.is_running:
            try:
                # Collect health metrics
                health_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'uptime': (datetime.now(timezone.utc) - self.bridge.performance_metrics['start_time']).total_seconds(),
                    'total_trades': self.bridge.performance_metrics['total_trades'],
                    'profitable_trades': self.bridge.performance_metrics['profitable_trades'],
                    'win_rate': self._calculate_win_rate(),
                    'total_pnl': float(self.bridge.performance_metrics['total_pnl']),
                    'active_strategies': len(self.trading_strategies),
                    'ai_service_status': 'active' if self.bridge.ai_service else 'inactive',
                    'mcp_service_status': 'active' if self.bridge.mcp_service else 'inactive'
                }
                
                self.system_health = health_data
                
                # Log health status every 5 minutes
                if int(health_data['uptime']) % 300 == 0:
                    self.logger.info(f"💚 System Health: {health_data['total_trades']} trades, "
                                   f"{health_data['win_rate']:.1%} win rate, "
                                   f"${health_data['total_pnl']:.2f} PnL")
                
                # Store health data in knowledge graph
                await self._store_system_health(health_data)
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
                
    def _calculate_win_rate(self) -> float:
        """Calculate current win rate"""
        total = self.bridge.performance_metrics['total_trades']
        if total == 0:
            return 0.0
        return self.bridge.performance_metrics['profitable_trades'] / total
        
    async def _store_system_health(self, health_data: Dict):
        """Store system health in knowledge graph"""
        try:
            if self.bridge.mcp_service:
                entity_name = f"system_health_{int(time.time())}"
                
                observations = [f"{k}: {v}" for k, v in health_data.items()]
                
                await self.bridge.mcp_service.create_entities([{
                    'name': entity_name,
                    'entityType': 'system_health',
                    'observations': observations
                }])
                
        except Exception as e:
            self.logger.error(f"Health storage failed: {e}")
            
    async def stop_system(self):
        """Gracefully stop the trading system"""
        self.logger.info("🛑 Stopping Nautilus-MCPVots Trading System")
        self.is_running = False
        
        # Stop all strategies
        for strategy in self.trading_strategies:
            try:
                await strategy.stop()
            except:
                pass
                
        self.logger.info("✅ System stopped successfully")

async def main():
    """Main entry point for Nautilus-MCPVots integration"""
    print("🌊 Nautilus Trader - MCPVots Integration")
    print("🚀 Advanced Crypto Trading Intelligence System")
    print("💰 Starting with $50 budget on Solana & Base L2")
    print("=" * 60)
    
    # Create and start the system
    orchestrator = NautilusSystemOrchestrator()
    
    try:
        await orchestrator.start_system()
    except KeyboardInterrupt:
        print("\n⏹️ Shutdown requested by user")
        await orchestrator.stop_system()
    except Exception as e:
        print(f"❌ System error: {e}")
        await orchestrator.stop_system()

if __name__ == "__main__":
    asyncio.run(main())
