#!/usr/bin/env python3
"""
KyberSwap Aggregator Client for Base chain (ETH <-> MAXX)
 - Uses Kyber v1 routes + build, with legacy encode fallback
 - Integrates with MasterTradingSystem for EIP-1559 gas params and optional receipt wait
 - Expects wei inputs for buy/sell to align with aggressive trader
"""
from __future__ import annotations
import json
from datetime import datetime
from typing import Optional, Dict

import requests
from web3 import Web3

KYBER_HOST = 'https://aggregator-api.kyberswap.com'
KYBER_CHAIN = 'base'
KYBER_ROUTER = '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5'
KYBER_CLIENT_ID = 'AggressiveMAXXPy'

WETH = '0x4200000000000000000000000000000000000006'
MAXX = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'
ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'


class KyberClient:
    def __init__(self, w3: Web3, account, system=None, gas_cap: int | None = None, route_exclude_rfq: bool = True):
        self.w3 = w3
        self.account = account  # LocalAccount
        self.system = system  # optional MasterTradingSystem for gas params and wait
        self.gas_cap = gas_cap  # optional max gas limit cap per tx
        self.exclude_rfq = route_exclude_rfq

    def _headers(self) -> Dict[str, str]:
        return {
            'X-Client-Id': KYBER_CLIENT_ID,
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Origin': 'https://kyberswap.com',
            'Referer': 'https://kyberswap.com/'
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{KYBER_HOST}{path}"
        # Reduced timeout for faster failures
        resp = requests.get(url, headers=self._headers(), params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: Dict) -> Dict:
        url = f"{KYBER_HOST}{path}"
        # Reduced timeout for faster failures
        resp = requests.post(url, headers={**self._headers(), 'Content-Type': 'application/json'}, json=body, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_route(self, token_in: str, token_out: str, amount_in_wei: int, slippage_bps: int = 50,
                  v4_only=False, single_path=True, direct_pools=True, exclude_rfq: Optional[bool] = None) -> Dict:
        params = {
            'tokenIn': token_in,
            'tokenOut': token_out,
            'amountIn': str(amount_in_wei),
            'gasInclude': 'true',
            'slippageTolerance': str(slippage_bps)
        }
        if single_path:
            params['onlySinglePath'] = 'true'
        if direct_pools:
            params['onlyDirectPools'] = 'true'
        if (self.exclude_rfq if exclude_rfq is None else exclude_rfq):
            params['excludeRFQSources'] = 'true'

        data = self._get(f"/{KYBER_CHAIN}/api/v1/routes", params)
        if data.get('code') != 0:
            raise RuntimeError(f"Kyber routes error: {data.get('message')}")
        return data['data']

    def build_tx(self, route_summary: Dict, sender: str, recipient: str, slippage_bps: int = 50) -> Dict:
        body = {
            'routeSummary': route_summary,
            'sender': sender,
            'recipient': recipient,
            'slippageTolerance': slippage_bps,
            'source': KYBER_CLIENT_ID,
            'deadline': int(datetime.now().timestamp()) + 1200,
            'enableGasEstimation': True,
        }
        data = self._post(f"/{KYBER_CHAIN}/api/v1/route/build", body)
        if data.get('code') != 0:
            raise RuntimeError(f"Kyber build error: {data.get('message')}")
        return data['data']

    def legacy_encode(self, token_in: str, token_out: str, amount_in_wei: int, to: str, slippage_bps: int = 50) -> Dict:
        params = {
            'tokenIn': token_in,
            'tokenOut': token_out,
            'amountIn': str(amount_in_wei),
            'to': to,
            'slippageTolerance': str(slippage_bps),
            'clientData': json.dumps({'source': KYBER_CLIENT_ID})
        }
        data = self._get(f"/{KYBER_CHAIN}/route/encode", params)
        if not data or 'encodedSwapData' not in data or 'routerAddress' not in data:
            raise RuntimeError('Kyber legacy encode failed')
        return data

    def _get_gas_params(self) -> Dict:
        # Prefer system EIP-1559 settings if available
        if self.system and hasattr(self.system, '_get_gas_params'):
            try:
                params = self.system._get_gas_params(self.w3)
                return params
            except Exception:
                pass
        # fallback to ultra-low EIP-1559 defaults
        return {
            'maxFeePerGas': int(0.001 * 1e9),  # 0.001 gwei
            'maxPriorityFeePerGas': int(0 * 1e9)
        }

    def _should_wait(self) -> bool:
        if self.system and hasattr(self.system, 'wait_for_receipt'):
            return bool(getattr(self.system, 'wait_for_receipt'))
        return True

    def _receipt_timeout(self) -> int:
        if self.system and hasattr(self.system, 'receipt_timeout_secs'):
            return int(getattr(self.system, 'receipt_timeout_secs'))
        return 120

    def _send(self, to: str, data: str, value_wei: int) -> Optional[str]:
        try:
            tx = {
                'to': Web3.to_checksum_address(to),
                'data': data,
                'value': int(value_wei),
                'from': self.account.address,
                'chainId': self.w3.eth.chain_id,
            }

            # Faster gas estimation with fallback
            try:
                est = self.w3.eth.estimate_gas(tx)  # type: ignore
                tx['gas'] = int(est * 1.05)  # Reduced buffer from 1.1 to 1.05
            except Exception:
                tx['gas'] = 300000  # Lower default gas limit

            # Apply gas cap if set
            if self.gas_cap:
                tx['gas'] = min(tx['gas'], int(self.gas_cap))

            # Get gas params once and cache them
            gas_params = self._get_gas_params()
            tx.update(gas_params)

            # Get nonce once
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx['nonce'] = nonce

            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, private_key=self.account.key)
            raw = getattr(signed, 'raw_transaction', None) or getattr(signed, 'rawTransaction', None)
            if raw is None:
                return None
            tx_hash = self.w3.eth.send_raw_transaction(raw)

            # Optional waiting with shorter timeout
            if self._should_wait():
                try:
                    receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)  # Reduced from 120
                    return tx_hash.hex() if receipt and receipt['status'] == 1 else None
                except Exception:
                    return None  # Don't retry, just return None for speed

            return tx_hash.hex()

        except Exception:
            return None

    def buy_eth_to_maxx(self, eth_amount_wei: int, slippage_bps: int = 50) -> Optional[str]:
        sender = self.account.address
        try:
            try:
                route = self.get_route(ETH_ADDRESS, MAXX, eth_amount_wei, slippage_bps, exclude_rfq=self.exclude_rfq)
                built = self.build_tx(route['routeSummary'], sender, sender, slippage_bps)
                router = built['routerAddress']
                data = built['data']
                value = int(built.get('transactionValue') or eth_amount_wei)
            except Exception:
                legacy = self.legacy_encode(ETH_ADDRESS, MAXX, eth_amount_wei, sender, slippage_bps)
                router = legacy['routerAddress']
                data = legacy['encodedSwapData']
                value = eth_amount_wei
            return self._send(router, data, value)
        except Exception as e:
            try:
                print(f"[KyberClient] buy_eth_to_maxx error: {e}")
            except Exception:
                pass
            return None

    def sell_maxx_to_eth(self, maxx_amount_wei: int, slippage_bps: int = 50) -> Optional[str]:
        # Optimized allowance checking - only check if we haven't set unlimited approval recently
        erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(MAXX), abi=[
            {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}
        ])

        try:
            # Quick allowance check
            allowance = erc20.functions.allowance(self.account.address, Web3.to_checksum_address(KYBER_ROUTER)).call()
            if allowance < maxx_amount_wei:
                # Set unlimited approval for speed (only once)
                approve_tx = erc20.functions.approve(Web3.to_checksum_address(KYBER_ROUTER), 2**256-1).build_transaction({
                    'from': self.account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'gas': 100000,  # Fixed gas for approval
                })
                approve_tx.update(self._get_gas_params())

                signed = self.w3.eth.account.sign_transaction(approve_tx, private_key=self.account.key)
                raw = getattr(signed, 'raw_transaction', None) or getattr(signed, 'rawTransaction', None)
                if raw is None:
                    return None  # Skip if can't sign
                h = self.w3.eth.send_raw_transaction(raw)

                # Don't wait for approval to speed up trading
                if not self._should_wait():
                    pass  # Skip waiting
                else:
                    try:
                        self.w3.eth.wait_for_transaction_receipt(h, timeout=15)
                    except Exception:
                        pass  # Continue anyway
        except Exception:
            pass  # Skip approval issues for speed

        # Proceed with swap
        sender = self.account.address
        try:
            # Try modern API first, fallback to legacy
            try:
                route = self.get_route(MAXX, ETH_ADDRESS, maxx_amount_wei, slippage_bps, exclude_rfq=self.exclude_rfq)
                built = self.build_tx(route['routeSummary'], sender, sender, slippage_bps)
                router = built['routerAddress']
                data = built['data']
            except Exception:
                legacy = self.legacy_encode(MAXX, ETH_ADDRESS, maxx_amount_wei, sender, slippage_bps)
                router = legacy['routerAddress']
                data = legacy['encodedSwapData']

            return self._send(router, data, 0)
        except Exception:
            return None
