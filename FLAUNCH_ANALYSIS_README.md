# FLAUNCH TOKEN ANALYSIS SYSTEM

Complete analysis toolkit for evaluating Flaunch tokens before trading. Learn what to look for and make informed trading decisions.

## 📋 WHAT TO ANALYZE BEFORE TRADING

### 🔍 DUE DILIGENCE CHECKLIST
- [ ] **Contract Verification**: Is the contract verified on BaseScan?
- [ ] **Liquidity Lock**: Is liquidity locked to prevent rug pulls?
- [ ] **Honeypot Check**: Can tokens be sold after buying?
- [ ] **Token Distribution**: No single wallet holding >20% supply
- [ ] **Team Transparency**: Doxxed team with contact information
- [ ] **Audit Status**: Security audit completed (if available)

### 📊 FUNDAMENTAL ANALYSIS
- [ ] **Market Cap**: Prefer <$200K for early opportunities
- [ ] **Liquidity**: Minimum $10K for safe trading
- [ ] **24h Volume**: >$5K shows real interest
- [ ] **Holder Count**: >50 holders for good distribution
- [ ] **Token Age**: >24 hours to avoid extreme volatility
- [ ] **Fair Launch**: No large pre-sales or team allocations

### 📱 SOCIAL ANALYSIS
- [ ] **Community Size**: Active Telegram/Twitter presence
- [ ] **Sentiment**: Positive community discussions
- [ ] **Marketing**: Authentic promotion, not paid bots
- [ ] **Team Communication**: Regular updates and transparency

## 🛠️ ANALYSIS TOOLS

### 1. Comprehensive Analyzer (`flaunch_token_analyzer.py`)
**Purpose**: Detailed analysis with full scoring system
**Use When**: You want complete token evaluation
**Command**: `python flaunch_token_analyzer.py`

**Features**:
- On-chain metrics (liquidity, holders, volume)
- Social sentiment analysis
- Risk factor assessment
- Profit potential scoring
- Trading recommendations

### 2. Quick Scanner (`flaunch_quick_scanner.py`)
**Purpose**: Fast analysis for multiple tokens
**Use When**: Scanning opportunities quickly
**Command**: `python flaunch_quick_scanner.py [token1] [token2] ...`

**Features**:
- Parallel token analysis
- Quick risk assessment
- Sorted by profit potential
- Instant recommendations

### 3. Analysis Guide (`flaunch_analysis_guide.py`)
**Purpose**: Complete guide and checklists
**Use When**: Learning analysis criteria
**Command**: `python flaunch_analysis_guide.py`

**Features**:
- Detailed scoring criteria
- Risk factor explanations
- Trading recommendations
- Pre-trade checklists

## 📈 SCORING SYSTEM

### Profit Potential (0-100)
- **80-100**: Excellent opportunity
- **60-79**: Good potential
- **40-59**: Moderate potential
- **20-39**: Low potential
- **0-19**: Poor potential

### Risk Score (0-100)
- **0-19**: Very low risk
- **20-39**: Low risk
- **40-59**: Moderate risk
- **60-79**: High risk
- **80-100**: Very high risk

### Trading Recommendations
- **STRONG_BUY**: Profit >70, Risk <30 → $2-3 allocation
- **BUY**: Profit >50, Risk <50 → $1-2 allocation
- **WATCH**: Profit >30, Risk <60 → $0.50-1 allocation
- **PASS_LOW_POTENTIAL**: Profit <30 → Skip
- **AVOID_HIGH_RISK**: Risk >70 → Do not trade

## ⚠️ CRITICAL SAFETY CHECKS

### 🚨 RED FLAGS (Avoid These)
- Contract not verified on BaseScan
- Liquidity not locked
- High honeypot risk
- >20% supply held by single wallet
- Anonymous team with no contact info
- Very new token (<1 hour old)
- No community presence
- Paid bot marketing only

### ✅ GREEN FLAGS (Look For These)
- Verified contract
- Locked liquidity
- Fair token distribution
- Transparent team
- Growing community
- Positive sentiment
- Consistent volume
- Security audit

## 💰 POSITION SIZING GUIDELINES

### Based on Risk Level
- **Low Risk**: Up to 2% of trading capital
- **Medium Risk**: 0.5-1% of trading capital
- **High Risk**: 0.1-0.5% of trading capital
- **Very High Risk**: Skip or max 0.1%

### Maximum Allocation per Trade
- **Strong Buy**: $2-3
- **Buy**: $1-2
- **Watch**: $0.50-1
- **High Risk**: $0

## 🛡️ RISK MANAGEMENT

### Stop Loss Rules
- Set stop loss 20-50% below entry price
- Never risk more than 1% of total capital per trade
- Use trailing stops for profitable positions

### Take Profit Rules
- Take partial profits at 2x, 5x, 10x gains
- Don't hold forever expecting moonshots
- Set realistic profit targets

### ETH Reserve Protection
- Always maintain $5 ETH minimum for gas fees
- Never trade with < $2 ETH in wallet
- Monitor gas prices before large transactions

## 🚀 TRADING WORKFLOW

### 1. Token Discovery
```bash
# Quick scan multiple tokens
python flaunch_quick_scanner.py 0xTOKEN1 0xTOKEN2 0xTOKEN3
```

### 2. Detailed Analysis
```bash
# Full analysis of promising tokens
python flaunch_token_analyzer.py
```

### 3. Pre-Trade Checklist
- [ ] All safety checks passed
- [ ] Position size calculated
- [ ] Stop loss set
- [ ] ETH reserve confirmed
- [ ] Gas fees checked

### 4. Execution
- Use separate Flaunch wallet (0x84ce8BfDC3B3006c6d40d81db16B53f9e81C8B70)
- Start with small test trade
- Monitor position closely
- Take profits according to plan

### 5. Post-Trade Review
- Record trade details
- Analyze what worked/didn't work
- Update risk management rules
- Learn from experience

## 📊 PERFORMANCE TRACKING

### Key Metrics to Track
- Win rate percentage
- Average profit per trade
- Maximum drawdown
- Risk-adjusted returns
- Best/worst performing tokens

### Monthly Review
- Analyze trading performance
- Adjust position sizing
- Update analysis criteria
- Refine risk management

## 🔧 ADVANCED FEATURES

### Integration with Trading Bot
The analysis system integrates with your Flaunch trading bot:
- Automatic token screening
- Risk-based position sizing
- Stop loss management
- Profit taking automation

### Custom Scoring
Modify analysis weights in `FlaunchTokenAnalyzer` class:
```python
self.weights = {
    "liquidity": 0.25,    # 25% weight
    "holders": 0.20,      # 20% weight
    "volume": 0.15,       # 15% weight
    "social": 0.15,       # 15% weight
    "age": 0.10,          # 10% weight
    "contract": 0.10,     # 10% weight
    "risk": 0.05          # 5% weight
}
```

## ⚡ QUICK START

1. **Install Dependencies**:
   ```bash
   pip install requests
   ```

2. **Run Quick Analysis**:
   ```bash
   python flaunch_quick_scanner.py
   ```

3. **Get Full Guide**:
   ```bash
   python flaunch_analysis_guide.py
   ```

4. **Detailed Analysis**:
   ```bash
   python flaunch_token_analyzer.py
   ```

## 📞 SUPPORT

- Use the analysis tools before every trade
- Never invest more than you can afford to lose
- Start small and scale up gradually
- Keep detailed trading records
- Learn from both wins and losses

## 🔄 CONTINUOUS IMPROVEMENT

- Review analysis accuracy monthly
- Update scoring criteria based on results
- Add new risk factors as discovered
- Refine position sizing based on performance
- Stay updated with latest DeFi security practices

---

**Remember**: Trading involves risk. These tools help make informed decisions, but cannot guarantee profits. Always do your own research and never trade with money you cannot afford to lose.
