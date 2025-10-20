# MAXX Ecosystem – Developer Guide (Architecture, Ops, and Extensibility)

This guide documents how the MAXX Ecosystem trading system and intelligence analyzer work, how to operate them safely, and how to extend them. It’s intended for future maintenance and feature work.

WARNING: This system can execute real on-chain transactions. Always verify modes and parameters before running anything that trades.

## Overview

Core components in this repo:

- master_trading_system.py – Unified trading controller, strategies, gas policy, CLI.
- real_dex_integration.py / Kyber client – Swap execution via Kyber aggregator (Uniswap V4 compatible routing).
- maxx_intelligence_analyzer.py – Data ingestion, analytics (pumps/whales/coordination), persistence (SQLite/JSON), signal generation.
- run_ethermax_intelligence.py / run_recent_ethermax_intel.py – CLIs to ingest data (API/logs/CSV) and export intelligence reports.
- config.py – Addresses, router, pool, and defaults reused across the system.
- requirements.txt – Python dependencies.

Pricing: DexScreener API for pool price and native price; cached for stability. Chain: Base (8453).

## Configuration and Secrets

- .env (not committed):
  - PRIVATE_KEY – Trading wallet private key used by master trading system and CLIs.
  - BASESCAN_API_KEY – For BaseScan APIs used by analyzer (tokentx, logs, proxy).
  - Optional RPC URLs – Defaults point to Base mainnet; you can add backups.
- config.py:
  - MAXX_CONTRACT_ADDRESS – Token address.
  - KYBER_ROUTER – Aggregator router address.
  - MAXX_ETH_POOL – DexScreener pair ID for price lookups.
  - GAS_LIMIT – Default gas units used in estimates.

Secrets are auto-loaded where supported. Never hardcode keys.

## Gas Policy and Safety

- EIP-1559 is used where possible (maxFeePerGas, maxPriorityFeePerGas) with a small base fee headroom and tiny priority tip by default.
- Global overrides:
  - --global-headroom-pct 0.02 – Add 2% over base to maxFeePerGas.
  - --global-priority-gwei 0.001 – Set priority fee in gwei.
- Per-action cap in USD (skip trades if too expensive):
  - Reactive: --reactive-gas-usd-cap (default $0.015)
  - Other modes: --gas-usd-cap (varies; see CLI)

Gas estimates include approval+swap for sells and swap-only for buys (conservative). Actions are skipped if balance is insufficient for gas.

## Pricing and Reserve Handling

- DexScreener provides:
  - maxx_usd – USD price per MAXX
  - maxx_eth – ETH price per MAXX (native)
  - eth_usd – Derived as maxx_usd / maxx_eth if available
- Reserves calculated in ETH from USD targets: reserve_eth = usd_reserve / eth_usd.
- If price fetch fails, system waits/retries; some logic falls back to placeholders but will skip trades if unsafe.

## Strategies in master_trading_system.py

All strategies run inside MasterTradingSystem with shared utilities:

- get_balances_cached() to reduce RPC churn.
- _get_prices() for DexScreener price snapshot.
- _estimate_gas_cost_eth() for quick gas ETH cost.
- buy_maxx()/sell_maxx() via Kyber aggregator.

### Reactive Strategy (Default +10% TP / -10% Re-entry)

Contract:

- Inputs: usd_to_spend, usd_reserve, sell_gain_pct, rebuy_drop_pct, gas_limit_override, slippage_bps, gas_usd_cap, spend_all
- Behavior:
  - If holding MAXX, track entry price and peak; sell ALL on +sell_gain_pct from entry.
  - After selling, set a re-entry anchor and rebuy when price drops rebuy_drop_pct from the post-sell anchor/peak.
  - On buys, either spend a fixed USD budget or all ETH above reserve (minus estimated gas) with --spend-all.
- Safety:
  - Skips sell if not enough ETH for gas.
  - Skips when estimated gas in USD exceeds cap.
  - Heartbeat logs include targets and deltas since entry/last action.

CLI usage (PowerShell):

```powershell
# Default 10%/10%
python .\master_trading_system.py --mode reactive --log-level INFO

# Customize thresholds and spend options
python .\master_trading_system.py --mode reactive \
  --sell-gain-pct 0.12 --rebuy-drop-pct 0.08 \
  --usd-to-spend 7 --usd-reserve 10 \
  --reactive-slippage-bps 75 --reactive-gas-usd-cap 0.02

# Spend all ETH above reserve (minus est gas)
python .\master_trading_system.py --mode reactive --spend-all --usd-reserve 10
```

Notes:

- sell_gain_pct and rebuy_drop_pct are decimals (0.10 = 10%).
- Re-entry anchor ratchets upward while flat to avoid buying shallow dips if price keeps rising.

### Automated Mode (Shortcut)

This calls the reactive strategy with the defaults (10%/10%) and prints a banner:

```powershell
python .\master_trading_system.py --mode automated
```

### Reserve Swing (Sell-All/Buy-All around a USD Reserve)

- If holding MAXX above dust, sell all; else buy all ETH above the reserve minus estimated gas.
- Gas cap checks applied.

```powershell
python .\master_trading_system.py --mode reserve-swing \
  --reserve-minutes 10 --reserve-usd 10 \
  --gas-usd-cap 0.015 --slippage-bps 75
```

### USD Ping-Pong

- Alternates buy $X then sell $X using current prices (amountOutMin=0 for tiny safety path).

```powershell
python .\master_trading_system.py --mode usd-pingpong \
  --usd-minutes 10 --usd-amount 1 --slippage-bps 75 --gas-usd-cap 0.001
```

### Burst Cycle

- Alternates SELL-ALL then BUY-ALL every interval to test plumbing or simple oscillations.

```powershell
python .\master_trading_system.py --mode burst-cycle \
  --burst-minutes 10 --burst-interval 1 --burst-usd-reserve 10
```

### Tiny Tests (Plumbing)

- run_tiny_buy / run_tiny_sell do very small trades with amountOutMin=0 to validate routes.
- These still spend real gas. Use sparingly.

```powershell
python .\master_trading_system.py --mode tiny-buy --tiny-buy-eth 0.00000001
python .\master_trading_system.py --mode tiny-sell --tiny-sell-eth 0.00001
```

### Sell All

```powershell
python .\master_trading_system.py --mode sell-all
```

### Cancel/Retry Helpers

- cancel-pending and retry-sell-fast use elevated gas to replace stuck txs.

```powershell
python .\master_trading_system.py --mode cancel-pending --headroom-pct 0.03 --priority-gwei 0.002
python .\master_trading_system.py --mode retry-sell-fast --gas-limit 300000 --slippage-bps 75
```

## Intelligence Analyzer (maxx_intelligence_analyzer.py)

Goals:

- Ingest MAXX token transfer data into SQLite and JSON.
- Detect pump windows, whale wallets, coordinated activity.
- Generate a structured intelligence report for strategy tuning.

Data ingestion pipelines:

- Etherscan-style API (tokentx) with pagination; handles NOTOK with warnings.
- logs.getLogs fallback with bounded scanning windows, proxy block/timestamp helpers, and early stop on sparse ranges.
- CSV import path for BaseScan-exported transfers (most reliable when APIs are flaky).

Key functions:

- collect_recent_trades(): paginated tokentx.
- collect_recent_trades_via_logs(): bounded logs scanning with progress and early exit.
- import_trades_from_csv(): flexible CSV schema mapping, numeric normalization, synthetic tx hash if missing.

Analysis:

- analyze_pump_patterns(): sliding windows to detect pumps; outputs windows summary.
- identify_whale_activity(): per-wallet stats (holdings, buy/sell counts, USD volume, first_trade, last_trade, span_days). Guards for None/empty values are in place.
- detect_coordinated_activity(): detects temporal clustering with safe division (guarded against division-by-zero).
- generate_trading_signals(): leverages whales and pumps; avoids KeyError by checking first/last_trade existence.

Persistence:

- SQLite: pumpfun_ecosystem.db (schema migrates: token_amount, token_decimals, etc.)
- JSON exports: e.g., maxx_intelligence_report.json, wallet profiles, pump windows.

Runner usage:

```powershell
# Analyze using CSV (recommended when API is NOTOK)
python .\run_recent_ethermax_intel.py --csv .\data\maxx_transfers.csv --out .\maxx_intelligence_report.json

# API + fallback
python .\run_recent_ethermax_intel.py --limit 1000 --out .\maxx_intelligence_report.json
```

## Logging & Artifacts

- Logs in the repo root: automated_trading_*.log, enhanced_trading_*.log, maxx_*_monitor.log, etc.
- Intelligence outputs: MAXX_ECOSYSTEM_ANALYSIS.json, maxx_intelligence_report.json, maxx_trades_database.json.
- Database: pumpfun_ecosystem.db.

## Common Operations

Status only (safe):

```powershell
python .\master_trading_system.py --mode status --log-level INFO
```

Reactive run with caps:

```powershell
python .\master_trading_system.py --mode reactive \
  --sell-gain-pct 0.10 --rebuy-drop-pct 0.10 \
  --usd-to-spend 7 --usd-reserve 10 \
  --reactive-gas-usd-cap 0.015 --reactive-slippage-bps 75
```

## Extending the System

- Add a new strategy:
  - Implement async def run_my_strategy(self, ...): inside MasterTradingSystem.
  - Use _get_prices(), get_balances_cached(), and gas cap checks consistently.
  - Wire into main() with a new --mode option and any CLI flags.

- Adjust pricing:
  - _get_prices() centralizes price fetch. Add alt sources or fallback if needed (respect timeouts and caching).

- Gas policy tweaks:
  - Respect global overrides and per-action USD caps. Keep estimates conservative and skip unsafe actions.

- Improving reliability:
  - Prefer cached balance reads in loops to avoid RPC 429.
  - Wrap external calls with try/except and short sleeps; never crash loops on transient errors.

- Analyzer enhancements:
  - Add new detectors under maxx_intelligence_analyzer.py; persist to SQLite/JSON consistently.
  - When adding fields (e.g., wallet stats), initialize safely and guard for missing data in downstream functions.

## Troubleshooting

- Price fetch fails: System waits and retries. If persistent, verify MAXX_ETH_POOL in config.py and DexScreener availability.
- Gas cap keeps skipping: Lower thresholds, increase cap slightly, or try off-peak times.
- Etherscan/BaseScan NOTOK: Use CSV ingestion for analyzer.
- KeyErrors in analyzer: Ensure newly added fields are set with defaults; guards exist for last_trade/first_trade and zero divisions.

## Quality Gates

- Lint/Type: Stick to Python 3.10+; run quick imports or use an IDE checker. get_errors reports no syntax issues for key modules.
- Smoke: Use --mode status for a safe system check; tiny trades validate routes but spend real gas.

## Appendix – Important CLI Flags

- Reactive:
  - --sell-gain-pct, --rebuy-drop-pct, --usd-to-spend, --usd-reserve, --spend-all,
  - --reactive-gas-usd-cap, --reactive-slippage-bps, --reactive-gas-limit
- Global gas overrides:
  - --global-headroom-pct, --global-priority-gwei
- Analyzer runner:
  - --csv, --limit, --out (exact options depend on the runner script)

---

Maintained: 2025-10-16
