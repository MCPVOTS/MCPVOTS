const ethers = require('ethers');

const provider = new ethers.providers.JsonRpcProvider('https://mainnet.base.org');

const POOL_MANAGER = '0x498581ff718922c3f8e6a244956af099b2652b2b';
const MAXX_TOKEN = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const WETH = '0x4200000000000000000000000000000000000006';

// Initialize event signature: Initialize(bytes32 indexed id, Currency indexed currency0, Currency indexed currency1, uint24 fee, int24 tickSpacing, IHooks hooks, uint160 sqrtPriceX96, int24 tick)
const INITIALIZE_EVENT = '0x98636036cb66a9c19a37435efc1e90142190214e8abeb821bdba3f2990dd4c95';

async function findMaxxPool() {
    console.log('🔍 Searching for MAXX V4 pool initialization...\n');

    const latestBlock = await provider.getBlockNumber();
    console.log('Latest block:', latestBlock);

    // MAXX token was created around 134 days ago based on earlier research
    // Estimate: ~7200 blocks per day on Base, so 134 days = ~967,000 blocks ago
    const estimatedCreationBlock = latestBlock - 1000000;
    console.log('Searching from block:', estimatedCreationBlock, '\n');

    // Search in chunks to avoid rate limits
    const chunkSize = 10000;

    for (let startBlock = estimatedCreationBlock; startBlock < latestBlock; startBlock += chunkSize) {
        const endBlock = Math.min(startBlock + chunkSize - 1, latestBlock);

        console.log(`Searching blocks ${startBlock} to ${endBlock}...`);

        try {
            const logs = await provider.getLogs({
                address: POOL_MANAGER,
                topics: [INITIALIZE_EVENT],
                fromBlock: startBlock,
                toBlock: endBlock
            });

            if (logs.length > 0) {
                console.log(`Found ${logs.length} Initialize events`);

                for (const log of logs) {
                    // Decode the event
                    const poolId = log.topics[1];
                    const currency0 = '0x' + log.topics[2].substring(26);
                    const currency1 = '0x' + log.topics[3].substring(26);

                    // Check if this is a MAXX pool
                    if (
                        (currency0.toLowerCase() === MAXX_TOKEN.toLowerCase() ||
                         currency1.toLowerCase() === MAXX_TOKEN.toLowerCase()) &&
                        (currency0.toLowerCase() === WETH.toLowerCase() ||
                         currency1.toLowerCase() === WETH.toLowerCase())
                    ) {
                        console.log('\n🎯 FOUND MAXX/WETH V4 POOL!');
                        console.log('=====================================');
                        console.log('Pool ID:', poolId);
                        console.log('Currency0:', currency0);
                        console.log('Currency1:', currency1);
                        console.log('Block:', log.blockNumber);
                        console.log('TX Hash:', log.transactionHash);

                        // Decode the rest of the data
                        const data = log.data;
                        const fee = ethers.BigNumber.from('0x' + data.substring(2, 8)).toNumber();
                        const tickSpacing = ethers.BigNumber.from('0x' + data.substring(8, 14)).toNumber();
                        const hooks = '0x' + data.substring(26, 66);

                        console.log('Fee:', fee);
                        console.log('TickSpacing:', tickSpacing);
                        console.log('Hooks:', hooks);
                        console.log('=====================================\n');

                        return {
                            poolId,
                            currency0,
                            currency1,
                            fee,
                            tickSpacing,
                            hooks,
                            block: log.blockNumber,
                            txHash: log.transactionHash
                        };
                    }
                }
            }

            // Add delay to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 200));

        } catch (error) {
            console.error(`Error searching blocks ${startBlock}-${endBlock}:`, error.message);
            // Continue with next chunk
        }
    }

    console.log('\n❌ No MAXX/WETH V4 pool found in the searched range');
}

findMaxxPool()
    .then(result => {
        if (result) {
            console.log('✅ Search complete! Pool found.');
        } else {
            console.log('⚠️  Search complete. No pool found.');
        }
    })
    .catch(error => {
        console.error('Fatal error:', error);
    });
