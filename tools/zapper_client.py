"""
Lightweight Zapper GraphQL client for fetching token price ticks and metadata.

Environment:
  - ZAPPER_API_KEY: Your Zapper API key (required)

Notes:
  - Endpoint: https://public.zapper.xyz/graphql
  - We keep requests minimal to conserve credits.
  - The priceTicks field typically lives under fungibleTokenV2.priceData.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

ZAPPER_GRAPHQL_URL = "https://public.zapper.xyz/graphql"


class ZapperClientError(Exception):
    pass


class ZapperClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 20.0):
        # Load .env lazily so CLI users don't need to export manually
        try:
            load_dotenv(override=False)
        except Exception:
            pass
        self.api_key = api_key or os.getenv("ZAPPER_API_KEY")
        if not self.api_key:
            raise ZapperClientError("ZAPPER_API_KEY not set in environment or passed explicitly")
        self._client = httpx.Client(timeout=timeout)

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass

    @retry(
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type(ZapperClientError),
        reraise=True,
    )
    def _post(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "x-zapper-api-key": self.api_key,
        }
        resp = self._client.post(ZAPPER_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers)
        if resp.status_code != 200:
            raise ZapperClientError(f"Zapper API HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        if "errors" in data and data["errors"]:
            # Surface the first error
            err = data["errors"][0]
            raise ZapperClientError(f"Zapper GraphQL error: {err}")
        return data.get("data") or {}

    def fetch_price_ticks(
        self,
        token_address: str,
        chain_id: int = 8453,
        currency: str = "USD",
        timeframe_candidates: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch price ticks for a token. Tries a few common timeFrame enum strings for compatibility.

        Returns a list of dicts: { open, median, close, timestamp }
        """
        timeframe_candidates = timeframe_candidates or [
            # Safer, commonly supported enums in Zapper schema
            "FIVE_MINUTES",
            "FIFTEEN_MINUTES",
            "THIRTY_MINUTES",
            "HOUR",
            "FOUR_HOURS",
            "DAY",
        ]

        last_error: Optional[Exception] = None
        for tf in timeframe_candidates:
            # Approach A: variables typed as proper ENUMs (Currency, TimeFrame)
            query_enum_var = (
                "query Token($address: Address!, $chainId: Int!, $currency: Currency!, $timeFrame: TimeFrame!) {\n"
                "  fungibleTokenV2(address: $address, chainId: $chainId) {\n"
                "    priceData {\n"
                "      price\n"
                "      priceChange1h\n"
                "      priceChange24h\n"
                "      volume24h\n"
                "      priceTicks(currency: $currency, timeFrame: $timeFrame) { open median close timestamp }\n"
                "    }\n"
                "  }\n"
                "}"
            )
            variables_enum = {
                "address": token_address,
                "chainId": chain_id,
                "currency": currency,
                "timeFrame": tf,
            }
            try:
                data = self._post(query_enum_var, variables_enum)
                pd = ((data or {}).get("fungibleTokenV2") or {}).get("priceData") or {}
                ticks = pd.get("priceTicks") or []
                if isinstance(ticks, list) and ticks:
                    return ticks
            except Exception as e:
                last_error = e
                # Fall through to approach B

            # Approach B: inline enum literal for timeFrame, variable for currency
            query_inline = (
                "query Token($address: Address!, $chainId: Int!, $currency: Currency!) {\n"
                "  fungibleTokenV2(address: $address, chainId: $chainId) {\n"
                "    priceData {\n"
                "      price\n"
                "      priceChange1h\n"
                "      priceChange24h\n"
                "      volume24h\n"
                f"      priceTicks(currency: $currency, timeFrame: {tf}) {{ open median close timestamp }}\n"
                "    }\n"
                "  }\n"
                "}"
            )
            variables_inline = {
                "address": token_address,
                "chainId": chain_id,
                "currency": currency,
            }
            try:
                data = self._post(query_inline, variables_inline)
                pd = ((data or {}).get("fungibleTokenV2") or {}).get("priceData") or {}
                ticks = pd.get("priceTicks") or []
                if isinstance(ticks, list) and ticks:
                    return ticks
            except Exception as e:
                last_error = e
                # Approach C: inline both currency and timeFrame as enum literals
                try:
                    query_both_inline = (
                        "query Token($address: Address!, $chainId: Int!) {\n"
                        "  fungibleTokenV2(address: $address, chainId: $chainId) {\n"
                        "    priceData {\n"
                        "      price\n"
                        "      priceChange1h\n"
                        "      priceChange24h\n"
                        "      volume24h\n"
                        f"      priceTicks(currency: {currency}, timeFrame: {tf}) {{ open median close timestamp }}\n"
                        "    }\n"
                        "  }\n"
                        "}"
                    )
                    variables_both_inline = {
                        "address": token_address,
                        "chainId": chain_id,
                    }
                    data = self._post(query_both_inline, variables_both_inline)
                    pd = ((data or {}).get("fungibleTokenV2") or {}).get("priceData") or {}
                    ticks = pd.get("priceTicks") or []
                    if isinstance(ticks, list) and ticks:
                        return ticks
                except Exception as e2:
                    last_error = e2
                    continue

        if last_error:
            raise ZapperClientError(f"Failed to fetch priceTicks with provided timeframe candidates: {last_error}")
        raise ZapperClientError("No priceTicks returned; check token address or timeframe compatibility")


__all__ = ["ZapperClient", "ZapperClientError", "ZAPPER_GRAPHQL_URL"]
