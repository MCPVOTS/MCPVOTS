"""
Simple environment loader to ensure .env is read before scripts use env vars.
"""
import os
from pathlib import Path

_LOADED = False

def load_env_once():
    global _LOADED
    if _LOADED:
        return
    try:
        from dotenv import load_dotenv
        # Look in repo root
        root = Path(__file__).resolve().parent
        dotenv_path = root / '.env'
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
        else:
            # Fallback to default loader
            load_dotenv()
        _LOADED = True
    except Exception:
        # dotenv optional; ignore if missing
        _LOADED = True
