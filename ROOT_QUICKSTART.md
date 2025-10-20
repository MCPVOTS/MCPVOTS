# Root Quickstart

Keep the essential files at the top of the repo and drive everything from the CLI—no moving folders, no broken paths.

## Most important files at root

- .env.example → template for your secrets (copy to .env)
- .env → your local secrets (gitignored)
- maxx_trader_fix.py → main trading entrypoint (kept intact)
- ecosystem_cli.py → unified runner to operate from the root
- standalone_config.py → proven on-chain addresses and defaults
- basescan_client.py → Etherscan v2 / BaseScan API client

Optional helpers

- load_env.ps1 → loads .env into the current PowerShell session
- .gitignore → protects secrets, DB files, and build output from Git commits

## Typical workflows from root

Trading (reactive)

```pwsh
python .\ecosystem_cli.py trade reactive --sell-gain-pct 0.12 --rebuy-drop-pct 0.10 --usd-reserve 10 --spend-all --log-level INFO
```

Trading (single test)

```pwsh
python .\ecosystem_cli.py trade test --log-level INFO
```

Mini-app build/dev (no folder changing)

```pwsh
python .\ecosystem_cli.py app build
python .\ecosystem_cli.py app dev
```

Vercel helpers (run in mini-app path by default)

```pwsh
python .\ecosystem_cli.py vercel whoami
python .\ecosystem_cli.py vercel link
python .\ecosystem_cli.py vercel pull
python .\ecosystem_cli.py vercel deploy --prod
```

Environment check

```pwsh
python .\ecosystem_cli.py env check
```

Quick status

```pwsh
python .\ecosystem_cli.py status
```

## Load your .env into PowerShell (optional)

```pwsh
. .\load_env.ps1   # dot-source to populate $env:* for this session
```

## Notes

- We did not move or rename any existing files.
- The trading script paths were left unchanged.
- Use .env (gitignored) to override anything in standalone_config safely.
