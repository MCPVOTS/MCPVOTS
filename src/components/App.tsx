/**
 * MCPVots Main React Application Component
 * Modern React application with advanced theming and MCP integration
 */

"use client";

import React, { useEffect, useState } from 'react';
import { EcosystemDashboard } from './EcosystemDashboard';
import { TrilogyAGIDashboard } from './TrilogyAGIDashboard';
import { GeminiCLIDashboard } from './GeminiCLIDashboard';

export function App() {
  const [currentView, setCurrentView] = useState<'ecosystem' | 'trilogy' | 'gemini'>('ecosystem');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize the application
    const init = async () => {
      try {
        // Add any initialization logic here
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setIsLoading(false);
      }
    };

    init();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-700">Loading MCPVots...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">MCPVots</h1>
              </div>
              <div className="ml-10 flex items-baseline space-x-4">
                <button
                  onClick={() => setCurrentView('ecosystem')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'ecosystem'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Ecosystem
                </button>
                <button
                  onClick={() => setCurrentView('trilogy')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'trilogy'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Trilogy AGI
                </button>
                <button
                  onClick={() => setCurrentView('gemini')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'gemini'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Gemini CLI
                </button>
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">System Online</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {currentView === 'ecosystem' && <EcosystemDashboard />}
          {currentView === 'trilogy' && <TrilogyAGIDashboard />}
          {currentView === 'gemini' && <GeminiCLIDashboard />}
        </div>
      </main>
    </div>
  );
}
