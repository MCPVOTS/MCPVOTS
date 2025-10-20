#!/usr/bin/env python3
import asyncio
from master_trading_system import MasterTradingSystem


async def main():
    sys = MasterTradingSystem()
    ok = await sys.initialize()
    if ok:
        await sys.print_system_status()


if __name__ == "__main__":
    asyncio.run(main())
