/**
 * Advanced Theme System with Custom Properties
 * Enhanced dark/light theme management with accessibility features
 */

export interface ThemeConfig {
  name: string;
  displayName: string;
  type: 'light' | 'dark' | 'auto';
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    warning: string;
    error: string;
    info: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
    };
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

export class AdvancedThemeManager {
  private currentTheme: string = 'dark';
  private themes: Map<string, ThemeConfig> = new Map();
  private systemPreference: 'light' | 'dark' = 'dark';
  private observers: Function[] = [];
  private animationDuration: number = 200;

  constructor() {
    this.initializeThemes();
    this.detectSystemPreference();
    this.loadSavedTheme();
    this.applyTheme(this.currentTheme);
    this.setupSystemPreferenceListener();
  }

  private initializeThemes(): void {
    // Dark theme (default)
    this.themes.set('dark', {
      name: 'dark',
      displayName: 'Dark',
      type: 'dark',
      colors: {
        primary: '#3b82f6',
        secondary: '#6366f1',
        accent: '#10b981',
        background: '#0a0a0a',
        surface: '#1a1a1a',
        text: '#ffffff',
        textSecondary: '#a1a1aa',
        border: '#374151',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
      },
      spacing: {
        xs: '0.5rem',
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem',
        xl: '3rem'
      },
      typography: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem'
        }
      },
      shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      },
      borderRadius: {
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem'
      }
    });

    // Light theme
    this.themes.set('light', {
      name: 'light',
      displayName: 'Light',
      type: 'light',
      colors: {
        primary: '#2563eb',
        secondary: '#4f46e5',
        accent: '#059669',
        background: '#ffffff',
        surface: '#f8fafc',
        text: '#1f2937',
        textSecondary: '#6b7280',
        border: '#e5e7eb',
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626',
        info: '#2563eb'
      },
      spacing: {
        xs: '0.5rem',
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem',
        xl: '3rem'
      },
      typography: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem'
        }
      },
      shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
      },
      borderRadius: {
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem'
      }
    });

    // High contrast dark theme
    this.themes.set('high-contrast-dark', {
      name: 'high-contrast-dark',
      displayName: 'High Contrast Dark',
      type: 'dark',
      colors: {
        primary: '#00d4ff',
        secondary: '#ff6b6b',
        accent: '#51cf66',
        background: '#000000',
        surface: '#1a1a1a',
        text: '#ffffff',
        textSecondary: '#cccccc',
        border: '#ffffff',
        success: '#51cf66',
        warning: '#ffd43b',
        error: '#ff6b6b',
        info: '#00d4ff'
      },
      spacing: {
        xs: '0.5rem',
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem',
        xl: '3rem'
      },
      typography: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        fontSize: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem'
        }
      },
      shadows: {
        sm: '0 1px 2px 0 rgba(255, 255, 255, 0.1)',
        md: '0 4px 6px -1px rgba(255, 255, 255, 0.1)',
        lg: '0 10px 15px -3px rgba(255, 255, 255, 0.1)',
        xl: '0 20px 25px -5px rgba(255, 255, 255, 0.1)'
      },
      borderRadius: {
        sm: '0.25rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem'
      }
    });
  }

  private detectSystemPreference(): void {
    if (typeof window !== 'undefined' && window.matchMedia) {
      this.systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
  }

  private setupSystemPreferenceListener(): void {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', (e) => {
        this.systemPreference = e.matches ? 'dark' : 'light';
        if (this.currentTheme === 'auto') {
          this.applyTheme('auto');
        }
        this.notifyObservers();
      });
    }
  }

  private loadSavedTheme(): void {
    try {
      const savedTheme = localStorage.getItem('mcpvots-theme');
      if (savedTheme && this.themes.has(savedTheme)) {
        this.currentTheme = savedTheme;
      }
    } catch (error) {
      console.warn('Failed to load saved theme:', error);
    }
  }

  private saveTheme(themeName: string): void {
    try {
      localStorage.setItem('mcpvots-theme', themeName);
    } catch (error) {
      console.warn('Failed to save theme:', error);
    }
  }

  public setTheme(themeName: string): void {
    if (!this.themes.has(themeName) && themeName !== 'auto') {
      console.warn(`Theme "${themeName}" not found`);
      return;
    }

    this.currentTheme = themeName;
    this.saveTheme(themeName);
    this.applyTheme(themeName);
    this.notifyObservers();
  }

  public toggleTheme(): void {
    const nextTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(nextTheme);
  }

  public getCurrentTheme(): string {
    return this.currentTheme;
  }

  public getThemes(): ThemeConfig[] {
    return Array.from(this.themes.values());
  }

  public getThemeConfig(themeName?: string): ThemeConfig | null {
    const name = themeName || this.getEffectiveTheme();
    return this.themes.get(name) || null;
  }

  private getEffectiveTheme(): string {
    if (this.currentTheme === 'auto') {
      return this.systemPreference;
    }
    return this.currentTheme;
  }

  private applyTheme(themeName: string): void {
    const effectiveTheme = themeName === 'auto' ? this.systemPreference : themeName;
    const theme = this.themes.get(effectiveTheme);
    
    if (!theme) {
      console.warn(`Theme "${effectiveTheme}" not found`);
      return;
    }

    // Add transition class for smooth theme changes
    document.documentElement.classList.add('theme-transitioning');

    // Apply CSS custom properties
    const root = document.documentElement;
    
    // Colors
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Spacing
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value);
    });

    // Typography
    root.style.setProperty('--font-family', theme.typography.fontFamily);
    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value);
    });

    // Shadows
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value);
    });

    // Border radius
    Object.entries(theme.borderRadius).forEach(([key, value]) => {
      root.style.setProperty(`--radius-${key}`, value);
    });

    // Update data attribute for CSS selectors
    root.setAttribute('data-theme', effectiveTheme);
    root.setAttribute('data-theme-type', theme.type);

    // Update class names for compatibility
    root.classList.remove('light', 'dark');
    root.classList.add(theme.type);

    // Remove transition class after animation
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning');
    }, this.animationDuration);

    console.log(`Applied theme: ${effectiveTheme}`);
  }

  public addCustomTheme(themeConfig: ThemeConfig): void {
    this.themes.set(themeConfig.name, themeConfig);
    console.log(`Added custom theme: ${themeConfig.name}`);
  }

  public removeTheme(themeName: string): boolean {
    if (['dark', 'light'].includes(themeName)) {
      console.warn('Cannot remove built-in themes');
      return false;
    }

    const removed = this.themes.delete(themeName);
    if (removed && this.currentTheme === themeName) {
      this.setTheme('dark');
    }
    return removed;
  }

  public exportTheme(themeName: string): string | null {
    const theme = this.themes.get(themeName);
    if (!theme) {
      return null;
    }
    return JSON.stringify(theme, null, 2);
  }

  public importTheme(themeJson: string): boolean {
    try {
      const theme: ThemeConfig = JSON.parse(themeJson);
      
      // Validate theme structure
      if (!theme.name || !theme.colors || !theme.type) {
        throw new Error('Invalid theme structure');
      }

      this.addCustomTheme(theme);
      return true;
    } catch (error) {
      console.error('Failed to import theme:', error);
      return false;
    }
  }

  public onThemeChange(callback: Function): () => void {
    this.observers.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) {
        this.observers.splice(index, 1);
      }
    };
  }

  private notifyObservers(): void {
    const themeData = {
      current: this.currentTheme,
      effective: this.getEffectiveTheme(),
      config: this.getThemeConfig(),
      systemPreference: this.systemPreference
    };

    this.observers.forEach(callback => {
      try {
        callback(themeData);
      } catch (error) {
        console.error('Theme observer error:', error);
      }
    });

    // Dispatch custom event for non-class listeners
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: themeData 
      }));
    }
  }

  public getSystemPreference(): 'light' | 'dark' {
    return this.systemPreference;
  }

  public setAnimationDuration(duration: number): void {
    this.animationDuration = Math.max(0, duration);
  }

  public preloadThemes(): void {
    // Preload theme CSS if needed
    console.log('Theme preloading complete');
  }

  public destroy(): void {
    this.observers = [];
    console.log('Theme manager destroyed');
  }
}

// Create global instance
export const themeManager = new AdvancedThemeManager();

// Make it available on window for debugging
if (typeof window !== 'undefined') {
  (window as any).themeManager = themeManager;
}

export default themeManager;
