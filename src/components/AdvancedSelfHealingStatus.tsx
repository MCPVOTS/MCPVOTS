/**
 * Advanced Self-Healing Status Component
 * Real-time display of intelligent auto-repair capabilities
 */

'use client'

import React, { useState, useEffect } from 'react'
import AdvancedSelfHealingService from '../services/AdvancedSelfHealingService'
import SelfHealingTestPanel from './SelfHealingTestPanel'

interface SystemHealth {
  overall: 'excellent' | 'good' | 'warning' | 'critical'
  components: Record<string, HealthStatus>
  issues: Issue[]
  autoFixes: AutoFix[]
  learningMetrics: LearningMetrics
}

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'failing' | 'offline'
  performance: number
  trend: 'improving' | 'stable' | 'degrading'
  metrics: Record<string, number>
}

interface Issue {
  id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  component: string
  description: string
  autoFixable: boolean
  autoFixApplied: boolean
}

interface AutoFix {
  id: string
  type: string
  description: string
  success: boolean
  confidence: number
  appliedAt: Date
}

interface LearningMetrics {
  totalFixes: number
  successRate: number
  patternRecognition: Record<string, number>
}

const AdvancedSelfHealingStatus: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [isActive, setIsActive] = useState(false)
  const [service] = useState(() => new AdvancedSelfHealingService())
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    const updateHealth = () => {
      setHealth(service.getSystemHealth())
      setIsActive(service.isMonitoringActive())
    }

    // Initial update
    updateHealth()

    // Update every 2 seconds for real-time display
    const interval = setInterval(updateHealth, 2000)

    return () => clearInterval(interval)
  }, [service])

  useEffect(() => {
    // Start service automatically
    service.startSelfHealing()

    return () => {
      service.stopSelfHealing()
    }
  }, [service])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-400'
      case 'healthy': return 'text-green-400'
      case 'good': return 'text-blue-400'
      case 'degraded': return 'text-yellow-400'
      case 'warning': return 'text-orange-400'
      case 'failing': return 'text-red-400'
      case 'critical': return 'text-red-500'
      case 'offline': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
      case 'healthy': return '✅'
      case 'good': return '🟢'
      case 'degraded': return '🟡'
      case 'warning': return '⚠️'
      case 'failing': return '🔴'
      case 'critical': return '🚨'
      case 'offline': return '💀'
      default: return '❓'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈'
      case 'stable': return '➡️'
      case 'degrading': return '📉'
      default: return '➡️'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-blue-400'
      case 'medium': return 'text-yellow-400'
      case 'high': return 'text-orange-400'
      case 'critical': return 'text-red-500'
      default: return 'text-gray-400'
    }
  }

  if (!health) {
    return (
      <div className="bg-black/80 border border-orange-500/30 rounded-lg p-4 text-orange-500">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500"></div>
          <span>Initializing Advanced Self-Healing System...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-black/90 border border-orange-500/50 rounded-lg p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500' : 'bg-red-500'} ${isActive ? 'animate-pulse' : ''}`}></div>
            {isActive && (
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"></div>
            )}
          </div>
          <span className="text-orange-500 font-bold">🧠 Advanced Self-Healing AGI</span>
          <span className={`text-sm font-medium ${getStatusColor(health.overall)}`}>
            {getStatusIcon(health.overall)} {health.overall.toUpperCase()}
          </span>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-orange-500 hover:text-orange-400 transition-colors text-sm"
        >
          {showDetails ? '▼ Hide Details' : '▶ Show Details'}
        </button>
      </div>

      {/* Learning Metrics Bar */}
      <div className="bg-gray-900/50 rounded p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-orange-400 text-sm font-medium">🎯 Learning Metrics</span>
          <span className="text-green-400 text-sm">
            Success Rate: {health.learningMetrics.successRate.toFixed(1)}%
          </span>
        </div>
        <div className="flex space-x-4 text-xs">
          <div className="text-blue-400">
            Total Fixes: {health.learningMetrics.totalFixes}
          </div>
          <div className="text-yellow-400">
            Patterns: {Object.keys(health.learningMetrics.patternRecognition).length}
          </div>
        </div>
      </div>

      {/* Component Health Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {Object.entries(health.components).map(([name, status]) => (
          <div key={name} className="bg-gray-900/50 rounded p-2 text-center">
            <div className="text-xs text-gray-400 mb-1">
              {name.replace('_', ' ').toUpperCase()}
            </div>
            <div className={`text-sm font-medium ${getStatusColor(status.status)}`}>
              {getStatusIcon(status.status)} {status.performance}%
            </div>
            <div className="text-xs text-gray-500">
              {getTrendIcon(status.trend)} {status.trend}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Auto-Fixes */}
      {health.autoFixes.length > 0 && (
        <div className="bg-gray-900/50 rounded p-3">
          <div className="text-orange-400 text-sm font-medium mb-2">
            🔧 Recent Auto-Fixes ({health.autoFixes.length})
          </div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {health.autoFixes.slice(-5).reverse().map((fix) => (
              <div
                key={fix.id}
                className={`text-xs p-2 rounded border-l-2 ${
                  fix.success 
                    ? 'border-green-500 bg-green-500/10 text-green-400' 
                    : 'border-red-500 bg-red-500/10 text-red-400'
                } ${fix.success ? 'animate-pulse' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <span>{fix.success ? '✅' : '❌'} {fix.description}</span>
                  <span className="text-gray-500">
                    {new Date(fix.appliedAt).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-gray-500 mt-1">
                  Confidence: {(fix.confidence * 100).toFixed(0)}% | Type: {fix.type}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Issues */}
      {health.issues.length > 0 && (
        <div className="bg-gray-900/50 rounded p-3">
          <div className="text-red-400 text-sm font-medium mb-2">
            🚨 Active Issues ({health.issues.length})
          </div>
          <div className="space-y-1 max-h-24 overflow-y-auto">
            {health.issues.map((issue) => (
              <div key={issue.id} className="text-xs p-2 rounded bg-red-500/10 border-l-2 border-red-500">
                <div className="flex items-center justify-between">
                  <span className={getSeverityColor(issue.severity)}>
                    {issue.severity.toUpperCase()}: {issue.description}
                  </span>
                  <span className="text-gray-500">
                    {issue.autoFixable ? '🔧 Auto-fixable' : '⚠️ Manual'}
                  </span>
                </div>
                <div className="text-gray-500 mt-1">
                  Component: {issue.component}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed View */}
      {showDetails && (
        <div className="border-t border-orange-500/30 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Performance History */}
            <div className="bg-gray-900/50 rounded p-3">
              <div className="text-orange-400 text-sm font-medium mb-2">
                📊 Performance Trends
              </div>
              {Object.entries(health.components).map(([name, status]) => (
                <div key={name} className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-400">{name}:</span>
                  <div className="flex items-center space-x-2">
                    <span className={getStatusColor(status.status)}>
                      {status.performance}%
                    </span>
                    <span className="text-gray-500">
                      {getTrendIcon(status.trend)}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* System Metrics */}
            <div className="bg-gray-900/50 rounded p-3">
              <div className="text-orange-400 text-sm font-medium mb-2">
                ⚡ System Metrics
              </div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Memory Usage:</span>
                  <span className="text-blue-400">
                    {health.components.memory_usage?.performance || 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Network Health:</span>
                  <span className="text-green-400">
                    {health.components.network?.performance || 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Dependencies:</span>
                  <span className="text-yellow-400">
                    {health.components.dependencies?.performance || 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">AI Models:</span>
                  <span className="text-purple-400">
                    {health.components.ai_models?.performance || 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="border-t border-orange-500/30 pt-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            🤖 Autonomous monitoring every 15s | Learning every 5min
          </span>
          <span className="text-orange-500">
            {isActive ? '🟢 ACTIVE' : '🔴 INACTIVE'}
          </span>
        </div>
      </div>

      {/* Test Panel */}
      <SelfHealingTestPanel />
    </div>
  )
}

export default AdvancedSelfHealingStatus
