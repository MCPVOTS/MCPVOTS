// verify_v4_pool.js - Check if the V4 pool actually exists on-chain

require('dotenv').config();
const { ethers } = require('ethers');

const { RPC_URL } = process.env;
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);

// Contract addresses
const POOL_MANAGER = '0x498581ff718922c3f8e6a244956af099b2652b2b';
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const MAXX_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';

// PoolManager ABI (minimal - just what we need)
const POOL_MANAGER_ABI = [
    "function getSlot0(bytes32 poolId) external view returns (uint160 sqrtPriceX96, int24 tick, uint24 protocolFee, uint24 lpFee)",
    "function getLiquidity(bytes32 poolId) external view returns (uint128 liquidity)",
    "function getPoolTickSpacing(bytes32 poolId) external view returns (int24 tickSpacing)"
];

const poolManager = new ethers.Contract(POOL_MANAGER, POOL_MANAGER_ABI, provider);

// Pool ID from DexScreener
const POOL_ID = '0x11bb2563a35b46d4086eec991dd5f374d8122a69e7998da1706454d4ee298148';

(async () => {
    try {
        console.log('==========================================');
        console.log('V4 POOL VERIFICATION');
        console.log('==========================================\n');

        console.log('Pool ID:', POOL_ID);
        console.log('PoolManager:', POOL_MANAGER);
        console.log('\nQuerying pool state...\n');

        try {
            const slot0 = await poolManager.getSlot0(POOL_ID);
            console.log('✅ Pool EXISTS!');
            console.log('Slot0 data:');
            console.log('  sqrtPriceX96:', slot0.sqrtPriceX96.toString());
            console.log('  tick:', slot0.tick);
            console.log('  protocolFee:', slot0.protocolFee);
            console.log('  lpFee:', slot0.lpFee);
        } catch (error) {
            console.log('❌ Pool does NOT exist or getSlot0 failed');
            console.log('Error:', error.message);
        }

        try {
            const liquidity = await poolManager.getLiquidity(POOL_ID);
            console.log('\n✅ Liquidity query successful');
            console.log('Liquidity:', liquidity.toString());
        } catch (error) {
            console.log('\n❌ getLiquidity failed');
            console.log('Error:', error.message);
        }

        // Alternative: try to compute the pool ID from the pool key
        console.log('\n==========================================');
        console.log('ATTEMPTING TO COMPUTE POOL ID');
        console.log('==========================================\n');

        // PoolKey struct: currency0, currency1, fee, tickSpacing, hooks
        const fee = 3000;
        const tickSpacing = 60;
        const hooks = ethers.constants.AddressZero;

        console.log('Pool Key components:');
        console.log('  currency0:', WETH_ADDRESS);
        console.log('  currency1:', MAXX_ADDRESS);
        console.log('  fee:', fee);
        console.log('  tickSpacing:', tickSpacing);
        console.log('  hooks:', hooks);

        // Encode the pool key
        const encoded = ethers.utils.defaultAbiCoder.encode(
            ['address', 'address', 'uint24', 'int24', 'address'],
            [WETH_ADDRESS, MAXX_ADDRESS, fee, tickSpacing, hooks]
        );

        // Hash it to get the pool ID
        const computedPoolId = ethers.utils.keccak256(encoded);

        console.log('\nComputed Pool ID:', computedPoolId);
        console.log('DexScreener Pool ID:', POOL_ID);
        console.log('Match:', computedPoolId.toLowerCase() === POOL_ID.toLowerCase() ? '✅ YES' : '❌ NO');

        if (computedPoolId.toLowerCase() !== POOL_ID.toLowerCase()) {
            console.log('\n⚠️  WARNING: Pool IDs do NOT match!');
            console.log('This suggests DexScreener data may be incorrect or this is not a V4 pool.');
        }

    } catch (error) {
        console.error('\n❌ Verification failed:', error.message);
    }
})();
