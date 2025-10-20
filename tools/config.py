"""
Legacy configuration wrapper for MAXX Ecosystem
This file provides backward compatibility while using the new core configuration system
"""
import os
from typing import Optional

from core.config import get_app_config


class Config:
    """
    Legacy configuration wrapper for backward compatibility
    Uses the new core configuration system internally
    """

    def __init__(self):
        self._core_config = get_app_config()

    @property
    def WALLET_ADDRESS(self) -> str:
        """Get wallet address"""
        return self._core_config.trading.wallet_address

    @property
    def PRIVATE_KEY(self) -> Optional[str]:
        """Get private key"""
        return self._core_config.trading.private_key

    @property
    def PROVIDER_URL(self) -> str:
        """Get provider URL"""
        return self._core_config.blockchain.rpc_url

    @property
    def CHAIN_ID(self) -> int:
        """Get chain ID"""
        return self._core_config.blockchain.chain_id

    @property
    def BLOCK_EXPLORER_URL(self) -> str:
        """Get block explorer URL"""
        return self._core_config.blockchain.explorer_url

    @property
    def RPC_TIMEOUT(self) -> int:
        """Get RPC timeout"""
        return self._core_config.blockchain.timeout

    @property
    def MAXX_CONTRACT_ADDRESS(self) -> str:
        """Get MAXX contract address"""
        return os.getenv("MAXX_CONTRACT_ADDRESS", "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467")

    @property
    def BUY_THRESHOLD(self) -> float:
        """Get buy threshold"""
        return self._core_config.trading.buy_threshold

    @property
    def SELL_THRESHOLD(self) -> float:
        """Get sell threshold"""
        return self._core_config.trading.sell_threshold

    @property
    def MAX_POSITION_SIZE(self) -> float:
        """Get max position size"""
        return self._core_config.trading.max_position_size

    @property
    def STOP_LOSS_PCT(self) -> float:
        """Get stop loss percentage"""
        return self._core_config.trading.stop_loss_percentage

    @property
    def TRADING_CYCLE_INTERVAL(self) -> int:
        """Get trading cycle interval"""
        return self._core_config.trading.cycle_interval

    @property
    def NOTIFICATION_WEBHOOK(self) -> str:
        """Get notification webhook URL"""
        return self._core_config.notifications.discord_webhook_url or ""

    @property
    def MAX_DAILY_TRADES(self) -> int:
        """Get max daily trades"""
        return self._core_config.trading.max_daily_trades

    @property
    def PROFIT_EXTRACTION_ADDRESS(self) -> str:
        """Get profit extraction address"""
        return self._core_config.trading.profit_extraction_address

    @property
    def DB_PATH(self) -> str:
        """Get database path"""
        return self._core_config.database.path

    @property
    def DB_MAX_CONNECTIONS(self) -> int:
        """Get max database connections"""
        return self._core_config.database.max_connections

    @property
    def VECTOR_STORE_PATH(self) -> str:
        """Get vector store path"""
        return os.path.join(self._core_config.data_dir, "vector_store.pkl")

    @property
    def MARKET_DATA_RETENTION_DAYS(self) -> int:
        """Get market data retention days"""
        return self._core_config.data_retention.market_data_days

    @property
    def TRADES_RETENTION_DAYS(self) -> int:
        """Get trades retention days"""
        return self._core_config.data_retention.trades_days

    @property
    def SENTIMENT_RETENTION_DAYS(self) -> int:
        """Get sentiment retention days"""
        return self._core_config.data_retention.sentiment_days

    @staticmethod
    def _safe_int(env_key: str, default: int) -> int:
        """Safely convert environment variable to int with default."""
        try:
            return int(os.getenv(env_key, str(default)))
        except ValueError:
            return default

    @staticmethod
    def _safe_float(env_key: str, default: float) -> float:
        """Safely convert environment variable to float with default."""
        try:
            return float(os.getenv(env_key, str(default)))
        except ValueError:
            return default


# Create a singleton instance for backward compatibility
_config_instance = None


def get_config() -> Config:
    """Get the legacy configuration instance"""
    global _config_instance

    if _config_instance is None:
        _config_instance = Config()

    return _config_instance


# For backward compatibility, create a module-level instance
Config = get_config()
