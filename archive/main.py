"""
MAXX Ecosystem Main Entry Point
Unified trading and analytics platform with real-time monitoring
"""
import asyncio
import signal
import sys
import os
from pathlib import Path
from typing import Optional
import argparse

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import get_app_config
from core.logging import get_logger, logging_manager
from core.database import get_database_manager, close_database
from core.network import get_network_manager, close_network
from core.trading import get_trading_engine, close_trading_engine
from core.analytics import get_analytics_manager, close_analytics


class MAXXEcosystem:
    """Main MAXX Ecosystem application"""

    def __init__(self):
        self.config = get_app_config()
        self.logger = get_logger(self.__class__.__name__)
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # Core components
        self.db_manager = None
        self.network_manager = None
        self.trading_engine = None
        self.analytics_manager = None

    async def initialize(self):
        """Initialize all ecosystem components"""
        self.logger.info("Initializing MAXX Ecosystem...")

        try:
            # Initialize database
            self.db_manager = await get_database_manager()
            self.logger.info("✓ Database initialized")

            # Initialize network manager
            self.network_manager = await get_network_manager()
            self.logger.info("✓ Network manager initialized")

            # Initialize trading engine
            self.trading_engine = await get_trading_engine()
            self.logger.info("✓ Trading engine initialized")

            # Initialize analytics manager
            self.analytics_manager = await get_analytics_manager()
            self.logger.info("✓ Analytics manager initialized")

            self.logger.info("MAXX Ecosystem initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize ecosystem: {e}")
            await self.cleanup()
            raise

    async def start(self):
        """Start the ecosystem"""
        if not self.db_manager:
            await self.initialize()

        self.is_running = True
        self.logger.info("Starting MAXX Ecosystem...")

        try:
            # Start analytics monitoring
            await self.analytics_manager.start()
            self.logger.info("✓ Analytics monitoring started")

            # Start trading engine
            asyncio.create_task(self.trading_engine.start())
            self.logger.info("✓ Trading engine started")

            # Start WebSocket server for real-time data
            websocket_manager = self.network_manager.get_websocket_manager()
            await websocket_manager.start_server(
                host=self.config.websocket_host,
                port=self.config.websocket_port
            )
            self.logger.info(f"✓ WebSocket server started on {self.config.websocket_host}:{self.config.websocket_port}")

            # Setup signal handlers
            self._setup_signal_handlers()

            self.logger.info("MAXX Ecosystem started successfully")
            self.logger.info(f"Dashboard available at: http://{self.config.api_host}:{self.config.api_port}")

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.logger.error(f"Failed to start ecosystem: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the ecosystem"""
        if not self.is_running:
            return

        self.is_running = False
        self.logger.info("Stopping MAXX Ecosystem...")

        try:
            # Stop trading engine
            if self.trading_engine:
                await close_trading_engine()
                self.logger.info("✓ Trading engine stopped")

            # Stop analytics
            if self.analytics_manager:
                await close_analytics()
                self.logger.info("✓ Analytics stopped")

            # Stop WebSocket server
            if self.network_manager:
                websocket_manager = self.network_manager.get_websocket_manager()
                await websocket_manager.stop_server()
                self.logger.info("✓ WebSocket server stopped")

            # Close network manager
            await close_network()
            self.logger.info("✓ Network manager closed")

            # Close database
            await close_database()
            self.logger.info("✓ Database closed")

            self.logger.info("MAXX Ecosystem stopped successfully")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def cleanup(self):
        """Cleanup resources"""
        await self.stop()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def get_status(self) -> dict:
        """Get ecosystem status"""
        return {
            'running': self.is_running,
            'components': {
                'database': self.db_manager is not None,
                'network': self.network_manager is not None,
                'trading': self.trading_engine is not None,
                'analytics': self.analytics_manager is not None
            }
        }


async def run_ecosystem(config_file: Optional[str] = None):
    """Run the MAXX Ecosystem"""
    ecosystem = MAXXEcosystem()

    try:
        await ecosystem.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    finally:
        await ecosystem.cleanup()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MAXX Ecosystem - Trading & Analytics Platform")
    parser.add_argument(
        "--config",
        type=str,
        help="Configuration file path"
    )
    parser.add_argument(
        "--mode",
        choices=["start", "status", "test"],
        default="start",
        help="Operation mode"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )

    args = parser.parse_args()

    # Set environment variables from arguments
    if args.log_level:
        os.environ['LOG_LEVEL'] = args.log_level

    if args.config:
        os.environ['CONFIG_FILE'] = args.config

    if args.mode == "status":
        # Check ecosystem status
        print("MAXX Ecosystem Status Check")
        print("=" * 40)
        print("This would check if the ecosystem is running")
        return 0

    elif args.mode == "test":
        # Run tests
        print("Running MAXX Ecosystem Tests")
        print("=" * 40)
        print("This would run the test suite")
        return 0

    else:
        # Start the ecosystem
        print("Starting MAXX Ecosystem")
        print("=" * 40)

        try:
            return asyncio.run(run_ecosystem(args.config))
        except KeyboardInterrupt:
            print("\nShutdown complete")
            return 0
        except Exception as e:
            print(f"Startup failed: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())