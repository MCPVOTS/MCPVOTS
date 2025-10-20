#!/usr/bin/env python3
"""

"""
import asyncio
import time
import json
import logging
import argparse
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from decimal import Decimal
from contextlib import suppress

# Web3 imports
from web3 import Web3
import requests

# Load environment from .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Local configuration and clients
try:
    import standalone_config as config  # type: ignore
except Exception as _e:
    config = None  # type: ignore

try:
    from kyber_client import KyberClient  # type: ignore
except Exception:
    KyberClient = None  # type: ignore

# Explorer API client (Etherscan v2 for Base)
try:
    from basescan_client import EtherscanV2Client  # type: ignore
except Exception:
    EtherscanV2Client = None  # type: ignore

# Optional ChromaDB integration flag
try:
    import standalone_config as _sc  # type: ignore
    CHROMADB_AVAILABLE = bool(getattr(_sc, 'CHROMADB_ENABLED', False))
    if CHROMADB_AVAILABLE:
        import ethermax_chromadb as chromadb_integration  # type: ignore
except Exception:
    CHROMADB_AVAILABLE = False


class RateLimiter:
    def __init__(self, max_calls: int = 10):
        self.max_calls = max_calls


class RPCManager:
    """Minimal RPC manager for Base chain with simple rotation stub."""
    def __init__(self):
        default_url = None
        try:
            default_url = os.getenv('BASE_RPC_URL') or (getattr(config, 'PROVIDER_URL', None) if config else None)
        except Exception:
            default_url = None
        self.rpc_endpoints = [u for u in [default_url] if u]
        if not self.rpc_endpoints:
            # Sensible default for Base mainnet
            self.rpc_endpoints = ["https://mainnet.base.org"]
        self.current_rpc_index = 0
        self._w3: Optional[Web3] = None
        self.rate_limiter = RateLimiter(10)

    async def get_w3_instance(self) -> Web3:
        url = self.rpc_endpoints[self.current_rpc_index]
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 30}))
        return self._w3


class DashboardWebSocketServer:
    """Lightweight WS broadcaster (no HTTP)."""
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self._server = None
        self._clients: set = set()

    async def start(self):
        if websockets is None:
            return None

        async def _handler(ws, path):
            self._clients.add(ws)
            try:
                async for _ in ws:
                    pass
            except Exception:
                pass
            finally:
                try:
                    self._clients.remove(ws)
                except KeyError:
                    pass

        self._server = await websockets.serve(_handler, self.host, self.port)  # type: ignore
        return self._server

    async def stop(self):
        if self._server:
            self._server.close()
            with suppress(Exception):
                await self._server.wait_closed()
            self._server = None
        for ws in list(self._clients):
            with suppress(Exception):
                await ws.close()
        self._clients.clear()

    async def broadcast(self, payload: Dict[str, Any]):
        if not self._clients:
            return
        try:
            msg = json.dumps(payload, default=str)
        except Exception:
            return
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            with suppress(Exception):
                await ws.close()
            try:
                self._clients.remove(ws)
            except KeyError:
                pass

class MasterTradingSystem:
    """Unified MAXX trading system with all functionality consolidated"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rpc_manager = RPCManager()
        self.w3 = None
        self.account = None
        self.router = None
        self.maxx_contract = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # ChromaDB integration
        self.chromadb = None
        self.chromadb_enabled = CHROMADB_AVAILABLE

        # WebSocket integration for dashboard (optional; disabled by default)
        self.ws_enabled = False
        self.ws_server = None
        self.ws_broadcast_task = None

        # Trading state
        self.trading_stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_gas_used': 0,
            'total_eth_spent': Decimal('0'),
            'start_time': None
        }

        # Load persisted trading stats
        persisted_stats = self._load_trading_stats()
        if persisted_stats:
            self.trading_stats.update(persisted_stats)
            self.logger.info(f"Loaded trading stats: {self.trading_stats['total_trades']} total trades, {self.trading_stats['successful_trades']} successful")

        # ERC20 ABI (for MAXX)
        self.erc20_abi = [
            {
                "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "spender", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        # Transaction config defaults (can be overridden in standalone_config.py)
        self.use_eip1559 = bool(getattr(config, 'USE_EIP1559', True))
        self.max_fee_gwei = float(getattr(config, 'MAX_FEE_GWEI', 0.001))
        self.priority_fee_gwei = float(getattr(config, 'PRIORITY_FEE_GWEI', 0.0))
        self.wait_for_receipt = bool(getattr(config, 'TX_WAIT_FOR_RECEIPT', True))
        self.receipt_timeout_secs = int(getattr(config, 'TX_RECEIPT_TIMEOUT', 120))
        # Small headroom over base fee to avoid reorg/spike drops (default 0% for minimum viable)
        self.base_fee_headroom_pct = float(getattr(config, 'BASE_FEE_HEADROOM_PCT', 0.0))
        # Optional forced gas limit for Kyber client sends
        self.forced_gas_limit = None

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}


    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # WebSocket broadcast helpers
    # ==============================
    async def start_ws_server(self, host: str = 'localhost', port: int = 8080):
        try:
            self.ws_server = DashboardWebSocketServer(host=host, port=port)
            await self.ws_server.start()
            self.ws_enabled = True
            self.logger.info(f"Dashboard WS enabled at ws://{host}:{port}/ws")
        except Exception as e:
            self.logger.error(f"Failed to start WS server: {e}")
            self.ws_enabled = False

    async def stop_ws_server(self):
        try:
            if self.ws_broadcast_task:
                self.ws_broadcast_task.cancel()
                with suppress(Exception):
                    await self.ws_broadcast_task
                self.ws_broadcast_task = None
            if self.ws_server:
                await self.ws_server.stop()
            self.ws_enabled = False
        except Exception as e:
            self.logger.error(f"Failed to stop WS server: {e}")

    async def ws_broadcast_price(self):
        if not self.ws_enabled or not self.ws_server:
            return
        p = self._get_prices() or {}
        if p:
            await self.ws_server.broadcast({
                'type': 'price_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'price': float(p.get('maxx_usd') or 0),
                    'maxx_price': float(p.get('maxx_usd') or 0),
                    'eth_price': float(p.get('eth_usd') or 0)
                }
            })

    async def ws_broadcast_balances(self):
        if not self.ws_enabled or not self.ws_server:
            return
        eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
        await self.ws_server.broadcast({
            'type': 'balance_update',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'eth_balance': float(eth),
                'maxx_balance': float(maxx)
            }
        })

    async def ws_broadcast_trade(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal, tx_hash: str, success: bool):
        if not self.ws_enabled or not self.ws_server:
            return
        # derive approximate price
        p = self._get_prices() or {}
        px = float(p.get('maxx_usd') or 0)
        await self.ws_server.broadcast({
            'type': 'trade',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'type': trade_type,
                'symbol': 'MAXX',
                'amount': float(amount_maxx) if trade_type == 'sell' else float(amount_maxx),
                'price': px,
                'tx_hash': tx_hash,
                'success': success
            }
        })

    async def ws_broadcast_tick(self, payload: Dict[str, Any]):
        if not self.ws_enabled or not self.ws_server:
            return
        await self.ws_server.broadcast({
            'type': 'tick',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': payload
        })

    async def ws_broadcast_loop(self, interval_seconds: float = 2.0):
        while not self.shutdown_event.is_set() and self.ws_enabled:
            try:
                await asyncio.gather(
                    self.ws_broadcast_price(),
                    self.ws_broadcast_balances(),
                )
            except Exception as e:
                self.logger.debug(f"WS broadcast loop error: {e}")
            await asyncio.sleep(interval_seconds)

    # ==============================
    # Reactive state persistence
    # ==============================
    def _reactive_state_path(self) -> str:
        return os.getenv('REACTIVE_STATE_FILE', 'reactive_state.json')

    def _load_reactive_state(self) -> Dict[str, Any]:
        path = self._reactive_state_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load reactive state: {e}")
        return {}

    def _save_reactive_state(self, state: Dict[str, Any]):
        path = self._reactive_state_path()
        try:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save reactive state: {e}")

    # ==============================
    # Trading stats persistence
    # ==============================
    def _trading_stats_path(self) -> str:
        return os.getenv('TRADING_STATS_FILE', 'trading_stats.json')

    def _load_trading_stats(self) -> Dict[str, Any]:
        path = self._trading_stats_path()
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f) or {}
                    if isinstance(d, dict):
                        # Convert string values back to Decimal
                        if 'total_eth_spent' in d:
                            d['total_eth_spent'] = Decimal(str(d['total_eth_spent']))
                        if 'start_time' in d and d['start_time']:
                            # Keep as datetime if possible
                            pass
                        return d
        except Exception as e:
            self.logger.debug(f"Failed to load trading stats: {e}")
        return {}

    def _save_trading_stats(self):
        path = self._trading_stats_path()
        try:
            tmp = path + '.tmp'
            stats_copy = self.trading_stats.copy()
            # Convert Decimal to string for JSON serialization
            stats_copy['total_eth_spent'] = str(stats_copy['total_eth_spent'])
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, separators=(',', ':'), default=str)
            os.replace(tmp, path)
        except Exception as e:
            self.logger.debug(f"Failed to save trading stats: {e}")

    # ==============================
    # Reactive strategy (buy low/sell high)
    # ==============================
    async def run_reactive_strategy(
        self,
        usd_to_spend: Decimal = Decimal('7'),
        usd_reserve: Decimal = Decimal('10'),
    sell_gain_pct: Decimal = Decimal('0.10'),
    rebuy_drop_pct: Decimal = Decimal('0.10'),
        gas_limit_override: Optional[int] = None,
        slippage_bps: int = 75,
        gas_usd_cap: Optional[Decimal] = None,
        spend_all: bool = False,
    ):
        """Reactive loop that anchors from last action price and only trades in profitable directions.

        - Uses single anchor price updated on every buy/sell action
        - If last action was BUY: only SELL when price > anchor_price + sell_gain_pct
        - If last action was SELL: only BUY when price < anchor_price - rebuy_drop_pct
        - Prints detailed decision logic for transparency
        """
        # Ensure system is initialized
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

    # Use current gas policy (respect global overrides and defaults)

        # Initial prices and reserve
        prices = self._get_prices() or {}
        eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
        reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

        # Starting state (resume from persistence when available)
        _, maxx_balance = await self.get_balances_cached(min_interval_seconds=10)
        cur_price_usd = Decimal(str(prices.get('maxx_usd') or '0'))
        holding = bool(maxx_balance) and Decimal(maxx_balance) > 0

        # Single anchor price that gets updated on every action
        anchor_price_usd: Decimal = cur_price_usd
        last_action_type: Optional[str] = None

        st = self._load_reactive_state()
        if st:
            try:
                st_holding = bool(st.get('holding'))
                st_anchor = Decimal(str(st.get('anchor_price_usd') or '0'))
                st_type = st.get('last_action_type') or None
                if st_anchor > 0:
                    anchor_price_usd = st_anchor
                    last_action_type = st_type
                    self.logger.info(
                        f"Resuming from state: anchor=${anchor_price_usd:.6f} last_action={last_action_type} holding={st_holding}"
                    )
            except Exception as e:
                self.logger.debug(f"Persisted state parse issue, using live defaults: {e}")

        if holding and (last_action_type is None):
            if anchor_price_usd <= 0:
                pnow = self._get_prices() or {}
                anchor_price_usd = Decimal(str(pnow.get('maxx_usd') or '0'))
            self.logger.info(
                f"Resuming HOLDING mode: MAXX balance detected. Anchor price=${anchor_price_usd:.6f}. Will SELL only when price > ${anchor_price_usd * (Decimal('1.0') + sell_gain_pct):.6f} (+{int(sell_gain_pct*100)}%)"
            )
            last_action_type = 'buy'
        if (not holding) and (last_action_type is None):
            self.logger.info("No MAXX holdings. Monitoring for re-entry conditions.")
            if anchor_price_usd > 0:
                last_action_type = 'sell'

        tick = 0
        while not self.shutdown_event.is_set():
            try:
                p = self._get_prices()
                if not p:
                    await asyncio.sleep(3)
                    continue
                maxx_usd = Decimal(str(p.get('maxx_usd') or '0'))
                eth_usd = Decimal(str(p.get('eth_usd') or '0'))

                if holding:
                    # Last action was BUY, only SELL if price > anchor + gain%
                    if anchor_price_usd > 0 and maxx_usd >= anchor_price_usd * (Decimal('1.0') + sell_gain_pct):
                        cur_eth, maxx_now = await self.get_balances_cached(min_interval_seconds=5)
                        if Decimal(maxx_now) > 0:
                            w3 = await self.rpc_manager.get_w3_instance()
                            gas_units = int(gas_limit_override or getattr(config, 'GAS_LIMIT', 300000))
                            est_approval_eth = self._estimate_gas_cost_eth(w3, 120000)
                            est_sell_eth = self._estimate_gas_cost_eth(w3, gas_units)
                            total_gas_eth = est_approval_eth + est_sell_eth
                            if gas_usd_cap is not None:
                                p_now = self._get_prices() or {}
                                eth_usd_now = Decimal(str(p_now.get('eth_usd') or '0'))
                                if eth_usd_now > 0 and (total_gas_eth * eth_usd_now) > gas_usd_cap:
                                    self.logger.info(f"SELL skip: gas ${(total_gas_eth*eth_usd_now):.4f} > cap ${gas_usd_cap}")
                                    await asyncio.sleep(2)
                                    continue
                            if Decimal(cur_eth) < total_gas_eth:
                                self.logger.warning(
                                    f"Skip SELL: not enough ETH for gas (need~{total_gas_eth:.6f} ETH, have {Decimal(cur_eth):.6f})"
                                )
                                await asyncio.sleep(2)
                                continue
                            self.logger.info(
                                f"PRE-SELL | ETH {Decimal(cur_eth):.6f} | MAXX {Decimal(maxx_now):,.2f} | gas~{total_gas_eth:.6f} ETH (${total_gas_eth*eth_usd:.4f}) | gas_limit {gas_units}"
                            )
                            self.logger.info(
                                f"SELL: +{int(sell_gain_pct*100)}% reached. Selling {Decimal(maxx_now):.2f} MAXX"
                            )
                            txh = await self.sell_maxx(Decimal(str(maxx_now)), gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"SELL_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")
                            holding = False
                            anchor_price_usd = maxx_usd
                            last_action_type = 'sell'
                            last_action_price_usd = maxx_usd
                            # Persist state after SELL
                            self._save_reactive_state({
                                'holding': holding,
                                'anchor_price_usd': float(anchor_price_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                            })
                else:
                    # Last action was SELL, only BUY if price < anchor - drop%
                    if anchor_price_usd > 0 and maxx_usd <= anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct):
                        cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                        w3 = await self.rpc_manager.get_w3_instance()
                        gas_units = int(gas_limit_override or getattr(config, 'GAS_LIMIT', 300000))
                        est_buy_eth = self._estimate_gas_cost_eth(w3, gas_units)
                        if gas_usd_cap is not None and eth_usd > 0 and (est_buy_eth * eth_usd) > gas_usd_cap:
                            self.logger.info(f"BUY skip: gas ${(est_buy_eth*eth_usd):.4f} > cap ${gas_usd_cap}")
                            await asyncio.sleep(2)
                            continue
                        avail_eth = Decimal(cur_eth) - reserve_eth - est_buy_eth
                        if avail_eth <= 0:
                            self.logger.info("BUY skip: not enough ETH beyond reserve+gas")
                        else:
                            if spend_all or usd_to_spend <= 0:
                                spend_eth = avail_eth
                            else:
                                max_budget_eth = (usd_to_spend / eth_usd) if eth_usd > 0 else avail_eth
                                spend_eth = min(avail_eth, max_budget_eth)
                            self.logger.info(
                                f"PRE-BUY | ETH avail {avail_eth:.6f} | gas~{est_buy_eth:.6f} ETH (${est_buy_eth*eth_usd:.4f}) | gas_limit {gas_units}"
                            )
                            self.logger.info(
                                f"REBUY: -{int(rebuy_drop_pct*100)}% from anchor. Buying with {spend_eth:.6f} ETH"
                            )
                            txh = await self.buy_maxx(spend_eth, gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"BUY_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")
                            holding = True
                            anchor_price_usd = maxx_usd
                            last_action_type = 'buy'
                            last_action_price_usd = maxx_usd
                            # Persist state after BUY
                            self._save_reactive_state({
                                'holding': holding,
                                'anchor_price_usd': float(anchor_price_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                            })
                tick += 1
                eth_bal, maxx_bal = await self.get_balances_cached(min_interval_seconds=20)
                avail_eth_hb = max(Decimal(eth_bal) - reserve_eth, Decimal('0'))
                # Compute delta relative to the anchor price whenever we have one
                delta_anchor = ((maxx_usd / anchor_price_usd) - 1) * 100 if (anchor_price_usd and anchor_price_usd > 0) else Decimal('0')
                delta_since_action = ((maxx_usd / last_action_price_usd) - 1) * 100 if (last_action_price_usd and last_action_price_usd > 0) else Decimal('0')
                ent_sign = '+' if delta_anchor > 0 else ('-' if delta_anchor < 0 else '0')
                ent_abs = abs(delta_anchor)
                act_sign = '+' if delta_since_action > 0 else ('-' if delta_since_action < 0 else '0')
                act_abs = abs(delta_since_action)
                state = 'HOLD' if holding else 'FLAT'
                target_txt = ''
                if holding and anchor_price_usd > 0:
                    target_sell = anchor_price_usd * (Decimal('1.0') + sell_gain_pct)
                    target_txt = f" | target_sell ${target_sell:.6f}"
                elif (not holding) and anchor_price_usd > 0:
                    target_buy = anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct)
                    target_txt = f" | target_buy ${target_buy:.6f}"
                self.logger.info(f"""
┌─ 🚀 MAXX Dashboard ──────────────────────────────┐
│ � MAXX: ${maxx_usd:.6f}  |  ETH: ${eth_usd:.2f}     │
│ 💰 ETH Balance: {Decimal(eth_bal):.6f} (avail {avail_eth_hb:.6f}) │
│ 📊 MAXX Balance: {Decimal(maxx_bal):,.2f}              │
│ 📈 Anchor: ${anchor_price_usd:.6f}  |  Gas: {fee_gwei:.4f} gwei │
│ {'📈' if ent_sign == '+' else ('📉' if ent_sign == '-' else '➡️')} {ent_abs:.2f}% from anchor │
│ {'📈' if act_sign == '+' else ('📉' if act_sign == '-' else '➡️')} {act_abs:.2f}% since {last_action_type or 'action'} │
│ {'🟢 HOLD' if state == 'HOLD' else '🔴 FLAT'}  | {target_txt} │
└─────────────────────────────────────────────────┘
""")
                # Broadcast a structured TICK for dashboards/phones
                with suppress(Exception):
                    # Get current gas price for dashboard
                    w3 = await self.rpc_manager.get_w3_instance()
                    params = self._get_gas_params(w3)
                    fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                    fee_gwei = Decimal(fee_wei) / Decimal(1e9)

                    tick_payload = {
                        'maxx_usd': float(maxx_usd),
                        'eth_usd': float(eth_usd),
                        'eth_balance': float(Decimal(eth_bal)),
                        'eth_avail': float(avail_eth_hb),
                        'maxx_balance': float(Decimal(maxx_bal)),
                        'anchor_price_usd': float(anchor_price_usd) if anchor_price_usd else 0.0,
                        'delta_anchor': float(act_abs if act_sign == '-' else act_abs) * (-1 if act_sign == '-' else (1 if act_sign == '+' else 0)),
                        'last_action_type': last_action_type or 'action',
                        'last_action_usd': float(last_action_price_usd) if last_action_price_usd else 0.0,
                        'delta_since_last': float(act_abs if act_sign == '-' else act_abs) * (-1 if act_sign == '-' else (1 if act_sign == '+' else 0)),
                        'state': state,
                        'target_sell_usd': float(anchor_price_usd * (Decimal('1.0') + sell_gain_pct)) if (state=='HOLD' and anchor_price_usd>0) else None,
                        'target_buy_usd': float(anchor_price_usd * (Decimal('1.0') - rebuy_drop_pct)) if (state=='FLAT' and anchor_price_usd>0) else None,
                        'gas_price_gwei': float(fee_gwei),
                        'gas_limit': gas_limit_override or getattr(config, 'GAS_LIMIT', 300000),
                    }
                    await self.ws_broadcast_tick(tick_payload)
                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"Reactive loop error: {e}")
                await asyncio.sleep(3)

    async def run_small_swap(self, eth_amount: Decimal = Decimal('0.0001')):
        """Perform a tiny 0.0001 ETH buy->sell round-trip via Kyber to validate plumbing."""
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        kyber = KyberClient(self.w3, self.account, self)

        eth_before, maxx_before = await self.get_balances()
        print(f"BEFORE | ETH: {eth_before:.6f} | MAXX: {maxx_before:,.2f}")

        eth_amount_wei = int(eth_amount * (10 ** 18))
        print(f"BUY | Spending {eth_amount} ETH on MAXX via Kyber...")
        buy_tx = kyber.buy_eth_to_maxx(eth_amount_wei)
        print(f"BUY_TX: {buy_tx}")

        await asyncio.sleep(8)

        eth_mid, maxx_mid = await self.get_balances()
        maxx_received = maxx_mid - maxx_before
        print(f"AFTER BUY | ETH: {eth_mid:.6f} | MAXX: {maxx_mid:,.2f} | MAXX received: {maxx_received:,.2f}")
        if maxx_received <= 0:
            print("No MAXX received; stopping.")
            return

        try:
            decimals = self.maxx_contract.functions.decimals().call()
        except Exception:
            decimals = 18
        sell_wei = int(Decimal(str(maxx_received)) * (10 ** decimals))
        print(f"SELL | Selling {maxx_received:,.2f} MAXX back to ETH via Kyber...")
        sell_tx = kyber.sell_maxx_to_eth(sell_wei)
        print(f"SELL_TX: {sell_tx}")

        await asyncio.sleep(10)

        eth_final, maxx_final = await self.get_balances()
        print(f"AFTER SELL | ETH: {eth_final:.6f} | MAXX: {maxx_final:,.2f}")
        print(f"ETH delta: {(eth_final - eth_before):.6f} | MAXX delta: {(maxx_final - maxx_before):,.2f}")

    async def run_tiny_sell(self, target_eth_out: Decimal = Decimal('0.00001'), gas_limit: Optional[int] = None):
        """Sell a tiny amount of MAXX targeting ~target_eth_out ETH to validate router path.

        - Uses DexScreener price to estimate MAXX amount.
        - Sets amountOutMin=0 to avoid revert on slippage for this tiny test.
        - Clamps to available MAXX balance.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        # Confirm router being used
        self.logger.info(f"Router in use: {getattr(config, 'KYBER_ROUTER', 'Kyber aggregator')}")

        prices = self._get_prices()
        if not prices or not prices.get('maxx_eth'):
            self.logger.error("Price fetch failed; cannot estimate tiny sell amount")
            return

        maxx_price_eth = Decimal(prices['maxx_eth'])  # ETH per MAXX
        if maxx_price_eth <= 0:
            self.logger.error("Invalid price; cannot estimate tiny sell amount")
            return

        # Estimate MAXX needed to receive target_eth_out
        est_maxx_needed = target_eth_out / maxx_price_eth
        _, maxx_balance = await self.get_balances()
        sell_amount = min(Decimal(maxx_balance), est_maxx_needed)

        if sell_amount <= 0:
            self.logger.info("No MAXX available to sell for tiny test")
            return

        # Avoid dust too small to pass decimals rounding
        try:
            dec = self.maxx_contract.functions.decimals().call()
        except Exception:
            dec = 18
        wei_amt = int(sell_amount * (10 ** dec))
        if wei_amt <= 0:
            self.logger.info("Computed sell amount too small after decimals rounding")
            return

        sell_amount = Decimal(wei_amt) / Decimal(10 ** dec)
        self.logger.info(f"TINY SELL | Target ~{target_eth_out:.8f} ETH | Selling {sell_amount:.6f} MAXX | minOut=0")

        # Set min_eth_out_wei=0 to avoid revert for tiny test
        txh = await self.sell_maxx(sell_amount, gas_limit=gas_limit, min_eth_out_wei=0)
        self.logger.info(f"TINY SELL TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")

    async def run_tiny_buy(self, eth_amount: Decimal = Decimal('0.00000001'), gas_limit: Optional[int] = None):
        """Execute a tiny ETH->MAXX buy with amountOutMin=0 to test router path."""
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        try:
            # Log pre-buy balances
            eth_before, maxx_before = await self.get_balances()
            print(f"Pre-buy ETH: {eth_before:.8f} | MAXX: {maxx_before:,.4f}")

            tx_hash = await self.buy_maxx(eth_amount, gas_limit=gas_limit, min_maxx_out_wei=0)
            if not tx_hash:
                print("Tiny buy did not return a transaction hash")
                return

            print(f"Tiny buy sent: {tx_hash}")

            # Optionally wait and show post-buy balances
            await asyncio.sleep(6)
            eth_after, maxx_after = await self.get_balances()
            print(f"Post-buy ETH: {eth_after:.8f} | MAXX: {maxx_after:,.4f}")
        except Exception as e:
            print(f"Tiny buy failed: {e}")

    async def run_burst_cycle(self,
                              duration_minutes: int = 10,
                              interval_minutes: int = 1,
                              usd_reserve: Decimal = Decimal('10'),
                              lower_gas_limit: Optional[int] = None):
        """Alternate SELL-ALL and BUY-ALL every interval for duration.

        - Keeps usd_reserve worth of ETH aside when buying.
        - Uses a slightly lower gas limit if provided.
    - Uses Kyber aggregator for routing to Uniswap V4 pool.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        start = time.time()
        end = start + duration_minutes * 60

        # Determine reserve in ETH from USD
        prices = self._get_prices() or {}
        eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
        reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0.0004')

        toggle_sell = True  # start with SELL-ALL as requested
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                eth_balance, maxx_balance = await self.get_balances_cached(min_interval_seconds=5)

                if toggle_sell:
                    # SELL ALL MAXX if any
                    if maxx_balance > 0:
                        self.logger.info(f"BURST SELL-ALL | MAXX {maxx_balance:,.2f}")
                        tx = await self.sell_maxx(Decimal(maxx_balance), gas_limit=lower_gas_limit)
                        self.logger.info(f"BURST SELL_TX: {tx}")
                    else:
                        self.logger.info("BURST SELL-ALL | No MAXX to sell")
                else:
                    # BUY with all ETH minus reserve
                    spend_eth = Decimal(eth_balance) - reserve_eth
                    if spend_eth > Decimal('0.0'):
                        # Small safety floor
                        spend_eth = max(spend_eth, Decimal('0'))
                        self.logger.info(f"BURST BUY-ALL | Spending {spend_eth:.6f} ETH (reserve {reserve_eth:.6f})")
                        tx = await self.buy_maxx(spend_eth, gas_limit=lower_gas_limit)
                        self.logger.info(f"BURST BUY_TX: {tx}")
                    else:
                        self.logger.info("BURST BUY-ALL | Not enough ETH beyond reserve")

                # Flip action and wait interval
                toggle_sell = not toggle_sell
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                self.logger.error(f"Burst cycle error: {e}")
                await asyncio.sleep(5)

    async def run_single_test(self):
        """Run a single buy/sell test"""
        print("\n" + "="*60)
        print("SINGLE TRADING TEST")
        print("="*60)

        # Get initial balances
        initial_eth, initial_maxx = await self.get_balances()
        print(f"Initial ETH: {initial_eth:.6f}")
        print(f"Initial MAXX: {initial_maxx:,.2f}")

        # Buy test
        print(f"\nExecuting buy test with {config.TEST_ETH_AMOUNT} ETH...")
        buy_tx = await self.buy_maxx(Decimal(config.TEST_ETH_AMOUNT))

        if buy_tx:
            print(f"Buy successful: {buy_tx}")

            # Wait for confirmation
            await asyncio.sleep(5)

            # Check post-buy balances
            post_buy_eth, post_buy_maxx = await self.get_balances()
            print(f"Post-buy ETH: {post_buy_eth:.6f}")
            print(f"Post-buy MAXX: {post_buy_maxx:,.2f}")

            # Sell test
            maxx_received = post_buy_maxx - initial_maxx
            if maxx_received > 0:
                print(f"\nExecuting sell test with {maxx_received} MAXX...")
                sell_tx = await self.sell_maxx(maxx_received)

                if sell_tx:
                    print(f"Sell successful: {sell_tx}")

                    # Wait for confirmation
                    await asyncio.sleep(5)

                    # Check final balances
                    final_eth, final_maxx = await self.get_balances()
                    print(f"Final ETH: {final_eth:.6f}")
                    print(f"Final MAXX: {final_maxx:,.2f}")

                    # Calculate results
                    eth_cost = initial_eth - final_eth
                    print(f"\nTotal ETH cost: {eth_cost:.6f}")
                    print(f"Test completed successfully!")
                else:
                    print("Sell test failed")
            else:
                print("No MAXX received from buy")
        else:
            print("Buy test failed")

    async def run_usd_pingpong(self,
                               duration_minutes: int = 10,
                               usd_amount: Decimal = Decimal('1'),
                               gas_limit: Optional[int] = None,
                               slippage_bps: int = 75,
                               gas_usd_cap: Optional[Decimal] = None):
        """Alternate buy $usd_amount and then sell $usd_amount for duration via Kyber.

        - Uses DexScreener prices to convert USD -> ETH for buys and USD -> MAXX for sells.
        - Waits for each tx confirmation (system default) before proceeding.
        - Skips an action if insufficient balance for trade + gas.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        end = time.time() + (duration_minutes * 60)
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                prices = self._get_prices()
                if not prices:
                    self.logger.warning("Price fetch failed; retrying...")
                    await asyncio.sleep(3)
                    continue
                eth_usd = Decimal(prices['eth_usd'])
                maxx_usd = Decimal(prices['maxx_usd']) if prices.get('maxx_usd') else Decimal('0')

                # 1) BUY $usd_amount worth
                if eth_usd > 0:
                    buy_eth = usd_amount / eth_usd
                    cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                    # Estimate gas for buy
                    w3 = await self.rpc_manager.get_w3_instance()
                    gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                    params = self._get_gas_params(w3)
                    fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                    fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                    est_buy_eth = self._estimate_gas_cost_eth(w3, gas_units)
                    if gas_usd_cap is not None:
                        est_buy_usd = est_buy_eth * eth_usd
                        if est_buy_usd > gas_usd_cap:
                            self.logger.info(f"PINGPONG BUY skip: gas ${est_buy_usd:.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                            await asyncio.sleep(5)
                            continue
                    if Decimal(cur_eth) < (buy_eth + est_buy_eth):
                        self.logger.info(f"PINGPONG BUY skip: need {buy_eth+est_buy_eth:.6f} ETH incl gas; have {Decimal(cur_eth):.6f} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                    else:
                        self.logger.info(f"PINGPONG BUY | USD ${usd_amount} (~{buy_eth:.8f} ETH)")
                        txb = await self.buy_maxx(buy_eth, gas_limit=gas_limit, min_maxx_out_wei=0, slippage_bps=slippage_bps)
                        self.logger.info(f"PINGPONG BUY_TX: {txb}")
                else:
                    self.logger.warning("ETH/USD invalid; skipping buy")

                # 2) SELL $usd_amount worth (use latest price)
                prices2 = self._get_prices() or prices
                maxx_usd2 = Decimal(prices2['maxx_usd']) if prices2 and prices2.get('maxx_usd') else maxx_usd
                if maxx_usd2 > 0:
                    _, cur_maxx = await self.get_balances_cached(min_interval_seconds=3)
                    target_maxx = usd_amount / maxx_usd2
                    sell_amt = min(Decimal(cur_maxx), target_maxx)
                    if sell_amt > 0:
                        # Estimate gas for sell (approx using same gas units)
                        w3 = await self.rpc_manager.get_w3_instance()
                        gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                        params = self._get_gas_params(w3)
                        fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                        fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                        est_sell_eth = self._estimate_gas_cost_eth(w3, gas_units)
                        if gas_usd_cap is not None:
                            est_sell_usd = est_sell_eth * eth_usd
                            if est_sell_usd > gas_usd_cap:
                                self.logger.info(f"PINGPONG SELL skip: gas ${est_sell_usd:.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                                await asyncio.sleep(5)
                                continue
                        self.logger.info(f"PINGPONG SELL | USD ${usd_amount} (~{sell_amt:.6f} MAXX)")
                        txs = await self.sell_maxx(sell_amt, gas_limit=gas_limit, min_eth_out_wei=0, slippage_bps=slippage_bps)
                        self.logger.info(f"PINGPONG SELL_TX: {txs}")
                    else:
                        self.logger.info("PINGPONG SELL skip: not enough MAXX")
                else:
                    self.logger.warning("MAXX/USD invalid; skipping sell")

                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"USD pingpong error: {e}")
                await asyncio.sleep(3)

    async def run_reserve_swing(self,
                                duration_minutes: int = 10,
                                usd_reserve: Decimal = Decimal('10'),
                                gas_limit: Optional[int] = None,
                                min_eth_trade: Decimal = Decimal('0.0000001'),
                                dust_maxx: Decimal = Decimal('0.000001'),
                                slippage_bps: int = 75,
                                gas_usd_cap: Optional[Decimal] = None):
        """Swing between sell-all and buy-all while keeping an ETH reserve.

        Logic per iteration:
        - If MAXX balance > dust, sell ALL MAXX via Kyber (minOut=0).
        - Else, buy MAXX with ALL ETH above the USD reserve minus estimated gas.
        - Uses cached balances to reduce RPC 429.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        end = time.time() + duration_minutes * 60
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                prices = self._get_prices()
                if not prices or not prices.get('eth_usd'):
                    self.logger.warning("Price fetch failed; retrying...")
                    await asyncio.sleep(3)
                    continue

                eth_usd = Decimal(prices['eth_usd'])
                # Compute reserve in ETH
                reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

                # Use cached balances to mitigate 429s
                cur_eth, cur_maxx = await self.get_balances_cached(min_interval_seconds=5)
                cur_eth = Decimal(cur_eth)
                cur_maxx = Decimal(cur_maxx)

                # If holding MAXX, sell all
                if cur_maxx > dust_maxx:
                    self.logger.info(f"SWING SELL-ALL | MAXX={cur_maxx}")
                    # Gas cap check for sell
                    if gas_usd_cap is not None and eth_usd > 0:
                        w3 = await self.rpc_manager.get_w3_instance()
                        gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                        params = self._get_gas_params(w3)
                        fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                        fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                        est_gas_eth = self._estimate_gas_cost_eth(w3, gas_units)
                        if (est_gas_eth * eth_usd) > gas_usd_cap:
                            self.logger.info(f"SWING SELL skip: gas ${(est_gas_eth*eth_usd):.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                            await asyncio.sleep(6)
                            continue
                    txs = await self.sell_maxx(cur_maxx, gas_limit=gas_limit, min_eth_out_wei=0, slippage_bps=slippage_bps)
                    self.logger.info(f"SWING SELL_TX: {txs}")
                else:
                    # Otherwise, buy using all ETH above reserve minus estimated gas
                    w3 = await self.rpc_manager.get_w3_instance()
                    gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                    params = self._get_gas_params(w3)
                    fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                    fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                    est_gas_eth = self._estimate_gas_cost_eth(w3, gas_units)
                    # Gas cap check for buy
                    if gas_usd_cap is not None and eth_usd > 0:
                        if (est_gas_eth * eth_usd) > gas_usd_cap:
                            self.logger.info(f"SWING BUY skip: gas ${(est_gas_eth*eth_usd):.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                            await asyncio.sleep(6)
                            continue
                    available_eth = cur_eth - reserve_eth - est_gas_eth
                    if available_eth > min_eth_trade:
                        self.logger.info(f"SWING BUY-ALL | ETH avail={available_eth:.8f} (reserve {reserve_eth:.8f} + est_gas {est_gas_eth:.8f}, fee {fee_gwei:.4f} gwei, gas {gas_units})")
                        txb = await self.buy_maxx(available_eth, gas_limit=gas_limit, min_maxx_out_wei=0, slippage_bps=slippage_bps)
                        self.logger.info(f"SWING BUY_TX: {txb}")
                    else:
                        self.logger.info(f"SWING skip: insufficient ETH above reserve; have {cur_eth:.8f}, need > {reserve_eth + est_gas_eth + min_eth_trade:.8f}")

                await asyncio.sleep(6)
            except Exception as e:
                self.logger.error(f"reserve_swing error: {e}")
                await asyncio.sleep(3)

    async def run_sell_all(self, gas_limit: Optional[int] = None) -> Optional[str]:
        """Sell all MAXX holdings for ETH via Kyber aggregator.

        - Fetches current MAXX balance and attempts to sell the entire amount.
        - Respects optional gas_limit override when provided.
        """
        try:
            _, maxx_balance = await self.get_balances()
            if maxx_balance <= 0:
                print("No MAXX tokens to sell")
                return None
            self.logger.info(f"Selling ALL MAXX: {maxx_balance}")
            txh = await self.sell_maxx(maxx_balance, gas_limit=gas_limit, min_eth_out_wei=0)
            if txh:
                print(f"SUCCESS! Sell transaction: https://basescan.org/tx/{txh}")
            else:
                print("FAILED! Sell transaction failed")
            return txh
        except Exception as e:
            self.logger.error(f"run_sell_all error: {e}")
            return None

    async def run_buy_pump_then_dip(self,
                                    duration_minutes: int = 15,
                                    usd_reserve: Decimal = Decimal('10'),
                                    pump_gain_pct: Decimal = Decimal('0.15'),
                                    dip_drop_pct: Decimal = Decimal('0.15'),
                                    gas_limit: Optional[int] = None,
                                    slippage_bps: int = 75,
                                    gas_usd_cap: Optional[Decimal] = None,
                                    cooldown_sec: int = 10):
        """Buy-only accumulator: buy on +pump% breakout, then buy again on -dip% pullback.

        - Keeps a fixed USD reserve in ETH.
        - On breakout: if price >= baseline * (1+pump), buy with all ETH above reserve minus est gas.
        - After that, tracks peak and buys again when price <= peak * (1-dip).
        - Tries to use the lowest viable gas; skips if estimated gas USD exceeds cap.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        end_ts = time.time() + (duration_minutes * 60)
        last_buy_ts = 0.0

    # Use current gas policy (respect global overrides and defaults)

        # Initialize price anchors
        prices = self._get_prices()
        if not prices:
            self.logger.warning("Price fetch failed at start; waiting...")
            await asyncio.sleep(3)
            prices = self._get_prices() or {}

        eth_usd = Decimal(str((prices.get('eth_usd') if prices else '3300') or '3300'))
        baseline_usd = Decimal(str((prices.get('maxx_usd') if prices else '0') or '0'))
        if baseline_usd <= 0:
            self.logger.warning("MAXX price unavailable; using placeholder baseline and retrying")
            baseline_usd = Decimal('0')
        peak_usd = baseline_usd

        # Determine reserve in ETH
        reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

        # State machine: waiting for pump -> then waiting for dip
        state = 'WAIT_PUMP'
        dip_anchor_peak = peak_usd

        while time.time() < end_ts and not self.shutdown_event.is_set():
            try:
                p = self._get_prices()
                if not p:
                    await asyncio.sleep(3)
                    continue
                maxx_usd = Decimal(p['maxx_usd'])
                eth_usd = Decimal(p['eth_usd'])

                # Update anchors
                if state == 'WAIT_PUMP':
                    if baseline_usd == 0:
                        baseline_usd = maxx_usd
                    peak_usd = max(peak_usd, maxx_usd) if peak_usd > 0 else maxx_usd
                else:
                    dip_anchor_peak = max(dip_anchor_peak, maxx_usd)

                # Estimate a conservative gas cost
                w3 = await self.rpc_manager.get_w3_instance()
                gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
                params = self._get_gas_params(w3)
                fee_wei = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
                fee_gwei = Decimal(fee_wei) / Decimal(1e9)
                est_gas_eth = self._estimate_gas_cost_eth(w3, gas_units)
                est_gas_usd = est_gas_eth * eth_usd

                # Helper: spendable ETH beyond reserve and gas
                cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                cur_eth = Decimal(cur_eth)
                reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')
                spend_eth = cur_eth - reserve_eth - est_gas_eth

                # Skip if gas beyond cap
                if gas_usd_cap is not None and est_gas_usd > gas_usd_cap:
                    self.logger.info(f"PUMP/DIP skip: gas ${est_gas_usd:.4f} > cap ${gas_usd_cap} (fee {fee_gwei:.4f} gwei, gas {gas_units})")
                    await asyncio.sleep(5)
                    continue

                # Cooldown guard
                if (time.time() - last_buy_ts) < max(0, cooldown_sec):
                    await asyncio.sleep(2)
                    continue

                if state == 'WAIT_PUMP':
                    trigger_price = baseline_usd * (Decimal('1.0') + pump_gain_pct) if baseline_usd > 0 else Decimal('0')
                    if baseline_usd > 0 and maxx_usd >= trigger_price:
                        if spend_eth > Decimal('0'):
                            self.logger.info(
                                f"BUY PUMP | price ${maxx_usd:.6f} >= ${trigger_price:.6f} (baseline ${baseline_usd:.6f}, +{int(pump_gain_pct*100)}%) | spending {spend_eth:.6f} ETH (reserve {reserve_eth:.6f}, gas~{est_gas_eth:.6f})"
                            )
                            txh = await self.buy_maxx(spend_eth, gas_limit=gas_limit, slippage_bps=slippage_bps)
                            self.logger.info(f"BUY_PUMP_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")
                            last_buy_ts = time.time()
                            state = 'WAIT_DIP'
                            dip_anchor_peak = maxx_usd
                        else:
                            self.logger.info("BUY PUMP skip: insufficient ETH beyond reserve+gas")
                    else:
                        # Optionally adapt baseline downward on clear declines
                        if baseline_usd == 0 or maxx_usd < baseline_usd * Decimal('0.985'):
                            baseline_usd = maxx_usd
                            peak_usd = maxx_usd
                else:  # WAIT_DIP
                    drop_price = dip_anchor_peak * (Decimal('1.0') - dip_drop_pct) if dip_anchor_peak > 0 else Decimal('0')
                    if dip_anchor_peak > 0 and maxx_usd <= drop_price:
                        if spend_eth > Decimal('0'):
                            self.logger.info(
                                f"BUY DIP | price ${maxx_usd:.6f} <= ${drop_price:.6f} (from peak ${dip_anchor_peak:.6f}, -{int(dip_drop_pct*100)}%) | spending {spend_eth:.6f} ETH (reserve {reserve_eth:.6f}, gas~{est_gas_eth:.6f})"
                            )
                            txh = await self.buy_maxx(spend_eth, gas_limit=gas_limit, slippage_bps=slippage_bps)
                            self.logger.info(f"BUY_DIP_TX: {txh} | https://basescan.org/tx/{txh if txh else ''}")
                            last_buy_ts = time.time()
                            # Reset for next cycle
                            state = 'WAIT_PUMP'
                            baseline_usd = maxx_usd
                            peak_usd = maxx_usd
                            dip_anchor_peak = Decimal('0')
                        else:
                            self.logger.info("BUY DIP skip: insufficient ETH beyond reserve+gas")

                # Heartbeat
                eth_bal, maxx_bal = await self.get_balances_cached(min_interval_seconds=10)
                self.logger.info(
                    (
                        "PUMP/DIP TICK | MAXX ${:.6f} | ETH ${:.2f} | ETH {:.6f} | MAXX {:,.2f} | baseline ${:.6f} peak ${:.6f} | state {}"
                    ).format(
                        maxx_usd, eth_usd, Decimal(eth_bal), Decimal(maxx_bal), baseline_usd, max(peak_usd, dip_anchor_peak), state
                    )
                )
                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"buy_pump_then_dip error: {e}")
                await asyncio.sleep(3)
