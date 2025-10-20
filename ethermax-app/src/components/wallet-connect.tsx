'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'

export function WalletConnect() {
    return (
        <div className="terminal-wallet-connect">
            <ConnectButton.Custom>
                {({
                    account,
                    chain,
                    openAccountModal,
                    openChainModal,
                    openConnectModal,
                    authenticationStatus,
                    mounted,
                }) => {
                    const ready = mounted && authenticationStatus !== 'loading'
                    const connected =
                        ready &&
                        account &&
                        chain &&
                        (!authenticationStatus ||
                            authenticationStatus === 'authenticated')

                    return (
                        <div
                            {...(!ready && {
                                'aria-hidden': true,
                                'style': {
                                    opacity: 0,
                                    pointerEvents: 'none',
                                    userSelect: 'none',
                                },
                            })}
                        >
                            {(() => {
                                if (!connected) {
                                    return (
                                        <button
                                            onClick={openConnectModal}
                                            type="button"
                                            className="bg-green-400/10 hover:bg-green-400/20 text-green-400 border border-green-400/50 px-4 py-2 rounded font-mono text-sm font-bold tracking-wide transition-all duration-200 hover:shadow-lg hover:shadow-green-400/20"
                                        >
                                            [CONNECT WALLET]
                                        </button>
                                    )
                                }

                                if (chain.unsupported) {
                                    return (
                                        <button
                                            onClick={openChainModal}
                                            type="button"
                                            className="bg-red-400/10 hover:bg-red-400/20 text-red-400 border border-red-400/50 px-4 py-2 rounded font-mono text-sm font-bold tracking-wide transition-all duration-200"
                                        >
                                            [UNSUPPORTED NETWORK]
                                        </button>
                                    )
                                }

                                return (
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={openChainModal}
                                            type="button"
                                            className="bg-green-400/10 hover:bg-green-400/20 text-green-400 border border-green-400/50 px-3 py-2 rounded font-mono text-sm font-bold tracking-wide transition-all duration-200 flex items-center space-x-2"
                                        >
                                            <span>{chain.name}</span>
                                        </button>

                                        <button
                                            onClick={openAccountModal}
                                            type="button"
                                            className="bg-green-400/10 hover:bg-green-400/20 text-green-400 border border-green-400/50 px-3 py-2 rounded font-mono text-sm font-bold tracking-wide transition-all duration-200"
                                        >
                                            {account.displayName}
                                            {account.displayBalance
                                                ? ` (${account.displayBalance})`
                                                : ''}
                                        </button>
                                    </div>
                                )
                            })()}
                        </div>
                    )
                }}
            </ConnectButton.Custom>
        </div>
    )
}
