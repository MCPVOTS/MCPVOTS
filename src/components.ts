/**
 * MCPVots Advanced Component System
 * Modern TypeScript component architecture for MCP integration
 */

export interface ComponentProps {
  className?: string;
  children?: any;
  [key: string]: any;
}

export interface MCPServer {
  name: string;
  url: string;
  status: 'online' | 'offline' | 'connecting' | 'error' | 'warning';
  enabled: boolean;
  capabilities: string[];
  lastPing: number | null;
  connections: number;
  messages: number;
  errors: number;
  uptime: number;
  startTime: number;
  reconnectInterval: number;
  description?: string;
}

export interface SystemStats {
  activeConnections: number;
  memoryUsage: number;
  uptime: number;
  messagesProcessed: number;
  errorCount: number;
  lastActivity: number;
}

export interface PerformanceMetrics {
  responseTime: number[];
  throughput: number;
  errorRate: number;
  latency: number;
  bandwidth: number;
}

export interface LogEntry {
  timestamp: number;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS' | 'DEBUG';
  message: string;
  source?: string;
  data?: any;
}

/**
 * Base Component Class
 */
export abstract class BaseComponent {
  protected element: HTMLElement;
  protected props: ComponentProps;
  protected eventListeners: Map<string, Function[]> = new Map();

  constructor(element: HTMLElement, props: ComponentProps = {}) {
    this.element = element;
    this.props = props;
    this.init();
  }

  protected abstract init(): void;
  protected abstract render(): void;

  protected on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  protected emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
    
    // Also emit as custom DOM event
    this.element.dispatchEvent(new CustomEvent(event, { detail: data }));
  }

  protected addClass(className: string): void {
    this.element.classList.add(className);
  }

  protected removeClass(className: string): void {
    this.element.classList.remove(className);
  }

  protected setHTML(html: string): void {
    this.element.innerHTML = html;
  }

  public destroy(): void {
    this.eventListeners.clear();
    this.element.remove();
  }
}

/**
 * Server Status Card Component
 */
export class ServerStatusCard extends BaseComponent {
  private server: MCPServer;
  private updateInterval: number | null = null;

  constructor(element: HTMLElement, server: MCPServer, props: ComponentProps = {}) {
    super(element, props);
    this.server = server;
  }

  protected init(): void {
    this.addClass('server-status-card');
    this.render();
    this.bindEvents();
    this.startUpdateLoop();
  }

  protected render(): void {
    const statusColor = this.getStatusColor(this.server.status);
    const statusIcon = this.getStatusIcon(this.server.status);
    const uptime = this.formatUptime(Date.now() - this.server.startTime);

    this.setHTML(`
      <div class="server-card bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4 transition-all duration-200 hover:scale-105 hover:shadow-lg">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-light-text dark:text-dark-text">${this.server.name}</h3>
          <div class="flex items-center space-x-2">
            <span class="status-indicator w-3 h-3 rounded-full ${statusColor}"></span>
            <span class="status-icon">${statusIcon}</span>
          </div>
        </div>
        
        <div class="server-details space-y-2 text-sm text-light-text-secondary dark:text-dark-text-secondary">
          <div class="flex justify-between">
            <span>Status:</span>
            <span class="capitalize font-medium ${this.getStatusTextColor(this.server.status)}">${this.server.status}</span>
          </div>
          <div class="flex justify-between">
            <span>Connections:</span>
            <span class="font-mono">${this.server.connections}</span>
          </div>
          <div class="flex justify-between">
            <span>Messages:</span>
            <span class="font-mono">${this.server.messages.toLocaleString()}</span>
          </div>
          <div class="flex justify-between">
            <span>Errors:</span>
            <span class="font-mono text-red-500">${this.server.errors}</span>
          </div>
          <div class="flex justify-between">
            <span>Uptime:</span>
            <span class="font-mono">${uptime}</span>
          </div>
        </div>

        <div class="capabilities mt-3">
          <div class="text-xs text-light-text-secondary dark:text-dark-text-secondary mb-1">Capabilities:</div>
          <div class="flex flex-wrap gap-1">
            ${this.server.capabilities.map(cap => 
              `<span class="capability-tag px-2 py-1 text-xs bg-accent-primary/10 text-accent-primary rounded">${cap}</span>`
            ).join('')}
          </div>
        </div>

        <div class="server-actions mt-4 flex space-x-2">
          <button class="btn-connect flex-1 px-3 py-2 text-xs bg-accent-primary text-white rounded hover:bg-accent-primary-dark transition-colors">
            ${this.server.status === 'online' ? 'Disconnect' : 'Connect'}
          </button>
          <button class="btn-details px-3 py-2 text-xs border border-light-border dark:border-dark-border rounded hover:bg-light-bg-secondary dark:hover:bg-dark-bg-secondary transition-colors">
            Details
          </button>
        </div>
      </div>
    `);
  }

  private bindEvents(): void {
    const connectBtn = this.element.querySelector('.btn-connect') as HTMLButtonElement;
    const detailsBtn = this.element.querySelector('.btn-details') as HTMLButtonElement;

    connectBtn?.addEventListener('click', () => {
      this.emit('toggle-connection', this.server);
    });

    detailsBtn?.addEventListener('click', () => {
      this.emit('show-details', this.server);
    });
  }

  private startUpdateLoop(): void {
    this.updateInterval = window.setInterval(() => {
      this.render();
    }, 5000);
  }

  private getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      online: 'bg-green-500',
      offline: 'bg-red-500',
      connecting: 'bg-yellow-500',
      warning: 'bg-orange-500',
      error: 'bg-red-600'
    };
    return colors[status] || 'bg-gray-500';
  }

  private getStatusIcon(status: string): string {
    const icons: Record<string, string> = {
      online: '🟢',
      offline: '🔴',
      connecting: '🟡',
      warning: '🟠',
      error: '❌'
    };
    return icons[status] || '⚪';
  }

  private getStatusTextColor(status: string): string {
    const colors: Record<string, string> = {
      online: 'text-green-500',
      offline: 'text-red-500',
      connecting: 'text-yellow-500',
      warning: 'text-orange-500',
      error: 'text-red-600'
    };
    return colors[status] || 'text-gray-500';
  }

  private formatUptime(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  public updateServer(server: MCPServer): void {
    this.server = server;
    this.render();
  }

  public destroy(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    super.destroy();
  }
}

/**
 * System Metrics Dashboard Component
 */
export class SystemMetricsDashboard extends BaseComponent {
  private stats: SystemStats;
  private metrics: PerformanceMetrics;
  private updateInterval: number | null = null;

  constructor(element: HTMLElement, stats: SystemStats, metrics: PerformanceMetrics, props: ComponentProps = {}) {
    super(element, props);
    this.stats = stats;
    this.metrics = metrics;
  }

  protected init(): void {
    this.addClass('system-metrics-dashboard');
    this.render();
    this.startUpdateLoop();
  }

  protected render(): void {
    const avgResponseTime = this.metrics.responseTime.length > 0 
      ? this.metrics.responseTime.reduce((a, b) => a + b, 0) / this.metrics.responseTime.length 
      : 0;

    this.setHTML(`
      <div class="metrics-grid grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="metric-card bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <div class="metric-icon text-2xl mb-2">📡</div>
          <div class="metric-value text-2xl font-bold text-light-text dark:text-dark-text">${this.stats.activeConnections}</div>
          <div class="metric-label text-sm text-light-text-secondary dark:text-dark-text-secondary">Active Connections</div>
        </div>

        <div class="metric-card bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <div class="metric-icon text-2xl mb-2">💬</div>
          <div class="metric-value text-2xl font-bold text-light-text dark:text-dark-text">${this.stats.messagesProcessed.toLocaleString()}</div>
          <div class="metric-label text-sm text-light-text-secondary dark:text-dark-text-secondary">Messages Processed</div>
        </div>

        <div class="metric-card bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <div class="metric-icon text-2xl mb-2">⚡</div>
          <div class="metric-value text-2xl font-bold text-light-text dark:text-dark-text">${avgResponseTime.toFixed(0)}ms</div>
          <div class="metric-label text-sm text-light-text-secondary dark:text-dark-text-secondary">Avg Response Time</div>
        </div>

        <div class="metric-card bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <div class="metric-icon text-2xl mb-2">🚨</div>
          <div class="metric-value text-2xl font-bold text-red-500">${this.stats.errorCount}</div>
          <div class="metric-label text-sm text-light-text-secondary dark:text-dark-text-secondary">Total Errors</div>
        </div>
      </div>

      <div class="performance-charts grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="chart-container bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <h3 class="text-lg font-semibold mb-3 text-light-text dark:text-dark-text">Response Time Trend</h3>
          <div class="chart-placeholder h-32 bg-light-bg-secondary dark:bg-dark-bg-secondary rounded flex items-center justify-center text-light-text-secondary dark:text-dark-text-secondary">
            Chart visualization would go here
          </div>
        </div>

        <div class="chart-container bg-light-bg dark:bg-dark-bg border border-light-border dark:border-dark-border rounded-lg p-4">
          <h3 class="text-lg font-semibold mb-3 text-light-text dark:text-dark-text">Throughput</h3>
          <div class="chart-placeholder h-32 bg-light-bg-secondary dark:bg-dark-bg-secondary rounded flex items-center justify-center text-light-text-secondary dark:text-dark-text-secondary">
            Chart visualization would go here
          </div>
        </div>
      </div>
    `);
  }

  private startUpdateLoop(): void {
    this.updateInterval = window.setInterval(() => {
      this.render();
    }, 2000);
  }

  public updateStats(stats: SystemStats, metrics: PerformanceMetrics): void {
    this.stats = stats;
    this.metrics = metrics;
  }

  public destroy(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    super.destroy();
  }
}

/**
 * Console Output Component
 */
export class ConsoleOutput extends BaseComponent {
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;
  private autoScroll: boolean = true;

  constructor(element: HTMLElement, props: ComponentProps = {}) {
    super(element, props);
    this.maxLogs = props.maxLogs || 1000;
  }

  protected init(): void {
    this.addClass('console-output');
    this.render();
    this.bindEvents();
  }

  protected render(): void {
    this.setHTML(`
      <div class="console-container bg-dark-bg border border-dark-border rounded-lg overflow-hidden">
        <div class="console-header bg-dark-bg-secondary p-3 border-b border-dark-border flex justify-between items-center">
          <h3 class="text-sm font-semibold text-dark-text">System Console</h3>
          <div class="console-controls flex space-x-2">
            <button class="btn-clear text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">Clear</button>
            <button class="btn-export text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">Export</button>
            <button class="btn-auto-scroll text-xs px-2 py-1 ${this.autoScroll ? 'bg-green-600' : 'bg-gray-600'} text-white rounded hover:opacity-80 transition-opacity">
              Auto-scroll
            </button>
          </div>
        </div>
        <div class="console-body h-64 overflow-y-auto p-3 font-mono text-sm">
          ${this.renderLogs()}
        </div>
      </div>
    `);

    if (this.autoScroll) {
      this.scrollToBottom();
    }
  }

  private renderLogs(): string {
    if (this.logs.length === 0) {
      return '<div class="text-dark-text-secondary">No logs yet...</div>';
    }

    return this.logs.map(log => {
      const timestamp = new Date(log.timestamp).toLocaleTimeString();
      const levelColor = this.getLevelColor(log.level);
      
      return `
        <div class="log-entry flex space-x-3 mb-1 hover:bg-dark-bg-secondary px-2 py-1 rounded">
          <span class="timestamp text-dark-text-secondary">${timestamp}</span>
          <span class="level ${levelColor} font-bold w-16">${log.level}</span>
          <span class="message text-dark-text flex-1">${this.escapeHtml(log.message)}</span>
          ${log.source ? `<span class="source text-dark-text-secondary text-xs">[${log.source}]</span>` : ''}
        </div>
      `;
    }).join('');
  }

  private bindEvents(): void {
    const clearBtn = this.element.querySelector('.btn-clear') as HTMLButtonElement;
    const exportBtn = this.element.querySelector('.btn-export') as HTMLButtonElement;
    const autoScrollBtn = this.element.querySelector('.btn-auto-scroll') as HTMLButtonElement;

    clearBtn?.addEventListener('click', () => {
      this.clearLogs();
    });

    exportBtn?.addEventListener('click', () => {
      this.exportLogs();
    });

    autoScrollBtn?.addEventListener('click', () => {
      this.toggleAutoScroll();
    });
  }

  private getLevelColor(level: string): string {
    const colors: Record<string, string> = {
      INFO: 'text-blue-400',
      WARNING: 'text-yellow-400',
      ERROR: 'text-red-400',
      SUCCESS: 'text-green-400',
      DEBUG: 'text-gray-400'
    };
    return colors[level] || 'text-white';
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private scrollToBottom(): void {
    const consoleBody = this.element.querySelector('.console-body');
    if (consoleBody) {
      consoleBody.scrollTop = consoleBody.scrollHeight;
    }
  }

  public addLog(log: LogEntry): void {
    this.logs.push(log);
    
    // Trim logs if over limit
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
    
    this.render();
    this.emit('log-added', log);
  }

  public clearLogs(): void {
    this.logs = [];
    this.render();
    this.emit('logs-cleared');
  }

  public exportLogs(): void {
    const logsData = JSON.stringify(this.logs, null, 2);
    const blob = new Blob([logsData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `mcpvots-logs-${new Date().toISOString().slice(0, 19)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    this.emit('logs-exported', this.logs.length);
  }

  public toggleAutoScroll(): void {
    this.autoScroll = !this.autoScroll;
    this.render();
  }
}

// Export all components
export const Components = {
  BaseComponent,
  ServerStatusCard,
  SystemMetricsDashboard,
  ConsoleOutput
};

export default Components;
