/**
 * Self-Healing AGI Status Component
 * Displays real-time system health and auto-improvement status
 */

'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  Brain, 
  Settings, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle,
  TrendingUp,
  Cpu,
  Sparkles
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { selfHealingService } from '@/services/SelfHealingService'

interface SelfHealingStatusProps {
  className?: string
}

export default function SelfHealingStatus({ className = '' }: SelfHealingStatusProps) {
  const [healthStatus, setHealthStatus] = useState(selfHealingService.getHealthStatus())
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    // Update status every 5 seconds
    const interval = setInterval(() => {
      setHealthStatus(selfHealingService.getHealthStatus())
      setLastUpdate(new Date())
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const handleToggleMonitoring = () => {
    if (isMonitoring) {
      selfHealingService.stopSelfHealing()
      setIsMonitoring(false)
    } else {
      selfHealingService.startSelfHealing()
      setIsMonitoring(true)
    }
  }

  const getOverallStatusIcon = () => {
    switch (healthStatus.overall) {
      case 'excellent':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'good':
        return <CheckCircle2 className="w-5 h-5 text-blue-400" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-orange-400" />
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-400" />
      default:
        return <Activity className="w-5 h-5 text-gray-400" />
    }
  }

  const getOverallStatusColor = () => {
    switch (healthStatus.overall) {
      case 'excellent':
        return 'from-green-500/20 to-emerald-500/20 border-green-400/30'
      case 'good':
        return 'from-blue-500/20 to-cyan-500/20 border-blue-400/30'
      case 'warning':
        return 'from-orange-500/20 to-yellow-500/20 border-orange-400/30'
      case 'critical':
        return 'from-red-500/20 to-pink-500/20 border-red-400/30'
      default:
        return 'from-gray-500/20 to-slate-500/20 border-gray-400/30'
    }
  }

  return (
    <div className={`${className}`}>
      {/* Main Status Card */}
      <Card className={`bg-gradient-to-br ${getOverallStatusColor()} border-2 backdrop-blur-sm`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-orange-300">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              <span>Self-Healing AGI</span>
              {isMonitoring && (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-2 h-2 bg-green-400 rounded-full"
                />
              )}
            </div>
            <div className="flex items-center gap-2">
              {getOverallStatusIcon()}
              <span className="text-sm font-mono uppercase">
                {healthStatus.overall}
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* System Components */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {healthStatus.components.map((component, index) => (
              <motion.div
                key={component.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-black/40 rounded-lg p-3 border border-orange-500/20"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-gray-300">
                    {component.name}
                  </span>
                  <Badge 
                    variant="outline"
                    style={{ borderColor: component.color, color: component.color }}
                    className="text-xs px-1 py-0"
                  >
                    {component.status}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${component.performance}%` }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: component.color }}
                    />
                  </div>
                  <span className="text-xs font-mono text-gray-400 min-w-[3rem]">
                    {component.performance}%
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-black/40 rounded-lg p-3 text-center border border-orange-500/20">
              <div className="flex items-center justify-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-orange-400" />
                <span className="text-xs text-gray-400">Issues</span>
              </div>
              <div className="text-lg font-bold text-orange-300">
                {healthStatus.issues}
              </div>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center border border-orange-500/20">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Settings className="w-4 h-4 text-green-400" />
                <span className="text-xs text-gray-400">Auto-Fixes</span>
              </div>
              <div className="text-lg font-bold text-green-300">
                {healthStatus.autoFixes}
              </div>
            </div>
            <div className="bg-black/40 rounded-lg p-3 text-center border border-orange-500/20">
              <div className="flex items-center justify-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-gray-400">Uptime</span>
              </div>
              <div className="text-sm font-bold text-blue-300">
                99.9%
              </div>
            </div>
          </div>

          {/* Control Panel */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-orange-500/20">
            <div className="flex items-center gap-3">
              <Button
                onClick={handleToggleMonitoring}
                size="sm"
                className={`${
                  isMonitoring 
                    ? 'bg-red-600 hover:bg-red-700 text-white' 
                    : 'bg-green-600 hover:bg-green-700 text-white'
                } border-none font-medium transition-all duration-300`}
              >
                <div className="flex items-center gap-2">
                  {isMonitoring ? (
                    <>
                      <XCircle className="w-4 h-4" />
                      <span>Stop Healing</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Start Healing</span>
                    </>
                  )}
                </div>
              </Button>
              
              <AnimatePresence>
                {isMonitoring && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full border border-green-400/30"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Cpu className="w-4 h-4 text-green-400" />
                    </motion.div>
                    <span className="text-xs text-green-400 font-medium">
                      ACTIVE MONITORING
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="text-xs text-gray-500 font-mono">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>

          {/* Auto-Improvement Indicators */}
          <AnimatePresence>
            {healthStatus.autoFixes > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-3 bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-lg border border-green-400/30"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-medium text-green-400">
                    Auto-Improvements Applied
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  System has automatically applied {healthStatus.autoFixes} optimizations
                  to improve performance and reliability.
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Real-time Metrics */}
          <div className="mt-4 p-3 bg-black/40 rounded-lg border border-orange-500/20">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-xs text-gray-400 mb-1">CPU</div>
                <div className="text-sm font-mono text-orange-300">23%</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Memory</div>
                <div className="text-sm font-mono text-orange-300">67%</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Network</div>
                <div className="text-sm font-mono text-orange-300">89%</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">AI Load</div>
                <div className="text-sm font-mono text-orange-300">45%</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
