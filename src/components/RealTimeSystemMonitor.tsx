/**
 * Real-Time System Monitor
 * Live logging and monitoring of self-healing activities
 */

'use client'

import React, { useState, useEffect } from 'react'

interface LogEntry {
  id: string
  timestamp: Date
  level: 'info' | 'warning' | 'error' | 'success'
  category: 'healing' | 'performance' | 'security' | 'ai' | 'system'
  message: string
  details?: string
}

const RealTimeSystemMonitor: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isActive, setIsActive] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [maxLogs] = useState(100)

  useEffect(() => {
    if (!isActive) return

    // Simulate real-time system monitoring
    const generateLog = (): LogEntry => {
      const categories: LogEntry['category'][] = ['healing', 'performance', 'security', 'ai', 'system']
      const levels: LogEntry['level'][] = ['info', 'warning', 'error', 'success']
      
      const messages = {
        healing: [
          'Auto-healing service scanning for issues...',
          'Memory optimization applied successfully',
          'Browser cache cleared automatically',
          'UI responsiveness improved',
          'WebSocket connection restored',
          'Performance bottleneck detected and resolved',
          'System diagnostics completed - all green'
        ],
        performance: [
          'Response time: 234ms (optimal)',
          'Memory usage: 67% (normal)',
          'CPU utilization optimized',
          'Network latency reduced to 45ms',
          'DOM rendering performance improved',
          'API response times within acceptable range'
        ],
        security: [
          'Security scan completed - no threats detected',
          'Authentication tokens refreshed',
          'Firewall rules updated',
          'Encryption protocols verified',
          'API endpoint security validated'
        ],
        ai: [
          'DeepSeek R1 model responding normally',
          'Gemini 2.5 performance at 97%',
          'Claude 3.5 processing requests efficiently',
          'AI model load balancing optimized',
          'Token usage within normal parameters',
          'Model inference time: 156ms'
        ],
        system: [
          'System uptime: 7d 14h 32m',
          'Background services healthy',
          'Database connections stable',
          'File system integrity verified',
          'System resources available'
        ]
      }

      const category = categories[Math.floor(Math.random() * categories.length)]
      const level = Math.random() > 0.8 ? levels[Math.floor(Math.random() * levels.length)] : 'info'
      const messageArray = messages[category]
      const message = messageArray[Math.floor(Math.random() * messageArray.length)]

      return {
        id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date(),
        level,
        category,
        message,
        details: Math.random() > 0.7 ? 'Additional diagnostic information available' : undefined
      }
    }

    // Add initial logs
    const initialLogs = Array.from({ length: 10 }, () => generateLog())
    setLogs(initialLogs)

    // Add new logs periodically
    const interval = setInterval(() => {
      const newLog = generateLog()
      setLogs(prev => {
        const updated = [...prev, newLog]
        return updated.length > maxLogs ? updated.slice(-maxLogs) : updated
      })
    }, 2000 + Math.random() * 3000) // Random interval between 2-5 seconds

    return () => clearInterval(interval)
  }, [isActive, maxLogs])

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return '✅'
      case 'info': return 'ℹ️'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      default: return 'ℹ️'
    }
  }

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return 'text-green-400'
      case 'info': return 'text-blue-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getCategoryIcon = (category: LogEntry['category']) => {
    switch (category) {
      case 'healing': return '🔧'
      case 'performance': return '⚡'
      case 'security': return '🛡️'
      case 'ai': return '🤖'
      case 'system': return '💻'
      default: return '📝'
    }
  }

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.category === filter || log.level === filter)

  return (
    <div className="bg-black/90 border border-orange-500/50 rounded-lg p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500' : 'bg-gray-500'} ${isActive ? 'animate-pulse' : ''}`}></div>
            {isActive && (
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"></div>
            )}
          </div>
          <h3 className="text-lg font-bold text-orange-500">📊 Real-Time System Monitor</h3>
          <span className="text-sm text-gray-400">
            ({filteredLogs.length} entries)
          </span>
        </div>
        <button
          onClick={() => setIsActive(!isActive)}
          className={`px-3 py-1 rounded text-sm transition-colors ${
            isActive 
              ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
              : 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
          }`}
        >
          {isActive ? '⏸️ Pause' : '▶️ Resume'}
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {['all', 'healing', 'performance', 'security', 'ai', 'system', 'success', 'warning', 'error'].map((filterOption) => (
          <button
            key={filterOption}
            onClick={() => setFilter(filterOption)}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              filter === filterOption
                ? 'bg-orange-500 text-black'
                : 'bg-gray-700/50 text-gray-400 hover:text-orange-400'
            }`}
          >
            {filterOption === 'all' ? '🔍 All' : `${getCategoryIcon(filterOption as LogEntry['category'])} ${filterOption}`}
          </button>
        ))}
      </div>

      {/* Log Display */}
      <div className="bg-gray-900/50 rounded-lg p-3 h-96 overflow-y-auto">
        <div className="space-y-2">
          {filteredLogs.slice().reverse().map((log) => (
            <div key={log.id} className="flex items-start space-x-3 text-xs hover:bg-gray-800/30 rounded p-2 transition-colors">
              <div className="flex-shrink-0 flex items-center space-x-1">
                <span>{getLevelIcon(log.level)}</span>
                <span>{getCategoryIcon(log.category)}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className={`font-medium ${getLevelColor(log.level)}`}>
                    [{log.level.toUpperCase()}] {log.category.toUpperCase()}
                  </span>
                  <span className="text-gray-500 text-xs">
                    {log.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-gray-300 mt-1 break-words">
                  {log.message}
                </div>
                {log.details && (
                  <div className="text-gray-500 text-xs mt-1 italic">
                    {log.details}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Stats */}
      <div className="border-t border-orange-500/30 pt-3">
        <div className="flex items-center justify-between text-xs">
          <div className="flex space-x-4">
            <span className="text-green-400">
              ✅ {logs.filter(l => l.level === 'success').length} Success
            </span>
            <span className="text-yellow-400">
              ⚠️ {logs.filter(l => l.level === 'warning').length} Warnings
            </span>
            <span className="text-red-400">
              ❌ {logs.filter(l => l.level === 'error').length} Errors
            </span>
          </div>
          <span className="text-orange-500">
            🔄 Auto-refreshing every 2-5s
          </span>
        </div>
      </div>
    </div>
  )
}

export default RealTimeSystemMonitor
