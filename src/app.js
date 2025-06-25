
// MCPVots - Advanced MCP Integration Application
class MCPVotsApp {
    constructor() {
        this.mcpServers = [];
        this.systemStats = {
            activeConnections: 0,
            memoryUsage: 0,
            uptime: 0
        };
        this.startTime = Date.now();
        this.consoleOutput = [];
        
        this.init();
    }

    init() {
        console.log("MCPVots application initializing...");
        this.log("INFO", "MCPVots system starting up...");
        
        // Initialize components
        this.initializeTheme();
        this.initializeMCPServers();
        this.initializeSystemMonitoring();
        this.bindEventListeners();
        this.startUpdateLoop();
        
        this.log("SUCCESS", "MCPVots system initialized successfully");
    }

    initializeTheme() {
        // Theme is handled by theme-manager.js
        this.log("INFO", "Theme system loaded");
    }

    initializeMCPServers() {
        // Simulate MCP server discovery
        const mockServers = [
            {
                name: "GitHub MCP",
                status: "online",
                url: "github.com/modelcontextprotocol/servers/tree/main/src/github",
                lastPing: Date.now(),
                connections: 3
            },
            {
                name: "Memory MCP",
                status: "online",
                url: "github.com/modelcontextprotocol/servers/tree/main/src/memory",
                lastPing: Date.now(),
                connections: 1
            },
            {
                name: "HuggingFace MCP",
                status: "warning",
                url: "huggingface-trilogy-mcp",
                lastPing: Date.now() - 30000,
                connections: 0
            },
            {
                name: "SuperMemory MCP",
                status: "offline",
                url: "supermemory-mcp",
                lastPing: Date.now() - 120000,
                connections: 0
            },
            {
                name: "Solana MCP",
                status: "online",
                url: "solanaMcp",
                lastPing: Date.now(),
                connections: 2
            },
            {
                name: "Browser Tools MCP",
                status: "online",
                url: "github.com/AgentDeskAI/browser-tools-mcp",
                lastPing: Date.now(),
                connections: 1
            }
        ];

        this.mcpServers = mockServers;
        this.updateMCPServerDisplay();
        this.log("INFO", `Discovered ${mockServers.length} MCP servers`);
    }

    updateMCPServerDisplay() {
        const container = document.getElementById('mcp-servers-list');
        if (!container) return;

        container.innerHTML = '';
        
        this.mcpServers.forEach(server => {
            const serverCard = document.createElement('div');
            serverCard.className = 'bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4 transition-all duration-200 hover:scale-105 hover:shadow-lg';
            
            const statusColor = this.getStatusColor(server.status);
            const statusIcon = this.getStatusIcon(server.status);
            
            serverCard.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-3 h-3 rounded-full ${statusColor} animate-pulse-glow"></div>
                        <div>
                            <h3 class="font-semibold text-light-text dark:text-dark-text">${server.name}</h3>
                            <p class="text-sm text-light-secondary-text dark:text-dark-secondary-text">${server.url}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-semibold ${this.getStatusTextColor(server.status)}">${statusIcon} ${server.status.toUpperCase()}</div>
                        <div class="text-xs text-light-secondary-text dark:text-dark-secondary-text">${server.connections} connections</div>
                    </div>
                </div>
            `;
            
            container.appendChild(serverCard);
        });

        // Update overall MCP status
        this.updateMCPStatus();
    }

    getStatusColor(status) {
        switch(status) {
            case 'online': return 'bg-accent-secondary';
            case 'warning': return 'bg-accent-warning';
            case 'offline': return 'bg-accent-danger';
            default: return 'bg-gray-400';
        }
    }

    getStatusIcon(status) {
        switch(status) {
            case 'online': return '🟢';
            case 'warning': return '🟡';
            case 'offline': return '🔴';
            default: return '⚪';
        }
    }

    getStatusTextColor(status) {
        switch(status) {
            case 'online': return 'text-accent-secondary';
            case 'warning': return 'text-accent-warning';
            case 'offline': return 'text-accent-danger';
            default: return 'text-gray-400';
        }
    }

    updateMCPStatus() {
        const statusIndicator = document.getElementById('mcp-status');
        if (!statusIndicator) return;

        const onlineServers = this.mcpServers.filter(s => s.status === 'online').length;
        const totalServers = this.mcpServers.length;
        
        if (onlineServers === totalServers) {
            statusIndicator.className = 'w-3 h-3 bg-accent-secondary rounded-full animate-pulse-glow';
        } else if (onlineServers > 0) {
            statusIndicator.className = 'w-3 h-3 bg-accent-warning rounded-full animate-pulse-glow';
        } else {
            statusIndicator.className = 'w-3 h-3 bg-accent-danger rounded-full animate-pulse-glow';
        }
    }

    initializeSystemMonitoring() {
        // Simulate system stats
        this.updateSystemStats();
    }

    updateSystemStats() {
        // Calculate uptime
        const uptime = Date.now() - this.startTime;
        const hours = Math.floor(uptime / (1000 * 60 * 60));
        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((uptime % (1000 * 60)) / 1000);
        
        this.systemStats.uptime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Simulate other stats
        this.systemStats.activeConnections = this.mcpServers.reduce((sum, server) => sum + server.connections, 0);
        this.systemStats.memoryUsage = Math.floor(Math.random() * 30) + 45; // 45-75%
        
        // Update UI
        this.updateSystemStatsDisplay();
    }

    updateSystemStatsDisplay() {
        const elements = {
            'active-connections': this.systemStats.activeConnections,
            'memory-usage': `${this.systemStats.memoryUsage}%`,
            'uptime': this.systemStats.uptime
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
    }

    bindEventListeners() {
        // Quick action buttons
        const buttons = document.querySelectorAll('[class*="bg-accent"]');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const buttonText = e.target.textContent.trim();
                this.handleQuickAction(buttonText);
            });
        });

        // Add some interactivity
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshSystem();
            }
        });
    }

    handleQuickAction(action) {
        switch(action) {
            case 'Monitor':
                this.log("INFO", "Opening monitoring dashboard...");
                break;
            case 'Refresh':
                this.refreshSystem();
                break;
            case 'Settings':
                this.log("INFO", "Opening settings panel...");
                break;
            case 'Logs':
                this.log("INFO", "Displaying system logs...");
                this.showDetailedLogs();
                break;
            default:
                this.log("INFO", `Executing action: ${action}`);
        }
    }

    refreshSystem() {
        this.log("INFO", "Refreshing system status...");
        
        // Simulate server status changes
        this.mcpServers.forEach(server => {
            if (Math.random() < 0.1) { // 10% chance of status change
                const statuses = ['online', 'warning', 'offline'];
                server.status = statuses[Math.floor(Math.random() * statuses.length)];
                server.lastPing = Date.now();
            }
        });
        
        this.updateMCPServerDisplay();
        this.log("SUCCESS", "System status refreshed");
    }

    showDetailedLogs() {
        const recentLogs = this.consoleOutput.slice(-10);
        recentLogs.forEach(log => {
            console.log(`[${log.timestamp}] ${log.level}: ${log.message}`);
        });
    }

    startUpdateLoop() {
        setInterval(() => {
            this.updateSystemStats();
            
            // Occasionally add random log entries
            if (Math.random() < 0.1) {
                const messages = [
                    "MCP heartbeat received",
                    "Connection pool optimized",
                    "Memory cleanup completed",
                    "Authentication token refreshed",
                    "Cache invalidated and rebuilt"
                ];
                const levels = ["INFO", "DEBUG", "SUCCESS"];
                const randomMessage = messages[Math.floor(Math.random() * messages.length)];
                const randomLevel = levels[Math.floor(Math.random() * levels.length)];
                this.log(randomLevel, randomMessage);
            }
        }, 1000);
    }

    log(level, message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = { timestamp, level, message };
        
        this.consoleOutput.push(logEntry);
        
        // Keep only last 100 log entries
        if (this.consoleOutput.length > 100) {
            this.consoleOutput.shift();
        }
        
        // Update console display
        this.updateConsoleDisplay(logEntry);
        
        // Also log to browser console
        console.log(`[${timestamp}] ${level}: ${message}`);
    }

    updateConsoleDisplay(logEntry) {
        const consoleElement = document.getElementById('console-output');
        if (!consoleElement) return;

        const logLine = document.createElement('div');
        const levelClass = this.getLogLevelClass(logEntry.level);
        logLine.className = levelClass;
        logLine.textContent = `[${logEntry.timestamp}] [${logEntry.level}] ${logEntry.message}`;
        
        consoleElement.appendChild(logLine);
        
        // Auto-scroll to bottom
        consoleElement.scrollTop = consoleElement.scrollHeight;
        
        // Remove old entries if too many
        while (consoleElement.children.length > 50) {
            consoleElement.removeChild(consoleElement.firstChild);
        }
    }

    getLogLevelClass(level) {
        switch(level) {
            case 'ERROR': return 'text-accent-danger';
            case 'WARN': case 'WARNING': return 'text-accent-warning';
            case 'INFO': return 'text-accent-primary';
            case 'SUCCESS': return 'text-accent-secondary';
            case 'DEBUG': return 'text-accent-cyan';
            default: return 'text-green-400';
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mcpVotsApp = new MCPVotsApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MCPVotsApp;
}
