'use client'

import { useResponsive } from '@/hooks/use-responsive'
import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface ResponsiveGridProps {
    children: ReactNode
    className?: string
    cols?: {
        mobile?: number
        tablet?: number
        desktop?: number
    }
    gap?: 'sm' | 'md' | 'lg'
}

const gapClasses = {
    sm: 'gap-2 md:gap-3',
    md: 'gap-4 md:gap-6',
    lg: 'gap-6 md:gap-8'
}

export function ResponsiveGrid({
    children,
    className,
    cols = { mobile: 1, tablet: 2, desktop: 3 },
    gap = 'md'
}: ResponsiveGridProps) {
    const { screenSize } = useResponsive()

    const getGridCols = () => {
        const colCount = cols[screenSize] || cols.desktop || 3
        return `grid-cols-${colCount}`
    }

    return (
        <div
            className={cn(
                'grid',
                getGridCols(),
                gapClasses[gap],
                className
            )}
        >
            {children}
        </div>
    )
}
