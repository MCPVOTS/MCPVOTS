# MAXX Trading Commands (Windows PowerShell)

Quick, copy-pasteable commands to run common actions with `master_trading_system.py` and small Python snippets. Assumes you’re in `C:\PumpFun_Ecosystem\ECOSYSTEM_UNIFIED` and using PowerShell (pwsh).

## 0) Environment setup

```powershell
# Activate virtual environment (adjust path if needed)
& C:/PumpFun_Ecosystem/ECOSYSTEM_UNIFIED/.venv/Scripts/Activate.ps1

# Optional: set log level for this session
$env:LOG_LEVEL = "INFO"

# Required for explorer history (BaseScan v2). Put this in .env for persistence.
$env:BASESCAN_API_KEY = "<your-api-key>"
```

## 1) System status and balances

```powershell
# Prints chain status, wallet balances, USD values, contract info, and a brief explorer summary
python .\master_trading_system.py --mode status --log-level INFO
```

Just balances via a small Python block:

```powershell
python -c "
from master_trading_system import MasterTradingSystem
import asyncio

async def main():
    s = MasterTradingSystem()
    await s.initialize()
    eth, maxx = await s.get_balances()
    print(f'ETH: {eth:.6f} | MAXX: {maxx:.2f}')

asyncio.run(main())
"
```

## 2) Buy MAXX

### Tiny buy (set ETH amount explicitly)

```powershell
# Default is very small; override with --tiny-buy-eth
python .\master_trading_system.py --mode tiny-buy --tiny-buy-eth 0.0003 --log-level INFO
```

### Reactive mode (auto loop with thresholds; buys/sells per rules)

```powershell
# Buys with ~$7 per entry by default; override with flags below
python .\master_trading_system.py --mode reactive --usd-to-spend 7 --usd-reserve 10 --sell-gain-pct 0.10 --rebuy-drop-pct 0.10 --reactive-slippage-bps 75 --log-level INFO
```

### Buy a custom ETH amount (Python)

```powershell
python -c "
from master_trading_system import MasterTradingSystem
from decimal import Decimal
import asyncio

async def main():
    s = MasterTradingSystem()
    await s.initialize()
    tx = await s.buy_maxx(Decimal('0.0012'))
    print('TX:', tx)

asyncio.run(main())
"
```

## 3) Sell MAXX

### Sell ALL MAXX

```powershell
python .\master_trading_system.py --mode sell-all --log-level INFO
```

### Tiny sell targeting a specific ETH out (estimates MAXX amount)

```powershell
python .\master_trading_system.py --mode tiny-sell --tiny-sell-eth 0.00002 --log-level INFO
```

### Sell a custom MAXX amount (Python)

```powershell
python -c "
from master_trading_system import MasterTradingSystem
from decimal import Decimal
import asyncio

async def main():
    s = MasterTradingSystem()
    await s.initialize()
    tx = await s.sell_maxx(Decimal('12345.67'))
    print('TX:', tx)

asyncio.run(main())
"
```

## 4) Automated strategies

### Automated demo loop

```powershell
python .\master_trading_system.py --mode automated --log-level INFO
```

### Reserve swing (sell-all if holding, else buy-all above reserve)

```powershell
python .\master_trading_system.py --mode reserve-swing --reserve-minutes 15 --reserve-usd 10 --slippage-bps 75 --log-level INFO
```

### Burst cycle (alternate sell-all / buy-all on a timer)

```powershell
python .\master_trading_system.py --mode burst-cycle --burst-minutes 10 --burst-interval 1 --burst-usd-reserve 10 --gas-limit 280000 --log-level INFO
```

### Buy pump then dip (accumulator)

```powershell
python .\master_trading_system.py --mode buy-pump-then-dip --pump-minutes 20 --pump-gain-pct 0.15 --dip-drop-pct 0.15 --reserve-usd 10 --cooldown-sec 10 --slippage-bps 75 --log-level INFO
```

## 5) Gas controls and reliability (optional)

### Lower EIP-1559 headroom or priority tip globally

```powershell
python .\master_trading_system.py --mode reactive --global-headroom-pct 0.00 --global-priority-gwei 0.0 --log-level INFO
```

### Cancel pending tx / Retry sell-fast

```powershell
# Cancel first pending tx
python .\master_trading_system.py --mode cancel-pending --headroom-pct 0.02 --priority-gwei 0.001 --log-level INFO

# Retry sell-all fast
python .\master_trading_system.py --mode retry-sell-fast --headroom-pct 0.02 --priority-gwei 0.001 --gas-limit 300000 --slippage-bps 75 --log-level INFO
```

## 6) Dashboard streaming (optional)

Serve your dashboard over HTTP, then run trading with WS broadcasting enabled:

```powershell
python .\master_trading_system.py --mode reactive --ws-enable --ws-host localhost --ws-port 8080 --log-level INFO
```

In the dashboard, set WebSocket URL to `ws://localhost:8080/ws` (use the `?ws=` query param or press `s` and paste it).

## 7) Explorer: last N Base transactions (e.g., 100)

Requires `$env:BASESCAN_API_KEY`. This prints recent activity for the trading wallet.

```powershell
python -c "
from basescan_client import EtherscanV2Client
from master_trading_system import MasterTradingSystem
import asyncio

async def main():
    s = MasterTradingSystem(); ok = await s.initialize()
    c = EtherscanV2Client(); txs = c.get_txlist(8453, s.account.address, page=1, offset=100, sort='desc')
    for t in (txs or [])[:100]:
        h = t.get('hash',''); frm = t.get('from',''); to = t.get('to',''); val = int(t.get('value','0') or 0)/1e18; blk = t.get('blockNumber','n/a')
        d = 'OUT' if frm and s.account and frm.lower()==s.account.address.lower() else 'IN'
        print(f"{d} {val:.6f} ETH | {h[:10]}... -> {(to or '')[:10]}... | block {blk}")

asyncio.run(main())
"
```

## 8) Quick price and balances heartbeat

```powershell
python -c "
from master_trading_system import MasterTradingSystem
import asyncio

async def main():
    s = MasterTradingSystem(); await s.initialize()
    for _ in range(10):
        eth, maxx = await s.get_balances_cached(min_interval_seconds=3)
        p = s._get_prices() or {}
        print(f"ETH {float(eth):.6f} | MAXX {float(maxx):.2f} | MAXX/USD {float(p.get('maxx_usd') or 0):.6f} | ETH/USD {float(p.get('eth_usd') or 0):.2f}")
        await asyncio.sleep(3)

asyncio.run(main())
"
```

## 9) Troubleshooting tips

- If you see WS errors, ensure the `websockets` package is installed in the active venv.
- For explorer calls, confirm `$env:BASESCAN_API_KEY` is set or exists in `.env`.
- If RPC rate limits appear, wait a few seconds; the system rotates endpoints and caches balances.
- Never commit secrets. Store them in `.env` or environment variables.
