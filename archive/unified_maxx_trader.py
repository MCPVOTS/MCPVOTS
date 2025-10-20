#!/usr/bin/env python3
"""
Unified MAXX Trader - Complete Buy/Sell System
Combines all trading functionality with retry logic and multiple RPC endpoints
"""
import asyncio
import time
import requests
from web3 import Web3
from standalone_config import *

# Multiple RPC endpoints for failover
RPC_ENDPOINTS = [
    "https://mainnet.base.org",
    "https://base-mainnet.g.alchemy.com/v2/demo",
    "https://rpc.ankr.com/base"
]

# Minimal router ABI for trading
ROUTER_ABI = [
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

# ERC20 ABI for token operations
ERC20_ABI = [
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
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class UnifiedMAXXTrader:
    def __init__(self):
        self.w3 = None
        self.account = None
        self.router = None
        self.maxx_contract = None
        self.current_rpc_index = 0

    def get_working_rpc(self):
        """Find a working RPC endpoint"""
        for i, rpc_url in enumerate(RPC_ENDPOINTS):
            try:
                print(f"Testing RPC {i+1}/{len(RPC_ENDPOINTS)}: {rpc_url}")
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    chain_id = w3.eth.chain_id
                    if chain_id == 8453:
                        print(f"SUCCESS: Working RPC found - {rpc_url}")
                        self.current_rpc_index = i
                        return rpc_url, w3
                    else:
                        print(f"Wrong chain ID: {chain_id}")
                else:
                    print("Failed to connect")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)

        raise Exception("No working RPC endpoints found")

    def rotate_rpc(self):
        """Rotate to next RPC endpoint"""
        self.current_rpc_index = (self.current_rpc_index + 1) % len(RPC_ENDPOINTS)
        rpc_url = RPC_ENDPOINTS[self.current_rpc_index]
        print(f"Rotating to RPC: {rpc_url}")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        return self.w3

    def initialize(self):
        """Initialize the trader with working RPC"""
        try:
            rpc_url, self.w3 = self.get_working_rpc()
            print(f"Using RPC: {rpc_url}")

            # Create account
            self.account = self.w3.eth.account.from_key(ETHEREUM_PRIVATE_KEY)
            print(f"SUCCESS: Trading account: {self.account.address}")

            # Create contracts
            self.router = self.w3.eth.contract(
                address=Web3.to_checksum_address(UNISWAP_V2_ROUTER),
                abi=ROUTER_ABI
            )

            self.maxx_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(MAXX_CONTRACT_ADDRESS),
                abi=ERC20_ABI
            )

            return True

        except Exception as e:
            print(f"ERROR: Failed to initialize: {e}")
            return False

    def get_balances(self):
        """Get current ETH and MAXX balances"""
        try:
            # ETH balance
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = balance_wei / 10**18

            # MAXX balance
            maxx_balance_wei = self.maxx_contract.functions.balanceOf(self.account.address).call()
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            maxx_balance = maxx_balance_wei / (10 ** maxx_decimals)

            return balance_eth, maxx_balance

        except Exception as e:
            print(f"ERROR: Failed to get balances: {e}")
            return None, None

    def buy_maxx(self, eth_amount):
        """Buy MAXX tokens with ETH"""
        try:
            print(f"BUYING MAXX with {eth_amount} ETH")

            # Check balance
            eth_balance, _ = self.get_balances()
            if eth_balance < eth_amount:
                print(f"ERROR: Insufficient ETH balance: {eth_balance} < {eth_amount}")
                return None

            # Calculate transaction parameters
            eth_amount_wei = int(eth_amount * 10**18)
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            min_maxx_wei = 1 * (10 ** maxx_decimals)  # Conservative minimum

            # Build transaction
            deadline = int(time.time()) + 300  # 5 minutes

            # Get nonce and gas price with retry
            for attempt in range(3):
                try:
                    nonce = self.w3.eth.get_transaction_count(self.account.address)
                    gas_price = self.w3.eth.gas_price
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return None
                    time.sleep(2)
                    self.rotate_rpc()

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
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)

            for attempt in range(3):
                try:
                    print(f"Sending buy transaction (attempt {attempt + 1})...")
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = tx_hash.hex()
                    break
                except Exception as e:
                    print(f"Send attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return None
                    time.sleep(3)
                    self.rotate_rpc()

            print(f"SUCCESS: Buy transaction sent!")
            print(f"   TX Hash: {tx_hash_hex}")
            print(f"   BaseScan: https://basescan.org/tx/{tx_hash_hex}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                print(f"SUCCESS! Buy transaction confirmed!")
                print(f"   Block: {receipt.blockNumber}")
                print(f"   Gas Used: {receipt.gasUsed}")
                return tx_hash_hex
            else:
                print(f"ERROR: Buy transaction failed!")
                return None

        except Exception as e:
            print(f"ERROR: Buy failed: {e}")
            return None

    def approve_maxx(self, amount):
        """Approve MAXX spending for router"""
        try:
            print(f"APPROVING MAXX spending: {amount} tokens")

            # Get decimals and convert amount
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** maxx_decimals))

            # Check current allowance
            current_allowance = self.maxx_contract.functions.allowance(
                self.account.address,
                Web3.to_checksum_address(UNISWAP_V2_ROUTER)
            ).call()

            if current_allowance >= amount_wei:
                print("MAXX spending already approved")
                return True

            # Build approval transaction
            for attempt in range(3):
                try:
                    nonce = self.w3.eth.get_transaction_count(self.account.address)
                    gas_price = self.w3.eth.gas_price
                    break
                except Exception as e:
                    print(f"Nonce attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return False
                    time.sleep(2)
                    self.rotate_rpc()

            tx_data = self.maxx_contract.functions.approve(
                Web3.to_checksum_address(UNISWAP_V2_ROUTER),
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'gas': GAS_LIMIT,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            # Sign and send approval
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)

            for attempt in range(3):
                try:
                    print(f"Sending approval (attempt {attempt + 1})...")
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    break
                except Exception as e:
                    print(f"Approval attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return False
                    time.sleep(3)
                    self.rotate_rpc()

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                print(f"SUCCESS: MAXX approval confirmed!")
                return True
            else:
                print(f"ERROR: MAXX approval failed!")
                return False

        except Exception as e:
            print(f"ERROR: Approval failed: {e}")
            return False

    def sell_maxx(self, maxx_amount):
        """Sell MAXX tokens for ETH"""
        try:
            print(f"SELLING {maxx_amount} MAXX tokens")

            # Check balance
            _, maxx_balance = self.get_balances()
            if maxx_balance < maxx_amount:
                print(f"ERROR: Insufficient MAXX balance: {maxx_balance} < {maxx_amount}")
                return None

            # First approve spending
            if not self.approve_maxx(maxx_amount):
                print("ERROR: Failed to approve MAXX spending")
                return None

            # Convert MAXX amount to wei
            maxx_decimals = self.maxx_contract.functions.decimals().call()
            maxx_amount_wei = int(maxx_amount * (10 ** maxx_decimals))

            # Conservative minimum ETH output
            min_eth_wei = int(0.0001 * (10 ** 18))  # 0.0001 ETH minimum

            # Build transaction
            deadline = int(time.time()) + 300  # 5 minutes

            # Get nonce and gas price with retry
            for attempt in range(3):
                try:
                    nonce = self.w3.eth.get_transaction_count(self.account.address)
                    gas_price = self.w3.eth.gas_price
                    break
                except Exception as e:
                    print(f"Nonce attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return None
                    time.sleep(2)
                    self.rotate_rpc()

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
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, ETHEREUM_PRIVATE_KEY)

            for attempt in range(3):
                try:
                    print(f"Sending sell transaction (attempt {attempt + 1})...")
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = tx_hash.hex()
                    break
                except Exception as e:
                    print(f"Send attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        return None
                    time.sleep(3)
                    self.rotate_rpc()

            print(f"SUCCESS: Sell transaction sent!")
            print(f"   TX Hash: {tx_hash_hex}")
            print(f"   BaseScan: https://basescan.org/tx/{tx_hash_hex}")

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                print(f"SUCCESS! Sell transaction confirmed!")
                print(f"   Block: {receipt.blockNumber}")
                print(f"   Gas Used: {receipt.gasUsed}")
                return tx_hash_hex
            else:
                print(f"ERROR: Sell transaction failed!")
                return None

        except Exception as e:
            print(f"ERROR: Sell failed: {e}")
            return None

async def main():
    """Main trading function"""
    print("=" * 80)
    print("UNIFIED MAXX TRADING SYSTEM")
    print("=" * 80)

    trader = UnifiedMAXXTrader()

    # Initialize
    if not trader.initialize():
        print("FAILED TO INITIALIZE TRADER")
        return False

    # Get current balances
    eth_balance, maxx_balance = trader.get_balances()
    print(f"\nCURRENT BALANCES:")
    print(f"ETH: {eth_balance:.6f} ETH")
    print(f"MAXX: {maxx_balance:,.2f} MAXX")

    # Trading menu
    print(f"\nTRADING OPTIONS:")
    print(f"1. Buy MAXX with {TEST_ETH_AMOUNT} ETH (~$1 USD)")
    print(f"2. Sell 50% of MAXX holdings")
    print(f"3. Sell all MAXX holdings")
    print(f"4. Just check balances")

    choice = input(f"\nEnter choice (1-4): ").strip()

    if choice == "1":
        # Buy MAXX
        print(f"\nEXECUTING BUY ORDER...")
        tx_hash = trader.buy_maxx(TEST_ETH_AMOUNT)
        if tx_hash:
            print(f"\nBUY ORDER SUCCESSFUL!")
            print(f"Transaction: https://basescan.org/tx/{tx_hash}")
        else:
            print(f"\nBUY ORDER FAILED!")

    elif choice == "2":
        # Sell 50% MAXX
        if maxx_balance > 0:
            sell_amount = maxx_balance * 0.5
            print(f"\nEXECUTING SELL ORDER (50% of holdings)...")
            tx_hash = trader.sell_maxx(sell_amount)
            if tx_hash:
                print(f"\nSELL ORDER SUCCESSFUL!")
                print(f"Transaction: https://basescan.org/tx/{tx_hash}")
            else:
                print(f"\nSELL ORDER FAILED!")
        else:
            print(f"\nNO MAXX TOKENS TO SELL!")

    elif choice == "3":
        # Sell all MAXX
        if maxx_balance > 0:
            print(f"\nEXECUTING SELL ORDER (all holdings)...")
            tx_hash = trader.sell_maxx(maxx_balance)
            if tx_hash:
                print(f"\nSELL ORDER SUCCESSFUL!")
                print(f"Transaction: https://basescan.org/tx/{tx_hash}")
            else:
                print(f"\nSELL ORDER FAILED!")
        else:
            print(f"\nNO MAXX TOKENS TO SELL!")

    elif choice == "4":
        # Just check balances
        print(f"\nBALANCE CHECK COMPLETE")

    else:
        print(f"\nINVALID CHOICE!")
        return False

    # Final balance check
    time.sleep(3)
    final_eth, final_maxx = trader.get_balances()
    print(f"\nFINAL BALANCES:")
    print(f"ETH: {final_eth:.6f} ETH (change: {final_eth - eth_balance:+.6f})")
    print(f"MAXX: {final_maxx:,.2f} MAXX (change: {final_maxx - maxx_balance:+,.2f})")

    return True

if __name__ == "__main__":
    print("WARNING: This will execute REAL transactions with REAL money!")
    print(f"Trading Account: 0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9")
    print(f"Token: MAXX ({MAXX_CONTRACT_ADDRESS})")
    print()

    # Auto-confirmed for testing
    print("AUTO-CONFIRMED: Proceeding with trading system...")

    # Run the trader
    success = asyncio.run(main())

    if success:
        print("\nTRADING SESSION COMPLETED!")
    else:
        print("\nTRADING SESSION FAILED!")