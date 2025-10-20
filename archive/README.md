# Archived Scripts

This directory contains old scripts that have been consolidated into the new `master_trading_system.py`.

## Archived Files

### Main Entry Points
- `main.py` - Original ecosystem main entry point
- `main_maxx_agent.py` - Agent-based trading system
- `start_agent.py` - Simple starter script
- `storage_integrated_main.py` - Storage-focused version

### Trading Implementations
- `unified_maxx_trader.py` - Working trading system (logic integrated)
- `standalone_dex_trader.py` - Another DEX implementation
- `final_trading_test.py` - Test-focused trading
- `simple_trading_test.py` - Simplified trading test

### Test Scripts
- `test_one_dollar_trading.py` - $1 trading test
- `test_sell_all.py` - Sell all test

## Migration

All functionality from these scripts has been consolidated into:
- **New System**: `../master_trading_system.py`
- **Configuration**: `../standalone_config.py`
- **Documentation**: `../MASTER_SYSTEM_GUIDE.md`

## Usage Examples

### Old Way (Archive)
```bash
python unified_maxx_trader.py
python test_one_dollar_trading.py
python main_maxx_agent.py
```

### New Way (Master System)
```bash
# Interactive trading (replaces unified_maxx_trader.py)
python ../master_trading_system.py

# Testing (replaces test_one_dollar_trading.py)
python ../master_trading_system.py --mode test

# Automated trading (replaces main_maxx_agent.py)
python ../master_trading_system.py --mode automated
```

## Why Archived?

1. **Code Consolidation**: Reduced from 15+ scripts to 1 master system
2. **Maintenance**: Single codebase is easier to maintain
3. **User Experience**: One script with multiple modes
4. **Rate Limiting**: Advanced rate limiting across all operations
5. **RPC Failover**: Unified RPC management

## Recovery

If you need to restore any of these scripts:
1. Copy the desired script from this directory to the parent directory
2. Update any import paths as needed
3. Note that dependencies may have changed

## Date Archived
2025-01-02 - Consolidated into master_trading_system.py