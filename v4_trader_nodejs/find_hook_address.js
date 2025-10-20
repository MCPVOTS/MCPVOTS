// find_hook_address.js - Search for the MAXX pool creation to find the hook address

require('dotenv').config();
const { ethers } = require('ethers');

const { RPC_URL } = process.env;
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);

// Contract addresses
const POOL_MANAGER = '0x498581ff718922c3f8e6a244956af099b2652b2b';
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const MAXX_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';

// PoolManager ABI - Initialize event
const POOL_MANAGER_ABI = [
    "event Initialize(bytes32 indexed id, address indexed currency0, address indexed currency1, uint24 fee, int24 tickSpacing, address hooks, uint160 sqrtPriceX96, int24 tick)"
];

const poolManager = new ethers.Contract(POOL_MANAGER, POOL_MANAGER_ABI, provider);

// Known pool ID from DexScreener
const POOL_ID = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148';

(async () => {
    try {
        console.log('==========================================');
        console.log('SEARCHING FOR MAXX POOL CREATION');
        console.log('==========================================\n');

        console.log('Target Pool ID:', POOL_ID);
        console.log('WETH Address:', WETH_ADDRESS);
        console.log('MAXX Address:', MAXX_ADDRESS);
        console.log('\nSearching Initialize events...\n');

        // Get current block
        const currentBlock = await provider.getBlockNumber();
        console.log('Current block:', currentBlock);

        // Search back only 10k blocks (approximately 3 days on Base) to avoid rate limits
        const fromBlock = currentBlock - 10000;
        console.log('Searching from block:', fromBlock);
        console.log('(Searching recent blocks first...)\n');        // Query Initialize events
        const filter = poolManager.filters.Initialize();
        const events = await poolManager.queryFilter(filter, fromBlock, currentBlock);

        console.log(`Found ${events.length} Initialize events\n`);

        // Look for our pool
        for (const event of events) {
            const { id, currency0, currency1, fee, tickSpacing, hooks, sqrtPriceX96, tick } = event.args;

            // Check if this is MAXX/WETH pool
            const isMaxxPool = (
                (currency0.toLowerCase() === WETH_ADDRESS.toLowerCase() &&
                 currency1.toLowerCase() === MAXX_ADDRESS.toLowerCase()) ||
                (currency0.toLowerCase() === MAXX_ADDRESS.toLowerCase() &&
                 currency1.toLowerCase() === WETH_ADDRESS.toLowerCase())
            );

            if (isMaxxPool) {
                console.log('==========================================');
                console.log('✅ FOUND MAXX POOL!');
                console.log('==========================================');
                console.log('Block:', event.blockNumber);
                console.log('TX Hash:', event.transactionHash);
                console.log('\nPool Details:');
                console.log('  Pool ID:', id);
                console.log('  currency0:', currency0);
                console.log('  currency1:', currency1);
                console.log('  fee:', fee);
                console.log('  tickSpacing:', tickSpacing);
                console.log('  hooks:', hooks);
                console.log('  sqrtPriceX96:', sqrtPriceX96.toString());
                console.log('  tick:', tick);

                // Check if this matches our target
                if (id.toLowerCase() === POOL_ID.toLowerCase()) {
                    console.log('\n🎯 This is THE pool from DexScreener!');
                    console.log('\n==========================================');
                    console.log('HOOK ADDRESS FOUND:');
                    console.log('==========================================');
                    console.log(hooks);
                    console.log('\n⚠️  Use this address in your trade_v4_sdk.js');
                    console.log('Update POOL_CONFIG.poolKey.hooks to:', hooks);
                } else {
                    console.log('\n⚠️  Different MAXX pool (different parameters)');
                }
                console.log('\n');
            }
        }

        console.log('Search complete!');

    } catch (error) {
        console.error('\n❌ Search failed:', error.message);
        console.error('\nTrying alternative approach...');

        // Alternative: search with specific pool ID filter
        try {
            console.log('\nSearching for specific Pool ID events...');
            const idFilter = poolManager.filters.Initialize(POOL_ID);
            const events = await poolManager.queryFilter(idFilter, currentBlock - 500000, currentBlock);

            if (events.length > 0) {
                const event = events[0];
                console.log('\n✅ Found pool via ID filter!');
                console.log('TX Hash:', event.transactionHash);
                console.log('Hook address:', event.args.hooks);
            } else {
                console.log('❌ No events found for this Pool ID');
                console.log('\nThe pool might be older than our search range,');
                console.log('or DexScreener data might be incorrect.');
            }
        } catch (err) {
            console.error('Alternative search also failed:', err.message);
        }
    }
})();
