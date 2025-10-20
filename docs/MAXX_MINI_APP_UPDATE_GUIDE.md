# MAXX Mini-App Update Guide

## Overview
This guide covers how to update and maintain the MAXX trading mini-app, including wallet integration, UI improvements, and feature additions.

## Core Architecture
- **Framework**: Next.js 15.5.6 with App Router
- **Wallet**: RainbowKit v2.2.9 with multi-network support
- **Blockchain**: Wagmi v2.18.1 + Viem v2.38.3
- **Styling**: Tailwind CSS with responsive design
- **3D Effects**: Three.js for cyberpunk background
- **Real-time**: WebSocket connection to MAXX bot

## File Structure
```
app/
├── page.tsx          # Main dashboard component
├── providers.tsx     # RainbowKit provider configuration
└── components/       # Reusable UI components

Key files:
- app/page.tsx: Main UI with wallet, trading data, Base names
- app/providers.tsx: Multi-network wallet configuration
- package.json: Dependencies and scripts
```

## Common Update Patterns

### 1. Adding New Networks to Wallet
**File**: `app/providers.tsx`
**Pattern**:
```typescript
const config = getDefaultConfig({
  appName: 'MAXX Trading',
  projectId: 'your-project-id',
  chains: [
    base,        // Always first for MAXX
    mainnet,
    sepolia,
    polygon,
    arbitrum,
    optimism,
    // Add new chains here
  ],
  ssr: true,
});
```

**Steps**:
1. Import new chain from 'viem/chains'
2. Add to chains array in getDefaultConfig
3. Test wallet modal shows new network

### 2. Updating Wallet Button Styling
**File**: `app/page.tsx`
**Pattern**:
```typescript
<ConnectButton.Custom>
  {({ account, chain, openConnectModal, mounted }) => {
    return (
      <div className="flex items-center gap-2">
        {/* Custom styling here */}
        <button
          onClick={openConnectModal}
          className="cyberpunk-button px-3 py-1 text-sm"
        >
          {account ? truncateAddress(account.address) : 'Connect Wallet'}
        </button>
      </div>
    );
  }}
</ConnectButton.Custom>
```

**Styling Classes**:
- `cyberpunk-button`: Neon glow effects
- `px-3 py-1`: Compact sizing
- `text-sm`: Smaller font

### 3. Adding Base Name Resolution
**File**: `app/page.tsx`
**Pattern**:
```typescript
const { data: baseName } = useReadContract({
  address: '0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5', // Basenames contract
  abi: BasenamesAbi,
  functionName: 'getName',
  args: [account?.address],
  chainId: base.id, // Only works on Base network
});

const displayName = baseName || truncateAddress(account?.address);
```

**Requirements**:
- Connected to Base network
- Basenames contract ABI imported
- Fallback to truncated address

### 4. Making Components Responsive
**File**: Any component file
**Pattern**:
```typescript
<div className="container mx-auto px-4">
  <div className="max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl">
    {/* Content */}
  </div>
</div>
```

**Breakpoints**:
- `sm:` 640px+
- `md:` 768px+
- `lg:` 1024px+
- `xl:` 1280px+

### 5. Adding New Features
**General Process**:
1. Identify requirement
2. Check existing components
3. Add to appropriate file
4. Test functionality
5. Update MCP memory
6. Commit changes

### 6. Testing Wallet Functionality
**Manual Testing Steps**:
1. Start dev server: `npm run dev`
2. Open wallet modal
3. Verify all networks appear
4. Test connection on each network
5. Check Base name resolution
6. Verify responsive design on mobile/desktop

**Automated Testing**:
```typescript
// Add to test file
describe('Wallet Connection', () => {
  it('should show all supported networks', () => {
    // Test network list
  });

  it('should resolve Base names correctly', () => {
    // Test Base name functionality
  });
});
```

### 7. Updating Dependencies
**Process**:
1. Check for updates: `npm outdated`
2. Update packages: `npm update`
3. Test compatibility
4. Update package.json if needed
5. Test wallet and UI functionality

### 8. WebSocket Integration Updates
**File**: `app/page.tsx`
**Pattern**:
```typescript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8080');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setTickData(data);
  };
  return () => ws.close();
}, []);
```

**Updates**:
- Handle connection errors
- Add reconnection logic
- Update data parsing

### 9. Adding New UI Components
**Process**:
1. Create component in `app/components/`
2. Import and use in `app/page.tsx`
3. Add responsive classes
4. Test on different screen sizes

### 10. Performance Optimization
**Common Issues**:
- Three.js background causing lag on mobile
- WebSocket reconnection issues
- Large bundle size

**Solutions**:
- Lazy load Three.js components
- Implement WebSocket reconnection
- Code splitting for large components

## Troubleshooting

### Wallet Modal Not Showing Networks
- Check chains array in providers.tsx
- Verify RainbowKit version compatibility
- Check console for errors

### Base Names Not Resolving
- Ensure connected to Base network
- Check Basenames contract address
- Verify ABI is correct

### Responsive Design Issues
- Check Tailwind configuration
- Test on actual devices
- Use browser dev tools responsive mode

### WebSocket Connection Issues
- Check MAXX bot is running
- Verify WebSocket URL
- Add error handling and reconnection

## Best Practices

1. **Always test on multiple networks**
2. **Check responsive design on mobile**
3. **Update MCP memory after changes**
4. **Use TypeScript for type safety**
5. **Follow existing code patterns**
6. **Test wallet disconnection/reconnection**
7. **Verify Base name resolution works**
8. **Check Three.js performance on mobile**

## Recent Updates Made

- ✅ RainbowKit v2.2.9 migration
- ✅ Multi-network support (6 networks)
- ✅ Base name resolution
- ✅ Responsive design implementation
- ✅ Cyberpunk UI styling
- ✅ MCP memory integration
- ✅ WebSocket real-time data

## Next Planned Updates

- [ ] Enhanced error handling
- [ ] Loading states for wallet operations
- [ ] Advanced trading features
- [ ] Performance optimizations
- [ ] Additional network support
- [ ] Mobile app considerations