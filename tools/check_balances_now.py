#!/usr/bin/env python3
import asyncio
from decimal import Decimal
import requests

from master_trading_system import MasterTradingSystem
import standalone_config as config


def get_eth_usd() -> Decimal:
    try:
        pair = getattr(config, 'MAXX_ETH_POOL', '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148')
        url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json()
        p = (d.get('pairs') or [None])[0]
        if not p:
            return Decimal('3300')
        maxx_usd = Decimal(str(p.get('priceUsd')))
        maxx_eth = Decimal(str(p.get('priceNative')))
        return (maxx_usd / maxx_eth) if (maxx_eth and maxx_eth > 0) else Decimal('3300')
    except Exception:
        return Decimal('3300')


async def main():
    sys = MasterTradingSystem()
    ok = await sys.initialize()
    if not ok:
        print('INIT_FAIL')
        return

    eth, maxx = await sys.get_balances()
    eth_usd = get_eth_usd()
    # Get MAXX USD via DexScreener pair
    try:
        pair = getattr(config, 'MAXX_ETH_POOL', '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148')
        url = f"https://api.dexscreener.com/latest/dex/pairs/base/{pair}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json()
        p = (d.get('pairs') or [None])[0]
        maxx_usd = Decimal(str(p.get('priceUsd'))) if p else Decimal('0')
    except Exception:
        maxx_usd = Decimal('0')
    usd_reserve = Decimal('2')
    reserve_eth = usd_reserve / eth_usd
    available_eth = max(Decimal(eth) - reserve_eth, Decimal('0'))

    eth_value = Decimal(eth) * eth_usd
    maxx_value = Decimal(maxx) * maxx_usd
    total_usd = eth_value + maxx_value

    print(f"ETH:  {Decimal(eth):.6f} ETH (${eth_value:.2f})")
    print(f"MAXX: {Decimal(maxx):,.2f} MAXX (${maxx_value:.2f})")
    print(f"Reserve: {reserve_eth:.6f} ETH ($2.00)")
    print(f"Available: {available_eth:.6f} ETH (${available_eth*eth_usd:.2f})")
    print(f"Total Wallet USD: ${total_usd:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
