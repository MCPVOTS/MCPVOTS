# 🚀 VOTS Token Bootstrap System

A revolutionary token launch system that bootstraps liquidity using Uniswap V4 hooks, enabling fair distribution without requiring initial capital.

## 🎯 The Problem

Traditional token launches require significant upfront capital for liquidity pools. This creates barriers to entry and often leads to unfair token distribution where early participants get disproportionate advantages.

## 💡 The Solution: V4 Bootstrap

VOTS uses Uniswap V4's advanced hook system to automatically bootstrap liquidity when the first meaningful trades occur. No initial liquidity required!

### How It Works

1. **Deploy Contracts**: VOTS token, V4 bootstrap hook, and pool manager
2. **Fair Launch Period**: 7-day window for community contributions
3. **Automatic Bootstrap**: When trading volume reaches threshold, liquidity is created
4. **Fair Distribution**: Contributors get VOTS proportional to their ETH contribution

## 🏗️ Architecture

### Core Contracts

#### VOTSToken.sol

- ERC20 token with automatic burn mechanisms (0.01% per transaction)
- Bot ecosystem integration for micro-payments
- Compatible with Uniswap V4 pools

#### VOTSBoostrapHook.sol

- Uniswap V4 hook that monitors trading activity
- Triggers bootstrap when volume threshold is reached
- Automatically creates initial liquidity pool

#### VOTSPoolManager.sol

- Manages fair launch contributions
- Handles proportional token distribution
- Coordinates with V4 hook for pool creation

## 🚀 Quick Start

### 1. Deploy the Ecosystem

```bash
# Deploy to Base mainnet
python deploy_vots.py --network base --private-key $PRIVATE_KEY
```

This deploys:
- VOTS token contract
- V4 bootstrap hook
- Pool manager contract
- Starts 7-day fair launch period

### 2. Community Contributions

During the fair launch period, anyone can contribute ETH:

```javascript
// Send ETH directly to pool manager (contributes automatically)
await wallet.sendTransaction({
  to: "POOL_MANAGER_ADDRESS",
  value: ethers.parseEther("0.1")
});
```

### 3. Automatic Bootstrap

When total ETH contributions reach 1 ETH, the system:
- Creates Uniswap V4 VOTS/ETH pool
- Adds initial liquidity (1M VOTS + contributed ETH)
- Enables trading

### 4. Claim Tokens

After bootstrap completion, contributors claim proportional VOTS:

```javascript
// Check claimable amount
const info = await poolManager.getBootstrapInfo(userAddress);
console.log(`Claimable: ${ethers.formatEther(info.userClaimable)} VOTS`);

// Claim tokens
await poolManager.claimTokens();
```

## 📊 Bootstrap Mechanics

### Fair Launch Parameters
- **Duration**: 7 days
- **Minimum ETH**: 1 ETH to trigger bootstrap
- **Initial VOTS**: 1,000,000 VOTS for liquidity
- **Distribution**: Proportional to ETH contribution

### Bootstrap Flow
```
Deploy Contracts → Fair Launch → Contributions → Volume Threshold → Auto Bootstrap → Trading Enabled
```

### Token Economics
- **Total Supply**: 10,000,000 VOTS
- **Burn Rate**: 0.01% per transaction
- **Bot Rewards**: 30% of burns go to registered bots
- **Treasury**: 60% of burns for ecosystem development

## 🧪 Testing

Test the bootstrap mechanism locally:

```bash
# Run bootstrap tests
python test_vots_bootstrap.py --pool-manager $POOL_MANAGER_ADDRESS --full-test
```

## 🔧 Configuration

### Network Support
- ✅ Base Mainnet
- ✅ Base Goerli (testnet)

### V4 Hook Permissions
```solidity
beforeSwap: true    // Monitor trading volume
afterSwap: true     // Track bootstrap progress
```

### Bootstrap Thresholds
```solidity
BOOTSTRAP_THRESHOLD = 0.1 ether;  // Minimum volume to trigger
INITIAL_LIQUIDITY_VOTS = 1000000 ether;  // VOTS for initial pool
INITIAL_LIQUIDITY_ETH = 1 ether;   // ETH for initial pool
```

## 🎯 Use Cases

### Bot Ecosystem
- **Micro-payments**: 0.01% fee enables $0.0001 transactions
- **Automated rewards**: Bots earn from successful operations
- **Reputation system**: Quality bots get higher rewards

### Fair Launch Example
```
Day 1: Deploy contracts, announce fair launch
Day 2-7: Community contributes 2 ETH total
Day 7: Bootstrap triggers, pool created with 1M VOTS + 2 ETH
Result: Fair distribution, immediate liquidity, no front-running
```

## 🔒 Security Features

- **ReentrancyGuard**: Prevents reentrancy attacks
- **Ownable**: Owner controls critical functions
- **Time-locked**: 7-day fair launch prevents flash launches
- **Proportional distribution**: No advantage to large contributors

## 📈 Success Metrics

### Launch Success
- ✅ Pool created with >1 ETH liquidity
- ✅ >10 contributors participated
- ✅ Fair distribution achieved

### Ecosystem Growth
- 🤖 50+ registered bots within 1 month
- 💰 $100+ daily volume
- 🔥 5% monthly burn rate

## 🚨 Important Notes

### Prerequisites
- Uniswap V4 must be deployed on target network
- Sufficient gas for contract deployments (~10 ETH recommended)

### Limitations
- Requires V4 deployment on target chain
- Bootstrap only triggers with sufficient volume
- Emergency functions available for recovery

### Emergency Functions
```solidity
// Recover tokens if bootstrap fails
await poolManager.emergencyRecover(tokenAddress, amount);

// Manual bootstrap trigger (testing only)
await bootstrapHook.emergencyBootstrap();
```

## 🎉 Conclusion

VOTS Bootstrap revolutionizes token launches by:
- **Eliminating liquidity barriers**
- **Ensuring fair distribution**
- **Creating immediate tradability**
- **Enabling micro-payment ecosystems**

**Launch a token with $0 initial liquidity and create a thriving bot ecosystem!** 🚀
