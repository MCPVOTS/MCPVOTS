#!/usr/bin/env python3
"""
Show real MAXX transactions for the trading wallet over the last N hours with full details.

Data shown per tx:
- timestamp, direction (IN/OUT), from -> to
- MAXX amount (if token transfer present)
- gasUsed, effectiveGasPrice (gwei), gas cost in ETH and USD
- tx hash

Requirements:
- BASESCAN_API_KEY in .env
- Uses Web3 RPC (BASE_RPC_URLS or BASE_RPC_URL or defaults)
"""
from __future__ import annotations

import os
import sys
import argparse
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple

import requests
from web3 import Web3

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Local modules
from basescan_client import EtherscanV2Client
import standalone_config as config  # trading wallet + addresses


def _get_w3() -> Web3:
    # Prefer env-specified RPCs
    rpc = None
    urls = os.getenv('BASE_RPC_URLS')
    if urls:
        rpc = urls.split(',')[0].strip()
    if not rpc:
        rpc = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
    w3 = Web3(Web3.HTTPProvider(rpc))
    try:
        from web3.middleware import geth_poa_middleware  # type: ignore
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    except Exception:
        pass
    return w3


def _dexscreener_token_prices(token_addr: str) -> Optional[Dict[str, Decimal]]:
    """Token-first pricing: find highest-liquidity Base pair and derive prices."""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_addr}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()
        pairs = d.get('pairs') or []
        if not pairs:
            return None
        base_pairs = [p for p in pairs if str(p.get('chainId')).lower() in ('base', '8453')]
        use = base_pairs or pairs
        def _liq_usd(px: dict) -> float:
            liq = px.get('liquidity')
            if isinstance(liq, dict):
                try:
                    return float(liq.get('usd') or 0)
                except Exception:
                    return 0.0
            return 0.0
        use.sort(key=_liq_usd, reverse=True)
        top = use[0]
        maxx_usd = Decimal(str(top.get('priceUsd')))
        maxx_eth = Decimal(str(top.get('priceNative')))
        eth_usd = (maxx_usd / maxx_eth) if maxx_eth and maxx_eth > 0 else Decimal('3300')
        return {
            'maxx_usd': maxx_usd,
            'maxx_eth': maxx_eth,
            'eth_usd': eth_usd,
        }
    except Exception:
        return None


def _short(addr: Optional[str], n: int = 10) -> str:
    if not addr:
        return ''
    return f"{addr[:n]}...{addr[-4:]}"


def _fmt_usd(x: Decimal) -> str:
    try:
        return f"${x:.4f}"
    except Exception:
        return "$0.0000"


def fetch_wallet_maxx_transfers(hours: int, limit: int, wallet: str, token_addr: str) -> List[Dict[str, Any]]:
    client = EtherscanV2Client()
    if not client.is_configured():
        raise SystemExit("Missing BASESCAN_API_KEY in environment (.env)")

    # Grab token transfers for this wallet and contract
    transfers = client.get_tokentx(8453, address=wallet, contractaddress=token_addr, page=1, offset=max(limit, 100), sort='desc')
    if not transfers:
        return []
    # Filter by time window
    cutoff = int(datetime.now(timezone.utc).timestamp()) - (hours * 3600)
    out: List[Dict[str, Any]] = []
    for t in transfers:
        try:
            ts = int(t.get('timeStamp') or t.get('timeStamp', 0))
            if ts < cutoff:
                continue
            out.append(t)
            if len(out) >= limit:
                break
        except Exception:
            continue
    return out


def enrich_with_gas_details(w3: Web3, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for t in items:
        txh = t.get('hash') or t.get('transactionHash')
        if not txh:
            continue
        try:
            tx = w3.eth.get_transaction(txh)
        except Exception:
            tx = None
        try:
            rcpt = w3.eth.get_transaction_receipt(txh)
        except Exception:
            rcpt = None

        gas_used = int(getattr(rcpt, 'gasUsed', rcpt['gasUsed'])) if rcpt else None
        # Prefer post-London effectiveGasPrice; fallback to tx.gasPrice
        eff_gas_price = None
        if rcpt is not None:
            try:
                eff_gas_price = int(getattr(rcpt, 'effectiveGasPrice', rcpt['effectiveGasPrice']))
            except Exception:
                eff_gas_price = None
        if eff_gas_price is None and tx is not None:
            try:
                eff_gas_price = int(getattr(tx, 'gasPrice', tx['gasPrice']))
            except Exception:
                eff_gas_price = None

        gas_cost_eth = None
        if gas_used is not None and eff_gas_price is not None:
            gas_cost_eth = Decimal(gas_used) * Decimal(eff_gas_price) / Decimal(10**18)

        t['_tx'] = tx
        t['_rcpt'] = rcpt
        t['_gas_used'] = gas_used
        t['_eff_gas_price'] = eff_gas_price
        t['_gas_cost_eth'] = gas_cost_eth
        enriched.append(t)
    return enriched


def main():
    ap = argparse.ArgumentParser(description='Show recent MAXX transactions with full gas/ETH details')
    ap.add_argument('--hours', type=int, default=24, help='Lookback window in hours')
    ap.add_argument('--limit', type=int, default=50, help='Max number of transfers to display')
    ap.add_argument('--wallet', type=str, default=None, help='Override wallet address (default trading wallet)')
    ap.add_argument('--contract', type=str, default=None, help='Override MAXX contract address')
    args = ap.parse_args()

    wallet = args.wallet or getattr(config, 'TRADING_ACCOUNT_ADDRESS', None)
    if not wallet:
        # fallback to key-derived address
        try:
            w3tmp = _get_w3()
            acct = w3tmp.eth.account.from_key(config.ETHEREUM_PRIVATE_KEY)
            wallet = acct.address
        except Exception:
            raise SystemExit('Unable to determine trading wallet address')

    token_addr = (args.contract or os.getenv('MAXX_CONTRACT_ADDRESS') or getattr(config, 'MAXX_CONTRACT_ADDRESS', '')).strip()
    if not token_addr:
        raise SystemExit('MAXX contract address not configured')

    prices = _dexscreener_token_prices(token_addr) or {'eth_usd': Decimal('3300'), 'maxx_usd': Decimal('0')}
    eth_usd = Decimal(str(prices.get('eth_usd') or '3300'))
    maxx_usd = Decimal(str(prices.get('maxx_usd') or '0'))

    items = fetch_wallet_maxx_transfers(args.hours, args.limit, wallet, token_addr)
    if not items:
        print('No recent MAXX transfers found for wallet in the given window')
        return

    w3 = _get_w3()
    enriched = enrich_with_gas_details(w3, items)

    print(f"\nMAXX Transfers for {wallet} over last {args.hours}h (limit {args.limit})\n")
    for t in enriched:
        try:
            ts = int(t.get('timeStamp') or 0)
            when = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
            frm = (t.get('from') or '').lower()
            to = (t.get('to') or '').lower()
            dirn = 'OUT' if frm == wallet.lower() else 'IN'
            dec = int(t.get('tokenDecimal') or t.get('tokenDecimal', 18))
            raw_val = int(t.get('value') or 0)
            amt = Decimal(raw_val) / Decimal(10 ** dec)
            amt_usd = amt * maxx_usd if maxx_usd > 0 else Decimal('0')

            gas_used = t.get('_gas_used')
            eff_price = t.get('_eff_gas_price')
            gas_cost_eth = t.get('_gas_cost_eth') or Decimal('0')
            gas_cost_usd = gas_cost_eth * eth_usd
            eff_gwei = (Decimal(eff_price) / Decimal(1e9)) if eff_price else Decimal('0')
            status = None
            if t.get('_rcpt') is not None:
                try:
                    status = int(getattr(t['_rcpt'], 'status', t['_rcpt']['status']))
                except Exception:
                    status = None

            txh = t.get('hash') or t.get('transactionHash')
            kyber = getattr(config, 'KYBER_ROUTER', '').lower()
            is_router = (to == kyber or frm == kyber)
            tag = 'ROUTER' if is_router else ''

            line = (
                f"{when} | {dirn:<3} | MAXX {amt:,.2f} ({_fmt_usd(amt_usd)}) | "
                f"Gas {gas_used or 0} @ {eff_gwei:.4f} gwei = {gas_cost_eth:.6f} ETH ({_fmt_usd(gas_cost_usd)}) | "
                f"{_short(frm)} -> {_short(to)} | status={status} {tag} | {txh}"
            )
            print(line)
        except Exception as e:
            print(f"Error printing tx: {e}")


if __name__ == '__main__':
    main()
