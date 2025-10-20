# MAXX ECOSYSTEM – CURRENT MCP MEMORY

## Live Trading System Status – October 16, 2025

## 🔥 System Overview

The MAXX Ecosystem is a unified, on-chain trading and intelligence stack running on Base (chainId 8453). It executes swaps via Kyber aggregator (Uniswap V4-compatible paths) and analyzes token flows to inform strategies. Real transactions only; no mocks.

## 📊 Current Status

- Status: ✅ OPERATIONAL
- Mode: LIVE (balances loaded, explorer checks OK)
- Chain: Base (8453)
- Token: MAXX (0xFB7a83abe4F4A4E51c77B92E521390B769ff6467)
- Router: Kyber Aggregator (0x6131B5fae19EA4f9D964eAc0408E4408b66337b5)
- Pricing: DexScreener pairs API with native price derivation

## 🎯 Core Components

1. master_trading_system.py

- Purpose: Unified orchestrator, strategies, gas policy, CLI.
- Features: EIP-1559 gas, status view, cancel/retry, cached balances, DexScreener pricing, Kyber swaps.

2. MAXX Mini-App (Next.js + RainbowKit)

- Purpose: Real-time trading dashboard with WebSocket connection to MAXX bot, Three.js cyberpunk background, and RainbowKit wallet integration.
- Features: Live tick data display, performance metrics, trading configuration, ultra-cyberpunk UI with neon effects, multi-network wallet support (Ethereum, Base, Polygon, Arbitrum, Optimism), address truncation for long wallet names, Base name resolution (.base.eth) for human-readable wallet display on Base network, fully responsive design for mobile/tablet/desktop.
- Tech Stack: Next.js 15.5.6, RainbowKit v2.2.9, Wagmi v2.18.1, Three.js particles, WebSocket real-time data, Basenames contract integration, Tailwind CSS responsive design.
- Networks: Mainnet, Base, Sepolia, Polygon, Arbitrum, Optimism (all available once connected).
- Responsive Breakpoints: Mobile (384px), Small tablets (448px), Tablets (512px), Small desktops (576px), Large desktops (672px).

3. Kyber integration (real_dex_intergration.py)

- Purpose: ETH <-> MAXX swaps via aggregator to Uniswap V4 pool.
- Inputs: amount, slippage bps, optional gas limit; returns tx hash.

4. maxx_intelligence_analyzer.py

- Purpose: Collect and analyze MAXX transfers; persist to SQLite/JSON; detect pumps/whales/coordination; generate signals.
- Ingestion: BaseScan tokentx (paginated), logs.getLogs bounded fallback, CSV import path (recommended when API is NOTOK).
- Safeguards: Timeouts, early-exit on sparse logs, first/last trade fields, division-by-zero guards.

5. Data/Artifacts

- DB: pumpfun_ecosystem.db (trades + analytics; schema migrates).
- JSON: maxx_intelligence_report.json, wallet profiles, pump windows.
- Logs: automated_trading_*.log, enhanced_trading_*.log, maxx_*_monitor.log.

## 🧠 MCP Memory System

- Purpose: Vector-based memory storage for MAXX ecosystem knowledge and workflows
- Features: SQLite storage with NumPy vectors, semantic search, categorized memories, direct API usage
- Direct Usage: Import VectorMemoryStore and call methods without MCP server
- Categories: system (architecture/docs), trading (strategies), analysis (intelligence), general (misc)
- Current Memories: 15 entries across 11 categories including mini-app update workflows

## 🧠 Strategies (Runtime)

- Reactive (default): Take profit +10% from entry; re-enter after -10% from anchor. Configurable via --sell-gain-pct/--rebuy-drop-pct. Can use fixed USD per entry or spend-all above reserve.
- Reserve Swing: If holding MAXX, sell-all; otherwise buy-all ETH above a USD reserve (minus gas). Gas cap respected.
- USD Ping-Pong: Buy $X then sell $X repeatedly for plumbing checks.
- Burst Cycle: Alternates SELL-ALL and BUY-ALL each interval.
- Tiny Trades: Very small buy/sell to validate routes (still costs gas).

Gas policy:

- EIP-1559 with small base headroom and tiny priority by default.
- Global overrides: --global-headroom-pct, --global-priority-gwei.
- Per-action caps: --reactive-gas-usd-cap (default ~$0.015), others via --gas-usd-cap.

## 🔍 Intelligence (Analytics)

- Pumps: Sliding windows to identify pump events.
- Whales: Per-wallet stats with first_trade/last_trade and activity spans; robust against missing values.
- Coordination: Temporal clustering with guarded math to avoid zero-division.
- Signals: Combines whales/pumps; guards against absent fields.

Ingestion reliability:

- Tokentx path logs warnings on NOTOK.
- logs.getLogs fallback is bounded, with progress and early stop on many empty windows.
- CSV import path normalizes headers, synthesizes tx hash if missing, and computes USD values.

## ⚙️ Ops (Key Commands – PowerShell)

Status (safe):

```powershell
python .\master_trading_system.py --mode status --log-level INFO
```

Reactive (defaults +10%/-10%):

```powershell
python .\master_trading_system.py --mode reactive --log-level INFO
```

Reactive (customized):

```powershell
python .\master_trading_system.py --mode reactive \
  --sell-gain-pct 0.12 --rebuy-drop-pct 0.08 \
  --usd-to-spend 7 --usd-reserve 10 \
  --reactive-gas-usd-cap 0.02 --reactive-slippage-bps 75
```

Sell all:

```powershell
python .\master_trading_system.py --mode sell-all
```

Analyzer via CSV:

```powershell
python .\run_recent_ethermax_intel.py --csv .\data\maxx_transfers.csv --out .\maxx_intelligence_report.json
```

## ✅ Current Health

- Initialization: PASS (RPC connected, account loaded)
- Explorer check: PASS (recent Base tx listed)
- Price fetch: PASS (DexScreener); system retries on transient failures
- Analyzer: PASS with CSV path; NOTOK guarded for API/logs

## 💡 Key Insights

- 10%/10% reactive thresholds active by default for more cycles.
- Gas USD caps prevent trading during expensive network conditions.
- CSV ingestion ensures analytics continuity when APIs are flaky.
- RainbowKit wallet integration supports multi-network connections with cyberpunk UI.
- Address truncation prevents UI overflow for long wallet addresses.
- Base name resolution provides human-readable wallet names on Base network.

## ⚠️ Notes

- Real funds; verify parameters before trading.
- Tiny trades still incur gas.
- Keep .env PRIVATE_KEY and BASESCAN_API_KEY configured; do not commit secrets.
- Wallet connection supports Ethereum, Base, Polygon, Arbitrum, and Optimism networks.
- Base names (.base.eth) are automatically resolved and displayed when connected to Base network.

---
Last Updated: October 17, 2025

System Version: MAXX Ecosystem (Base 8453) + RainbowKit Wallet Integration

Status: Live and Operational
