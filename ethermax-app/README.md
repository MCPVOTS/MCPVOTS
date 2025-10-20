# EtherMax - VOTS Mining & Staking App

A modern Next.js 15 application for mining and staking VOTS tokens in the MCPVOTS ecosystem.

## Features

- 🚀 Next.js 15 with App Router
- 🌐 Base network integration
- 💰 RainbowKit wallet connection
- ⛏️ Real-time VOTS mining dashboard
- 🏦 VOTS staking interface
- 🏆 Leaderboard with rankings
- 📊 Live statistics and analytics
- 🎨 Modern UI with Tailwind CSS

## Tech Stack

- **Framework:** Next.js 15
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Web3:** Wagmi v2, RainbowKit, Viem
- **State Management:** TanStack Query
- **Backend:** MCPVOTS API integration

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Add your WalletConnect Project ID:
```
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_project_id
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                 # Next.js app router pages
├── components/          # React components
│   ├── mining-dashboard.tsx
│   ├── wallet-connect.tsx
│   └── providers.tsx
├── lib/                 # Utility functions and configs
│   └── wagmi.ts
├── hooks/               # Custom React hooks
└── types/               # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Environment Variables

- `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID` - WalletConnect project ID for wallet connections

## Contributing

This is part of the MCPVOTS ecosystem. See the main repository for contribution guidelines.
