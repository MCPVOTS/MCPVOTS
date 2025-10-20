#!/usr/bin/env python3
"""
Real DEX Integration Module for MAXX Token Trading
Implements actual DEX swapping functionality for Base chain
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound, ContractLogicError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.real_trading')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_dex_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealDEXIntegration:
    """
    Real DEX integration for MAXX token trading on Base chain
    """

    def __init__(self):
        self.logger = logger
        self.w3 = None
        self.router_address = None
        self.pool_address = None
        self.maxx_contract_address = None
        self.weth_address = None
        self.private_key = None
        self.account = None

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
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "reserveIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "reserveOut", "type": "uint256"}
                ],
                "name": "getAmountOut",
                "outputs": [
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
                ],
                "stateMutability": "pure",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenA", "type": "address"},
                    {"internalType": "address", "name": "tokenB", "type": "address"}
                ],
                "name": "getPair",
                "outputs": [
                    {"internalType": "address", "name": "pair", "type": "address"}
                ],
                "stateMutability": "view",
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
        Initialize the DEX integration with blockchain connection
        """
        try:
            self.logger.info("Initializing DEX integration...")

            # Get configuration from environment
            provider_url = os.getenv('PROVIDER_URL')
            chain_id = int(os.getenv('CHAIN_ID', '8453'))
            self.private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
            self.router_address = os.getenv('UNISWAP_V2_ROUTER')
            self.pool_address = os.getenv('MAXX_ETH_POOL')
            self.maxx_contract_address = os.getenv('MAXX_CONTRACT_ADDRESS')
            self.weth_address = os.getenv('WETH_ADDRESS')

            # Validate configuration
            if not all([provider_url, self.private_key, self.router_address,
                       self.pool_address, self.maxx_contract_address, self.weth_address]):
                missing = [name for name, value in [
                    ('PROVIDER_URL', provider_url),
                    ('ETHEREUM_PRIVATE_KEY', self.private_key),
                    ('UNISWAP_V2_ROUTER', self.router_address),
                    ('MAXX_ETH_POOL', self.pool_address),
                    ('MAXX_CONTRACT_ADDRESS', self.maxx_contract_address),
                    ('WETH_ADDRESS', self.weth_address)
                ] if not value]
                raise ValueError(f"Missing required configuration: {missing}")

            # Connect to blockchain
            self.w3 = Web3(Web3.HTTPProvider(provider_url))

            # Add middleware for Base chain
            if chain_id == 8453:  # Base
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Verify connection
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to blockchain")

            # Get chain ID
            connected_chain_id = self.w3.eth.chain_id
            if connected_chain_id != chain_id:
                raise ValueError(f"Chain ID mismatch: expected {chain_id}, got {connected_chain_id}")

            # Create account from private key
            self.account = self.w3.eth.account.from_key(self.private_key)

            # Initialize contracts
            self.router = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.router_address),
                abi=self.router_abi
            )

            self.pool = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.pool_address),
                abi=self.pool_abi
            )

            self.maxx_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.maxx_contract_address),
                abi=self.erc20_abi
            )

            self.weth_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.weth_address),
                abi=self.erc20_abi
            )

            self.logger.info(f"SUCCESS: DEX integration initialized")
            self.logger.info(f"Connected to chain ID: {connected_chain_id}")
            self.logger.info(f"Trading account: {self.account.address}")
            self.logger.info(f"Router: {self.router_address}")
            self.logger.info(f"Pool: {self.pool_address}")

            return True

        except Exception as e:
            self.logger.error(f"ERROR: Failed to initialize DEX integration: {e}")
            return False

    async def get_pool_reserves(self) -> Tuple[Decimal, Decimal]:
        """
        Get the current reserves from the MAXX/ETH pool
        """
        try:
            reserves = self.pool.functions.getReserves().call()
            token0 = self.pool.functions.token0().call()

            # Determine which reserve is MAXX and which is ETH
            if token0.lower() == self.maxx_contract_address.lower():
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
                self.router_address
            ).call()

            if current_allowance >= amount_wei:
                self.logger.info("MAXX spending already approved")
                return True

            # Approve spending
            tx_data = self.maxx_contract.functions.approve(
                self.router_address,
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': int(os.getenv('GAS_LIMIT', '300000')),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
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

    async def buy_maxx_with_eth(self, eth_amount: Decimal, slippage_tolerance: float = 0.5) -> Optional[str]:
        """
        Buy MAXX tokens with ETH
        """
        try:
            self.logger.info(f"Starting MAXX purchase with {eth_amount} ETH")

            # Convert ETH amount to wei
            eth_amount_wei = int(eth_amount * (10 ** 18))

            # Get expected output amount
            maxx_reserve, eth_reserve = await self.get_pool_reserves()

            # Calculate expected MAXX amount using Uniswap V2 formula
            # amountOut = amountIn * reserveOut / (reserveIn + amountIn)
            expected_maxx = eth_amount * maxx_reserve / (eth_reserve + eth_amount)

            # Apply slippage tolerance
            min_maxx = expected_maxx * (1 - slippage_tolerance / 100)

            # Get decimals for MAXX
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            min_maxx_wei = int(min_maxx * (10 ** maxx_decimals))

            # Prepare transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes

            tx_data = self.router.functions.swapExactETHForTokens(
                min_maxx_wei,
                [
                    Web3.to_checksum_address(self.weth_address),
                    Web3.to_checksum_address(self.maxx_contract_address)
                ],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'value': eth_amount_wei,
                'gas': int(os.getenv('GAS_LIMIT', '300000')),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
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

    async def sell_maxx_for_eth(self, maxx_amount: Decimal, slippage_tolerance: float = 0.5) -> Optional[str]:
        """
        Sell MAXX tokens for ETH
        """
        try:
            self.logger.info(f"Starting MAXX sale of {maxx_amount} MAXX")

            # First approve spending
            if not await self.approve_maxx_spending(maxx_amount):
                raise Exception("Failed to approve MAXX spending")

            # Convert MAXX amount to wei
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            maxx_amount_wei = int(maxx_amount * (10 ** maxx_decimals))

            # Get expected output amount
            maxx_reserve, eth_reserve = await self.get_pool_reserves()

            # Calculate expected ETH amount using Uniswap V2 formula
            # amountOut = amountIn * reserveOut / (reserveIn + amountIn)
            expected_eth = maxx_amount * eth_reserve / (maxx_reserve + maxx_amount)

            # Apply slippage tolerance
            min_eth = expected_eth * (1 - slippage_tolerance / 100)
            min_eth_wei = int(min_eth * (10 ** 18))

            # Prepare transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes

            tx_data = self.router.functions.swapExactTokensForETH(
                maxx_amount_wei,
                min_eth_wei,
                [
                    Web3.to_checksum_address(self.maxx_contract_address),
                    Web3.to_checksum_address(self.weth_address)
                ],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'gas': int(os.getenv('GAS_LIMIT', '300000')),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
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
                'transaction_index': receipt.transactionIndex
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
    Test the DEX integration
    """
    dex = RealDEXIntegration()

    if not await dex.initialize():
        print("Failed to initialize DEX integration")
        return

    # Test basic functionality
    try:
        eth_balance = await dex.get_eth_balance()
        maxx_balance = await dex.get_maxx_balance()
        price = await dex.get_token_price()

        print(f"ETH Balance: {eth_balance}")
        print(f"MAXX Balance: {maxx_balance}")
        print(f"MAXX Price: {price} ETH")

    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    asyncio.run(main())