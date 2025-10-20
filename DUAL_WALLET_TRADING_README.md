# Dual Wallet Trading Setup
## Running Flaunch Trading Separate from Main MAXX Trader

This guide shows you how to run **two independent trading systems** simultaneously:
- **Main MAXX Trader**: Your existing trading system
- **Flaunch Trader**: New system for Flaunch token opportunities

## 🏦 Why Two Wallets?

- **Safety**: Each system uses a separate wallet
- **Isolation**: No interference between systems
- **Risk Management**: Different capital allocations
- **Strategy Diversity**: Different trading approaches

## 📋 Quick Setup (3 Steps)

### 1. Create Separate Flaunch Wallet

```bash
# Run the setup helper
python flaunch_wallet_setup.py
```

This will:
- Guide you through creating a new wallet
- Set up configuration for $20 capital
- Create `flaunch_wallet_config.py`

### 2. Fund Your Flaunch Wallet

- **Amount**: Exactly $20 worth of ETH
- **Network**: Base mainnet
- **Security**: Use a NEW wallet, never reuse your main trading wallet

### 3. Start Both Systems

```bash
# Windows: Run both systems simultaneously
run_both_traders.bat

# Or manually:
# Terminal 1: python maxx_trader_fix.py [your usual args]
# Terminal 2: python flaunch_separate_trader.py
```

## 📊 System Overview

| System | Wallet | Capital | Strategy | Risk |
|--------|--------|---------|----------|------|
| **MAXX Trader** | Main Wallet | $50+ | Reactive trading | Medium |
| **Flaunch Trader** | Separate Wallet | $20 | Launch sniping | Low-Medium |

## 🔧 Configuration Files

### Main MAXX Trader
- Uses: `standalone_config.py` or `.env`
- Wallet: Your main trading wallet
- Database: `trades.db`

### Flaunch Trader
- Uses: `flaunch_wallet_config.py`
- Wallet: **Separate wallet**
- Database: `flaunch_trades.db`
- Logs: `flaunch_trading.log`

## 📈 Trading Strategies

### Flaunch Trader Features:
- **Fair Launch Sniping**: Buy during 30-60 min launch window
- **Revenue Manager Focus**: Target tokens with fee collection
- **Burn Mechanism Trading**: Use VOTS analysis signals
- **Conservative Sizing**: Max $5 per trade
- **Daily Limits**: Max 3 trades per day

### Risk Management:
- **Stop Loss**: 50% per trade
- **Profit Target**: 250% per trade
- **Daily Loss Limit**: $4 max loss
- **Emergency Stop**: 80% wallet loss triggers

## 📊 Monitoring Both Systems

### Main MAXX Trader
- Check existing dashboard/logs
- Monitor `trades.db`
- Watch main wallet balance

### Flaunch Trader
```bash
# Check status
python flaunch_separate_trader.py  # Shows current stats

# View logs
tail -f flaunch_trading.log

# Check database
sqlite3 flaunch_trades.db "SELECT * FROM flaunch_trades;"
```

## 🚨 Safety Features

### Independent Operation
- ✅ Separate wallets prevent cross-contamination
- ✅ Different databases avoid conflicts
- ✅ Isolated logging and monitoring
- ✅ Independent risk management

### Emergency Controls
```bash
# Stop Flaunch trader only
# Close the "Flaunch Trader" command window

# Or modify config
# Set REQUIRE_MANUAL_APPROVAL = True in flaunch_wallet_config.py
```

## 💰 Capital Allocation

### Recommended Split:
- **Main MAXX Trader**: $50+ (your existing capital)
- **Flaunch Trader**: $20 (new wallet)

### Scaling Plan:
1. **Phase 1**: $20 Flaunch - prove strategies
2. **Phase 2**: $50 Flaunch - scale successful approaches
3. **Phase 3**: $100+ Flaunch - full deployment

## 🔍 Performance Tracking

### Daily Reports
Both systems generate daily P&L reports:
- Main: Check existing logs
- Flaunch: Check `flaunch_trading.log`

### Weekly Review
Compare performance:
```bash
# Flaunch weekly stats
sqlite3 flaunch_trades.db "
SELECT
    COUNT(*) as total_trades,
    SUM(pnl_usd) as total_pnl,
    AVG(pnl_pct) as avg_return,
    SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
FROM flaunch_trades
WHERE entry_time >= date('now', '-7 days');
"
```

## 🛑 Troubleshooting

### Flaunch Trader Issues
```bash
# Check configuration
python flaunch_wallet_config.py

# Validate setup
python flaunch_separate_trader.py  # Should show status without starting
```

### Common Issues
1. **"Configuration not found"**: Run `python flaunch_wallet_setup.py`
2. **"Private key invalid"**: Check format (must start with 0x)
3. **"No ETH balance"**: Fund the Flaunch wallet with ETH
4. **"API errors"**: Check internet connection

## 📞 Support

- **Main MAXX Trader**: Use existing support channels
- **Flaunch Trader**: Check `flaunch_trading.log` for errors
- **Dual Setup**: Ensure both wallets have sufficient ETH for gas

## 🎯 Next Steps

1. ✅ Set up Flaunch wallet
2. ✅ Fund with $20 ETH
3. ✅ Test both systems separately
4. 🔄 Start dual trading
5. 📊 Monitor and optimize weekly

**Remember**: Start small, monitor closely, and never risk more than you can afford to lose!
