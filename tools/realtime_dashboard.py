#!/usr/bin/env python3
"""
Realtime MAXX Dashboard (1s refresh)
- Collects: Birdeye price + token info, DexScreener pair stats, on-chain balances and block/gas
- Renders: High-contrast terminal dashboard (prefers 'rich'; falls back to ANSI)
- Rate limits: Price(1s), DexScreener(10s), TokenInfo(30s), Chain(5s)

Controls:
- Reserve: keep 0.001 ETH unspent in availability calculation
"""
import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

import aiohttp
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.text import Text
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False

from decimal import Decimal

# Local imports
try:
    import standalone_config as cfg
except Exception:
    class _Cfg:
        CHAIN_ID = 8453
        MAXX_CONTRACT_ADDRESS = "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"
        WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
        LOG_LEVEL = "INFO"
    cfg = _Cfg()


MAXX = cfg.MAXX_CONTRACT_ADDRESS
DEX_PAIR = "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148"
BIRDEYE_BASE = "https://public-api.birdeye.so"
# Prefer environment override for API keys
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "cafe578a9ee7495f9de4c9e390f31c24")

RESERVE_ETH = Decimal("0.001")


@dataclass
class DashboardState:
    # Timestamps
    last_update_price: Optional[float] = None
    last_update_info: Optional[float] = None
    last_update_dex: Optional[float] = None
    last_update_chain: Optional[float] = None

    # Price + info
    price_usd: Optional[float] = None
    price_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity_usd: Optional[float] = None
    market_cap: Optional[float] = None

    # DexScreener extras
    ds_price_usd: Optional[float] = None
    ds_buys_24h: Optional[int] = None
    ds_sells_24h: Optional[int] = None

    # Chain
    latest_block: Optional[int] = None
    base_fee_gwei: Optional[float] = None
    gas_price_gwei: Optional[float] = None

    # Wallet
    wallet_eth: Decimal = Decimal(0)
    wallet_maxx: Decimal = Decimal(0)
    available_eth: Decimal = Decimal(0)

    # Meta
    errors: Dict[str, str] = field(default_factory=dict)


async def fetch_birdeye_price(session: aiohttp.ClientSession, state: DashboardState):
    url = f"{BIRDEYE_BASE}/defi/price"
    params = {"address": MAXX}
    try:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("success") and data.get("data"):
                    state.price_usd = float(data["data"].get("price") or 0)
                    state.last_update_price = time.time()
                    state.errors.pop("price", None)
                    return
            state.errors["price"] = f"HTTP {resp.status}"
    except Exception as e:
        state.errors["price"] = str(e)


async def fetch_birdeye_info(session: aiohttp.ClientSession, state: DashboardState):
    url = f"{BIRDEYE_BASE}/public/tokenv2/token_info"
    params = {"address": MAXX}
    try:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("success") and data.get("data"):
                    token = data["data"]
                    state.price_24h = float(token.get("priceChange24h") or 0)
                    state.volume_24h = float(token.get("volume24h") or 0)
                    state.liquidity_usd = float(token.get("liquidity") or 0)
                    state.market_cap = float(token.get("mc") or 0)
                    state.last_update_info = time.time()
                    state.errors.pop("info", None)
                    return
            state.errors["info"] = f"HTTP {resp.status}"
    except Exception as e:
        state.errors["info"] = str(e)


async def fetch_dexscreener(state: DashboardState):
    import aiohttp
    url = f"https://api.dexscreener.com/latest/dex/pairs/base/{DEX_PAIR}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pair = None
                    if isinstance(data, dict):
                        if isinstance(data.get("pair"), dict):
                            pair = data["pair"]
                        elif isinstance(data.get("pairs"), list) and data["pairs"]:
                            pair = data["pairs"][0]
                    if pair:
                        state.ds_price_usd = float(pair.get("priceUsd") or 0)
                        txns = (pair.get("txns") or {}).get("h24") or {}
                        state.ds_buys_24h = int(txns.get("buys") or 0)
                        state.ds_sells_24h = int(txns.get("sells") or 0)
                        state.last_update_dex = time.time()
                        state.errors.pop("dex", None)
                        return
                state.errors["dex"] = f"HTTP {resp.status}"
    except Exception as e:
        state.errors["dex"] = str(e)


async def fetch_chain_and_balances(state: DashboardState):
    # Use existing MasterTradingSystem for w3 and balances
    from master_trading_system import MasterTradingSystem
    sys_inst = MasterTradingSystem()
    if not await sys_inst.initialize():
        state.errors["chain"] = "init failed"
        return
    try:
        w3 = sys_inst.w3
        state.latest_block = int(w3.eth.block_number)
        try:
            # web3 v6 base fee per gas (wei)
            base_fee = w3.eth.get_block("latest").baseFeePerGas  # type: ignore[attr-defined]
            state.base_fee_gwei = float(base_fee) / 1e9 if base_fee is not None else None
        except Exception:
            state.base_fee_gwei = None

        try:
            gas_price = w3.eth.gas_price
            state.gas_price_gwei = float(gas_price) / 1e9
        except Exception:
            state.gas_price_gwei = None

        # Balances
        eth_bal, maxx_bal = await sys_inst.get_balances()
        state.wallet_eth = eth_bal
        state.wallet_maxx = maxx_bal
        state.available_eth = max(Decimal(0), eth_bal - RESERVE_ETH)
        state.last_update_chain = time.time()
        state.errors.pop("chain", None)
    except Exception as e:
        state.errors["chain"] = str(e)


def _format_usd(v: Optional[float]) -> str:
    if v is None:
        return "-"
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v/1_000:.2f}K"
    return f"${v:.4f}" if v < 1 else f"${v:.2f}"


def _render_plain(state: DashboardState):
    os.system("cls" if os.name == "nt" else "clear")
    # Basic ANSI colors: orange approximated by yellow, matrix green by bright green
    Y = "\033[33m"  # yellow/orange
    G = "\033[92m"  # bright green
    R = "\033[91m"  # red
    C = "\033[96m"  # cyan
    W = "\033[97m"  # white
    B = "\033[90m"  # gray
    X = "\033[0m"   # reset

    print(f"{B}==== {Y}MAXX REALTIME DASHBOARD{B} | {datetime.now().strftime('%H:%M:%S')} ===={X}")
    price = state.price_usd or state.ds_price_usd
    ch = state.price_24h or 0
    ch_col = G if ch >= 0 else R
    print(f"{W}Price:{X} {G if price else B}{price if price else '-':>12} USD  {W}24h:{X} {ch_col}{ch:+.2f}%{X}  {W}Vol24h:{X} {C}{_format_usd(state.volume_24h)}{X}")
    print(f"{W}MCap:{X} {C}{_format_usd(state.market_cap)}{X}   {W}Liq:{X} {C}{_format_usd(state.liquidity_usd)}{X}   {W}Dex Buys/Sells 24h:{X} {G}{state.ds_buys_24h or 0}{X}/{R}{state.ds_sells_24h or 0}{X}")
    print()
    print(f"{W}Block:{X} {state.latest_block or '-'}   {W}BaseFee:{X} {state.base_fee_gwei if state.base_fee_gwei is not None else '-'} gwei   {W}Gas:{X} {state.gas_price_gwei if state.gas_price_gwei is not None else '-'} gwei")
    print(f"{W}ETH:{X} {G}{state.wallet_eth:.6f}{X}  {W}MAXX:{X} {G}{state.wallet_maxx:,.2f}{X}  {W}Avail ETH:{X} {G}{state.available_eth:.6f}{X}  {B}(reserve {RESERVE_ETH} ETH){X}")
    if state.errors:
        print(f"\n{R}Errors:{X} " + ", ".join(f"{k}:{v}" for k, v in state.errors.items()))


def _render_rich(state: DashboardState, console: Console):
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=1),
    )

    title = Text(" MAXX REALTIME DASHBOARD ", style="bold black on orange1")
    subtitle = Text(datetime.now().strftime(" %H:%M:%S "), style="bold white on grey19")
    layout["header"].update(Panel(title + subtitle, style="grey19"))

    # Left: Market, Right: Chain/Wallet
    body = Layout()
    body.split_row(Layout(name="market"), Layout(name="chain"))

    # Market table
    mt = Table(expand=True, box=None, show_edge=False)
    mt.add_column("Metric", style="bold bright_white")
    mt.add_column("Value", style="green1")
    price = state.price_usd or state.ds_price_usd
    mt.add_row("Price (USD)", f"{price:.8f}" if price else "-")
    ch = state.price_24h
    ch_style = "green1" if (ch or 0) >= 0 else "red1"
    mt.add_row("24h Change", Text(f"{ch:+.2f}%" if ch is not None else "-", style=ch_style))
    mt.add_row("Volume 24h", _format_usd(state.volume_24h))
    mt.add_row("Market Cap", _format_usd(state.market_cap))
    mt.add_row("Liquidity", _format_usd(state.liquidity_usd))
    mt.add_row("Dex Buy/Sell 24h", f"[green1]{state.ds_buys_24h or 0}[/]/[red1]{state.ds_sells_24h or 0}")
    body["market"].update(Panel(mt, title="Market", border_style="orange1"))

    # Chain table
    ct = Table(expand=True, box=None, show_edge=False)
    ct.add_column("Metric", style="bold bright_white")
    ct.add_column("Value", style="cyan1")
    ct.add_row("Block", str(state.latest_block or "-"))
    ct.add_row("Base Fee (gwei)", f"{state.base_fee_gwei:.4f}" if state.base_fee_gwei is not None else "-")
    ct.add_row("Gas Price (gwei)", f"{state.gas_price_gwei:.4f}" if state.gas_price_gwei is not None else "-")
    ct.add_row("ETH", f"{state.wallet_eth:.6f}")
    ct.add_row("MAXX", f"{state.wallet_maxx:,.2f}")
    ct.add_row("Available ETH", f"{state.available_eth:.6f} (reserve {RESERVE_ETH})")
    err_text = ", ".join(f"{k}:{v}" for k, v in state.errors.items()) if state.errors else "OK"
    body["chain"].update(Panel(ct, title=f"Chain/Wallet  [{'red1' if state.errors else 'green1'}]{err_text}", border_style="orange1"))

    layout["body"].update(body)
    layout["footer"].update(Text("Refresh: 1s  |  Sources: Birdeye, DexScreener, Base RPC", style="bright_black"))
    console.print(layout)


async def renderer(state: DashboardState):
    console = Console() if RICH_AVAILABLE else None
    while True:
        try:
            if RICH_AVAILABLE:
                Console().clear()
                _render_rich(state, console)
            else:
                _render_plain(state)
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(1)


async def run_dashboard():
    state = DashboardState()
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    async with aiohttp.ClientSession(headers=headers) as session:
        # Initial chain/balances fetch
        await fetch_chain_and_balances(state)

        async def loop_price():
            while True:
                await fetch_birdeye_price(session, state)
                await asyncio.sleep(1)

        async def loop_info():
            while True:
                await fetch_birdeye_info(session, state)
                await asyncio.sleep(30)

        async def loop_dex():
            while True:
                await fetch_dexscreener(state)
                await asyncio.sleep(10)

        async def loop_chain():
            while True:
                await fetch_chain_and_balances(state)
                await asyncio.sleep(5)

        tasks = [
            asyncio.create_task(renderer(state)),
            asyncio.create_task(loop_price()),
            asyncio.create_task(loop_info()),
            asyncio.create_task(loop_dex()),
            asyncio.create_task(loop_chain()),
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            for t in tasks:
                t.cancel()


def main():
    try:
        asyncio.run(run_dashboard())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
