#!/usr/bin/env python3
"""
Static DEX Trader for MAXX Token Trading
Uses static configuration - no environment variables

✅ WORKING SCRIPT - Uses Uniswap V2
✅ Uses standalone_config.py or config/real_trading_config.py
✅ V2 Router: 0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24
⚠️ Keep V2 configuration - DO NOT switch to V4
"""
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from web3 import Web3
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
    geth_poa_middleware = ExtraDataToPOAMiddleware
from web3.exceptions import TransactionNotFound, ContractLogicError

# Import static configuration
try:
    from config.real_trading_config import *
except ImportError:
    # Fallback to standalone config
    import standalone_config as config
    # Map the variables
    PROVIDER_URL = config.PROVIDER_URL
    CHAIN_ID = config.CHAIN_ID
    ETHEREUM_PRIVATE_KEY = config.ETHEREUM_PRIVATE_KEY
    MAXX_CONTRACT_ADDRESS = config.MAXX_CONTRACT_ADDRESS
    UNISWAP_V2_ROUTER = config.UNISWAP_V2_ROUTER
    UNISWAP_V2_FACTORY = config.UNISWAP_V2_FACTORY
    WETH_ADDRESS = config.WETH_ADDRESS
    MAXX_ETH_POOL = config.MAXX_ETH_POOL
    TRADING_MODE = config.TRADING_MODE
    SLIPPAGE_TOLERANCE = config.SLIPPAGE_TOLERANCE
    GAS_LIMIT = config.GAS_LIMIT
    GAS_PRICE_GWEI = config.GAS_PRICE_GWEI
    LOG_LEVEL = config.LOG_LEVEL
    TRANSACTION_LOG_FILE = config.TRANSACTION_LOG_FILE
    MAX_POSITION_SIZE_USD = config.MAX_POSITION_SIZE_USD
    MIN_LIQUIDITY_USD = config.MIN_LIQUIDITY_USD
    TEST_ETH_AMOUNT = config.TEST_ETH_AMOUNT
    TEST_SLIPPAGE = config.TEST_SLIPPAGE
    ENABLE_SAFETY_CHECKS = config.ENABLE_SAFETY_CHECKS
    REQUIRE_BALANCE_CHECK = config.REQUIRE_BALANCE_CHECK
    REQUIRE_LIQUIDITY_CHECK = config.REQUIRE_LIQUIDITY_CHECK
    MAX_GAS_PRICE_GWEI = config.MAX_GAS_PRICE_GWEI

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(TRANSACTION_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StaticDEXTrader:
    """
    Static DEX trader for MAXX token trading on Base chain
    All configuration is static - no environment variables
    """

    def __init__(self):
        self.logger = logger
        self.w3 = None
        self.account = None
        self.router = None
        self.pool = None
        self.maxx_contract = None
        self.weth_contract = None

        # Validate private key
        if ETHEREUM_PRIVATE_KEY == "your_private_key_here":
            raise ValueError("Please update ETHEREUM_PRIVATE_KEY in config/real_trading_config.py")

        # DEX Router ABI (Uniswap V2 compatible)
        self.router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountInMax", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapTokensForExactTokens",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForTokens",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactETHForTokens",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForETH",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        # ERC20 ABI
        self.erc20_abi = [
            {
                "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "spender", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

        # Pool ABI (Uniswap V2 Pair)
        self.pool_abi = [
            {
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"internalType": "uint112", "name": "reserve0", "type": "uint112"},
                    {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
                    {"internalType": "uint32", "name": "blockTimestampLast", "type": "uint32"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "token0",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "token1",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    async def initialize(self) -> bool:
        """
        Initialize the DEX trader with blockchain connection
        """
        try:
            self.logger.info("Initializing Static DEX Trader...")

            # Connect to blockchain
            self.w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

            # Add middleware for Base chain
            if CHAIN_ID == 8453:  # Base
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Verify connection
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to blockchain")

            # Get chain ID
            connected_chain_id = self.w3.eth.chain_id
            if connected_chain_id != CHAIN_ID:
                raise ValueError(f"Chain ID mismatch: expected {CHAIN_ID}, got {connected_chain_id}")

            # Create account from private key
            self.account = self.w3.eth.account.from_key(ETHEREUM_PRIVATE_KEY)

            # Initialize contracts
            self.router = self.w3.eth.contract(
                address=Web3.to_checksum_address(UNISWAP_V2_ROUTER),
                abi=self.router_abi
            )

            self.pool = self.w3.eth.contract(
                address=Web3.to_checksum_address(MAXX_ETH_POOL),
                abi=self.pool_abi
            )

            self.maxx_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS),
                abi=self.erc20_abi
            )

            self.weth_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(WETH_ADDRESS),
                abi=self.erc20_abi
            )

            self.logger.info(f"SUCCESS: Static DEX Trader initialized")
            self.logger.info(f"Connected to chain ID: {connected_chain_id}")
            self.logger.info(f"Trading account: {self.account.address}")
            self.logger.info(f"Router: {UNISWAP_V2_ROUTER}")
            self.logger.info(f"Pool: {MAXX_ETH_POOL}")

            return True

        except Exception as e:
            self.logger.error(f"ERROR: Failed to initialize Static DEX Trader: {e}")
            return False

    async def get_pool_reserves(self) -> Tuple[Decimal, Decimal]:
        """
        Get the current reserves from the MAXX/ETH pool
        """
        try:
            reserves = self.pool.functions.getReserves().call()
            token0 = self.pool.functions.token0().call()

            # Determine which reserve is MAXX and which is ETH
            if token0.lower() == MAXX_CONTRACT_ADDRESS.lower():
                maxx_reserve = Decimal(reserves[0])
                eth_reserve = Decimal(reserves[1])
            else:
                maxx_reserve = Decimal(reserves[1])
                eth_reserve = Decimal(reserves[0])

            # Get decimals
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            eth_decimals = self.weth_contract.functions.decimals().call()

            # Convert to proper decimal values
            maxx_reserve = maxx_reserve / (10 ** maxx_decimals)
            eth_reserve = eth_reserve / (10 ** eth_decimals)

            self.logger.info(f"Pool reserves - MAXX: {maxx_reserve}, ETH: {eth_reserve}")

            return maxx_reserve, eth_reserve

        except Exception as e:
            self.logger.error(f"ERROR: Failed to get pool reserves: {e}")
            raise

    async def get_token_price(self) -> Decimal:
        """
        Get the current price of MAXX in ETH
        """
        try:
            maxx_reserve, eth_reserve = await self.get_pool_reserves()

            if maxx_reserve == 0:
                raise ValueError("MAXX reserve is zero")

            price = eth_reserve / maxx_reserve
            self.logger.info(f"Current MAXX price: {price} ETH")

            return price

        except Exception as e:
            self.logger.error(f"ERROR: Failed to get token price: {e}")
            raise

    async def get_eth_balance(self) -> Decimal:
        """
        Get the ETH balance of the trading account
        """
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = Decimal(balance_wei) / Decimal(10**18)

            self.logger.info(f"ETH balance: {balance_eth} ETH")
            return balance_eth

        except Exception as e:
            self.logger.error(f"ERROR: Failed to get ETH balance: {e}")
            raise

    async def get_maxx_balance(self) -> Decimal:
        """
        Get the MAXX token balance of the trading account
        """
        try:
            balance_wei = self.maxx_contract.functions.balanceOf(self.account.address).call()
            decimals = self.maxx_contract.functions.decimals().call()
            balance = Decimal(balance_wei) / Decimal(10**decimals)

            self.logger.info(f"MAXX balance: {balance} MAXX")
            return balance

        except Exception as e:
            self.logger.error(f"ERROR: Failed to get MAXX balance: {e}")
            raise

    async def approve_maxx_spending(self, amount: Decimal) -> bool:
        """
        Approve the router to spend MAXX tokens
        """
        try:
            decimals = self.maxx_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))

            # Check current allowance
            current_allowance = self.maxx_contract.functions.allowance(
                self.account.address,
                UNISWAP_V2_ROUTER
            ).call()

            if current_allowance >= amount_wei:
                self.logger.info("MAXX spending already approved")
                return True

            # Approve spending
            tx_data = self.maxx_contract.functions.approve(
                UNISWAP_V2_ROUTER,
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': GAS_LIMIT,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                self.logger.info(f"SUCCESS: MAXX approval confirmed - TX: {tx_hash.hex()}")
                return True
            else:
                self.logger.error(f"ERROR: MAXX approval failed - TX: {tx_hash.hex()}")
                return False

        except Exception as e:
            self.logger.error(f"ERROR: Failed to approve MAXX spending: {e}")
            return False

    async def buy_maxx_with_eth(self, eth_amount: Decimal, slippage_tolerance: float = None) -> Optional[str]:
        """
        Buy MAXX tokens with ETH
        """
        try:
            if slippage_tolerance is None:
                slippage_tolerance = SLIPPAGE_TOLERANCE

            self.logger.info(f"Starting MAXX purchase with {eth_amount} ETH")

            # Safety checks
            if ENABLE_SAFETY_CHECKS:
                # Check balance
                if REQUIRE_BALANCE_CHECK:
                    current_balance = await self.get_eth_balance()
                    if current_balance < eth_amount:
                        raise ValueError(f"Insufficient ETH balance: {current_balance} < {eth_amount}")

                # Check gas price
                current_gas_price = self.w3.eth.gas_price / 10**9  # Convert to Gwei
                if current_gas_price > MAX_GAS_PRICE_GWEI:
                    raise ValueError(f"Gas price too high: {current_gas_price} Gwei > {MAX_GAS_PRICE_GWEI} Gwei")

            # Convert ETH amount to wei
            eth_amount_wei = int(eth_amount * (10 ** 18))

            # Get expected output amount
            maxx_reserve, eth_reserve = await self.get_pool_reserves()

            # Calculate expected MAXX amount using Uniswap V2 formula
            # Includes 0.3% fee
            expected_maxx = eth_amount * 0.997 * maxx_reserve / (eth_reserve + eth_amount * 0.997)

            # Apply slippage tolerance
            min_maxx = expected_maxx * (1 - slippage_tolerance / 100)

            # Get decimals for MAXX
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            min_maxx_wei = int(min_maxx * (10 ** maxx_decimals))

            # Optimize gas price for Base chain
            current_gas_price = self.w3.eth.gas_price
            # Use lower gas for Base chain (it's cheaper)
            optimal_gas_price = int(current_gas_price * 0.5) if current_gas_price > 10**9 else current_gas_price
            optimal_gas_price = max(optimal_gas_price, 10**8)  # Minimum 0.1 Gwei

            # Prepare transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes

            tx_data = self.router.functions.swapExactETHForTokens(
                min_maxx_wei,
                [
                    Web3.to_checksum_address(WETH_ADDRESS),
                    Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS)
                ],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'value': eth_amount_wei,
                'gas': GAS_LIMIT,
                'gasPrice': optimal_gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            self.logger.info(f"Buy transaction sent: {tx_hash.hex()}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                self.logger.info(f"SUCCESS: MAXX purchase confirmed - TX: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                self.logger.error(f"ERROR: MAXX purchase failed - TX: {tx_hash.hex()}")
                return None

        except Exception as e:
            self.logger.error(f"ERROR: Failed to buy MAXX: {e}")
            return None

    async def sell_maxx_for_eth(self, maxx_amount: Decimal, slippage_tolerance: float = None) -> Optional[str]:
        """
        Sell MAXX tokens for ETH
        """
        try:
            if slippage_tolerance is None:
                slippage_tolerance = SLIPPAGE_TOLERANCE

            self.logger.info(f"Starting MAXX sale of {maxx_amount} MAXX")

            # Safety checks
            if ENABLE_SAFETY_CHECKS:
                # Check balance
                if REQUIRE_BALANCE_CHECK:
                    current_balance = await self.get_maxx_balance()
                    if current_balance < maxx_amount:
                        raise ValueError(f"Insufficient MAXX balance: {current_balance} < {maxx_amount}")

                # Check gas price
                current_gas_price = self.w3.eth.gas_price / 10**9  # Convert to Gwei
                if current_gas_price > MAX_GAS_PRICE_GWEI:
                    raise ValueError(f"Gas price too high: {current_gas_price} Gwei > {MAX_GAS_PRICE_GWEI} Gwei")

            # First approve spending
            if not await self.approve_maxx_spending(maxx_amount):
                raise Exception("Failed to approve MAXX spending")

            # Convert MAXX amount to wei
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            maxx_amount_wei = int(maxx_amount * (10 ** maxx_decimals))

            # Get expected output amount
            maxx_reserve, eth_reserve = await self.get_pool_reserves()

            # Calculate expected ETH amount using Uniswap V2 formula
            # Includes 0.3% fee
            expected_eth = maxx_amount * 0.997 * eth_reserve / (maxx_reserve + maxx_amount * 0.997)

            # Apply slippage tolerance
            min_eth = expected_eth * (1 - slippage_tolerance / 100)
            min_eth_wei = int(min_eth * (10 ** 18))

            # Optimize gas price for Base chain
            current_gas_price = self.w3.eth.gas_price
            # Use lower gas for Base chain (it's cheaper)
            optimal_gas_price = int(current_gas_price * 0.5) if current_gas_price > 10**9 else current_gas_price
            optimal_gas_price = max(optimal_gas_price, 10**8)  # Minimum 0.1 Gwei

            # Prepare transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes

            tx_data = self.router.functions.swapExactTokensForETH(
                maxx_amount_wei,
                min_eth_wei,
                [
                    Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS),
                    Web3.to_checksum_address(WETH_ADDRESS)
                ],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'gas': GAS_LIMIT,
                'gasPrice': optimal_gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            self.logger.info(f"Sell transaction sent: {tx_hash.hex()}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                self.logger.info(f"SUCCESS: MAXX sale confirmed - TX: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                self.logger.error(f"ERROR: MAXX sale failed - TX: {tx_hash.hex()}")
                return None

        except Exception as e:
            self.logger.error(f"ERROR: Failed to sell MAXX: {e}")
            return None

    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get the status of a transaction
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)

            return {
                'tx_hash': tx_hash,
                'status': 'success' if receipt.status == 1 else 'failed',
                'gas_used': receipt.gasUsed,
                'block_number': receipt.blockNumber,
                'transaction_index': receipt.transaction_index
            }

        except TransactionNotFound:
            return {
                'tx_hash': tx_hash,
                'status': 'not_found',
                'error': 'Transaction not found'
            }
        except Exception as e:
            return {
                'tx_hash': tx_hash,
                'status': 'error',
                'error': str(e)
            }


async def main():
    """
    Test the static DEX trader
    """
    trader = StaticDEXTrader()

    if not await trader.initialize():
        print("Failed to initialize Static DEX Trader")
        return

    # Test basic functionality
    try:
        eth_balance = await trader.get_eth_balance()
        maxx_balance = await trader.get_maxx_balance()
        price = await trader.get_token_price()

        print(f"ETH Balance: {eth_balance}")
        print(f"MAXX Balance: {maxx_balance}")
        print(f"MAXX Price: {price} ETH")

    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    asyncio.run(main())