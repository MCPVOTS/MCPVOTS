import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ThemeProvider } from '@/components/theme-provider'
import { QueryProvider } from '@/components/query-provider'
import { Toaster } from '@/components/ui/toaster'
import '@/styles/globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: {
    default: 'MCPVots - Modern MCP Integration Platform',
    template: '%s | MCPVots',
  },
  description: 'Next-generation Model Context Protocol integration platform with high-contrast dark theme and advanced AI capabilities.',
  keywords: ['MCP', 'Model Context Protocol', 'AI', 'Integration', 'Dark Theme', 'Accessibility'],
  authors: [{ name: 'MCPVots Team' }],
  creator: 'MCPVots Team',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://mcpvots.ai',
    siteName: 'MCPVots',
    title: 'MCPVots - Modern MCP Integration Platform',
    description: 'Next-generation Model Context Protocol integration platform with high-contrast dark theme and advanced AI capabilities.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'MCPVots Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MCPVots - Modern MCP Integration Platform',
    description: 'Next-generation Model Context Protocol integration platform with high-contrast dark theme and advanced AI capabilities.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#000000" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <QueryProvider>
            <div className="relative flex min-h-screen flex-col">
              <main className="flex-1">{children}</main>
            </div>
            <Toaster />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
