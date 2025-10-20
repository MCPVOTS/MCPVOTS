#!/usr/bin/env python3
"""
Build and sign a low-gas ETH -> MAXX buy via KyberSwap on Base, then print a curl
command for eth_sendRawTransaction. Does not use the master system.

Safety:
- This script creates a real signed transaction. By default it DOES NOT send it;
  it only prints a curl command you can copy/paste to broadcast.

Requirements:
- Environment: ETHEREUM_PRIVATE_KEY in .env (hex, 0x...)
- Optional: BASE_RPC_URL in .env (defaults to https://mainnet.base.org)
- Optional: MAXX_ETH_POOL in .env or standalone_config (DexScreener pair id)

Usage (PowerShell):
  python .\buy_maxx_curl.py --usd 7 --slippage-bps 75

Options:
  --usd <float>           Amount in USD to spend (default 7)
  --slippage-bps <int>    Slippage tolerance in basis points (default 75)
  --rpc <url>             Base RPC URL (default env BASE_RPC_URL or https://mainnet.base.org)
    --dry-run               Just build/sign and print curl (default)
  --send                  Broadcast immediately (uses HTTP to RPC); prints tx hash
    --pk <hex>              Private key (0x...) to use instead of .env (avoid on shared machines)

Note: Gas policy uses EIP-1559 with maxFeePerGas = baseFeePerGas + 1 wei, priority = 0.
      This is the lowest viable setting; inclusion time depends on Base's base fee.
"""
import os
import json
import argparse
from decimal import Decimal
from typing import Optional, Dict

import requests
from web3 import Web3

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Try to import standalone_config for defaults (token/pool)
try:
    import standalone_config as config  # type: ignore
except Exception:
    config = None  # type: ignore

# Constants
KYBER_HOST = 'https://aggregator-api.kyberswap.com'
KYBER_CHAIN = 'base'
ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
MAXX_ADDRESS = getattr(config, 'MAXX_CONTRACT_ADDRESS', '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467')


def dex_price_eth_usd(pair_id: Optional[str] = None) -> Optional[Decimal]:
    """Fetch ETH/USD via MAXX pair from DexScreener: eth_usd = priceUsd / priceNative."""
    try:
        # Prefer explicit arg, then env, then standalone_config
        pid = pair_id or os.getenv('MAXX_ETH_POOL') or (getattr(config, 'MAXX_ETH_POOL', None) if config else None)
        if not pid:
            # Default to known MAXX/ETH pair id (can change over time)
            pid = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148'
        url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pid}"
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        d = r.json()
        p = (d.get('pairs') or [None])[0]
        if not p:
            return None
        price_usd = Decimal(str(p.get('priceUsd')))
        price_native = Decimal(str(p.get('priceNative')))
        if price_native <= 0:
            return None
        return price_usd / price_native
    except Exception:
        return None


def kyber_headers() -> Dict[str, str]:
    return {
        'X-Client-Id': 'AggressiveMAXXPy',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Origin': 'https://kyberswap.com',
        'Referer': 'https://kyberswap.com/'
    }


def kyber_get(path: str, params: Optional[Dict] = None) -> Dict:
    url = f"{KYBER_HOST}/{KYBER_CHAIN}{path}"
    resp = requests.get(url, headers=kyber_headers(), params=params, timeout=25)
    resp.raise_for_status()
    return resp.json()


def kyber_post(path: str, body: Dict) -> Dict:
    url = f"{KYBER_HOST}/{KYBER_CHAIN}{path}"
    resp = requests.post(url, headers={**kyber_headers(), 'Content-Type': 'application/json'}, json=body, timeout=35)
    resp.raise_for_status()
    return resp.json()


def get_route_eth_to_maxx(amount_in_wei: int, slippage_bps: int = 75) -> Dict:
    """Try progressively relaxed Kyber route params for Base until one succeeds."""
    base_params = {
        'tokenIn': ETH_ADDRESS,
        'tokenOut': MAXX_ADDRESS,
        'amountIn': str(amount_in_wei),
        'gasInclude': 'true',
        'slippageTolerance': str(slippage_bps),
        'excludeRFQSources': 'true',
    }

    variants = [
        # Strict: v4 only, single path, direct pools
        {'onlySinglePath': 'true', 'onlyDirectPools': 'true', 'includedSources': 'uniswapv4'},
        # Allow indirect pools
        {'onlySinglePath': 'true', 'onlyDirectPools': 'false', 'includedSources': 'uniswapv4'},
        # Allow multi-path
        {'onlySinglePath': 'false', 'onlyDirectPools': 'false', 'includedSources': 'uniswapv4'},
        # Allow all sources
        {'onlySinglePath': 'false', 'onlyDirectPools': 'false'},
    ]

    last_err: Optional[Exception] = None
    for v in variants:
        params = {**base_params, **v}
        try:
            data = kyber_get('/api/v1/routes', params)
            if data.get('code') == 0 and data.get('data'):
                return data['data']
            last_err = RuntimeError(f"Kyber routes code {data.get('code')}: {data.get('message')}")
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"Failed to fetch route after relax attempts: {last_err}")


def legacy_encode_eth_to_maxx(amount_in_wei: int, to: str, slippage_bps: int = 75) -> Dict:
    """Fallback to Kyber legacy encode endpoint when route/build path fails."""
    params = {
        'tokenIn': ETH_ADDRESS,
        'tokenOut': MAXX_ADDRESS,
        'amountIn': str(amount_in_wei),
        'to': to,
        'slippageTolerance': str(slippage_bps),
        'clientData': json.dumps({'source': 'AggressiveMAXXPy'})
    }
    data = kyber_get('/route/encode', params)  # note: host already includes /base in kyber_get
    if not data or 'encodedSwapData' not in data or 'routerAddress' not in data:
        raise RuntimeError('Kyber legacy encode failed')
    return data


def build_tx(route_summary: Dict, sender: str, slippage_bps: int = 75) -> Dict:
    body = {
        'routeSummary': route_summary,
        'sender': sender,
        'recipient': sender,
        'slippageTolerance': slippage_bps,
        'source': 'AggressiveMAXXPy',
    'deadline': int(__import__('time').time()) + 1200,
        'enableGasEstimation': True,
    }
    data = kyber_post('/api/v1/route/build', body)
    if data.get('code') != 0:
        raise RuntimeError(f"Kyber build error: {data.get('message')}")
    return data['data']


def compute_low_gas_params(w3: Web3) -> Dict[str, int]:
    """Lowest viable EIP-1559: maxFeePerGas = baseFee + 1 wei, priority = 0."""
    try:
        latest = w3.eth.get_block('latest')
        base_fee = int(getattr(latest, 'baseFeePerGas', latest['baseFeePerGas']))  # type: ignore[index]
    except Exception:
        base_fee = int(0.5 * 1e9)  # fallback 0.5 gwei
    return {
        'maxFeePerGas': int(base_fee) + 1,
        'maxPriorityFeePerGas': 0,
    }


def main():
    ap = argparse.ArgumentParser(description='Build a signed ETH->MAXX buy and print a curl command to send it')
    ap.add_argument('--usd', type=float, default=7.0, help='USD to spend')
    ap.add_argument('--slippage-bps', type=int, default=75, help='Slippage tolerance in bps (e.g., 75 = 0.75%)')
    ap.add_argument('--rpc', type=str, default=os.getenv('BASE_RPC_URL', 'https://mainnet.base.org'), help='Base RPC URL')
    ap.add_argument('--dry-run', action='store_true', help='Do not send, just print curl (default)')
    ap.add_argument('--send', action='store_true', help='Broadcast immediately via RPC (HTTP)')
    ap.add_argument('--pk', type=str, default=None, help='Private key hex (0x...) to override .env (insecure on shared machines)')
    args = ap.parse_args()

    # Select private key: CLI --pk overrides env and config
    pk = args.pk or os.getenv('ETHEREUM_PRIVATE_KEY')
    if not pk:
        # fallback to standalone_config
        if config and getattr(config, 'ETHEREUM_PRIVATE_KEY', None):
            pk = getattr(config, 'ETHEREUM_PRIVATE_KEY')
    if not pk:
        raise SystemExit('ETHEREUM_PRIVATE_KEY not set in environment or standalone_config')

    w3 = Web3(Web3.HTTPProvider(args.rpc))
    # Inject Base middleware when on chain 8453
    try:
        chain_id = w3.eth.chain_id
    except Exception:
        chain_id = 8453
    if chain_id == 8453:
        try:
            from web3.middleware import geth_poa_middleware  # type: ignore
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception:
            pass

    acct = w3.eth.account.from_key(pk)

    # Determine ETH/USD
    eth_usd = dex_price_eth_usd(getattr(config, 'MAXX_ETH_POOL', None) if config else None) or Decimal('3300')
    usd = Decimal(str(args.usd))
    eth_amount = usd / eth_usd
    eth_amount_wei = int(eth_amount * Decimal(10**18))
    if eth_amount_wei <= 0:
        raise SystemExit('Computed ETH amount is zero; check price feed or USD amount')

    # Route and build with fallback to legacy encode
    try:
        route = get_route_eth_to_maxx(eth_amount_wei, slippage_bps=int(args.slippage_bps))
        built = build_tx(route['routeSummary'], acct.address, slippage_bps=int(args.slippage_bps))
        to = built['routerAddress']
        data = built['data']
        value = int(built.get('transactionValue') or eth_amount_wei)
    except Exception as route_err:
        # Fallback to legacy encode path
        legacy = legacy_encode_eth_to_maxx(eth_amount_wei, acct.address, slippage_bps=int(args.slippage_bps))
        to = legacy['routerAddress']
        data = legacy['encodedSwapData']
        value = eth_amount_wei

    # Prepare tx
    tx = {
        'to': Web3.to_checksum_address(to),
        'from': acct.address,
        'value': value,
        'data': data,
        'chainId': 8453,
    }
    # Estimate gas then cap softly
    try:
        est = w3.eth.estimate_gas(tx)
        tx['gas'] = int(est * 1.05)
    except Exception:
        tx['gas'] = 400000

    # Apply minimal gas params
    tx.update(compute_low_gas_params(w3))
    # Nonce
    tx['nonce'] = w3.eth.get_transaction_count(acct.address)

    signed = w3.eth.account.sign_transaction(tx, private_key=acct.key)
    raw = getattr(signed, 'raw_transaction', None) or getattr(signed, 'rawTransaction', None)
    if not raw:
        raise SystemExit('Failed to sign transaction')
    raw_hex = Web3.to_hex(raw)

    print('\n=== BUY PREVIEW ===')
    print(f"Account: {acct.address}")
    print(f"Spend: ~{eth_amount:.8f} ETH (~${usd} @ ${eth_usd:.2f}/ETH)")
    print(f"Slippage: {args.slippage_bps} bps | Gas: {tx.get('gas')} | maxFeePerGas: {tx.get('maxFeePerGas')} | priority: {tx.get('maxPriorityFeePerGas')}")

    curl_cmd = (
        f"curl -s -X POST {args.rpc} -H 'Content-Type: application/json' "
        f"-d '{{\"jsonrpc\":\"2.0\",\"method\":\"eth_sendRawTransaction\",\"params\":[\"{raw_hex}\"],\"id\":1}}'"
    )
    print('\n=== Copy to broadcast (PowerShell) ===')
    print(curl_cmd)

    if args.send:
        try:
            r = requests.post(
                args.rpc,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'jsonrpc': '2.0',
                    'method': 'eth_sendRawTransaction',
                    'params': [raw_hex],
                    'id': 1
                }),
                timeout=25
            )
            r.raise_for_status()
            print('\nRPC response:')
            print(r.text)
        except Exception as e:
            print(f"Broadcast failed: {e}")


if __name__ == '__main__':
    main()
