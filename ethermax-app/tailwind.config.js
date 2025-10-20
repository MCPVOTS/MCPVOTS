/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                border: 'hsl(var(--border))',
                input: 'hsl(var(--input))',
                ring: 'hsl(var(--ring))',
                background: 'hsl(var(--background))',
                foreground: 'hsl(var(--foreground))',
                primary: {
                    DEFAULT: 'hsl(var(--primary))',
                    foreground: 'hsl(var(--primary-foreground))',
                },
                secondary: {
                    DEFAULT: 'hsl(var(--secondary))',
                    foreground: 'hsl(var(--secondary-foreground))',
                },
                destructive: {
                    DEFAULT: 'hsl(var(--destructive))',
                    foreground: 'hsl(var(--destructive-foreground))',
                },
                muted: {
                    DEFAULT: 'hsl(var(--muted))',
                    foreground: 'hsl(var(--muted-foreground))',
                },
                accent: {
                    DEFAULT: 'hsl(var(--accent))',
                    foreground: 'hsl(var(--accent-foreground))',
                },
                popover: {
                    DEFAULT: 'hsl(var(--popover))',
                    foreground: 'hsl(var(--popover-foreground))',
                },
                card: {
                    DEFAULT: 'hsl(var(--card))',
                    foreground: 'hsl(var(--card-foreground))',
                },
            },
            borderRadius: {
                lg: 'var(--radius)',
                md: 'calc(var(--radius) - 2px)',
                sm: 'calc(var(--radius) - 4px)',
            },
            animation: {
                'cube-float': 'cube-float 8s ease-in-out infinite',
                'cube-pulse': 'cube-pulse 3s ease-in-out infinite',
                'cube-orbit': 'cube-orbit 6s linear infinite',
                'cube-text': 'cube-text 4s ease-in-out infinite',
                'cube-glitch': 'cube-glitch 2s ease-in-out infinite',
                'cube-fade-in': 'cube-fade-in 1s ease-out',
                'cube-terminal': 'cube-terminal 3s ease-in-out infinite',
                'cube-line': 'cube-line 0.5s ease-out',
                'cube-typewriter': 'cube-typewriter 2s steps(40, end)',
                'cube-text-reveal': 'cube-text-reveal 0.8s ease-out',
                'cube-progress': 'cube-progress 2s ease-out',
                'cube-scan': 'cube-scan 2s linear infinite',
                'cube-progress-left': 'cube-progress-left 1s ease-in-out infinite',
                'cube-progress-right': 'cube-progress-right 1s ease-in-out infinite',
                'cube-corner': 'cube-corner 4s ease-in-out infinite',
                'cube-dot': 'cube-dot 2s ease-in-out infinite',
                'cube-icon': 'cube-icon 3s ease-in-out infinite',
                'cube-corner-element': 'cube-corner-element 0.6s ease-out',
                'spin-ring': 'spin-ring 3s linear infinite',
                'gradient-shift': 'gradient-shift 4s ease-in-out infinite',
                'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
                'text-glow': 'text-glow 2s ease-in-out infinite',
            },
            keyframes: {
                'spin-ring': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                },
                'gradient-shift': {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                'glow-pulse': {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(34, 197, 94, 0.5), 0 0 10px rgba(34, 197, 94, 0.3), 0 0 15px rgba(34, 197, 94, 0.1)' },
                    '50%': { boxShadow: '0 0 10px rgba(34, 197, 94, 0.8), 0 0 20px rgba(34, 197, 94, 0.6), 0 0 30px rgba(34, 197, 94, 0.3)' },
                },
                'text-glow': {
                    '0%, 100%': { textShadow: '0 0 5px rgba(34, 197, 94, 0.5), 0 0 10px rgba(34, 197, 94, 0.3)' },
                    '50%': { textShadow: '0 0 10px rgba(34, 197, 94, 0.8), 0 0 20px rgba(34, 197, 94, 0.6)' },
                },
            },
        },
    },
    plugins: [],
}
