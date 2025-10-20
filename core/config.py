"""
Configuration Management System for MAXX Ecosystem
Provides secure, validated configuration management with proper environment variable handling
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum
import json
from cryptography.fernet import Fernet
import hashlib


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class BlockchainConfig:
    """Blockchain configuration"""
    provider_url: str
    chain_id: int
    block_explorer_url: str
    rpc_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class TradingConfig:
    """Trading configuration"""
    buy_threshold: float = 0.02
    sell_threshold: float = 0.05
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.03
    max_daily_trades: int = 50
    max_position_value: float = 1000.0
    trading_cycle_interval: int = 30
    profit_extraction_address: str = "0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70"


@dataclass
class TokenConfig:
    """Token configuration"""
    contract_address: str
    symbol: str
    name: str
    decimals: int = 18


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str
    max_connections: int = 10
    connection_timeout: int = 30
    retention_days: Dict[str, int] = field(default_factory=lambda: {
        'market_data': 90,
        'trades': 365,
        'sentiment': 90
    })


@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: Optional[str] = None
    private_key_env_var: str = "ETHEREUM_PRIVATE_KEY"
    webhook_url_env_var: str = "DISCORD_WEBHOOK_URL"
    basescan_api_key_env_var: str = "BASESCAN_API_KEY"


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    metrics_enabled: bool = True
    alerts_enabled: bool = True


class ConfigManager:
    """
    Secure configuration manager with validation and encryption support
    """

    def __init__(self, env: Environment = Environment.DEVELOPMENT, config_file: Optional[str] = None):
        self.env = env
        self.config_file = config_file or f"config_{env.value}.json"
        self.logger = logging.getLogger(self.__class__.__name__)
        self._encryption_key: Optional[Fernet] = None
        self._config_cache: Dict[str, Any] = {}

        # Initialize configuration
        self._load_configuration()

    def _load_configuration(self):
        """Load and validate configuration"""
        try:
            # Load from file if exists
            if Path(self.config_file).exists():
                self._load_from_file()
            else:
                self._load_from_environment()

            # Validate configuration
            self._validate_configuration()

            self.logger.info(f"Configuration loaded successfully for {self.env.value} environment")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def _load_from_file(self):
        """Load configuration from JSON file"""
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)

        # Decrypt sensitive values if encryption key is available
        if self._encryption_key:
            config_data = self._decrypt_sensitive_data(config_data)

        self._config_cache = config_data

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        self._config_cache = {
            'blockchain': {
                'provider_url': self._get_required_env('PROVIDER_URL', 'https://mainnet.base.org'),
                'chain_id': self._get_int_env('CHAIN_ID', 8453),
                'block_explorer_url': self._get_required_env('BLOCK_EXPLORER_URL', 'https://basescan.org'),
                'rpc_timeout': self._get_int_env('RPC_TIMEOUT', 30),
                'max_retries': self._get_int_env('MAX_RETRIES', 3),
                'retry_delay': self._get_float_env('RETRY_DELAY', 1.0)
            },
            'trading': {
                'buy_threshold': self._get_float_env('BUY_THRESHOLD', 0.02),
                'sell_threshold': self._get_float_env('SELL_THRESHOLD', 0.05),
                'max_position_size': self._get_float_env('MAX_POSITION_SIZE', 0.1),
                'stop_loss_pct': self._get_float_env('STOP_LOSS_PCT', 0.03),
                'max_daily_trades': self._get_int_env('MAX_DAILY_TRADES', 50),
                'max_position_value': self._get_float_env('MAX_POSITION_VALUE', 1000.0),
                'trading_cycle_interval': self._get_int_env('TRADING_CYCLE_INTERVAL', 30),
                'profit_extraction_address': self._get_required_env('PROFIT_EXTRACTION_ADDRESS', '0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70')
            },
            'token': {
                'contract_address': self._get_required_env('MAXX_CONTRACT_ADDRESS'),
                'symbol': 'MAXX',
                'name': 'MAXX Token',
                'decimals': self._get_int_env('TOKEN_DECIMALS', 18)
            },
            'database': {
                'path': self._get_required_env('DB_PATH', 'pumpfun_ecosystem.db'),
                'max_connections': self._get_int_env('DB_MAX_CONNECTIONS', 10),
                'connection_timeout': self._get_int_env('DB_CONNECTION_TIMEOUT', 30),
                'retention_days': {
                    'market_data': self._get_int_env('MARKET_DATA_RETENTION_DAYS', 90),
                    'trades': self._get_int_env('TRADES_RETENTION_DAYS', 365),
                    'sentiment': self._get_int_env('SENTIMENT_RETENTION_DAYS', 90)
                }
            },
            'security': {
                'private_key_env_var': 'ETHEREUM_PRIVATE_KEY',
                'webhook_url_env_var': 'DISCORD_WEBHOOK_URL',
                'basescan_api_key_env_var': 'BASESCAN_API_KEY'
            },
            'monitoring': {
                'log_level': self._get_required_env('LOG_LEVEL', 'INFO').upper(),
                'log_file': os.getenv('LOG_FILE'),
                'metrics_enabled': self._get_bool_env('METRICS_ENABLED', True),
                'alerts_enabled': self._get_bool_env('ALERTS_ENABLED', True)
            }
        }

    def _validate_configuration(self):
        """Validate configuration values"""
        # Validate blockchain config
        blockchain_config = self.get_blockchain_config()
        if not blockchain_config.provider_url:
            raise ValueError("Blockchain provider URL is required")

        if blockchain_config.chain_id <= 0:
            raise ValueError("Chain ID must be positive")

        # Validate trading config
        trading_config = self.get_trading_config()
        if not (0 < trading_config.buy_threshold < 1):
            raise ValueError("Buy threshold must be between 0 and 1")

        if not (0 < trading_config.sell_threshold < 1):
            raise ValueError("Sell threshold must be between 0 and 1")

        if not (0 < trading_config.max_position_size <= 1):
            raise ValueError("Max position size must be between 0 and 1")

        # Validate token config
        token_config = self.get_token_config()
        if not token_config.contract_address or not self._is_valid_address(token_config.contract_address):
            raise ValueError("Invalid token contract address")

        # Validate required environment variables
        self._validate_required_env_vars()

    def _validate_required_env_vars(self):
        """Validate required environment variables"""
        security_config = self.get_security_config()

        # Check for private key
        if not os.getenv(security_config.private_key_env_var):
            if self.env == Environment.PRODUCTION:
                raise ValueError(f"Environment variable {security_config.private_key_env_var} is required in production")
            else:
                self.logger.warning(f"Environment variable {security_config.private_key_env_var} not set")

    def _is_valid_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        return (address.startswith('0x') and
                len(address) == 42 and
                all(c in '0123456789abcdefABCDEF' for c in address[2:]))

    def _get_required_env(self, key: str, default: Optional[str] = None) -> str:
        """Get required environment variable"""
        value = os.getenv(key, default)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            self.logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default

    def _get_float_env(self, key: str, default: float) -> float:
        """Get float environment variable"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            self.logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def get_blockchain_config(self) -> BlockchainConfig:
        """Get blockchain configuration"""
        config = self._config_cache.get('blockchain', {})
        return BlockchainConfig(**config)

    def get_trading_config(self) -> TradingConfig:
        """Get trading configuration"""
        config = self._config_cache.get('trading', {})
        return TradingConfig(**config)

    def get_token_config(self) -> TokenConfig:
        """Get token configuration"""
        config = self._config_cache.get('token', {})
        return TokenConfig(**config)

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        config = self._config_cache.get('database', {})
        return DatabaseConfig(**config)

    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        config = self._config_cache.get('security', {})
        return SecurityConfig(**config)

    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        config = self._config_cache.get('monitoring', {})
        return MonitoringConfig(
            log_level=LogLevel(config.get('log_level', 'INFO')),
            log_file=config.get('log_file'),
            metrics_enabled=config.get('metrics_enabled', True),
            alerts_enabled=config.get('alerts_enabled', True)
        )

    def get_private_key(self) -> str:
        """Get encrypted private key from environment"""
        security_config = self.get_security_config()
        private_key = os.getenv(security_config.private_key_env_var)

        if not private_key:
            raise ValueError(f"Private key not found in environment variable {security_config.private_key_env_var}")

        # Validate private key format
        if not (private_key.startswith('0x') and len(private_key) == 66):
            raise ValueError("Invalid private key format")

        return private_key

    def get_webhook_url(self) -> Optional[str]:
        """Get webhook URL from environment"""
        security_config = self.get_security_config()
        return os.getenv(security_config.webhook_url_env_var)

    def get_basescan_api_key(self) -> Optional[str]:
        """Get BaseScan API key from environment"""
        security_config = self.get_security_config()
        return os.getenv(security_config.basescan_api_key_env_var)

    def reload_configuration(self):
        """Reload configuration from source"""
        self._config_cache.clear()
        self._load_configuration()
        self.logger.info("Configuration reloaded successfully")

    def save_configuration(self, encrypt_sensitive: bool = True):
        """Save current configuration to file"""
        config_data = self._config_cache.copy()

        if encrypt_sensitive and self._encryption_key:
            config_data = self._encrypt_sensitive_data(config_data)

        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        self.logger.info(f"Configuration saved to {self.config_file}")


# Global configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_blockchain_config() -> BlockchainConfig:
    return config_manager.get_blockchain_config()

def get_trading_config() -> TradingConfig:
    return config_manager.get_trading_config()

def get_token_config() -> TokenConfig:
    return config_manager.get_token_config()

def get_database_config() -> DatabaseConfig:
    return config_manager.get_database_config()

def get_security_config() -> SecurityConfig:
    return config_manager.get_security_config()

def get_monitoring_config() -> MonitoringConfig:
    return config_manager.get_monitoring_config()

def get_private_key() -> str:
    return config_manager.get_private_key()

def get_webhook_url() -> Optional[str]:
    return config_manager.get_webhook_url()

def get_basescan_api_key() -> Optional[str]:
    return config_manager.get_basescan_api_key()