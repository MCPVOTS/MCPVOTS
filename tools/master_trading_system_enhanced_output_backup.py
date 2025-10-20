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
try:
    import websockets  # type: ignore
except Exception:
    websockets = None  # type: ignore

# Load environment from .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Local configuration and clients
try:
    import standalone_config as config  # type: ignore
except Exception:
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
        self._server = None

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

    def _get_gas_params(self, w3: Web3) -> Dict[str, int]:
        """Build gas parameters with an adaptive, lowest-viable EIP-1559 strategy.

        - If USE_EIP1559: set maxFeePerGas >= baseFeePerGas (+1 wei buffer) and
          maxPriorityFeePerGas from config (default 0). If a configured max fee is
          lower than base fee, clamp it upward to base fee + 1 wei to ensure inclusion.
        - Else: use legacy gasPrice from config or node suggestion.
        """
        if self.use_eip1559:
            # Base fee from latest block (wei)
            try:
                latest = w3.eth.get_block('latest')
                base_fee_wei = int(getattr(latest, 'baseFeePerGas', latest['baseFeePerGas']))  # type: ignore[index]
            except Exception:
                base_fee_wei = int(0.5 * 1e9)  # fallback 0.5 gwei if node lacks field

            cfg_max_fee_wei = int(float(self.max_fee_gwei) * 1e9)
            priority_fee_wei = int(float(self.priority_fee_gwei) * 1e9)

            # Ensure max fee is at least base fee + small headroom + 1 wei buffer
            headroom = int(base_fee_wei * max(0.0, self.base_fee_headroom_pct))
            min_required_max_fee = base_fee_wei + headroom + 1
            max_fee_wei = max(cfg_max_fee_wei, min_required_max_fee)

            # Ensure priority fee does not exceed max fee
            if priority_fee_wei > max_fee_wei:
                priority_fee_wei = max_fee_wei

            return {
                'maxFeePerGas': max_fee_wei,
                'maxPriorityFeePerGas': priority_fee_wei,
            }
        else:
            cfg_gas_price_gwei = getattr(config, 'GAS_PRICE_GWEI', None)
            if cfg_gas_price_gwei is not None:
                gas_price_wei = int(float(cfg_gas_price_gwei) * 1e9)
            else:
                gas_price_wei = w3.eth.gas_price
            return {'gasPrice': gas_price_wei}

    def _estimate_gas_cost_eth(self, w3: Web3, gas_units: int) -> Decimal:
        """Rough gas cost estimate in ETH using our current gas params.

        Uses maxFeePerGas (or gasPrice) times gas units. This is a conservative upper bound.
        """
        try:
            params = self._get_gas_params(w3)
            fee = int(params.get('maxFeePerGas') or params.get('gasPrice') or 0)
        except Exception:
            fee = 0
        wei_cost = gas_units * fee
        return Decimal(wei_cost) / Decimal(10**18)

    async def cancel_pending(self, headroom_pct: float = 0.02, priority_gwei: float = 0.001) -> Optional[str]:
        """Cancel the first pending tx by replacing it with a 0-ETH self-tx at the same nonce.

        - Computes latest and pending nonces; if pending > latest, cancels nonce=latest.
        - Uses EIP-1559 with small headroom and tiny priority tip to speed inclusion.
        """
        try:
            if self.w3 is None or self.account is None:
                return None
            w3 = await self.rpc_manager.get_w3_instance()
            addr = self.account.address
            latest_nonce = w3.eth.get_transaction_count(addr, 'latest')
            pending_nonce = w3.eth.get_transaction_count(addr, 'pending')
            if pending_nonce <= latest_nonce:
                self.logger.info("No pending tx to cancel (pending_nonce <= latest_nonce)")
                return None

            # Build EIP-1559 params with headroom and tiny tip
            try:
                blk = w3.eth.get_block('latest')
                base_fee = int(getattr(blk, 'baseFeePerGas', blk['baseFeePerGas']))  # type: ignore[index]
            except Exception:
                base_fee = int(0.5 * 1e9)
            headroom = int(base_fee * max(0.0, headroom_pct))
            max_fee = base_fee + headroom + 1
            prio = int(max(0.0, priority_gwei) * 1e9)
            prio = min(prio, max_fee)
            tx = {
                'to': Web3.to_checksum_address(addr),
                'value': 0,
                'from': addr,
                'chainId': w3.eth.chain_id,
                'nonce': latest_nonce,
                'gas': 21000,
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': prio,
            }
            signed = w3.eth.account.sign_transaction(tx, private_key=self.account.key)
            raw = getattr(signed, 'raw_transaction', None) or getattr(signed, 'rawTransaction', None)
            h = w3.eth.send_raw_transaction(raw)
            if self.wait_for_receipt:
                w3.eth.wait_for_transaction_receipt(h, timeout=self.receipt_timeout_secs)
            hx = h.hex()
            self.logger.info(f"Cancel tx sent (nonce {latest_nonce}): {hx}")
            return hx
        except Exception as e:
            self.logger.error(f"cancel_pending error: {e}")
            return None

    async def run_retry_sell_fast(self, headroom_pct: float = 0.02, priority_gwei: float = 0.001, gas_limit: Optional[int] = 300000, slippage_bps: int = 100):
        """Cancel the first pending tx (if any) and retry sell-all with slight headroom/tip.

        Useful when a previous sell is stuck under heavy base fee.
        """
        _ = await self.cancel_pending(headroom_pct=headroom_pct, priority_gwei=priority_gwei)
        # Attempt to sell all with temporary gas policy bump
        _, maxx = await self.get_balances()
        if maxx > 0:
            prev_headroom = self.base_fee_headroom_pct
            prev_priority = self.priority_fee_gwei
            try:
                self.base_fee_headroom_pct = float(headroom_pct)
                self.priority_fee_gwei = float(priority_gwei)
                self.logger.info(f"Retrying sell-all with headroom {self.base_fee_headroom_pct:.2%}, priority {self.priority_fee_gwei} gwei")
                await self.sell_maxx(Decimal(maxx), gas_limit=gas_limit, slippage_bps=slippage_bps)
            finally:
                self.base_fee_headroom_pct = prev_headroom
                self.priority_fee_gwei = prev_priority
        else:
            self.logger.info("No MAXX to sell after cancel")

    async def _log_trade_to_chromadb(self, trade_type: str, amount_maxx: Decimal, amount_eth: Decimal,
                                   tx_hash: str, success: bool, gas_used: int = 0,
                                   gas_cost_eth: Decimal = Decimal('0'), slippage_percent: float = 0.0):
        """Log trade execution to ChromaDB"""
        if not self.chromadb_enabled or not self.chromadb:
            return

        try:
            # Get current market conditions
            eth_balance, maxx_balance = await self.get_balances()

            # Calculate price
            price_eth_per_maxx = float(amount_eth / amount_maxx) if amount_maxx > 0 else 0

            # Prepare trade data
            trade_data = {
                "trade_details": {
                    "trade_type": trade_type,
                    "amount_maxx": float(amount_maxx),
                    "amount_eth": float(amount_eth),
                    "price_eth_per_maxx": price_eth_per_maxx,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "block_number": None,  # Could be fetched if needed
                    "gas_used": gas_used,
                    "gas_cost_eth": float(gas_cost_eth),
                    "slippage_percent": slippage_percent,
                    "transaction_hash": tx_hash,
                    "success": success
                },
                "market_conditions": {
                    "eth_price_usd": 3300.0,  # Could be fetched from API
                    "maxx_market_cap": 1500000.0,  # Could be fetched from API
                    "pool_liquidity": 50000.0,  # Could be fetched from API
                    "volume_24h": 250000.0,  # Could be fetched from API
                    "price_impact_percent": slippage_percent,
                    "market_sentiment": "neutral"
                },
                "performance_metrics": {
                    "pnl_eth": 0.0,  # Will be calculated on sell
                    "pnl_usd": 0.0,
                    "pnl_percent": 0.0,
                    "holding_period_minutes": 0,
                    "success": success,
                    "exit_reason": "manual" if trade_type == "sell" else "entry"
                },
                "trading_pattern": {
                    "position_size_relative": float(amount_eth) / float(eth_balance) if eth_balance > 0 else 0,
                    "timing_pattern": "manual",
                    "coordination_indicator": False,
                    "cluster_activity": False,
                    "preceding_trades": [],
                    "subsequent_trades": []
                },
                "manipulation_analysis": {
                    "price_impact_anomaly": slippage_percent > 1.0,
                    "volume_spike": False,
                    "coordinated_buying": False,
                    "wash_trading_probability": 0.0,
                    "pump_participation": False,
                    "dump_timing": "none"
                },
                "technical_indicators": {
                    "rsi": 50.0,  # Could be calculated
                    "macd_signal": "neutral",
                    "bollinger_position": "middle",
                    "volume_ratio": 1.0,
                    "price_momentum": 0.0,
                    "volatility_index": 0.5
                },
                "execution_quality": {
                    "slippage_vs_expected": slippage_percent,
                    "gas_efficiency": 0.8,
                    "timing_optimization": 0.9,
                    "mev_protection": False,
                    "front_running_detected": False
                }
            }

            # Log to ChromaDB
            await self.chromadb.add_trade_history(self.account.address, trade_data)
            self.logger.debug(f"Trade logged to ChromaDB: {trade_type} {amount_maxx} MAXX")

        except Exception as e:
            self.logger.error(f"Failed to log trade to ChromaDB: {e}")

    async def _log_funding_pattern(self, source_wallet: str, target_wallet: str,
                                 amount_eth: Decimal, transaction_hash: str):
        """Log funding pattern to ChromaDB"""
        if not self.chromadb_enabled or not self.chromadb:
            return

        try:
            funding_data = {
                "transaction_details": {
                    "amount_eth": float(amount_eth),
                    "amount_usd": float(amount_eth) * 3300.0,  # Approximate USD value
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "block_number": None,
                    "gas_used": 21000,
                    "gas_price_gwei": 25.5,
                    "transaction_type": "transfer",
                    "transaction_hash": transaction_hash
                },
                "relationship_metrics": {
                    "relationship_strength": 0.5,
                    "frequency_score": 0.3,
                    "amount_consistency": 0.7,
                    "timing_pattern": "immediate",
                    "recycling_indicator": False,
                    "round_trip_time_hours": 0
                },
                "funding_pattern": {
                    "pattern_type": "single_large",
                    "sequence_position": 1,
                    "total_sequence_size": 1,
                    "coordination_wallets": [],
                    "timing_relationship": "immediate"
                },
                "manipulation_indicators": {
                    "wash_trading_score": 0.0,
                    "layering_indicator": False,
                    "spoofing_probability": 0.0,
                    "pump_and_dump_risk": 0.3,
                    "circular_funding": False,
                    "concealment_attempts": 0
                },
                "network_analysis": {
                    "shortest_path": 1,
                    "centrality_score": 0.5,
                    "betweenness": 0.3,
                    "clustering_coefficient": 0.7,
                    "community_id": "community_001",
                    "bridge_wallet": False
                },
                "temporal_analysis": {
                    "founding_timestamp": datetime.now(timezone.utc).isoformat(),
                    "relationship_duration_days": 0,
                    "interaction_frequency": "sporadic",
                    "trend_analysis": "stable"
                }
            }

            await self.chromadb.add_funding_connection(source_wallet, target_wallet, funding_data)
            self.logger.debug(f"Funding pattern logged to ChromaDB: {source_wallet} -> {target_wallet}")

        except Exception as e:
            self.logger.error(f"Failed to log funding pattern to ChromaDB: {e}")

    async def _update_identity_tracking(self):
        """Update identity tracking based on trading behavior"""
        if not self.chromadb_enabled or not self.chromadb:
            return

        try:
            # Analyze current trading patterns
            total_trades = self.trading_stats['total_trades']
            success_rate = (self.trading_stats['successful_trades'] / max(1, total_trades)) * 100

            # Get current balances
            eth_balance, maxx_balance = await self.get_balances()

            # Calculate behavioral patterns
            identity_data = {
                "identity_type": "trading_wallet",
                "confidence_score": min(0.9, total_trades / 100),  # Increase confidence with more trades
                "risk_level": "medium" if success_rate > 70 else "high",
                "behavioral_patterns": {
                    "trading_frequency": total_trades / max(1, (datetime.now() - self.trading_stats['start_time']).total_seconds() / 3600),
                    "avg_transaction_size": float(eth_balance) / max(1, total_trades),
                    "preferred_tokens": ["MAXX", "ETH"],
                    "coordination_score": 0.3,  # Could be calculated based on timing
                    "timing_patterns": {
                        "most_active_hours": [datetime.now().hour],
                        "day_of_week_patterns": [datetime.now().weekday()],
                        "coordination_timing": "random"
                    }
                },
                "wallet_characteristics": {
                    "age_days": 30,  # Could be calculated from first transaction
                    "total_transactions": total_trades,
                    "unique_counterparties": 5,  # Could be tracked
                    "gas_spending_pattern": "normal",
                    "contract_interactions": ["uniswap"],
                    "chain_diversity": ["base"]
                },
                "ethermax_indicators": {
                    "similarity_score": 0.2,
                    "pattern_matches": [],
                    "network_proximity": 3,
                    "behavioral_fingerprint": f"0x{self.account.address[:8]}...",
                    "cluster_membership": []
                },
                "temporal_evolution": {
                    "first_seen": self.trading_stats['start_time'].isoformat(),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "evolution_trend": "stable",
                    "pattern_changes": []
                },
                "analysis_metadata": {
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                    "analysis_version": "v1.0.0",
                    "data_sources": ["base"],
                    "confidence_factors": ["trading_frequency", "success_rate"],
                    "last_analyzed_block": None
                }
            }

            await self.chromadb.add_identity_tracking(self.account.address, identity_data)
            self.logger.debug("Identity tracking updated in ChromaDB")

        except Exception as e:
            self.logger.error(f"Failed to update identity tracking: {e}")

    async def initialize(self) -> bool:
        """Initialize the master trading system"""
        try:
            self.logger.info("Initializing Master Trading System...")

            # Get Web3 instance
            self.w3 = await self.rpc_manager.get_w3_instance()

            # Create account
            self.account = self.w3.eth.account.from_key(config.ETHEREUM_PRIVATE_KEY)
            self.logger.info(f"Trading account: {self.account.address}")

            # Initialize contracts (ERC20 only; aggregator handles routing)
            self.maxx_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(config.MAXX_CONTRACT_ADDRESS),
                abi=self.erc20_abi
            )

            # Initialize ChromaDB if available
            if self.chromadb_enabled:
                try:
                    self.chromadb = await chromadb_integration.get_chromadb_instance()
                    self.logger.info("ChromaDB integration initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize ChromaDB: {e}")
                    self.chromadb_enabled = False
            else:
                self.logger.info("ChromaDB integration not available")

            # Setup signal handlers
            self._setup_signal_handlers()

            # Initialize trading stats
            self.trading_stats['start_time'] = datetime.now()

            self.logger.info("Master Trading System initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Master Trading System: {e}")
            return False

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def get_balances(self) -> Tuple[Decimal, Decimal]:
        """Get current ETH and MAXX balances"""
        try:
            # ETH balance
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = Decimal(balance_wei) / Decimal(10**18)

            # MAXX balance
            maxx_balance_wei = self.maxx_contract.functions.balanceOf(self.account.address).call()
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            maxx_balance = Decimal(maxx_balance_wei) / Decimal(10 ** maxx_decimals)

            return balance_eth, maxx_balance

        except Exception as e:
            self.logger.error(f"Failed to get balances: {e}")
            return Decimal('0'), Decimal('0')

    async def get_balances_cached(self, min_interval_seconds: int = 15) -> Tuple[Decimal, Decimal]:
        """Get balances with simple caching and 429 handling to avoid RPC rate limits.

        - Returns cached values if called again within min_interval_seconds.
        - On RPC 429 or transient errors, keeps the last cached values and attempts a quick RPC refresh/rotate.
        """
        now = time.time()
        cache = getattr(self, "_balances_cache", None)
        if cache and (now - cache.get("ts", 0)) < max(0, min_interval_seconds):
            return cache["eth"], cache["maxx"]

        # Try up to 2 attempts with a brief backoff and optional RPC refresh
        last_exc = None
        for attempt in range(2):
            try:
                eth, maxx = await self.get_balances()
                # If a failure returned (0,0), treat as failure and try fallback
                if eth == 0 and maxx == 0:
                    raise RuntimeError("zero-balance fetch (likely RPC error)")
                # Cache and return
                self._balances_cache = {"eth": eth, "maxx": maxx, "ts": now}
                return eth, maxx
            except Exception as e:
                last_exc = e
                # Try rotating the RPC on first failure
                try:
                    _ = await self.rpc_manager.get_w3_instance()
                except Exception:
                    pass
                await asyncio.sleep(1.5)

        # On persistent failure, return the last cached values if present, else zeros
        if cache:
            self.logger.warning(f"Using cached balances due to RPC error: {last_exc}")
            return cache["eth"], cache["maxx"]
        self.logger.warning(f"Balance fetch failed with no cache available: {last_exc}")
        return Decimal('0'), Decimal('0')

    async def buy_maxx(self, eth_amount: Decimal, gas_limit: Optional[int] = None, min_maxx_out_wei: Optional[int] = None, slippage_bps: int = 50) -> Optional[str]:
        """Buy MAXX tokens with ETH via KyberSwap aggregator"""
        try:
            self.logger.info(f"Buying MAXX with {eth_amount} ETH")

            # Update trading stats
            self.trading_stats['total_trades'] += 1

            # Check balance
            eth_balance, maxx_balance_before = await self.get_balances()
            if eth_balance < eth_amount:
                self.logger.error(f"Insufficient ETH balance: {eth_balance} < {eth_amount}")
                await self._log_trade_to_chromadb("buy", 0, eth_amount, "", False, 0, 0, 0)
                return None

            # Use Kyber client to build and send the swap
            w3 = await self.rpc_manager.get_w3_instance()
            kc = KyberClient(w3, self.account, system=self, gas_cap=gas_limit)
            eth_amount_wei = int(eth_amount * 10**18)
            txh = kc.buy_eth_to_maxx(eth_amount_wei, slippage_bps=slippage_bps)
            if txh:
                self.logger.info(f"Buy transaction sent: {txh}")
                # Post-trade logging best-effort
                try:
                    _, maxx_after = await self.get_balances()
                    maxx_received = maxx_after - maxx_balance_before
                    await self._log_trade_to_chromadb("buy", maxx_received, eth_amount, txh, True, 0, Decimal('0'), 0.0)
                    await self._update_identity_tracking()
                    # Broadcast trade event to dashboard (best-effort)
                    with suppress(Exception):
                        await self.ws_broadcast_trade('buy', Decimal(maxx_received), Decimal(eth_amount), txh, True)
                except Exception:
                    pass
                return txh
            else:
                self.logger.error("Buy via Kyber failed")
                await self._log_trade_to_chromadb("buy", 0, eth_amount, "", False, 0, Decimal('0'), 0.0)
                return None

        except Exception as e:
            self.logger.error(f"Buy failed: {e}")
            self.trading_stats['failed_trades'] += 1

            # Log failed trade to ChromaDB
            await self._log_trade_to_chromadb("buy", 0, eth_amount, "", False, 0, 0, 0)

            return None

    async def approve_maxx_spending(self, amount: Decimal) -> bool:
        """Approve MAXX spending for router using one-time infinite allowance.

        - Skips if current allowance already covers the requested amount.
        - Sets allowance to uint256 max to avoid repeated approvals.
        - Retries with exponential backoff and RPC rotation on errors (e.g., 429).
        """
        try:
            self.logger.info(f"Approving MAXX spending (infinite): need >= {amount}")

            # Get decimals and convert amount
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** maxx_decimals))
            max_uint256 = (1 << 256) - 1

            # Check current allowance
            current_allowance = self.maxx_contract.functions.allowance(
                self.account.address,
                Web3.to_checksum_address(getattr(config, 'KYBER_ROUTER'))
            ).call()

            if current_allowance >= amount_wei:
                self.logger.info("MAXX spending already approved for required amount")
                return True

            # Get fresh Web3 instance
            w3 = await self.rpc_manager.get_w3_instance()

            # Build approval transaction
            nonce = w3.eth.get_transaction_count(self.account.address)
            gas_params = self._get_gas_params(w3)

            tx_data = self.maxx_contract.functions.approve(
                Web3.to_checksum_address(getattr(config, 'KYBER_ROUTER')),
                max_uint256
            ).build_transaction({
                'from': self.account.address,
                'gas': config.GAS_LIMIT,
                'nonce': nonce,
                **gas_params,
            })

            # Sign and send approval with basic retry/backoff to handle 429s
            retries = 5
            backoff = 1.5
            last_err = None
            for i in range(retries):
                try:
                    signed_tx = w3.eth.account.sign_transaction(tx_data, config.ETHEREUM_PRIVATE_KEY)
                    raw = getattr(signed_tx, 'raw_transaction', None) or getattr(signed_tx, 'rawTransaction', None)
                    tx_hash = w3.eth.send_raw_transaction(raw)

                    if not self.wait_for_receipt:
                        return True
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.receipt_timeout_secs)
                    if receipt.status == 1:
                        self.logger.info(f"MAXX infinite approval confirmed: {tx_hash.hex()}")
                        return True
                    else:
                        self.logger.error(f"MAXX approval failed: {tx_hash.hex()}")
                        return False
                except Exception as e:
                    last_err = e
                    self.logger.error(f"Approval attempt {i+1}/{retries} failed: {e}")
                    # Rotate RPC and rebuild tx with new nonce and gas if possible
                    try:
                        _ = await self.rpc_manager.get_w3_instance()
                        w3 = _
                        nonce = w3.eth.get_transaction_count(self.account.address)
                        gas_params = self._get_gas_params(w3)
                        tx_data = self.maxx_contract.functions.approve(
                            Web3.to_checksum_address(getattr(config, 'KYBER_ROUTER')),
                            max_uint256
                        ).build_transaction({
                            'from': self.account.address,
                            'gas': config.GAS_LIMIT,
                            'nonce': nonce,
                            **gas_params,
                        })
                    except Exception:
                        pass
                    await asyncio.sleep(backoff * (i + 1))

            self.logger.error(f"Approval failed after retries: {last_err}")
            return False

        except Exception as e:
            self.logger.error(f"Approval failed: {e}")
            return False

    async def sell_maxx(self, maxx_amount: Decimal, gas_limit: Optional[int] = None, min_eth_out_wei: Optional[int] = None, slippage_bps: int = 50) -> Optional[str]:
        """Sell MAXX for ETH via KyberSwap aggregator"""
        try:
            self.logger.info(f"Selling {maxx_amount} MAXX")

            # Update trading stats
            self.trading_stats['total_trades'] += 1

            # Check balance
            eth_balance_before, maxx_balance = await self.get_balances()
            if maxx_balance < maxx_amount:
                self.logger.error(f"Insufficient MAXX balance: {maxx_balance} < {maxx_amount}")
                await self._log_trade_to_chromadb("sell", maxx_amount, 0, "", False, 0, 0, 0)
                return None

            # Use Kyber client for sell path
            w3 = await self.rpc_manager.get_w3_instance()
            kc = KyberClient(w3, self.account, system=self, gas_cap=gas_limit)
            # Ensure approval to Kyber router inside kyber_client
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            wei_amt = int(maxx_amount * (10 ** maxx_decimals))
            txh = kc.sell_maxx_to_eth(wei_amt, slippage_bps=slippage_bps)
            if txh:
                self.logger.info(f"Sell transaction sent: {txh}")
                # Post-trade logging best-effort
                try:
                    eth_after, _ = await self.get_balances()
                    eth_received = eth_after - eth_balance_before
                    await self._log_trade_to_chromadb("sell", maxx_amount, eth_received, txh, True, 0, Decimal('0'), 0.0)
                    await self._update_identity_tracking()
                    # Broadcast trade event to dashboard (best-effort)
                    with suppress(Exception):
                        await self.ws_broadcast_trade('sell', Decimal(maxx_amount), Decimal(eth_received), txh, True)
                except Exception:
                    pass
                return txh
            else:
                self.logger.error("Sell via Kyber failed")
                await self._log_trade_to_chromadb("sell", maxx_amount, 0, "", False, 0, Decimal('0'), 0.0)
                return None

        except Exception as e:
            self.logger.error(f"Sell failed: {e}")
            self.trading_stats['failed_trades'] += 1

            # Log failed trade to ChromaDB
            await self._log_trade_to_chromadb("sell", maxx_amount, 0, "", False, 0, 0, 0)

            return None

    async def run_reserve_swing(self, duration_minutes: int = 10, usd_reserve: Decimal = Decimal('10'), gas_limit: Optional[int] = 300000, slippage_bps: int = 100):
        """Alternate sell-all and buy-all respecting a fixed USD ETH reserve.

        - If holding MAXX (> 0), sell all MAXX.
        - Else, buy MAXX with all ETH above usd_reserve (converted via DexScreener).
        - Runs for duration_minutes, waits a few seconds between actions.
        - Uses low gas cap and adjustable slippage for reliability at low fees.
        """
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return
        end = time.time() + duration_minutes * 60
        while time.time() < end and not self.shutdown_event.is_set():
            try:
                prices = self._get_prices()
                if not prices:
                    await asyncio.sleep(3)
                    continue
                eth_usd = Decimal(str(prices.get('eth_usd') or '0'))
                eth_reserve = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

                eth, maxx = await self.get_balances_cached(min_interval_seconds=3)
                if maxx > 0:
                    self.logger.info(f"RESERVE-SWING SELL-ALL | MAXX {maxx}")
                    await self.sell_maxx(Decimal(maxx), gas_limit=gas_limit, slippage_bps=slippage_bps)
                else:
                    avail_eth = Decimal(eth) - eth_reserve
                    if avail_eth > 0:
                        self.logger.info(f"RESERVE-SWING BUY-ALL | ETH {avail_eth:.8f} (reserve {eth_reserve:.8f})")
                        await self.buy_maxx(avail_eth, gas_limit=gas_limit, slippage_bps=slippage_bps)
                    else:
                        self.logger.info("RESERVE-SWING skip: below reserve")
                await asyncio.sleep(6)
            except Exception as e:
                self.logger.error(f"reserve-swing error: {e}")
                await asyncio.sleep(3)

    async def run_interactive_mode(self):
        """Run interactive trading mode"""
        print("\n" + "="*80)
        print("MAXX ECOSYSTEM MASTER TRADING SYSTEM")
        print("="*80)

        while True:
            try:
                # Get current balances
                eth_balance, maxx_balance = await self.get_balances()

                print(f"\nCURRENT BALANCES:")
                print(f"ETH: {eth_balance:.6f} ETH")
                print(f"MAXX: {maxx_balance:,.2f} MAXX")
                print(f"\nTRADING STATS:")
                print(f"Total Trades: {self.trading_stats['total_trades']}")
                print(f"Successful: {self.trading_stats['successful_trades']}")
                print(f"Failed: {self.trading_stats['failed_trades']}")
                print(f"Total Gas Used: {self.trading_stats['total_gas_used']}")

                print(f"\nTRADING OPTIONS:")
                print(f"1. Buy MAXX with {config.TEST_ETH_AMOUNT} ETH (~$1 USD)")
                print(f"2. Sell 50% of MAXX holdings")
                print(f"3. Sell all MAXX holdings")
                print(f"4. Custom buy amount")
                print(f"5. Custom sell amount")
                print(f"6. Run automated trading bot")
                print(f"7. View system status")
                print(f"8. Exit")

                choice = input(f"\nEnter choice (1-8): ").strip()

                if choice == "1":
                    # Buy MAXX with test amount
                    print(f"\nExecuting buy order...")
                    tx_hash = await self.buy_maxx(Decimal(config.TEST_ETH_AMOUNT))
                    if tx_hash:
                        print(f"SUCCESS! Buy transaction: https://basescan.org/tx/{tx_hash}")
                    else:
                        print("FAILED! Buy transaction failed")

                elif choice == "2":
                    # Sell 50% MAXX
                    if maxx_balance > 0:
                        sell_amount = maxx_balance * Decimal('0.5')
                        print(f"\nExecuting sell order (50% of holdings)...")
                        tx_hash = await self.sell_maxx(sell_amount)
                        if tx_hash:
                            print(f"SUCCESS! Sell transaction: https://basescan.org/tx/{tx_hash}")
                        else:
                            print("FAILED! Sell transaction failed")
                    else:
                        print("No MAXX tokens to sell")

                elif choice == "3":
                    # Sell all MAXX
                    if maxx_balance > 0:
                        print(f"\nExecuting sell order (all holdings)...")
                        tx_hash = await self.sell_maxx(maxx_balance)
                        if tx_hash:
                            print(f"SUCCESS! Sell transaction: https://basescan.org/tx/{tx_hash}")
                        else:
                            print("FAILED! Sell transaction failed")
                    else:
                        print("No MAXX tokens to sell")

                elif choice == "4":
                    # Custom buy amount
                    try:
                        amount = float(input("Enter ETH amount to buy: "))
                        if amount > 0:
                            print(f"\nExecuting buy order...")
                            tx_hash = await self.buy_maxx(Decimal(str(amount)))
                            if tx_hash:
                                print(f"SUCCESS! Buy transaction: https://basescan.org/tx/{tx_hash}")
                            else:
                                print("FAILED! Buy transaction failed")
                        else:
                            print("Invalid amount")
                    except ValueError:
                        print("Invalid input")

                elif choice == "5":
                    # Custom sell amount
                    try:
                        amount = float(input("Enter MAXX amount to sell: "))
                        if amount > 0:
                            print(f"\nExecuting sell order...")
                            tx_hash = await self.sell_maxx(Decimal(str(amount)))
                            if tx_hash:
                                print(f"SUCCESS! Sell transaction: https://basescan.org/tx/{tx_hash}")
                            else:
                                print("FAILED! Sell transaction failed")
                        else:
                            print("Invalid amount")
                    except ValueError:
                        print("Invalid input")

                elif choice == "6":
                    # Automated trading bot
                    await self.run_automated_trading()

                elif choice == "7":
                    # System status
                    await self.print_system_status()

                elif choice == "8":
                    # Exit
                    print("Exiting...")
                    break

                else:
                    print("Invalid choice")

                # Wait before next iteration
                if choice != "8":
                    await asyncio.sleep(2)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")

    async def run_automated_trading(self):
        """Run automated trading bot (reactive):
        - Takes profit at +10% from entry; re-enters after -10% drawdown from peak.
        - Prints a 1-second heartbeat with prices and balances.
        """
        print("\nStarting automated reactive bot (+10% TP / -10% re-entry)...")
        print("Press Ctrl+C to stop")
        await self.run_reactive_strategy(
            Decimal('7'),
            Decimal('10'),
            sell_gain_pct=Decimal('0.10'),
            rebuy_drop_pct=Decimal('0.10')
        )

    async def print_system_status(self):
        """Print detailed system status"""
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60)

        # Connection status
        try:
            w3 = await self.rpc_manager.get_w3_instance()
            connected = w3.is_connected()
            chain_id = w3.eth.chain_id if connected else "N/A"
            print(f"Blockchain Connection: {'Connected' if connected else 'Disconnected'}")
            print(f"Chain ID: {chain_id}")
        except Exception as e:
            print(f"Blockchain Connection: Error - {e}")

        # Account info
        print(f"Trading Account: {self.account.address}")

        # Balances
        eth_balance, maxx_balance = await self.get_balances()
        print(f"ETH Balance: {eth_balance:.6f} ETH")
        print(f"MAXX Balance: {maxx_balance:,.2f} MAXX")
        # USD totals (no per-token price print)
        try:
            prices = self._get_prices() or {}
            eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
            maxx_usd = Decimal(str(prices.get('maxx_usd') or '0'))
            eth_value_usd = Decimal(eth_balance) * eth_usd
            maxx_value_usd = Decimal(maxx_balance) * maxx_usd
            total_usd = eth_value_usd + maxx_value_usd
            print(f"MAXX Value (USD): ${maxx_value_usd:.2f}")
            print(f"ETH Value  (USD): ${eth_value_usd:.2f}")
            print(f"Total Wallet USD: ${total_usd:.2f}")
        except Exception as e:
            print(f"USD valuation unavailable: {e}")

        # Total wallet USD using DexScreener prices
        try:
            prices = self._get_prices()
            if prices:
                eth_usd = prices['eth_usd']
                maxx_usd = prices['maxx_usd']
                total_usd = (Decimal(eth_balance) * Decimal(eth_usd)) + (Decimal(maxx_balance) * Decimal(maxx_usd))
                print(f"Total Wallet USD: ${total_usd:.2f} (ETH ${Decimal(eth_balance)*Decimal(eth_usd):.2f} + MAXX ${Decimal(maxx_balance)*Decimal(maxx_usd):.2f})")
        except Exception:
            pass

        # Contract info
        print(f"MAXX Contract: {config.MAXX_CONTRACT_ADDRESS}")
        print(f"Router: {getattr(config, 'KYBER_ROUTER', 'Kyber aggregator')}")

        # Trading stats
        print(f"\nTrading Statistics:")
        print(f"Total Trades: {self.trading_stats['total_trades']}")
        print(f"Successful: {self.trading_stats['successful_trades']}")
        print(f"Failed: {self.trading_stats['failed_trades']}")
        print(f"Success Rate: {(self.trading_stats['successful_trades'] / max(1, self.trading_stats['total_trades']) * 100):.1f}%")
        print(f"Total Gas Used: {self.trading_stats['total_gas_used']}")

        # RPC status
        print(f"\nRPC Status:")
        print(f"Current RPC Index: {self.rpc_manager.current_rpc_index}")
        print(f"Available RPCs: {len(self.rpc_manager.rpc_endpoints)}")
        print(f"Rate Limit: {self.rpc_manager.rate_limiter.max_calls} calls/second")

        # ChromaDB status
        print(f"\nChromaDB Status:")
        if self.chromadb_enabled and self.chromadb:
            try:
                stats = await self.chromadb.get_collection_stats()
                print(f"Identity Collection: {stats['identity_collection'].get('document_count', 0)} documents")
                print(f"Funding Collection: {stats['funding_collection'].get('document_count', 0)} documents")
                print(f"Trade Collection: {stats['trade_collection'].get('document_count', 0)} documents")
                print(f"Total Documents: {stats.get('total_documents', 0)}")
            except Exception as e:
                print(f"Error getting ChromaDB stats: {e}")
        else:
            print("ChromaDB: Not available or disabled")

        # Explorer: Recent Base transactions (requires BASESCAN_API_KEY)
        print("\nExplorer (Base 8453):")
        if EtherscanV2Client is None:
            print("Explorer client unavailable")
        else:
            try:
                client = EtherscanV2Client()
                if not client.is_configured():
                    print("Missing BASESCAN_API_KEY in .env")
                else:
                    txs = client.get_txlist(8453, self.account.address, page=1, offset=5, sort='desc')
                    if not txs:
                        print("No recent transactions or API returned empty")
                    else:
                        for t in txs:
                            h = t.get('hash', '')
                            from_addr = t.get('from', '')
                            to_addr = t.get('to', '')
                            value_wei = int(t.get('value', '0') or 0)
                            value_eth = value_wei / 1e18
                            direction = 'OUT' if from_addr.lower() == self.account.address.lower() else 'IN'
                            print(f"{direction} {value_eth:.6f} ETH | {h[:10]}... -> {to_addr[:8]}... | block {t.get('blockNumber', 'n/a')}")
            except Exception as e:
                print(f"Explorer error: {e}")

    def _get_prices(self) -> Optional[dict]:
        """Fetch MAXX/ETH and USD prices from DexScreener.

        Strategy:
        - Order is selectable via env MAXX_PRICE_SOURCE:
          pair_first (default) | token_first | birdeye_first | birdeye_only
        - Pair method: configured pair endpoint first (fast, specific).
        - Token method: token endpoint selecting the highest-liquidity Base pair.
        - Birdeye method: use Birdeye USD price for MAXX, supplement ETH/USD from DexScreener token method.

        Returns Decimal values: { 'maxx_usd', 'maxx_eth', 'eth_usd' } or None.
        """
        # Helper: build price dict from a DexScreener pair object
        def _from_pair_obj(pobj: dict) -> Optional[dict]:
            try:
                maxx_usd = Decimal(str(pobj.get('priceUsd')))
                maxx_eth = Decimal(str(pobj.get('priceNative')))
                if maxx_usd <= 0 or maxx_eth <= 0:
                    return None
                eth_usd = (maxx_usd / maxx_eth) if maxx_eth > 0 else Decimal('3300')
                return {
                    'maxx_usd': maxx_usd,
                    'maxx_eth': maxx_eth,
                    'eth_usd': eth_usd,
                }
            except Exception:
                return None

        def _dexscreener_pair_method() -> Optional[dict]:
            try:
                pair = os.getenv('MAXX_ETH_POOL') or getattr(config, 'MAXX_ETH_POOL', '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148')
                if pair:
                    url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair}"
                    r = requests.get(url, timeout=10)
                    r.raise_for_status()
                    d = r.json()
                    pobj = (d.get('pairs') or [None])[0]
                    return _from_pair_obj(pobj or {})
            except Exception:
                return None

        def _dexscreener_token_best() -> Tuple[Optional[dict], Optional[dict]]:
            """Return (price_dict, raw_pair) from token endpoint best Base pair."""
            try:
                token = os.getenv('MAXX_CONTRACT_ADDRESS') or getattr(config, 'MAXX_CONTRACT_ADDRESS', '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')
                url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                d = r.json()
                pairs = d.get('pairs') or []
                if not pairs:
                    return None, None
                base_pairs = [p for p in pairs if str(p.get('chainId')).lower() in ('base', '8453')]
                use = base_pairs or pairs
                def _liq_usd(px: dict) -> float:
                    liq = px.get('liquidity')
                    if isinstance(liq, dict):
                        try:
                            return float(liq.get('usd') or 0)
                        except Exception:
                            return 0.0
                    return 0.0
                use.sort(key=_liq_usd, reverse=True)
                raw = use[0]
                return _from_pair_obj(raw), raw
            except Exception:
                return None, None

        def _birdeye_method(supplement_eth_usd: Optional[Decimal]) -> Optional[dict]:
            try:
                api_key = os.getenv('BIRDEYE_API_KEY')
                if not api_key:
                    return None
                token = os.getenv('MAXX_CONTRACT_ADDRESS') or getattr(config, 'MAXX_CONTRACT_ADDRESS', '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')
                url = f"https://public-api.birdeye.so/defi/price"
                params = {'address': token, 'chain': 'base'}
                headers = {'X-API-KEY': api_key}
                r = requests.get(url, params=params, headers=headers, timeout=10)
                r.raise_for_status()
                jd = r.json() or {}
                data = jd.get('data') or {}
                px_usd = data.get('price')
                if px_usd is None:
                    return None
                maxx_usd = Decimal(str(px_usd))
                # We still need maxx_eth and eth_usd; get via token best pair or supplement_eth_usd
                price_dict, raw_pair = _dexscreener_token_best()
                if price_dict:
                    # Replace USD price with Birdeye price but keep eth price/eth_usd derived
                    maxx_eth = Decimal(str(raw_pair.get('priceNative')))
                    if maxx_eth and maxx_eth > 0:
                        eth_usd = maxx_usd / maxx_eth
                    else:
                        eth_usd = price_dict.get('eth_usd') or supplement_eth_usd or Decimal('3300')
                    return {
                        'maxx_usd': maxx_usd,
                        'maxx_eth': maxx_eth if maxx_eth and maxx_eth > 0 else Decimal(str(price_dict.get('maxx_eth') or '0')),
                        'eth_usd': eth_usd,
                    }
                # Last resort: compute with supplement_eth_usd only
                eth_usd = supplement_eth_usd or Decimal('3300')
                # Without maxx_eth we can't return a full dict reliably
                return None
            except Exception:
                return None

        # Determine order from env
        pref = (os.getenv('MAXX_PRICE_SOURCE') or 'pair_first').strip().lower()
        order = []
        if pref == 'token_first':
            order = ['token', 'pair', 'birdeye']
        elif pref == 'birdeye_first':
            order = ['birdeye', 'token', 'pair']
        elif pref == 'birdeye_only':
            order = ['birdeye']
        else:
            order = ['pair', 'token', 'birdeye']

        # Try sources in order
        last_price_dict = None
        for src in order:
            if src == 'pair':
                out = _dexscreener_pair_method()
                if out:
                    return out
            elif src == 'token':
                out, _raw = _dexscreener_token_best()
                if out:
                    return out
            elif src == 'birdeye':
                # Try to supplement with eth_usd from token-best
                token_out, _ = _dexscreener_token_best()
                eth_usd_supp = (token_out or {}).get('eth_usd') if token_out else None
                out = _birdeye_method(supplement_eth_usd=eth_usd_supp)  # type: ignore[arg-type]
                if out:
                    return out
            # keep last for possible diagnostics
            last_price_dict = last_price_dict or None
        return last_price_dict

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
        """Reactive loop that SELLS ALL at +sell_gain_pct, then re-buys after a -rebuy_drop_pct.

        - Start: If holding, set entry; sell all when price hits +sell_gain_pct from entry.
        - After sell: wait for a drop of rebuy_drop_pct from the post-sell peak, then buy using
          min(available ETH beyond reserve, usd_to_spend converted to ETH).
        - Uses cached balances to reduce RPC 429 errors.
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

        entry_usd: Decimal = cur_price_usd
        peak_usd: Decimal = entry_usd
        reentry_anchor_usd: Decimal = Decimal('0')
        last_action_type: Optional[str] = None
        last_action_price_usd: Decimal = Decimal('0')

        st = self._load_reactive_state()
        if st:
            try:
                st_holding = bool(st.get('holding'))
                st_entry = Decimal(str(st.get('entry_usd') or '0'))
                st_peak = Decimal(str(st.get('peak_usd') or '0'))
                st_anchor = Decimal(str(st.get('reentry_anchor_usd') or '0'))
                st_type = st.get('last_action_type') or None
                st_price = Decimal(str(st.get('last_action_price_usd') or '0'))
                if holding:
                    entry_usd = st_entry if st_entry > 0 else (cur_price_usd or st_entry)
                    peak_usd = st_peak if st_peak > 0 else entry_usd
                    last_action_type = st_type or 'buy'
                    last_action_price_usd = st_price if st_price > 0 else entry_usd
                    self.logger.info(
                        f"🔄 Resuming 🟢 HOLDING from state: entry=${entry_usd:.6f} peak=${peak_usd:.6f} last=({last_action_type}) ${last_action_price_usd:.6f}"
                    )
                else:
                    reentry_anchor_usd = st_anchor if st_anchor > 0 else Decimal('0')
                    last_action_type = st_type or 'sell'
                    last_action_price_usd = st_price if st_price > 0 else (st_entry if st_entry > 0 else cur_price_usd)
                    self.logger.info(
                        f"🔄 Resuming 🔴 FLAT from state: last=({last_action_type}) ${last_action_price_usd:.6f} anchor=${reentry_anchor_usd:.6f}"
                    )
            except Exception as e:
                self.logger.debug(f"Persisted state parse issue, using live defaults: {e}")

        if holding and (last_action_type is None):
            if entry_usd <= 0:
                pnow = self._get_prices() or {}
                entry_usd = Decimal(str(pnow.get('maxx_usd') or '0'))
                peak_usd = entry_usd
            self.logger.info(
                f"🔄 Resuming 🟢 HOLDING mode: MAXX balance detected. Baseline entry=${entry_usd:.6f}. Will SELL at +{int(sell_gain_pct*100)}% from here."
            )
            last_action_type = 'buy'
            last_action_price_usd = entry_usd
        if (not holding) and (last_action_type is None):
            self.logger.info("🔍 No MAXX holdings. Monitoring for re-entry conditions.")
            if entry_usd > 0:
                last_action_type = 'sell'
                last_action_price_usd = entry_usd

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
                    if peak_usd == 0 or maxx_usd > peak_usd:
                        peak_usd = maxx_usd

                    if entry_usd > 0 and maxx_usd >= entry_usd * (Decimal('1.0') + sell_gain_pct):
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
                                    self.logger.info(f"⛽ SELL skip: gas ${(total_gas_eth*eth_usd_now):.4f} > cap ${gas_usd_cap}")
                                    await asyncio.sleep(2)
                                    continue
                            if Decimal(cur_eth) < total_gas_eth:
                                self.logger.warning(
                                    f"⚠️ Skip SELL: not enough ETH for gas (need~{total_gas_eth:.6f} ETH, have {Decimal(cur_eth):.6f})"
                                )
                                await asyncio.sleep(2)
                                continue
                            self.logger.info(
                                f"💰 PRE-SELL | 🪙 ETH {Decimal(cur_eth):.6f} | 🏆 MAXX {Decimal(maxx_now):,.2f} | ⛽ gas~{total_gas_eth:.6f} ETH"
                            )
                            self.logger.info(
                                f"📈 SELL: +{int(sell_gain_pct*100)}% reached. Selling {Decimal(maxx_now):.2f} MAXX"
                            )
                            txh = await self.sell_maxx(Decimal(str(maxx_now)), gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"✅ SELL_TX: {txh} | 🔗 https://basescan.org/tx/{txh if txh else ''}")
                            holding = False
                            reentry_anchor_usd = maxx_usd
                            last_action_type = 'sell'
                            last_action_price_usd = maxx_usd
                            # Persist state after SELL
                            self._save_reactive_state({
                                'holding': holding,
                                'entry_usd': float(entry_usd),
                                'peak_usd': float(peak_usd),
                                'reentry_anchor_usd': float(reentry_anchor_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                            })
                else:
                    if reentry_anchor_usd == 0 or maxx_usd > reentry_anchor_usd:
                        reentry_anchor_usd = maxx_usd

                    if reentry_anchor_usd > 0 and maxx_usd <= reentry_anchor_usd * (Decimal('1.0') - rebuy_drop_pct):
                        cur_eth, _ = await self.get_balances_cached(min_interval_seconds=5)
                        w3 = await self.rpc_manager.get_w3_instance()
                        gas_units = int(gas_limit_override or getattr(config, 'GAS_LIMIT', 300000))
                        est_buy_eth = self._estimate_gas_cost_eth(w3, gas_units)
                        if gas_usd_cap is not None and eth_usd > 0 and (est_buy_eth * eth_usd) > gas_usd_cap:
                            self.logger.info(f"⛽ BUY skip: gas ${(est_buy_eth*eth_usd):.4f} > cap ${gas_usd_cap}")
                            await asyncio.sleep(2)
                            continue
                        avail_eth = Decimal(cur_eth) - reserve_eth - est_buy_eth
                        if avail_eth <= 0:
                            self.logger.info("💸 BUY skip: not enough ETH beyond reserve+gas")
                        else:
                            if spend_all or usd_to_spend <= 0:
                                spend_eth = avail_eth
                            else:
                                max_budget_eth = (usd_to_spend / eth_usd) if eth_usd > 0 else avail_eth
                                spend_eth = min(avail_eth, max_budget_eth)
                            self.logger.info(
                                f"📉 REBUY: -{int(rebuy_drop_pct*100)}% from anchor. Buying with {spend_eth:.6f} ETH (reserve {reserve_eth:.6f}, gas~{est_buy_eth:.6f})"
                            )
                            txh = await self.buy_maxx(spend_eth, gas_limit=gas_limit_override, slippage_bps=slippage_bps)
                            self.logger.info(f"✅ BUY_TX: {txh} | 🔗 https://basescan.org/tx/{txh if txh else ''}")
                            holding = True
                            entry_usd = maxx_usd
                            peak_usd = maxx_usd
                            reentry_anchor_usd = Decimal('0')
                            last_action_type = 'buy'
                            last_action_price_usd = maxx_usd
                            # Persist state after BUY
                            self._save_reactive_state({
                                'holding': holding,
                                'entry_usd': float(entry_usd),
                                'peak_usd': float(peak_usd),
                                'reentry_anchor_usd': float(reentry_anchor_usd),
                                'last_action_type': last_action_type,
                                'last_action_price_usd': float(last_action_price_usd),
                            }))

                # Heartbeat
                tick += 1
                eth_bal, maxx_bal = await self.get_balances_cached(min_interval_seconds=20)
                avail_eth_hb = max(Decimal(eth_bal) - reserve_eth, Decimal('0'))
                # Compute entry delta relative to the baseline entry price whenever we have one
                delta_entry = ((maxx_usd / entry_usd) - 1) * 100 if (entry_usd and entry_usd > 0) else Decimal('0')
                delta_since_action = ((maxx_usd / last_action_price_usd) - 1) * 100 if (last_action_price_usd and last_action_price_usd > 0) else Decimal('0')
                ent_sign = '+' if delta_entry > 0 else ('-' if delta_entry < 0 else '0')
                ent_abs = abs(delta_entry)
                act_sign = '+' if delta_since_action > 0 else ('-' if delta_since_action < 0 else '0')
                act_abs = abs(delta_since_action)
                state = 'HOLD' if holding else 'FLAT'
                target_txt = ''
                if holding and entry_usd > 0:
                    target_sell = entry_usd * (Decimal('1.0') + sell_gain_pct)
                    target_txt = f" | 🎯 ${target_sell:.6f}"
                elif (not holding) and reentry_anchor_usd > 0:
                    target_buy = reentry_anchor_usd * (Decimal('1.0') - rebuy_drop_pct)
                    target_txt = f" | 🎯 ${target_buy:.6f}"
                self.logger.info(
                    (
                        "📊 TICK | 💰 MAXX ${:.6f} | 🪙 ETH ${:.2f} | 💵 ETH {:.6f} (avail {:.6f}) | 🏆 MAXXX {:,.2f} | 📈 Entry ${:.6f} Peak ${:.6f} | 📊 entry_change {}{:.2f}% | ⏰ since_last_{} {}{:.2f}% | {} {}{}"
                    ).format(
                        maxx_usd, eth_usd, Decimal(eth_bal), avail_eth_hb,
                        Decimal(maxx_bal), entry_usd, peak_usd,
                        ent_sign, ent_abs,
                        (last_action_type or 'action'), act_sign, act_abs,
                        '🟢 HOLDING' if holding else '🔴 FLAT', state, target_txt
                    )
                )
                # Broadcast a structured TICK for dashboards/phones
                with suppress(Exception):
                    tick_payload = {
                        'maxx_usd': float(maxx_usd),
                        'eth_usd': float(eth_usd),
                        'eth_balance': float(Decimal(eth_bal)),
                        'eth_avail': float(avail_eth_hb),
                        'maxx_balance': float(Decimal(maxx_bal)),
                        'entry_usd': float(entry_usd) if entry_usd else 0.0,
                        'peak_usd': float(peak_usd) if peak_usd else 0.0,
                        'delta_entry': float(ent_abs if ent_sign == '-' else ent_abs) * (-1 if ent_sign == '-' else (1 if ent_sign == '+' else 0)),
                        'last_action_type': last_action_type or 'action',
                        'last_action_usd': float(last_action_price_usd) if last_action_price_usd else 0.0,
                        'delta_since_last': float(act_abs if act_sign == '-' else act_abs) * (-1 if act_sign == '-' else (1 if act_sign == '+' else 0)),
                        'state': state,
                        'target_sell_usd': float(entry_usd * (Decimal('1.0') + sell_gain_pct)) if (state=='HOLD' and entry_usd>0) else None,
                        'target_buy_usd': float(reentry_anchor_usd * (Decimal('1.0') - rebuy_drop_pct)) if (state=='FLAT' and reentry_anchor_usd>0) else None,
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
        """Execute a tiny ETH->MAXX buy with amountOutMin=0 to test router path, respecting USD reserve."""
        if self.w3 is None or self.account is None:
            self.logger.error("System not initialized")
            return

        try:
            # Check USD reserve before proceeding
            prices = self._get_prices()
            if not prices or not prices.get('eth_usd'):
                self.logger.error("Price fetch failed; cannot check reserve")
                return

            eth_usd = Decimal(str(prices['eth_usd']))
            usd_reserve = Decimal('10')  # $10 USD reserve as per system default
            reserve_eth = (usd_reserve / eth_usd) if eth_usd > 0 else Decimal('0')

            # Get current ETH balance
            eth_before, _ = await self.get_balances()
            available_eth = Decimal(str(eth_before)) - reserve_eth

            # Estimate gas cost
            w3 = await self.rpc_manager.get_w3_instance()
            gas_units = int(gas_limit or getattr(config, 'GAS_LIMIT', 300000))
            est_gas_eth = self._estimate_gas_cost_eth(w3, gas_units)

            # Check if we have enough ETH above reserve for trade + gas
            required_eth = eth_amount + est_gas_eth
            if available_eth < required_eth:
                self.logger.warning(
                    f"Tiny buy blocked by reserve: need {required_eth:.8f} ETH (trade {eth_amount:.8f} + gas ~{est_gas_eth:.8f}), "
                    f"but only {available_eth:.8f} ETH available above ${usd_reserve} reserve (reserve: {reserve_eth:.8f} ETH)"
                )
                return

            # Log pre-buy balances
            print(f"Pre-buy ETH: {eth_before:.8f} | Available above reserve: {available_eth:.8f}")

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

        end = time.time() + (duration_minutes * 60)
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
                reserve_eth = (usd_usd / eth_usd) if eth_usd > 0 else Decimal('0')
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

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MAXX Ecosystem Master Trading System")
    parser.add_argument(
        "--mode",
    choices=["interactive", "automated", "test", "status", "reactive", "small-swap", "burst-cycle", "tiny-sell", "tiny-buy", "usd-pingpong", "usd-once", "sell-all", "reserve-swing", "cancel-pending", "retry-sell-fast", "buy-pump-then-dip"],
        default="interactive",
        help="Operating mode"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    # Reactive strategy options
    parser.add_argument("--usd-to-spend", type=float, default=7.0, help="USD to spend per entry (reactive mode, ignored if --spend-all)")
    parser.add_argument("--usd-reserve", type=float, default=10.0, help="USD to keep as ETH reserve (reactive mode)")
    parser.add_argument("--sell-gain-pct", type=float, default=0.10, help="Take-profit threshold for reactive mode (e.g., 0.10 for +10%)")
    parser.add_argument("--rebuy-drop-pct", type=float, default=0.10, help="Re-entry drop threshold for reactive mode (e.g., 0.10 for -10%)")
    parser.add_argument("--reactive-slippage-bps", type=int, default=75, help="Slippage bps for reactive mode")
    parser.add_argument("--reactive-gas-usd-cap", type=float, default=0.015, help="Max USD gas per tx in reactive mode; actions skipped if exceeded")
    parser.add_argument("--reactive-gas-limit", type=int, default=None, help="Optional gas limit override in reactive mode")
    parser.add_argument("--spend-all", action="store_true", help="In reactive mode, buy with all ETH above reserve (minus gas)")
    # Small swap option
    parser.add_argument("--eth-amount", type=float, default=0.0001, help="ETH amount for small-swap validation")
    # Burst-cycle options
    parser.add_argument("--burst-minutes", type=int, default=10, help="Total minutes to run burst cycle")
    parser.add_argument("--burst-interval", type=int, default=1, help="Minutes between actions in burst cycle")
    parser.add_argument("--gas-limit", type=int, default=None, help="Optional lower gas limit to use for txs")
    parser.add_argument("--burst-usd-reserve", type=float, default=10.0, help="USD reserve to keep in ETH while buying (burst)")
    # Tiny trade options
    parser.add_argument("--tiny-sell-eth", type=float, default=0.00001, help="Target ETH out for tiny sell test")
    parser.add_argument("--tiny-buy-eth", type=float, default=0.00000001, help="ETH amount for tiny buy test")
    # USD pingpong options
    parser.add_argument("--usd-minutes", type=int, default=10, help="Minutes to run usd-pingpong")
    parser.add_argument("--usd-amount", type=float, default=1.0, help="USD amount to buy then sell")
    parser.add_argument("--slippage-bps", type=int, default=75, help="Slippage in basis points for Kyber routes (e.g., 75 = 0.75%)")
    parser.add_argument("--gas-usd-cap", type=float, default=0.001, help="Skip trades if estimated gas > this USD amount (default $0.001)")
    # Reserve swing options
    parser.add_argument("--reserve-minutes", type=int, default=10, help="Minutes to run reserve-swing")
    parser.add_argument("--reserve-usd", type=float, default=10.0, help="USD to keep as ETH reserve (swing mode)")
    # Pump-then-dip params
    parser.add_argument("--pump-minutes", type=int, default=15, help="Minutes to run pump-then-dip buy mode")
    parser.add_argument("--pump-gain-pct", type=float, default=0.15, help="Pump threshold (e.g., 0.15 for +15%)")
    parser.add_argument("--dip-drop-pct", type=float, default=0.15, help="Dip threshold from peak (e.g., 0.15 for -15%)")
    parser.add_argument("--cooldown-sec", type=int, default=10, help="Cooldown seconds between buys")
    # Dashboard WebSocket options
    parser.add_argument("--ws-enable", action="store_true", help="Enable dashboard WebSocket broadcaster")
    parser.add_argument("--ws-host", type=str, default="localhost", help="WebSocket host to bind (default localhost)")
    parser.add_argument("--ws-port", type=int, default=8080, help="WebSocket port to bind (default 8080)")
    # Global gas policy (optional overrides)
    parser.add_argument("--global-headroom-pct", type=float, default=None, help="Override base fee headroom pct globally (e.g., 0.0=base only, 0.02=+2%)")
    parser.add_argument("--global-priority-gwei", type=float, default=None, help="Override priority fee gwei globally (e.g., 0.0 for zero tip)")
    # Cancel/Retry options
    parser.add_argument("--headroom-pct", type=float, default=0.02, help="Headroom pct above base fee for cancel/fast retry (e.g., 0.02 = 2%)")
    parser.add_argument("--priority-gwei", type=float, default=0.001, help="Priority fee in gwei for cancel/fast retry")

    args = parser.parse_args()

    # Set log level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, args.log_level))
    # Ensure console handler exists so INFO logs (TICK/status) are visible
    if not root_logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(getattr(logging, args.log_level))
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(ch)

    print("MAXX ECOSYSTEM MASTER TRADING SYSTEM")
    print("="*50)
    print("WARNING: This system executes REAL transactions with REAL money!")
    print(f"Token: MAXX ({config.MAXX_CONTRACT_ADDRESS})")
    print()

    # Create and initialize the system
    system = MasterTradingSystem()
    # Apply global gas overrides if provided
    if args.global_headroom_pct is not None:
        system.base_fee_headroom_pct = float(args.global_headroom_pct)
    if args.global_priority_gwei is not None:
        system.priority_fee_gwei = float(args.global_priority_gwei)

    async def run_system():
        if not await system.initialize():
            print("Failed to initialize system")
            return 1

        # Optionally start WebSocket server and broadcast loop
        if args.ws_enable:
            await system.start_ws_server(host=args.ws_host, port=int(args.ws_port))
            if system.ws_enabled:
                system.ws_broadcast_task = asyncio.create_task(system.ws_broadcast_loop())
        try:
            if args.mode == "interactive":
                await system.run_interactive_mode()
            elif args.mode == "automated":
                await system.run_automated_trading()
            elif args.mode == "test":
                await system.run_single_test()
            elif args.mode == "status":
                await system.print_system_status()
            elif args.mode == "reactive":
                await system.run_reactive_strategy(
                    Decimal(str(args.usd_to_spend)),
                    Decimal(str(args.usd_reserve)),
                    sell_gain_pct=Decimal(str(args.sell_gain_pct)),
                    rebuy_drop_pct=Decimal(str(args.rebuy_drop_pct)),
                    gas_limit_override=(args.reactive_gas_limit if args.reactive_gas_limit is not None else None),
                    slippage_bps=int(args.reactive_slippage_bps),
                    gas_usd_cap=(Decimal(str(args.reactive_gas_usd_cap)) if args.reactive_gas_usd_cap is not None else None),
                    spend_all=bool(args.spend_all)
                )
            elif args.mode == "small-swap":
                await system.run_small_swap(Decimal(str(args.eth_amount)))
            elif args.mode == "burst-cycle":
                await system.run_burst_cycle(
                    duration_minutes=int(args.burst_minutes),
                    interval_minutes=int(args.burst_interval),
                    usd_reserve=Decimal(str(args.burst_usd_reserve)),
                    lower_gas_limit=args.gas_limit
                )
            elif args.mode == "tiny-sell":
                await system.run_tiny_sell(
                    target_eth_out=Decimal(str(args.tiny_sell_eth)),
                    gas_limit=args.gas_limit
                )
            elif args.mode == "tiny-buy":
                await system.run_tiny_buy(
                    eth_amount=Decimal(str(args.tiny_buy_eth)),
                    gas_limit=args.gas_limit
                )
            elif args.mode == "usd-pingpong":
                await system.run_usd_pingpong(
                    duration_minutes=int(args.usd_minutes),
                    usd_amount=Decimal(str(args.usd_amount)),
                    gas_limit=args.gas_limit,
                    slippage_bps=int(args.slippage_bps),
                    gas_usd_cap=Decimal(str(args.gas_usd_cap))
                )
            elif args.mode == "usd-once":
                await system.run_usd_once(
                    usd_amount=Decimal(str(args.usd_amount)),
                    gas_limit=args.gas_limit,
                    slippage_bps=int(args.slippage_bps),
                    gas_usd_cap=Decimal(str(args.gas_usd_cap))
                )
            elif args.mode == "sell-all":
                await system.run_sell_all(gas_limit=args.gas_limit)
            elif args.mode == "reserve-swing":
                await system.run_reserve_swing(
                    duration_minutes=int(args.reserve_minutes),
                    usd_reserve=Decimal(str(args.reserve_usd)),
                    gas_limit=args.gas_limit,
                    slippage_bps=int(args.slippage_bps),
                    gas_usd_cap=Decimal(str(args.gas_usd_cap))
                )
            elif args.mode == "buy-pump-then-dip":
                await system.run_buy_pump_then_dip(
                    duration_minutes=int(args.pump_minutes),
                    usd_reserve=Decimal(str(args.reserve_usd)),
                    pump_gain_pct=Decimal(str(args.pump_gain_pct)),
                    dip_drop_pct=Decimal(str(args.dip_drop_pct)),
                    gas_limit=args.gas_limit,
                    slippage_bps=int(args.slippage_bps),
                    gas_usd_cap=Decimal(str(args.gas_usd_cap)),
                    cooldown_sec=int(args.cooldown_sec)
                )
            elif args.mode == "cancel-pending":
                await system.cancel_pending(headroom_pct=float(args.headroom_pct), priority_gwei=float(args.priority_gwei))
            elif args.mode == "retry-sell-fast":
                await system.run_retry_sell_fast(
                    headroom_pct=float(args.headroom_pct),
                    priority_gwei=float(args.priority_gwei),
                    gas_limit=args.gas_limit or 300000,
                    slippage_bps=int(args.slippage_bps)
                )
            return 0
        finally:
            if system.ws_enabled:
                with suppress(Exception):
                    await system.stop_ws_server()

    try:
        rc = asyncio.run(run_system())
        return rc
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
