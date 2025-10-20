#!/usr/bin/env python3
import asyncio
import os
import signal
import sys
import logging
from decimal import Decimal
from typing import Optional

import requests
from dotenv import load_dotenv

from master_trading_system import MasterTradingSystem
from kyber_client import KyberClient
import standalone_config as config


DEX_PAIR = getattr(config, 'MAXX_ETH_POOL', '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148')
DEX_URL = f"https://api.dexscreener.com/latest/dex/pairs/base/{DEX_PAIR}"
USD_TO_SPEND = Decimal('7')
USD_RESERVE = Decimal('2')  # keep $2 of ETH for gas

# Logging setup
logger = logging.getLogger("strategy_buy7usd_reactive")
logger.setLevel(logging.INFO)
_fh = logging.FileHandler("strategy_buy7usd_reactive.log")
_fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
_sh = logging.StreamHandler()
_sh.setFormatter(logging.Formatter('%(message)s'))
if not logger.handlers:
    logger.addHandler(_fh)
    logger.addHandler(_sh)


def get_prices() -> Optional[dict]:
    try:
        r = requests.get(DEX_URL, timeout=10)
        r.raise_for_status()
        d = r.json()
        pair = (d.get('pairs') or [None])[0]
        if not pair:
            return None
        # priceUsd is MAXX in USD; priceNative is MAXX in ETH
        maxx_usd = Decimal(str(pair.get('priceUsd')))
        maxx_eth = Decimal(str(pair.get('priceNative')))
        # ETH_USD = MAXX_USD / MAXX_ETH
        eth_usd = maxx_usd / maxx_eth if maxx_eth > 0 else Decimal('3300')
        return {
            'maxx_usd': maxx_usd,
            'maxx_eth': maxx_eth,
            'eth_usd': eth_usd,
        }
    except Exception:
        return None


async def main():
    load_dotenv()
    system = MasterTradingSystem()
    ok = await system.initialize()
    if not ok:
        logger.error('INIT_FAIL')
        return

    kyber = KyberClient(system.w3, system.account, system)

    # Ultra-low gas hint (already minimal: baseFee + 1 wei); keep priority = 0
    try:
        system.base_fee_headroom_pct = 0.0  # no extra headroom
        system.priority_fee_gwei = 0.0
        system.max_fee_gwei = min(float(getattr(config, 'MAX_FEE_GWEI', 0.001)), 0.001)
    except Exception:
        pass

    # Determine ETH to spend from $7 with $2 reserve
    prices = get_prices()
    eth_usd = Decimal('3300')
    if prices and prices.get('eth_usd'):
        eth_usd = Decimal(prices['eth_usd'])

    # Reserve in ETH
    reserve_eth = USD_RESERVE / eth_usd

    eth_balance, maxx_balance = await system.get_balances()
    spend_eth = USD_TO_SPEND / eth_usd

    # Enforce reserve
    available_eth = Decimal(eth_balance) - reserve_eth
    if available_eth <= 0:
        logger.warning('Not enough ETH after reserve')
        return
    spend_eth = min(spend_eth, available_eth)
    if spend_eth <= 0:
        logger.warning('Spend amount <= 0')
        return

    # Execute buy
    logger.info(f"BUY: Spending ${USD_TO_SPEND} ~ {spend_eth:.6f} ETH via Kyber (reserve ${USD_RESERVE})")
    buy_tx = kyber.buy_eth_to_maxx(int(spend_eth * (10 ** 18)))
    logger.info(f"BUY_TX: {buy_tx} | https://basescan.org/tx/{buy_tx if buy_tx else ''}")

    # Establish entry and peak from fresh price
    await asyncio.sleep(5)
    prices = get_prices() or {}
    entry_usd = Decimal(str(prices.get('maxx_usd') or '0'))
    if entry_usd <= 0:
        # fallback compute from balances if needed
        entry_usd = Decimal('0')
    peak_usd = entry_usd
    holding = True

    logger.info(f"Entry price (MAXX USD): {entry_usd}")

    stop = False

    def handle_sigint(sig, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_sigint)

    tick = 0
    while not stop:
        try:
            prices = get_prices()
            if not prices:
                await asyncio.sleep(1)
                continue
            maxx_usd = prices['maxx_usd']
            eth_usd = prices['eth_usd']

            if holding:
                if peak_usd == 0 or maxx_usd > peak_usd:
                    peak_usd = maxx_usd

                if entry_usd > 0 and maxx_usd >= entry_usd * Decimal('1.10'):
                    # Sell all MAXX
                    _, maxx_balance_now = await system.get_balances()
                    if maxx_balance_now > 0:
                        logger.info(f"SELL: +10% reached. Selling {maxx_balance_now:.2f} MAXX via Kyber")
                        # to wei
                        try:
                            dec = system.maxx_contract.functions.decimals().call()
                        except Exception:
                            dec = 18
                        sell_wei = int(Decimal(str(maxx_balance_now)) * (10 ** dec))
                        sell_tx = kyber.sell_maxx_to_eth(sell_wei)
                        logger.info(f"SELL_TX: {sell_tx} | https://basescan.org/tx/{sell_tx if sell_tx else ''}")
                        holding = False
                        # set a drop target at -15% from peak
                        drop_target = peak_usd * Decimal('0.85')
                    else:
                        drop_target = peak_usd * Decimal('0.85')
                        holding = False
                else:
                    drop_target = peak_usd * Decimal('0.85')
            else:
                # flat: wait for 15% correction to buy again
                if maxx_usd <= drop_target and maxx_usd > 0:
                    # compute spend given current ETH
                    eth_balance_now, _ = await system.get_balances()
                    prices_now = get_prices() or prices
                    eth_usd_now = prices_now['eth_usd'] if prices_now else eth_usd
                    reserve_eth_now = USD_RESERVE / eth_usd_now
                    avail_eth_now = Decimal(eth_balance_now) - reserve_eth_now
                    to_spend = min(USD_TO_SPEND / eth_usd_now, avail_eth_now)
                    if to_spend > 0:
                        logger.info(f"REBUY: ${USD_TO_SPEND} ~ {to_spend:.6f} ETH via Kyber")
                        tx = kyber.buy_eth_to_maxx(int(to_spend * (10 ** 18)))
                        logger.info(f"BUY_TX: {tx} | https://basescan.org/tx/{tx if tx else ''}")
                        # reset entry and peak
                        entry_usd = maxx_usd
                        peak_usd = maxx_usd
                        holding = True
            # periodic status prints (price + balances)
            tick += 1
            if tick % 1 == 0:
                eth_bal, maxx_bal = await system.get_balances()
                # available ETH after reserve
                avail_eth = max(Decimal(eth_bal) - (USD_RESERVE / eth_usd), Decimal('0'))
                delta_entry = ((maxx_usd / entry_usd) - 1) * 100 if entry_usd > 0 else Decimal('0')
                state = 'HOLD' if holding else 'FLAT'
                logger.info(f"TICK | MAXX ${maxx_usd:.6f} | ETH ${eth_usd:.2f} | ETH {Decimal(eth_bal):.6f} (avail {avail_eth:.6f}) | MAXX {Decimal(maxx_bal):,.2f} | Entry ${entry_usd:.6f} Peak ${peak_usd:.6f} Δ {delta_entry:.2f}% | {state}")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Loop error: {e}")
            await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
