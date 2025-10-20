# Flaunch Token Creator

Create your own Flaunch tokens on Base with royalty NFTs, progressive bid walls, and creator revenue sharing.

## What is Flaunch?

Flaunch is a permissionless tokenization protocol on Base that gives creators true ownership through:

- **Royalty NFT**: Transferable NFT representing your share of future trading fees
- **Progressive Bid Wall**: Automatic buyback mechanism using trading fees to protect price floors
- **Creator Revenue**: 0-100% of trading fees streamed directly to creators in ETH
- **Fair Launch**: Permissionless token creation with customizable parameters

## Features

- 🚀 Create tokens with custom parameters
- 👑 Royalty NFT ownership of revenue streams
- 🛡️ Progressive Bid Wall price protection
- 💰 Creator fee sharing (0-100%)
- 🎯 Fair launch mechanics
- 📊 Automatic metadata handling via IPFS
- 🔗 Integration with existing trading infrastructure

## Quick Start

### Prerequisites

1. **Node.js and npm** (for Flaunch SDK)
2. **Base network wallet** with ETH for gas
3. **Private key** (keep secure!)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt  # If you have a requirements.txt

# Or manually install required packages
pip install requests web3
```

### Environment Setup

```bash
# Set your environment variables
export PRIVATE_KEY="your_private_key_here"
export WALLET_ADDRESS="0xYourWalletAddress"
```

### Create Your First Token

```bash
# Basic token creation (no protocol fees for < $10k market cap)
python flaunch_token_creator.py \
  --name "My Awesome Token" \
  --symbol "AWESOME" \
  --mcap 5000 \
  --creator-fee 50

# Advanced token with custom parameters
python flaunch_token_creator.py \
  --name "Premium Token" \
  --symbol "PREMIUM" \
  --mcap 25000 \
  --fair-launch 70 \
  --creator-fee 75 \
  --description "A premium token with high creator rewards" \
  --image "https://example.com/token-image.png" \
  --external-url "https://example.com"
```

## Token Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `--name` | Token name | Required | Any string |
| `--symbol` | Token symbol | Required | 1-8 characters |
| `--mcap` | Initial market cap (USD) | 10000 | > 0 |
| `--fair-launch` | % allocated to fair launch | 60 | 40-80 recommended |
| `--duration` | Fair launch duration (seconds) | 1800 | > 0 |
| `--creator-fee` | Creator's fee share (%) | 50 | 0-100 |
| `--description` | Token description | Auto-generated | Any string |
| `--image` | Token image URL | Placeholder | Valid URL |
| `--external-url` | Website/social link | None | Valid URL |

## Understanding Flaunch Economics

### Royalty NFT
- **Transferable**: Sell your revenue stream to investors
- **Fractionalizable**: Split ownership across multiple holders
- **DAO-compatible**: Use with DAOs for community ownership
- **Passive income**: Receive ETH from all future trading fees

### Progressive Bid Wall (PBW)
- **Automatic buybacks**: Uses trading fees to create buy orders below current price
- **Price protection**: Prevents extreme dumps
- **Community benefit**: Remaining fees go to community
- **Uniswap V4 integration**: Advanced AMM mechanics

### Creator Revenue
- **0-100% split**: Choose your revenue share
- **ETH streaming**: Direct payments in ETH
- **Immutable after launch**: Set once, locked forever
- **No token dumps**: Pure ETH revenue

## Integration with Trading System

The created tokens integrate seamlessly with your existing trading infrastructure:

```python
# After creating a token, it will appear in DexScreener
# Your existing scanners will automatically detect it
# Use your trading bots to provide initial liquidity

# Example: Monitor your new token
python base_trading_scanner.py --token YOUR_TOKEN_ADDRESS
```

## Examples

### Meme Token
```bash
python flaunch_token_creator.py \
  --name "Doge Moon" \
  --symbol "MOON" \
  --mcap 5000 \
  --fair-launch 60 \
  --creator-fee 25 \
  --description "To the moon! 🚀"
```

### Utility Token
```bash
python flaunch_token_creator.py \
  --name "Build Protocol" \
  --symbol "BUILD" \
  --mcap 15000 \
  --fair-launch 70 \
  --creator-fee 80 \
  --description "Decentralized building protocol" \
  --external-url "https://build-protocol.com"
```

### Community Token
```bash
python flaunch_token_creator.py \
  --name "Community Coin" \
  --symbol "COMMUNITY" \
  --mcap 8000 \
  --fair-launch 50 \
  --creator-fee 10 \
  --description "Owned by the community, for the community"
```

## Security Notes

- 🔐 **Never share your private key**
- ⚡ **Test on testnet first** (if available)
- 💰 **Market caps < $10k have no protocol fees**
- 🛡️ **Royalty NFT gives true ownership**
- 📊 **All parameters are immutable after launch**

## Troubleshooting

### Common Issues

1. **"PRIVATE_KEY environment variable required"**
   - Set your private key: `export PRIVATE_KEY="0x..."`

2. **"Wallet address required"**
   - Set wallet address: `export WALLET_ADDRESS="0x..."`

3. **Node.js not found**
   - Install Node.js from https://nodejs.org/

4. **Transaction failed**
   - Check ETH balance for gas fees
   - Verify network connection to Base

### Getting Help

- Check the [Flaunch Documentation](https://docs.flaunch.gg/)
- Join the [Flaunch Discord](https://discord.gg/flaunch)
- Review transaction on [BaseScan](https://basescan.org/)

## Advanced Usage

### Custom Metadata
```python
# The script automatically creates IPFS metadata
# For custom metadata, modify the token_params in the code
metadata = {
    "name": "Custom Token",
    "description": "Advanced token with custom properties",
    "image": "ipfs://your-image-hash",
    "attributes": [
        {"trait_type": "Rarity", "value": "Legendary"},
        {"trait_type": "Utility", "value": "Governance"}
    ]
}
```

### Revenue Management
```python
# After launch, your Royalty NFT can be:
# - Sold to investors
# - Used as collateral
# - Split among community members
# - Donated to charities
# - Traded on secondary markets
```

## License

This tool integrates with the Flaunch protocol. Please review Flaunch's terms of service.
