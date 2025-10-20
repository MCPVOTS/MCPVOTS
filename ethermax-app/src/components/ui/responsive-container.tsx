'use client'

import { useResponsive } from '@/hooks/use-responsive'
import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface ResponsiveContainerProps {
    children: ReactNode
    className?: string
    maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
    padding?: 'none' | 'sm' | 'md' | 'lg'
}

const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-full'
}

const paddingClasses = {
    none: 'p-0',
    sm: 'p-2 md:p-4',
    md: 'p-4 md:p-6',
    lg: 'p-6 md:p-8'
}

export function ResponsiveContainer({
    children,
    className,
    maxWidth = '2xl',
    padding = 'md'
}: ResponsiveContainerProps) {
    const { isMobile, isTablet } = useResponsive()

    return (
        <div
            className={cn(
                'w-full mx-auto',
                maxWidthClasses[maxWidth],
                paddingClasses[padding],
                className
            )}
        >
            {children}
        </div>
    )
}
