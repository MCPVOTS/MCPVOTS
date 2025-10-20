# MAXX Ecosystem — API & CLI Analysis Guide

This guide shows how to use the APIs wired into this repo and run quick, copy‑paste PowerShell commands to analyze wallet balances, prices, liquidity, gas, token transfers, and your trading bot’s reactive state.

All commands are designed for PowerShell on Windows and assume you are in the folder:

- C:\PumpFun_Ecosystem\ECOSYSTEM_UNIFIED (with your venv activated)

If you see “unknown option --mode”, ensure you include the script name (e.g., `python .\master_trading_system.py ...`).

---

## Prerequisites

- Python 3.11+
- Virtual environment activated
- `.env` configured with:
  - `ETHEREUM_PRIVATE_KEY` (trading wallet private key)
  - `BASE_RPC_URL` (optional, default uses https://mainnet.base.org)
  - `BASESCAN_API_KEY` (Etherscan v2 compatible key)
  - `BIRDEYE_API_KEY` (optional, for price history)
  - `MAXX_CONTRACT_ADDRESS` (default: `0xFB7a83abe4F4A4E51c77B92E521390B769ff6467`)

Optional config in `config.py`:
- `PROFIT_EXTRACTION_ADDRESS` — wallet that receives extracted profits after sells

---

## APIs used

- Etherscan v2 multi-chain API (Base chain id 8453)
  - Wrapped by `basescan_client.py`
  - Base URL: `https://api.etherscan.io/v2/api`
  - Key env var: `BASESCAN_API_KEY`

- DexScreener (public)
  - Token endpoint: `https://api.dexscreener.com/latest/dex/tokens/{token}`
  - Pairs endpoint: `https://api.dexscreener.com/latest/dex/pairs/base/{pair}`

- Birdeye (optional; requires key)
  - Price: `https://public-api.birdeye.so/defi/price`
  - History (e.g., 1H): `https://public-api.birdeye.so/defi/history`

- Base RPC via Web3
  - Default: `https://mainnet.base.org` or your `BASE_RPC_URL`

- KyberSwap Aggregator (used internally by the trading bot for routing)

---

## Quick checks

### Verify account and ETH balance
'python -c 'import os, dotenv; dotenv.load_dotenv(); from web3 import Web3; pk=os.getenv("ETHEREUM_PRIVATE_KEY"); assert pk, "Missing ETHEREUM_PRIVATE_KEY"; w3=Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL","https://mainnet.base.org"))); acct=w3.eth.account.from_key(pk); bal=w3.eth.get_balance(acct.address)/1e18; print("Account:", acct.address); print(f"ETH Balance: {bal:.6f}")''

### Best MAXX pair on DexScreener (price & liquidity)
'python -c 'import os, requests; token=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"); d=requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token}", timeout=10).json(); pairs=[p for p in d.get("pairs",[]) if str(p.get("chainId")).lower() in ("base","8453")]; pairs.sort(key=lambda p: (p.get("liquidity",{}) or {}).get("usd",0) or 0, reverse=True); p=(pairs or [None])[0]; print("Pair:", (p or {}).get("pairAddress")); print("Price USD:", (p or {}).get("priceUsd")); print("Price ETH:", (p or {}).get("priceNative")); print("Liquidity USD:", ((p or {}).get("liquidity") or {}).get("usd")); print("24h Vol USD:", ((p or {}).get("volume") or {}).get("h24")); print("PriceChange %:", (p or {}).get("priceChange"))''

### Wallet valuation (ETH + MAXX in USD)
'python -c 'import os, dotenv, requests; from web3 import Web3; from decimal import Decimal; dotenv.load_dotenv(); w3=Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL","https://mainnet.base.org"))); acct=w3.eth.account.from_key(os.getenv("ETHEREUM_PRIVATE_KEY")); MAXX=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"); ABI=[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]; c=w3.eth.contract(address=Web3.to_checksum_address(MAXX), abi=ABI); dec=c.functions.decimals().call(); maxx=Decimal(c.functions.balanceOf(acct.address).call())/Decimal(10**dec); d=requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{MAXX}", timeout=10).json(); pairs=[p for p in d.get("pairs",[]) if str(p.get("chainId")).lower() in ("base","8453")]; pairs.sort(key=lambda p: (p.get("liquidity",{}) or {}).get("usd",0) or 0, reverse=True); p=(pairs or [None])[0]; maxx_usd=Decimal(str((p or {}).get("priceUsd") or "0")); maxx_eth=Decimal(str((p or {}).get("priceNative") or "0")); eth_usd=maxx_usd/maxx_eth if (maxx_eth and maxx_eth>0) else Decimal("0"); eth=Decimal(w3.eth.get_balance(acct.address))/Decimal(10**18); print(f"MAXX: {maxx:,.2f} (${maxx*maxx_usd:.2f}) | ETH: {eth:.6f} (${eth*eth_usd:.2f}) | Total: ${eth*eth_usd + maxx*maxx_usd:.2f}")''

### Current gas and estimated tx cost
'python -c 'import os, dotenv; from web3 import Web3; from decimal import Decimal; dotenv.load_dotenv(); w3=Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL","https://mainnet.base.org"))); blk=w3.eth.get_block("latest"); base=blk.get("baseFeePerGas") or blk["baseFeePerGas"]; g=300000; cost_eth=Decimal(base)*g/Decimal(10**18); print(f"Base fee: {base/1e9:.4f} gwei | Est cost @{g} gas: {cost_eth:.6f} ETH")''

---

## Token transfers — Etherscan v2

The repo includes `basescan_client.py` which wraps Etherscan v2.

### Last 100 MAXX transfers (global)
'

### Your wallet’s last 2-week MAXX transfers (paged until cutoff)
'python -c 'import os, time, statistics; from collections import Counter; from web3 import Web3; from basescan_client import EtherscanV2Client; w3=Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL","https://mainnet.base.org"))); addr=w3.eth.account.from_key(os.getenv("ETHEREUM_PRIVATE_KEY")).address.lower(); token=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467").lower(); client=EtherscanV2Client(); cutoff=int(time.time())-14*24*3600; page=1; vals=[]; ins=outs=0; cin=Counter(); cout=Counter();
while True:
    txs=client.get_tokentx(8453,address=addr,contractaddress=token,page=page,offset=100,sort="desc") or []
    if not txs: break
    stop=False
    for t in txs:
        ts=int(t.get("timeStamp") or t.get("timestamp") or 0)
        if ts and ts<cutoff: stop=True; break
        dec=int(t.get("tokenDecimal","18") or 18)
        amt=int(t.get("value","0") or 0)/(10**dec)
        frm=(t.get("from","") or '').lower(); to=(t.get("to","") or '').lower()
        vals.append(amt)
        if to==addr: ins+=1; cin[frm]+=1
        elif frm==addr: outs+=1; cout[to]+=1
    if stop: break
    page+=1
n=len(vals); print(f"Wallet {addr} | 2-week MAXX transfers: {n} | IN:{ins} OUT:{outs}")
if n:
    import statistics as S
    print("Avg: {:.2f} | Median: {:.2f} | Max: {:.2f} | Min: {:.2f}".format(S.mean(vals), S.median(vals), max(vals), min(vals)))
    small=sum(1 for a in vals if a<1_000); med=sum(1 for a in vals if 1_000<=a<10_000); large=sum(1 for a in vals if a>=10_000)
    print(f"Size buckets | Small<1k: {small} | 1k-10k: {med} | >=10k: {large}")
    print("Top IN counterparties:", cin.most_common(3))
    print("Top OUT counterparties:", cout.most_common(3))''

---

## Birdeye — 14-day hourly volatility & swings (optional)

This requires `BIRDEYE_API_KEY`. It counts how often the price rallies/drops ≥10%, ≥12%, ≥15% between local troughs/peaks and reports hourly return volatility.

'python -c 'import os, requests, statistics; token=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"); api=os.getenv("BIRDEYE_API_KEY"); headers={"X-API-KEY":api} if api else {}; url="https://public-api.birdeye.so/defi/history"; params={"address":token,"chain":"base","type":"1H"}; r=requests.get(url, params=params, headers=headers, timeout=20); d=r.json() if r.ok else {}; items=(d.get("data") or {}).get("items") or []; prices=[float(it.get("value")) for it in items if it.get("value")];
if len(prices)<24:
    print("Birdeye 1H history unavailable or too short"); raise SystemExit(0)
rets=[(prices[i]/prices[i-1]-1.0)*100.0 for i in range(1,len(prices)) if prices[i-1]]; sigma=statistics.pstdev(rets) if rets else 0.0;
up10=dn10=up12=dn12=up15=dn15=0; peak=trough=prices[0]
for p in prices[1:]:
    if p>peak: peak=p
    if p<trough: trough=p
    if peak>0 and (peak-p)/peak>=0.10: dn10+=1; peak=p; trough=p
    elif trough>0 and (p-trough)/trough>=0.10: up10+=1; peak=p; trough=p
peak=trough=prices[0]
for p in prices[1:]:
    if p>peak: peak=p
    if p<trough: trough=p
    if peak>0 and (peak-p)/peak>=0.12: dn12+=1; peak=p; trough=p
    elif trough>0 and (p-trough)/trough>=0.12: up12+=1; peak=p; trough=p
peak=trough=prices[0]
for p in prices[1:]:
    if p>peak: peak=p
    if p<trough: trough=p
    if peak>0 and (peak-p)/peak>=0.15: dn15+=1; peak=p; trough=p
    elif trough>0 and (p-trough)/trough>=0.15: up15+=1; peak=p; trough=p
print(f"Points: {len(prices)} | 1H sigma: {sigma:.2f}%"); print(f"Swings ≥10% (up/down): {up10}/{dn10}"); print(f"Swings ≥12% (up/down): {up12}/{dn12}"); print(f"Swings ≥15% (up/down): {up15}/{dn15}")''

Interpretation:
- If `Swings ≥15%` are rare (e.g., ≤2), use ±12% to get more trades.
- If `Swings ≥10%` are frequent, you can try +10% sell / -12% rebuy to increase entries (watch gas).

---

## Reserve & available ETH for buys

Shows how much ETH is spendable above a $10 reserve minus an estimated gas budget.

'python -c 'import os, requests; from web3 import Web3; from decimal import Decimal; w3=Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL","https://mainnet.base.org"))); eth=Decimal(w3.eth.get_balance(w3.eth.account.from_key(os.getenv("ETHEREUM_PRIVATE_KEY")).address))/Decimal(10**18); token=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"); d=requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token}", timeout=10).json(); pairs=[p for p in d.get("pairs",[]) if str(p.get("chainId")).lower() in ("base","8453")]; pairs.sort(key=lambda p: (p.get("liquidity",{}) or {}).get("usd",0) or 0, reverse=True); p=(pairs or [None])[0]; maxx_usd=Decimal(str((p or {}).get("priceUsd") or "0")); maxx_eth=Decimal(str((p or {}).get("priceNative") or "0")); eth_usd=maxx_usd/maxx_eth if (maxx_eth and maxx_eth>0) else Decimal("0"); reserve_usd=Decimal("10"); reserve_eth=reserve_usd/eth_usd if eth_usd>0 else Decimal("0"); base_fee=int(w3.eth.get_block("latest").get("baseFeePerGas") or 0); gas_eth=Decimal(base_fee)*Decimal(300000)/Decimal(10**18); avail=eth - reserve_eth - gas_eth; print(f"ETH total: {eth:.6f} | reserve ${reserve_usd} ≈ {reserve_eth:.6f} ETH | gas~{gas_eth:.6f} | available: {max(avail,Decimal(0)):.6f}")''

---

## Reactive bot state & target gap

Reads `reactive_state.json` (if present) and compares current price vs the +sell% target.

'python -c 'import os, json, requests; st="reactive_state.json"; token=os.getenv("MAXX_CONTRACT_ADDRESS","0xFB7a83abe4F4A4E51c77B92E521390B769ff6467"); d=requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token}", timeout=10).json(); pairs=[q for q in d.get("pairs",[]) if str(q.get("chainId")).lower() in ("base","8453")]; pairs.sort(key=lambda r: (r.get("liquidity",{}) or {}).get("usd",0) or 0, reverse=True); cur=float((pairs[0] if pairs else {}).get("priceUsd") or 0); s=json.load(open(st,"r")) if os.path.exists(st) else None;
if s:
    entry=float(s.get("entry_usd") or 0); last=s.get("last_action_type") or "n/a"; sell_gain=0.12; target=entry*(1+sell_gain) if entry>0 else 0; gap=((target-cur)/target*100) if target>0 else None; print(f"Reactive state: holding={s.get('holding')} entry=${entry:.6f} last={last} target(+12%)=${target:.6f} cur=${cur:.6f} gap={gap:.2f}%")
else:
    print("No reactive_state.json found")''

---

## Profit extraction destination

After a sell, profit (current ETH minus the baseline at start) is sent here.

'python -c 'import os, importlib.util as iu; mod="config.py"; spec=iu.spec_from_file_location("cfg", mod); cfg=iu.module_from_spec(spec); spec.loader.exec_module(cfg); print("Profit extraction address:", getattr(cfg,"PROFIT_EXTRACTION_ADDRESS","<not-set>"))''

---

## Run the bot (reactive: hold → sell pump → buy dip)

12%/12% is a solid starting point if 15% swings are sparse; keep the $10 reserve and tight slippage.

python .\master_trading_system.py --mode reactive --usd-reserve 10 --sell-gain-pct 0.12 --rebuy-drop-pct 0.12 --reactive-slippage-bps 50 --spend-all

Optional gas guard to skip trades when gas USD is too high:

--reactive-gas-usd-cap 0.02

Example with gas guard:

python .\master_trading_system.py --mode reactive --usd-reserve 10 --sell-gain-pct 0.12 --rebuy-drop-pct 0.12 --reactive-slippage-bps 50 --spend-all --reactive-gas-usd-cap 0.02

---

## Troubleshooting

- unknown option --mode
  - Include the script: `python .\master_trading_system.py --mode ...`
- Etherscan API key not configured
  - Set `BASESCAN_API_KEY` in `.env`.
- Birdeye history unavailable
  - Set `BIRDEYE_API_KEY` or skip that section.
- Route failures / slippage
  - Keep slippage at 50 bps (0.5%); increase cautiously if trades revert.
- Insufficient ETH for gas
  - The bot keeps a $10 reserve. If your ETH is near/under this, buys will be skipped.

---

## File references

- master_trading_system.py — main trading engine (reactive mode, reserve, profit extraction)
- basescan_client.py — Etherscan v2 wrapper (Base chain id 8453)
- config.py — runtime configuration
