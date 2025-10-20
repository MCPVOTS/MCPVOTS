# Enhanced Flaunch V1 API Documentation with Burn Mechanisms

{% hint style="info" %}
If you are looking to upload images, create revenue managers, or create tokens, [check out the API section](https://docs.flaunch.gg/for-builders/references/api).
{% endhint %}

## Overview

The Flaunch V1 API provides comprehensive access to token data, trading information, holder analytics, and **burn mechanism operations** across supported blockchain networks. All endpoints are publicly accessible (no authentication required) and return JSON responses with consistent formatting.

**Base URL**: `https://dev-api.flayerlabs.xyz`

## Burn Mechanisms in Flaunch

Flaunch supports token burning through the **Royalty NFT management rights**. The Royalty NFT holder can burn tokens they have bought back, providing deflationary pressure and enhanced tokenomics.

### Burn Mechanism Features

- **Royalty NFT Controlled**: Only Royalty NFT holders can initiate burns
- **Buyback Integration**: Burns tokens purchased through market buy operations
- **Deflationary Pressure**: Reduces total supply for enhanced scarcity
- **Market Analysis**: Perfect for VOTS token price analysis via MCPVOTS a2a
- **Community Benefits**: Creates buying pressure and supports price stability

### Burn Operations Available

1. **Market Buy + Burn**: Purchase tokens at market price and burn them
2. **Treasury Burn**: Burn accumulated tokens from Progressive Bid Wall
3. **Selective Burn**: Burn specific amounts based on market conditions
4. **Automated Burn**: Programmatic burning based on price triggers

---

## Enhanced Endpoints

### 7. Get Token Burn Data

**Endpoint**: `GET /v1/:chain/tokens/:tokenAddress/burns`

Returns comprehensive burn history and statistics for a specific token.

**Parameters**

* `chain` (path) - Network identifier (required)
* `tokenAddress` (path) - Token contract address (required)
* `limit` (query) - Items per page (optional, default: 50, max: 100)
* `offset` (query) - Items to skip (optional, default: 0)
* `startTime` (query) - Start timestamp for burn history (optional)
* `endTime` (query) - End timestamp for burn history (optional)

**Example Request**

```bash
curl "https://dev-api.flayerlabs.xyz/v1/base/tokens/0x1c93d155bd388241f9ab5df500d69eb529ce9583/burns?limit=10"
```

**Example Response**

```json
{
  "tokenAddress": "0x1c93d155bd388241f9ab5df500d69eb529ce9583",
  "burnStats": {
    "totalBurned": "1000000000000000000000",
    "totalBurnTransactions": 25,
    "burnRate24h": "50000000000000000000",
    "burnRate7d": "350000000000000000000",
    "burnRate30d": "1500000000000000000000",
    "averageBurnSize": "40000000000000000000",
    "largestBurn": "200000000000000000000",
    "burnEfficiency": 85.5
  },
  "burnHistory": [
    {
      "transactionHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
      "blockNumber": 12345678,
      "timestamp": 1703980800,
      "burnerAddress": "0x742d35cc6354c7deae7a5d3f2f4c2f8b8a8b9e6c",
      "amountBurned": "50000000000000000000",
      "burnType": "market_buy_burn",
      "ethSpent": "0.1",
      "royaltyNFTOwner": "0x742d35cc6354c7deae7a5d3f2f4c2f8b8a8b9e6c",
      "priceImpact": 0.02
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 25
  },
  "meta": {
    "network": "mainnet",
    "timestamp": 1703980800
  }
}
```

### 8. Get Burn Analytics for Market Analysis

**Endpoint**: `GET /v1/:chain/tokens/:tokenAddress/burn-analytics`

Returns advanced burn analytics optimized for market analysis and VOTS token pricing via MCPVOTS a2a.

**Parameters**

* `chain` (path) - Network identifier (required)
* `tokenAddress` (path) - Token contract address (required)
* `timeframe` (query) - Analysis timeframe: "1h", "24h", "7d", "30d" (default: "24h")
* `analysisType` (query) - Type of analysis: "price_impact", "supply_shrinkage", "holder_concentration" (default: "price_impact")

**Example Request**

```bash
curl "https://dev-api.flayerlabs.xyz/v1/base/tokens/0x1c93d155bd388241f9ab5df500d69eb529ce9583/burn-analytics?timeframe=24h&analysisType=price_impact"
```

**Example Response**

```json
{
  "tokenAddress": "0x1c93d155bd388241f9ab5df500d69eb529ce9583",
  "analysisType": "price_impact",
  "timeframe": "24h",
  "burnMetrics": {
    "totalBurned24h": "50000000000000000000",
    "supplyReductionPercentage": 0.05,
    "averagePriceImpact": 0.02,
    "burnFrequency": 12,
    "effectiveBuybackPressure": 85.5,
    "marketCapPreservation": 92.3
  },
  "priceAnalysis": {
    "preBurnPrice": "1234.567890123456789",
    "postBurnPrice": "1250.123456789012345",
    "priceIncrease": 1.26,
    "volatilityReduction": 15.7,
    "supportLevel": "1200.0"
  },
  "supplyAnalytics": {
    "totalSupplyBefore": "1000000000000000000000000",
    "totalSupplyAfter": "999950000000000000000000",
    "circulatingSupply": "999950000000000000000000",
    "burnedSupply": "50000000000000000000",
    "burnRateVelocity": 0.0005
  },
  "marketAnalysis": {
    "votsPriceRecommendation": "1240.0",
    "confidenceScore": 87.5,
    "nextBurnPrediction": 1703990800,
    "optimalEntryPoint": "1220.0",
    "riskAssessment": "low"
  },
  "meta": {
    "network": "mainnet",
    "timestamp": 1703980800,
    "analysisVersion": "1.2.0"
  }
}
```

### 9. Initiate Burn Operation (Royalty NFT Required)

**Endpoint**: `POST /v1/:chain/tokens/:tokenAddress/burn`

Initiates a burn operation for Royalty NFT holders. Requires proper authorization.

**Parameters**

* `chain` (path) - Network identifier (required)
* `tokenAddress` (path) - Token contract address (required)
* `amount` (body) - Amount of tokens to burn (required)
* `burnType` (body) - Type of burn: "market_buy_burn", "treasury_burn", "selective_burn" (required)
* `royaltyNFTSignature` (body) - Signature proving Royalty NFT ownership (required)

**Headers**

* `Authorization: Bearer <royalty_nft_signature>`
* `Content-Type: application/json`

**Example Request**

```bash
curl -X POST "https://dev-api.flayerlabs.xyz/v1/base/tokens/0x1c93d155bd388241f9ab5df500d69eb529ce9583/burn" \
  -H "Authorization: Bearer 0xabcdef..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100000000000000000000",
    "burnType": "market_buy_burn",
    "royaltyNFTSignature": "0xsignature..."
  }'
```

**Example Response**

```json
{
  "success": true,
  "transactionHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
  "burnDetails": {
    "amountBurned": "100000000000000000000",
    "burnType": "market_buy_burn",
    "ethSpent": "0.2",
    "royaltyNFTOwner": "0x742d35cc6354c7deae7a5d3f2f4c2f8b8a8b9e6c",
    "supplyReduction": 0.01,
    "estimatedPriceImpact": 0.05
  },
  "marketAnalysis": {
    "newVotsPrice": "1260.0",
    "confidenceInterval": {
      "low": "1240.0",
      "high": "1280.0"
    },
    "nextOptimalBurnTime": 1703990800
  },
  "meta": {
    "network": "mainnet",
    "timestamp": 1703980800,
    "royaltyNFTVerified": true
  }
}
```

### 10. Get Burn Strategy Recommendations

**Endpoint**: `GET /v1/:chain/tokens/:tokenAddress/burn-strategy`

Provides AI-powered burn strategy recommendations for optimal market analysis and VOTS token pricing.

**Parameters**

* `chain` (path) - Network identifier (required)
* `tokenAddress` (path) - Token contract address (required)
* `currentPrice` (query) - Current token price in ETH (optional)
* `marketCap` (query) - Current market cap in ETH (optional)
* `timeHorizon` (query) - Strategy time horizon: "short", "medium", "long" (default: "medium")

**Example Request**

```bash
curl "https://dev-api.flayerlabs.xyz/v1/base/tokens/0x1c93d155bd388241f9ab5df500d69eb529ce9583/burn-strategy?currentPrice=0.001234&timeHorizon=medium"
```

**Example Response**

```json
{
  "tokenAddress": "0x1c93d155bd388241f9ab5df500d69eb529ce9583",
  "strategyRecommendations": [
    {
      "strategyId": "conservative_buyback",
      "name": "Conservative Buyback Strategy",
      "description": "Gradual burning to maintain steady price appreciation",
      "recommendedBurnAmount": "25000000000000000000",
      "optimalTiming": "market_dip",
      "expectedPriceImpact": 0.8,
      "riskLevel": "low",
      "timeHorizon": "2-4 weeks",
      "votsPriceTarget": "1280.0",
      "confidenceScore": 92.5
    },
    {
      "strategyId": "aggressive_deflation",
      "name": "Aggressive Deflation Strategy",
      "description": "Large burns during high volume periods for maximum impact",
      "recommendedBurnAmount": "100000000000000000000",
      "optimalTiming": "high_volume",
      "expectedPriceImpact": 3.2,
      "riskLevel": "medium",
      "timeHorizon": "1 week",
      "votsPriceTarget": "1350.0",
      "confidenceScore": 78.3
    }
  ],
  "marketContext": {
    "currentPrice": "1234.567890123456789",
    "priceMomentum": "bullish",
    "volume24h": "456.789",
    "burnEfficiency": 85.5,
    "optimalBurnWindow": {
      "start": 1703980800,
      "end": 1703990800
    }
  },
  "meta": {
    "network": "mainnet",
    "timestamp": 1703980800,
    "strategyModelVersion": "2.1.0"
  }
}
```

## Burn Mechanism Integration for MCPVOTS a2a

### VOTS Token Market Analysis

The burn mechanism endpoints enable sophisticated market analysis for VOTS tokens:

1. **Real-time Burn Tracking**: Monitor burn transactions and their market impact
2. **Supply Analysis**: Track total supply reduction and deflationary pressure
3. **Price Impact Modeling**: Predict price movements based on burn activities
4. **Strategy Optimization**: AI-powered recommendations for optimal burn timing
5. **Risk Assessment**: Evaluate burn strategy risks and confidence scores

### MCPVOTS a2a Integration Example

```javascript
// MCPVOTS a2a integration for VOTS token analysis
const votsAnalysis = {
  tokenAddress: "0x1c93d155bd388241f9ab5df500d69eb529ce9583",
  burnData: await fetchBurnAnalytics(tokenAddress),
  marketData: await fetchPriceData(tokenAddress),
  strategy: await fetchBurnStrategy(tokenAddress),

  calculateVotsPrice() {
    const burnPressure = this.burnData.burnMetrics.effectiveBuybackPressure;
    const marketCap = this.marketData.price.marketCapETH;
    const supplyReduction = this.burnData.supplyAnalytics.supplyReductionPercentage;

    // Advanced VOTS pricing algorithm
    return marketCap * (1 + burnPressure/100) * (1 - supplyReduction/100);
  },

  getRecommendations() {
    return this.strategy.strategyRecommendations.map(strategy => ({
      ...strategy,
      projectedVotsPrice: this.calculateVotsPrice() * (1 + strategy.expectedPriceImpact/100)
    }));
  }
};
```

## Rate Limits & Best Practices

### Enhanced Rate Limiting for Burn Operations

- **Read Operations**: 100 requests/minute per IP
- **Burn Analytics**: 50 requests/minute per IP
- **Burn Operations**: 10 requests/minute per Royalty NFT holder
- **Strategy Recommendations**: 25 requests/minute per IP

### Burn Mechanism Best Practices

1. **Royalty NFT Verification**: Always verify NFT ownership before operations
2. **Market Timing**: Use analytics endpoints to identify optimal burn windows
3. **Supply Impact**: Monitor total supply changes and adjust strategies accordingly
4. **Price Impact**: Consider both immediate and long-term price effects
5. **Community Communication**: Burn operations should be transparent to holders

## Support and Resources

* **API Issues**: Report any API issues or bugs through Discord
* **Burn Mechanism Support**: Contact the team for Royalty NFT burn operation assistance
* **Market Analysis**: MCPVOTS a2a integration support available
* **Rate Limiting**: Higher limits available for production applications - contact the team
* **Feature Requests**: Suggest new burn-related endpoints or analytics features

This enhanced documentation provides everything needed to integrate burn mechanisms into your Flaunch token operations and enable sophisticated market analysis for VOTS tokens via MCPVOTS a2a.
