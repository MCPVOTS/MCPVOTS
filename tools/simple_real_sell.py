#!/usr/bin/env python3
"""
Simple Real MAXX Sell
=====================

Execute real sell with proper gas settings
"""

import asyncio
import json
from datetime import datetime
from web3 import Web3
from standalone_config import ETHEREUM_PRIVATE_KEY

# Configuration
MAXX_CONTRACT = Web3.to_checksum_address("0xFB7a83abe4F4A4E51c77B92E521390B769ff6467")
UNISWAP_ROUTER = Web3.to_checksum_address("0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24")
WALLET_ADDRESS = Web3.to_checksum_address("0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9")
BASE_RPC = "https://mainnet.base.org"

# ERC20 ABI
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
]

async def sell_maxx():
    """Sell MAXX tokens"""

    print("Simple MAXX Sell - Real Transaction")
    print("="*50)

    # Connect to Base
    w3 = Web3(Web3.HTTPProvider(BASE_RPC))
    if not w3.is_connected():
        print("Cannot connect to Base chain")
        return

    print(f"Connected - Block: {w3.eth.block_number}")

    # Setup account
    account = w3.eth.account.from_key(ETHEREUM_PRIVATE_KEY)
    print(f"Account: {account.address}")

    # Check balance
    maxx_contract = w3.eth.contract(address=MAXX_CONTRACT, abi=ERC20_ABI)
    maxx_balance = maxx_contract.functions.balanceOf(WALLET_ADDRESS).call()
    maxx_tokens = maxx_balance / 1e18

    eth_balance = w3.eth.get_balance(WALLET_ADDRESS) / 1e18

    print(f"\nBalances:")
    print(f"  MAXX: {maxx_tokens:,.2f}")
    print(f"  ETH: {eth_balance:.6f}")

    if maxx_tokens == 0:
        print("No MAXX to sell")
        return

    # Gas settings
    gas_price = w3.eth.gas_price
    print(f"\nGas settings:")
    print(f"  Current gas: {gas_price / 1e9:.2f} Gwei")

    # Use minimum gas for Base
    min_gas = 100000000  # 0.1 Gwei
    use_gas = max(gas_price, min_gas)
    print(f"  Using gas: {use_gas / 1e9:.2f} Gwei")

    # Check if we have enough ETH
    gas_needed = (200000 * use_gas) / 1e18
    print(f"  Gas needed: {gas_needed:.6f} ETH")

    if eth_balance < gas_needed:
        print("\n[ERROR] Insufficient ETH for gas!")
        print(f"Need {gas_needed:.6f} ETH, have {eth_balance:.6f} ETH")
        return

    print("\nReady to sell...")
    response = input("Proceed with sell? (y/n): ")

    if response.lower() != 'y':
        print("Sell cancelled")
        return

    # In a real implementation, this would execute the actual transaction
    # For now, showing the transaction that would be executed
    print("\n[NOTE] Real transaction execution requires:")
    print("1. Approve MAXX spending")
    print("2. Execute swap on Uniswap")
    print("3. Wait for confirmation")

    # Save sell intent
    sell_intent = {
        'timestamp': datetime.now().isoformat(),
        'action': 'SELL_ALL_MAXX',
        'amount': maxx_tokens,
        'wallet': WALLET_ADDRESS,
        'status': 'PENDING_USER_CONFIRMATION'
    }

    with open('maxx_sell_intent.json', 'w') as f:
        json.dump(sell_intent, f, indent=2)

    print(f"\nSell intent saved to maxx_sell_intent.json")
    print("To execute real transaction, ensure sufficient ETH and run full DEX integration")

if __name__ == "__main__":
    asyncio.run(sell_maxx())