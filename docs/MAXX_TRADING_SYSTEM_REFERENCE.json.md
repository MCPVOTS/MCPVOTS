{
  "meta": {
    "title": "MAXX Ecosystem Unified Trading System — Reference",
    "version": "1.0.0",
    "last_updated": "2025-10-16",
    "owner": "wallet: 0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9",
    "notes": "This is a machine-friendly JSON-in-Markdown reference designed for LLM agents and developers. Keep fields stable; extend instead of mutating semantics."
  },
  "project": {
    "language": "Python",
    "frameworks": ["web3.py v6", "requests", "python-dotenv (optional)"],
    "entrypoints": ["master_trading_system.py"],
    "dependencies_file": "requirements.txt",
    "logs": {
      "transaction_log_file": "REAL_TRADING_EXECUTION_REPORT.md / *.log",
      "windows_console": "ASCII-safe formatter; file logs are UTF-8"
    }
  },
  "network": {
    "chain": "Base Mainnet",
    "chain_id": 8453,
    "rpc_endpoints": [
      "https://mainnet.base.org",
      "https://rpc.ankr.com/base"
    ],
    "middleware": "geth_poa_middleware injected on Base"
  },
  "addresses": {
    "MAXX": "0xFB7a83abe4F4A4E51c77B92E521390B769ff6467",
    "WETH": "0x4200000000000000000000000000000000000006",
    "KyberRouter": "0x6131B5fae19EA4f9D964eAc0408E4408b66337b5",
    "pair_source": {
      "provider": "DexScreener",
      "pair_id": "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148",
      "endpoint": "https://api.dexscreener.com/latest/dex/pairs/base/{pair_id}"
    }
  },
  "environment": {
    "required": [
      "ETHEREUM_PRIVATE_KEY",
      "BASESCAN_API_KEY (optional; for explorer)"
    ],
    "loading": "dotenv supported if present"
  },
  "files": [
    {"path": "master_trading_system.py", "purpose": "Unified CLI tool; strategies, gas policy, status, utilities."},
    {"path": "kyber_client.py", "purpose": "Kyber aggregator swap client, infinite allowance, adaptive replacements."},
    {"path": "standalone_config.py", "purpose": "Runtime config: gas, router, pool id, feature toggles (loaded at start)."},
    {"path": "basescan_client.py", "purpose": "Optional explorer client (BaseScan) for recent txs."}
  ],
  "pricing": {
    "source": "DexScreener",
    "fields": ["priceUsd -> maxx_usd", "priceNative -> maxx_eth", "eth_usd = maxx_usd / maxx_eth"],
    "fallbacks": {"eth_usd": 3300}
  },
  "gas_policy": {
    "type": "EIP-1559",
    "params": {
      "base_fee_headroom_pct": {"default": 0.0, "cli_override": "--global-headroom-pct"},
      "priority_fee_gwei": {"default": 0.0, "cli_override": "--global-priority-gwei"},
      "max_fee_gwei": {"default": 0.001, "note": "Min-clamped to baseFee+headroom+1 wei."}
    },
    "caps": {
      "gas_units_default": 300000,
      "gas_usd_cap": {"cli": "--gas-usd-cap", "behavior": "skip action if est gas (ETH*USD) > cap"}
    },
    "estimation": "Uses maxFeePerGas*gasUnits for a conservative upper bound",
    "reliability": {
      "kyber_client_replacement": "Up to 2 mild replacement bumps (+1–2% headroom, +0.001–0.002 gwei) if not mined",
      "cancel_pending": "0-ETH self-tx replacement to clear stuck nonce",
      "retry_sell_fast": "Temporary higher headroom/tip for sell reattempt"
    }
  },
  "core_modes": {
    "status": {
      "desc": "Print balances, USD totals, RPC and explorer info.",
      "cli": "--mode status"
    },
    "sell-all": {
      "desc": "Sell entire MAXX balance to ETH via Kyber.",
      "cli": "--mode sell-all [--gas-limit]"
    },
    "reserve-swing": {
      "desc": "Alternate SELL-ALL if holding, else BUY-ALL with ETH above USD reserve; respects gas USD cap.",
      "defaults": {"reserve_usd": 10.0, "slippage_bps": 75, "gas_limit": 300000},
      "cli": "--mode reserve-swing --reserve-minutes <m> --reserve-usd <usd> --slippage-bps <bps> --gas-usd-cap <usd> [--gas-limit]"
    },
    "usd-pingpong": {
      "desc": "Buy $X then sell $X repeatedly; enforces gas USD cap.",
      "cli": "--mode usd-pingpong --usd-minutes <m> --usd-amount <usd> --slippage-bps <bps> --gas-usd-cap <usd> [--gas-limit]"
    },
    "reactive": {
      "desc": "+15% take-profit then -15% re-entry; $-budgeted with reserve.",
      "cli": "--mode reactive --usd-to-spend <usd> --usd-reserve <usd>"
    },
    "burst-cycle": {
      "desc": "Alternating SELL-ALL/BUY-ALL every N minutes; keeps reserve.",
      "cli": "--mode burst-cycle --burst-minutes <m> --burst-interval <min> --burst-usd-reserve <usd> [--gas-limit]"
    },
    "tiny-buy": {"desc": "Dust buy path test", "cli": "--mode tiny-buy --tiny-buy-eth <eth>"},
    "tiny-sell": {"desc": "Dust sell path test", "cli": "--mode tiny-sell --tiny-sell-eth <eth>"},
    "small-swap": {"desc": "0.0001 ETH roundtrip validation", "cli": "--mode small-swap --eth-amount <eth>"},
    "cancel-pending": {"desc": "Replace first pending nonce with 0-ETH self-tx", "cli": "--mode cancel-pending --headroom-pct <pct> --priority-gwei <gwei>"},
    "retry-sell-fast": {"desc": "Cancel pending then sell-all with temporary higher headroom/tip", "cli": "--mode retry-sell-fast --headroom-pct <pct> --priority-gwei <gwei> [--gas-limit]"},
    "buy-pump-then-dip": {
      "desc": "Buy on +pump% breakout, then buy again on -dip% pullback; no sells.",
      "defaults": {"reserve_usd": 10.0, "pump_gn_pct": 0.15, "dip_dr_pct": 0.15, "slippage_bps": 75},
      "cli": "--mode buy-pump-then-dip --pump-minutes <m> --reserve-usd <usd> --pump-gain-pct <f> --dip-drop-pct <f> --slippage-bps <bps> --gas-usd-cap <usd> [--gas-limit] --cooldown-sec <s>"
    }
  },
  "key_functions": {
    "MasterTradingSystem": {
      "get_balances": "Returns (eth: Decimal, maxx: Decimal)",
      "get_balances_cached": "Cached balances (min interval) to avoid 429",
      "buy_maxx(eth_amount, gas_limit, slippage_bps, min_maxx_out_wei)": "ETH->MAXX via Kyber",
      "sell_maxx(maxx_amount, gas_limit, slippage_bps, min_eth_out_wei)": "MAXX->ETH via Kyber",
      "_get_gas_params": "EIP-1559 calculation using baseFee and headroom",
      "_estimate_gas_cost_eth": "Conservative gas estimate in ETH",
      "cancel_pending": "Nonce replacement utility",
      "run_retry_sell_fast": "Cancel + temporary gas bump sell-all"
    },
    "KyberClient": {
      "buy_eth_to_maxx(eth_amount_wei, slippage_bps)": "Builds route and sends tx",
      "sell_maxx_to_eth(maxx_amount_wei, slippage_bps)": "Ensures allowance, builds route, sends tx",
      "gas_cap": "Optional gas limit enforcement"
    }
  },
  "configuration": {
    "file": "standalone_config.py",
    "fields": {
      "USE_EIP1559": {"type": "bool", "default": true},
      "MAX_FEE_GWEI": {"type": "float", "default": 0.001},
      "PRIORITY_FEE_GWEI": {"type": "float", "default": 0.0},
      "TX_WAIT_FOR_RECEIPT": {"type": "bool", "default": true},
      "TX_RECEIPT_TIMEOUT": {"type": "int", "default": 120},
      "BASE_FEE_HEADROOM_PCT": {"type": "float", "default": 0.0},
      "GAS_LIMIT": {"type": "int", "default": 300000},
      "MAXX_CONTRACT_ADDRESS": {"type": "str", "default": "0xFB7a83...6467"},
      "KYBER_ROUTER": {"type": "str", "default": "0x6131B5...37b5"},
      "MAXX_ETH_POOL": {"type": "str", "default": "DexScreener pair id"},
      "LOG_LEVEL": {"type": "str", "default": "INFO"},
      "CHAIN_ID": {"type": "int", "default": 8453}
    },
    "overrides_via_cli": [
      "--global-headroom-pct", "--global-priority-gwei", "--gas-limit", "--slippage-bps", "--gas-usd-cap",
      "mode-specific knobs (see core_modes)"
    ]
  },
  "safety": {
    "rate_limiting": "RPCManager RateLimiter; default 3 calls/sec",
    "rpc_rotation": "Auto-rotate across endpoints on failure",
    "balance_cache": "Avoids 429; uses cached values for short intervals",
    "infinite_approval": "One-time approve MAXX -> Kyber router (uint256 max)",
    "slippage": "Basis points; default 75 = 0.75%",
    "dust_thresholds": {"min_eth_trade": "1e-7 ETH", "dust_maxx": "1e-6 MAXX"},
    "skip_when_expensive": "gas_usd_cap enforces a per-action economic ceiling"
  },
  "operations": {
    "common_commands_pwsh": [
      {
        "desc": "Status",
        "cmd": "python master_trading_system.py --mode status"
      },
      {
        "desc": "Reserve swing ($10 reserve, cap $0.015, 0.75% slippage)",
        "cmd": "python master_trading_system.py --mode reserve-swing --reserve-minutes 15 --reserve-usd 10 --slippage-bps 75 --gas-usd-cap 0.015 --gas-limit 300000 --global-headroom-pct 0.01 --global-priority-gwei 0.001"
      },
      {
        "desc": "Buy pump then dip (buy-only)",
        "cmd": "python master_trading_system.py --mode buy-pump-then-dip --pump-minutes 30 --reserve-usd 10 --pump-gain-pct 0.15 --dip-drop-pct 0.15 --slippage-bps 75 --gas-usd-cap 0.015 --gas-limit 300000 --global-headroom-pct 0.01 --global-priority-gwei 0.001"
      }
    ],
    "playbooks": {
      "unstick_pending": ["--mode cancel-pending", "then optionally --mode retry-sell-fast with higher headroom/tip"],
      "test_paths": ["--mode tiny-buy", "--mode tiny-sell", "--mode small-swap"]
    }
  },
  "troubleshooting": {
    "429_or_rate_limits": "Rely on cached balances; wait a few seconds; RPC rotates automatically.",
    "gas_too_high": "Increase --gas-usd-cap slightly or wait; keep headroom low (e.g., 0–1%).",
    "no_price": "DexScreener may be rate-limited; retry in a few seconds.",
    "router_allowance": "First sell may require approval; infinite allowance is handled automatically."
  },
  "llm_extension_guidelines": {
    "invariants": [
      "ALWAYS use Kyber aggregator router 0x6131...37b5; do NOT reintroduce Uniswap V2 paths.",
      "Respect EIP-1559; do not hardcode legacy gasPrice unless explicitly requested.",
      "Keep USD reserve logic intact for buy modes; subtract estimated gas before spending.",
      "Default reserve is $10 across modes."
    ],
    "safe_edits": [
      "Add new modes by composing existing helpers (buy_maxx, sell_maxx, get_balances_cached).",
      "Expose new CLI flags consistently and document them here.",
      "Guard all network calls with short retries or caches if looped."
    ],
    "do_not": [
      "Do not remove skip-on-gas-usd-cap logic.",
      "Do not increase default slippage above 1% without explicit instruction.",
      "Do not log secrets (private key, API keys)."
    ],
    "review_checklist": [
      "Build/lint OK; no syntax errors",
      "Modes documented; CLI help updated",
      "Gas policy respected; defaults unchanged unless requested",
      "No leaked secrets; addresses checksumed"
    ]
  }
}
