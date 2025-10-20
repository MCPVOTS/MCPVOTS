r"""
Backtest and suggest sell/buy thresholds using Zapper price ticks for MAXX.

- Pulls OHLC-like ticks from Zapper GraphQL via zapper_client.py
- Simulates a simple strategy: sell after X% rise from anchor; re-buy after Y% drop from the post-sell anchor
- Scans a small grid around 10%/10% and prints the best combo by total return

Usage (PowerShell):
    $env:ZAPPER_API_KEY = "<your_key>"
    python .\zapper_threshold_optimizer.py --token 0x1bff6cbd036162e3535b7969f63fd8043ccc1433 --chain 8453 --base-usd 100.0

Notes:
  - Does not modify any live code; read-only analytics
  - Keep runs short to conserve credits; defaults to ~1H tick granularity if available
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Dict, Tuple

from zapper_client import ZapperClient


@dataclass
class Tick:
    open: float
    median: float
    close: float
    timestamp: int


def to_ticks(raw: List[Dict]) -> List[Tick]:
    ticks: List[Tick] = []
    for r in raw:
        try:
            ticks.append(
                Tick(
                    open=float(r.get("open") or 0),
                    median=float(r.get("median") or 0),
                    close=float(r.get("close") or 0),
                    timestamp=int(r.get("timestamp") or 0),
                )
            )
        except Exception:
            continue
    # Deduplicate and sort by timestamp
    uniq = {(t.timestamp, t.close): t for t in ticks}
    out = sorted(uniq.values(), key=lambda x: x.timestamp)
    return out


def simulate_strategy(
    prices: List[float],
    sell_up_pct: float,  # e.g., 0.10 for 10%
    buy_down_pct: float,  # e.g., 0.10 for 10%
    start_usd: float = 100.0,
) -> Tuple[float, int, int]:
    """
    Simple 1-position strategy:
      - Start fully in the asset.
      - Track an anchor (last buy price). If price rises >= sell_up_pct from anchor -> sell all to USD, set new anchor at sell price.
      - While in USD, if price drops >= buy_down_pct from last sell anchor -> buy all back, set anchor at buy price.
      - No fees/slippage modeled for simplicity.

    Returns: (final_value_usd, sell_count, buy_count)
    """
    if not prices:
        return 0.0, 0, 0

    anchor = prices[0]
    usd = 0.0
    token = start_usd / anchor  # start fully invested
    in_token = True
    sells = 0
    buys = 0

    for p in prices[1:]:
        if in_token:
            # Check for take-profit
            if p >= anchor * (1.0 + sell_up_pct):
                usd = token * p
                token = 0.0
                in_token = False
                sells += 1
                anchor = p  # set a new anchor at the sell price
        else:
            # Check for re-entry after drop from post-sell anchor
            if p <= anchor * (1.0 - buy_down_pct):
                token = usd / p
                usd = 0.0
                in_token = True
                buys += 1
                anchor = p

    final_value = token * prices[-1] if in_token else usd
    return final_value, sells, buys


def grid_search(prices: List[float], base_usd: float) -> Tuple[Tuple[float, float], Dict[str, float]]:
    """
    Search a small grid around 10%/10%, e.g., 6%..16% in 2% steps.
    Returns ((sell_up_pct, buy_down_pct), metrics)
    """
    best = None
    best_metrics = {}
    for su in [x / 100.0 for x in range(6, 18, 2)]:
        for bd in [x / 100.0 for x in range(6, 18, 2)]:
            final_usd, sells, buys = simulate_strategy(prices, su, bd, start_usd=base_usd)
            ret = (final_usd - base_usd) / base_usd if base_usd else 0.0
            score = final_usd  # simple objective
            if best is None or score > best:
                best = score
                best_metrics = {
                    "sell_up_pct": su,
                    "buy_down_pct": bd,
                    "final_usd": final_usd,
                    "return_pct": ret,
                    "sells": sells,
                    "buys": buys,
                }
    return (best_metrics["sell_up_pct"], best_metrics["buy_down_pct"]), best_metrics


def main():
    ap = argparse.ArgumentParser(description="Optimize MAXX sell/buy thresholds using Zapper price ticks")
    ap.add_argument("--token", default="0x1bff6cbd036162e3535b7969f63fd8043ccc1433", help="Token address (MAXX on Base)")
    ap.add_argument("--chain", type=int, default=8453, help="Chain ID (Base=8453)")
    ap.add_argument("--base-usd", type=float, default=100.0, help="Starting USD for backtest")
    ap.add_argument("--currency", default="USD", help="Currency for priceTicks")
    ap.add_argument(
        "--timeframes",
        nargs="*",
        default=["FIFTEEN_MINUTES", "HOUR", "FOUR_HOURS", "DAY"],
        help="Timeframe candidates to try (use valid Zapper enums, e.g., FIFTEEN_MINUTES, HOUR, FOUR_HOURS, DAY)",
    )
    args = ap.parse_args()

    client = ZapperClient()
    try:
        raw_ticks = client.fetch_price_ticks(
            token_address=args.token, chain_id=args.chain, currency=args.currency, timeframe_candidates=args.timeframes
        )
    finally:
        client.close()

    ticks = to_ticks(raw_ticks)
    if not ticks:
        print("No ticks returned; cannot optimize.")
        return

    # Use close price series
    prices = [t.close or t.median or t.open for t in ticks]
    prices = [p for p in prices if p and p > 0]
    if len(prices) < 10:
        print(f"Not enough price points ({len(prices)}) to run a useful grid search.")
        return

    (sell_up, buy_down), metrics = grid_search(prices, base_usd=args.base_usd)
    print("Suggested thresholds (based on historical ticks):")
    print(f"  Sell after rise: {sell_up*100:.1f}%  |  Re-buy after drop: {buy_down*100:.1f}%")
    print("Performance (toy backtest, no fees/slippage):")
    print(f"  Final USD: ${metrics['final_usd']:.2f}  Return: {metrics['return_pct']*100:.2f}%")
    print(f"  Trades: sells={metrics['sells']} buys={metrics['buys']}")


if __name__ == "__main__":
    main()
