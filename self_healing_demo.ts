/**
 * Self-Healing System Demonstration
 * Shows the AGI app fixing itself in real-time
 */

import SystemRecoveryManager from '../src/services/SystemRecoveryManager'
import AdvancedSelfHealingService from '../src/services/AdvancedSelfHealingService'

class SelfHealingDemo {
  private recoveryManager: SystemRecoveryManager
  private healingService: AdvancedSelfHealingService

  constructor() {
    this.recoveryManager = new SystemRecoveryManager()
    this.healingService = new AdvancedSelfHealingService()
  }

  /**
   * Demonstrate comprehensive self-healing capabilities
   */
  async demonstrateSelfHealing(): Promise<void> {
    console.log('🚀 Starting Self-Healing AGI Demonstration...\n')

    // 1. System Health Check
    console.log('📊 Running System Diagnostics...')
    const diagnostics = await this.recoveryManager.runDiagnostics()
    
    console.log('\n📋 Diagnostic Results:')
    diagnostics.forEach(result => {
      const status = result.passed ? '✅' : '❌'
      console.log(`  ${status} ${result.name}: ${result.passed ? 'PASS' : 'FAIL'} (${result.duration.toFixed(0)}ms)`)
      if (result.error) {
        console.log(`    Error: ${result.error}`)
      }
    })

    // 2. Auto-Repair Process
    console.log('\n🔧 Starting Auto-Repair Process...')
    const repairResult = await this.recoveryManager.autoRepair()
    
    console.log(`\n📝 Repair Results:`)
    console.log(`  Success: ${repairResult.success ? '✅' : '❌'}`)
    console.log(`  Message: ${repairResult.message}`)
    
    if (repairResult.repairsApplied.length > 0) {
      console.log(`  Applied Fixes:`)
      repairResult.repairsApplied.forEach(fix => {
        console.log(`    ✅ ${fix}`)
      })
    }
    
    if (repairResult.failedRepairs && repairResult.failedRepairs.length > 0) {
      console.log(`  Failed Fixes:`)
      repairResult.failedRepairs.forEach(fix => {
        console.log(`    ❌ ${fix}`)
      })
    }

    // 3. Advanced Self-Healing Service
    console.log('\n🧠 Starting Advanced Self-Healing Service...')
    this.healingService.startSelfHealing()
    
    // Wait a bit to see the service in action
    await new Promise(resolve => setTimeout(resolve, 5000))
    
    const systemHealth = this.healingService.getSystemHealth()
    console.log(`\n📊 System Health: ${systemHealth.overall.toUpperCase()}`)
    
    console.log('\n🔍 Component Health:')
    Object.entries(systemHealth.components).forEach(([name, status]) => {
      const healthIcon = this.getHealthIcon(status.status)
      console.log(`  ${healthIcon} ${name}: ${status.performance}% (${status.trend})`)
    })

    if (systemHealth.autoFixes.length > 0) {
      console.log('\n🔧 Recent Auto-Fixes:')
      systemHealth.autoFixes.slice(-3).forEach(fix => {
        const statusIcon = fix.success ? '✅' : '❌'
        console.log(`  ${statusIcon} ${fix.description} (${(fix.confidence * 100).toFixed(0)}% confidence)`)
      })
    }

    // 4. Repair History
    const repairHistory = this.recoveryManager.getRepairHistory()
    if (repairHistory.length > 0) {
      console.log('\n📜 Repair History:')
      repairHistory.slice(-5).forEach(log => {
        const statusIcon = log.success ? '✅' : '❌'
        const time = log.timestamp.toLocaleTimeString()
        console.log(`  ${statusIcon} [${time}] ${log.action}`)
        if (log.error) {
          console.log(`    Error: ${log.error}`)
        }
      })
    }

    // 5. Demonstrate Real-Time Monitoring
    console.log('\n🔄 Real-Time Monitoring Active...')
    console.log('  The system will continue to monitor and self-heal automatically.')
    console.log('  Check the browser dashboard for live updates!')

    // 6. Performance Metrics
    this.showPerformanceMetrics()

    console.log('\n✨ Self-Healing Demonstration Complete!')
    console.log('🎯 The AGI system is now actively monitoring and fixing itself.')
  }

  /**
   * Show current performance metrics
   */
  private showPerformanceMetrics(): void {
    console.log('\n⚡ Performance Metrics:')
    
    // Memory usage
    const memInfo = this.getMemoryInfo()
    console.log(`  💾 Memory Usage: ${memInfo.usedPercent.toFixed(1)}%`)
    
    // Performance timing
    if (typeof window !== 'undefined' && window.performance) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      if (navigation) {
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart
        console.log(`  ⚡ Page Load Time: ${loadTime.toFixed(0)}ms`)
      }
    }

    // System uptime (simulated)
    const uptime = this.getSystemUptime()
    console.log(`  ⏰ System Uptime: ${uptime}`)
  }

  /**
   * Get health icon for status
   */
  private getHealthIcon(status: string): string {
    const icons: Record<string, string> = {
      'healthy': '💚',
      'degraded': '🟡',
      'failing': '🔴',
      'offline': '💀'
    }
    return icons[status] || '❓'
  }

  /**
   * Get memory information
   */
  private getMemoryInfo(): { usedPercent: number; heapUsed: number; heapTotal: number } {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const memory = (performance as unknown as { memory: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory
      return {
        usedPercent: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100,
        heapUsed: memory.usedJSHeapSize,
        heapTotal: memory.totalJSHeapSize
      }
    }
    return { usedPercent: 45, heapUsed: 0, heapTotal: 0 } // Simulated values
  }

  /**
   * Get system uptime (simulated)
   */
  private getSystemUptime(): string {
    // Simulate uptime calculation
    const hours = Math.floor(Math.random() * 24) + 1
    const minutes = Math.floor(Math.random() * 60)
    return `${hours}h ${minutes}m`
  }

  /**
   * Stop the healing service
   */
  stopDemo(): void {
    this.healingService.stopSelfHealing()
    console.log('⏹️ Self-Healing Demo Stopped')
  }
}

// Export for use in browser console or Node.js
if (typeof window !== 'undefined') {
  // Browser environment
  (window as any).SelfHealingDemo = SelfHealingDemo
  console.log('🧠 Self-Healing Demo loaded in browser. Run: new SelfHealingDemo().demonstrateSelfHealing()')
} else {
  // Node.js environment
  module.exports = SelfHealingDemo
}

export default SelfHealingDemo
