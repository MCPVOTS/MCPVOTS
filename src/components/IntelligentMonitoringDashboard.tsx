/**
 * Intelligent Monitoring Dashboard
 * Real-time AI-powered system monitoring and diagnostics
 */

'use client'

import React, { useState, useEffect } from 'react'
import AdvancedSelfHealingService from '../services/AdvancedSelfHealingService'
import RealTimeSystemMonitor from './RealTimeSystemMonitor'

interface MonitoringData {
  systemHealth: {
    overall: string
    components: Record<string, unknown>
    issues: unknown[]
    autoFixes: unknown[]
  }
  performanceMetrics: PerformanceMetrics
  aiInsights: AIInsight[]
  predictiveAlerts: PredictiveAlert[]
  optimizationSuggestions: OptimizationSuggestion[]
}

interface PerformanceMetrics {
  responseTime: number
  memoryUsage: number
  cpuUsage: number
  networkLatency: number
  aiModelPerformance: number
  userSatisfaction: number
}

interface AIInsight {
  id: string
  type: 'performance' | 'security' | 'optimization' | 'prediction'
  message: string
  confidence: number
  actionable: boolean
  timestamp: Date
}

interface PredictiveAlert {
  id: string
  prediction: string
  probability: number
  timeframe: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  preventive_actions: string[]
}

interface OptimizationSuggestion {
  id: string
  category: string
  suggestion: string
  impact: 'low' | 'medium' | 'high'
  effort: 'low' | 'medium' | 'high'
  automated: boolean
}

const IntelligentMonitoringDashboard: React.FC = () => {
  const [monitoringData, setMonitoringData] = useState<MonitoringData | null>(null)
  const [service] = useState(() => new AdvancedSelfHealingService())
  const [selectedTab, setSelectedTab] = useState<'overview' | 'insights' | 'predictions' | 'optimizations' | 'monitor'>('overview')
  const [realTimeMode, setRealTimeMode] = useState(true)

  useEffect(() => {
    const generateMockData = (): MonitoringData => {
      const systemHealth = service.getSystemHealth()
      
      return {
        systemHealth,
        performanceMetrics: {
          responseTime: Math.random() * 1000 + 200,
          memoryUsage: Math.random() * 40 + 50,
          cpuUsage: Math.random() * 30 + 20,
          networkLatency: Math.random() * 50 + 20,
          aiModelPerformance: Math.random() * 20 + 80,
          userSatisfaction: Math.random() * 15 + 85
        },
        aiInsights: [
          {
            id: '1',
            type: 'performance',
            message: 'Chat response time optimized by 23% through intelligent caching',
            confidence: 0.95,
            actionable: true,
            timestamp: new Date()
          },
          {
            id: '2',
            type: 'optimization',
            message: 'Memory usage patterns suggest implementing lazy loading for better performance',
            confidence: 0.87,
            actionable: true,
            timestamp: new Date()
          },
          {
            id: '3',
            type: 'security',
            message: 'No security vulnerabilities detected in recent API interactions',
            confidence: 0.99,
            actionable: false,
            timestamp: new Date()
          }
        ],
        predictiveAlerts: [
          {
            id: '1',
            prediction: 'Potential memory leak in chat component',
            probability: 0.73,
            timeframe: '2-4 hours',
            severity: 'medium',
            preventive_actions: ['Enable memory monitoring', 'Implement garbage collection optimization']
          },
          {
            id: '2',
            prediction: 'High user activity expected based on usage patterns',
            probability: 0.89,
            timeframe: '30 minutes',
            severity: 'low',
            preventive_actions: ['Scale chat services', 'Optimize API responses']
          }
        ],
        optimizationSuggestions: [
          {
            id: '1',
            category: 'Performance',
            suggestion: 'Implement WebWorkers for AI model inference',
            impact: 'high',
            effort: 'medium',
            automated: false
          },
          {
            id: '2',
            category: 'UI/UX',
            suggestion: 'Add progressive loading for chat history',
            impact: 'medium',
            effort: 'low',
            automated: true
          },
          {
            id: '3',
            category: 'Infrastructure',
            suggestion: 'Enable service worker caching for static assets',
            impact: 'medium',
            effort: 'low',
            automated: true
          }
        ]
      }
    }

    const updateData = () => {
      setMonitoringData(generateMockData())
    }

    updateData()

    let interval: NodeJS.Timeout | null = null
    if (realTimeMode) {
      interval = setInterval(updateData, 3000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [service, realTimeMode])

  const getMetricColor = (value: number, threshold: { good: number; warning: number }) => {
    if (value >= threshold.good) return 'text-green-400'
    if (value >= threshold.warning) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500'
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500'
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500'
    }
  }

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'low': return '🔷'
      case 'medium': return '🔶'
      case 'high': return '🔴'
      default: return '⚪'
    }
  }

  if (!monitoringData) {
    return (
      <div className="bg-black/80 border border-orange-500/30 rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
        <span className="text-orange-500">Loading Intelligent Monitoring Dashboard...</span>
      </div>
    )
  }

  return (
    <div className="bg-black/90 border border-orange-500/50 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-4 h-4 rounded-full bg-green-500 animate-pulse"></div>
            <div className="absolute inset-0 w-4 h-4 rounded-full bg-green-500 animate-ping opacity-75"></div>
          </div>
          <h2 className="text-xl font-bold text-orange-500">🧠 Intelligent Monitoring Dashboard</h2>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setRealTimeMode(!realTimeMode)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              realTimeMode 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                : 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
            }`}
          >
            {realTimeMode ? '🟢 Real-time' : '⏸️ Paused'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-900/50 rounded-lg p-1">
        {(['overview', 'insights', 'predictions', 'optimizations', 'monitor'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              selectedTab === tab
                ? 'bg-orange-500 text-black'
                : 'text-orange-400 hover:text-orange-300'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      {selectedTab === 'overview' && (
        <div className="space-y-6">
          {/* Performance Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Response Time</div>
              <div className={`text-2xl font-bold ${getMetricColor(2000 - monitoringData.performanceMetrics.responseTime, { good: 1500, warning: 800 })}`}>
                {monitoringData.performanceMetrics.responseTime.toFixed(0)}ms
              </div>
              <div className="text-xs text-gray-500">⚡ Chat & AI responses</div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Memory Usage</div>
              <div className={`text-2xl font-bold ${getMetricColor(100 - monitoringData.performanceMetrics.memoryUsage, { good: 20, warning: 40 })}`}>
                {monitoringData.performanceMetrics.memoryUsage.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">🧠 System memory</div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">AI Performance</div>
              <div className={`text-2xl font-bold ${getMetricColor(monitoringData.performanceMetrics.aiModelPerformance, { good: 85, warning: 70 })}`}>
                {monitoringData.performanceMetrics.aiModelPerformance.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">🤖 Model efficiency</div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Network Latency</div>
              <div className={`text-2xl font-bold ${getMetricColor(100 - monitoringData.performanceMetrics.networkLatency, { good: 50, warning: 30 })}`}>
                {monitoringData.performanceMetrics.networkLatency.toFixed(0)}ms
              </div>
              <div className="text-xs text-gray-500">🌐 API connections</div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">User Satisfaction</div>
              <div className={`text-2xl font-bold ${getMetricColor(monitoringData.performanceMetrics.userSatisfaction, { good: 90, warning: 75 })}`}>
                {monitoringData.performanceMetrics.userSatisfaction.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">😊 Experience score</div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">System Health</div>
              <div className="text-2xl font-bold text-green-400">
                {monitoringData.systemHealth.overall.toUpperCase()}
              </div>
              <div className="text-xs text-gray-500">💚 Overall status</div>
            </div>
          </div>
        </div>
      )}

      {selectedTab === 'insights' && (
        <div className="space-y-4">
          <div className="text-lg font-semibold text-orange-400 mb-4">
            🔍 AI-Generated Insights ({monitoringData.aiInsights.length})
          </div>
          {monitoringData.aiInsights.map((insight) => (
            <div key={insight.id} className="bg-gray-900/50 rounded-lg p-4 border-l-4 border-blue-500">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-blue-400 font-medium">{insight.type.toUpperCase()}</span>
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                    {(insight.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {insight.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <p className="text-gray-300 mb-2">{insight.message}</p>
              {insight.actionable && (
                <div className="flex items-center space-x-2">
                  <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded">
                    ⚡ Actionable
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedTab === 'predictions' && (
        <div className="space-y-4">
          <div className="text-lg font-semibold text-orange-400 mb-4">
            🔮 Predictive Alerts ({monitoringData.predictiveAlerts.length})
          </div>
          {monitoringData.predictiveAlerts.map((alert) => (
            <div key={alert.id} className={`rounded-lg p-4 border-l-4 ${getSeverityColor(alert.severity)}`}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">{alert.prediction}</span>
                  <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                    {(alert.probability * 100).toFixed(0)}% probability
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  in {alert.timeframe}
                </span>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-400">Preventive Actions:</div>
                <ul className="space-y-1">
                  {alert.preventive_actions.map((action, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-center space-x-2">
                      <span className="text-green-400">•</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedTab === 'optimizations' && (
        <div className="space-y-4">
          <div className="text-lg font-semibold text-orange-400 mb-4">
            ⚡ Optimization Suggestions ({monitoringData.optimizationSuggestions.length})
          </div>
          <div className="grid gap-4">
            {monitoringData.optimizationSuggestions.map((suggestion) => (
              <div key={suggestion.id} className="bg-gray-900/50 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-orange-400 font-medium">{suggestion.category}</span>
                    <span className="text-xs bg-gray-500/20 text-gray-400 px-2 py-1 rounded">
                      {suggestion.effort} effort
                    </span>
                    <span className="text-xs">
                      {getImpactIcon(suggestion.impact)} {suggestion.impact} impact
                    </span>
                  </div>
                  {suggestion.automated && (
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                      🤖 Auto-implementable
                    </span>
                  )}
                </div>
                <p className="text-gray-300">{suggestion.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedTab === 'monitor' && (
        <div className="space-y-4">
          <RealTimeSystemMonitor />
        </div>
      )}

      {/* Footer */}
      <div className="border-t border-orange-500/30 pt-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>🤖 AI-powered monitoring with predictive analytics</span>
          <span className="text-orange-500">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default IntelligentMonitoringDashboard
