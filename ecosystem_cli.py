#!/usr/bin/env python3
"""
Unified CLI for the ECOSYSTEM_UNIFIED workspace.

- Does NOT create folders or move files.
- Does NOT modify your trading runtime.
- Provides one-liners for frequent actions so you can work from root.

Commands:
  python ecosystem_cli.py trade [reactive|test|sell-all] [options]
  python ecosystem_cli.py app [build|dev]
  python ecosystem_cli.py vercel [whoami|link|pull|deploy]
  python ecosystem_cli.py env [check]
  python ecosystem_cli.py status

Examples:
  python ecosystem_cli.py trade reactive --sell-gain-pct 0.12 --rebuy-drop-pct 0.10 --usd-reserve 10 --spend-all
  python ecosystem_cli.py app dev
  python ecosystem_cli.py vercel link
  python ecosystem_cli.py vercel deploy --prod
"""
from __future__ import annotations
import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parent
MINI_APP_DIR = ROOT / "base-mini-apps" / "demos" / "mini-apps" / "workshops" / "my-simple-mini-app"
TRADER_PATH = ROOT / "maxx_trader_fix.py"


def _run(cmd: list[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> int:
    print(f"Running: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env or os.environ.copy())
        return r.returncode
    except FileNotFoundError as e:
        print(f"Command not found: {cmd[0]} ({e})")
        return 127
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def cmd_trade(args: argparse.Namespace) -> int:
    if not TRADER_PATH.exists():
        print(f"Trading script not found: {TRADER_PATH}")
        return 1

    mode = args.mode
    if mode == "reactive":
        cmd = [
            sys.executable, str(TRADER_PATH), "--mode", "reactive",
            "--sell-gain-pct", str(args.sell_gain_pct),
            "--rebuy-drop-pct", str(args.rebuy_drop_pct),
            "--usd-reserve", str(args.usd_reserve),
        ]
        if args.spend_all:
            cmd.append("--spend-all")
        if args.log_level:
            cmd += ["--log-level", args.log_level]
        return _run(cmd, cwd=ROOT)

    if mode == "test":
        cmd = [sys.executable, str(TRADER_PATH), "--mode", "test"]
        if args.log_level:
            cmd += ["--log-level", args.log_level]
        return _run(cmd, cwd=ROOT)

    if mode == "sell-all":
        cmd = [sys.executable, str(TRADER_PATH), "--mode", "sell-all"]
        if args.log_level:
            cmd += ["--log-level", args.log_level]
        return _run(cmd, cwd=ROOT)

    print(f"Unknown trading mode: {mode}")
    return 2


def cmd_app(args: argparse.Namespace) -> int:
    if not MINI_APP_DIR.exists():
        print(f"Mini-app directory not found: {MINI_APP_DIR}")
        return 1

    if args.action == "build":
        # npm run build in mini-app directory
        return _run(["npm", "run", "build"], cwd=MINI_APP_DIR)

    if args.action == "dev":
        # npm run dev in mini-app directory
        return _run(["npm", "run", "dev"], cwd=MINI_APP_DIR)

    print(f"Unknown app action: {args.action}")
    return 2


def _ensure_vercel() -> bool:
    ver = shutil.which("vercel")
    if not ver:
        print("Vercel CLI not found. Install from https://vercel.com/docs/cli or `npm i -g vercel`.")
        return False
    return True


def cmd_vercel(args: argparse.Namespace) -> int:
    if not _ensure_vercel():
        return 127

    cwd = MINI_APP_DIR if args.cwd == "mini-app" else ROOT

    if args.sub == "whoami":
        return _run(["vercel", "whoami"], cwd=cwd)

    if args.sub == "link":
        # Non-interactive attempt; if it needs prompts, user can re-run without --yes
        return _run(["vercel", "link"], cwd=cwd)

    if args.sub == "pull":
        return _run(["vercel", "pull"], cwd=cwd)

    if args.sub == "deploy":
        cmd = ["vercel"]
        if args.prod:
            cmd.append("--prod")
        return _run(cmd, cwd=cwd)

    print(f"Unknown vercel subcommand: {args.sub}")
    return 2


MASK = "********"
SENSITIVE_KEYS = {
    "ETHEREUM_PRIVATE_KEY",
    "BASESCAN_API_KEY",
    "ETHERSCAN_API_KEY",
    "REDIS_TOKEN",
}


def _mask_value(key: str, val: Optional[str]) -> str:
    if not val:
        return "<missing>"
    if key in SENSITIVE_KEYS:
        return MASK if len(val) <= 8 else (val[:4] + MASK + val[-4:])
    return val


def cmd_env(args: argparse.Namespace) -> int:
    # Check root .env and some expected vars
    env_path = ROOT / ".env"
    print(f"Root .env: {'present' if env_path.exists() else 'missing'} | {env_path}")

    # Print a few key env values masked
    keys = [
        "ETHEREUM_PRIVATE_KEY",
        "BASE_RPC_URL",
        "BASESCAN_API_KEY",
        "DEXSCREENER_PAIR_ADDRESS",
        "MAXX_TOKEN_ADDRESS",
    ]
    for k in keys:
        print(f"{k} = {_mask_value(k, os.environ.get(k))}")

    # Mini-app envs (if using Next public variables, they usually start with NEXT_PUBLIC_*)
    next_keys = [
        "NEXT_PUBLIC_URL",
        "NEXT_PUBLIC_VERSION",
        "FARCASTER_HEADER",
        "FARCASTER_PAYLOAD",
        "FARCASTER_SIGNATURE",
        "REDIS_URL",
        "REDIS_TOKEN",
    ]

    print("\nMini-app env (masked where needed):")
    for k in next_keys:
        print(f"{k} = {_mask_value(k, os.environ.get(k))}")

    return 0


def cmd_status(args: argparse.Namespace) -> int:
    # Basic summary for quick orientation from root
    print("Workspace status:")
    print(f"- Root: {ROOT}")
    print(f"- Trading script: {'present' if TRADER_PATH.exists() else 'missing'} -> {TRADER_PATH}")
    print(f"- Mini-app dir: {'present' if MINI_APP_DIR.exists() else 'missing'} -> {MINI_APP_DIR}")

    vercel_ok = shutil.which("vercel") is not None
    print(f"- Vercel CLI: {'available' if vercel_ok else 'missing'}")

    node_ok = shutil.which("node") is not None
    npm_ok = shutil.which("npm") is not None
    print(f"- Node: {'yes' if node_ok else 'no'} | npm: {'yes' if npm_ok else 'no'}")

    # Env quick check
    keys = ["ETHEREUM_PRIVATE_KEY", "BASESCAN_API_KEY"]
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        print(f"- Missing env: {', '.join(missing)} (set them in .env)")
    else:
        print("- Required env present: ETHEREUM_PRIVATE_KEY, BASESCAN_API_KEY")

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ecosystem unified CLI")
    sub = p.add_subparsers(dest="cmd")

    # trade
    pt = sub.add_parser("trade", help="Run trading system modes")
    pt.add_argument("mode", choices=["reactive", "test", "sell-all"], help="Trading mode")
    pt.add_argument("--sell-gain-pct", type=float, default=0.12)
    pt.add_argument("--rebuy-drop-pct", type=float, default=0.10)
    pt.add_argument("--usd-reserve", type=float, default=10.0)
    pt.add_argument("--spend-all", action="store_true")
    pt.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default=None)
    pt.set_defaults(func=cmd_trade)

    # app
    pa = sub.add_parser("app", help="Mini-app controls")
    pa.add_argument("action", choices=["build", "dev"], help="Build or run dev server")
    pa.set_defaults(func=cmd_app)

    # vercel
    pv = sub.add_parser("vercel", help="Vercel CLI helpers")
    pv.add_argument("sub", choices=["whoami", "link", "pull", "deploy"], help="Vercel action")
    pv.add_argument("--cwd", choices=["root", "mini-app"], default="mini-app", help="Directory to run Vercel in")
    pv.add_argument("--prod", action="store_true", help="Deploy to production")
    pv.set_defaults(func=cmd_vercel)

    # env
    pe = sub.add_parser("env", help="Environment helpers")
    pe.add_argument("action", choices=["check"], nargs="?", default="check")
    pe.set_defaults(func=cmd_env)

    # status
    ps = sub.add_parser("status", help="Quick workspace status")
    ps.set_defaults(func=cmd_status)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    if not argv:
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
