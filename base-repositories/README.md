# Base Repositories Collection

This directory contains all repositories from the [Base](https://github.com/base) organization on GitHub, automatically cloned and kept up-to-date for reference and development purposes.

## 📁 Repository Overview

The Base organization contains repositories related to:

- **Base Blockchain**: Coinbase's Layer 2 Ethereum scaling solution
- **Smart Contracts**: Protocol contracts and deployment scripts
- **Developer Tools**: SDKs, libraries, and development utilities
- **Documentation**: Guides, tutorials, and API references
- **Infrastructure**: Node software, bridges, and supporting systems

## 🚀 Quick Start

### Initial Setup

1. All repositories are automatically cloned using `clone_all.bat`
2. Large repositories (optimism, op-geth, reth, etc.) are skipped initially for faster setup
3. Run `clone_all.bat update` to update existing repositories

### Daily Updates

- Run `daily_update.bat` to update all cloned repositories
- Or use `clone_all.bat update` for manual updates
- Windows Scheduled Task can be set up using `setup_scheduled_task.ps1`

## 📂 Repository Categories

### 01-Core-Protocol
- `contracts` - Base protocol smart contracts
- `contract-deployments` - Deployment scripts and addresses
- `op-enclave` - Optimism enclave for Base

### 02-Developer-Tools
- `account-sdk` - Account abstraction SDK
- `foundry` - Foundry tooling
- `keyspace-client` - Keyspace client utilities
- `keyspace-recovery-service` - Keyspace recovery service
- `op-viem` - Viem utilities for Optimism/Base
- `op-wagmi` - Wagmi hooks for Optimism/Base
- `paymaster` - Paymaster implementation

### 03-Infrastructure
- `blob-archiver` - Blob archiving system
- `bridge` - Cross-chain bridge
- `node` - Base node software

### 04-Applications
- `demos` - Example applications
- `docs` - Documentation site
- `land-sea-and-sky` - Land, Sea & Sky game
- `onchainsummer.xyz` - Onchain Summer website
- `web` - Base website

### 05-Security
- `FCL-ecdsa-verify-audit` - ECDSA verification audit
- `pessimism` - Pessimistic proof system

### 06-Identity
- `basenames` - Base names service
- `eip712sign` - EIP-712 signing utilities
- `webauthn-sol` - WebAuthn Solidity contracts

### 07-Utilities
- `brand-kit` - Branding assets
- `chains` - Chain configurations
- `guides` - Developer guides
- `withdrawer` - Withdrawal utilities

## 🔧 Scripts

### `clone_all.bat`

Clones all Base repositories (skips large ones initially)

```batch
clone_all.bat          # Clone missing repositories
clone_all.bat update   # Update existing repositories
```

### `daily_update.bat`

Updates all cloned repositories (designed for scheduled execution)

### `setup_scheduled_task.ps1`

Sets up Windows Scheduled Task for daily updates (run as Administrator)

### `clone_base_repos.ps1`
PowerShell version of the cloning script (alternative to batch files)

## 📊 Repository Statistics

- **Total Repositories**: 70+ (as of October 2025)
- **Primary Languages**: Solidity, TypeScript, Go, Rust
- **Key Topics**: Blockchain, DeFi, Layer 2, Ethereum scaling

## 🔄 Update Process

The repositories are kept synchronized with upstream using:
```bash
git pull --rebase
```

This ensures clean commit history while staying up-to-date with the latest changes.

## 📈 Monitoring

- Check `clone_log.txt` for cloning/update logs
- Check `update_log.txt` for daily update logs
- Scheduled task runs daily at 2:00 AM (configurable)

## 🤝 Contributing

This is an automated mirror of the Base organization repositories. For contributions:
1. Visit the original repository on GitHub
2. Follow Base's contribution guidelines
3. Submit pull requests to the upstream repositories

## 📚 Resources

- [Base Documentation](https://docs.base.org)
- [Base Developer Portal](https://base.org)
- [Base GitHub Organization](https://github.com/base)
- [Base Discord](https://discord.gg/base)

## ⚠️ Notes

- Large repositories (optimism, op-geth, reth, etc.) are skipped by default
- Manual cloning of large repos may be needed for specific development work
- Some repositories may require specific build tools or dependencies
- Always check individual repository READMEs for setup instructions

---

*Last updated: October 19, 2025*
*Automated setup for Base ecosystem development and reference*
