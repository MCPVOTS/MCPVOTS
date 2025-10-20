# MAXX Ecosystem - Enhanced Trading & Analytics Platform

A comprehensive, production-ready trading and analytics platform for the MAXX token on the Base blockchain. This ecosystem has been completely refactored to eliminate all mocks, simulations, and placeholders, implementing the highest coding standards with real API integrations.

## 🚀 Features

### Core Architecture
- **Modular Design**: Clean separation of concerns with dedicated core modules
- **Async/Await Patterns**: Non-blocking operations throughout the entire codebase
- **Type Safety**: Comprehensive type hints and dataclasses for all data structures
- **Error Handling**: Robust error handling with custom exception classes
- **Performance Monitoring**: Built-in metrics collection and performance tracking

### Trading Engine
- **Real-time Trading**: Live trading execution on Base blockchain
- **Risk Management**: Comprehensive risk controls and position management
- **Order Management**: Advanced order tracking and execution
- **Portfolio Management**: Real-time portfolio tracking and analytics

### Analytics & Monitoring
- **Market Data**: Real-time market data from multiple sources (DexScreener, BaseScan, CoinGecko)
- **Swarm Detection**: Advanced pattern detection for coordinated trading
- **Wallet Analysis**: Comprehensive wallet behavior analysis and risk scoring
- **Performance Metrics**: Detailed trading performance analytics

### Data Storage
- **Vector Database**: High-performance vector storage for similarity search
- **Time Series Data**: Efficient storage and retrieval of historical data
- **Caching**: Multi-level caching for optimal performance
- **Data Retention**: Configurable data retention policies

## 📁 Project Structure

```
ECOSYSTEM_UNIFIED/
├── core/                          # Core system modules
│   ├── config.py                  # Configuration management
│   ├── logging.py                 # Advanced logging system
│   ├── database.py                # Database connection management
│   ├── network.py                 # HTTP client and WebSocket management
│   ├── trading.py                 # Trading engine
│   └── analytics.py               # Analytics and monitoring
├── ethermax_analyzer.py           # MAXX token analysis tools
├── market_data_service.py         # Real-time market data service
├── base_utils.py                  # Base blockchain utilities
├── db_vector_storage.py           # Vector storage implementation
├── config.py                      # Legacy configuration wrapper
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This documentation
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+ (for some tools)
- SQLite3
- Environment variables for API keys

### Environment Variables

Create a `.env` file in the project root:

```bash
# Blockchain Configuration
ETHEREUM_PRIVATE_KEY=your_private_key_here
PROVIDER_URL=https://mainnet.base.org
BASESCAN_API_KEY=your_basescan_api_key

# MAXX Token Configuration
MAXX_CONTRACT_ADDRESS=0xFB7a83abe4F4A4E51c77B92E521390B769ff6467

# Trading Configuration
BUY_THRESHOLD=0.02
SELL_THRESHOLD=0.05
MAX_POSITION_SIZE=0.1
STOP_LOSS_PCT=0.03

# Notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Database
DB_PATH=./data/ecosystem.db
```

### Installation

#### Option 1: Quick Setup (Recommended)

**Windows Users:**
```powershell
# PowerShell (recommended)
.\setup.ps1

# Or use batch file
setup.bat
```

**Linux/macOS Users:**
```bash
make setup
```

#### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/MCPVOTS/ECOSYSTEM_UNIFIED.git
cd ECOSYSTEM_UNIFIED
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create necessary directories:
```bash
mkdir -p data logs
```

4. Set up environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python main.py
```

## 📊 Usage

### Basic Usage

```python
import asyncio
from main import MAXXEcosystem

async def main():
    # Initialize the ecosystem
    ecosystem = MAXXEcosystem()
    await ecosystem.initialize()

    # Get market overview
    overview = await ecosystem.get_market_overview()
    print(f"Market Status: {overview}")

    # Analyze a wallet
    analyzer = await ecosystem.get_ethermax_analyzer()
    wallet_analysis = await analyzer.analyze_wallet("0x...")
    print(f"Wallet Analysis: {wallet_analysis}")

    # Start trading (if configured)
    await ecosystem.start_trading()

    # Cleanup
    await ecosystem.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

#### Market Data Service
```python
from market_data_service import get_market_data_service

# Get real-time market data
market_service = await get_market_data_service()
market_data = await market_service.get_market_overview()
price_data = await market_service.get_price_history("MAXX", days=7)
```

#### Vector Storage
```python
from db_vector_storage import get_vector_storage

# Store and search vectors
storage = await get_vector_storage()
await storage.store_vector(vector_data)
similar_vectors = await storage.search_similar_vectors(query_vector)
```

#### Blockchain Utilities
```python
from base_utils import get_blockchain_utils

# Interact with Base blockchain
utils = await get_blockchain_utils()
balance = await utils.get_token_balance(token_address, wallet_address)
transfers = await utils.get_token_transfers(token_address)
```

## 🔧 Configuration

The system uses a hierarchical configuration system:

1. **Core Configuration** (`core/config.py`): Main configuration with Pydantic models
2. **Environment Variables**: Override configuration with environment variables
3. **Legacy Wrapper** (`config.py`): Backward compatibility with existing code

### Key Configuration Options

- **Trading Parameters**: Buy/sell thresholds, position sizes, risk limits
- **API Endpoints**: Blockchain RPC, external APIs
- **Database Settings**: Connection pools, retention policies
- **Monitoring**: Logging levels, metrics collection
- **Performance**: Cache sizes, rate limits

## 📈 Performance & Monitoring

### Built-in Metrics

The system automatically collects metrics for:
- API response times
- Trading performance
- Database query performance
- Cache hit rates
- Error rates

### Logging

Structured logging with multiple levels:
- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical system failures

### Performance Optimization

- **Connection Pooling**: Database and HTTP connection pools
- **Caching**: Multi-level caching strategy
- **Async Operations**: Non-blocking I/O throughout
- **Rate Limiting**: Built-in rate limiting for external APIs

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=.

# Run specific test file
python -m pytest tests/test_trading.py
```

### Test Structure

```
tests/
├── unit/                   # Unit tests
├── integration/            # Integration tests
├── fixtures/              # Test fixtures
└── conftest.py            # Test configuration
```

## 🔒 Security

### Security Features

- **Private Key Management**: Secure private key handling
- **API Key Protection**: Environment variable-based API key storage
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Secure error handling without information leakage

### Security Best Practices

1. Never commit private keys or API keys to version control
2. Use environment variables for sensitive configuration
3. Regularly rotate API keys
4. Monitor for unusual activity
5. Keep dependencies updated

## 📚 API Reference

### Core Modules

#### Configuration
```python
from core.config import get_app_config

config = get_app_config()
print(config.trading.max_position_size)
```

#### Logging
```python
from core.logging import get_logger

logger = get_logger("my_module")
logger.info("Application started")
```

#### Database
```python
from core.database import get_database_manager

db = await get_database_manager()
result = await db.execute_query("SELECT * FROM tokens")
```

#### Network
```python
from core.network import get_network_manager

network = await get_network_manager()
http_client = network.get_http_client("https://api.example.com")
```

#### Trading
```python
from core.trading import get_trading_engine

trading = await get_trading_engine()
order = await trading.place_order("buy", amount, price)
```

#### Analytics
```python
from core.analytics import get_analytics_manager

analytics = await get_analytics_manager()
await analytics.record_metric("custom_metric", 1.0)
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**: Configure production environment variables
2. **Database Setup**: Initialize production database
3. **Monitoring**: Set up monitoring and alerting
4. **Security**: Configure security measures
5. **Backup**: Set up regular backups

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  maxx-ecosystem:
    build: .
    environment:
      - ETHEREUM_PRIVATE_KEY=${PRIVATE_KEY}
      - BASESCAN_API_KEY=${BASESCAN_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Write tests for new features
- Keep functions small and focused

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check this README and inline documentation
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Common Issues

1. **Connection Issues**: Check RPC URL and network connectivity
2. **API Errors**: Verify API keys and rate limits
3. **Database Issues**: Check database permissions and disk space
4. **Performance**: Monitor resource usage and optimize configuration

## 🔄 Version History

### v2.0.0 (Current)
- Complete refactoring with no mocks or placeholders
- Real API integrations
- Enhanced performance and monitoring
- Comprehensive error handling
- Production-ready architecture

### v1.0.0 (Legacy)
- Initial implementation with placeholders
- Basic functionality
- Limited error handling

---

**Note**: This is a production-ready trading system. Always test thoroughly before deploying with real funds. Use paper trading or testnets for initial testing.

## 🖥️ Windows-Specific Instructions

### PowerShell Setup (Recommended)

1. **Enable Script Execution** (if needed):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **Run Setup Script**:
```powershell
.\setup.ps1
```

3. **Available Commands**:
```powershell
.\setup.ps1 -Dev      # Install development dependencies
.\setup.ps1 -Clean    # Clean temporary files
.\setup.ps1 -Test     # Run tests
.\setup.ps1 -Run      # Start application
.\setup.ps1 -Validate # Validate refactor
```

### Batch File Alternative

If you prefer traditional batch files or have PowerShell restrictions:

```cmd
setup.bat
setup.bat -Test
setup.bat -Run
```

### Windows Development Tips

1. **Use Windows Terminal** for better PowerShell experience
2. **Install Git for Windows** for better command line tools
3. **Use VS Code** with Python extension for development
4. **Enable virtual environment**:
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### Troubleshooting Windows Issues

**"Execution Policy" Error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

**"Python not found" Error:**
- Install Python from python.org
- Add Python to PATH during installation
- Restart PowerShell

**"pip not found" Error:**
- Ensure Python and pip are in PATH
- Use `python -m pip` instead of `pip`

### Quick Start for Windows Users

```powershell
# 1. Run initial setup
.\setup.ps1

# 2. Edit .env file with your configuration
notepad .env

# 3. Validate the refactor
.\setup.ps1 -Validate

# 4. Run tests
.\setup.ps1 -Test

# 5. Start the application
.\setup.ps1 -Run
```
