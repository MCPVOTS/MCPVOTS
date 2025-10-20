"use client"

import { useLeaderboard, useMiningStats, useStakingInfo } from '@/hooks/use-mcpvots'
import { Coins, TrendingUp, Trophy, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAccount, useBalance } from 'wagmi'
import { BaseInsightPopup } from './base-insight-popup'

export function MiningDashboard() {
    const [mounted, setMounted] = useState(false)
    const [showBaseInsight, setShowBaseInsight] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    const { address, isConnected } = useAccount()
    const { data: balance } = useBalance({
        address: address,
    })

    const { data: miningStats } = useMiningStats(address)
    const { data: leaderboard } = useLeaderboard()
    const { data: stakingInfo } = useStakingInfo(address)

    if (!mounted) {
        return (
            <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded mb-4"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
                    <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                </div>
            </div>
        )
    }

    if (!isConnected) {
        return (
            <div className="text-center py-12">
                <div className="bg-red-900/20 border border-red-400/30 rounded-lg p-8 max-w-md mx-auto">
                    <div className="text-red-400 font-mono text-lg font-bold mb-4">
                        [WALLET NOT CONNECTED]
                    </div>
                    <div className="text-green-400/70 font-mono text-sm mb-6">
                        Please connect your wallet to access the MCPVOTS mining terminal.
                    </div>
                    <div className="text-green-400/50 font-mono text-xs">
                        Use the [CONNECT WALLET] button in the top-right corner.
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Data Intelligence Showcase */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h2 className="text-green-400 font-mono text-lg font-bold tracking-wide text-center">
                        [UNIQUE AI DATA INTELLIGENCE - NO OTHER PLATFORM OFFERS THIS LEVEL]
                    </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-400/50 rounded-lg p-4 hover:border-green-400/70 transition-all duration-300 hover:shadow-lg hover:shadow-green-400/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-green-400 font-mono text-sm font-bold tracking-wide">BASE NETWORK INSIGHTS</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            Real-time Base blockchain analytics, gas optimization, and network health monitoring
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-green-900/30 to-blue-900/30 border border-green-400/50 rounded-lg p-4 hover:border-green-400/70 transition-all duration-300 hover:shadow-lg hover:shadow-green-400/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                            <span className="text-green-400 font-mono text-sm font-bold tracking-wide">AGENT PERFORMANCE</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            AI agent success rates, transaction efficiency, and predictive performance metrics
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/30 border border-emerald-400/50 rounded-lg p-4 hover:border-emerald-400/70 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-400/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                            <span className="text-emerald-400 font-mono text-sm font-bold tracking-wide">MARKET INTELLIGENCE</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            Advanced market analysis, trend prediction, and arbitrage opportunities
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-lime-900/30 to-green-900/30 border border-lime-400/50 rounded-lg p-4 hover:border-lime-400/70 transition-all duration-300 hover:shadow-lg hover:shadow-lime-400/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-lime-400 rounded-full animate-pulse" style={{ animationDelay: '0.9s' }}></div>
                            <span className="text-lime-400 font-mono text-sm font-bold tracking-wide">SOCIAL SENTIMENT</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            Real-time social media analysis and sentiment tracking for market movements
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-green-900/30 to-lime-900/30 border border-green-500/50 rounded-lg p-4 hover:border-green-500/70 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '1.2s' }}></div>
                            <span className="text-green-500 font-mono text-sm font-bold tracking-wide">PREDICTIVE ANALYTICS</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            Machine learning predictions for price movements and market trends
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/30 border border-emerald-500/50 rounded-lg p-4 hover:border-emerald-500/70 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/20">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" style={{ animationDelay: '1.5s' }}></div>
                            <span className="text-emerald-500 font-mono text-sm font-bold tracking-wide">ECONOMIC INDICATORS</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            Macro-economic data analysis and its impact on crypto markets
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-lime-900/30 to-emerald-900/30 border border-lime-500/50 rounded-lg p-4 hover:border-lime-500/70 transition-all duration-300 hover:shadow-lg hover:shadow-lime-500/20 md:col-span-2 lg:col-span-1">
                        <div className="flex items-center space-x-2 mb-2">
                            <div className="w-3 h-3 bg-lime-500 rounded-full animate-pulse" style={{ animationDelay: '1.8s' }}></div>
                            <span className="text-lime-500 font-mono text-sm font-bold tracking-wide">SMART AGENT DISCOVERY</span>
                        </div>
                        <p className="text-green-400/70 font-mono text-xs">
                            AI-powered agent matching and recommendation system for optimal performance
                        </p>
                    </div>
                </div>
            </div>
            {/* Header Stats - Terminal Style */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-4 hover:border-green-400/50 transition-all duration-300 hover:shadow-lg hover:shadow-green-400/10">
                    <div className="flex items-center space-x-2 mb-2">
                        <Coins className="h-5 w-5 text-green-400 animate-pulse" />
                        <div className="text-green-400/70 font-mono text-xs font-bold tracking-wide">ETH BALANCE</div>
                    </div>
                    <div className="text-green-400 font-mono text-lg font-bold">
                        {balance?.formatted || '0.0000'} {balance?.symbol}
                    </div>
                </div>

                <div className="relative">
                    <div onMouseEnter={() => setShowBaseInsight(true)} onMouseLeave={() => setShowBaseInsight(false)} className="bg-gray-900 border border-green-400/30 rounded-lg p-4 transition-all duration-300 hover:shadow-lg hover:shadow-green-400/10 hover:border-green-400/40">
                        <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="h-5 w-5 text-green-400" />
                            <div className="text-green-400/80 font-mono text-xs font-bold tracking-wide">MINING RATE</div>
                        </div>
                        <div className="text-green-400 font-mono text-lg font-bold">
                            {miningStats?.miningRate.toFixed(4) || '0.0000'} VOTS/min
                        </div>
                    </div>
                    {showBaseInsight && <BaseInsightPopup address={address} />}
                </div>

                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-4 hover:border-green-400/50 transition-colors">
                    <div className="flex items-center space-x-2 mb-2">
                        <Trophy className="h-5 w-5 text-emerald-400" />
                        <div className="text-emerald-400/70 font-mono text-xs font-bold tracking-wide">TOTAL MINED</div>
                    </div>
                    <div className="text-emerald-400 font-mono text-lg font-bold">
                        {miningStats?.totalMined.toFixed(4) || '0.0000'} VOTS
                    </div>
                </div>

                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-4 hover:border-green-400/50 transition-colors">
                    <div className="flex items-center space-x-2 mb-2">
                        <Users className="h-5 w-5 text-green-300" />
                        <div className="text-green-300/70 font-mono text-xs font-bold tracking-wide">YOUR RANK</div>
                    </div>
                    <div className="text-green-300 font-mono text-lg font-bold">
                        #42
                    </div>
                </div>
            </div>

            {/* Main Dashboard Grid - Terminal Style */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Mining Stats */}
                <div className="lg:col-span-2 bg-gray-900 border border-green-400/30 rounded-lg p-6">
                    <div className="border-b border-green-400/30 pb-3 mb-4">
                        <h2 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                            [MCPVOTS MINING DASHBOARD]
                        </h2>
                    </div>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <span className="text-green-400/80 font-mono text-sm font-bold">STATUS</span>
                            <span className={`px-3 py-1 rounded text-xs font-mono font-bold tracking-wide ${miningStats?.status === 'active'
                                ? 'bg-green-400/20 text-green-400 border border-green-400/50'
                                : 'bg-gray-700 text-green-400/60 border border-green-400/30'
                                }`}>
                                [{miningStats?.status?.toUpperCase() || 'INACTIVE'}]
                            </span>
                        </div>

                        <div className="flex justify-between items-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <span className="text-green-400/80 font-mono text-sm font-bold">LAST UPDATE</span>
                            <span className="text-green-400/60 font-mono text-sm">
                                {miningStats?.lastUpdate ? new Date(miningStats.lastUpdate).toLocaleTimeString() : 'NEVER'}
                            </span>
                        </div>
                    </div>

                    {/* Action Buttons - Terminal Style */}
                    <div className="mt-6 flex flex-col sm:flex-row gap-4">
                        <button className={`flex-1 font-mono text-sm font-bold tracking-wide px-6 py-3 rounded border transition-all duration-200 ${miningStats?.status === 'active'
                            ? 'bg-red-400/10 hover:bg-red-400/20 text-red-400 border-red-400/50 hover:border-red-400/70'
                            : 'bg-green-400/10 hover:bg-green-400/20 text-green-400 border-green-400/50 hover:border-green-400/70'
                            }`}>
                            [{miningStats?.status === 'active' ? 'PAUSE' : 'START'} MINING]
                        </button>
                        <button className="flex-1 bg-emerald-400/10 hover:bg-emerald-400/20 text-emerald-400 border border-emerald-400/50 hover:border-emerald-400/70 font-mono text-sm font-bold tracking-wide px-6 py-3 rounded transition-all duration-200">
                            [STAKE VOTS]
                        </button>
                    </div>
                </div>                {/* Leaderboard - Terminal Style */}
                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                    <div className="border-b border-green-400/30 pb-3 mb-4">
                        <h2 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                            [MCPVOTS TOP MINERS]
                        </h2>
                    </div>
                    <div className="space-y-3">
                        {leaderboard?.slice(0, 5).map((entry) => (
                            <div key={entry.rank} className="flex items-center justify-between p-3 bg-gray-800 border border-green-400/20 rounded hover:border-green-400/40 transition-colors">
                                <div className="flex items-center space-x-3">
                                    <span className="text-green-400 font-mono font-bold text-lg">#{entry.rank}</span>
                                    <div>
                                        <p className="text-green-400/90 font-mono text-sm font-bold">
                                            {entry.address.slice(0, 6)}...{entry.address.slice(-4)}
                                        </p>
                                        <p className="text-green-400/60 font-mono text-xs">
                                            {entry.totalMined.toFixed(1)} VOTS
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-lime-400 font-mono font-bold text-sm">
                                        {entry.rewards.toFixed(1)}
                                    </p>
                                    <p className="text-green-400/50 font-mono text-xs">
                                        rewards
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Staking Info - Terminal Style */}
            {stakingInfo && (
                <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                    <div className="border-b border-green-400/30 pb-3 mb-4">
                        <h2 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                            [MCPVOTS STAKING OVERVIEW]
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <div className="text-green-400 font-mono text-xl font-bold mb-1">
                                {stakingInfo.stakedAmount.toFixed(2)}
                            </div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                VOTS STAKED
                            </p>
                        </div>
                        <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <div className="text-emerald-400 font-mono text-xl font-bold mb-1">
                                {stakingInfo.rewards.toFixed(2)}
                            </div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                REWARDS EARNED
                            </p>
                        </div>
                        <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <div className="text-lime-400 font-mono text-xl font-bold mb-1">
                                {stakingInfo.apr}%
                            </div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                APR
                            </p>
                        </div>
                        <div className="text-center p-4 bg-gray-800 border border-green-400/20 rounded">
                            <div className="text-green-500 font-mono text-xl font-bold mb-1">
                                {stakingInfo.lockPeriod}
                            </div>
                            <p className="text-green-400/70 font-mono text-xs font-bold tracking-wide">
                                DAYS LOCKED
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
