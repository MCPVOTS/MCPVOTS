'use client'

import { AppNavigation } from '@/components/app-navigation'
import { Intro } from '@/components/intro'
import { useEffect, useState } from 'react'

export const dynamic = 'force-dynamic'

export default function Home() {
    const [showIntro, setShowIntro] = useState(true)

    const handleIntroComplete = () => {
        setShowIntro(false)
    }

    // Auto-hide intro after 5 seconds as fallback
    useEffect(() => {
        const timer = setTimeout(() => {
            setShowIntro(false)
        }, 5000)

        return () => clearTimeout(timer)
    }, [])

    if (showIntro) {
        return <Intro onComplete={handleIntroComplete} />
    }

    return <AppNavigation />
}
