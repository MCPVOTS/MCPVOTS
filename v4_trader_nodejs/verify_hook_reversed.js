const ethers = require('ethers');
require('dotenv').config();

const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL || 'https://mainnet.base.org');

const HOOK_ADDRESS = '0xB7f5BF799fB265657c628ef4a13f90f83a3a616A';
const WETH = '0x4200000000000000000000000000000000000006';
const MAXX = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const DEXSCREENER_POOL_ID = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148';

async function verifyHookAllCombinations() {
    console.log('🔍 TRYING ALL TOKEN ORDER & FEE COMBINATIONS\n');
    console.log('Hook Address:', HOOK_ADDRESS);
    console.log('Target Pool ID:', DEXSCREENER_POOL_ID, '\n');

    // Check hook contract
    const code = await provider.getCode(HOOK_ADDRESS);
    console.log('Hook Contract Verified:', code !== '0x', `(${code.length} bytes)\n`);

    // Try different fee tiers with extended options
    const feeTiers = [
        { fee: 100, tickSpacing: 1 },
        { fee: 500, tickSpacing: 10 },
        { fee: 3000, tickSpacing: 60 },
        { fee: 10000, tickSpacing: 200 },
        // Also try some non-standard combinations
        { fee: 2500, tickSpacing: 50 },
        { fee: 5000, tickSpacing: 100 },
    ];

    // Try both token orders
    const tokenOrders = [
        { name: 'WETH/MAXX', currency0: WETH, currency1: MAXX },
        { name: 'MAXX/WETH', currency0: MAXX, currency1: WETH }
    ];

    let matchFound = false;
    let matchConfig = null;

    for (const order of tokenOrders) {
        console.log(`\n📊 Testing ${order.name} order:\n`);

        for (const tier of feeTiers) {
            const poolKeyEncoded = ethers.utils.defaultAbiCoder.encode(
                ['address', 'address', 'uint24', 'int24', 'address'],
                [order.currency0, order.currency1, tier.fee, tier.tickSpacing, HOOK_ADDRESS]
            );

            const poolId = ethers.utils.keccak256(poolKeyEncoded);
            const matches = poolId.toLowerCase() === DEXSCREENER_POOL_ID.toLowerCase();

            console.log(`  Fee: ${tier.fee} (tick: ${tier.tickSpacing}) => ${poolId.substring(0, 20)}...`);

            if (matches) {
                console.log('  🎉 *** PERFECT MATCH! ***\n');
                matchFound = true;
                matchConfig = { order: order.name, ...tier };
            }
        }
    }

    if (matchFound) {
        console.log('\n✅ SUCCESS! Pool configuration found:');
        console.log(JSON.stringify(matchConfig, null, 2));
    } else {
        console.log('\n❌ No match found with standard configurations.');
        console.log('\nNext steps:');
        console.log('1. Check if DexScreener Pool ID is actually from a different chain');
        console.log('2. Query PoolManager Initialize events to get exact parameters');
        console.log('3. The hook might use dynamic fee (fee = 0x800000)');
    }
}

verifyHookAllCombinations().catch(console.error);
