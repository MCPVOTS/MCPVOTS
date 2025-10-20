# Deprecated/Archived Components

This folder contains legacy agent/network scaffolding that is no longer used by the primary trading system (`maxx_trader_fix.py`) or current analytics.

Archived modules:

- `BASE_AGENTIC/`
- `BASE_AUTONOMOUS_BOT/`
- `BASE_NETWORK/`
- `MAXX_token_agent.py`
- `maxx_network_utils.py`
- `storage_integration.py`

Reason:

- These were part of an experimental agent/bot architecture. The active system uses the `core/` modules and does not depend on these packages.

How to restore:

- Move any needed file or folder back to the repository root.
- Update imports accordingly if you relocate files.

Note:

- If you have custom code importing these modules, update it to use `core/` equivalents or restore the archived modules.
