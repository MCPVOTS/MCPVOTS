import { useQuery } from '@tanstack/react-query'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MCPVOTS_API_URL = process.env.NEXT_PUBLIC_MCPVOTS_API_URL || 'http://localhost:3001'

export interface MiningStats {
    miningRate: number
    totalMined: number
    status: 'active' | 'inactive' | 'paused'
    lastUpdate: string
}

export interface LeaderboardEntry {
    rank: number
    address: string
    totalMined: number
    reputation: number
    rewards: number
}

export function useMiningStats(address?: string) {
    return useQuery({
        queryKey: ['mining-stats', address],
        queryFn: async (): Promise<MiningStats> => {
            if (!address) {
                return {
                    miningRate: 0,
                    totalMined: 0,
                    status: 'inactive',
                    lastUpdate: new Date().toISOString()
                }
            }

            // In a real implementation, this would call the MCPVOTS API
            // For now, return mock data
            return {
                miningRate: 0.001,
                totalMined: Math.random() * 10,
                status: 'active',
                lastUpdate: new Date().toISOString()
            }
        },
        enabled: !!address,
        refetchInterval: 5000, // Refetch every 5 seconds
    })
}

export function useLeaderboard() {
    return useQuery({
        queryKey: ['leaderboard'],
        queryFn: async (): Promise<LeaderboardEntry[]> => {
            // Mock leaderboard data - in real app, fetch from MCPVOTS API
            return [
                {
                    rank: 1,
                    address: '0x1234...5678',
                    totalMined: 1250.5,
                    reputation: 98.5,
                    rewards: 250.0
                },
                {
                    rank: 2,
                    address: '0xabcd...efgh',
                    totalMined: 1180.2,
                    reputation: 95.2,
                    rewards: 200.0
                },
                {
                    rank: 3,
                    address: '0x9876...4321',
                    totalMined: 1050.8,
                    reputation: 92.1,
                    rewards: 150.0
                }
            ]
        },
        refetchInterval: 30000, // Refetch every 30 seconds
    })
}

export function useStakingInfo(address?: string) {
    return useQuery({
        queryKey: ['staking-info', address],
        queryFn: async () => {
            if (!address) {
                return {
                    stakedAmount: 0,
                    rewards: 0,
                    apr: 0,
                    lockPeriod: 0
                }
            }

            // Mock staking data
            return {
                stakedAmount: Math.random() * 1000,
                rewards: Math.random() * 100,
                apr: 12.5,
                lockPeriod: 30
            }
        },
        enabled: !!address,
    })
}
