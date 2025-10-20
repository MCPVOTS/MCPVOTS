"""
Anchor/6% re-entry analyzer using Zapper price ticks for MAXX (or any token).

What it does:
- Fetches historical price ticks via Zapper GraphQL (see zapper_client.py)
- Simulates a simple rule:
    - Start in token (fully invested) at first price.
    - When price >= anchor * (1 + sell_up_pct): SELL all, record anchor-sell event; set new anchor to sell price.
    - While out of token, when price <= anchor * (1 - buy_down_pct): BUY all, record re-entry event; set new anchor to buy price.
- Persists events into SQLite tables (in maxx_intelligence.db by default):
    - anchor_events (SELL events)
    - reentry_signals (BUY events)
- Emits a JSON summary report with events and basic performance metrics.

Usage (PowerShell):
    $env:ZAPPER_API_KEY = "<your_key>"
    python .\zapper_anchor_reentry_analyzer.py \
      --token 0x1bff6cbd036162e3535b7969f63fd8043ccc1433 \
      --chain 8453 --sell-up 0.06 --buy-down 0.06 --json-out maxx_anchor_reentry_signals.json

Notes:
- Zapper API key required in environment (ZAPPER_API_KEY).
- Keep timeframes conservative to conserve credits; default tries HOUR, FOUR_HOURS, DAY.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from env_loader import load_env_once
from zapper_client import ZapperClient, ZapperClientError


@dataclass
class Tick:
    open: float
    median: float
    close: float
    timestamp: int


def _to_ticks(raw: List[Dict]) -> List[Tick]:
    out: List[Tick] = []
    seen = set()
    for r in raw or []:
        try:
            ts = int(r.get("timestamp") or 0)
            cl = float(r.get("close") or 0) or float(r.get("median") or 0) or float(r.get("open") or 0)
            key = (ts, cl)
            if ts and cl and key not in seen:
                seen.add(key)
                out.append(
                    Tick(
                        open=float(r.get("open") or 0),
                        median=float(r.get("median") or 0),
                        close=float(r.get("close") or 0),
                        timestamp=ts,
                    )
                )
        except Exception:
            continue
    out.sort(key=lambda t: t.timestamp)
    return out


def simulate_with_events(
    prices: List[Tuple[int, float]],
    sell_up_pct: float,
    buy_down_pct: float,
    start_usd: float = 100.0,
    start_in_token: bool = True,
) -> Tuple[float, List[Dict], List[Dict]]:
    """Run the anchor/sell and re-entry strategy and capture detailed events.

    Returns: (final_value_usd, sells, buys)
    - sells: list of dicts { ts, price, anchor_price, gain_pct }
    - buys:  list of dicts { ts, price, anchor_price, drop_pct }
    """
    if not prices:
        return 0.0, [], []

    first_price = prices[0][1]
    in_token = start_in_token
    if in_token:
        token = start_usd / first_price
        usd = 0.0
        anchor = first_price
    else:
        token = 0.0
        usd = start_usd
        anchor = first_price  # used for the first buy check

    sells: List[Dict] = []
    buys: List[Dict] = []

    for ts, p in prices[1:]:
        if p <= 0:
            continue
        if in_token:
            # take-profit condition
            if p >= anchor * (1.0 + sell_up_pct):
                usd = token * p
                token = 0.0
                in_token = False
                gain_pct = (p / anchor) - 1.0 if anchor > 0 else 0.0
                sells.append({
                    "ts": ts,
                    "price": p,
                    "anchor_price": anchor,
                    "gain_pct": gain_pct,
                })
                anchor = p  # new anchor at the executed sell price
        else:
            # re-entry condition
            if p <= anchor * (1.0 - buy_down_pct):
                token = usd / p
                usd = 0.0
                in_token = True
                drop_pct = 1.0 - (p / anchor) if anchor > 0 else 0.0
                buys.append({
                    "ts": ts,
                    "price": p,
                    "anchor_price": anchor,
                    "drop_pct": drop_pct,
                })
                anchor = p

    final_value = token * prices[-1][1] if in_token else usd
    return final_value, sells, buys


def ensure_tables(db_path: str):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS anchor_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER,
            price REAL,
            anchor_price REAL,
            gain_pct REAL,
            action TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reentry_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER,
            price REAL,
            anchor_price REAL,
            drop_pct REAL,
            action TEXT
        )
        """
    )
    con.commit()
    con.close()


def persist_events(db_path: str, sells: List[Dict], buys: List[Dict]):
    if not (sells or buys):
        return
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for e in sells:
        cur.execute(
            "INSERT INTO anchor_events (ts, price, anchor_price, gain_pct, action) VALUES (?, ?, ?, ?, ?)",
            (int(e["ts"]), float(e["price"]), float(e["anchor_price"]), float(e["gain_pct"]), "SELL"),
        )
    for e in buys:
        cur.execute(
            "INSERT INTO reentry_signals (ts, price, anchor_price, drop_pct, action) VALUES (?, ?, ?, ?, ?)",
            (int(e["ts"]), float(e["price"]), float(e["anchor_price"]), float(e["drop_pct"]), "BUY"),
        )
    con.commit()
    con.close()


def save_json(path: str, payload: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    load_env_once()
    ap = argparse.ArgumentParser(description="Anchor/6% re-entry analyzer using Zapper price ticks")
    ap.add_argument("--token", default="0x1bff6cbd036162e3535b7969f63fd8043ccc1433", help="Token address (MAXX on Base)")
    ap.add_argument("--chain", type=int, default=8453, help="Chain ID (Base=8453)")
    ap.add_argument("--currency", default="USD", help="Currency enum for priceTicks (e.g., USD)")
    ap.add_argument(
        "--timeframes",
        nargs="*",
        default=["HOUR", "FOUR_HOURS", "DAY"],
        help="TimeFrame candidates to try (e.g., FIFTEEN_MINUTES, HOUR, FOUR_HOURS, DAY)",
    )
    ap.add_argument("--sell-up", type=float, default=0.06, help="Sell after rise fraction (e.g., 0.06 for 6%)")
    ap.add_argument("--buy-down", type=float, default=0.06, help="Buy after drop fraction (e.g., 0.06 for 6%)")
    ap.add_argument("--base-usd", type=float, default=100.0, help="Starting USD for toy performance calc")
    ap.add_argument("--start-in-token", action="store_true", default=True, help="Start simulation in token (default)")
    ap.add_argument("--start-in-usd", action="store_true", help="Start simulation in USD (overrides --start-in-token)")
    ap.add_argument("--db-path", default="data/maxx_intelligence.db", help="Path to SQLite database")
    ap.add_argument("--json-out", default="maxx_anchor_reentry_signals.json", help="Path to JSON output file")
    ap.add_argument("--no-sql", action="store_true", help="Do not write to SQLite, JSON only")
    args = ap.parse_args()

    client = ZapperClient()
    try:
        raw = client.fetch_price_ticks(
            token_address=args.token,
            chain_id=args.chain,
            currency=args.currency,
            timeframe_candidates=args.timeframes,
        )
    finally:
        client.close()

    ticks = _to_ticks(raw)
    if not ticks:
        print("No price ticks available from Zapper; aborting.")
        return

    # Use the most recent timeframe data series as-is
    series: List[Tuple[int, float]] = [(t.timestamp, (t.close or t.median or t.open)) for t in ticks if (t.close or t.median or t.open)]

    start_in_token = not args.start_in_usd
    final_usd, sells, buys = simulate_with_events(
        series, sell_up_pct=args.sell_up, buy_down_pct=args.buy_down, start_usd=args.base_usd, start_in_token=start_in_token
    )

    # Persist
    if not args.no_sql:
        ensure_tables(args.db_path)
        persist_events(args.db_path, sells, buys)

    # Build JSON out
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "token": args.token,
        "chain_id": args.chain,
        "rules": {
            "sell_up_pct": args.sell_up,
            "buy_down_pct": args.buy_down,
            "start_in_token": start_in_token,
        },
        "counts": {"sells": len(sells), "buys": len(buys)},
        "performance_toy": {"base_usd": args.base_usd, "final_usd": final_usd, "return_pct": (final_usd / args.base_usd - 1.0) if args.base_usd else 0.0},
        "events": {
            "anchor_sells": [
                {
                    **e,
                    "ts_iso": datetime.utcfromtimestamp(int(e["ts"])) .isoformat() + "Z",
                }
                for e in sells
            ],
            "reentries": [
                {
                    **e,
                    "ts_iso": datetime.utcfromtimestamp(int(e["ts"])) .isoformat() + "Z",
                }
                for e in buys
            ],
        },
        "data_points": len(series),
        "time_range": {
            "from": datetime.utcfromtimestamp(series[0][0]).isoformat() + "Z",
            "to": datetime.utcfromtimestamp(series[-1][0]).isoformat() + "Z",
        },
    }

    save_json(args.json_out, report)
    print(f"Saved anchor/re-entry report to {args.json_out} | sells={len(sells)} buys={len(buys)}")


if __name__ == "__main__":
    main()
