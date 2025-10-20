"""
Enhanced Base blockchain utilities for MAXX Ecosystem
Provides Base-specific blockchain interactions and utilities with real API integrations
"""
import asyncio
import time
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from decimal import Decimal
import json

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.exceptions import Web3Exception, ContractLogicError

from core.config import get_app_config
from core.logging import get_logger, log_performance
from core.network import get_network_manager
from core.analytics import get_analytics_manager


@dataclass
class TokenInfo:
    """Token information structure"""
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: int
    chain: str
    price_usd: Optional[float] = None
    holders_count: Optional[int] = None


@dataclass
class TransactionInfo:
    """Transaction information structure"""
    hash: str
    from_address: str
    to_address: str
    value: int
    gas_used: int
    gas_price: int
    block_number: int
    timestamp: int
    status: str
    token_symbol: Optional[str] = None


@dataclass
class NetworkStats:
    """Network statistics"""
    block_height: int
    gas_price: int
    network_utilization: float
    tps: float
    synced: bool
    chain_id: int


class BaseBlockchainUtils:
    """
    Enhanced utilities for interacting with the Base blockchain
    Real API integrations with proper error handling and caching
    """

    # Standard ERC20 ABI for token interactions
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

    def __init__(self, provider_url: Optional[str] = None, api_key: Optional[str] = None):
        self.config = get_app_config()
        self.logger = get_logger(self.__class__.__name__)
        self.network_manager = None
        self.analytics_manager = None

        # Blockchain configuration
        self.provider_url = provider_url or self.config.blockchain.rpc_url
        self.api_key = api_key or os.getenv('BASESCAN_API_KEY')
        self.block_explorer_url = "https://basescan.org"
        self.chain_id = 8453  # Base mainnet

        # Web3 instance
        self._w3: Optional[AsyncWeb3] = None

        # Cache for frequently accessed data
        self._token_cache: Dict[str, TokenInfo] = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_update = 0

    async def initialize(self):
        """Initialize the blockchain utilities"""
        self.network_manager = await get_network_manager()
        self.analytics_manager = await get_analytics_manager()

        # Initialize Web3 connection
        await self._get_w3()

        self.logger.info("Base blockchain utilities initialized")

    async def _get_w3(self) -> AsyncWeb3:
        """Get or create Web3 instance"""
        if self._w3 is None:
            self._w3 = AsyncWeb3(AsyncHTTPProvider(self.provider_url))

            # Test connection
            try:
                chain_id = await self._w3.eth.chain_id
                self.logger.info(f"Connected to Base chain (ID: {chain_id})")
            except Exception as e:
                self.logger.error(f"Failed to connect to Base chain: {e}")
                raise

        return self._w3

    @log_performance("blockchain.get_token_balance")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_token_balance(self, token_address: str, wallet_address: str) -> int:
        """
        Get token balance for a specific wallet on Base using async web3
        """
        self.logger.debug(f"Querying balance for token {token_address} at wallet {wallet_address}")

        try:
            w3 = await self._get_w3()

            # Validate addresses
            if not w3.is_address(token_address) or not w3.is_address(wallet_address):
                raise ValueError("Invalid token or wallet address")

            # Create contract instance
            contract = w3.eth.contract(address=token_address, abi=self.ERC20_ABI)

            # Call balanceOf function asynchronously
            balance = await contract.functions.balanceOf(wallet_address).call()

            # Record metrics
            await self.analytics_manager.record_metric(
                "token_balance_query",
                1,
                tags={"token": token_address, "success": "true"}
            )

            return int(balance)

        except Web3Exception as e:
            self.logger.error(f"Web3 error getting token balance: {e}")
            await self.analytics_manager.record_metric(
                "token_balance_query",
                1,
                tags={"token": token_address, "success": "false"}
            )
            raise
        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            await self.analytics_manager.record_metric(
                "token_balance_query",
                1,
                tags={"token": token_address, "success": "false"}
            )
            return 0

    @log_performance("blockchain.get_gas_price")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_gas_price(self) -> int:
        """
        Get the current gas price on Base
        """
        try:
            w3 = await self._get_w3()
            gas_price = await w3.eth.gas_price

            await self.analytics_manager.record_metric(
                "gas_price_query",
                1,
                tags={"success": "true"}
            )

            return gas_price

        except Web3Exception as e:
            self.logger.error(f"Web3 error getting gas price: {e}")
            await self.analytics_manager.record_metric(
                "gas_price_query",
                1,
                tags={"success": "false"}
            )
            raise
        except Exception as e:
            self.logger.error(f"Error getting gas price: {e}")
            # Return a default low gas price for Base chain
            return AsyncWeb3.to_wei(0.1, 'gwei')  # 0.1 gwei in wei

    @log_performance("blockchain.check_transaction")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def check_transaction_status(self, tx_hash: str) -> str:
        """
        Check the status of a transaction on Base
        """
        self.logger.debug(f"Checking transaction status for {tx_hash}")

        try:
            w3 = await self._get_w3()

            # Get transaction receipt asynchronously
            receipt = await w3.eth.get_transaction_receipt(tx_hash)

            if receipt is None:
                status = "pending"
            elif receipt['status'] == 0:
                status = "failed"
            elif receipt['status'] == 1:
                status = "confirmed"
            else:
                status = "unknown"

            await self.analytics_manager.record_metric(
                "transaction_status_check",
                1,
                tags={"status": status, "success": "true"}
            )

            return status

        except Web3Exception as e:
            self.logger.warning(f"Web3 receipt not available yet for {tx_hash}: {e}")
            # Fallback to BaseScan
        except Exception as e:
            self.logger.error(f"Web3 error checking transaction status: {e}")

        # Fallback to BaseScan if Web3 fails
        return await self._check_transaction_via_basescan(tx_hash)

    async def _check_transaction_via_basescan(self, tx_hash: str) -> str:
        """Check transaction status via BaseScan API"""
        if not self.api_key:
            self.logger.warning("BaseScan API key not available")
            return "unknown"

        try:
            http_client = self.network_manager.get_http_client("https://api.basescan.org")

            params = {
                'module': 'transaction',
                'action': 'gettxreceiptstatus',
                'txhash': tx_hash,
                'apikey': self.api_key
            }

            response = await http_client.get('/api', params=params)

            if response.success and response.data.get('status') == '1':
                result = response.data.get('result', {})
                if isinstance(result, dict):
                    status = result.get('status', '0')
                    return "confirmed" if status == '1' else "failed"

            await self.analytics_manager.record_metric(
                "transaction_status_check",
                1,
                tags={"method": "basescan", "success": "false"}
            )

        except Exception as e:
            self.logger.error(f"Error checking transaction status via BaseScan: {e}")

        return "unknown"

    @log_performance("blockchain.get_token_metadata")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_token_metadata(self, token_address: str) -> TokenInfo:
        """
        Get comprehensive token metadata from multiple sources
        """
        self.logger.debug(f"Fetching token metadata for {token_address}")

        # Check cache first
        if token_address in self._token_cache:
            cache_time = self._token_cache[token_address].timestamp if hasattr(self._token_cache[token_address], 'timestamp') else 0
            if time.time() - cache_time < self._cache_ttl:
                return self._token_cache[token_address]

        try:
            # Validate address
            w3 = await self._get_w3()
            if not w3.is_address(token_address):
                raise ValueError("Invalid token address")

            # Try BaseScan first for comprehensive data
            token_info = await self._get_token_from_basescan(token_address)

            if not token_info:
                # Fallback to Web3 direct contract calls
                token_info = await self._get_token_from_web3(token_address)

            if token_info:
                # Cache the result
                self._token_cache[token_address] = token_info
                self._last_cache_update = time.time()

                await self.analytics_manager.record_metric(
                    "token_metadata_query",
                    1,
                    tags={"token": token_address, "success": "true"}
                )

                return token_info

        except Exception as e:
            self.logger.error(f"Error getting token metadata: {e}")
            await self.analytics_manager.record_metric(
                "token_metadata_query",
                1,
                tags={"token": token_address, "success": "false"}
            )

        # Return minimal info if all methods fail
        return TokenInfo(
            address=token_address,
            name="Unknown",
            symbol="UNKNOWN",
            decimals=18,
            total_supply=0,
            chain="Base"
        )

    async def _get_token_from_basescan(self, token_address: str) -> Optional[TokenInfo]:
        """Get token info from BaseScan API"""
        if not self.api_key:
            return None

        try:
            http_client = self.network_manager.get_http_client("https://api.basescan.org")

            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': token_address,
                'apikey': self.api_key
            }

            response = await http_client.get('/api', params=params)

            if response.success and response.data.get('status') == '1':
                result = response.data.get('result', {})
                token_info = result[0] if isinstance(result, list) and result else result

                return TokenInfo(
                    address=token_address,
                    name=token_info.get('tokenName', 'Unknown'),
                    symbol=token_info.get('tokenSymbol', 'UNKNOWN'),
                    decimals=int(token_info.get('tokenDecimal', 18)),
                    total_supply=int(token_info.get('totalSupply', '0')),
                    chain="Base"
                )

        except Exception as e:
            self.logger.warning(f"BaseScan token query failed: {e}")

        return None

    async def _get_token_from_web3(self, token_address: str) -> Optional[TokenInfo]:
        """Get token info from direct Web3 contract calls"""
        try:
            w3 = await self._get_w3()
            contract = w3.eth.contract(address=token_address, abi=self.ERC20_ABI)

            name, symbol, decimals, total_supply = await asyncio.gather(
                contract.functions.name().call(),
                contract.functions.symbol().call(),
                contract.functions.decimals().call(),
                contract.functions.totalSupply().call()
            )

            return TokenInfo(
                address=token_address,
                name=name,
                symbol=symbol,
                decimals=int(decimals),
                total_supply=int(total_supply),
                chain="Base"
            )

        except Exception as e:
            self.logger.warning(f"Web3 token query failed: {e}")

        return None

    @log_performance("blockchain.get_holders_count")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_holders_count(self, token_address: str, max_pages: int = 10) -> int:
        """
        Get holder count from BaseScan API with pagination
        """
        self.logger.debug(f"Fetching holders count for {token_address}")

        if not self.api_key:
            self.logger.warning("BaseScan API key not available")
            return 0

        try:
            http_client = self.network_manager.get_http_client("https://api.basescan.org")

            total_holders = 0
            page = 1

            while page <= max_pages:
                params = {
                    'module': 'token',
                    'action': 'tokenholderlist',
                    'contractaddress': token_address,
                    'page': page,
                    'offset': 1000,
                    'apikey': self.api_key
                }

                response = await http_client.get('/api', params=params)

                if not response.success or response.data.get('status') != '1':
                    break

                result = response.data.get('result', [])
                if not result:
                    break

                total_holders += len(result)
                page += 1

                # If less than offset returned, we've reached the end
                if len(result) < 1000:
                    break

                # Rate limiting
                await asyncio.sleep(0.2)

            await self.analytics_manager.record_metric(
                "holders_count_query",
                1,
                tags={"token": token_address, "holders": total_holders}
            )

            return total_holders

        except Exception as e:
            self.logger.error(f"Error getting holders count: {e}")
            return 0

    @log_performance("blockchain.get_token_transfers")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_token_transfers(
        self,
        token_address: str,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
        limit: int = 1000
    ) -> List[TransactionInfo]:
        """
        Get token transfer events from BaseScan API
        """
        self.logger.debug(f"Fetching transfers for {token_address} (limit={limit})")

        if not self.api_key:
            self.logger.warning("BaseScan API key not available")
            return []

        try:
            http_client = self.network_manager.get_http_client("https://api.basescan.org")

            all_transfers = []
            page = 1
            startblock = from_block or 0
            endblock = to_block or 99999999

            while len(all_transfers) < limit:
                params = {
                    'module': 'account',
                    'action': 'tokentx',
                    'contractaddress': token_address,
                    'startblock': startblock,
                    'endblock': endblock,
                    'page': page,
                    'offset': min(10000, limit - len(all_transfers)),
                    'sort': 'desc',
                    'apikey': self.api_key
                }

                response = await http_client.get('/api', params=params)

                if not response.success or response.data.get('status') != '1':
                    break

                result = response.data.get('result', [])
                if not result:
                    break

                batch_transfers = []
                for tx in result:
                    transfer_info = TransactionInfo(
                        hash=tx.get('hash', ''),
                        from_address=tx.get('from', ''),
                        to_address=tx.get('to', ''),
                        value=int(tx.get('value', '0')),
                        gas_used=int(tx.get('gasUsed', 0)),
                        gas_price=int(tx.get('gasPrice', 0)),
                        block_number=int(tx.get('blockNumber', 0)),
                        timestamp=int(tx.get('timeStamp', 0)),
                        status="confirmed",  # BaseScan only returns confirmed transactions
                        token_symbol=tx.get('tokenSymbol', '')
                    )
                    batch_transfers.append(transfer_info)

                all_transfers.extend(batch_transfers)

                if len(result) < 10000 or len(all_transfers) >= limit:
                    break

                page += 1
                await asyncio.sleep(0.2)  # Rate limiting

            await self.analytics_manager.record_metric(
                "token_transfers_query",
                1,
                tags={"token": token_address, "transfers": len(all_transfers)}
            )

            return all_transfers[:limit]

        except Exception as e:
            self.logger.error(f"Error getting token transfers: {e}")
            return []

    @log_performance("blockchain.get_token_price")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_token_price_usd(self, token_address: str) -> float:
        """
        Get token price in USD from DexScreener API
        """
        self.logger.debug(f"Fetching USD price for {token_address}")

        try:
            # Primary: DexScreener API
            http_client = self.network_manager.get_http_client("https://api.dexscreener.com")

            response = await http_client.get(f'/latest/dex/tokens/{token_address}')

            if response.success and response.data.get('pairs'):
                # Find the pair with the highest liquidity
                pairs = response.data['pairs']
                sorted_pairs = sorted(
                    pairs,
                    key=lambda x: float(x.get('liquidity', {}).get('usd', 0) or 0),
                    reverse=True
                )

                if sorted_pairs:
                    top_pair = sorted_pairs[0]
                    price_usd = top_pair.get('priceUsd')
                    if price_usd:
                        price = float(price_usd)

                        await self.analytics_manager.record_metric(
                            "token_price_query",
                            1,
                            tags={"token": token_address, "success": "true"}
                        )

                        return price

        except Exception as e:
            self.logger.warning(f"DexScreener price fetch failed: {e}")

        await self.analytics_manager.record_metric(
            "token_price_query",
            1,
            tags={"token": token_address, "success": "false"}
        )

        return 0.0

    @log_performance("blockchain.get_network_stats")
    async def get_network_stats(self) -> NetworkStats:
        """
        Get comprehensive network statistics for Base
        """
        try:
            w3 = await self._get_w3()

            # Get network data concurrently
            block_height, gas_price, syncing = await asyncio.gather(
                w3.eth.block_number,
                w3.eth.gas_price,
                w3.eth.syncing
            )

            is_synced = syncing is False

            # Calculate estimated TPS (simplified)
            # In production, this would use historical block data
            tps = 15.0  # Base average TPS

            # Network utilization (simplified calculation)
            # In production, this would use gas limit usage
            network_utilization = min(0.8, gas_price / 1000000000)  # Convert to gwei and normalize

            stats = NetworkStats(
                block_height=block_height,
                gas_price=gas_price,
                network_utilization=network_utilization,
                tps=tps,
                synced=is_synced,
                chain_id=self.chain_id
            )

            await self.analytics_manager.record_metric(
                "network_stats_query",
                1,
                tags={"synced": str(is_synced)}
            )

            return stats

        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")

            # Return default stats
            return NetworkStats(
                block_height=0,
                gas_price=100000000,  # 0.1 gwei
                network_utilization=0.1,
                tps=0.0,
                synced=False,
                chain_id=self.chain_id
            )

    async def get_contract_events(
        self,
        contract_address: str,
        event_name: str,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get contract events using Web3 logs
        """
        try:
            w3 = await self._get_w3()

            # This would require the contract ABI
            # For now, return empty list
            # In production, implement proper event filtering

            self.logger.warning("Contract event fetching not fully implemented")
            return []

        except Exception as e:
            self.logger.error(f"Error getting contract events: {e}")
            return []

    async def validate_address(self, address: str) -> bool:
        """
        Validate if an address is a proper Ethereum address
        """
        try:
            w3 = await self._get_w3()
            return w3.is_address(address)
        except Exception:
            return False

    async def get_block_timestamp(self, block_number: int) -> int:
        """
        Get the timestamp of a specific block
        """
        try:
            w3 = await self._get_w3()
            block = await w3.eth.get_block(block_number)
            return block['timestamp']
        except Exception as e:
            self.logger.error(f"Error getting block timestamp: {e}")
            return int(time.time())

    async def close(self):
        """Close blockchain utilities"""
        if self._w3:
            await self._w3.provider.disconnect()
            self._w3 = None

        self.logger.info("Base blockchain utilities closed")


# Global blockchain utils instance
_blockchain_utils: Optional[BaseBlockchainUtils] = None


async def get_blockchain_utils() -> BaseBlockchainUtils:
    """Get global blockchain utils instance"""
    global _blockchain_utils

    if _blockchain_utils is None:
        _blockchain_utils = BaseBlockchainUtils()
        await _blockchain_utils.initialize()

    return _blockchain_utils


async def close_blockchain_utils():
    """Close global blockchain utils"""
    global _blockchain_utils

    if _blockchain_utils:
        await _blockchain_utils.close()
        _blockchain_utils = None


if __name__ == "__main__":
    import asyncio

    async def main():
        utils = await get_blockchain_utils()

        # Test network stats
        stats = await utils.get_network_stats()
        print(f"Network stats: block={stats.block_height}, synced={stats.synced}")

        # Test gas price
        gas_price = await utils.get_gas_price()
        print(f"Gas price: {gas_price} wei")

        await close_blockchain_utils()

    asyncio.run(main())
