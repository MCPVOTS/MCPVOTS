/**
 * Theme Context Provider
 * Manages dark/light theme state and transitions across the React application
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Theme = 'light' | 'dark' | 'auto';

export interface ThemeContextType {
  theme: Theme;
  effectiveTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isHighContrast: boolean;
  setHighContrast: (enabled: boolean) => void;
  accentColor: string;
  setAccentColor: (color: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export interface ThemeProviderProps {
  children: ReactNode;
}

const STORAGE_KEYS = {
  THEME: 'mcpvots-theme',
  HIGH_CONTRAST: 'mcpvots-high-contrast',
  ACCENT_COLOR: 'mcpvots-accent-color',
};

const ACCENT_COLORS = {
  blue: '#3b82f6',
  green: '#10b981',
  purple: '#8b5cf6',
  cyan: '#06b6d4',
  orange: '#f59e0b',
  red: '#ef4444',
};

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>('dark');
  const [isHighContrast, setHighContrastState] = useState(false);
  const [accentColor, setAccentColorState] = useState(ACCENT_COLORS.blue);

  // Calculate effective theme based on system preference
  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>('dark');

  // Load saved preferences
  useEffect(() => {
    const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME) as Theme;
    const savedHighContrast = localStorage.getItem(STORAGE_KEYS.HIGH_CONTRAST) === 'true';
    const savedAccentColor = localStorage.getItem(STORAGE_KEYS.ACCENT_COLOR);

    if (savedTheme) {
      setThemeState(savedTheme);
    }
    
    setHighContrastState(savedHighContrast);
    
    if (savedAccentColor && Object.values(ACCENT_COLORS).includes(savedAccentColor)) {
      setAccentColorState(savedAccentColor);
    }
  }, []);

  // Update effective theme based on theme and system preference
  useEffect(() => {
    const updateEffectiveTheme = () => {
      if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setEffectiveTheme(prefersDark ? 'dark' : 'light');
      } else {
        setEffectiveTheme(theme);
      }
    };

    updateEffectiveTheme();

    if (theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', updateEffectiveTheme);
      
      return () => {
        mediaQuery.removeEventListener('change', updateEffectiveTheme);
      };
    }
  }, [theme]);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove('light', 'dark', 'high-contrast');
    
    // Add current theme class
    root.classList.add(effectiveTheme);
    
    if (isHighContrast) {
      root.classList.add('high-contrast');
    }

    // Update CSS custom properties for accent color
    root.style.setProperty('--accent-primary', accentColor);

    // Update meta theme-color for mobile browsers
    const themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (themeColorMeta) {
      themeColorMeta.setAttribute('content', effectiveTheme === 'dark' ? '#0a0a0a' : '#ffffff');
    }

    // Announce theme change for screen readers
    const announcement = `Theme changed to ${effectiveTheme}${isHighContrast ? ' high contrast' : ''}`;
    announceToScreenReader(announcement);
  }, [effectiveTheme, isHighContrast, accentColor]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(STORAGE_KEYS.THEME, newTheme);
  };

  const toggleTheme = () => {
    const newTheme = effectiveTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  };

  const setHighContrast = (enabled: boolean) => {
    setHighContrastState(enabled);
    localStorage.setItem(STORAGE_KEYS.HIGH_CONTRAST, enabled.toString());
  };

  const setAccentColor = (color: string) => {
    setAccentColorState(color);
    localStorage.setItem(STORAGE_KEYS.ACCENT_COLOR, color);
  };

  const value: ThemeContextType = {
    theme,
    effectiveTheme,
    setTheme,
    toggleTheme,
    isHighContrast,
    setHighContrast,
    accentColor,
    setAccentColor,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// Utility function to announce changes to screen readers
function announceToScreenReader(message: string) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.setAttribute('class', 'sr-only');
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}
