#!/usr/bin/env python3
"""
AI Ultra Smart Trader Configuration
==================================

Advanced configuration for the AI-powered trading system
"""

from decimal import Decimal

# Trading Parameters
TRADING_CONFIG = {
    # Position Management
    'max_position_size_usd': 50.0,
    'min_position_size_usd': 1.0,
    'max_positions': 3,
    'risk_per_trade': 0.02,  # 2% risk per trade

    # Trading Fees
    'trading_fee_percent': 0.3,
    'gas_limit': 300000,
    'max_gas_price_gwei': 1.0,

    # Stop Loss & Take Profit
    'default_stop_loss': 0.02,  # 2%
    'default_take_profit': 0.05,  # 5%
    'trailing_stop': True,
    'trailing_stop_percent': 0.01,
}

# AI Model Configuration
AI_CONFIG = {
    # Model Parameters
    'price_prediction_window': 300,  # 5 minutes
    'sentiment_update_interval': 60,  # 1 minute
    'volatility_lookback': 24,  # hours

    # Confidence Thresholds
    'min_signal_confidence': 0.7,
    'min_sentiment_confidence': 0.6,
    'min_ml_confidence': 0.75,

    # Feature Engineering
    'technical_indicators': [
        'RSI', 'MACD', 'Bollinger_Bands',
        'Stochastic', 'ATR', 'OBV'
    ],
    'timeframes': ['1m', '5m', '15m', '1h', '4h'],
}

# Strategy Configuration
STRATEGY_CONFIG = {
    # Strategy Weights (must sum to 1.0)
    'strategy_weights': {
        'momentum': 0.25,
        'mean_reversion': 0.20,
        'sentiment': 0.20,
        'technical': 0.15,
        'swarm': 0.10,
        'ml_prediction': 0.10
    },

    # Momentum Strategy
    'momentum': {
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'min_change_1h': 0.02,
        'min_change_24h': 0.05,
    },

    # Mean Reversion Strategy
    'mean_reversion': {
        'deviation_threshold': 0.05,
        'oversold_rsi': 30,
        'overbought_rsi': 70,
        'lookback_period': 20,
    },

    # Sentiment Strategy
    'sentiment': {
        'positive_threshold': 0.6,
        'negative_threshold': 0.4,
        'sources': ['twitter', 'reddit', 'news'],
        'weight_decay': 0.9,
    },

    # Technical Strategy
    'technical': {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bollinger_period': 20,
        'bollinger_std': 2,
    },

    # Swarm Strategy
    'swarm': {
        'min_wallets': 5,
        'time_window': 300,  # 5 minutes
        'volume_threshold': 10000,
        'confidence_threshold': 0.7,
    },
}

# Risk Management
RISK_CONFIG = {
    # Portfolio Risk
    'max_portfolio_risk': 0.10,  # 10% max portfolio risk
    'max_correlation': 0.8,
    'var_confidence': 0.95,

    # Position Risk
    'max_position_risk': 0.02,  # 2% max risk per position
    'max_leverage': 1.0,
    'margin_call_threshold': 0.8,

    # Drawdown Protection
    'max_drawdown': 0.15,  # 15% max drawdown
    'drawdown_lookback': 24,  # hours

    # Volatility Filters
    'max_volatility': 0.5,
    'volatility_scaling': True,
    'volatility_lookback': 24,
}

# Market Data Configuration
MARKET_CONFIG = {
    # Data Sources
    'primary_source': 'uniswap',
    'backup_sources': ['coingecko', 'coinmarketcap'],

    # Update Intervals
    'price_update_interval': 15,  # seconds
    'volume_update_interval': 30,
    'sentiment_update_interval': 60,

    # History
    'price_history_hours': 168,  # 1 week
    'volume_history_hours': 168,
    'sentiment_history_hours': 24,

    # API Keys (set in environment variables)
    'coingecko_api_key': 'CG_KEY',
    'twitter_bearer_token': 'TWITTER_BEARER',
    'reddit_client_id': 'REDDIT_ID',
    'reddit_client_secret': 'REDDIT_SECRET',
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_prefix': 'ai_ultra_trader',
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'backup_count': 5,
    'console_output': True,
}

# Alert Configuration
ALERT_CONFIG = {
    # Trade Alerts
    'trade_alerts': True,
    'profit_target_alerts': True,
    'stop_loss_alerts': True,

    # System Alerts
    'system_error_alerts': True,
    'low_balance_alerts': True,
    'high_gas_alerts': True,

    # Channels
    'email_alerts': False,
    'discord_webhook': '',
    'telegram_bot': '',
}

# Performance Tracking
PERFORMANCE_CONFIG = {
    # Metrics to Track
    'track_metrics': [
        'total_pnl',
        'win_rate',
        'sharpe_ratio',
        'max_drawdown',
        'avg_trade_duration',
        'profit_factor',
        'calmar_ratio'
    ],

    # Benchmarking
    'benchmark_against': ['ETH', 'BTC'],
    'risk_free_rate': 0.02,  # 2% annual

    # Reporting
    'daily_report': True,
    'weekly_report': True,
    'monthly_report': True,
}

# Development/Testing
DEV_CONFIG = {
    'paper_trading': False,
    'simulation_mode': False,
    'debug_mode': False,
    'log_trades': True,
    'save_signals': True,
}

# Contract Addresses (from main config)
MAXX_CONTRACT = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
UNISWAP_V2_ROUTER = "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"

# Network Configuration
NETWORK_CONFIG = {
    'chain_id': 8453,  # Base chain
    'rpc_endpoints': [
        "https://mainnet.base.org",
        "https://rpc.ankr.com/base"
    ],
    'block_explorer': "https://basescan.org",
}

# Export all configurations
def get_config(section: str = None):
    """Get configuration section or all config"""
    configs = {
        'trading': TRADING_CONFIG,
        'ai': AI_CONFIG,
        'strategy': STRATEGY_CONFIG,
        'risk': RISK_CONFIG,
        'market': MARKET_CONFIG,
        'logging': LOGGING_CONFIG,
        'alerts': ALERT_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'dev': DEV_CONFIG,
        'network': NETWORK_CONFIG,
    }

    if section:
        return configs.get(section, {})
    return configs

# Validate configuration
def validate_config():
    """Validate configuration settings"""
    errors = []

    # Check strategy weights sum to 1
    total_weight = sum(STRATEGY_CONFIG['strategy_weights'].values())
    if abs(total_weight - 1.0) > 0.01:
        errors.append(f"Strategy weights sum to {total_weight}, should be 1.0")

    # Check risk settings
    if RISK_CONFIG['max_position_risk'] > RISK_CONFIG['max_portfolio_risk']:
        errors.append("Position risk cannot exceed portfolio risk")

    # Check trading limits
    if TRADING_CONFIG['max_position_size_usd'] < TRADING_CONFIG['min_position_size_usd']:
        errors.append("Max position size must be greater than min position size")

    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))

    return True

# Auto-validate on import
validate_config()