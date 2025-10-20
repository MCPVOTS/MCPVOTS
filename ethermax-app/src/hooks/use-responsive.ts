'use client'

import { APP_CONFIG, DeviceSize } from '@/config/app-config'
import { useEffect, useState } from 'react'

export function useResponsive() {
    const [screenSize, setScreenSize] = useState<DeviceSize>('desktop')
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

    useEffect(() => {
        const updateDimensions = () => {
            const width = window.innerWidth
            const height = window.innerHeight

            setDimensions({ width, height })

            if (width < APP_CONFIG.breakpoints.tablet) {
                setScreenSize('mobile')
            } else if (width < APP_CONFIG.breakpoints.desktop) {
                setScreenSize('tablet')
            } else {
                setScreenSize('desktop')
            }
        }

        updateDimensions()
        window.addEventListener('resize', updateDimensions)

        return () => window.removeEventListener('resize', updateDimensions)
    }, [])

    const isMobile = screenSize === 'mobile'
    const isTablet = screenSize === 'tablet'
    const isDesktop = screenSize === 'desktop'

    const getResponsiveValue = <T>(values: { mobile: T; tablet: T; desktop: T }): T => {
        return values[screenSize]
    }

    return {
        screenSize,
        dimensions,
        isMobile,
        isTablet,
        isDesktop,
        getResponsiveValue,
        breakpoints: APP_CONFIG.breakpoints
    }
}
