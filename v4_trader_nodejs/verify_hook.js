const ethers = require('ethers');
require('dotenv').config();

const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL || 'https://mainnet.base.org');

const HOOK_ADDRESS = '0xB7f5BF799fB265657c628ef4a13f90f83a3a616A';
const WETH = '0x4200000000000000000000000000000000000006';
const MAXX = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const DEXSCREENER_POOL_ID = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148';

async function verifyHook() {
    console.log('🔍 VERIFYING CUSTOM HOOK ADDRESS\n');
    console.log('Hook Address:', HOOK_ADDRESS);

    // Check if it's a contract
    const code = await provider.getCode(HOOK_ADDRESS);
    console.log('Is Contract:', code !== '0x');
    console.log('Code Length:', code.length, 'bytes\n');

    // Get some transaction history
    const txCount = await provider.getTransactionCount(HOOK_ADDRESS);
    console.log('Transaction Count:', txCount);

    // Check balance
    const balance = await provider.getBalance(HOOK_ADDRESS);
    console.log('ETH Balance:', ethers.utils.formatEther(balance), 'ETH\n');

    // Try different fee tiers
    const feeTiers = [
        { fee: 100, tickSpacing: 1 },
        { fee: 500, tickSpacing: 10 },
        { fee: 3000, tickSpacing: 60 },
        { fee: 10000, tickSpacing: 200 }
    ];

    console.log('🎯 Computing Pool IDs with custom hook:\n');

    let matchFound = false;

    for (const tier of feeTiers) {
        const poolKeyEncoded = ethers.utils.defaultAbiCoder.encode(
            ['address', 'address', 'uint24', 'int24', 'address'],
            [WETH, MAXX, tier.fee, tier.tickSpacing, HOOK_ADDRESS]
        );

        const poolId = ethers.utils.keccak256(poolKeyEncoded);
        const matches = poolId.toLowerCase() === DEXSCREENER_POOL_ID.toLowerCase();

        console.log(`Fee: ${tier.fee} (tickSpacing: ${tier.tickSpacing})`);
        console.log(`Pool ID: ${poolId}`);

        if (matches) {
            console.log('🎉 *** MATCH FOUND! THIS IS THE CORRECT POOL CONFIGURATION! ***\n');
            matchFound = true;
        } else {
            console.log('');
        }
    }

    console.log('DexScreener Pool ID:', DEXSCREENER_POOL_ID);

    if (matchFound) {
        console.log('\n✅ SUCCESS! We found the exact pool configuration!');
    } else {
        console.log('\n❌ No match found. Trying more fee tiers or different parameters may be needed.');
    }
}

verifyHook().catch(console.error);
