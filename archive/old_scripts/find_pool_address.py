#!/usr/bin/env python3
"""
Find the correct MAXX/ETH pool address by querying the Uniswap V2 factory
"""
from web3 import Web3
from standalone_config import *

# Uniswap V2 Factory ABI (minimal)
FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"}
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "type": "function"
    }
]

def find_pool_address():
    """Find the MAXX/ETH pool address from the factory"""
    print("Finding MAXX/ETH pool address...")
    print(f"Factory: {UNISWAP_V2_FACTORY}")
    print(f"MAXX Token: {MAXX_CONTRACT_ADDRESS}")
    print(f"WETH: {WETH_ADDRESS}")

    # Connect to Base chain
    w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

    if not w3.is_connected():
        print("ERROR: Failed to connect to Base chain")
        return None

    print(f"Connected to chain ID: {w3.eth.chain_id}")

    # Create factory contract
    factory = w3.eth.contract(
        address=Web3.to_checksum_address(UNISWAP_V2_FACTORY),
        abi=FACTORY_ABI
    )

    try:
        # Get pair address
        pair_address = factory.functions.getPair(
            Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS),
            Web3.to_checksum_address(WETH_ADDRESS)
        ).call()

        print(f"Pool address: {pair_address}")

        if pair_address == "0x0000000000000000000000000000000000000000":
            print("ERROR: Pool does not exist!")
            return None

        return pair_address

    except Exception as e:
        print(f"ERROR: Failed to get pool address: {e}")
        return None

def test_pool_contract(pool_address):
    """Test if the pool contract is working"""
    print(f"\nTesting pool contract: {pool_address}")

    w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

    # Minimal pool ABI for getReserves
    POOL_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "getReserves",
            "outputs": [
                {"name": "reserve0", "type": "uint112"},
                {"name": "reserve1", "type": "uint112"},
                {"name": "blockTimestampLast", "type": "uint32"}
            ],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token0",
            "outputs": [{"name": "", "type": "address"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "token1",
            "outputs": [{"name": "", "type": "address"}],
            "type": "function"
        }
    ]

    try:
        pool = w3.eth.contract(
            address=Web3.to_checksum_address(pool_address),
            abi=POOL_ABI
        )

        # Get reserves
        reserves = pool.functions.getReserves().call()
        print(f"Reserves: {reserves}")

        # Get tokens
        token0 = pool.functions.token0().call()
        token1 = pool.functions.token1().call()
        print(f"Token0: {token0}")
        print(f"Token1: {token1}")

        return True

    except Exception as e:
        print(f"ERROR: Pool contract test failed: {e}")
        return False

if __name__ == "__main__":
    pool_address = find_pool_address()

    if pool_address:
        if test_pool_contract(pool_address):
            print(f"\nSUCCESS: Pool address is {pool_address}")
            print(f"Update MAXX_ETH_POOL in standalone_config.py to: {pool_address}")
        else:
            print("ERROR: Pool contract is not working")
    else:
        print("ERROR: Could not find pool address")