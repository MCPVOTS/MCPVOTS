// trade.js - Uniswap V4 trader for MAXX token on Base

require('dotenv').config();
const { ethers } = require('ethers');

// --- CONFIGURATION ---
const { RPC_URL, PRIVATE_KEY, RECIPIENT_ADDRESS } = process.env;

// Contract Addresses on Base
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const MAXX_ADDRESS = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const UNIVERSAL_ROUTER = '0x6fF5693b99212Da76ad316178A184AB56D299b43';
const POOL_MANAGER = '0x498581ff718922c3f8e6a244956af099b2652b2b';
const PERMIT2_ADDRESS = '0x000000000022D473030F116dDEE9F6B43aC78BA3';

// Pool parameters from DexScreener
const POOL_FEE = 3000; // 0.3%
const TICK_SPACING = 60;

// --- SETUP ---
const provider = new ethers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log(`Using wallet: ${wallet.address}`);

// ABI definitions
const ROUTER_ABI = [
    "function execute(bytes calldata commands, bytes[] calldata inputs, uint256 deadline) external payable"
];

const ERC20_ABI = [
    "function approve(address spender, uint256 amount) external returns (bool)",
    "function balanceOf(address account) external view returns (uint256)",
    "function allowance(address owner, address spender) external view returns (uint256)",
    "function decimals() external view returns (uint8)"
];

const PERMIT2_ABI = [
    "function approve(address token, address spender, uint160 amount, uint48 expiration) external"
];

const routerContract = new ethers.Contract(UNIVERSAL_ROUTER, ROUTER_ABI, wallet);
const maxxContract = new ethers.Contract(MAXX_ADDRESS, ERC20_ABI, wallet);
const wethContract = new ethers.Contract(WETH_ADDRESS, ERC20_ABI, wallet);
const permit2Contract = new ethers.Contract(PERMIT2_ADDRESS, PERMIT2_ABI, wallet);

// Helper function to encode pool key
function encodePoolKey() {
    return ethers.solidityPacked(
        ['address', 'address', 'uint24', 'int24', 'address'],
        [WETH_ADDRESS, MAXX_ADDRESS, POOL_FEE, TICK_SPACING, ethers.ZeroAddress]
    );
}

// Optional EIP-1559 gas override
function applyGasOverrides(tx) {
    try {
        const priorityGwei = process.env.PRIORITY_GWEI ?? '0.001';
        const absMaxFeeGwei = process.env.GAS_MAX_FEE_GWEI; // absolute cap if provided
        const feeMult = Number(process.env.MAXFEE_MULT || '101');
        const maxPriority = ethers.parseUnits(priorityGwei, 'gwei');
        tx.type = 2;
        tx.maxPriorityFeePerGas = maxPriority;
        if (absMaxFeeGwei) {
            tx.maxFeePerGas = ethers.parseUnits(absMaxFeeGwei, 'gwei');
        } else {
            // Fallback dynamic cap will be applied by provider if omitted; keep priority set
        }
        console.log(`Gas params -> priority ${ethers.formatUnits(maxPriority,'gwei')} gwei` + (tx.maxFeePerGas ? `, maxFee ${ethers.formatUnits(tx.maxFeePerGas,'gwei')} gwei` : ''));
    } catch {}
}

// --- BUY FUNCTION (ETH -> MAXX) ---
async function buyMaxx(ethAmount) {
    console.log(`\n--- Buying MAXX with ${ethers.formatEther(ethAmount)} ETH ---`);
    try {
        const deadline = Math.floor(Date.now() / 1000) + 1200; // 20 minutes

        // Command sequence: WRAP_ETH (0x0b) + V4_SWAP (0x00)
        const commands = '0x0b00';

        // Encode inputs for WRAP_ETH
        const wrapInput = ethers.AbiCoder.defaultAbiCoder().encode(
            ['address', 'uint256'],
            [UNIVERSAL_ROUTER, ethAmount]
        );

        // Encode V4 swap parameters
        // Using simplified encoding - exact structure may need adjustment
        const swapInput = ethers.AbiCoder.defaultAbiCoder().encode(
            ['address', 'address', 'address', 'uint24', 'uint256', 'uint256', 'uint160'],
            [
                WETH_ADDRESS,     // tokenIn
                MAXX_ADDRESS,     // tokenOut
                RECIPIENT_ADDRESS, // recipient
                POOL_FEE,         // fee
                ethAmount,        // amountIn
                0,                // amountOutMinimum (0 for now, adjust for slippage)
                0                 // sqrtPriceLimitX96 (0 = no limit)
            ]
        );

        const inputs = [wrapInput, swapInput];

        console.log('Sending transaction...');
    const txOpts = { value: ethAmount, gasLimit: 500000 };
    applyGasOverrides(txOpts);
    const tx = await routerContract.execute(commands, inputs, deadline, txOpts);

        console.log(`TX sent: ${tx.hash}`);
        console.log('Waiting for confirmation...');

        const receipt = await tx.wait();
        console.log(`✅ Buy successful! Gas used: ${receipt.gasUsed.toString()}`);

        // Check new balance
        const newBalance = await maxxContract.balanceOf(wallet.address);
        console.log(`New MAXX balance: ${ethers.formatEther(newBalance)} MAXX`);

        return receipt;

    } catch (error) {
        console.error('❌ Buy failed:', error.message);
        if (error.data) {
            console.error('Error data:', error.data);
        }
        throw error;
    }
}

// --- SELL FUNCTION (MAXX -> ETH) ---
async function sellMaxx(maxxAmount) {
    console.log(`\n--- Selling ${ethers.formatEther(maxxAmount)} MAXX for ETH ---`);
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
        const permit2ApproveTx = await permit2Contract.approve(
            MAXX_ADDRESS,
            UNIVERSAL_ROUTER,
            ethers.MaxUint256,
            expiration
        );
        await permit2ApproveTx.wait();
        console.log('✅ Router approved via Permit2');

        // Step 3: Execute V4 swap
        const deadline = Math.floor(Date.now() / 1000) + 1200;

        // Command: V4_SWAP (0x00) + UNWRAP_WETH (0x0c)
        const commands = '0x000c';

        const swapInput = ethers.AbiCoder.defaultAbiCoder().encode(
            ['address', 'address', 'address', 'uint24', 'uint256', 'uint256', 'uint160'],
            [
                MAXX_ADDRESS,     // tokenIn
                WETH_ADDRESS,     // tokenOut
                UNIVERSAL_ROUTER, // recipient (router will unwrap)
                POOL_FEE,         // fee
                maxxAmount,       // amountIn
                0,                // amountOutMinimum
                0                 // sqrtPriceLimitX96
            ]
        );

        const unwrapInput = ethers.AbiCoder.defaultAbiCoder().encode(
            ['address', 'uint256'],
            [RECIPIENT_ADDRESS, 0] // 0 = unwrap all
        );

        const inputs = [swapInput, unwrapInput];

        console.log('Sending sell transaction...');
    const txOpts = { gasLimit: 500000 };
    applyGasOverrides(txOpts);
    const tx = await routerContract.execute(commands, inputs, deadline, txOpts);

        console.log(`TX sent: ${tx.hash}`);
        console.log('Waiting for confirmation...');

        const receipt = await tx.wait();
        console.log(`✅ Sell successful! Gas used: ${receipt.gasUsed.toString()}`);

        // Check balances
        const newMaxxBalance = await maxxContract.balanceOf(wallet.address);
        const newEthBalance = await provider.getBalance(wallet.address);
        console.log(`New MAXX balance: ${ethers.formatEther(newMaxxBalance)} MAXX`);
        console.log(`New ETH balance: ${ethers.formatEther(newEthBalance)} ETH`);

        return receipt;

    } catch (error) {
        console.error('❌ Sell failed:', error.message);
        if (error.data) {
            console.error('Error data:', error.data);
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
        console.log('Current Balances:');
        console.log(`ETH: ${ethers.formatEther(ethBalance)} ETH`);
        console.log(`MAXX: ${ethers.formatEther(maxxBalance)} MAXX`);
        console.log('==========================================');

        // Test with small amount - 0.0001 ETH (~$0.40)
        const ethToSpend = ethers.parseEther('0.0001');

        console.log('\n⚠️  WARNING: This is experimental V4 code!');
        console.log('Starting small test buy...\n');

        await buyMaxx(ethToSpend);

        console.log('\n✅ Test completed successfully!');

    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
        console.error('\nNote: V4 encoding is complex and may need adjustments');
        console.error('Check the Universal Router documentation for exact parameter formats');
    }
})();
