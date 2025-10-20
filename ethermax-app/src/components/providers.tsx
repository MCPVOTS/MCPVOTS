'use client'

import '@rainbow-me/rainbowkit/styles.css'

import {
    darkTheme,
    getDefaultConfig,
    RainbowKitProvider,
} from '@rainbow-me/rainbowkit'
import {
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query"
import { WagmiProvider } from 'wagmi'
import {
    arbitrum,
    base,
    bsc,
    mainnet,
    optimism,
    polygon,
} from 'wagmi/chains'

const config = getDefaultConfig({
    appName: 'MCPVOTS Dashboard',
    projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || '2f05a7db73b6e7a4e0b7e8a6c2f5a7db',
    chains: [base, mainnet, polygon, optimism, arbitrum, bsc],
    ssr: true,
})

const queryClient = new QueryClient()

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                <RainbowKitProvider
                    theme={darkTheme({
                        accentColor: '#00f2fe',
                        accentColorForeground: 'white',
                        borderRadius: 'none',
                        fontStack: 'system',
                        overlayBlur: 'none',
                    })}
                    modalSize="wide"
                    initialChain={base}
                    coolMode={true}
                    appInfo={{
                        appName: 'MCPVOTS Dashboard',
                        learnMoreUrl: 'https://base.org',
                    }}
                >
                    {children}
                </RainbowKitProvider>
            </QueryClientProvider>
        </WagmiProvider>
    )
}
