'use client'

import { create } from 'ipfs-http-client'
import { useEffect, useState } from 'react'
import { useAccount, useWriteContract } from 'wagmi'

interface MiningStatus {
    isMining: boolean
    uptime: number
    peers: number
    dataPinned: number
    miningScore: number
    rewards: number
}

export function MiningDashboard() {
    const { address, isConnected } = useAccount()
    const [ipfs, setIpfs] = useState<any>(null)
    const [status, setStatus] = useState<MiningStatus>({
        isMining: false,
        uptime: 0,
        peers: 0,
        dataPinned: 0,
        miningScore: 0,
        rewards: 0
    })
    const [isMobile, setIsMobile] = useState(false)
    const [startTime, setStartTime] = useState<Date | null>(null)

    // Mock reward contract ABI (replace with actual)
    const rewardContractABI = [
        {
            inputs: [{ name: 'score', type: 'uint256' }],
            name: 'claimMiningReward',
            outputs: [],
            stateMutability: 'nonpayable',
            type: 'function'
        }
    ]

    const { writeContract } = useWriteContract()

    const generateSignature = async (message: string): Promise<string> => {
        // In browser, we'd use wallet to sign, but for demo use HMAC
        const encoder = new TextEncoder()
        const key = await crypto.subtle.importKey(
            'raw',
            encoder.encode('mining-secret-key'), // Use env var in production
            { name: 'HMAC', hash: 'SHA-256' },
            false,
            ['sign']
        )
        const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(message))
        return Array.from(new Uint8Array(signature))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('')
    }

    useEffect(() => {
        // Detect if mobile
        const userAgent = navigator.userAgent
        setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent))

        // Initialize IPFS client (public gateway)
        const initIPFS = async () => {
            try {
                const client = create({ url: 'https://ipfs.infura.io:5001/api/v0' })
                setIpfs(client)
            } catch (error) {
                console.error('Failed to initialize IPFS:', error)
            }
        }
        initIPFS()
    }, [])

    const startMining = async () => {
        if (!ipfs) return

        setStatus(prev => ({ ...prev, isMining: true }))
        setStartTime(new Date())

        // Pin some ecosystem data
        try {
            const data = JSON.stringify({
                ecosystem: 'MCPVOTS',
                timestamp: new Date().toISOString(),
                user: address
            })
            const result = await ipfs.add(data)
            console.log('Pinned data:', result.cid.toString())

            setStatus(prev => ({
                ...prev,
                dataPinned: prev.dataPinned + data.length
            }))
        } catch (error) {
            console.error('Failed to pin data:', error)
        }

        // Start mining loop
        const miningInterval = setInterval(async () => {
            if (!status.isMining) {
                clearInterval(miningInterval)
                return
            }

            try {
                // Get peers
                const peers = await ipfs.swarm.peers()
                const uptime = startTime ? (Date.now() - startTime.getTime()) / 1000 / 3600 : 0

                // Calculate score (simplified)
                const score = uptime * peers.length * (1 + status.dataPinned / 1000)

                setStatus(prev => ({
                    ...prev,
                    peers: peers.length,
                    uptime: uptime,
                    miningScore: score
                }))

                // Report to mining API with signature
                const message = `${address}:${uptime}:${peers.length}:${status.dataPinned}:${score}`
                const signature = await generateSignature(message)

                await fetch('/api/mining/report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        address,
                        uptime,
                        peers: peers.length,
                        dataPinned: status.dataPinned,
                        score,
                        signature
                    })
                })

            } catch (error) {
                console.error('Mining cycle error:', error)
            }
        }, 60000) // Every minute
    }

    const stopMining = () => {
        setStatus(prev => ({ ...prev, isMining: false }))
        setStartTime(null)
    }

    const claimRewards = () => {
        if (!isConnected || status.miningScore < 10) return

        writeContract({
            address: '0x...' as `0x${string}`, // Replace with actual contract address
            abi: rewardContractABI,
            functionName: 'claimMiningReward',
            args: [BigInt(Math.floor(status.miningScore * 100))]
        })
    }

    const downloadPythonScript = () => {
        // Create download link for Python script
        const link = document.createElement('a')
        link.href = '/ipfs_mining.py' // Assuming script is served from public
        link.download = 'ipfs_mining.py'
        link.click()
    }

    return (
        <div className="bg-black/90 backdrop-blur-sm border-2 border-green-400/60 rounded-lg p-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-green-400 mb-4 text-center">
                MCPVOTS IPFS Mining
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-green-900/20 border border-green-400/30 rounded p-4 text-center">
                    <div className="text-green-400 font-mono text-sm">Status</div>
                    <div className="text-green-300 font-mono text-lg">
                        {status.isMining ? 'MINING' : 'STOPPED'}
                    </div>
                </div>
                <div className="bg-green-900/20 border border-green-400/30 rounded p-4 text-center">
                    <div className="text-green-400 font-mono text-sm">Mining Score</div>
                    <div className="text-green-300 font-mono text-lg">
                        {status.miningScore.toFixed(2)}
                    </div>
                </div>
                <div className="bg-green-900/20 border border-green-400/30 rounded p-4 text-center">
                    <div className="text-green-400 font-mono text-sm">Peers</div>
                    <div className="text-green-300 font-mono text-lg">{status.peers}</div>
                </div>
                <div className="bg-green-900/20 border border-green-400/30 rounded p-4 text-center">
                    <div className="text-green-400 font-mono text-sm">Uptime (hrs)</div>
                    <div className="text-green-300 font-mono text-lg">{status.uptime.toFixed(1)}</div>
                </div>
            </div>

            <div className="flex flex-col gap-4">
                {!status.isMining ? (
                    <button
                        onClick={startMining}
                        className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                        disabled={!ipfs}
                    >
                        {isMobile ? 'Start Browser Mining' : 'Start Mining'}
                    </button>
                ) : (
                    <button
                        onClick={stopMining}
                        className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                    >
                        Stop Mining
                    </button>
                )}

                {isConnected && status.miningScore >= 10 && (
                    <button
                        onClick={claimRewards}
                        className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                    >
                        Claim Rewards ({status.rewards} MCPVOTS)
                    </button>
                )}

                {!isMobile && (
                    <button
                        onClick={downloadPythonScript}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                    >
                        Download PC Mining Script
                    </button>
                )}

                <div className="text-center text-green-300/70 font-mono text-sm">
                    {isMobile
                        ? 'Browser mining provides limited rewards. For full mining, use PC with Python script.'
                        : 'PC users get full mining rewards. Mobile users can mine via browser.'
                    }
                </div>
            </div>
        </div>
    )
}
