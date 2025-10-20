# Master Trading System — Overview

This document summarizes the architecture, components, and operation of `master_trading_system.py`, the central controller for live MAXX trading on Base.

## Purpose and Capabilities

- Live trading engine for MAXX on Base mainnet
- Multiple operating modes: interactive/manual and several automated strategies
- DEX aggregator routing via KyberSwap (best-price pathing)
- Robust RPC management with failover + rate limiting
- EIP-1559 gas optimization (lowest viable inclusion policy)
- Optional ChromaDB logging for analytics (off by default)
- Real-time dashboard broadcasting via embedded WebSocket server (flag-gated)

## Key Components

- RateLimiter: Limits RPC calls/sec to avoid 429s; async lock and sliding window
- RPCManager: Manages Base RPC endpoints, rotates on failure, and reuses healthy Web3 instances
- DashboardWebSocketServer: Minimal WS at `ws://<host>:<port>/ws` broadcasting JSON events (price_update, balance_update, trade)
- MasterTradingSystem: Orchestrates initialization, account/ABI setup, strategies, and order execution via KyberClient

## MasterTradingSystem Highlights

- Initialization: Connects with RPCManager; loads trading account; binds MAXX ERC-20; optional ChromaDB guarded
- Strategies: reactive (TP + re-buy), reserve-swing (sell-all/buy-above-reserve), pump-then-dip (breakout + dip); plus burst/tiny/usd modes
- Order Execution: buy_maxx/sell_maxx via KyberClient; logs identity/trades when enabled; emits WS trade events when WS is enabled
- Gas Policy: `_get_gas_params` builds EIP-1559 params from base fee + optional headroom and minimal tip; global overrides supported
- Interactive Mode: CLI menu for manual buys/sells, status, and bot launch

## CLI Usage (modes and flags)

Modes (`--mode`):

- interactive, automated, test, status
- reactive, burst-cycle, reserve-swing
- tiny-buy, tiny-sell, small-swap, sell-all
- usd-pingpong, usd-once
- cancel-pending, retry-sell-fast, buy-pump-then-dip

Useful flags:

- Logging: `--log-level [DEBUG|INFO|WARNING|ERROR]`
- Reactive params: `--usd-to-spend`, `--usd-reserve`, `--sell-gain-pct`, `--rebuy-drop-pct`, `--reactive-slippage-bps`, `--reactive-gas-limit`, `--reactive-gas-usd-cap`, `--spend-all`
- Burst params: `--burst-minutes`, `--burst-interval`, `--burst-usd-reserve`, `--gas-limit`
- Tiny trade params: `--tiny-buy-eth`, `--tiny-sell-eth`
- Global gas policy: `--global-headroom-pct`, `--global-priority-gwei`
- Cancel/Retry: `--headroom-pct`, `--priority-gwei`
- Dashboard WS (optional): `--ws-enable`, `--ws-host`, `--ws-port`

See `MAXX_TRADING_COMMANDS.md` for copy‑pasteable commands covering status, buy/sell, strategies, explorer history, and dashboard streaming.

## Quick Start

- Print status and balances (PowerShell):

```powershell
python .\master_trading_system.py --mode status --log-level INFO
```

- Run reactive strategy (~$7 entries by default):

```powershell
python .\master_trading_system.py --mode reactive --usd-to-spend 7 --usd-reserve 10 --sell-gain-pct 0.10 --rebuy-drop-pct 0.10 --reactive-slippage-bps 75 --log-level INFO
```

- Stream to dashboard (served over HTTP) while trading:

```powershell
python .\master_trading_system.py --mode reactive --ws-enable --ws-host localhost --ws-port 8080 --log-level INFO
```

Then connect your dashboard to `ws://localhost:8080/ws`.

## Live Trading Warning

WARNING: This system executes REAL transactions with REAL money. Double‑check private keys, RPC endpoints, and amounts before running. Start with tiny trades while validating routes and gas behavior.
# Master Trading System — Overview

This document summarizes the architecture, components, and operation of `master_trading_system.py`, the central controller for live MAXX trading on Base.

## Purpose and Capabilities


## Key Components

  - Limits RPC calls/sec to avoid 429s; async lock and sliding window
  - Manages a list of Base RPC endpoints; detects failures and rotates; reuses healthy Web3 instances
  - Minimal WS server at `ws://<host>:<port>/ws` broadcasting JSON events (price_update, balance_update, trade)
  - Orchestrates initialization, account/ABI setup, strategies, and order execution via KyberClient
## Key Components

- RateLimiter: Limits RPC calls/sec to avoid 429s; async lock and sliding window
- RPCManager: Manages Base RPC endpoints, rotates on failure, and reuses healthy Web3 instances
- DashboardWebSocketServer: Minimal WS at `ws://<host>:<port>/ws` broadcasting JSON events (price_update, balance_update, trade)
- MasterTradingSystem: Orchestrates initialization, account/ABI setup, strategies, and order execution via KyberClient
# Master Trading System — Overview

This document summarizes the architecture, components, and operation of `master_trading_system.py`, the central controller for live MAXX trading on Base.

## Purpose and Capabilities

- Live trading engine for MAXX on Base mainnet
- Multiple operating modes: interactive/manual and several automated strategies
- DEX aggregator routing via KyberSwap (best-price pathing)
- Robust RPC management with failover + rate limiting
- EIP-1559 gas optimization (lowest viable inclusion policy)
- Optional ChromaDB logging for analytics (off by default)
- Real-time dashboard broadcasting via embedded WebSocket server (flag-gated)

## Key Components

- RateLimiter: Limits RPC calls/sec to avoid 429s; async lock and sliding window
- RPCManager: Manages Base RPC endpoints, rotates on failure, and reuses healthy Web3 instances
- DashboardWebSocketServer: Minimal WS at `ws://<host>:<port>/ws` broadcasting JSON events (price_update, balance_update, trade)
- MasterTradingSystem: Orchestrates initialization, account/ABI setup, strategies, and order execution via KyberClient

## MasterTradingSystem Highlights

- Initialization: Connects with RPCManager; loads trading account; binds MAXX ERC-20; optional ChromaDB guarded
- Strategies: reactive (TP + re-buy), reserve-swing (sell-all/buy-above-reserve), pump-then-dip (breakout + dip); plus burst/tiny/usd modes
- Order Execution: buy_maxx/sell_maxx via KyberClient; logs identity/trades when enabled; emits WS trade events when WS is enabled
- Gas Policy: _get_gas_params builds EIP-1559 params from base fee + optional headroom and minimal tip; global overrides supported
- Interactive Mode: CLI menu for manual buys/sells, status, and bot launch

## CLI Usage (modes and flags)

Modes (`--mode`):

- interactive, automated, test, status
- reactive, burst-cycle, reserve-swing
- tiny-buy, tiny-sell, small-swap, sell-all
- usd-pingpong, usd-once
- cancel-pending, retry-sell-fast, buy-pump-then-dip

Useful flags:

- Logging: `--log-level [DEBUG|INFO|WARNING|ERROR]`
- Reactive params: `--usd-to-spend`, `--usd-reserve`, `--sell-gain-pct`, `--rebuy-drop-pct`, `--reactive-slippage-bps`, `--reactive-gas-limit`, `--reactive-gas-usd-cap`, `--spend-all`
- Burst params: `--burst-minutes`, `--burst-interval`, `--burst-usd-reserve`, `--gas-limit`
- Tiny trade params: `--tiny-buy-eth`, `--tiny-sell-eth`
- Global gas policy: `--global-headroom-pct`, `--global-priority-gwei`
- Cancel/Retry: `--headroom-pct`, `--priority-gwei`
- Dashboard WS (optional): `--ws-enable`, `--ws-host`, `--ws-port`

See `MAXX_TRADING_COMMANDS.md` for copy‑pasteable commands covering status, buy/sell, strategies, explorer history, and dashboard streaming.

## Quick Start

- Print status and balances (PowerShell):

```powershell
python .\master_trading_system.py --mode status --log-level INFO
```

- Run reactive strategy (~$7 entries by default):

```powershell
python .\master_trading_system.py --mode reactive --usd-to-spend 7 --usd-reserve 10 --sell-gain-pct 0.10 --rebuy-drop-pct 0.10 --reactive-slippage-bps 75 --log-level INFO
```

- Stream to dashboard (served over HTTP) while trading:

```powershell
python .\master_trading_system.py --mode reactive --ws-enable --ws-host localhost --ws-port 8080 --log-level INFO
```
Then connect your dashboard to `ws://localhost:8080/ws`.

## Live Trading Warning

WARNING: This system executes REAL transactions with REAL money. Double‑check private keys, RPC endpoints, and amounts before running. Start with tiny trades while validating routes and gas behavior.
