#!/usr/bin/env python3
"""
Analyze successful V4 transaction to learn encoding
"""

from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Successful V4 swap transaction
tx_hash = '0xcd147b39887e629c268a9af02080a5c06736af96fd977a1d520f001f11ccc5d4'

print("Analyzing successful V4 transaction...")
print(f"TX: {tx_hash}\n")

tx = w3.eth.get_transaction(tx_hash)

print(f"From: {tx['from']}")
print(f"To: {tx['to']}")
print(f"Value: {tx['value'] / 1e18} ETH")
print(f"Gas: {tx['gas']}")
print(f"\nInput data ({len(tx['input'])} bytes):")
print(f"Method ID: {tx['input'][:10]}")
print(f"First 200 chars: {tx['input'][:200]}")

# Try to decode
print("\nDecoding execute() function...")
# execute(bytes commands, bytes[] inputs, uint256 deadline)

input_data = tx['input']
method_id = input_data[:10]
params = input_data[10:]

print(f"Method: {method_id}")
print(f"Params length: {len(params)} bytes")
print(f"Params hex: {params[:100]}...")
