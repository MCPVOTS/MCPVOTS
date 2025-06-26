import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Workflow, 
  Play, 
  Pause, 
  Settings, 
  Activity, 
  Zap, 
  Brain, 
  GitBranch,
  Database,
  Server,
  Monitor,
  RefreshCw,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Cpu,
  HardDrive,
  Network
} from 'lucide-react'

interface N8nIntegrationProps {
  isDarkTheme: boolean
}

interface WorkflowStatus {
  id: string
  name: string
  active: boolean
  lastRun: string
  status: 'success' | 'running' | 'error' | 'idle'
  executions: number
  avgDuration: number
}

interface AGIService {
  name: string
  port: number
  status: 'healthy' | 'degraded' | 'down'
  uptime: string
  requests: number
  avgResponseTime: number
}

export default function N8nIntegration({ isDarkTheme }: N8nIntegrationProps) {
  const [workflows, setWorkflows] = useState<WorkflowStatus[]>([])
  const [agiServices, setAgiServices] = useState<AGIService[]>([])
  const [activeTab, setActiveTab] = useState('overview')
  const [isConnected, setIsConnected] = useState(false)
  const [realTimeData, setRealTimeData] = useState<any[]>([])
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0
  })

  // Initialize mock data and real-time connection
  useEffect(() => {
    // Mock workflows
    setWorkflows([
      {
        id: '1',
        name: 'AGI Health Monitor',
        active: true,
        lastRun: '2 minutes ago',
        status: 'success',
        executions: 1247,
        avgDuration: 1.2
      },
      {
        id: '2', 
        name: 'AI Code Optimizer',
        active: true,
        lastRun: '5 minutes ago',
        status: 'running',
        executions: 89,
        avgDuration: 15.7
      },
      {
        id: '3',
        name: 'GitHub AI Assistant',
        active: true,
        lastRun: '1 hour ago',
        status: 'success',
        executions: 234,
        avgDuration: 3.4
      },
      {
        id: '4',
        name: 'Trilogy AGI Orchestrator',
        active: true,
        lastRun: '30 seconds ago',
        status: 'success',
        executions: 2891,
        avgDuration: 0.8
      }
    ])

    // Mock AGI services (from the actual running services)
    setAgiServices([
      {
        name: 'DeerFlow Orchestrator',
        port: 8014,
        status: 'healthy',
        uptime: '2h 34m',
        requests: 1247,
        avgResponseTime: 45
      },
      {
        name: 'DGM Evolution Engine',
        port: 8013,
        status: 'healthy',
        uptime: '2h 34m',
        requests: 892,
        avgResponseTime: 120
      },
      {
        name: 'OWL Semantic Reasoning',
        port: 8011,
        status: 'healthy',
        uptime: '2h 34m',
        requests: 634,
        avgResponseTime: 78
      },
      {
        name: 'Agent File System',
        port: 8012,
        status: 'healthy',
        uptime: '2h 34m',
        requests: 1891,
        avgResponseTime: 23
      },
      {
        name: 'n8n Integration Server',
        port: 8020,
        status: 'healthy',
        uptime: '2h 34m',
        requests: 445,
        avgResponseTime: 67
      }
    ])

    // Simulate real-time updates
    const interval = setInterval(() => {
      setRealTimeData(prev => [
        ...prev.slice(-49),
        {
          timestamp: new Date().toISOString(),
          workflows_active: workflows.filter(w => w.active).length,
          services_healthy: agiServices.filter(s => s.status === 'healthy').length,
          total_executions: workflows.reduce((sum, w) => sum + w.executions, 0),
          avg_response_time: agiServices.reduce((sum, s) => sum + s.avgResponseTime, 0) / agiServices.length
        }
      ])

      // Update system metrics
      setSystemMetrics({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: Math.random() * 100
      })
    }, 2000)

    setIsConnected(true)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'healthy':
        return 'bg-green-500'
      case 'running':
        return 'bg-blue-500'
      case 'error':
      case 'down':
        return 'bg-red-500'
      case 'degraded':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'healthy':
        return <CheckCircle className="h-4 w-4" />
      case 'running':
        return <Clock className="h-4 w-4 animate-spin" />
      case 'error':
      case 'down':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Monitor className="h-4 w-4" />
    }
  }

  const handleWorkflowToggle = (workflowId: string) => {
    setWorkflows(prev => prev.map(w => 
      w.id === workflowId ? { ...w, active: !w.active } : w
    ))
  }

  const handleWorkflowRun = (workflowId: string) => {
    setWorkflows(prev => prev.map(w => 
      w.id === workflowId ? { ...w, status: 'running' as const, lastRun: 'now' } : w
    ))
    
    // Simulate completion after 3 seconds
    setTimeout(() => {
      setWorkflows(prev => prev.map(w => 
        w.id === workflowId ? { 
          ...w, 
          status: 'success' as const, 
          executions: w.executions + 1,
          lastRun: 'just now'
        } : w
      ))
    }, 3000)
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Workflow className="h-5 w-5" />
              n8n + AGI Integration
            </CardTitle>
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Badge className="bg-green-500 text-white">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Connected
                </Badge>
              ) : (
                <Badge className="bg-red-500 text-white">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Disconnected
                </Badge>
              )}
              <Button size="sm" variant="outline" className="text-white border-gray-600">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-gray-800 border-gray-700">
          <TabsTrigger value="overview" className="text-white">Overview</TabsTrigger>
          <TabsTrigger value="workflows" className="text-white">Workflows</TabsTrigger>
          <TabsTrigger value="services" className="text-white">AGI Services</TabsTrigger>
          <TabsTrigger value="monitoring" className="text-white">Monitoring</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Active Workflows</p>
                    <p className="text-2xl font-bold text-white">
                      {workflows.filter(w => w.active).length}
                    </p>
                  </div>
                  <Workflow className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Healthy Services</p>
                    <p className="text-2xl font-bold text-white">
                      {agiServices.filter(s => s.status === 'healthy').length}
                    </p>
                  </div>
                  <Server className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Total Executions</p>
                    <p className="text-2xl font-bold text-white">
                      {workflows.reduce((sum, w) => sum + w.executions, 0).toLocaleString()}
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Avg Response Time</p>
                    <p className="text-2xl font-bold text-white">
                      {Math.round(agiServices.reduce((sum, s) => sum + s.avgResponseTime, 0) / agiServices.length)}ms
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Real-time Activity */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Real-time Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {realTimeData.slice(-5).reverse().map((data, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-800 rounded">
                    <span className="text-sm text-gray-400">
                      {new Date(data.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-sm text-white">
                      {data.workflows_active} workflows active, {data.services_healthy} services healthy
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <div className="grid gap-4">
            {workflows.map((workflow) => (
              <Card key={workflow.id} className="bg-gray-900 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(workflow.status)}`} />
                      <div>
                        <h3 className="font-medium text-white">{workflow.name}</h3>
                        <p className="text-sm text-gray-400">
                          Last run: {workflow.lastRun} • {workflow.executions} executions
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-gray-400">
                        {workflow.avgDuration}s avg
                      </Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleWorkflowRun(workflow.id)}
                        className="text-white border-gray-600"
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleWorkflowToggle(workflow.id)}
                        className={`border-gray-600 ${workflow.active ? 'text-green-400' : 'text-gray-400'}`}
                      >
                        {workflow.active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* AGI Services Tab */}
        <TabsContent value="services" className="space-y-4">
          <div className="grid gap-4">
            {agiServices.map((service) => (
              <Card key={service.name} className="bg-gray-900 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(service.status)}
                      <div>
                        <h3 className="font-medium text-white">{service.name}</h3>
                        <p className="text-sm text-gray-400">
                          Port {service.port} • Uptime: {service.uptime}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium text-white">{service.requests}</p>
                        <p className="text-xs text-gray-400">requests</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-white">{service.avgResponseTime}ms</p>
                        <p className="text-xs text-gray-400">avg response</p>
                      </div>
                      <Badge className={getStatusColor(service.status)}>
                        {service.status}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* System Metrics */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  System Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">CPU Usage</span>
                    <span className="text-sm text-white">{Math.round(systemMetrics.cpu)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${systemMetrics.cpu}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Memory</span>
                    <span className="text-sm text-white">{Math.round(systemMetrics.memory)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${systemMetrics.memory}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Disk I/O</span>
                    <span className="text-sm text-white">{Math.round(systemMetrics.disk)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${systemMetrics.disk}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-400">Network</span>
                    <span className="text-sm text-white">{Math.round(systemMetrics.network)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${systemMetrics.network}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Activity Log */}
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Activity Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-2">
                    {realTimeData.slice(-10).reverse().map((data, index) => (
                      <div key={index} className="flex items-start gap-2 p-2 bg-gray-800 rounded text-sm">
                        <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-1" />
                        <div>
                          <span className="text-white">
                            System health check completed
                          </span>
                          <p className="text-xs text-gray-400">
                            {new Date(data.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
