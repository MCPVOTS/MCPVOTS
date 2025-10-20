// trade_v4_sdk.js - Proper Uniswap V4 SDK implementation for MAXX token on Base

require('dotenv').config();
const { ethers } = require('ethers');
const { Actions, V4Planner } = require('@uniswap/v4-sdk');
const { CommandType, RoutePlanner } = require('@uniswap/universal-router-sdk');

// --- CONFIGURATION ---
const { RPC_URL, PRIVATE_KEY, RECIPIENT_ADDRESS } = process.env;

// Contract Addresses on Base
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const MAXX_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const UNIVERSAL_ROUTER = '0x6fF5693b99212Da76ad316178A184AB56D299b43';
const PERMIT2_ADDRESS = '0x000000000022D473030F116dDEE9F6B43aC78BA3';

// IMPORTANT: For V4, native ETH is represented as address(0), not WETH
// The Universal Router handles wrapping automatically
const ETH_ADDRESS = '0x0000000000000000000000000000000000000000';

// Pool parameters from DexScreener
// Note: The actual pool uses WETH, but for swapping with native ETH we use address(0)
const POOL_CONFIG = {
    poolKey: {
        currency0: WETH_ADDRESS,    // Lower address (pool uses WETH)
        currency1: MAXX_ADDRESS,    // Higher address
        fee: 3000,                  // 0.3%
        tickSpacing: 60,
        hooks: ethers.constants.AddressZero  // No hooks for standard pool
    },
    zeroForOne: true // Swapping currency0 (WETH) -> currency1 (MAXX)
};

// --- SETUP ---
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log(`Using wallet: ${wallet.address}`);

// Contract ABIs
const ROUTER_ABI = [
    "function execute(bytes calldata commands, bytes[] calldata inputs, uint256 deadline) external payable"
];

const ERC20_ABI = [
    "function approve(address spender, uint256 amount) external returns (bool)",
    "function balanceOf(address account) external view returns (uint256)",
    "function allowance(address owner, address spender) external view returns (uint256)"
];

const PERMIT2_ABI = [
    "function approve(address token, address spender, uint160 amount, uint48 expiration) external"
];

// Contract instances
const routerContract = new ethers.Contract(UNIVERSAL_ROUTER, ROUTER_ABI, wallet);
const maxxContract = new ethers.Contract(MAXX_ADDRESS, ERC20_ABI, wallet);
const permit2Contract = new ethers.Contract(PERMIT2_ADDRESS, PERMIT2_ABI, wallet);

// --- BUY FUNCTION (ETH -> MAXX) using V4 SDK ---
async function buyMaxx(ethAmount) {
    console.log(`\n--- Buying MAXX with ${ethers.utils.formatEther(ethAmount)} ETH (V4 SDK) ---`);
    try {
        const v4Planner = new V4Planner();
        const routePlanner = new RoutePlanner();
        const deadline = Math.floor(Date.now() / 1000) + 1200;

        console.log('Pool Configuration:');
        console.log('  currency0 (WETH):', POOL_CONFIG.poolKey.currency0);
        console.log('  currency1 (MAXX):', POOL_CONFIG.poolKey.currency1);
        console.log('  fee:', POOL_CONFIG.poolKey.fee);
        console.log('  tickSpacing:', POOL_CONFIG.poolKey.tickSpacing);
        console.log('  hooks:', POOL_CONFIG.poolKey.hooks);
        console.log('  zeroForOne:', POOL_CONFIG.zeroForOne);

        // Configure swap - the SDK should handle this correctly
        const swapConfig = {
            poolKey: POOL_CONFIG.poolKey,
            zeroForOne: POOL_CONFIG.zeroForOne,
            amountIn: ethAmount.toString(),
            amountOutMinimum: '0', // No slippage protection for testing
            hookData: '0x'  // Empty bytes, not '0x00'
        };

        console.log('\nSwap Config:');
        console.log('  amountIn:', ethers.utils.formatEther(ethAmount), 'ETH');
        console.log('  amountOutMinimum: 0 (no slippage protection)');

        // Add V4 actions in the correct sequence
        console.log('\nAdding V4 actions...');
        v4Planner.addAction(Actions.SWAP_EXACT_IN_SINGLE, [swapConfig]);
        v4Planner.addAction(Actions.SETTLE_ALL, [
            POOL_CONFIG.poolKey.currency0,  // Paying in WETH
            ethAmount.toString()
        ]);
        v4Planner.addAction(Actions.TAKE_ALL, [
            POOL_CONFIG.poolKey.currency1,  // Receiving MAXX
            '0'  // Take all output
        ]);

        // Finalize V4 actions
        v4Planner.finalize();

        console.log('V4 actions:', v4Planner.actions);
        console.log('V4 params length:', v4Planner.params.length);

        // Add V4_SWAP command to route planner
        routePlanner.addCommand(CommandType.V4_SWAP, [
            v4Planner.actions,
            v4Planner.params
        ]);

        console.log('\nRoute planner commands:', routePlanner.commands);

        // Transaction options - sending native ETH
        const txOptions = {
            value: ethAmount,
            gasLimit: 500000
        };

        console.log('\nSending transaction...');
        console.log('  value:', ethers.utils.formatEther(ethAmount), 'ETH');
        console.log('  gasLimit:', txOptions.gasLimit);

        const tx = await routerContract.execute(
            routePlanner.commands,
            routePlanner.inputs,  // Use inputs, not raw encodedActions
            deadline,
            txOptions
        );

        console.log(`\nTX sent: ${tx.hash}`);
        console.log('Waiting for confirmation...');

        const receipt = await tx.wait();
        console.log(`✅ Buy successful! Gas used: ${receipt.gasUsed.toString()}`);

        // Check new balance
        const newBalance = await maxxContract.balanceOf(wallet.address);
        console.log(`New MAXX balance: ${ethers.utils.formatEther(newBalance)} MAXX`);

        return receipt;

    } catch (error) {
        console.error('\n❌ Buy failed:', error.message);
        if (error.receipt) {
            console.error('Transaction failed on-chain');
            console.error('TX hash:', error.receipt.hash);
        }
        if (error.data) {
            console.error('Error data:', error.data);
        }
        if (error.transaction) {
            console.error('Transaction data:', error.transaction.data);
        }
        throw error;
    }
}

// --- SELL FUNCTION (MAXX -> ETH) using V4 SDK ---
async function sellMaxx(maxxAmount) {
    console.log(`\n--- Selling ${ethers.utils.formatEther(maxxAmount)} MAXX for ETH (V4 SDK) ---`);
    try {
        // Step 1: Approve Permit2 if needed
        const permit2Allowance = await maxxContract.allowance(wallet.address, PERMIT2_ADDRESS);
        if (permit2Allowance < maxxAmount) {
            console.log('Approving Permit2...');
            const approveTx = await maxxContract.approve(PERMIT2_ADDRESS, ethers.MaxUint256);
            await approveTx.wait();
            console.log('✅ Permit2 approved');
        }

        // Step 2: Approve Universal Router via Permit2
        console.log('Approving Universal Router via Permit2...');
        const expiration = Math.floor(Date.now() / 1000) + 3600; // 1 hour
        const maxUint160 = ethers.BigNumber.from(2).pow(160).sub(1);

        const permit2ApproveTx = await permit2Contract.approve(
            MAXX_ADDRESS,
            UNIVERSAL_ROUTER,
            maxUint160,
            expiration
        );
        await permit2ApproveTx.wait();
        console.log('✅ Router approved via Permit2');        // Step 3: Execute V4 swap
        const v4Planner = new V4Planner();
        const routePlanner = new RoutePlanner();
        const deadline = Math.floor(Date.now() / 1000) + 1200;

        // Sell config (reverse direction)
        const swapConfig = {
            poolKey: POOL_CONFIG.poolKey,
            zeroForOne: false, // MAXX (currency1) -> WETH (currency0)
            amountIn: maxxAmount.toString(),
            amountOutMinimum: '0',
            hookData: '0x00'
        };

        v4Planner.addAction(Actions.SWAP_EXACT_IN_SINGLE, [swapConfig]);
        v4Planner.addAction(Actions.SETTLE_ALL, [
            POOL_CONFIG.poolKey.currency1, // MAXX in
            swapConfig.amountIn
        ]);
        v4Planner.addAction(Actions.TAKE_ALL, [
            POOL_CONFIG.poolKey.currency0, // WETH out
            swapConfig.amountOutMinimum
        ]);

        const encodedActions = v4Planner.finalize();
        routePlanner.addCommand(CommandType.V4_SWAP, [
            v4Planner.actions,
            v4Planner.params
        ]);

        console.log('Sending sell transaction...');
        const tx = await routerContract.execute(
            routePlanner.commands,
            [encodedActions],
            deadline,
            { gasLimit: 500000 }
        );

        console.log(`TX sent: ${tx.hash}`);
        console.log('Waiting for confirmation...');

        const receipt = await tx.wait();
        console.log(`✅ Sell successful! Gas used: ${receipt.gasUsed.toString()}`);

        // Check balances
        const newMaxxBalance = await maxxContract.balanceOf(wallet.address);
        const newEthBalance = await provider.getBalance(wallet.address);
        console.log(`New MAXX balance: ${ethers.utils.formatEther(newMaxxBalance)} MAXX`);
        console.log(`New ETH balance: ${ethers.utils.formatEther(newEthBalance)} ETH`);

        return receipt;    } catch (error) {
        console.error('❌ Sell failed:', error.message);
        if (error.receipt) {
            console.error('Transaction failed on-chain');
            console.error('TX hash:', error.receipt.hash);
        }
        throw error;
    }
}

// --- MAIN EXECUTION ---
(async () => {
    try {
        const ethBalance = await provider.getBalance(wallet.address);
        const maxxBalance = await maxxContract.balanceOf(wallet.address);

        console.log('\n==========================================');
        console.log('UNISWAP V4 SDK - MAXX TRADER');
        console.log('==========================================');
        console.log('Pool:', POOL_CONFIG.poolKey.currency0, '/', POOL_CONFIG.poolKey.currency1);
        console.log('Fee:', POOL_CONFIG.poolKey.fee / 10000, '%');
        console.log('\nCurrent Balances:');
        console.log(`  ETH: ${ethers.utils.formatEther(ethBalance)} ETH`);
        console.log(`  MAXX: ${ethers.utils.formatEther(maxxBalance)} MAXX`);
        console.log('==========================================\n');

        // Test with 0.0001 ETH (~$0.40)
        const ethToSpend = ethers.utils.parseEther('0.0001');        console.log('Starting V4 SDK swap test...');
        await buyMaxx(ethToSpend);

        console.log('\n✅ V4 SDK test completed!');
        console.log('Check transaction on BaseScan to verify');

    } catch (error) {
        console.error('\n❌ V4 SDK test failed:', error.message);
        console.error('\nTroubleshooting:');
        console.error('1. Verify Universal Router address for Base chain');
        console.error('2. Check pool exists and has liquidity');
        console.error('3. Ensure wallet has enough ETH for gas');
    }
})();
