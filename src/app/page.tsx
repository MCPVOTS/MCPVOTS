'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Bot, 
  Brain, 
  Zap, 
  Cpu, 
  MessageSquare, 
  Code2, 
  Sparkles, 
  Globe, 
  Database,
  Terminal,
  Settings,
  Play,
  BarChart3
} from 'lucide-react'

interface ModelStatus {
  name: string
  status: 'online' | 'offline' | 'loading'
  version: string
  capabilities: string[]
  performance: {
    latency: number
    accuracy: number
    throughput: number
  }
}

export default function HomePage() {
  const [geminiStatus, setGeminiStatus] = useState<ModelStatus>({
    name: 'Gemini 2.5 Flash',
    status: 'online',
    version: '2.5.0',
    capabilities: ['Multimodal', 'Code Generation', 'Reasoning', '2M Context'],
    performance: { latency: 245, accuracy: 94.7, throughput: 1280 }
  })

  const [deepseekStatus, setDeepseekStatus] = useState<ModelStatus>({
    name: 'DeepSeek R1',
    status: 'online',
    version: 'R1-1.5B',
    capabilities: ['Chain of Thought', 'Math Reasoning', 'Code Analysis', 'Local Processing'],
    performance: { latency: 180, accuracy: 96.2, throughput: 890 }
  })

  const [activeTab, setActiveTab] = useState('overview')
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            MCPVots AGI Ecosystem
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Advanced AI-Powered Model Context Protocol with Gemini 2.5 & DeepSeek R1
          </p>
          <div className="flex justify-center gap-2 flex-wrap">
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Activity className="w-3 h-3 mr-1" />
              System Active
            </Badge>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              <Sparkles className="w-3 h-3 mr-1" />
              Gemini 2.5 Ready
            </Badge>
            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
              <Brain className="w-3 h-3 mr-1" />
              DeepSeek R1 Active
            </Badge>
            <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
              <Zap className="w-3 h-3 mr-1" />
              AGI Enhanced
            </Badge>
          </div>
        </div>

        {/* Main Dashboard with Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="gemini">Gemini 2.5</TabsTrigger>
            <TabsTrigger value="deepseek">DeepSeek R1</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* System Status */}
              <Card className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-600" />
                    System Status
                  </CardTitle>
                  <CardDescription>Overall system health</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>MCP Server</span>
                      <Badge className="bg-green-100 text-green-800">Online</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Trilogy AGI</span>
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>WebSocket</span>
                      <Badge className="bg-green-100 text-green-800">Connected</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Database</span>
                      <Badge className="bg-green-100 text-green-800">Healthy</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Model Overview */}
              <Card className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-blue-600" />
                    AI Models
                  </CardTitle>
                  <CardDescription>Available AI models</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-blue-500" />
                        <span>Gemini 2.5</span>
                      </div>
                      <Badge className="bg-blue-100 text-blue-800">{geminiStatus.status}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-purple-500" />
                        <span>DeepSeek R1</span>
                      </div>
                      <Badge className="bg-purple-100 text-purple-800">{deepseekStatus.status}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-green-500" />
                        <span>Claude MCP</span>
                      </div>
                      <Badge className="bg-green-100 text-green-800">Ready</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Performance Metrics */}
              <Card className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-orange-600" />
                    Performance
                  </CardTitle>
                  <CardDescription>Real-time metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Gemini Accuracy</span>
                        <span>{geminiStatus.performance.accuracy}%</span>
                      </div>
                      <Progress value={geminiStatus.performance.accuracy} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>DeepSeek Accuracy</span>
                        <span>{deepseekStatus.performance.accuracy}%</span>
                      </div>
                      <Progress value={deepseekStatus.performance.accuracy} className="h-2" />
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Avg Latency: {Math.round((geminiStatus.performance.latency + deepseekStatus.performance.latency) / 2)}ms
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Gemini 2.5 Tab */}
          <TabsContent value="gemini" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-blue-600" />
                    Gemini 2.5 Flash
                  </CardTitle>
                  <CardDescription>Google's latest multimodal AI model</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Badge variant="outline" className="mb-2">Version {geminiStatus.version}</Badge>
                      <p className="text-sm text-gray-600 mb-4">
                        Advanced multimodal AI with 2M context window, supporting text, code, images, and reasoning tasks.
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Capabilities</h4>
                      <div className="flex flex-wrap gap-1">
                        {geminiStatus.capabilities.map((cap, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">{cap}</Badge>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Latency</span>
                        <p className="font-semibold">{geminiStatus.performance.latency}ms</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Throughput</span>
                        <p className="font-semibold">{geminiStatus.performance.throughput} tok/s</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code2 className="w-5 h-5 text-green-600" />
                    Gemini Actions
                  </CardTitle>
                  <CardDescription>Available operations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Button className="w-full justify-start" variant="outline">
                      <Play className="w-4 h-4 mr-2" />
                      Start Multimodal Session
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Terminal className="w-4 h-4 mr-2" />
                      Code Generation Mode
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Globe className="w-4 h-4 mr-2" />
                      Web Search Integration
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Settings className="w-4 h-4 mr-2" />
                      Model Configuration
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* DeepSeek R1 Tab */}
          <TabsContent value="deepseek" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-600" />
                    DeepSeek R1
                  </CardTitle>
                  <CardDescription>Advanced reasoning AI model</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Badge variant="outline" className="mb-2">Version {deepseekStatus.version}</Badge>
                      <p className="text-sm text-gray-600 mb-4">
                        Specialized in chain-of-thought reasoning, mathematical problem solving, and code analysis with local processing capabilities.
                      </p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Capabilities</h4>
                      <div className="flex flex-wrap gap-1">
                        {deepseekStatus.capabilities.map((cap, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">{cap}</Badge>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Latency</span>
                        <p className="font-semibold">{deepseekStatus.performance.latency}ms</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Throughput</span>
                        <p className="font-semibold">{deepseekStatus.performance.throughput} tok/s</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-red-600" />
                    DeepSeek Actions
                  </CardTitle>
                  <CardDescription>Reasoning operations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Button className="w-full justify-start" variant="outline">
                      <Play className="w-4 h-4 mr-2" />
                      Chain-of-Thought Reasoning
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Terminal className="w-4 h-4 mr-2" />
                      Math Problem Solver
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Code2 className="w-4 h-4 mr-2" />
                      Code Analysis Mode
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Database className="w-4 h-4 mr-2" />
                      Local Processing
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle>Model Comparison</CardTitle>
                  <CardDescription>Performance metrics comparison</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">Gemini 2.5 Accuracy</span>
                        <span className="text-sm font-semibold">{geminiStatus.performance.accuracy}%</span>
                      </div>
                      <Progress value={geminiStatus.performance.accuracy} className="h-2 mb-3" />
                      
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">DeepSeek R1 Accuracy</span>
                        <span className="text-sm font-semibold">{deepseekStatus.performance.accuracy}%</span>
                      </div>
                      <Progress value={deepseekStatus.performance.accuracy} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                  <CardDescription>Real-time usage data</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span>Active Sessions</span>
                      <Badge variant="secondary">24</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Requests/Hour</span>
                      <Badge variant="secondary">1,247</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Success Rate</span>
                      <Badge className="bg-green-100 text-green-800">98.5%</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Quick Actions Footer */}
        <div className="mt-8 text-center">
          <h2 className="text-2xl font-semibold mb-4">Quick Actions</h2>
          <div className="flex justify-center gap-4 flex-wrap">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Sparkles className="w-4 h-4 mr-2" />
              Chat with Gemini 2.5
            </Button>
            <Button className="bg-purple-600 hover:bg-purple-700">
              <Brain className="w-4 h-4 mr-2" />
              Reasoning with DeepSeek
            </Button>
            <Button variant="outline">
              <BarChart3 className="w-4 h-4 mr-2" />
              View Analytics
            </Button>
            <Button variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              System Configuration
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500">
          <p>MCPVots AGI Ecosystem v2.0 - Enhanced with Gemini 2.5 & DeepSeek R1</p>
        </div>
      </div>
    </div>
  )
}
