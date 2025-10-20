'use client'

import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface ResponsiveTextProps {
    children: ReactNode
    size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'
    weight?: 'normal' | 'medium' | 'semibold' | 'bold'
    className?: string
    as?: 'p' | 'span' | 'div' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
}

const sizeClasses = {
    xs: 'text-xs md:text-sm',
    sm: 'text-sm md:text-base',
    base: 'text-base md:text-lg',
    lg: 'text-lg md:text-xl',
    xl: 'text-xl md:text-2xl',
    '2xl': 'text-2xl md:text-3xl',
    '3xl': 'text-3xl md:text-4xl',
    '4xl': 'text-4xl md:text-5xl'
}

const weightClasses = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold'
}

export function ResponsiveText({
    children,
    size = 'base',
    weight = 'normal',
    className,
    as: Component = 'span'
}: ResponsiveTextProps) {
    return (
        <Component
            className={cn(
                sizeClasses[size],
                weightClasses[weight],
                className
            )}
        >
            {children}
        </Component>
    )
}
