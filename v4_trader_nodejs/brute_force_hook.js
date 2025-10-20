// brute_force_hook.js - Try to find the hook address by testing common addresses

require('dotenv').config();
const { ethers } = require('ethers');

const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const MAXX_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const TARGET_POOL_ID = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148';

const fee = 3000;
const tickSpacing = 60;

// Common hook addresses to try
const COMMON_HOOKS = [
    '0x0000000000000000000000000000000000000000', // Zero address (we already know this doesn't work)
    '0x0000000000000000000000000000000000000001', // Common placeholder
    // Add more if needed
];

function computePoolId(currency0, currency1, fee, tickSpacing, hooks) {
    const encoded = ethers.utils.defaultAbiCoder.encode(
        ['address', 'address', 'uint24', 'int24', 'address'],
        [currency0, currency1, fee, tickSpacing, hooks]
    );
    return ethers.utils.keccak256(encoded);
}

console.log('==========================================');
console.log('BRUTE FORCE HOOK ADDRESS SEARCH');
console.log('==========================================\n');
console.log('Target Pool ID:', TARGET_POOL_ID);
console.log('\nTrying common hook addresses...\n');

// Try common hooks
for (const hook of COMMON_HOOKS) {
    const computedId = computePoolId(WETH_ADDRESS, MAXX_ADDRESS, fee, tickSpacing, hook);
    const match = computedId.toLowerCase() === TARGET_POOL_ID.toLowerCase();

    console.log(`Hook: ${hook}`);
    console.log(`  Computed ID: ${computedId}`);
    console.log(`  Match: ${match ? '✅ YES!' : '❌ No'}`);
    console.log('');

    if (match) {
        console.log('==========================================');
        console.log('🎯 HOOK ADDRESS FOUND!');
        console.log('==========================================');
        console.log('Use this in your trade_v4_sdk.js:');
        console.log(`hooks: '${hook}'`);
        process.exit(0);
    }
}

console.log('==========================================');
console.log('⚠️  NOT FOUND IN COMMON ADDRESSES');
console.log('==========================================');
console.log('\nThe hook must be a custom contract address.');
console.log('We need to find it by:');
console.log('1. Checking BaseScan transaction logs for the Initialize event');
console.log('2. Looking at the DexScreener pool page for more details');
console.log('3. Querying the PoolManager contract directly (if RPC allows)');
console.log('\nLet me try one more thing - maybe the tokens are in reverse order...\n');

// Try with reversed token order
console.log('Trying with reversed token order (MAXX, WETH)...\n');
const computedIdReversed = computePoolId(MAXX_ADDRESS, WETH_ADDRESS, fee, tickSpacing, '0x0000000000000000000000000000000000000000');
console.log(`Computed ID (reversed): ${computedIdReversed}`);
console.log(`Match: ${computedIdReversed.toLowerCase() === TARGET_POOL_ID.toLowerCase() ? '✅ YES!' : '❌ No'}`);

if (computedIdReversed.toLowerCase() === TARGET_POOL_ID.toLowerCase()) {
    console.log('\n⚠️  WARNING: Tokens are in wrong order!');
    console.log('currency0 should be MAXX, currency1 should be WETH');
    console.log('This is unusual but possible.');
}
