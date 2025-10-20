#!/usr/bin/env python3
"""
Deploy MAXXDataService to Base mainnet
"""

import os
import json
from web3 import Web3
from solcx import compile_source, install_solc

# Install solc if needed
try:
    install_solc('0.8.20')
except:
    pass  # Already installed

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Mainnet configuration
MAINNET_RPC = "https://mainnet.base.org"
TREASURY_WALLET = "0x78c35a4206d18f58f1DB46f06A6507D094d7A7A9"  # Your treasury wallet
MAXX_TOKEN_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467'
PRIVATE_KEY = os.getenv('ETHEREUM_PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("ETHEREUM_PRIVATE_KEY not set")

# Read contract source
with open('contracts/MAXXDataService.sol', 'r') as f:
    contract_source = f.read()

# Compile contract
compiled_sol = compile_source(contract_source, solc_version="0.8.20")
contract_interface = compiled_sol['<stdin>:MAXXDataService']

# Connect to mainnet
w3 = Web3(Web3.HTTPProvider(MAINNET_RPC))
account = w3.eth.account.from_key(PRIVATE_KEY)

print(f"Deploying from: {account.address}")
print(f"Balance: {w3.eth.get_balance(account.address) / 10**18} ETH")

# Deploy
contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

# Build transaction
nonce = w3.eth.get_transaction_count(account.address)
tx = contract.constructor(MAXX_TOKEN_ADDRESS, TREASURY_WALLET).build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': w3.eth.gas_price
})

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Deployment tx: {tx_hash.hex()}")

# Wait for receipt
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
contract_address = receipt['contractAddress']

print(f"Contract deployed at: {contract_address}")

# Save to .env
with open('.env', 'a') as f:
    f.write(f"\nDATA_SERVICE_CONTRACT={contract_address}\n")

print("Deployment complete!")
