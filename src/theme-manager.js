// MCPVots Theme Manager - Advanced Dark/Light Theme System
class ThemeManager {
    constructor() {
        this.currentTheme = this.getInitialTheme();
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.bindEventListeners();
        this.setupSystemThemeListener();
        console.log(`Theme Manager initialized with ${this.currentTheme} theme`);
    }

    getInitialTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem('mcpvots-theme');
        if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
            return savedTheme;
        }

        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return prefersDark ? 'dark' : 'light';
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
        const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

        if (theme === 'dark') {
            html.classList.add('dark');
            if (themeToggleLightIcon) themeToggleLightIcon.classList.remove('hidden');
            if (themeToggleDarkIcon) themeToggleDarkIcon.classList.add('hidden');
        } else {
            html.classList.remove('dark');
            if (themeToggleDarkIcon) themeToggleDarkIcon.classList.remove('hidden');
            if (themeToggleLightIcon) themeToggleLightIcon.classList.add('hidden');
        }

        // Save to localStorage
        localStorage.setItem('mcpvots-theme', theme);
        this.currentTheme = theme;

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: this.currentTheme }
        }));

        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }

        const color = theme === 'dark' ? '#0a0a0a' : '#ffffff';
        metaThemeColor.content = color;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        
        // Add a subtle transition effect
        this.addTransitionEffect();
        
        console.log(`Theme switched to ${newTheme}`);
    }

    addTransitionEffect() {
        // Add a subtle flash effect when switching themes
        const body = document.body;
        body.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            body.style.transition = '';
        }, 300);
    }

    bindEventListeners() {
        const themeToggleButton = document.getElementById('theme-toggle');
        if (themeToggleButton) {
            themeToggleButton.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Keyboard shortcut: Ctrl+Shift+T
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    setupSystemThemeListener() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', (e) => {
            // Only auto-switch if user hasn't manually set a preference
            const hasUserPreference = localStorage.getItem('mcpvots-theme');
            if (!hasUserPreference) {
                const systemTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(systemTheme);
                console.log(`Auto-switched to ${systemTheme} theme based on system preference`);
            }
        });
    }

    // Public methods for external use
    getTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            this.applyTheme(theme);
        } else {
            console.warn(`Invalid theme: ${theme}. Use 'light' or 'dark'.`);
        }
    }

    // Advanced features
    scheduleThemeSwitch(hour, theme) {
        const now = new Date();
        const switchTime = new Date();
        switchTime.setHours(hour, 0, 0, 0);
        
        if (switchTime <= now) {
            switchTime.setDate(switchTime.getDate() + 1);
        }
        
        const timeUntilSwitch = switchTime.getTime() - now.getTime();
        
        setTimeout(() => {
            this.setTheme(theme);
            console.log(`Scheduled theme switch to ${theme} at ${hour}:00`);
        }, timeUntilSwitch);
    }

    enableAutoTheme() {
        // Schedule automatic theme switching
        this.scheduleThemeSwitch(18, 'dark');  // Dark at 6 PM
        this.scheduleThemeSwitch(6, 'light');  // Light at 6 AM
        console.log('Automatic theme switching enabled');
    }

    // Theme analytics
    getThemeUsageStats() {
        const stats = JSON.parse(localStorage.getItem('mcpvots-theme-stats') || '{}');
        return stats;
    }

    trackThemeUsage() {
        const stats = this.getThemeUsageStats();
        const today = new Date().toDateString();
        
        if (!stats[today]) {
            stats[today] = { light: 0, dark: 0 };
        }
        
        stats[today][this.currentTheme]++;
        localStorage.setItem('mcpvots-theme-stats', JSON.stringify(stats));
    }

    // High contrast mode support
    enableHighContrast() {
        document.documentElement.classList.add('high-contrast');
        localStorage.setItem('mcpvots-high-contrast', 'true');
        console.log('High contrast mode enabled');
    }

    disableHighContrast() {
        document.documentElement.classList.remove('high-contrast');
        localStorage.setItem('mcpvots-high-contrast', 'false');
        console.log('High contrast mode disabled');
    }

    toggleHighContrast() {
        const isEnabled = document.documentElement.classList.contains('high-contrast');
        if (isEnabled) {
            this.disableHighContrast();
        } else {
            this.enableHighContrast();
        }
    }

    // Initialize high contrast based on user preference or system setting
    initializeHighContrast() {
        const userPreference = localStorage.getItem('mcpvots-high-contrast');
        const systemPreference = window.matchMedia('(prefers-contrast: high)').matches;
        
        if (userPreference === 'true' || (userPreference === null && systemPreference)) {
            this.enableHighContrast();
        }
    }
}

// CSS custom properties for dynamic theming
class DynamicThemeProperties {
    constructor() {
        this.properties = {
            light: {
                '--primary-bg': '#ffffff',
                '--secondary-bg': '#f3f4f6',
                '--text-primary': '#1f2937',
                '--text-secondary': '#374151',
                '--border-color': '#d1d5db',
                '--accent-color': '#3b82f6'
            },
            dark: {
                '--primary-bg': '#0a0a0a',
                '--secondary-bg': '#1a1a1a',
                '--text-primary': '#ffffff',
                '--text-secondary': '#cccccc',
                '--border-color': '#333333',
                '--accent-color': '#3b82f6'
            }
        };
    }

    applyProperties(theme) {
        const root = document.documentElement;
        const properties = this.properties[theme];
        
        if (properties) {
            Object.entries(properties).forEach(([property, value]) => {
                root.style.setProperty(property, value);
            });
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
    window.dynamicThemeProperties = new DynamicThemeProperties();
    
    // Initialize high contrast support
    window.themeManager.initializeHighContrast();
    
    // Track theme usage
    setInterval(() => {
        window.themeManager.trackThemeUsage();
    }, 60000); // Track every minute
    
    // Listen for theme changes and apply dynamic properties
    window.addEventListener('themeChanged', (e) => {
        window.dynamicThemeProperties.applyProperties(e.detail.theme);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeManager, DynamicThemeProperties };
}
