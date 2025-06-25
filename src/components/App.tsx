/**
 * MCPVots Main React Application Component
 * Modern React application with advanced theming and MCP integration
 */

import React, { useEffect, useState } from 'react';
import { useMCP } from '../contexts/MCPContext';
import { useTheme } from '../contexts/ThemeContext';
import { Header } from './Header';
import { Dashboard } from './Dashboard';
import { ServerPanel } from './ServerPanel';
import { SystemMetrics } from './SystemMetrics';
import { ConsoleLog } from './ConsoleLog';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorBoundary } from './ErrorBoundary';

export function App() {
  const { state: mcpState, mcpService } = useMCP();
  const { effectiveTheme } = useTheme();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize the application
    const init = async () => {
      try {
        // Wait for MCP service to be ready
        if (mcpService) {
          setIsInitialized(true);
        }
      } catch (error) {
        console.error('Failed to initialize app:', error);
      }
    };

    init();
  }, [mcpService]);

  // Show loading state while initializing
  if (!isInitialized || mcpState.isLoading) {
    return (
      <div className="min-h-screen bg-light-bg dark:bg-dark-bg flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className={`min-h-screen bg-light-bg dark:bg-dark-bg text-light-text dark:text-dark-text transition-colors duration-300 ${effectiveTheme}`}>
        <Header />
        
        <main className="container mx-auto px-6 py-8">
          {/* Error Display */}
          {mcpState.error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-700 dark:text-red-300 font-medium">
                  {mcpState.error}
                </span>
              </div>
            </div>
          )}

          {/* Main Dashboard Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 mb-8">
            {/* Primary Dashboard */}
            <div className="xl:col-span-2">
              <Dashboard />
            </div>
            
            {/* System Metrics */}
            <div className="xl:col-span-1">
              <SystemMetrics />
            </div>
            
            {/* Server Panel */}
            <div className="xl:col-span-1">
              <ServerPanel />
            </div>
          </div>

          {/* Secondary Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Console Log */}
            <div className="lg:col-span-1">
              <ConsoleLog />
            </div>
            
            {/* Additional Information Panel */}
            <div className="lg:col-span-1">
              <div className="bg-light-secondary-bg dark:bg-dark-secondary-bg rounded-xl border border-light-border dark:border-dark-border p-6">
                <h3 className="text-lg font-semibold mb-4 text-light-text dark:text-dark-text">
                  System Information
                </h3>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-light-border dark:border-dark-border">
                    <span className="text-light-secondary-text dark:text-dark-secondary-text">
                      Connected Servers
                    </span>
                    <span className="font-mono text-accent-primary">
                      {mcpState.servers.filter(s => s.status === 'online').length}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center py-2 border-b border-light-border dark:border-dark-border">
                    <span className="text-light-secondary-text dark:text-dark-secondary-text">
                      Messages Processed
                    </span>
                    <span className="font-mono text-accent-secondary">
                      {mcpState.systemStats.messagesProcessed.toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center py-2 border-b border-light-border dark:border-dark-border">
                    <span className="text-light-secondary-text dark:text-dark-secondary-text">
                      Uptime
                    </span>
                    <span className="font-mono text-accent-cyan">
                      {formatUptime(mcpState.systemStats.uptime)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center py-2">
                    <span className="text-light-secondary-text dark:text-dark-secondary-text">
                      Error Rate
                    </span>
                    <span className="font-mono text-accent-warning">
                      {mcpState.performanceMetrics.errorRate.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-light-border dark:border-dark-border bg-light-secondary-bg dark:bg-dark-secondary-bg">
          <div className="container mx-auto px-6 py-4">
            <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-light-secondary-text dark:text-dark-secondary-text">
              <div className="mb-2 sm:mb-0">
                MCPVots v1.0.0 - Advanced MCP Integration Platform
              </div>
              <div className="flex items-center space-x-4">
                <span>Theme: {effectiveTheme}</span>
                <span>•</span>
                <span>Active Connections: {mcpState.activeConnections}</span>
                <span>•</span>
                <span>Last Update: {new Date(mcpState.systemStats.lastActivity).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

// Utility function to format uptime
function formatUptime(uptime: number): string {
  const seconds = Math.floor(uptime / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days}d ${hours % 24}h ${minutes % 60}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}
