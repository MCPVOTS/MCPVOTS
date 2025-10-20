'use client'

import { useEffect, useState } from 'react'

export function BaseInsightPopup({ address }: { address?: string }) {
    const [visible, setVisible] = useState(true)
    const [streamLines, setStreamLines] = useState<string[]>([])

    useEffect(() => {
        // fake stream data
        const lines = [
            `Base: avg-block-time 2.1s, tx/s 72`,
            `Active validators: 21`,
            `Gas price median: 8 gwei`,
            `Top token movers: VOTS, USDC, WETH`,
        ]
        let idx = 0
        setStreamLines([])
        const t = setInterval(() => {
            setStreamLines((s) => [lines[idx % lines.length], ...s].slice(0, 6))
            idx += 1
        }, 600)

        return () => clearInterval(t)
    }, [address])

    if (!visible) return null

    return (
        <div className="absolute right-0 top-full mt-3 w-96 bg-black/80 border border-orange-400/20 rounded-lg p-4 backdrop-blur-md shadow-2xl shadow-orange-400/10 animate-fade-in">
            <div className="flex justify-between items-center mb-2">
                <div className="text-xs font-mono text-orange-300">BASE NETWORK INSIGHT</div>
                <button
                    onClick={() => setVisible(false)}
                    className="text-orange-400/60 hover:text-orange-400 text-xs font-mono"
                >
                    ✕
                </button>
            </div>
            <div className="space-y-1 text-sm font-mono text-green-300">
                {streamLines.map((l, i) => (
                    <div key={i} className="flex items-center space-x-2 opacity-90">
                        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" />
                        <div className="truncate">{l}</div>
                    </div>
                ))}
            </div>
        </div>
    )
}

/* animations */
const style = `
@keyframes fadeIn { from { opacity: 0; transform: translateY(-6px) } to { opacity: 1; transform: translateY(0) } }
.animate-fade-in { animation: fadeIn 220ms ease-out; }
`

if (typeof document !== 'undefined') {
    const id = 'mcpvots-popup-style'
    if (!document.getElementById(id)) {
        const s = document.createElement('style')
        s.id = id
        s.innerHTML = style
        document.head.appendChild(s)
    }
}
