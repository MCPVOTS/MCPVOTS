import asyncio
import argparse
import time
from decimal import Decimal

from master_trading_system import MasterTradingSystem


async def main():
    parser = argparse.ArgumentParser(description="Batch buy small USD amounts then sell final USD amount")
    parser.add_argument("--usd", type=float, default=1.0, help="USD amount per buy")
    parser.add_argument("--count", type=int, default=10, help="Number of buys")
    parser.add_argument("--interval-sec", type=int, default=30, help="Seconds between buys")
    parser.add_argument("--sell-usd", type=float, default=10.0, help="Final USD amount to sell")
    parser.add_argument("--slippage-bps", type=int, default=75, help="Slippage bps for buys/sell")
    parser.add_argument("--gas-usd-cap", type=float, default=0.01, help="Skip action if est gas USD exceeds this cap")
    parser.add_argument("--gas-limit", type=int, default=None, help="Optional gas limit override")
    parser.add_argument("--global-headroom-pct", type=float, default=0.0, help="Global base fee headroom pct (e.g., 0.0)")
    parser.add_argument("--global-priority-gwei", type=float, default=0.0005, help="Global priority fee gwei (e.g., 0.0005)")

    args = parser.parse_args()

    system = MasterTradingSystem()
    # Apply global gas overrides
    system.base_fee_headroom_pct = float(args.global_headroom_pct)
    system.priority_fee_gwei = float(args.global_priority_gwei)

    if not await system.initialize():
        print("Failed to initialize system")
        return 1

    usd_per_buy = Decimal(str(args.usd))
    gas_usd_cap = Decimal(str(args.gas_usd_cap)) if args.gas_usd_cap is not None else None
    gas_limit = args.gas_limit
    slippage_bps = int(args.slippage_bps)

    # Perform sequential buys
    for i in range(int(args.count)):
        try:
            prices = system._get_prices()
            if not prices or not prices.get('eth_usd'):
                print(f"[{i+1}/{args.count}] Price fetch failed; retrying in 5s...")
                await asyncio.sleep(5)
                continue
            eth_usd = Decimal(str(prices['eth_usd']))
            if eth_usd <= 0:
                print(f"[{i+1}/{args.count}] Invalid ETH/USD; skipping this iteration")
                await asyncio.sleep(3)
                continue

            buy_eth = usd_per_buy / eth_usd

            # Gas cap check
            w3 = await system.rpc_manager.get_w3_instance()
            gas_units = int(gas_limit or getattr(system, 'GAS_LIMIT', 300000))
            est_gas_eth = system._estimate_gas_cost_eth(w3, gas_units)
            est_gas_usd = est_gas_eth * eth_usd
            if gas_usd_cap is not None and est_gas_usd > gas_usd_cap:
                print(f"[{i+1}/{args.count}] BUY skip: gas ${est_gas_usd:.4f} > cap ${gas_usd_cap}")
            else:
                print(f"[{i+1}/{args.count}] BUY ${usd_per_buy} (~{buy_eth:.8f} ETH) | gas~${est_gas_usd:.4f}")
                txb = await system.buy_maxx(buy_eth, gas_limit=gas_limit, slippage_bps=slippage_bps)
                print(f"[{i+1}/{args.count}] BUY_TX: {txb}")
        except Exception as e:
            print(f"[{i+1}/{args.count}] BUY error: {e}")

        if i < int(args.count) - 1:
            await asyncio.sleep(int(args.interval_sec))

    # Final sell of $sell-usd worth
    try:
        prices2 = system._get_prices()
        if not prices2 or not prices2.get('maxx_usd'):
            print("SELL: Price fetch failed; aborting final sell")
            return 0
        maxx_usd = Decimal(str(prices2['maxx_usd']))
        eth_usd = Decimal(str(prices2['eth_usd'])) if prices2.get('eth_usd') else Decimal('0')
        target_usd = Decimal(str(args.sell_usd))
        if maxx_usd <= 0:
            print("SELL: Invalid MAXX/USD; aborting")
            return 0

        # Determine amount of MAXX to sell (clamped by available balance)
        _, cur_maxx = await system.get_balances()
        cur_maxx = Decimal(str(cur_maxx))
        target_maxx = target_usd / maxx_usd
        sell_amt = min(cur_maxx, target_maxx)

        if sell_amt <= 0:
            print("SELL: No MAXX to sell for the final USD amount")
            return 0

        # Gas cap check for sell
        w3 = await system.rpc_manager.get_w3_instance()
        gas_units = int(gas_limit or getattr(system, 'GAS_LIMIT', 300000))
        est_gas_eth = system._estimate_gas_cost_eth(w3, gas_units)
        est_gas_usd = est_gas_eth * eth_usd if eth_usd > 0 else Decimal('0')
        if gas_usd_cap is not None and eth_usd > 0 and est_gas_usd > gas_usd_cap:
            print(f"SELL skip: gas ${est_gas_usd:.4f} > cap ${gas_usd_cap}")
            return 0

        print(f"SELL ${target_usd} (~{sell_amt:.6f} MAXX) | gas~${est_gas_usd:.4f}")
        txs = await system.sell_maxx(sell_amt, gas_limit=gas_limit, slippage_bps=slippage_bps)
        print(f"SELL_TX: {txs}")
    except Exception as e:
        print(f"SELL error: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
