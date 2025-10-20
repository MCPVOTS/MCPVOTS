#!/usr/bin/env python3
"""
tx_gas_report.py — Fetch gas breakdown for a Base transaction and output JSON and/or Markdown.

Usage:
  python tools/tx_gas_report.py --tx 0x... [--out reports/tx.json] [--md reports/tx.md] [--rpc <url>]
"""
import argparse
import json
import sys
import urllib.request
import decimal
import os
from typing import Any, Dict, Optional

DEFAULT_RPCS = [
    # Developer access endpoint is often friendlier to scripts
    "https://developer-access-mainnet.base.org",
    # Public mainnet endpoint
    "https://mainnet.base.org",
]


def post(rpc: str, method: str, params: list[Any]) -> Any:
    data = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(
        rpc,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "tx-gas-report/1.0 (+https://base.org)",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = r.read()
    obj = json.loads(payload)
    if "error" in obj:
        raise RuntimeError(f"RPC error: {obj['error']}")
    return obj["result"]


def h2i(x: Optional[str]) -> Optional[int]:
    if not x or not isinstance(x, str):
        return None
    if not x.startswith("0x"):
        return None
    return int(x, 16)


def build_report(tx_hash: str, rpc: str) -> Dict[str, Any]:
    tx = post(rpc, "eth_getTransactionByHash", [tx_hash])
    if tx is None:
        raise RuntimeError("Transaction not found")
    rcpt = post(rpc, "eth_getTransactionReceipt", [tx_hash])
    if rcpt is None:
        raise RuntimeError("Receipt not found")

    blk = post(rpc, "eth_getBlockByHash", [rcpt["blockHash"], False]) if rcpt.get("blockHash") else None

    D = decimal.Decimal
    GWEI = D(10) ** 9
    ETH = D(10) ** 18

    gas_limit = h2i(tx.get("gas"))
    max_fee = h2i(tx.get("maxFeePerGas"))
    max_prio = h2i(tx.get("maxPriorityFeePerGas"))
    gas_used = h2i(rcpt.get("gasUsed"))
    eff = h2i(rcpt.get("effectiveGasPrice"))
    base = h2i(blk.get("baseFeePerGas")) if blk else None
    l1 = h2i(rcpt.get("l1Fee")) if (rcpt and "l1Fee" in rcpt) else None

    eff_gwei = (D(eff) / GWEI) if eff is not None else None
    base_gwei = (D(base) / GWEI) if base is not None else None
    implied_tip_gwei = (eff_gwei - base_gwei) if (eff_gwei is not None and base_gwei is not None) else None

    total_fee_wei = (D(gas_used) * D(eff)) if (gas_used is not None and eff is not None) else None

    def q(x: Optional[decimal.Decimal], places: str) -> Optional[str]:
        return None if x is None else str(x.quantize(decimal.Decimal(places)))

    report: Dict[str, Any] = {
        "chain": "base",
        "hash": tx_hash,
        "status": rcpt.get("status"),
        "blockNumber": rcpt.get("blockNumber"),
        "gasUsed": gas_used,
        "gasLimit": gas_limit,
        "baseFeePerGas_wei": base,
        "maxFeePerGas_wei": max_fee,
        "maxPriorityFeePerGas_wei": max_prio,
        "effectiveGasPrice_wei": eff,
        "effectiveGasPrice_gwei": q(eff_gwei, "0.000001"),
        "baseFee_gwei": q(base_gwei, "0.000001"),
        "impliedPriority_gwei": q(implied_tip_gwei, "0.000001"),
        "totalFee_wei": int(total_fee_wei) if total_fee_wei is not None else None,
        "totalFee_ETH": q((total_fee_wei / ETH) if total_fee_wei is not None else None, "0.000000000000000001"),
        "l1DataFee_wei": l1,
        "logs": len(rcpt.get("logs", [])),
    }
    return report


def markdown_from_report(r: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Base Tx Gas Breakdown\n")
    lines.append(f"Tx: `{r['hash']}`  ")
    lines.append(f"Explorer: https://basescan.org/tx/{r['hash']}\n")
    lines.append("## Summary\n")
    lines.append(f"- Status: {r.get('status')}  ")
    lines.append(f"- Gas Used: {r.get('gasUsed')}  ")
    lines.append(f"- Effective Gas Price: {r.get('effectiveGasPrice_gwei')} gwei  ")
    if r.get("baseFee_gwei") is not None:
        lines.append(f"- Base Fee: {r.get('baseFee_gwei')} gwei  ")
    if r.get("impliedPriority_gwei") is not None:
        lines.append(f"- Priority Tip (implied): {r.get('impliedPriority_gwei')} gwei  ")
    lines.append(f"- Total Fee: {r.get('totalFee_ETH')} ETH  ")
    if r.get("l1DataFee_wei") is not None:
        lines.append(f"- L1 Data Fee (wei): {r.get('l1DataFee_wei')}  ")
    lines.append("\n## Raw JSON\n")
    lines.append("```json")
    lines.append(json.dumps(r, indent=2))
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tx", required=True, help="Transaction hash")
    ap.add_argument("--out", help="Write JSON to this path")
    ap.add_argument("--md", help="Write Markdown to this path")
    ap.add_argument("--rpc", help="RPC URL for Base JSON-RPC. Defaults to BASE_RPC env or known public endpoints.")
    args = ap.parse_args()

    # Resolve RPC endpoint
    rpc = (
        args.rpc
        or os.environ.get("BASE_RPC")
        or DEFAULT_RPCS[0]
    )
    # Try chosen RPC, on failure try fallbacks
    last_err: Optional[Exception] = None
    report: Optional[Dict[str, Any]] = None
    for candidate in [rpc] + [r for r in DEFAULT_RPCS if r != rpc]:
        try:
            report = build_report(args.tx, candidate)
            rpc = candidate
            break
        except Exception as e:
            last_err = e
            continue
    if report is None:
        raise RuntimeError(f"Failed to fetch tx via RPCs. Last error: {last_err}")
    out_json = json.dumps(report, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_json)
    if args.md:
        md = markdown_from_report(report)
        os.makedirs(os.path.dirname(args.md), exist_ok=True)
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    # Always print JSON to stdout for convenience
    print(out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
