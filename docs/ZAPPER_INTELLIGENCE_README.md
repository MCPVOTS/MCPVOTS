# Zapper-Powered Threshold Intelligence

Goal: Use up to 5,000 credits to analyze MAXX price behavior and fine‑tune the 10%/10% sell/buy thresholds for higher hit probability when the price fluctuates.

What’s included

- `zapper_client.py`: Minimal GraphQL client to fetch `priceTicks` for a fungible token.
- `zapper_threshold_optimizer.py`: Runs a small grid search around 10%/10% using historical ticks to suggest thresholds.

Credits and scope

- priceTicks queries are lightweight; avoid heavy fields (like `latestSwaps`) unless needed.
- A few timeframes per run should keep usage well within 5,000 credits.

Setup

1. Set your API key in environment:

```powershell
$env:ZAPPER_API_KEY = "<your_zapper_api_key>"
```

1. Install dependencies (if not already):

```powershell
pip install -r .\requirements.txt
```

Run the optimizer

```powershell
python .\zapper_threshold_optimizer.py --token 0x1bff6cbd036162e3535b7969f63fd8043ccc1433 --chain 8453 --base-usd 100
```

Output example

- Suggested thresholds (e.g., sell after rise: 12%, re‑buy after drop: 8%).
- Toy backtest performance (no fees/slippage) and trade counts.

Next steps (optional)

- Add fees/slippage to the simulation for realism.
- Persist suggested thresholds and expose them as optional flags to `master_trading_system.py` (kept off by default).
- Extend to multiple timeframes and weight results.

Safety

- This tooling is read‑only analytics. It does not execute trades or modify live behavior.
