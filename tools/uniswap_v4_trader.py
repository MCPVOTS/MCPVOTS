#!/usr/bin/env python3
"""
Uniswap V4 Trading System for MAXX Token
Uses Universal Router on Base Chain
NO MORE V2 - PROPER V4 IMPLEMENTATION
"""

import asyncio
import time
from decimal import Decimal
from typing import Optional, Tuple
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account
import logging

# Import configuration
from standalone_config import (
    PROVIDER_URL,
    CHAIN_ID,
    ETHEREUM_PRIVATE_KEY,
    MAXX_CONTRACT_ADDRESS,
    WETH_ADDRESS,
    SLIPPAGE_TOLERANCE,
    GAS_LIMIT
)

# V4 Contract Addresses for Base Chain
UNIVERSAL_ROUTER_V4 = "0x6fF5693b99212Da76ad316178A184AB56D299b43"
POOL_MANAGER_V4 = "0x498581ff718922c3f8e6a244956af099b2652b2b"
PERMIT2_ADDRESS = "0x000000000022D473030F116dDEE9F6B43aC78BA3"
MAXX_ETH_POOL_ID = "0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148"

logger = logging.getLogger(__name__)

# Universal Router ABI (simplified for execute function)
UNIVERSAL_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "bytes", "name": "commands", "type": "bytes"},
            {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "execute",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# ERC20 ABI for token operations
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
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Permit2 ABI (simplified)
PERMIT2_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint160", "name": "amount", "type": "uint160"},
            {"internalType": "uint48", "name": "expiration", "type": "uint48"}
        ],
        "name": "approve",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# V4 Command Types (from Universal Router)
class Commands:
    V4_SWAP = 0x00

# V4 Action Types (from V4Router)
class Actions:
    SWAP_EXACT_IN_SINGLE = 0x00
    SWAP_EXACT_IN = 0x01
    SWAP_EXACT_OUT_SINGLE = 0x02
    SWAP_EXACT_OUT = 0x03
    SETTLE_ALL = 0x09
    TAKE_ALL = 0x0a

class UniswapV4Trader:
    """Uniswap V4 Trading implementation using Universal Router"""

    def __init__(self):
        # Connect to Base chain
        self.w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Base chain")

        # Setup account
        self.account = Account.from_key(ETHEREUM_PRIVATE_KEY)
        self.address = self.account.address

        # Setup contracts
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(UNIVERSAL_ROUTER_V4),
            abi=UNIVERSAL_ROUTER_ABI
        )

        self.maxx_token = self.w3.eth.contract(
            address=Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS),
            abi=ERC20_ABI
        )

        self.permit2 = self.w3.eth.contract(
            address=Web3.to_checksum_address(PERMIT2_ADDRESS),
            abi=PERMIT2_ABI
        )

        logger.info(f"V4 Trader initialized for address: {self.address}")
        logger.info(f"Universal Router: {UNIVERSAL_ROUTER_V4}")
        logger.info(f"Pool Manager: {POOL_MANAGER_V4}")

    async def get_balances(self) -> Tuple[Decimal, Decimal]:
        """Get ETH and MAXX balances"""
        try:
            eth_balance = self.w3.eth.get_balance(self.address)
            eth = Decimal(str(eth_balance)) / Decimal('1000000000000000000')

            maxx_balance = self.maxx_token.functions.balanceOf(self.address).call()
            maxx = Decimal(str(maxx_balance)) / Decimal('1000000000000000000')

            return eth, maxx
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            return Decimal('0'), Decimal('0')

    async def approve_permit2(self) -> bool:
        """Approve Permit2 to spend MAXX tokens"""
        try:
            # Check current allowance
            allowance = self.maxx_token.functions.allowance(
                self.address,
                PERMIT2_ADDRESS
            ).call()

            if allowance > 0:
                logger.info(f"Permit2 already approved: {allowance}")
                return True

            # Approve Permit2 for unlimited MAXX
            max_approval = 2**256 - 1

            tx = self.maxx_token.functions.approve(
                PERMIT2_ADDRESS,
                max_approval
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            logger.info(f"Permit2 approval tx: {tx_hash.hex()}")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] == 1:
                logger.info("✓ Permit2 approved successfully")
                return True
            else:
                logger.error("✗ Permit2 approval failed")
                return False

        except Exception as e:
            logger.error(f"Error approving Permit2: {e}")
            return False

    async def approve_universal_router_via_permit2(self) -> bool:
        """Approve Universal Router via Permit2"""
        try:
            # Approve Universal Router for a large amount (1 billion MAXX)
            amount = int(1e9 * 1e18)  # 1 billion MAXX
            expiration = int(time.time()) + (365 * 24 * 60 * 60)  # 1 year

            tx = self.permit2.functions.approve(
                MAXX_CONTRACT_ADDRESS,
                UNIVERSAL_ROUTER_V4,
                amount,
                expiration
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            logger.info(f"Universal Router approval via Permit2 tx: {tx_hash.hex()}")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] == 1:
                logger.info("✓ Universal Router approved via Permit2")
                return True
            else:
                logger.error("✗ Universal Router approval failed")
                return False

        except Exception as e:
            logger.error(f"Error approving Universal Router: {e}")
            return False

    async def buy_maxx_v4(self, eth_amount: Decimal) -> Optional[str]:
        """
        Buy MAXX using Uniswap V4 Universal Router

        Args:
            eth_amount: Amount of ETH to spend (in ETH, not Wei)

        Returns:
            Transaction hash if successful, None otherwise
        """
        try:
            logger.info(f"🔄 Buying MAXX with {eth_amount} ETH (V4)")

            eth_amount_wei = int(eth_amount * Decimal('1000000000000000000'))

            # Calculate minimum MAXX output (with slippage)
            # Estimate: ~$0.00447 per MAXX, ETH at ~$4000
            # So 1 ETH = ~894,900 MAXX
            estimated_maxx = int(float(eth_amount) * 894900 * 1e18)
            min_maxx_out = int(estimated_maxx * (1 - SLIPPAGE_TOLERANCE / 100))

            # Build V4 swap command
            # Command: V4_SWAP
            commands = bytes([Commands.V4_SWAP])

            # Actions: SWAP_EXACT_IN_SINGLE -> SETTLE_ALL -> TAKE_ALL
            actions = bytes([
                Actions.SWAP_EXACT_IN_SINGLE,
                Actions.SETTLE_ALL,
                Actions.TAKE_ALL
            ])

            # PoolKey struct for MAXX/ETH pool
            # currency0 = address(0) for native ETH
            # currency1 = MAXX_CONTRACT_ADDRESS
            # fee = 3000 (0.3%)
            # tickSpacing = 60
            # hooks = address(0)

            # Encode swap parameters
            # ExactInputSingleParams struct
            swap_params = self.w3.codec.encode(
                ['address', 'address', 'uint24', 'int24', 'address', 'bool', 'uint128', 'uint128', 'bytes'],
                [
                    '0x0000000000000000000000000000000000000000',  # currency0 (ETH)
                    MAXX_CONTRACT_ADDRESS,  # currency1 (MAXX)
                    3000,  # fee (0.3%)
                    60,  # tickSpacing
                    '0x0000000000000000000000000000000000000000',  # hooks
                    True,  # zeroForOne (ETH -> MAXX)
                    eth_amount_wei,  # amountIn
                    min_maxx_out,  # amountOutMinimum
                    b''  # hookData
                ]
            )

            # SETTLE_ALL params
            settle_params = self.w3.codec.encode(
                ['address', 'uint256'],
                ['0x0000000000000000000000000000000000000000', eth_amount_wei]
            )

            # TAKE_ALL params
            take_params = self.w3.codec.encode(
                ['address', 'uint256'],
                [MAXX_CONTRACT_ADDRESS, min_maxx_out]
            )

            # Combine into params array
            params = [swap_params, settle_params, take_params]

            # Encode actions + params
            inputs = [self.w3.codec.encode(['bytes', 'bytes[]'], [actions, params])]

            # Deadline (2 minutes from now)
            deadline = int(time.time()) + 120

            # Build transaction
            tx = self.router.functions.execute(
                commands,
                inputs,
                deadline
            ).build_transaction({
                'from': self.address,
                'value': eth_amount_wei,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': CHAIN_ID
            })

            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            logger.info(f"Buy tx sent: {tx_hash.hex()}")            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] == 1:
                logger.info(f"✓ Buy successful! TX: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"✗ Buy failed! TX: {tx_hash.hex()}")
                return None

        except Exception as e:
            logger.error(f"Error buying MAXX (V4): {e}")
            return None

    async def sell_maxx_v4(self, maxx_amount: Decimal) -> Optional[str]:
        """
        Sell MAXX using Uniswap V4 Universal Router

        Args:
            maxx_amount: Amount of MAXX to sell (in MAXX, not Wei)

        Returns:
            Transaction hash if successful, None otherwise
        """
        try:
            logger.info(f"🔄 Selling {maxx_amount} MAXX (V4)")

            # Ensure approvals are in place
            if not await self.approve_permit2():
                logger.error("Failed to approve Permit2")
                return None

            if not await self.approve_universal_router_via_permit2():
                logger.error("Failed to approve Universal Router")
                return None

            maxx_amount_wei = int(maxx_amount * Decimal('1000000000000000000'))

            # Calculate minimum ETH output (with slippage)
            estimated_eth = int(float(maxx_amount) / 894900 * 1e18)
            min_eth_out = int(estimated_eth * (1 - SLIPPAGE_TOLERANCE / 100))

            # Build V4 swap command
            commands = bytes([Commands.V4_SWAP])

            # Actions: SWAP_EXACT_IN_SINGLE -> SETTLE_ALL -> TAKE_ALL
            actions = bytes([
                Actions.SWAP_EXACT_IN_SINGLE,
                Actions.SETTLE_ALL,
                Actions.TAKE_ALL
            ])

            # Encode swap parameters (MAXX -> ETH, so zeroForOne = False)
            swap_params = self.w3.codec.encode(
                ['address', 'address', 'uint24', 'int24', 'address', 'bool', 'uint128', 'uint128', 'bytes'],
                [
                    '0x0000000000000000000000000000000000000000',  # currency0 (ETH)
                    MAXX_CONTRACT_ADDRESS,  # currency1 (MAXX)
                    3000,  # fee (0.3%)
                    60,  # tickSpacing
                    '0x0000000000000000000000000000000000000000',  # hooks
                    False,  # zeroForOne (MAXX -> ETH)
                    maxx_amount_wei,  # amountIn
                    min_eth_out,  # amountOutMinimum
                    b''  # hookData
                ]
            )

            # SETTLE_ALL params
            settle_params = self.w3.codec.encode(
                ['address', 'uint256'],
                [MAXX_CONTRACT_ADDRESS, maxx_amount_wei]
            )

            # TAKE_ALL params
            take_params = self.w3.codec.encode(
                ['address', 'uint256'],
                ['0x0000000000000000000000000000000000000000', min_eth_out]
            )

            # Combine into params array
            params = [swap_params, settle_params, take_params]

            # Encode actions + params
            inputs = [self.w3.codec.encode(['bytes', 'bytes[]'], [actions, params])]

            # Deadline
            deadline = int(time.time()) + 120

            # Build transaction
            tx = self.router.functions.execute(
                commands,
                inputs,
                deadline
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': CHAIN_ID
            })

            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            logger.info(f"Sell tx sent: {tx_hash.hex()}")            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt['status'] == 1:
                logger.info(f"✓ Sell successful! TX: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                logger.error(f"✗ Sell failed! TX: {tx_hash.hex()}")
                return None

        except Exception as e:
            logger.error(f"Error selling MAXX (V4): {e}")
            return None

# Test function
async def test_v4_trader():
    """Test the V4 trader"""
    logging.basicConfig(level=logging.INFO)

    trader = UniswapV4Trader()

    print("="*60)
    print("UNISWAP V4 TRADER TEST")
    print("="*60)

    # Get balances
    eth, maxx = await trader.get_balances()
    print(f"\nCurrent Balances:")
    print(f"  ETH: {eth:.6f}")
    print(f"  MAXX: {maxx:.2f}")

    # Test buying $1 worth of MAXX
    test_amount = Decimal('0.00025')  # ~$1 at $4000/ETH
    print(f"\nTesting buy of {test_amount} ETH worth of MAXX...")

    tx_hash = await trader.buy_maxx_v4(test_amount)

    if tx_hash:
        print(f"✓ Test buy successful: {tx_hash}")
    else:
        print("✗ Test buy failed")

if __name__ == "__main__":
    asyncio.run(test_v4_trader())
