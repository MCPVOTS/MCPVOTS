'use client'

import { useState } from 'react'
import { 
  Brain, 
  Zap, 
  Activity, 
  Network, 
  Terminal,
  Cpu,
  Database,
  Globe,
  Shield,
  TrendingUp,
  Settings,
  Monitor
} from 'lucide-react'
import '../styles/cyberpunk.css'

// Import regular components
import VoltAgentChat from '@/components/VoltAgentChat'
import AdvancedSelfHealingStatus from '@/components/AdvancedSelfHealingStatus'
import IntelligentMonitoringDashboard from '@/components/IntelligentMonitoringDashboard'

interface ModelStatus {
  status: 'online' | 'busy' | 'offline'
  tokensUsed: number
  lastUsed: string
  model: string
  performance: number
}

interface SystemMetrics {
  cpu: number
  memory: number
  network: number
  uptime: string
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')

  // System status tracking
  const [systemMetrics] = useState<SystemMetrics>({
    cpu: 23,
    memory: 67,
    network: 89,
    uptime: '7d 14h 32m'
  })

  // AI Models status
  const [modelStatus] = useState<ModelStatus[]>([
    {
      status: 'online',
      tokensUsed: 125847,
      lastUsed: '2 min ago',
      model: 'DeepSeek R1',
      performance: 94
    },
    {
      status: 'online',
      tokensUsed: 89632,
      lastUsed: '5 min ago',
      model: 'Gemini 2.5',
      performance: 97
    },
    {
      status: 'busy',
      tokensUsed: 234156,
      lastUsed: 'Active',
      model: 'Claude 3.5',
      performance: 91
    }
  ])

  const [mcpServers] = useState([
    { name: 'Knowledge Graph', status: 'online', connections: 4 },
    { name: 'Vector Memory', status: 'online', connections: 2 },
    { name: 'Semantic Reasoning', status: 'online', connections: 3 },
    { name: 'Content Pipeline', status: 'busy', connections: 1 },
    { name: 'Trilogy Brain', status: 'online', connections: 5 }
  ])

  return (
    <div className="cyber-container">
      <div className="cyber-grid">
        {/* Header */}
        <div className="cyber-header">
          <h1 className="cyber-title">
            <Terminal className="inline-block mr-2" />
            MCPVots AGI Command Center
            <Zap className="inline-block ml-2" />
          </h1>
          <div className="flex justify-center items-center gap-4 mt-4">
            <div className="cyber-status online">
              <Activity className="w-4 h-4" />
              System Online
            </div>
            <div className="cyber-status online">
              <Network className="w-4 h-4" />
              {mcpServers.filter(s => s.status === 'online').length} MCP Servers
            </div>
            <div className="cyber-status online">
              <Brain className="w-4 h-4" />
              {modelStatus.filter(m => m.status === 'online').length} AI Models
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex justify-center mt-6">
            <div className="flex space-x-1 bg-gray-900/50 rounded-lg p-1">
              {[
                { id: 'chat', label: 'AI Chat', icon: Brain },
                { id: 'monitoring', label: 'Monitoring', icon: Monitor },
                { id: 'healing', label: 'Self-Healing', icon: Settings }
              ].map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-6 py-2 rounded flex items-center space-x-2 text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-orange-500 text-black'
                        : 'text-orange-400 hover:text-orange-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Left Sidebar - System Status */}
        <div className="cyber-sidebar-left">
          <div className="cyber-card">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <Cpu className="w-5 h-5" />
                System Metrics
              </h3>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">CPU</span>
                  <span className="text-sm text-orange-400">{systemMetrics.cpu}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-orange-400 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${systemMetrics.cpu}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Memory</span>
                  <span className="text-sm text-blue-400">{systemMetrics.memory}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-cyan-400 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${systemMetrics.memory}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Network</span>
                  <span className="text-sm text-green-400">{systemMetrics.network}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-emerald-400 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${systemMetrics.network}%` }}
                  ></div>
                </div>
              </div>
              <div className="pt-2 border-t border-gray-700">
                <span className="text-xs text-gray-400">Uptime: {systemMetrics.uptime}</span>
              </div>
            </div>
          </div>

          <div className="cyber-card">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <Database className="w-5 h-5" />
                MCP Servers
              </h3>
            </div>
            <div className="space-y-2">
              {mcpServers.map((server, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-800/50 rounded">
                  <div>
                    <div className="text-sm font-medium">{server.name}</div>
                    <div className="text-xs text-gray-400">{server.connections} connections</div>
                  </div>
                  <div className={`cyber-status ${server.status}`}>
                    {server.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content - Tabbed Interface */}
        <div className="cyber-main-content">
          {activeTab === 'chat' && <VoltAgentChat />}
          {activeTab === 'monitoring' && <IntelligentMonitoringDashboard />}
          {activeTab === 'healing' && <AdvancedSelfHealingStatus />}
        </div>

        {/* Right Sidebar - AI Models */}
        <div className="cyber-sidebar-right">
          <div className="cyber-card">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <Brain className="w-5 h-5" />
                AI Models
              </h3>
            </div>
            <div className="space-y-3">
              {modelStatus.map((model, index) => (
                <div key={index} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium text-sm">{model.model}</div>
                      <div className="text-xs text-gray-400">{model.lastUsed}</div>
                    </div>
                    <div className={`cyber-status ${model.status}`}>
                      {model.status}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span>Performance</span>
                      <span className="text-orange-400">{model.performance}%</span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-1">
                      <div 
                        className="bg-orange-500 h-1 rounded-full"
                        style={{ width: `${model.performance}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-400">
                      Tokens: {model.tokensUsed.toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Self-Healing AGI Status Mini */}
          <div className="cyber-card mt-4">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <Brain className="w-5 h-5" />
                Self-Healing AGI
              </h3>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Status</span>
                <div className="cyber-status online">Active</div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Auto-Fixes</span>
                <span className="text-orange-400 text-sm">7 applied</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Success Rate</span>
                <span className="text-green-400 text-sm">94%</span>
              </div>
              <div className="text-xs text-gray-400 text-center mt-2">
                🧠 Learning & adapting autonomously
              </div>
            </div>
          </div>

          <div className="cyber-card">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <Shield className="w-5 h-5" />
                Security Status
              </h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Firewall</span>
                <div className="cyber-status online">Active</div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Encryption</span>
                <div className="cyber-status online">AES-256</div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Auth</span>
                <div className="cyber-status online">Secured</div>
              </div>
            </div>
          </div>

          <div className="cyber-card">
            <div className="cyber-card-header">
              <h3 className="cyber-card-title">
                <TrendingUp className="w-5 h-5" />
                Quick Actions
              </h3>
            </div>
            <div className="space-y-2">
              <button className="cyber-button w-full">
                <Globe className="w-4 h-4 mr-2" />
                Deploy Model
              </button>
              <button className="cyber-button-secondary w-full">
                <Activity className="w-4 h-4 mr-2" />
                Run Diagnostics
              </button>
              <button className="cyber-button-secondary w-full">
                <Network className="w-4 h-4 mr-2" />
                Sync Knowledge
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}