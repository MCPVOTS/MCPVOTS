'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Activity, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Wifi, 
  AlertTriangle, 
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Download,
  Settings,
  Monitor,
  Zap,
  Database,
  Server
} from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface SystemMetrics {
  timestamp: Date
  cpu: number
  memory: number
  disk: number
  network: {
    incoming: number
    outgoing: number
  }
  agents: {
    active: number
    idle: number
    error: number
  }
  models: {
    gemini: {
      status: 'online' | 'offline' | 'busy'
      requests: number
      latency: number
      tokens: number
    }
    deepseek: {
      status: 'online' | 'offline' | 'busy'
      requests: number
      latency: number
      tokens: number
    }
  }
  mcp: {
    connections: number
    tools: number
    memory_usage: number
    knowledge_graph: {
      nodes: number
      edges: number
      queries: number
    }
  }
}

interface Alert {
  id: string
  type: 'warning' | 'error' | 'info'
  message: string
  timestamp: Date
  resolved: boolean
  component: string
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

interface TelemetryDashboardProps {
  isDarkTheme: boolean
}

export default function TelemetryDashboard({ isDarkTheme }: TelemetryDashboardProps) {
  const [metrics, setMetrics] = useState<SystemMetrics[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [activeTab, setActiveTab] = useState('overview')
  const [isRealTime, setIsRealTime] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(5000)

  // Mock data generation - in real app, this would come from your telemetry system
  useEffect(() => {
    const generateMetrics = (): SystemMetrics => ({
      timestamp: new Date(),
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100,
      network: {
        incoming: Math.random() * 1000,
        outgoing: Math.random() * 800
      },
      agents: {
        active: Math.floor(Math.random() * 10) + 1,
        idle: Math.floor(Math.random() * 5),
        error: Math.floor(Math.random() * 2)
      },
      models: {
        gemini: {
          status: Math.random() > 0.1 ? 'online' : 'busy',
          requests: Math.floor(Math.random() * 100),
          latency: Math.random() * 500 + 100,
          tokens: Math.floor(Math.random() * 10000)
        },
        deepseek: {
          status: Math.random() > 0.15 ? 'online' : 'busy',
          requests: Math.floor(Math.random() * 80),
          latency: Math.random() * 300 + 150,
          tokens: Math.floor(Math.random() * 8000)
        }
      },
      mcp: {
        connections: Math.floor(Math.random() * 20) + 5,
        tools: Math.floor(Math.random() * 50) + 10,
        memory_usage: Math.random() * 100,
        knowledge_graph: {
          nodes: Math.floor(Math.random() * 1000) + 500,
          edges: Math.floor(Math.random() * 2000) + 800,
          queries: Math.floor(Math.random() * 100)
        }
      }
    })

    // Initialize with some data
    const initialData = Array.from({ length: 20 }, () => generateMetrics())
    setMetrics(initialData)

    // Mock alerts
    setAlerts([
      {
        id: '1',
        type: 'warning',
        message: 'Memory usage above 85%',
        timestamp: new Date(Date.now() - 300000),
        resolved: false,
        component: 'System'
      },
      {
        id: '2',
        type: 'info',
        message: 'Gemini model successfully updated',
        timestamp: new Date(Date.now() - 600000),
        resolved: true,
        component: 'Models'
      }
    ])

    let interval: NodeJS.Timeout
    if (isRealTime) {
      interval = setInterval(() => {
        setMetrics(prev => {
          const newMetrics = [...prev.slice(-19), generateMetrics()]
          return newMetrics
        })
      }, refreshInterval)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRealTime, refreshInterval])

  const currentMetrics = metrics[metrics.length - 1]
  
  const formatChartData = (key: string) => {
    return metrics.slice(-10).map((metric, index) => ({
      time: index,
      value: key === 'cpu' ? metric.cpu : 
             key === 'memory' ? metric.memory :
             key === 'disk' ? metric.disk :
             key === 'network_in' ? metric.network.incoming :
             key === 'network_out' ? metric.network.outgoing : 0
    }))
  }

  const agentDistributionData = currentMetrics ? [
    { name: 'Active', value: currentMetrics.agents.active, color: '#10b981' },
    { name: 'Idle', value: currentMetrics.agents.idle, color: '#f59e0b' },
    { name: 'Error', value: currentMetrics.agents.error, color: '#ef4444' }
  ] : []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400'
      case 'busy': return 'text-yellow-400'
      case 'offline': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-900 text-green-300 border-green-600'
      case 'busy': return 'bg-yellow-900 text-yellow-300 border-yellow-600'
      case 'offline': return 'bg-red-900 text-red-300 border-red-600'
      default: return 'bg-gray-900 text-gray-300 border-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-400" />
            System Telemetry
          </h2>
          <Badge variant="outline" className={isRealTime ? 'text-green-400 border-green-400' : 'text-gray-400 border-gray-400'}>
            {isRealTime ? 'Live' : 'Paused'}
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsRealTime(!isRealTime)}
            className="text-gray-400 hover:text-white"
          >
            {isRealTime ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            {isRealTime ? 'Pause' : 'Resume'}
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Download className="w-4 h-4" />
            Export
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Alert Strip */}
      {alerts.filter(a => !a.resolved).length > 0 && (
        <Card className="bg-red-900/20 border-red-600">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-red-300 font-medium">
                {alerts.filter(a => !a.resolved).length} active alert(s)
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 bg-gray-800">
          <TabsTrigger value="overview" className="text-gray-300 data-[state=active]:text-white">
            Overview
          </TabsTrigger>
          <TabsTrigger value="system" className="text-gray-300 data-[state=active]:text-white">
            System
          </TabsTrigger>
          <TabsTrigger value="agents" className="text-gray-300 data-[state=active]:text-white">
            Agents
          </TabsTrigger>
          <TabsTrigger value="models" className="text-gray-300 data-[state=active]:text-white">
            Models
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {currentMetrics && (
              <>
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">CPU Usage</p>
                        <p className="text-2xl font-bold text-white">{currentMetrics.cpu.toFixed(1)}%</p>
                      </div>
                      <Cpu className="w-8 h-8 text-blue-400" />
                    </div>
                    <Progress value={currentMetrics.cpu} className="mt-2" />
                  </CardContent>
                </Card>

                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">Memory</p>
                        <p className="text-2xl font-bold text-white">{currentMetrics.memory.toFixed(1)}%</p>
                      </div>
                      <MemoryStick className="w-8 h-8 text-green-400" />
                    </div>
                    <Progress value={currentMetrics.memory} className="mt-2" />
                  </CardContent>
                </Card>

                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">Active Agents</p>
                        <p className="text-2xl font-bold text-white">{currentMetrics.agents.active}</p>
                      </div>
                      <Zap className="w-8 h-8 text-yellow-400" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">MCP Tools</p>
                        <p className="text-2xl font-bold text-white">{currentMetrics.mcp.tools}</p>
                      </div>
                      <Database className="w-8 h-8 text-purple-400" />
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>

          {/* System Performance Chart */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">System Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formatChartData('cpu')}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="time" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Resource Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={metrics.slice(-10)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="timestamp" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="cpu" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="memory" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="disk" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Network Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={metrics.slice(-10)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="timestamp" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Line type="monotone" dataKey="network.incoming" stroke="#10b981" strokeWidth={2} name="Incoming" />
                    <Line type="monotone" dataKey="network.outgoing" stroke="#ef4444" strokeWidth={2} name="Outgoing" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Agent Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={agentDistributionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {agentDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Agent Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {currentMetrics && (
                    <>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Active Agents</span>
                        <Badge className="bg-green-900 text-green-300 border-green-600">
                          {currentMetrics.agents.active}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Idle Agents</span>
                        <Badge className="bg-yellow-900 text-yellow-300 border-yellow-600">
                          {currentMetrics.agents.idle}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Error States</span>
                        <Badge className="bg-red-900 text-red-300 border-red-600">
                          {currentMetrics.agents.error}
                        </Badge>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {currentMetrics && (
              <>
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      Gemini 2.5 Flash
                      <Badge className={getStatusBadge(currentMetrics.models.gemini.status)}>
                        {currentMetrics.models.gemini.status}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-300">Requests</span>
                        <span className="text-white">{currentMetrics.models.gemini.requests}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Avg Latency</span>
                        <span className="text-white">{currentMetrics.models.gemini.latency.toFixed(0)}ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Tokens Processed</span>
                        <span className="text-white">{currentMetrics.models.gemini.tokens.toLocaleString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      DeepSeek R1
                      <Badge className={getStatusBadge(currentMetrics.models.deepseek.status)}>
                        {currentMetrics.models.deepseek.status}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-300">Requests</span>
                        <span className="text-white">{currentMetrics.models.deepseek.requests}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Avg Latency</span>
                        <span className="text-white">{currentMetrics.models.deepseek.latency.toFixed(0)}ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Tokens Processed</span>
                        <span className="text-white">{currentMetrics.models.deepseek.tokens.toLocaleString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>

          {/* MCP System Stats */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">MCP System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {currentMetrics && (
                  <>
                    <div className="space-y-2">
                      <h4 className="text-gray-300 font-medium">Connections</h4>
                      <p className="text-2xl font-bold text-white">{currentMetrics.mcp.connections}</p>
                      <p className="text-sm text-gray-400">Active MCP connections</p>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-gray-300 font-medium">Knowledge Graph</h4>
                      <p className="text-2xl font-bold text-white">{currentMetrics.mcp.knowledge_graph.nodes}</p>
                      <p className="text-sm text-gray-400">{currentMetrics.mcp.knowledge_graph.edges} edges, {currentMetrics.mcp.knowledge_graph.queries} queries</p>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-gray-300 font-medium">Memory Usage</h4>
                      <p className="text-2xl font-bold text-white">{currentMetrics.mcp.memory_usage.toFixed(1)}%</p>
                      <Progress value={currentMetrics.mcp.memory_usage} className="mt-2" />
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Alerts Panel */}
      {alerts.length > 0 && (
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Recent Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-32">
              <div className="space-y-2">
                {alerts.slice(0, 5).map(alert => (
                  <div 
                    key={alert.id}
                    className={`flex items-center gap-3 p-2 rounded ${
                      alert.resolved ? 'bg-gray-700' : 
                      alert.type === 'error' ? 'bg-red-900/20' : 
                      alert.type === 'warning' ? 'bg-yellow-900/20' : 'bg-blue-900/20'
                    }`}
                  >
                    <AlertTriangle className={`w-4 h-4 ${
                      alert.type === 'error' ? 'text-red-400' : 
                      alert.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm text-white">{alert.message}</p>
                      <p className="text-xs text-gray-400">
                        {alert.component} • {alert.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    {alert.resolved && (
                      <Badge variant="outline" className="text-green-400 border-green-400 text-xs">
                        Resolved
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
