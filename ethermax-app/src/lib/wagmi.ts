import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { arbitrum, base, mainnet, optimism, polygon, zkSync } from 'wagmi/chains'

const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || 'demo-project-id'

export const config = getDefaultConfig({
    appName: 'MCPVOTS',
    projectId,
    chains: [base, mainnet, polygon, arbitrum, optimism, zkSync],
    ssr: true, // Enable SSR but handle it properly in components
})

declare module 'wagmi' {
    interface Register {
        config: typeof config
    }
}
