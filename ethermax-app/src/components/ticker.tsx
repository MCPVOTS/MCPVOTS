'use client'

export function Ticker({ items = [] }: { items?: string[] }) {
    const messages = items.length ? items : [
        'MCPVOTS — Real-time Base network insights',
        'Agent Performance Analytics: latency, success-rate, reward-efficiency',
        'Market Intelligence: predictive indicators, top movers',
        'Staking = governance (sVOTS) — secure the system, shape the future',
    ]

    return (
        <div className="overflow-hidden border-t border-b border-green-400/10 bg-black/30">
            <div className="relative text-sm text-green-300 font-mono whitespace-nowrap">
                <div className="inline-block ticker-track">
                    {messages.concat(messages).map((m, i) => (
                        <span key={i} className="inline-block px-8 py-2 opacity-90">
                            <span className="text-green-400/75 mr-3">»</span>
                            {m}
                        </span>
                    ))}
                </div>
            </div>

            <style>{`
                .ticker-track{
                    animation: ticker 26s linear infinite;
                    white-space: nowrap;
                }

                @keyframes ticker{
                    0%{ transform: translateX(0%); }
                    100%{ transform: translateX(-50%); }
                }
            `}</style>
        </div>
    )
}
