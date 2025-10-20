# AAVE Trade History Monitor

A comprehensive monitoring system for AAVE token trades on Base chain, similar to the MAXX trading system but focused on historical data collection and analysis.

## Features

- **SQLite Database**: Stores all AAVE trade history with detailed transaction data
- **Real-time Monitoring**: Continuously fetches new trades from DexScreener API
- **Price History**: Tracks AAVE price movements and volume data
- **WebSocket Dashboard**: Optional real-time broadcasting for dashboard integration
- **Comprehensive Analytics**: Transaction volume, price analysis, and trading patterns
- **Error Handling**: Robust API error handling and retry logic

## Database Schema

### trades table

- `id`: Primary key
- `timestamp`: Transaction timestamp
- `tx_hash`: Unique transaction hash
- `block_number`: Base chain block number
- `trade_type`: BUY/SELL (inferred from DEX data)
- `amount_aave`: AAVE token amount
- `amount_usd`: USD value of transaction
- `price_usd`: AAVE price at time of transaction
- `volume_usd`: Transaction volume
- `maker/taker`: Transaction participants
- `dex`: DEX where trade occurred
- `pair_address`: Trading pair address
- `gas_used/gas_price/fee_usd`: Gas data

### price_history table

- Price tracking data with volume and market cap information

### monitoring_stats table

- System monitoring statistics and health metrics

## Usage

### Basic Monitoring

```bash
python aave_trade_monitor.py
```

### With WebSocket Dashboard

```bash
python aave_trade_monitor.py --ws-enable --ws-port 8081
```

### Custom Pair Address

```bash
python aave_trade_monitor.py --pair-address 0x1234...abcd
```

### Options

- `--pair-address`: Specific AAVE pair address (auto-discovered if not provided)
- `--interval`: Monitoring interval in seconds (default: 60)
- `--ws-enable`: Enable WebSocket server for dashboards
- `--ws-port`: WebSocket server port (default: 8081)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

## API Integration

The system integrates with:

- **DexScreener API**: Primary data source for trades and prices
- **Base Chain**: Transaction data from Base blockchain
- **WebSocket**: Real-time dashboard updates

## Data Analysis

Use the built-in methods to analyze AAVE trading patterns:

```python
from aave_trade_monitor import AaveTradeMonitor

monitor = AaveTradeMonitor()
monitor._init_database()

# Get recent trades
trades = monitor.get_recent_trades(limit=50)

# Get price history
prices = monitor.get_price_history(hours=24)

# Get trading statistics
stats = monitor.get_trading_stats()
```

## Similar to MAXX System

This AAVE monitor follows the same architecture as the MAXX trading system:

- SQLite database for persistent storage
- Async monitoring loops
- WebSocket broadcasting
- Comprehensive logging
- Error handling and recovery

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- DexScreener API access (no API key required)
- Internet connection for API calls

## Output

The monitor provides real-time logging of:

- AAVE price updates
- Transaction counts and volumes
- API call statistics
- System health metrics

Example output:

```text
2024-01-15 10:30:15 - AAVE_Monitor - INFO - AAVE Price: $2.456789 | 24h Vol: $1,234,567 | Change: +5.23%
2024-01-15 10:30:15 - AAVE_Monitor - INFO - Monitoring: 47 txns/24h | Vol: $89,123
```
