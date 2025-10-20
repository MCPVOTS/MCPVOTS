#!/usr/bin/env python3
"""
Unified launcher: starts the phone dashboard server and the master trading system together.

Examples:
  python run_master_with_dashboard.py --mode reactive --port 8123 --host 0.0.0.0 \
    --usd-to-spend 7 --usd-reserve 10 --sell-gain 0.06 --rebuy-drop 0.06

  python run_master_with_dashboard.py --mode status --port 8123 --host 127.0.0.1
"""
import argparse
import asyncio
import logging
import os
from decimal import Decimal

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from phone_dashboard_server import PhoneDashboardServer
from master_trading_system import MasterTradingSystem


async def run(mode: str,
              host: str,
              port: int,
              log_file: str,
              usd_to_spend: Decimal,
              usd_reserve: Decimal,
              sell_gain: Decimal,
              rebuy_drop: Decimal,
              reactive_slippage_bps: int,
              reactive_gas_usd_cap: Decimal | None,
              reactive_gas_limit: int | None,
              spend_all: bool):
    # Logging to both console and file (dashboard tails the same file)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(fh)

    # Start dashboard
    dash = PhoneDashboardServer(host=host, port=port, log_file=log_file)
    await dash.start()

    # Start trading system
    system = MasterTradingSystem()
    ok = await system.initialize()
    if not ok:
        print("Failed to initialize trading system")
        return 1

    if mode == 'status':
        await system.print_system_status()
        # keep dashboard running for a short while so you can open it
        await asyncio.sleep(60)
        return 0
    elif mode == 'reactive':
        await system.run_reactive_strategy(
            usd_to_spend,
            usd_reserve,
            sell_gain_pct=sell_gain,
            rebuy_drop_pct=rebuy_drop,
            gas_limit_override=reactive_gas_limit,
            slippage_bps=reactive_slippage_bps,
            gas_usd_cap=reactive_gas_usd_cap,
            spend_all=spend_all,
        )
        return 0
    else:
        print(f"Unsupported mode: {mode}")
        return 2


def main():
    ap = argparse.ArgumentParser(description="Run trading system + phone dashboard together")
    ap.add_argument('--mode', choices=['reactive', 'status'], default='reactive')
    ap.add_argument('--host', default=os.getenv('PHONE_DASHBOARD_HOST', '0.0.0.0'))
    ap.add_argument('--port', type=int, default=int(os.getenv('PHONE_DASHBOARD_PORT', '8123')))
    ap.add_argument('--log-file', default=os.getenv('TRANSACTION_LOG_FILE', 'real_trading_transactions.log'))
    ap.add_argument('--usd-to-spend', type=float, default=7.0)
    ap.add_argument('--usd-reserve', type=float, default=10.0)
    ap.add_argument('--sell-gain', type=float, default=0.06)
    ap.add_argument('--rebuy-drop', type=float, default=0.06)
    ap.add_argument('--reactive-slippage-bps', type=int, default=75)
    ap.add_argument('--reactive-gas-usd-cap', type=float, default=0.015)
    ap.add_argument('--reactive-gas-limit', type=int, default=None)
    ap.add_argument('--spend-all', action='store_true')
    args = ap.parse_args()

    try:
        rc = asyncio.run(run(
            mode=args.mode,
            host=args.host,
            port=int(args.port),
            log_file=str(args.log_file),
            usd_to_spend=Decimal(str(args.usd_to_spend)),
            usd_reserve=Decimal(str(args.usd_reserve)),
            sell_gain=Decimal(str(args.sell_gain)),
            rebuy_drop=Decimal(str(args.rebuy_drop)),
            reactive_slippage_bps=int(args.reactive_slippage_bps),
            reactive_gas_usd_cap=(Decimal(str(args.reactive_gas_usd_cap)) if args.reactive_gas_usd_cap is not None else None),
            reactive_gas_limit=(int(args.reactive_gas_limit) if args.reactive_gas_limit is not None else None),
            spend_all=bool(args.spend_all),
        ))
    except KeyboardInterrupt:
        rc = 0
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
