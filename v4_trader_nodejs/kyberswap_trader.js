require('dotenv').config();
const ethers = require('ethers');
const https = require('https');

// Configuration
const CHAIN = 'base';
const KYBERSWAP_ROUTER = '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5';
const CLIENT_ID = 'MAXXTrader';

const WETH = '0x4200000000000000000000000000000000000006';
const MAXX = '0xFB7a83abe4F4A4E51c77B92E521390B769ff6467';
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'; // Native ETH for KyberSwap

// Setup provider and wallet
const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

console.log('🔧 KyberSwap MAXX Trader');
console.log('========================\n');
console.log('Wallet:', wallet.address);
console.log('Chain:', CHAIN);
console.log('Router:', KYBERSWAP_ROUTER);
console.log('');

function printRouteExchanges(routeSummary) {
    try {
        const routes = routeSummary && routeSummary.route;
        if (!routes || !Array.isArray(routes)) return;
        const hops = [];
        for (const path of routes) {
            for (const hop of path) {
                const ex = hop.exchange || hop.poolType || 'unknown';
                const pool = hop.pool || 'n/a';
                hops.push(`${ex}:${pool.substring(0,10)}…`);
            }
        }
        if (hops.length) console.log('  Route:', hops.join(' -> '));
    } catch {}
}

function toNumber(val, def = 0) {
    const n = Number(val);
    return Number.isFinite(n) ? n : def;
}

async function estimateFeeEth(txReq, gasLimitOverride) {
    let gas;
    try {
        gas = gasLimitOverride || (await provider.estimateGas(txReq));
    } catch {
        gas = gasLimitOverride || ethers.BigNumber.from(300000);
    }
    let maxFeePerGas;
    try {
        if (txReq.maxFeePerGas) maxFeePerGas = txReq.maxFeePerGas;
        else {
            const latest = await provider.getBlock('latest');
            const base = latest.baseFeePerGas || (await provider.getFeeData()).gasPrice;
            const prio = ethers.utils.parseUnits(process.env.PRIORITY_GWEI || '0', 'gwei');
            maxFeePerGas = base ? base.mul(toNumber(process.env.MAXFEE_MULT || '105')).div(100).add(prio) : prio;
        }
    } catch {
        maxFeePerGas = ethers.utils.parseUnits('0.05', 'gwei');
    }
    const fee = gas.mul(maxFeePerGas);
    return { gas, maxFeePerGas, feeEth: parseFloat(ethers.utils.formatEther(fee)) };
}

/**
 * Make HTTP request to KyberSwap API
 */
function apiRequest(path, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'aggregator-api.kyberswap.com',
            path: path,
            method: method,
            headers: {
                'X-Client-Id': CLIENT_ID,
                'Accept': 'application/json',
                // Try to appease Cloudflare by mimicking a browser
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                'Origin': 'https://kyberswap.com',
                'Referer': 'https://kyberswap.com/'
            }
        };

        if (body) {
            options.headers['Content-Type'] = 'application/json';
        }

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(new Error('Failed to parse response: ' + data));
                }
            });
        });

        req.on('error', reject);

        if (body) {
            req.write(JSON.stringify(body));
        }

        req.end();
    });
}

/**
 * Get swap route from KyberSwap
 */
async function getSwapRoute(tokenIn, tokenOut, amountIn, slippageTolerance = 50, opts = {}) {
    const params = new URLSearchParams({
        tokenIn: tokenIn,
        tokenOut: tokenOut,
        amountIn: amountIn,
        gasInclude: 'true',
        slippageTolerance: slippageTolerance.toString() // 50 = 0.5%
    });

    if (opts.v4Only) {
        params.set('includedSources', 'uniswapv4');
    }
    if (opts.singlePath) {
        params.set('onlySinglePath', 'true');
    }
    if (opts.directPools) {
        params.set('onlyDirectPools', 'true');
    }
    if (opts.excludeRFQ) {
        params.set('excludeRFQSources', 'true');
    }

    const path = `/${CHAIN}/api/v1/routes?${params.toString()}`;

    console.log('📊 Getting swap route from KyberSwap...');
    try {
        const response = await apiRequest(path);
        if (response.code !== 0) {
            throw new Error(`KyberSwap API error: ${response.message}`);
        }
        return response.data;
    } catch (err) {
        // Surface for caller to try legacy fallback
        err.__kyber_v1_failed = true;
        throw err;
    }
}

/**
 * Build transaction data for swap
 */
async function buildSwapTransaction(routeSummary, sender, recipient, slippageTolerance = 50) {
    const path = `/${CHAIN}/api/v1/route/build`;

    const body = {
        routeSummary: routeSummary,
        sender: sender,
        recipient: recipient,
        slippageTolerance: slippageTolerance,
        source: CLIENT_ID,
    deadline: Math.floor(Date.now() / 1000) + 1200, // 20 minutes
    enableGasEstimation: true
    };

    console.log('🔨 Building swap transaction...');
    const response = await apiRequest(path, 'POST', body);

    if (response.code !== 0) {
        throw new Error(`KyberSwap build error: ${response.message}`);
    }

    return response.data;
}

/**
 * Legacy fallback: GET /{chain}/route/encode to obtain encoded calldata
 */
async function getSwapLegacyEncode(tokenIn, tokenOut, amountIn, toAddress, slippageTolerance = 50) {
    const params = new URLSearchParams({
        tokenIn: tokenIn,
        tokenOut: tokenOut,
        amountIn: amountIn,
        to: toAddress,
        slippageTolerance: String(slippageTolerance),
        clientData: JSON.stringify({ source: CLIENT_ID })
    });
    const path = `/${CHAIN}/route/encode?${params.toString()}`;
    console.log('📊 Getting legacy encoded route (fallback)...');
    const data = await apiRequest(path);
    if (!data || !data.encodedSwapData || !data.routerAddress) {
        throw new Error('Kyber legacy encode failed or returned incomplete data');
    }
    return data;
}

/**
 * Buy MAXX with ETH
 */
async function buyMaxx(ethAmount, slippageTolerance = 50, routeOpts = {}) {
    try {
        console.log('\n🔷 BUY MAXX WITH ETH');
        console.log('===================');
        console.log('ETH Amount:', ethers.utils.formatEther(ethAmount), 'ETH\n');

        let txCalldata, routerAddress, txValue, previewOut;
        try {
            // Prefer V1 route + build
            const routeData = await getSwapRoute(ETH_ADDRESS, MAXX, ethAmount, slippageTolerance, routeOpts);
            const { routeSummary, routerAddress: r } = routeData;

            console.log('✅ Route found (V1):');
            console.log('  Amount In:', ethers.utils.formatEther(routeSummary.amountIn), 'ETH');
            console.log('  Amount Out:', ethers.utils.formatUnits(routeSummary.amountOut, 18), 'MAXX');
            console.log('  Gas Estimate:', routeSummary.gas);
            console.log('  Gas USD:', routeSummary.gasUsd);
            console.log('  Router:', r);
            printRouteExchanges(routeSummary);
            console.log('');

            const built = await buildSwapTransaction(routeSummary, wallet.address, wallet.address, slippageTolerance);
            txCalldata = built.data;
            routerAddress = built.routerAddress;
            txValue = built.transactionValue;
            previewOut = built.amountOut;

            console.log('✅ Transaction built:');
            console.log('  Expected Out:', ethers.utils.formatUnits(previewOut, 18), 'MAXX');
            console.log('  Gas Estimate:', built.gas);
            console.log('  Value:', ethers.utils.formatEther(txValue), 'ETH');
            console.log('');
        } catch (e) {
            if (!e.__kyber_v1_failed) throw e;
            // Fallback to legacy
            const legacy = await getSwapLegacyEncode(ETH_ADDRESS, MAXX, ethAmount, wallet.address, slippageTolerance);
            txCalldata = legacy.encodedSwapData;
            routerAddress = legacy.routerAddress;
            txValue = ethAmount; // native in -> send amountIn as value
            previewOut = legacy.outputAmount || '0';
            console.log('✅ Legacy route encoded');
            console.log('  Router:', routerAddress);
            console.log('  Value :', ethers.utils.formatEther(txValue), 'ETH');
            if (legacy.outputAmount) console.log('  Est Out:', ethers.utils.formatUnits(legacy.outputAmount, 18), 'MAXX');
            console.log('  Route : legacy encode (no detailed hops available)');
            console.log('');
        }

        // Optional dry-run
        if (process.env.DRY_RUN === '1' || process.env.DRY_RUN === 'true') {
            console.log('🧪 DRY-RUN enabled: not broadcasting transaction.');
            return 'DRY_RUN';
        }

        // Execute transaction
        console.log('📤 Sending transaction...');
        // Use estimated gas with a tight buffer when available
        const txRequest = {
            to: routerAddress,
            data: txCalldata,
            value: txValue,
        };
        try {
            const builtGas = await provider.estimateGas(txRequest);
            txRequest.gasLimit = builtGas.mul(105).div(100); // +5%
        } catch {
            txRequest.gasLimit = 400000; // conservative fallback (lower than earlier 600k)
        }

        // Set EIP-1559 fees conservatively for Base
        try {
            const latest = await provider.getBlock('latest');
            const priorityGwei = process.env.PRIORITY_GWEI || (process.env.PRIORITY_GWEI === '0' ? '0' : '0.01');
            const feeMult = Number(process.env.MAXFEE_MULT || '105');
            const absMaxFeeGwei = process.env.GAS_MAX_FEE_GWEI; // optional absolute cap in gwei
            let maxPriority = ethers.utils.parseUnits(priorityGwei, 'gwei');
            const baseFee = latest.baseFeePerGas || (await provider.getFeeData()).gasPrice;
            if (baseFee) {
                let maxFee;
                if (absMaxFeeGwei) {
                    maxFee = ethers.utils.parseUnits(absMaxFeeGwei, 'gwei');
                } else {
                    maxFee = baseFee.mul(feeMult).div(100).add(maxPriority);
                }
                // Ensure priority <= maxFee
                if (maxPriority.gt(maxFee)) {
                    // clamp priority to 90% of maxFee
                    maxPriority = maxFee.mul(90).div(100);
                }
                txRequest.maxPriorityFeePerGas = maxPriority;
                txRequest.maxFeePerGas = maxFee;
                txRequest.type = 2;
                console.log(`  Gas params: maxFee ${ethers.utils.formatUnits(maxFee,'gwei')} gwei, priority ${ethers.utils.formatUnits(maxPriority,'gwei')} gwei`);
            }
        } catch {}

        // Pre-send fee check
        const ETH_PRICE_USD = toNumber(process.env.ETH_PRICE_USD || '4000', 4000);
        const MAX_FEE_USD = toNumber(process.env.MAX_FEE_USD || process.env.MAX_TX_FEE_USD || '', NaN);
    const feeEst = await estimateFeeEth(txRequest, txRequest.gasLimit);
        console.log(`  Fee estimate: ~${feeEst.feeEth.toFixed(6)} ETH (~$${(feeEst.feeEth*ETH_PRICE_USD).toFixed(4)})`);
        if (Number.isFinite(MAX_FEE_USD) && (feeEst.feeEth * ETH_PRICE_USD) > MAX_FEE_USD) {
            console.log(`⛔ Aborting: estimated fee exceeds cap $${MAX_FEE_USD}`);
            return null;
        }

        const tx = await wallet.sendTransaction(txRequest);

        console.log('⏳ Transaction sent:', tx.hash);
        if (process.env.NO_WAIT === '1' || process.env.NO_WAIT === 'true') {
            console.log('🕒 NO-WAIT enabled: returning tx hash without waiting for confirmation.');
            return tx.hash;
        }
        console.log('   Waiting for confirmation...\n');

        const receipt = await tx.wait();

        if (receipt.status === 1) {
            console.log('✅ SUCCESS! Transaction confirmed');
            console.log('   Gas Used:', receipt.gasUsed.toString());
            console.log('   Block:', receipt.blockNumber);
            console.log('   TX:', receipt.transactionHash);
            return receipt.transactionHash;
        } else {
            console.log('❌ Transaction reverted');
            return null;
        }

    } catch (error) {
        console.error('❌ Error buying MAXX:', error.message);
        if (error.response) {
            console.error('   API Response:', JSON.stringify(error.response, null, 2));
        }
        return null;
    }
}

/**
 * Sell MAXX for ETH
 */
async function sellMaxx(maxxAmount, slippageTolerance = 50, routeOpts = {}) {
    try {
        console.log('\n🔶 SELL MAXX FOR ETH');
        console.log('===================');
        console.log('MAXX Amount:', ethers.utils.formatUnits(maxxAmount, 18), 'MAXX\n');

        // Check allowance first
        const maxxContract = new ethers.Contract(
            MAXX,
            ['function allowance(address owner, address spender) view returns (uint256)'],
            provider
        );

        const allowance = await maxxContract.allowance(wallet.address, KYBERSWAP_ROUTER);

        if (allowance.lt(maxxAmount)) {
            console.log('⚠️  Need to approve MAXX spending first...');
            const approveContract = new ethers.Contract(
                MAXX,
                ['function approve(address spender, uint256 amount) returns (bool)'],
                wallet
            );

            const approveTx = await approveContract.approve(
                KYBERSWAP_ROUTER,
                ethers.constants.MaxUint256
            );
            console.log('   Approval TX:', approveTx.hash);
            await approveTx.wait();
            console.log('   ✅ Approval confirmed\n');
        }

        let txCalldata, routerAddress, previewOut;
        try {
            const routeData = await getSwapRoute(MAXX, ETH_ADDRESS, maxxAmount, slippageTolerance, routeOpts);
            const { routeSummary, routerAddress: r } = routeData;

            console.log('✅ Route found (V1):');
            console.log('  Amount In:', ethers.utils.formatUnits(routeSummary.amountIn, 18), 'MAXX');
            console.log('  Amount Out:', ethers.utils.formatEther(routeSummary.amountOut), 'ETH');
            console.log('  Gas Estimate:', routeSummary.gas);
            console.log('  Gas USD:', routeSummary.gasUsd);
            console.log('  Router:', r);
            console.log('');

            const built = await buildSwapTransaction(routeSummary, wallet.address, wallet.address, slippageTolerance);
            txCalldata = built.data;
            routerAddress = built.routerAddress;
            previewOut = built.amountOut;

            console.log('✅ Transaction built:');
            console.log('  Expected Out:', ethers.utils.formatEther(previewOut), 'ETH');
            console.log('  Gas Estimate:', built.gas);
            console.log('');
        } catch (e) {
            if (!e.__kyber_v1_failed) throw e;
            // Fallback to legacy
            const legacy = await getSwapLegacyEncode(MAXX, ETH_ADDRESS, maxxAmount, wallet.address, slippageTolerance);
            txCalldata = legacy.encodedSwapData;
            routerAddress = legacy.routerAddress;
            previewOut = legacy.outputAmount || '0';
            console.log('✅ Legacy route encoded');
            console.log('  Router:', routerAddress);
            if (legacy.outputAmount) console.log('  Est Out:', ethers.utils.formatEther(legacy.outputAmount), 'ETH');
            console.log('');
        }

        // Optional dry-run
        if (process.env.DRY_RUN === '1' || process.env.DRY_RUN === 'true') {
            console.log('🧪 DRY-RUN enabled: not broadcasting transaction.');
            return 'DRY_RUN';
        }

        // Execute transaction
        console.log('📤 Sending transaction...');
        const txReq = { to: routerAddress, data: txCalldata, value: '0' };
        try {
            const est = await provider.estimateGas(txReq);
            txReq.gasLimit = est.mul(105).div(100);
        } catch {
            txReq.gasLimit = 350000;
        }
        // EIP-1559 fee tuning
        try {
            const latest = await provider.getBlock('latest');
            const priorityGwei = process.env.PRIORITY_GWEI || (process.env.PRIORITY_GWEI === '0' ? '0' : '0.01');
            const feeMult = Number(process.env.MAXFEE_MULT || '105');
            const absMaxFeeGwei = process.env.GAS_MAX_FEE_GWEI;
            let maxPriority = ethers.utils.parseUnits(priorityGwei, 'gwei');
            const baseFee = latest.baseFeePerGas || (await provider.getFeeData()).gasPrice;
            if (baseFee) {
                let maxFee;
                if (absMaxFeeGwei) {
                    maxFee = ethers.utils.parseUnits(absMaxFeeGwei, 'gwei');
                } else {
                    maxFee = baseFee.mul(feeMult).div(100).add(maxPriority);
                }
                if (maxPriority.gt(maxFee)) {
                    maxPriority = maxFee.mul(90).div(100);
                }
                txReq.maxPriorityFeePerGas = maxPriority;
                txReq.maxFeePerGas = maxFee;
                txReq.type = 2;
                console.log(`  Gas params: maxFee ${ethers.utils.formatUnits(maxFee,'gwei')} gwei, priority ${ethers.utils.formatUnits(maxPriority,'gwei')} gwei`);
            }
        } catch {}

        const ETH_PRICE_USD = toNumber(process.env.ETH_PRICE_USD || '4000', 4000);
        const MAX_FEE_USD = toNumber(process.env.MAX_FEE_USD || process.env.MAX_TX_FEE_USD || '', NaN);
        const feeEst2 = await estimateFeeEth(txReq, txReq.gasLimit);
        console.log(`  Fee estimate: ~${feeEst2.feeEth.toFixed(6)} ETH (~$${(feeEst2.feeEth*ETH_PRICE_USD).toFixed(4)})`);
        if (Number.isFinite(MAX_FEE_USD) && (feeEst2.feeEth * ETH_PRICE_USD) > MAX_FEE_USD) {
            console.log(`⛔ Aborting: estimated fee exceeds cap $${MAX_FEE_USD}`);
            return null;
        }

        const tx = await wallet.sendTransaction(txReq);

        console.log('⏳ Transaction sent:', tx.hash);
        if (process.env.NO_WAIT === '1' || process.env.NO_WAIT === 'true') {
            console.log('🕒 NO-WAIT enabled: returning tx hash without waiting for confirmation.');
            return tx.hash;
        }
        console.log('   Waiting for confirmation...\n');

        const receipt = await tx.wait();

        if (receipt.status === 1) {
            console.log('✅ SUCCESS! Transaction confirmed');
            console.log('   Gas Used:', receipt.gasUsed.toString());
            console.log('   Block:', receipt.blockNumber);
            console.log('   TX:', receipt.transactionHash);
            return receipt.transactionHash;
        } else {
            console.log('❌ Transaction reverted');
            return null;
        }

    } catch (error) {
        console.error('❌ Error selling MAXX:', error.message);
        if (error.response) {
            console.error('   API Response:', JSON.stringify(error.response, null, 2));
        }
        return null;
    }
}

/**
 * Get current balances
 */
async function getBalances() {
    const ethBalance = await provider.getBalance(wallet.address);

    const maxxContract = new ethers.Contract(
        MAXX,
        ['function balanceOf(address) view returns (uint256)'],
        provider
    );
    const maxxBalance = await maxxContract.balanceOf(wallet.address);

    return {
        eth: ethBalance,
        maxx: maxxBalance
    };
}

/**
 * Main function
 */
async function main() {
    // CLI: node kyberswap_trader.js [buy|sell|quote] <amount> [--slippage=50] [--usd] [--dry-run]
    const args = process.argv.slice(2);
    const cmd = (args[0] || 'quote').toLowerCase();
    const amountArg = args[1];
    const flags = args.slice(2);

    // Flags
    const slippageFlag = flags.find(f => f.startsWith('--slippage='));
    const slippageTolerance = slippageFlag ? Number(slippageFlag.split('=')[1]) : 50; // bps
    const isUsd = flags.includes('--usd');
    const isDryRun = flags.includes('--dry-run');
    const noWait = flags.includes('--no-wait');
    if (isDryRun) process.env.DRY_RUN = '1';
    if (noWait) process.env.NO_WAIT = '1';
    const prioFlag = flags.find(f => f.startsWith('--priority-gwei='));
    const feeMultFlag = flags.find(f => f.startsWith('--maxfee-mult='));
    const absMaxFeeFlag = flags.find(f => f.startsWith('--max-fee-gwei='));
    if (prioFlag) process.env.PRIORITY_GWEI = prioFlag.split('=')[1];
    if (feeMultFlag) process.env.MAXFEE_MULT = feeMultFlag.split('=')[1];
    if (absMaxFeeFlag) process.env.GAS_MAX_FEE_GWEI = absMaxFeeFlag.split('=')[1];

    // Route tuning flags
    const routeOpts = {
        v4Only: flags.includes('--v4-only'),
        singlePath: flags.includes('--single'),
        directPools: flags.includes('--direct'),
        excludeRFQ: flags.includes('--no-rfq')
    };

    // Show balances
    const balances = await getBalances();
    console.log('Current Balances:');
    console.log('  ETH:', ethers.utils.formatEther(balances.eth), 'ETH');
    console.log('  MAXX:', ethers.utils.formatUnits(balances.maxx, 18), 'MAXX');
    console.log('');

    if (cmd === 'quote') {
        // Default quote: 0.001 ETH -> MAXX
        const ethAmount = ethers.utils.parseEther('0.001');
        console.log('🧮 Quote: ETH -> MAXX');
        try {
        const routeData = await getSwapRoute(ETH_ADDRESS, MAXX, ethAmount.toString(), slippageTolerance, routeOpts);
            console.log('  Amount In:', ethers.utils.formatEther(routeData.routeSummary.amountIn), 'ETH');
            console.log('  Est Out :', ethers.utils.formatUnits(routeData.routeSummary.amountOut, 18), 'MAXX');
            console.log('  Gas     :', routeData.routeSummary.gas);
            console.log('  Router  :', routeData.routerAddress);
        printRouteExchanges(routeData.routeSummary);
        } catch (e) {
            console.log('  V1 routes blocked, trying legacy encode...');
            const legacy = await getSwapLegacyEncode(ETH_ADDRESS, MAXX, ethAmount.toString(), wallet.address, slippageTolerance);
            console.log('  Router  :', legacy.routerAddress);
            if (legacy.outputAmount) console.log('  Est Out :', ethers.utils.formatUnits(legacy.outputAmount, 18), 'MAXX');
            console.log('  DataLen :', legacy.encodedSwapData.length);
        }
        return;
    }

    if (!amountArg) {
        console.error('Usage: node kyberswap_trader.js [buy|sell|quote] <amount> [--slippage=50] [--usd] [--dry-run]');
        process.exit(1);
    }

    if (cmd === 'buy') {
        let ethAmount;
        if (isUsd) {
            const ETH_PRICE_USD = Number(process.env.ETH_PRICE_USD || 4000);
            const usd = Number(amountArg);
            ethAmount = ethers.utils.parseEther((usd / ETH_PRICE_USD).toFixed(6));
            console.log(`📝 Buy $${usd} USD worth (ETH price $${ETH_PRICE_USD}) => ${ethers.utils.formatEther(ethAmount)} ETH`);
        } else {
            ethAmount = ethers.utils.parseEther(String(amountArg));
            console.log(`📝 Buy with ${ethers.utils.formatEther(ethAmount)} ETH`);
        }
    const result = await buyMaxx(ethAmount.toString(), slippageTolerance, routeOpts);
        if (result && result !== 'DRY_RUN') {
            console.log('\n🎉 Trade completed successfully!');
            console.log('   BaseScan:', `https://basescan.org/tx/${result}`);
        }
        return;
    }

    if (cmd === 'sell') {
        // amountArg in MAXX tokens (unless --usd which is not supported for sell here)
        const maxxAmount = ethers.utils.parseUnits(String(amountArg), 18);
        console.log(`📝 Sell ${ethers.utils.formatUnits(maxxAmount, 18)} MAXX`);
    const result = await sellMaxx(maxxAmount.toString(), slippageTolerance, routeOpts);
        if (result && result !== 'DRY_RUN') {
            console.log('\n🎉 Trade completed successfully!');
            console.log('   BaseScan:', `https://basescan.org/tx/${result}`);
        }
        return;
    }

    console.error('Unknown command. Use buy|sell|quote');
    process.exit(1);
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

// Export functions for use in other scripts
module.exports = {
    buyMaxx,
    sellMaxx,
    getBalances,
    getSwapRoute,
    buildSwapTransaction
};
