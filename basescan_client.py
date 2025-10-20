#!/usr/bin/env python3
"""
Etherscan v2 Multi-Chain client (works for Base via chainid=8453).
 - Supports account balance, multi-balance, tx lists, internal txs, and ERC20 transfers.
 - Reads API key from env BASESCAN_API_KEY (same key works on v2 endpoint).
Docs: https://docs.etherscan.io/
"""
from __future__ import annotations
import os
from typing import Optional, Dict, Any, List, Sequence

import requests


class EtherscanV2Client:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.etherscan.io/v2/api"):
        self.api_key = api_key or os.getenv("BASESCAN_API_KEY", "")
        self.base_url = base_url.rstrip('/')

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Use V2 endpoint for all chains
        url = self.base_url

        if self.api_key:
            params = {**params, 'apikey': self.api_key}
        resp = requests.get(url, params=params, timeout=25)
        resp.raise_for_status()
        return resp.json()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    # Accounts
    def get_balance(self, chainid: int, address: str, tag: str = 'latest') -> Optional[str]:
        try:
            data = self._get({'chainid': chainid, 'module': 'account', 'action': 'balance', 'address': address, 'tag': tag})
            return data.get('result')
        except Exception:
            return None

    def get_balancemulti(self, chainid: int, addresses: Sequence[str], tag: str = 'latest') -> List[Dict[str, Any]]:
        try:
            joined = ','.join(addresses)
            data = self._get({'chainid': chainid, 'module': 'account', 'action': 'balancemulti', 'address': joined, 'tag': tag})
            result = data.get('result')
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def get_txlist(self, chainid: int, address: str, startblock: int = 0, endblock: int = 99999999, page: int = 1, offset: int = 10, sort: str = 'desc') -> List[Dict[str, Any]]:
        try:
            data = self._get({'chainid': chainid, 'module': 'account', 'action': 'txlist', 'address': address, 'startblock': startblock, 'endblock': endblock, 'page': page, 'offset': offset, 'sort': sort})
            result = data.get('result')
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def get_txlistinternal(self, chainid: int, address: Optional[str] = None, txhash: Optional[str] = None, startblock: Optional[int] = None, endblock: Optional[int] = None, page: int = 1, offset: int = 10, sort: str = 'asc') -> List[Dict[str, Any]]:
        try:
            params: Dict[str, Any] = {'chainid': chainid, 'module': 'account', 'action': 'txlistinternal', 'page': page, 'offset': offset, 'sort': sort}
            if address:
                params['address'] = address
            if txhash:
                params['txhash'] = txhash
            if startblock is not None:
                params['startblock'] = startblock
            if endblock is not None:
                params['endblock'] = endblock
            data = self._get(params)
            result = data.get('result')
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def get_tokentx(self, chainid: int, address: Optional[str] = None, contractaddress: Optional[str] = None, startblock: int = 0, endblock: int = 99999999, page: int = 1, offset: int = 100, sort: str = 'desc') -> List[Dict[str, Any]]:
        try:
            params: Dict[str, Any] = {'chainid': chainid, 'module': 'account', 'action': 'tokentx', 'startblock': startblock, 'endblock': endblock, 'page': page, 'offset': offset, 'sort': sort}
            if address:
                params['address'] = address
            if contractaddress:
                params['contractaddress'] = contractaddress
            data = self._get(params)
            result = data.get('result')
            return result if isinstance(result, list) else []
        except Exception:
            return []
