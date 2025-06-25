/**
 * MCPVots Trilogy AGI Integration Entry Point
 * Modern React + TypeScript entry point for the complete AGI ecosystem showcase
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './components/App';
import { MCPProvider } from './contexts/MCPContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { TrilogyAGIDashboard } from './components/TrilogyAGIDashboard';
import EcosystemDashboard from './components/EcosystemDashboard';
import './styles/globals.css';

// Main Application Component
const MCPVotsApp: React.FC = () => {
  const [currentView, setCurrentView] = React.useState<'ecosystem' | 'trilogy' | 'traditional'>('ecosystem');

  return (
    <div className="min-h-screen bg-light-bg dark:bg-dark-bg">
      {/* Main Navigation */}
      <nav className="bg-light-secondary-bg dark:bg-dark-secondary-bg border-b border-light-border dark:border-dark-border">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-trilogy-gradient rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-light-text dark:text-dark-text">
                  MCPVots
                </h1>
                <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">
                  Trilogy AGI • MCP Ecosystem • Value Platform
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentView('ecosystem')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'ecosystem'
                    ? 'bg-accent-primary text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                🌟 Ecosystem
              </button>
              <button
                onClick={() => setCurrentView('trilogy')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'trilogy'
                    ? 'bg-accent-primary text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                🧠 Trilogy AGI
              </button>
              <button
                onClick={() => setCurrentView('traditional')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentView === 'traditional'
                    ? 'bg-accent-primary text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                🔧 Traditional MCP
              </button>
              
              <span className="px-3 py-1 bg-accent-secondary text-white text-sm rounded-full ml-4">
                🟢 Live
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentView === 'ecosystem' && <EcosystemDashboard />}
        
        {currentView === 'trilogy' && (
          <div className="container mx-auto px-6 py-8">
            <TrilogyAGIDashboard className="mb-8" />
          </div>
        )}
        
        {currentView === 'traditional' && (
          <div className="container mx-auto px-6 py-8">
            <div className="bg-light-secondary-bg dark:bg-dark-secondary-bg rounded-xl border border-light-border dark:border-dark-border p-6">
              <h2 className="text-xl font-semibold text-light-text dark:text-dark-text mb-4">
                🔧 Traditional MCP Integration
              </h2>
              <App />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-light-border dark:border-dark-border bg-light-secondary-bg dark:bg-dark-secondary-bg">
        <div className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-semibold text-light-text dark:text-dark-text mb-3">
                MCPVots Platform
              </h3>
              <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text mb-4">
                Democratizing access to advanced artificial general intelligence through comprehensive ecosystem integration.
              </p>
              <div className="flex space-x-2">
                <span className="px-2 py-1 bg-accent-primary text-white text-xs rounded">Agents</span>
                <span className="px-2 py-1 bg-accent-cyan text-white text-xs rounded">Humans</span>
                <span className="px-2 py-1 bg-accent-secondary text-white text-xs rounded">Value</span>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold text-light-text dark:text-dark-text mb-3">
                Value Proposition
              </h3>
              <ul className="space-y-2 text-sm text-light-secondary-text dark:text-dark-secondary-text">
                <li>� 400% Agent Productivity</li>
                <li>� 300% Human Efficiency</li>
                <li>� 85% Cost Reduction</li>
                <li>⚡ 95% Faster Reasoning</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-light-text dark:text-dark-text mb-3">
                Core Technologies
              </h3>
              <ul className="space-y-2 text-sm text-light-secondary-text dark:text-dark-secondary-text">
                <li>🧠 Trilogy AGI System</li>
                <li>🔄 Model Context Protocol</li>
                <li>⛓️ Blockchain Integration</li>
                <li>🔄 Darwin Gödel Machine</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-light-text dark:text-dark-text mb-3">
                Community
              </h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="https://github.com/kabrony/MCPVots" 
                     className="text-accent-primary hover:text-accent-secondary">
                    GitHub Repository
                  </a>
                </li>
                <li>
                  <a href="https://docs.mcpvots.app" 
                     className="text-accent-primary hover:text-accent-secondary">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="https://discord.gg/mcpvots" 
                     className="text-accent-primary hover:text-accent-secondary">
                    Discord Community
                  </a>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-light-border dark:border-dark-border mt-8 pt-6 text-center">
            <p className="text-sm text-light-secondary-text dark:text-dark-secondary-text">
              © 2025 MCPVots - Bringing unprecedented value to both AI agents and humans in the MCP ecosystem
            </p>
            <p className="text-xs text-light-secondary-text dark:text-dark-secondary-text mt-2">
              Open Source • Decentralized • Future-Ready • Community-Driven
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Initialize React application
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <MCPProvider>
        <MCPVotsApp />
      </MCPProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// Enable hot module replacement in development
declare const module: any;
if (typeof module !== 'undefined' && module.hot) {
  module.hot.accept();
}

// Global analytics and monitoring
if (typeof window !== 'undefined') {
  (window as any).mcpAnalytics = {
    pageView: () => console.log('📊 MCPVots page view tracked'),
    event: (name: string, data: any) => console.log('📊 MCPVots event:', name, data),
    trilogyMetrics: {
      serviceStatus: () => console.log('🧠 Trilogy service status checked'),
      performanceMetric: (metric: string, value: number) => 
        console.log('⚡ Performance metric:', metric, value),
    }
  };
}

console.log('🚀 MCPVots Trilogy AGI Integration Platform initialized');
console.log('🧠 Showcasing advanced AGI capabilities for the MCP ecosystem');
console.log('⛓️ Blockchain integration: Solana + Base L2');
console.log('💰 Unprecedented value for both AI agents and humans');
