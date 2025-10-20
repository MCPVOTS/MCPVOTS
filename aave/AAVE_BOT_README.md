# AAVE Trading Bot - Python Implementation

A comprehensive automated trading bot for AAVE protocol with multiple strategies, real-time market analysis, and performance tracking.

## Features

- 🤖 **Multiple Trading Strategies**: Market Making, Momentum, Arbitrage, Manual
- 📊 **Real-time Market Analysis**: Live price monitoring via APIs and WebSockets
- 🎯 **Signal Generation**: AI-powered signals with confidence scoring
- ⚡ **Automated Trade Execution**: High-confidence signals execute automatically
- 📈 **Performance Tracking**: Comprehensive P&L, win rates, and trade history
- 🔒 **Risk Management**: Position sizing, stop losses, and daily loss limits
- 🌐 **WebSocket Integration**: Live market data streaming
- 📝 **Detailed Logging**: Complete trade logs and system monitoring
- 💾 **Database Persistence**: SQLite-based trade logging and recovery
- 🚀 **GPU Acceleration**: CuPy-based GPU computing for market analysis (optional)
- 📡 **Real-time Broadcasting**: WebSocket server for dashboard integration
- ⛽ **Gas Optimization**: EIP-1559 gas parameter optimization
- 🔄 **State Persistence**: Automatic bot state saving and recovery

## Installation

1. **Clone or download** the bot script:
   ```bash
   # The bot is located at: aave_trading_bot.py
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements_aave_bot.txt
   ```

3. **Configure environment** (optional):
   Create a `.env` file with your API keys:

   ```env
   BIRDEYE_API_KEY=your_birdeye_key
   ETHERSCAN_API_KEY=your_etherscan_key
   INFURA_PROJECT_ID=your_infura_key
   ```

## Usage

### Basic Usage

```bash
python aave_trading_bot.py
```

### Enhanced Usage with WebSocket Dashboard

```bash
# Enable WebSocket server for real-time dashboard
python aave_trading_bot.py --ws-enable --ws-port 8080

# Use momentum strategy with WebSocket
python aave_trading_bot.py --strategy momentum --ws-enable
```

### Command Line Options

- `--ws-enable`: Enable WebSocket server for dashboard connectivity
- `--ws-port PORT`: WebSocket server port (default: 8080)
- `--strategy STRATEGY`: Trading strategy (market_making, momentum, arbitrage, manual)

### Configuration

The bot can be configured via the `config` dictionary in the `main()` function:

```python
config = {
    'strategy': 'market_making',  # or 'momentum', 'arbitrage', 'manual'
    'initial_balance': 1000.0,
    'max_position_size': 100.0,
    'min_trade_amount': 10.0,
    'analysis_interval': 30,  # seconds
    'api_keys': {
        'birdeye': os.getenv('BIRDEYE_API_KEY'),
        'etherscan': os.getenv('ETHERSCAN_API_KEY'),
        'infura': os.getenv('INFURA_PROJECT_ID'),
    },
    'risk_management': {
        'max_daily_loss': 50.0,
        'max_single_trade_loss': 10.0,
        'stop_loss_pct': 0.05,
    }
}
```

## Trading Strategies

### 1. Market Making

- Provides liquidity by buying low and selling high
- Uses statistical analysis of price movements
- Targets consistent small profits with high frequency

### 2. Momentum Trading

- Follows strong price trends
- Enters positions during momentum bursts
- Exits when momentum fades

### 3. Arbitrage

- Exploits price differences across exchanges
- Requires exchange API access
- Low-risk, high-frequency strategy

### 4. Manual

- Signals generated but no automatic execution
- Allows manual review and execution
- Good for learning and testing

## Risk Management

- **Position Sizing**: Maximum position limits
- **Stop Losses**: Automatic loss prevention
- **Daily Loss Limits**: Circuit breakers for drawdown
- **Trade Frequency**: Rate limiting to prevent overtrading

## Output Example

```bash
🤖 AAVE Trading Bot v2.0.0
==================================================
Starting AAVE Trading Bot...
Strategy: market_making
Initial Balance: $1000.0
--------------------------------------------------

📊 Status Update - 14:30:15
Active: 🟢 | Trading: ⏸️
Strategy: market_making | Balance: $1000.00
Price: $219.7800 | Signals: 0
Trades: 0 | Win Rate: 0.0%
Total P&L: $0.00
```

## Dependencies

### Core Dependencies
- `requests`: HTTP API calls
- `websockets`: Real-time data streaming
- `python-dotenv`: Environment variable management

### Enhanced Features (Optional)
- `numpy`: Advanced mathematical operations
- `web3`: Blockchain interactions and gas optimization
- `ccxt`: Cryptocurrency exchange integration
- `cupy-cuda11/cupy-cuda12`: GPU acceleration for market analysis

### Database
- SQLite3 (built-in Python): Trade logging and persistence

## Safety Features

- **Demo Mode**: All trades are simulated by default
- **Balance Tracking**: Real-time portfolio monitoring
- **Error Handling**: Graceful failure recovery
- **Logging**: Complete audit trail
- **Rate Limiting**: Prevents API abuse

## API Integrations

- **CoinGecko**: Free price and market data
- **Binance WebSocket**: Real-time trade data
- **Infura** (optional): Ethereum blockchain access
- **CCXT** (optional): Multi-exchange support

## Advanced Features

### Database Persistence
- All trades are logged to SQLite database (`data/aave_trades.db`)
- Trade history persists across bot restarts
- Performance analytics and recovery capabilities

### GPU Acceleration
- CuPy-based GPU computing for intensive market analysis
- Automatic fallback to CPU if GPU unavailable
- Significant performance boost for complex calculations

### WebSocket Broadcasting
- Real-time data broadcasting to dashboard clients
- Live price, balance, and trade updates
- Enables external monitoring and visualization

### Gas Optimization
- EIP-1559 gas parameter calculation
- Dynamic fee adjustment based on network conditions
- Gas cost estimation for trade profitability analysis

### Enhanced Monitoring
- Comprehensive system status reporting
- Real-time performance metrics
- Database-backed trade history retrieval

## Disclaimer

This bot is for educational and research purposes. Always test with small amounts and never risk more than you can afford to lose. Past performance does not guarantee future results. The authors are not responsible for any financial losses incurred through the use of this software.

## License

MIT License - See LICENSE file for details.

