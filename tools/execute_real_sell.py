#!/usr/bin/env python3
"""
REAL SELL ALL MAXX TOKENS - NO SIMULATION
=========================================

This executes a REAL transaction on Base chain
"""

import asyncio
import json
from datetime import datetime
from web3 import Web3
from standalone_config import ETHEREUM_PRIVATE_KEY

# Contract addresses (using checksum addresses)
MAXX_CONTRACT = Web3.to_checksum_address("0xFB7a83abe4F4A4E51c77B92E521390B769ff6467")
UNISWAP_ROUTER = Web3.to_checksum_address("0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24")
WALLET_ADDRESS = Web3.to_checksum_address("0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9")

# Base chain RPC
BASE_RPC = "https://mainnet.base.org"

# ERC20 ABI (minimal for balance and approve)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

# Uniswap Router ABI (minimal for swap)
ROUTER_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "type": "function"
    }
]

async def execute_real_sell():
    """Execute REAL sell transaction"""

    print("="*80)
    print("REAL SELL TRANSACTION - NO SIMULATION")
    print("="*80)
    print(f"Wallet: {WALLET_ADDRESS}")
    print(f"MAXX Contract: {MAXX_CONTRACT}")
    print(f"Uniswap Router: {UNISWAP_ROUTER}")
    print("-"*80)

    # Connect to Base chain
    print("\n[1] Connecting to Base chain...")
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))

    if not w3.is_connected():
        print("[ERROR] Cannot connect to Base chain!")
        return

    print(f"[OK] Connected to Base chain")
    print(f"    Block: {w3.eth.block_number}")

    # Setup account
    account = w3.eth.account.from_key(ETHEREUM_PRIVATE_KEY)
    if account.address.lower() != WALLET_ADDRESS.lower():
        print(f"[ERROR] Private key does not match wallet address!")
        print(f"    Expected: {WALLET_ADDRESS}")
        print(f"    Got: {account.address}")
        return

    print(f"[OK] Account verified: {account.address}")

    # Check balances
    print("\n[2] Checking balances...")

    # ETH balance
    eth_balance = w3.eth.get_balance(WALLET_ADDRESS)
    eth_balance_eth = eth_balance / 1e18
    print(f"    ETH Balance: {eth_balance_eth:.6f} ETH")

    # MAXX balance
    maxx_contract = w3.eth.contract(
        address=Web3.to_checksum_address(MAXX_CONTRACT),
        abi=ERC20_ABI
    )
    maxx_balance = maxx_contract.functions.balanceOf(WALLET_ADDRESS).call()
    maxx_balance_tokens = maxx_balance / 1e18

    print(f"    MAXX Balance: {maxx_balance_tokens:,.2f} tokens")

    if maxx_balance_tokens == 0:
        print("[ERROR] No MAXX tokens to sell!")
        return

    # Check gas price
    gas_price = w3.eth.gas_price
    gas_price_gwei = gas_price / 1e9
    print(f"    Current Gas: {gas_price_gwei:.2f} Gwei")

    # Use minimum gas for Base (0.1 Gwei minimum)
    min_gas_price = 100000000  # 0.1 Gwei in wei
    use_gas_price = max(gas_price, min_gas_price)
    use_gas_gwei = use_gas_price / 1e9
    print(f"    Using Gas: {use_gas_gwei:.2f} Gwei")

    # Get price estimate
    print("\n[3] Getting price estimate...")

    # This is a simplified estimate - in production use DEX aggregator
    estimated_price = 0.000033  # Approximate price
    estimated_eth = maxx_balance_tokens * estimated_price * 0.997  # 0.3% fee
    estimated_usd = estimated_eth * 3300

    print(f"    Est. Price: ${estimated_price:.8f}")
    print(f"    Est. ETH: {estimated_eth:.6f}")
    print(f"    Est. USD: ${estimated_usd:.2f}")

    # Calculate gas needed
    approve_gas = 50000
    swap_gas = 150000
    total_gas = approve_gas + swap_gas
    gas_cost_eth = (total_gas * use_gas_price) / 1e18

    print(f"    Gas Cost: {gas_cost_eth:.6f} ETH")

    if eth_balance_eth < gas_cost_eth + 0.00001:
        print(f"[WARNING] Low ETH for gas!")

    # Execute approval
    print("\n[4] Approving MAXX spending...")

    approve_tx = maxx_contract.functions.approve(
        UNISWAP_ROUTER,
        maxx_balance
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': approve_gas,
        'gasPrice': use_gas_price,
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS)
    })

    # Sign and send approval
    signed_approve = w3.eth.account.sign_transaction(approve_tx, ETHEREUM_PRIVATE_KEY)
    approve_tx_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)

    print(f"    Approval TX: {approve_tx_hash.hex()}")
    print(f"    Waiting for confirmation...")

    # Wait for approval
    approve_receipt = w3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=120)

    if approve_receipt['status'] == 1:
        print(f"    [OK] Approval confirmed!")
    else:
        print(f"    [ERROR] Approval failed!")
        return

    # Execute swap
    print("\n[5] Executing swap MAXX -> ETH...")

    # Build swap transaction
    router_contract = w3.eth.contract(
        address=Web3.to_checksum_address(UNISWAP_ROUTER),
        abi=ROUTER_ABI
    )

    # Calculate minimum ETH output (5% slippage)
    min_eth = int(estimated_eth * 0.95 * 1e18)

    swap_tx = router_contract.functions.swapExactTokensForETH(
        maxx_balance,
        min_eth,
        [MAXX_CONTRACT, "0x4200000000000000000000000000000000000006"],  # MAXX -> WETH on Base
        WALLET_ADDRESS,
        int(w3.eth.get_block('latest')['timestamp']) + 300  # 5 minute deadline
    ).build_transaction({
        'from': WALLET_ADDRESS,
        'gas': swap_gas,
        'gasPrice': use_gas_price,
        'nonce': w3.eth.get_transaction_count(WALLET_ADDRESS)
    })

    # Sign and send swap
    print("    Signing transaction...")
    signed_swap = w3.eth.account.sign_transaction(swap_tx, ETHEREUM_PRIVATE_KEY)

    print("    Sending transaction...")
    swap_tx_hash = w3.eth.send_raw_transaction(signed_swap.raw_transaction)

    print(f"    Swap TX: {swap_tx_hash.hex()}")
    print(f"    Waiting for confirmation...")

    # Wait for swap
    swap_receipt = w3.eth.wait_for_transaction_receipt(swap_tx_hash, timeout=120)

    if swap_receipt['status'] == 1:
        print(f"\n[SUCCESS] SELL EXECUTED!")
        print(f"    Transaction: https://basescan.org/tx/{swap_tx_hash.hex()}")

        # Calculate actual gas used
        gas_used = swap_receipt['gasUsed']
        gas_used_eth = (gas_used * use_gas_price) / 1e18
        gas_used_usd = gas_used_eth * 3300

        print(f"    Gas Used: {gas_used_eth:.6f} ETH (${gas_used_usd:.2f})")

        # Update balances
        new_eth_balance = w3.eth.get_balance(WALLET_ADDRESS) / 1e18
        new_maxx_balance = maxx_contract.functions.balanceOf(WALLET_ADDRESS).call() / 1e18

        print(f"\n    New Balances:")
        print(f"    ETH: {new_eth_balance:.6f} (+{new_eth_balance - eth_balance_eth:+.6f})")
        print(f"    MAXX: {new_maxx_balance:,.2f}")

        # Save transaction
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'type': 'REAL_SELL_ALL',
            'maxx_sold': maxx_balance_tokens,
            'maxx_contract': MAXX_CONTRACT,
            'approval_tx': approve_tx_hash.hex(),
            'swap_tx': swap_tx_hash.hex(),
            'gas_used': gas_used,
            'gas_price_gwei': low_gas_gwei,
            'gas_cost_eth': gas_used_eth,
            'status': 'CONFIRMED',
            'eth_before': eth_balance_eth,
            'eth_after': new_eth_balance,
            'maxx_before': maxx_balance_tokens,
            'maxx_after': new_maxx_balance
        }

        with open('maxx_real_sell_transaction.json', 'w') as f:
            json.dump(transaction, f, indent=2)

        print(f"\n[SAVED] Transaction saved to maxx_real_sell_transaction.json")

        return swap_tx_hash.hex()

    else:
        print(f"\n[ERROR] Transaction failed!")
        print(f"    Check BaseScan: https://basescan.org/tx/{swap_tx_hash.hex()}")
        return None

if __name__ == "__main__":
    try:
        tx_hash = asyncio.run(execute_real_sell())
        if tx_hash:
            print(f"\n[SUCCESS] REAL SELL COMPLETE: {tx_hash}")
        else:
            print(f"\n[FAILED] SELL FAILED")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()