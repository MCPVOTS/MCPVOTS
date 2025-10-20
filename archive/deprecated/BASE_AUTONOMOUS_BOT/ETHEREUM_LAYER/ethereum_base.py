"""
Base Ethereum implementation for the autonomous bot system.
"""
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from web3 import Web3
import uuid
import time


class TransactionStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REPLACED = "replaced"


class EthereumBase(ABC):
    """
    Abstract base class for Ethereum operations.
    """
    
    def __init__(self, provider_url: str, chain_id: int, account_private_key: Optional[str] = None):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.chain_id = chain_id
        self.account = None
        self.nonce = None
        
        if account_private_key:
            self.account = self.w3.eth.account.from_key(account_private_key)
            self.address = self.account.address
        else:
            self.address = None
    
    def is_connected(self) -> bool:
        """
        Check if the Ethereum provider is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.w3.is_connected()
    
    async def get_balance(self, address: Optional[str] = None) -> int:
        """
        Get the balance of an address in wei.
        
        Args:
            address: Address to check balance for. If None, uses the bot's address.
            
        Returns:
            Balance in wei
        """
        target_address = address or self.address
        if not target_address:
            raise ValueError("No address provided and no default address set")
        
        return self.w3.eth.get_balance(target_address)
    
    async def get_nonce(self, address: Optional[str] = None) -> int:
        """
        Get the transaction count (nonce) for an address.
        
        Args:
            address: Address to get nonce for. If None, uses the bot's address.
            
        Returns:
            Transaction count (nonce)
        """
        target_address = address or self.address
        if not target_address:
            raise ValueError("No address provided and no default address set")
        
        return self.w3.eth.get_transaction_count(target_address)
    
    @abstractmethod
    async def send_transaction(self, to: str, value: int, data: str = "0x", gas_limit: Optional[int] = None, 
                              gas_price: Optional[int] = None, max_fee_per_gas: Optional[int] = None, 
                              max_priority_fee_per_gas: Optional[int] = None) -> str:
        """
        Send a transaction to the Ethereum network.
        
        Args:
            to: Recipient address
            value: Amount to send in wei
            data: Transaction data
            gas_limit: Gas limit for the transaction
            gas_price: Gas price for legacy transactions (in wei)
            max_fee_per_gas: Max fee per gas for EIP-1559 transactions (in wei)
            max_priority_fee_per_gas: Max priority fee per gas for EIP-1559 transactions (in wei)
            
        Returns:
            Transaction hash
        """
        pass
    
    @abstractmethod
    async def deploy_contract(self, abi: List[Dict], bytecode: str, constructor_args: List[Any] = None) -> str:
        """
        Deploy a smart contract to the Ethereum network.
        
        Args:
            abi: Contract ABI
            bytecode: Contract bytecode
            constructor_args: Arguments for contract constructor
            
        Returns:
            Contract address
        """
        pass
    
    @abstractmethod
    async def call_contract_function(self, contract_address: str, abi: List[Dict], function_name: str, args: List[Any] = None) -> Any:
        """
        Call a contract function.
        
        Args:
            contract_address: Address of the contract
            abi: Contract ABI
            function_name: Name of the function to call
            args: Arguments for the function
            
        Returns:
            Function return value
        """
        pass
    
    async def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """
        Estimate the gas required for a transaction.
        
        Args:
            transaction: Transaction parameters
            
        Returns:
            Estimated gas amount
        """
        return self.w3.eth.estimate_gas(transaction)
    
    async def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Wait for a transaction to be mined.
        
        Args:
            tx_hash: Hash of the transaction to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            Transaction receipt
        """
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    
    async def get_block(self, block_identifier: Any) -> Dict[str, Any]:
        """
        Get block information.
        
        Args:
            block_identifier: Block number or hash
            
        Returns:
            Block information
        """
        return self.w3.eth.get_block(block_identifier)


class ContractInteractor:
    """
    Interacts with Ethereum smart contracts.
    """
    
    def __init__(self, eth_base: EthereumBase):
        self.eth_base = eth_base
        self.contracts = {}
    
    def add_contract(self, name: str, address: str, abi: List[Dict]):
        """
        Add a contract to the interactor.
        
        Args:
            name: Name to identify the contract
            address: Contract address
            abi: Contract ABI
        """
        contract = self.eth_base.w3.eth.contract(address=address, abi=abi)
        self.contracts[name] = contract
    
    async def call_function(self, contract_name: str, function_name: str, *args) -> Any:
        """
        Call a function on a registered contract.
        
        Args:
            contract_name: Name of the registered contract
            function_name: Function to call
            *args: Function arguments
            
        Returns:
            Function result
        """
        if contract_name not in self.contracts:
            raise ValueError(f"Contract {contract_name} not registered")
        
        contract = self.contracts[contract_name]
        func = getattr(contract.functions, function_name)
        return await func(*args).call()
    
    async def transact_function(self, contract_name: str, function_name: str, *args, value: int = 0, 
                               gas_limit: Optional[int] = None, gas_price: Optional[int] = None,
                               max_fee_per_gas: Optional[int] = None, max_priority_fee_per_gas: Optional[int] = None) -> str:
        """
        Execute a transaction on a registered contract.
        
        Args:
            contract_name: Name of the registered contract
            function_name: Function to call
            *args: Function arguments
            value: Amount of wei to send with transaction
            gas_limit: Gas limit for the transaction
            gas_price: Gas price for legacy transactions (in wei)
            max_fee_per_gas: Max fee per gas for EIP-1559 transactions (in wei)
            max_priority_fee_per_gas: Max priority fee per gas for EIP-1559 transactions (in wei)
            
        Returns:
            Transaction hash
        """
        if contract_name not in self.contracts:
            raise ValueError(f"Contract {contract_name} not registered")
        
        contract = self.contracts[contract_name]
        func = getattr(contract.functions, function_name)
        
        # Build transaction
        transaction = {
            'to': contract.address,
            'from': self.eth_base.address,
            'value': value,
            'chainId': self.eth_base.chain_id,
            'nonce': await self.eth_base.get_nonce(),
        }
        
        # Add gas price or EIP-1559 parameters based on provided arguments
        if max_fee_per_gas is not None and max_priority_fee_per_gas is not None:
            # EIP-1559 transaction
            transaction['type'] = 2  # EIP-1559 transaction type
            transaction['maxFeePerGas'] = max_fee_per_gas
            transaction['maxPriorityFeePerGas'] = max_priority_fee_per_gas
        elif gas_price is not None:
            # Legacy transaction
            transaction['gasPrice'] = gas_price
        else:
            # Use eth_feeHistory and eth_gasPrice to get appropriate values
            import logging
            logger = logging.getLogger(__name__)
            try:
                # Try to get fee data for EIP-1559
                fee_history = self.eth_base.w3.eth.fee_history(10, 'latest', [50])
                if fee_history and len(fee_history['baseFeePerGas']) > 0:
                    base_fee = fee_history['baseFeePerGas'][-1]
                    # Set max fees based on current base fee
                    transaction['type'] = 2
                    transaction['maxFeePerGas'] = base_fee * 2  # 2x base fee
                    transaction['maxPriorityFeePerGas'] = self.eth_base.w3.to_wei(1.5, 'gwei')  # 1.5 gwei priority fee
                else:
                    # Fallback to gas price
                    transaction['gasPrice'] = self.eth_base.w3.eth.gas_price
            except Exception as e:
                logger.warning(f"Could not fetch fee history, using default gas price: {e}")
                transaction['gasPrice'] = self.eth_base.w3.eth.gas_price

        # Estimate gas if not provided
        if gas_limit is None:
            try:
                estimated_gas = await func(*args).estimate_gas(transaction)
                transaction['gas'] = int(estimated_gas * 1.2)  # Add 20% buffer
            except Exception as e:
                # If gas estimation fails, use a default value
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Gas estimation failed, using default gas limit: {e}")
                transaction['gas'] = 200000  # Default gas limit
        else:
            transaction['gas'] = gas_limit
        
        # Build transaction data
        transaction['data'] = func(*args).build_transaction(transaction)['data']
        
        # Sign transaction
        try:
            signed_txn = self.eth_base.w3.eth.account.sign_transaction(transaction, self.eth_base.account.key)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error signing transaction: {e}")
            raise
        
        # Send transaction
        tx_hash = self.eth_base.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()


class TransactionManager:
    """
    Manages Ethereum transactions.
    """
    
    def __init__(self, eth_base: EthereumBase):
        self.eth_base = eth_base
        self.pending_transactions = {}
        self.transaction_history = {}
    
    async def submit_transaction(self, tx_data: Dict[str, Any], tx_id: Optional[str] = None) -> str:
        """
        Submit a transaction for processing.
        
        Args:
            tx_data: Transaction data
            tx_id: Optional transaction ID. If not provided, one will be generated.
            
        Returns:
            Transaction ID
        """
        transaction_id = tx_id or str(uuid.uuid4())
        
        # Record the transaction as pending
        self.pending_transactions[transaction_id] = {
            'data': tx_data,
            'status': TransactionStatus.PENDING,
            'submitted_at': time.time(),
            'hash': None
        }
        
        try:
            # Send the transaction to the network, using enhanced parameters if available
            tx_hash = await self.eth_base.send_transaction(
                to=tx_data.get('to'),
                value=tx_data.get('value', 0),
                data=tx_data.get('data', '0x'),
                gas_limit=tx_data.get('gas_limit'),
                gas_price=tx_data.get('gas_price'),
                max_fee_per_gas=tx_data.get('max_fee_per_gas'),
                max_priority_fee_per_gas=tx_data.get('max_priority_fee_per_gas')
            )
            
            # Update the transaction record
            self.pending_transactions[transaction_id]['hash'] = tx_hash
            self.pending_transactions[transaction_id]['status'] = TransactionStatus.PENDING
            
            # Move from pending to history
            self.transaction_history[transaction_id] = self.pending_transactions[transaction_id]
            del self.pending_transactions[transaction_id]
            
            return transaction_id
        except Exception as e:
            # Mark as failed if there was an error
            self.pending_transactions[transaction_id]['status'] = TransactionStatus.FAILED
            self.pending_transactions[transaction_id]['error'] = str(e)
            self.transaction_history[transaction_id] = self.pending_transactions[transaction_id]
            del self.pending_transactions[transaction_id]
            
            raise e
    
    async def get_transaction_status(self, tx_id: str) -> str:
        """
        Get the status of a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction status
        """
        if tx_id in self.pending_transactions:
            return self.pending_transactions[tx_id]['status']
        elif tx_id in self.transaction_history:
            return self.transaction_history[tx_id]['status']
        else:
            raise ValueError(f"Transaction {tx_id} not found")
    
    async def get_transaction_receipt(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the receipt of a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction receipt or None if not confirmed
        """
        if tx_id in self.transaction_history and self.transaction_history[tx_id]['hash']:
            tx_hash = self.transaction_history[tx_id]['hash']
            try:
                receipt = await self.eth_base.wait_for_transaction(tx_hash)
                return receipt
            except Exception:
                # Transaction might not be mined yet
                return None
        else:
            return None
    
    async def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all transactions.
        
        Returns:
            List of transaction records
        """
        return list(self.transaction_history.values())