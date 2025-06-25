'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Bot, 
  Brain, 
  Database, 
  GitBranch, 
  Globe, 
  Zap, 
  Shield, 
  Workflow,
  MessageSquare,
  Users,
  BarChart3
} from 'lucide-react'
import { MCPClient } from '@/lib/mcp/client'
import { useToast } from '@/hooks/use-toast'
import { GeminiCLIDashboard } from '@/components/GeminiCLIDashboard'

interface SystemStatus {
  mcp: 'connected' | 'disconnected' | 'error'
  trilogy: 'active' | 'inactive' | 'error'
  websocket: 'connected' | 'disconnected' | 'error'
  database: 'healthy' | 'degraded' | 'error'
}

interface MCPMetrics {
  totalRequests: number
  successRate: number
  averageResponseTime: number
  activeConnections: number
}

export default function HomePage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    mcp: 'disconnected',
    trilogy: 'inactive',
    websocket: 'disconnected',
    database: 'healthy'
  })
  
  const [mcpMetrics, setMcpMetrics] = useState<MCPMetrics>({
    totalRequests: 0,
    successRate: 0,
    averageResponseTime: 0,
    activeConnections: 0
  })
  
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const initializeSystem = async () => {
      try {
        setIsLoading(true)
        
        // Initialize MCP client
        const mcpClient = new MCPClient()
        await mcpClient.connect()
        
        setSystemStatus(prev => ({
          ...prev,
          mcp: 'connected',
          websocket: 'connected'
        }))
        
        // Fetch initial metrics
        const metrics = await mcpClient.getMetrics()
        setMcpMetrics(metrics)
        
        toast({
          title: "System Initialized",
          description: "MCP integration is now active",
        })
        
      } catch (error) {
        console.error('Failed to initialize system:', error)
        setSystemStatus(prev => ({
          ...prev,
          mcp: 'error',
          websocket: 'error'
        }))
        
        toast({
          title: "Initialization Error",
          description: "Failed to connect to MCP services",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    initializeSystem()
  }, [toast])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'healthy':
        return 'bg-green-500'
      case 'disconnected':
      case 'inactive':
      case 'degraded':
        return 'bg-yellow-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'disconnected':
        return 'Disconnected'
      case 'active':
        return 'Active'
      case 'inactive':
        return 'Inactive'
      case 'healthy':
        return 'Healthy'
      case 'degraded':
        return 'Degraded'
      case 'error':
        return 'Error'
      default:
        return 'Unknown'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          MCPVots Platform
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Next-generation Model Context Protocol integration with advanced AI capabilities and high-contrast accessibility
        </p>
      </motion.div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              System Status
            </CardTitle>
            <CardDescription>
              Real-time status of all system components
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(systemStatus).map(([service, status]) => (
                <div key={service} className="flex items-center gap-3 p-3 rounded-lg border">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
                  <div>
                    <p className="font-medium capitalize">{service}</p>
                    <p className="text-sm text-muted-foreground">{getStatusText(status)}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Dashboard */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="mcp">MCP Protocol</TabsTrigger>
          <TabsTrigger value="trilogy">Trilogy AGI</TabsTrigger>
          <TabsTrigger value="gemini">Gemini AI</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* MCP Metrics */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mcpMetrics.totalRequests.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    +12% from last hour
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mcpMetrics.successRate}%</div>
                  <Progress value={mcpMetrics.successRate} className="mt-2" />
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Connections</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mcpMetrics.activeConnections}</div>
                  <p className="text-xs text-muted-foreground">
                    {mcpMetrics.averageResponseTime}ms avg response
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="w-5 h-5" />
                  MCP Integration
                </CardTitle>
                <CardDescription>
                  Advanced Model Context Protocol implementation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Protocol Version</span>
                  <Badge variant="secondary">2024-11-05</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Transport Layer</span>
                  <Badge variant="secondary">WebSocket</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Security</span>
                  <Badge variant="secondary">TLS 1.3</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Trilogy AGI
                </CardTitle>
                <CardDescription>
                  Advanced AI capabilities and reasoning
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Memory System</span>
                  <Badge variant="outline">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Reasoning Engine</span>
                  <Badge variant="outline">Enhanced</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Self-Healing</span>
                  <Badge variant="outline">Enabled</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="mcp" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>MCP Protocol Dashboard</CardTitle>
              <CardDescription>
                Monitor and manage Model Context Protocol connections
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Globe className="w-5 h-5" />
                    <div>
                      <p className="font-medium">WebSocket Connection</p>
                      <p className="text-sm text-muted-foreground">ws://localhost:3001/mcp</p>
                    </div>
                  </div>
                  <Badge variant={systemStatus.websocket === 'connected' ? 'default' : 'destructive'}>
                    {getStatusText(systemStatus.websocket)}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Workflow className="w-5 h-5" />
                    <div>
                      <p className="font-medium">Protocol Handler</p>
                      <p className="text-sm text-muted-foreground">JSON-RPC 2.0 over WebSocket</p>
                    </div>
                  </div>
                  <Badge variant={systemStatus.mcp === 'connected' ? 'default' : 'destructive'}>
                    {getStatusText(systemStatus.mcp)}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trilogy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Trilogy AGI Integration</CardTitle>
              <CardDescription>
                Advanced AI reasoning and memory capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Memory System</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4" />
                        <span className="text-sm">Graph Database</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Reasoning Engine</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        <span className="text-sm">Enhanced Logic</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Self-Healing</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        <span className="text-sm">Auto-Recovery</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="gemini" className="space-y-4">
          <GeminiCLIDashboard />
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Analytics</CardTitle>
              <CardDescription>
                Performance metrics and usage statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">CPU Usage</span>
                    <span className="text-sm text-muted-foreground">23%</span>
                  </div>
                  <Progress value={23} />
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Memory Usage</span>
                    <span className="text-sm text-muted-foreground">67%</span>
                  </div>
                  <Progress value={67} />
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Network I/O</span>
                    <span className="text-sm text-muted-foreground">12%</span>
                  </div>
                  <Progress value={12} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
