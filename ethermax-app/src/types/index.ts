export interface MiningStats {
    miningRate: number
    totalMined: number
    status: 'active' | 'inactive' | 'paused'
    lastUpdate: Date
}

export interface StakingInfo {
    stakedAmount: number
    rewards: number
    apr: number
    lockPeriod: number
}

export interface LeaderboardEntry {
    rank: number
    address: string
    totalMined: number
    reputation: number
    rewards: number
}

export interface VOTSTokenInfo {
    balance: number
    staked: number
    rewards: number
    price: number
}
