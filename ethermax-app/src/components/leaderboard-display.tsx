'use client'

import { useLeaderboard } from '@/hooks/use-mcpvots'
import { Award, Crown, Medal, Trophy } from 'lucide-react'

const rankIcons = {
    1: Crown,
    2: Medal,
    3: Award,
    default: Trophy
}

const rankColors = {
    1: 'text-green-400',
    2: 'text-emerald-400',
    3: 'text-lime-400',
    default: 'text-green-400/70'
}

export function LeaderboardDisplay() {
    const { data: leaderboard, isLoading } = useLeaderboard()

    if (isLoading) {
        return (
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-700 rounded w-1/3 mb-6"></div>
                    <div className="space-y-4">
                        {[...Array(10)].map((_, i) => (
                            <div key={i} className="h-16 bg-gray-700 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6 animate-fade-in">
                <div className="flex items-center mb-6">
                    <Trophy className="h-6 w-6 text-green-400 mr-3 animate-pulse" />
                    <h2 className="text-green-400 font-mono text-xl font-bold tracking-wide animate-glow">
                        WELCOME TO MCPVOTS
                    </h2>
                </div>

                <div className="p-4 bg-green-900/20 border border-green-400/30 rounded">
                    <h3 className="text-green-400 font-mono text-sm font-bold mb-2 tracking-wide">
                        TOP PERFORMERS
                    </h3>
                    <p className="text-green-400/70 font-mono text-sm">
                        Compete with other miners to earn VOTS rewards and climb the rankings!
                        Top 10 miners receive bonus rewards every week.
                    </p>
                </div>
            </div>

            {/* Leaderboard Entries */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                        [RANKINGS]
                    </h3>
                </div>

                <div className="space-y-3">
                    {leaderboard?.map((entry, index) => {
                        const RankIcon = rankIcons[entry.rank as keyof typeof rankIcons] || rankIcons.default
                        const rankColor = rankColors[entry.rank as keyof typeof rankColors] || rankColors.default

                        return (
                            <div
                                key={entry.rank}
                                className={`flex items-center justify-between p-4 rounded border transition-all duration-300 hover:border-green-400/50 hover:shadow-lg hover:shadow-green-400/10 transform hover:scale-[1.02] animate-slide-in ${entry.rank <= 3
                                    ? 'bg-green-900/10 border-green-400/30 animate-glow-subtle'
                                    : 'bg-gray-800 border-green-400/20'
                                    }`}
                                style={{
                                    animationDelay: `${index * 100}ms`,
                                    animationFillMode: 'both'
                                }}
                            >
                                <div className="flex items-center space-x-4">
                                    <div className={`flex items-center justify-center w-10 h-10 rounded border ${entry.rank <= 3 ? 'border-green-400/50 bg-green-900/20' : 'border-green-400/30 bg-gray-700'
                                        }`}>
                                        <RankIcon className={`h-5 w-5 ${rankColor}`} />
                                    </div>

                                    <div>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-green-400 font-mono text-lg font-bold">
                                                #{entry.rank}
                                            </span>
                                            {entry.rank <= 3 && (
                                                <span className="px-2 py-1 text-xs font-mono font-bold bg-green-400/20 text-green-400 border border-green-400/50 rounded tracking-wide">
                                                    TOP {entry.rank}
                                                </span>
                                            )}
                                        </div>
                                        <p className="font-mono text-xs text-green-400/60">
                                            {entry.address}
                                        </p>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-green-400 font-mono font-bold">
                                        {entry.totalMined.toFixed(2)} VOTS
                                    </div>
                                    <div className="text-green-400/50 font-mono text-xs">
                                        MINED
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-emerald-400 font-mono font-bold">
                                        {entry.reputation.toFixed(1)}%
                                    </div>
                                    <div className="text-green-400/50 font-mono text-xs">
                                        REPUTATION
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-lime-400 font-mono font-bold">
                                        {entry.rewards.toFixed(2)}
                                    </div>
                                    <div className="text-green-400/50 font-mono text-xs">
                                        REWARDS
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* How Rankings Work */}
            <div className="bg-gray-900 border border-green-400/30 rounded-lg p-6">
                <div className="border-b border-green-400/30 pb-3 mb-4">
                    <h3 className="text-green-400 font-mono text-lg font-bold tracking-wide">
                        [RANKING SYSTEM]
                    </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="p-3 bg-gray-800 border border-green-400/20 rounded">
                        <strong className="text-green-400 font-mono text-sm font-bold block mb-1">MINING VOLUME</strong>
                        <span className="text-green-400/70 font-mono text-xs">Total VOTS mined over time</span>
                    </div>
                    <div className="p-3 bg-gray-800 border border-green-400/20 rounded">
                        <strong className="text-green-400 font-mono text-sm font-bold block mb-1">REPUTATION</strong>
                        <span className="text-green-400/70 font-mono text-xs">Based on successful transactions and community standing</span>
                    </div>
                    <div className="p-3 bg-gray-800 border border-green-400/20 rounded">
                        <strong className="text-green-400 font-mono text-sm font-bold block mb-1">REWARDS</strong>
                        <span className="text-green-400/70 font-mono text-xs">Bonus VOTS earned from leaderboard position</span>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="text-center">
                <p className="text-green-400/60 font-mono text-sm">
                    Rankings update every 5 minutes. Keep mining to climb the leaderboard!
                </p>
            </div>
        </div>
    )
}

/* Enhanced Animations */
const style = `
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes glow {
    0%, 100% { text-shadow: 0 0 5px #10b981, 0 0 10px #10b981, 0 0 15px #10b981; }
    50% { text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 30px #10b981; }
}

@keyframes glowSubtle {
    0%, 100% { box-shadow: 0 0 5px rgba(251, 191, 36, 0.3); }
    50% { box-shadow: 0 0 15px rgba(251, 191, 36, 0.5), 0 0 25px rgba(251, 191, 36, 0.3); }
}

.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-slide-in { animation: slideIn 0.5s ease-out; }
.animate-glow { animation: glow 2s ease-in-out infinite; }
.animate-glow-subtle { animation: glowSubtle 3s ease-in-out infinite; }
`

if (typeof document !== 'undefined') {
    const id = 'leaderboard-animations'
    if (!document.getElementById(id)) {
        const s = document.createElement('style')
        s.id = id
        s.innerHTML = style
        document.head.appendChild(s)
    }
}
