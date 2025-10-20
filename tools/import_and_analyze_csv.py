#!/usr/bin/env python3
r"""
Import a BaseScan/Etherscan CSV for MAXX transfers and generate intelligence outputs.

Usage (PowerShell):
    python .\import_and_analyze_csv.py --csv "c:\\PumpFun_Ecosystem\\ECOSYSTEM_UNIFIED\\export-token-0xFB7a83abe4F4A4E51c77B92E521390B769ff6467.csv"
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from env_loader import load_env_once
from maxx_intelligence_analyzer import MAXXIntelligenceAnalyzer


async def run(csv_path: str):
    analyzer = MAXXIntelligenceAnalyzer()
    # Import trades from CSV
    trades = await analyzer.import_trades_from_csv(csv_path)
    # Quick analytics on the imported trades
    pumps = await analyzer.analyze_pump_patterns(trades)
    whales = await analyzer.identify_whale_activity(trades)
    coordinated = await analyzer.detect_coordinated_activity(trades)
    await analyzer.generate_trading_signals(trades, pumps, whales, coordinated)
    # Export a compact report (uses DB aggregates too)
    await analyzer.export_intelligence_report()


def main():
    load_env_once()
    ap = argparse.ArgumentParser(description="Import MAXX CSV and analyze")
    ap.add_argument("--csv", required=True, help="Path to CSV export for the MAXX token")
    args = ap.parse_args()
    path = Path(args.csv)
    if not path.exists():
        raise SystemExit(f"CSV not found: {path}")
    asyncio.run(run(str(path)))


if __name__ == "__main__":
    main()
