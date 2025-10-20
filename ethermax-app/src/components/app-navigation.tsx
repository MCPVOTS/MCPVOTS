'use client'

import { Cpu, Database, Lock, Network, Pickaxe, Trophy, Zap } from 'lucide-react'
import { useEffect, useState } from 'react'
import { LeaderboardDisplay } from './leaderboard-display'
import { MiningDashboard } from './mining-dashboard'
import { StakingInterface } from './staking-interface'

type TabType = 'mining' | 'staking' | 'leaderboard'

export function AppNavigation() {
    const [activeTab, setActiveTab] = useState<TabType>('mining')
    const [currentStatus, setCurrentStatus] = useState('')
    const [currentIntelligence, setCurrentIntelligence] = useState('')
    const [gasPrice, setGasPrice] = useState('0.00')
    const [ethPrice, setEthPrice] = useState('0.00')

    const statusMessages = [
        'CONNECTED TO BASE NETWORK',
        'AI AGENT PROTOCOLS ACTIVE',
        'VOTS ECONOMICS CALIBRATED',
        'SECURE CONNECTIONS ESTABLISHED',
        'SYSTEM OPERATIONAL'
    ]

    const intelligenceMessages = [
        'MCPVOTS INTELLIGENCE: BASE NETWORK GAS OPTIMIZATION ACTIVE',
        'MCPVOTS INTELLIGENCE: AI AGENT PERFORMANCE TRACKING ENABLED',
        'MCPVOTS INTELLIGENCE: MARKET SENTIMENT ANALYSIS RUNNING',
        'MCPVOTS INTELLIGENCE: PREDICTIVE ANALYTICS ENGAGED',
        'MCPVOTS INTELLIGENCE: SOCIAL MEDIA MONITORING ACTIVE'
    ]

    useEffect(() => {
        let index = 0
        const interval = setInterval(() => {
            setCurrentStatus(statusMessages[index])
            index = (index + 1) % statusMessages.length
        }, 3000)

        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        let index = 0
        const interval = setInterval(() => {
            setCurrentIntelligence(intelligenceMessages[index])
            index = (index + 1) % intelligenceMessages.length
        }, 4000)

        return () => clearInterval(interval)
    }, [])

    // Simulate real-time data updates
    useEffect(() => {
        const updatePrices = () => {
            setGasPrice((Math.random() * 50 + 10).toFixed(2))
            setEthPrice((Math.random() * 500 + 2500).toFixed(2))
        }

        updatePrices()
        const interval = setInterval(updatePrices, 5000)
        return () => clearInterval(interval)
    }, [])

    const tabs = [
        {
            id: 'mining' as TabType,
            label: 'Mining',
            icon: Pickaxe,
            component: MiningDashboard
        },
        {
            id: 'staking' as TabType,
            label: 'Staking',
            icon: Lock,
            component: StakingInterface
        },
        {
            id: 'leaderboard' as TabType,
            label: 'Leaderboard',
            icon: Trophy,
            component: LeaderboardDisplay
        }
    ]

    const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || MiningDashboard

    return (
        <div className="min-h-screen bg-black text-green-400 font-mono p-4 relative overflow-hidden">
            {/* Animated Cube Background */}
            <div className="fixed inset-0 opacity-20">
                <div className="absolute inset-0 bg-gradient-to-br from-green-900/10 via-black to-blue-900/10"></div>
                {/* Animated cubes */}
                {[...Array(20)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute w-8 h-8 border border-green-400/30 animate-pulse"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 3}s`,
                            animationDuration: `${2 + Math.random() * 3}s`
                        }}
                    >
                        <div className="w-full h-full bg-green-400/5 border border-green-400/20"></div>
                    </div>
                ))}
                {/* Grid overlay */}
                <div className="absolute inset-0 opacity-10">
                    <div className="w-full h-full bg-[linear-gradient(90deg,rgba(34,197,94,0.1)_1px,transparent_1px),linear-gradient(180deg,rgba(34,197,94,0.1)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
                </div>
            </div>

            <div className="max-w-6xl mx-auto relative z-10">
                {/* Animated Logo - Top Left with MCPVOTS */}
                <div className="fixed top-4 left-4 z-50 flex items-center space-x-4 group animate-logo-hover-float hover:animate-logo-hover-float">
                    {/* Glowing Logo with Hover Effect */}
                    <div className="relative group cursor-pointer">
                        {/* Outer glow ring */}
                        <div className="absolute -inset-2 bg-gradient-to-r from-green-400/20 via-cyan-400/20 to-green-400/20 rounded-full blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-pulse"></div>

                        {/* Spinning outer ring */}
                        <div className="absolute -inset-1 border-2 border-green-400/40 rounded-full animate-spin-slow"></div>

                        {/* Middle pulsing ring */}
                        <div className="absolute inset-0.5 border border-cyan-400/50 rounded-full animate-pulse"></div>

                        {/* Inner glow */}
                        <div className="absolute inset-1 bg-gradient-radial from-green-400/30 to-transparent rounded-full animate-ping"></div>

                        {/* Logo container */}
                        <div className="relative w-10 h-10 rounded-full overflow-hidden border-2 border-green-400/60 bg-black/80 backdrop-blur-sm group-hover:border-green-400 group-hover:shadow-[0_0_20px_rgba(34,197,94,0.6)] transition-all duration-300 group-hover:scale-110 animate-logo-hover-glow">
                            <img
                                src="/logo.jpg"
                                alt="MCPVOTS Logo"
                                className="w-full h-full object-cover animate-pulse group-hover:animate-none"
                            />
                        </div>

                        {/* Floating particles */}
                        <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-bounce opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-particle-hover-sparkle"></div>
                        <div className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-particle-hover-sparkle" style={{ animationDelay: '0.2s' }}></div>
                        <div className="absolute top-1/2 -right-2 w-1 h-1 bg-green-300 rounded-full animate-ping opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-particle-hover-sparkle" style={{ animationDelay: '0.4s' }}></div>
                    </div>

                    {/* Animated MCPVOTS Text */}
                    <div className="flex items-center space-x-1">
                        {['M', 'C', 'P', 'V', 'O', 'T', 'S'].map((letter, index) => (
                            <div
                                key={letter}
                                className="w-6 h-6 bg-gradient-to-br from-green-400 to-green-600 border border-green-300/50 flex items-center justify-center font-mono font-bold text-xs text-black animate-bounce hover:shadow-[0_0_10px_rgba(34,197,94,0.8)] hover:scale-110 cursor-pointer transition-all duration-300 animate-letter-hover-bounce"
                                style={{
                                    animationDelay: `${index * 0.1}s`,
                                    animationDuration: '2s'
                                }}
                            >
                                {letter}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Logo and Branding Header */}
                <div className="text-center mb-8 relative pt-16">
                    {/* Animated Logo with Spinning Ring */}
                    <div className="relative inline-block mb-6">
                        {/* Outer spinning ring */}
                        <div className="absolute inset-0 w-32 h-32 rounded-full border-2 border-green-400/30 animate-spin-ring"></div>

                        {/* Middle glowing ring */}
                        <div className="absolute inset-2 w-28 h-28 rounded-full border border-green-300/50 animate-glow-pulse"></div>

                        {/* Inner pulsing ring */}
                        <div className="absolute inset-4 w-24 h-24 rounded-full border border-green-200/70 animate-pulse"></div>

                        {/* Logo container */}
                        <div className="relative w-20 h-20 mx-auto rounded-full overflow-hidden border-2 border-green-400/50 bg-black/50 backdrop-blur-sm">
                            <img
                                src="/logo.jpg"
                                alt="MCPVOTS Logo"
                                className="w-full h-full object-cover animate-pulse"
                            />
                        </div>

                        {/* Animated corner elements */}
                        <div className="absolute -top-1 -left-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
                        <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '1.5s' }}></div>
                    </div>

                    {/* Animated MCPVOTS Text */}
                    <div className="mb-4">
                        <h1 className="text-4xl md:text-6xl font-mono font-bold text-green-400 animate-text-glow tracking-wider">
                            MCPVOTS
                        </h1>
                        <div className="text-green-300/80 font-mono text-sm mt-2 animate-pulse">
                            MAXIMUM COMPUTE PROTOCOL • VOTING OPTIMIZATION TRADING SYSTEM
                        </div>
                    </div>

                    {/* Intelligence Ticker */}
                    <div className="bg-gray-900/80 border border-green-400/30 rounded-lg p-4 mb-4 backdrop-blur-sm">
                        <div className="flex items-center justify-center space-x-2">
                            <Cpu className="h-5 w-5 text-green-400 animate-pulse" />
                            <span className="text-green-400 font-mono text-sm font-bold animate-pulse">
                                {currentIntelligence}
                            </span>
                            <Database className="h-5 w-5 text-green-400 animate-pulse" />
                        </div>
                    </div>
                </div>

                {/* Real-time Data Bar */}
                <div className="bg-gray-900/90 border border-green-400/30 rounded-lg p-4 mb-6 backdrop-blur-sm">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {/* Status */}
                        <div className="flex items-center space-x-3">
                            <Network className="h-4 w-4 text-green-400 animate-pulse" />
                            <div>
                                <div className="text-green-400 font-mono text-xs font-bold">STATUS</div>
                                <div className="text-green-400/80 font-mono text-sm animate-pulse">
                                    {currentStatus}
                                </div>
                            </div>
                        </div>

                        {/* Gas Price */}
                        <div className="flex items-center space-x-3">
                            <Zap className="h-4 w-4 text-green-400 animate-pulse" />
                            <div>
                                <div className="text-green-400 font-mono text-xs font-bold">GAS PRICE</div>
                                <div className="text-green-400/80 font-mono text-sm">
                                    {gasPrice} GWEI
                                </div>
                            </div>
                        </div>

                        {/* ETH Price */}
                        <div className="flex items-center space-x-3">
                            <div className="w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
                            <div>
                                <div className="text-green-400 font-mono text-xs font-bold">ETH PRICE</div>
                                <div className="text-green-400/80 font-mono text-sm">
                                    ${ethPrice}
                                </div>
                            </div>
                        </div>

                        {/* Chain Info */}
                        <div className="flex items-center space-x-3">
                            <div className="w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
                            <div>
                                <div className="text-green-400 font-mono text-xs font-bold">CHAIN</div>
                                <div className="text-green-400/80 font-mono text-sm">
                                    BASE • 8453
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Navigation Tabs */}
                <div className="mb-6">
                    <nav className="flex space-x-4">
                        {tabs.map((tab) => {
                            const Icon = tab.icon
                            const isActive = activeTab === tab.id
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center space-x-2 px-6 py-3 border rounded-lg transition-all duration-300 backdrop-blur-sm ${isActive
                                        ? 'border-green-400 text-green-400 bg-green-400/10 shadow-lg shadow-green-400/20'
                                        : 'border-green-400/30 text-green-400/70 hover:text-green-400 hover:border-green-400/50 hover:bg-green-400/5'
                                        }`}
                                >
                                    <Icon className={`h-4 w-4 ${isActive ? 'animate-pulse' : ''}`} />
                                    <span className="font-mono font-bold tracking-wide">{tab.label}</span>
                                </button>
                            )
                        })}
                    </nav>
                </div>

                {/* Main Content */}
                <div className="bg-gray-900/90 border border-green-400/30 p-6 rounded-lg backdrop-blur-sm">
                    <ActiveComponent />
                </div>
            </div>
        </div>
    )
}
