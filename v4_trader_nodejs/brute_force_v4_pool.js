require('dotenv').config();
const { ethers } = require('ethers');

const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);

// Contracts
const POOL_MANAGER = '0x498581ff718922c3f8e6a244956af099b2652b2b';
const WETH = '0x4200000000000000000000000000000000000006';
const MAXX = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';

// Known potential hook addresses
const HOOK_ADDRESSES = [
    '0x0000000000000000000000000000000000000000', // No hook
    '0xB7f5BF799fB265657c628ef4a13f90f83a3a616A', // Hook from CSV analysis
];

// Standard V4 fee tiers
const FEE_TIERS = [
    { fee: 100, tickSpacing: 1, name: '0.01%' },
    { fee: 500, tickSpacing: 10, name: '0.05%' },
    { fee: 3000, tickSpacing: 60, name: '0.3%' },
    { fee: 10000, tickSpacing: 200, name: '1%' },
];

// PoolManager ABI for querying
const poolManagerABI = [
    'function getSlot0(bytes32 id) external view returns (uint160 sqrtPriceX96, int24 tick, uint24 protocolFee, uint24 lpFee)',
    'function getLiquidity(bytes32 id) external view returns (uint128 liquidity)',
];

const poolManager = new ethers.Contract(POOL_MANAGER, poolManagerABI, provider);

// Function to compute Pool ID from PoolKey
function computePoolId(currency0, currency1, fee, tickSpacing, hooks) {
    const poolKeyEncoded = ethers.utils.defaultAbiCoder.encode(
        ['address', 'address', 'uint24', 'int24', 'address'],
        [currency0, currency1, fee, tickSpacing, hooks]
    );
    return ethers.utils.keccak256(poolKeyEncoded);
}

// Function to check if a pool exists
async function checkPool(currency0, currency1, fee, tickSpacing, hooks, description) {
    const poolId = computePoolId(currency0, currency1, fee, tickSpacing, hooks);

    try {
        // Try to get pool data
        const slot0 = await poolManager.getSlot0(poolId);
        const liquidity = await poolManager.getLiquidity(poolId);

        // If we get here, pool exists!
        console.log('\n🎉 ===== POOL FOUND! ===== 🎉');
        console.log(`Description: ${description}`);
        console.log(`Pool ID: ${poolId}`);
        console.log('\nPoolKey Configuration:');
        console.log(`  currency0: ${currency0}`);
        console.log(`  currency1: ${currency1}`);
        console.log(`  fee: ${fee}`);
        console.log(`  tickSpacing: ${tickSpacing}`);
        console.log(`  hooks: ${hooks}`);
        console.log('\nPool State:');
        console.log(`  sqrtPriceX96: ${slot0.sqrtPriceX96.toString()}`);
        console.log(`  tick: ${slot0.tick}`);
        console.log(`  protocolFee: ${slot0.protocolFee}`);
        console.log(`  lpFee: ${slot0.lpFee}`);
        console.log(`  liquidity: ${liquidity.toString()}`);
        console.log('\n========================\n');

        return {
            found: true,
            poolId,
            currency0,
            currency1,
            fee,
            tickSpacing,
            hooks,
            slot0,
            liquidity
        };
    } catch (error) {
        // Pool doesn't exist or error querying
        console.log(`❌ ${description}: Pool not found`);
        return { found: false };
    }
}

async function bruteForceSearch() {
    console.log('🔍 BRUTE FORCE V4 POOL SEARCH FOR MAXX/WETH\n');
    console.log('Testing all combinations of:');
    console.log(`- Fee tiers: ${FEE_TIERS.map(t => t.name).join(', ')}`);
    console.log(`- Hook addresses: ${HOOK_ADDRESSES.length} candidates`);
    console.log(`- Token orderings: WETH/MAXX and MAXX/WETH`);
    console.log(`\nTotal configurations to test: ${FEE_TIERS.length * HOOK_ADDRESSES.length * 2}\n`);
    console.log('Starting search...\n');

    const results = [];
    let tested = 0;

    // Try both token orderings
    const orderings = [
        { curr0: WETH, curr1: MAXX, name: 'WETH/MAXX' },
        { curr0: MAXX, curr1: WETH, name: 'MAXX/WETH' },
    ];

    for (const ordering of orderings) {
        console.log(`\n=== Testing ${ordering.name} ordering ===\n`);

        for (const tier of FEE_TIERS) {
            for (const hook of HOOK_ADDRESSES) {
                tested++;
                const hookLabel = hook === ethers.constants.AddressZero ? 'No Hook' : `Hook ${hook.slice(0, 10)}...`;
                const description = `${ordering.name} | Fee: ${tier.name} | ${hookLabel}`;

                const result = await checkPool(
                    ordering.curr0,
                    ordering.curr1,
                    tier.fee,
                    tier.tickSpacing,
                    hook,
                    description
                );

                if (result.found) {
                    results.push(result);
                }

                // Small delay to avoid rate limiting
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
    }

    console.log('\n' + '='.repeat(60));
    console.log('SEARCH COMPLETE');
    console.log('='.repeat(60));
    console.log(`Total configurations tested: ${tested}`);
    console.log(`Pools found: ${results.length}`);

    if (results.length === 0) {
        console.log('\n❌ NO POOLS FOUND');
        console.log('\nThis could mean:');
        console.log('1. The hook address is different from our candidates');
        console.log('2. The pool uses a non-standard fee tier');
        console.log('3. The pool is using a custom implementation');
        console.log('\nNext steps:');
        console.log('- Search PoolManager Initialize events for MAXX');
        console.log('- Analyze recent MAXX transactions for V4 patterns');
        console.log('- Check if PoolManager balance is from liquidity provision, not swaps');
    } else {
        console.log('\n✅ FOUND WORKING POOL(S)!');
        console.log('\nYou can now use these exact parameters in your V4 swap script.');
        console.log('\nSave this configuration to trade_v4_sdk.js:');
        results.forEach((r, i) => {
            console.log(`\n--- Pool ${i + 1} ---`);
            console.log(`currency0: '${r.currency0}',`);
            console.log(`currency1: '${r.currency1}',`);
            console.log(`fee: ${r.fee},`);
            console.log(`tickSpacing: ${r.tickSpacing},`);
            console.log(`hooks: '${r.hooks}'`);
        });
    }

    return results;
}

// Run the search
bruteForceSearch()
    .then(results => {
        console.log('\n✅ Script completed successfully');
        process.exit(results.length > 0 ? 0 : 1);
    })
    .catch(error => {
        console.error('\n❌ Error:', error.message);
        process.exit(1);
    });
