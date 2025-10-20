'use client'

import { useStakingInfo } from '@/hooks/use-mcpvots'
import { Clock, DollarSign, Globe, Lock, TrendingUp, Vote } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAccount } from 'wagmi'

export function StakingInterface() {
    const { address } = useAccount()
    const { data: stakingInfo } = useStakingInfo(address)
    const [stakeAmount, setStakeAmount] = useState('')
    const [unstakeAmount, setUnstakeAmount] = useState('')
    const [ipfsConnected, setIpfsConnected] = useState(false)
    const [governancePower, setGovernancePower] = useState(0)

    // Simulate IPFS connection check
    useEffect(() => {
        const checkIpfsConnection = async () => {
            // In real app, this would check actual IPFS node connection
            setTimeout(() => {
                setIpfsConnected(Math.random() > 0.3) // 70% chance of being connected
            }, 1000)
        }
        checkIpfsConnection()
    }, [])

    // Calculate governance power based on staked amount
    useEffect(() => {
        if (stakingInfo?.stakedAmount) {
            setGovernancePower(stakingInfo.stakedAmount * 10) // 10x multiplier for governance
        }
    }, [stakingInfo?.stakedAmount])

    const handleStake = () => {
        // In real app, this would call the staking contract
        console.log('Staking', stakeAmount, 'VOTS')
        setStakeAmount('')
    }

    const handleUnstake = () => {
        // In real app, this would call the unstaking function
        console.log('Unstaking', unstakeAmount, 'VOTS')
        setUnstakeAmount('')
    }

    const handleClaimRewards = () => {
        // In real app, this would claim staking rewards
        console.log('Claiming rewards')
    }

    return (
        <div className="space-y-6">
            {/* Staking Overview - Terminal Style */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-6">
                    <h2 className="text-green-400 font-mono text-lg font-bold tracking-wide flex items-center">
                        <Lock className="h-5 w-5 mr-2" />
                        [MCPVOTS STAKING TERMINAL]
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                        <DollarSign className="h-6 w-6 text-green-400 mx-auto mb-2" />
                        <div className="text-green-400 font-mono text-xl font-bold">
                            {stakingInfo?.stakedAmount.toFixed(2) || '0.00'}
                        </div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            VOTS STAKED
                        </p>
                    </div>

                    <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                        <TrendingUp className="h-6 w-6 text-green-400 mx-auto mb-2" />
                        <div className="text-green-400 font-mono text-xl font-bold">
                            {stakingInfo?.rewards.toFixed(2) || '0.00'}
                        </div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            REWARDS EARNED
                        </p>
                    </div>

                    <div className="text-center p-4 bg-gray-800 border border-emerald-400/20 rounded">
                        <Vote className="h-6 w-6 text-emerald-400 mx-auto mb-2" />
                        <div className="text-emerald-400 font-mono text-xl font-bold">
                            {governancePower.toFixed(0)}
                        </div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            SVOTS GOVERNANCE
                        </p>
                    </div>

                    <div className="text-center p-4 bg-gray-800 border border-lime-400/20 rounded">
                        <Clock className="h-6 w-6 text-lime-400 mx-auto mb-2" />
                        <div className="text-lime-400 font-mono text-xl font-bold">
                            {stakingInfo?.lockPeriod || '0'}
                        </div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            DAYS LOCKED
                        </p>
                    </div>
                </div>

                {/* Claim Rewards - Terminal Style */}
                <div className="flex justify-center mb-8">
                    <button
                        onClick={handleClaimRewards}
                        disabled={!stakingInfo?.rewards || stakingInfo.rewards <= 0}
                        className="bg-green-400/10 hover:bg-green-400/20 disabled:bg-gray-700 disabled:cursor-not-allowed text-green-400 disabled:text-green-400/50 border border-green-400/50 disabled:border-green-400/30 font-mono text-sm font-bold tracking-wide px-8 py-3 rounded transition-all duration-200"
                    >
                        [CLAIM {stakingInfo?.rewards.toFixed(2) || '0.00'} VOTS REWARDS]
                    </button>
                </div>
            </div>

            {/* Staking Actions - Terminal Style */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Stake VOTS */}
                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                    <div className="border-b border-green-400/30 pb-3 mb-4">
                        <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                            [STAKE VOTS]
                        </h3>
                    </div>
                    <p className="text-green-400/70 font-mono text-sm mb-4">
                        Stake your VOTS tokens to earn rewards and participate in governance.
                    </p>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-green-400/80 font-mono text-sm font-bold mb-2 tracking-wide">
                                AMOUNT TO STAKE
                            </label>
                            <input
                                type="number"
                                value={stakeAmount}
                                onChange={(e) => setStakeAmount(e.target.value)}
                                placeholder="Enter VOTS amount"
                                className="w-full px-4 py-3 bg-gray-800 border border-green-400/30 rounded font-mono text-green-400 placeholder-green-400/50 focus:border-green-400/70 focus:outline-none transition-colors"
                            />
                        </div>

                        <button
                            onClick={handleStake}
                            disabled={!stakeAmount || parseFloat(stakeAmount) <= 0}
                            className="w-full bg-green-400/10 hover:bg-green-400/20 disabled:bg-gray-700 disabled:cursor-not-allowed text-green-400 disabled:text-green-400/50 border border-green-400/50 disabled:border-green-400/30 font-mono text-sm font-bold tracking-wide px-6 py-3 rounded transition-all duration-200"
                        >
                            [STAKE VOTS]
                        </button>
                    </div>

                    <div className="mt-4 p-4 bg-green-900/20 border border-green-400/30 rounded">
                        <p className="text-green-400/80 font-mono text-sm font-bold mb-2">
                            STAKING BENEFITS & SVOTS GOVERNANCE:
                        </p>
                        <ul className="text-green-400/70 font-mono text-sm space-y-1">
                            <li>• Earn {stakingInfo?.apr || '0'}% APR on staked tokens</li>
                            <li>• Receive SVOTS governance tokens (10x multiplier)</li>
                            <li>• Vote on ecosystem decisions and protocol upgrades</li>
                            <li>• Shape the future of MCPVOTS platform</li>
                            <li>• Access to exclusive features and early releases</li>
                            <li>• Priority in mining queues and agent matching</li>
                        </ul>
                    </div>
                </div>

                {/* Unstake VOTS */}
                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                    <div className="border-b border-green-400/30 pb-3 mb-4">
                        <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                            [UNSTAKE VOTS]
                        </h3>
                    </div>
                    <p className="text-green-400/70 font-mono text-sm mb-4">
                        Unstake your VOTS tokens. Note: Early unstaking may incur penalties.
                    </p>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-green-400/80 font-mono text-sm font-bold mb-2 tracking-wide">
                                AMOUNT TO UNSTAKE
                            </label>
                            <input
                                type="number"
                                value={unstakeAmount}
                                onChange={(e) => setUnstakeAmount(e.target.value)}
                                placeholder="Enter VOTS amount"
                                max={stakingInfo?.stakedAmount || 0}
                                className="w-full px-4 py-3 bg-gray-800 border border-green-400/30 rounded font-mono text-green-400 placeholder-green-400/50 focus:border-red-400/70 focus:outline-none transition-colors"
                            />
                        </div>

                        <button
                            onClick={handleUnstake}
                            disabled={!unstakeAmount || parseFloat(unstakeAmount) <= 0}
                            className="w-full bg-red-400/10 hover:bg-red-400/20 disabled:bg-gray-700 disabled:cursor-not-allowed text-red-400 disabled:text-red-400/50 border border-red-400/50 disabled:border-red-400/30 font-mono text-sm font-bold tracking-wide px-6 py-3 rounded transition-all duration-200"
                        >
                            [UNSTAKE VOTS]
                        </button>
                    </div>

                    <div className="mt-4 p-4 bg-green-900/20 border border-green-400/30 rounded">
                        <p className="text-green-400/80 font-mono text-sm font-bold">
                            IMPORTANT:
                        </p>
                        <p className="text-green-400/70 font-mono text-sm mt-1">
                            Unstaking before the lock period ends may result in a penalty of up to 10% of your staked amount.
                        </p>
                    </div>
                </div>
            </div>

            {/* IPFS Connectivity Status */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide flex items-center">
                        <Globe className="h-5 w-5 mr-2" />
                        [MCPVOTS IPFS NETWORK STATUS]
                    </h3>
                </div>
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full ${ipfsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                        <span className="text-green-400 font-mono text-sm font-bold">
                            {ipfsConnected ? 'CONNECTED TO MCPVOTS IPFS NODE' : 'CONNECTING TO IPFS NETWORK...'}
                        </span>
                    </div>
                    <div className="text-green-400/70 font-mono text-xs">
                        Decentralized data storage & agent communication
                    </div>
                </div>
            </div>

            {/* Staking Statistics - Terminal Style */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                        [MCPVOTS STAKING STATISTICS]
                    </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                        <div className="text-green-400 font-mono text-2xl font-bold">1,250,000</div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            TOTAL VOTS STAKED
                        </p>
                    </div>
                    <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                        <div className="text-emerald-400 font-mono text-2xl font-bold">2,847</div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            ACTIVE STAKERS
                        </p>
                    </div>
                    <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                        <div className="text-lime-400 font-mono text-2xl font-bold">15.2%</div>
                        <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                            AVERAGE APR
                        </p>
                    </div>
                </div>
            </div>

            {/* SVOTS Governance Section */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide flex items-center gap-2">
                        <Vote className="w-5 h-5" />
                        [SVOTS GOVERNANCE TOKENS]
                    </h3>
                </div>
                <div className="space-y-4">
                    <div className="bg-gray-800 border border-green-400/20 rounded p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-green-400 font-mono text-sm font-bold">
                                YOUR SVOTS BALANCE
                            </span>
                            <span className="text-emerald-400 font-mono text-lg font-bold">
                                1,250 SVOTS
                            </span>
                        </div>
                        <div className="text-green-400/70 font-mono text-xs">
                            Governance power: 12,500 votes (10x multiplier)
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-gray-800 border border-green-400/20 rounded p-4">
                            <h4 className="text-green-400 font-mono text-sm font-bold mb-2">
                                PROPOSAL VOTING
                            </h4>
                            <p className="text-green-400/70 font-mono text-xs">
                                Vote on ecosystem upgrades, fee structures, and data offerings
                            </p>
                            <button className="mt-3 w-full bg-green-600 hover:bg-green-500 text-white font-mono text-sm py-2 px-4 rounded border border-green-400/30 transition-colors">
                                VIEW ACTIVE PROPOSALS
                            </button>
                        </div>
                        <div className="bg-gray-800 border border-green-400/20 rounded p-4">
                            <h4 className="text-green-400 font-mono text-sm font-bold mb-2">
                                GOVERNANCE REWARDS
                            </h4>
                            <p className="text-green-400/70 font-mono text-xs">
                                Earn additional VOTS for active participation in governance
                            </p>
                            <div className="mt-2 text-emerald-400 font-mono text-sm">
                                +250 VOTS this month
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* IPFS Connectivity Section */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide flex items-center gap-2">
                        <Globe className="w-5 h-5" />
                        [IPFS CONNECTIVITY STATUS]
                    </h3>
                </div>
                <div className="space-y-4">
                    <div className="bg-gray-800 border border-green-400/20 rounded p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-green-400 font-mono text-sm font-bold">
                                NETWORK STATUS
                            </span>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                <span className="text-green-400 font-mono text-sm font-bold">
                                    CONNECTED
                                </span>
                            </div>
                        </div>
                        <div className="text-green-400/70 font-mono text-xs">
                            Connected to MCPVOTS IPFS node for decentralized data storage
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gray-800 border border-green-400/20 rounded p-4 text-center">
                            <div className="text-emerald-400 font-mono text-xl font-bold">47</div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                PEERS CONNECTED
                            </p>
                        </div>
                        <div className="bg-gray-800 border border-green-400/20 rounded p-4 text-center">
                            <div className="text-lime-400 font-mono text-xl font-bold">2.1GB</div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                DATA STORED
                            </p>
                        </div>
                        <div className="bg-gray-800 border border-green-400/20 rounded p-4 text-center">
                            <div className="text-green-500 font-mono text-xl font-bold">99.8%</div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                UPTIME
                            </p>
                        </div>
                    </div>
                    <div className="bg-gray-800 border border-green-400/20 rounded p-4">
                        <h4 className="text-green-400 font-mono text-sm font-bold mb-2">
                            DECENTRALIZED FEATURES
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-green-400/70 font-mono text-xs">
                            <div>• Agent communication storage</div>
                            <div>• Immutable data archives</div>
                            <div>• Censorship-resistant content</div>
                            <div>• Global content delivery</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
