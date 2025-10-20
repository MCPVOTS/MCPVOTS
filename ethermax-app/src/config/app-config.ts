export const APP_CONFIG = {
    version: '3.0.0',
    name: 'MCPVOTS',
    description: 'Maximum Compute Protocol • Voting Optimization Trading System',

    // Responsive breakpoints
    breakpoints: {
        mobile: 320,
        tablet: 768,
        desktop: 1024,
        wide: 1440,
        ultra: 1920
    },

    // Component sizing
    sizing: {
        mobile: {
            logo: { width: 48, height: 48 },
            button: { height: 44, padding: 12 },
            card: { padding: 16, margin: 8 },
            text: { h1: 24, h2: 20, body: 14 }
        },
        tablet: {
            logo: { width: 64, height: 64 },
            button: { height: 48, padding: 16 },
            card: { padding: 20, margin: 12 },
            text: { h1: 32, h2: 24, body: 16 }
        },
        desktop: {
            logo: { width: 80, height: 80 },
            button: { height: 52, padding: 20 },
            card: { padding: 24, margin: 16 },
            text: { h1: 48, h2: 32, body: 18 }
        }
    },

    // Animation timings
    animations: {
        intro: {
            duration: 4000, // 4 seconds
            phases: 6,
            typingSpeed: 20,
            phaseDelay: 600
        },
        transitions: {
            fast: 150,
            normal: 300,
            slow: 500
        }
    },

    // Feature flags
    features: {
        responsive: true,
        modular: true,
        versioning: true,
        threeJsIntro: true,
        walletIntegration: true
    },

    // API endpoints
    api: {
        baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
        websocket: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080'
    }
} as const

export type Breakpoint = keyof typeof APP_CONFIG.breakpoints
export type DeviceSize = 'mobile' | 'tablet' | 'desktop'
