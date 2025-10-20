'use client'

import { useEffect, useState } from 'react'

interface IntroProps {
    onComplete: () => void
}

export function Intro({ onComplete }: IntroProps) {
    const [currentStep, setCurrentStep] = useState(0)
    const [scanLine, setScanLine] = useState(0)
    const [systemStatus, setSystemStatus] = useState({
        cpu: 0,
        memory: 0,
        network: 0,
        agents: 0
    })

    const steps = [
        {
            title: "INITIALIZING EtherMax TERMINAL",
            subtitle: "Loading core systems...",
            status: "BOOTING"
        },
        {
            title: "ESTABLISHING SECURE CONNECTIONS",
            subtitle: "Connecting to blockchain networks...",
            status: "CONNECTING"
        },
        {
            title: "ACTIVATING AI AGENTS",
            subtitle: "Initializing neural networks...",
            status: "CALIBRATING"
        },
        {
            title: "SYSTEM READY",
            subtitle: "All systems operational",
            status: "ONLINE"
        }
    ]

    useEffect(() => {
        // Scanning line animation
        const scanInterval = setInterval(() => {
            setScanLine(prev => (prev + 1) % 100)
        }, 50)

        // System status animation
        const statusInterval = setInterval(() => {
            setSystemStatus(prev => ({
                cpu: Math.min(prev.cpu + Math.random() * 5, 100),
                memory: Math.min(prev.memory + Math.random() * 4, 100),
                network: Math.min(prev.network + Math.random() * 6, 100),
                agents: Math.min(prev.agents + Math.random() * 3, 100)
            }))
        }, 100)

        // Step progression
        const stepTimers = steps.map((_, index) =>
            setTimeout(() => setCurrentStep(index), index * 1200)
        )

        // Complete intro
        const completeTimer = setTimeout(() => {
            onComplete()
        }, 5500)

        return () => {
            clearInterval(scanInterval)
            clearInterval(statusInterval)
            stepTimers.forEach(clearTimeout)
            clearTimeout(completeTimer)
        }
    }, [onComplete])

    return (
        <div className="min-h-screen bg-black relative overflow-hidden">
            {/* Matrix-style animated background */}
            <div className="absolute inset-0 opacity-20">
                <div className="w-full h-full animate-pulse" style={{
                    backgroundImage: `
                        linear-gradient(rgba(0, 255, 0, 0.1) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(0, 255, 0, 0.1) 1px, transparent 1px)
                    `,
                    backgroundSize: '30px 30px',
                    animation: 'matrix-rain 20s linear infinite'
                }}></div>
            </div>

            {/* Multiple scanning lines for matrix effect */}
            <div
                className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-green-400 to-transparent opacity-80 animate-pulse"
                style={{
                    top: `${scanLine}%`,
                    boxShadow: '0 0 30px rgba(0, 255, 0, 0.8)',
                    animation: 'scan-line 3s ease-in-out infinite'
                }}
            ></div>
            <div
                className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-cyan-300 to-transparent opacity-60"
                style={{
                    top: `${(scanLine + 30) % 100}%`,
                    boxShadow: '0 0 20px rgba(34, 211, 238, 0.6)',
                    animation: 'scan-line 4s ease-in-out infinite reverse'
                }}
            ></div>
            <div
                className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-orange-400 to-transparent opacity-40"
                style={{
                    top: `${(scanLine + 60) % 100}%`,
                    boxShadow: '0 0 15px rgba(255, 165, 0, 0.5)',
                    animation: 'scan-line 5s ease-in-out infinite'
                }}
            ></div>

            {/* Main terminal interface */}
            <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8">
                {/* Terminal header */}
                <div className="mb-8 text-center animate-fade-in">
                    <div className="mb-4">
                        <span className="text-green-400 font-mono text-lg tracking-wider animate-pulse font-bold">
                            EtherMax MATRIX TERMINAL v9.7.3
                        </span>
                    </div>
                    <div className="text-cyan-300/90 font-mono text-sm animate-bounce">
                        [NEURAL MATRIX] [QUANTUM SECURE] [AI ENHANCED]
                    </div>
                </div>

                {/* Main terminal window */}
                <div className="bg-black/95 backdrop-blur-sm border-2 border-green-400/80 rounded-lg p-8 relative overflow-hidden shadow-2xl max-w-4xl w-full animate-glow"
                    style={{
                        boxShadow: '0 0 60px rgba(0, 255, 0, 0.4), inset 0 0 60px rgba(0, 255, 0, 0.1)',
                        animation: 'terminal-glow 2s ease-in-out infinite alternate'
                    }}>

                    {/* Animated matrix border */}
                    <div className="absolute inset-0 border-2 border-cyan-400/60 rounded-lg animate-spin-slow"></div>
                    <div className="absolute inset-2 border border-orange-400/40 rounded-lg animate-pulse"></div>

                    {/* System status grid */}
                    <div className="grid grid-cols-4 gap-4 mb-8">
                        <div className="bg-slate-900/30 border border-cyan-400/40 rounded p-4 text-center">
                            <div className="text-cyan-300 font-mono text-sm font-bold mb-2">CPU</div>
                            <div className="text-cyan-200 font-mono text-xl mb-1">{Math.round(systemStatus.cpu)}%</div>
                            <div className="w-full bg-slate-800/50 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-cyan-500 to-cyan-400 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${systemStatus.cpu}%` }}
                                ></div>
                            </div>
                        </div>
                        <div className="bg-slate-900/30 border border-orange-400/40 rounded p-4 text-center">
                            <div className="text-orange-300 font-mono text-sm font-bold mb-2">MEMORY</div>
                            <div className="text-orange-200 font-mono text-xl mb-1">{Math.round(systemStatus.memory)}%</div>
                            <div className="w-full bg-slate-800/50 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-orange-500 to-orange-400 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${systemStatus.memory}%` }}
                                ></div>
                            </div>
                        </div>
                        <div className="bg-slate-900/30 border border-cyan-400/40 rounded p-4 text-center">
                            <div className="text-cyan-300 font-mono text-sm font-bold mb-2">NETWORK</div>
                            <div className="text-cyan-200 font-mono text-xl mb-1">{Math.round(systemStatus.network)}%</div>
                            <div className="w-full bg-slate-800/50 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-cyan-500 to-cyan-400 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${systemStatus.network}%` }}
                                ></div>
                            </div>
                        </div>
                        <div className="bg-slate-900/30 border border-orange-400/40 rounded p-4 text-center">
                            <div className="text-orange-300 font-mono text-sm font-bold mb-2">AGENTS</div>
                            <div className="text-orange-200 font-mono text-xl mb-1">{Math.round(systemStatus.agents)}%</div>
                            <div className="w-full bg-slate-800/50 rounded-full h-2">
                                <div
                                    className="bg-gradient-to-r from-orange-500 to-orange-400 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${systemStatus.agents}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    {/* Agent connections */}
                    <div className="mb-8">
                        <div className="text-cyan-300 font-mono text-sm mb-4 text-center">AGENT CONNECTIONS</div>
                        <div className="grid grid-cols-3 gap-4">
                            {['TRADE_AGENT', 'ANALYSIS_AGENT', 'RISK_AGENT'].map((agent, i) => (
                                <div key={agent} className="bg-slate-900/30 border border-cyan-400/40 rounded p-3 text-center">
                                    <div className="text-cyan-200 font-mono text-xs mb-2">{agent}</div>
                                    <div className="flex items-center justify-center space-x-2">
                                        <div className={`w-2 h-2 rounded-full ${systemStatus.agents > (i + 1) * 30 ? 'bg-cyan-400 animate-pulse' : 'bg-gray-600'}`}></div>
                                        <span className="text-cyan-300 font-mono text-xs">
                                            {systemStatus.agents > (i + 1) * 30 ? 'CONNECTED' : 'CONNECTING...'}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* MCPVOTS ASCII Art - Clean and Technological */}
                    <div className="text-center mb-8">
                        <div className="font-mono text-sm leading-none">
                            <pre className="text-cyan-300/90 animate-pulse" style={{
                                textShadow: '0 0 10px rgba(34, 211, 238, 0.5)',
                                fontSize: '12px',
                                lineHeight: '1.1'
                            }}>
                                {`███████╗████████╗██╗░░██╗███████╗██████╗░███╗░░░███╗░█████╗░██╗░░██╗
██╔════╝╚══██╔══╝██║░░██║██╔════╝██╔══██╗████╗░████║██╔══██╗╚██╗██╔╝
█████╗░░░░░██║░░░███████║█████╗░░██████╔╝██╔████╔██║███████║░╚███╔╝░
██╔══╝░░░░░██║░░░██╔══██║██╔══╝░░██╔══██╗██║╚██╔╝██║██╔══██║░██╔██╗░
███████╗░░░██║░░░██║░░██║███████╗██║░░██║██║░╚═╝░██║██║░░██║██╔╝╚██╗
╚══════╝░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝`}
                            </pre>
                        </div>
                        <div className="mt-4 text-center">
                            <div className="text-orange-400/80 font-mono text-xs tracking-widest animate-pulse">
                                EtherMax PROTOCOL • VOTING OPTIMIZATION TRADING SYSTEM
                            </div>
                            <div className="text-cyan-300/60 font-mono text-xs mt-1">
                                [QUANTUM NEURAL INTERFACE] [IPFS MINING NETWORK] [BASE NETWORK] [AI AGENTS]
                            </div>
                        </div>
                    </div>                    {/* Status indicator */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center space-x-3 bg-slate-900/30 border border-cyan-400/30 rounded-full px-6 py-3">
                            <div className={`w-3 h-3 rounded-full animate-pulse ${steps[currentStep]?.status === 'ONLINE' ? 'bg-cyan-400/70' :
                                steps[currentStep]?.status === 'CALIBRATING' ? 'bg-orange-400/70' :
                                    'bg-cyan-400/70'
                                }`}></div>
                            <span className="text-cyan-300/70 font-mono text-sm tracking-wider">
                                [{steps[currentStep]?.status || 'BOOTING'}]
                            </span>
                        </div>
                    </div>

                    {/* Progress bar */}
                    <div className="mt-8">
                        <div className="w-full bg-slate-800/50 rounded-full h-3 mb-2">
                            <div
                                className="bg-gradient-to-r from-cyan-500/70 via-cyan-400/70 to-cyan-500/70 h-3 rounded-full transition-all duration-500 ease-out"
                                style={{
                                    width: `${(currentStep + 1) * 25}%`,
                                    boxShadow: '0 0 10px rgba(34, 211, 238, 0.3)'
                                }}
                            ></div>
                        </div>
                        <div className="text-center text-cyan-300/70 font-mono text-sm">
                            INITIALIZATION: {Math.round((currentStep + 1) * 25)}%
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center">
                    <div className="text-cyan-300/50 font-mono text-xs tracking-wider">
                        © 2025 EtherMax | QUANTUM AI ECONOMICS | NEURAL INTERFACE v9.7.3
                    </div>
                    <div className="text-orange-300/40 font-mono text-xs mt-1">
                        [SECURE] [ENCRYPTED] [AI POWERED]
                    </div>
                </div>
            </div>
        </div>
    )
}
