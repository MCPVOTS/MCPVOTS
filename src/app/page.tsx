'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Brain, 
  Zap, 
  Sparkles, 
  MessageSquare, 
  Bot, 
  Activity, 
  Network, 
  Box, 
  FileText,
  Sun,
  Moon
} from 'lucide-react'
import dynamic from 'next/dynamic'

// Import regular components
import VoltAgentChat from '@/components/VoltAgentChat'
import AgentOrchestrator from '@/components/AgentOrchestrator'
import TelemetryDashboard from '@/components/TelemetryDashboard'
import N8nIntegration from '@/components/N8nIntegration'

// Dynamic imports for components that use client-side 3D libraries
const KnowledgeGraphBrowser = dynamic(() => import('@/components/KnowledgeGraphBrowser'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
})

const ThreeDVisualizer = dynamic(() => import('@/components/ThreeDVisualizer'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
})

interface ModelStatus {
  status: 'active' | 'idle' | 'error'
  tokensUsed: number
  lastUsed: string
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [isDarkTheme, setIsDarkTheme] = useState(true)

  // Model status tracking
  const [claudeStatus] = useState<ModelStatus>({
    status: 'active',
    tokensUsed: 125847,
    lastUsed: '2 minutes ago'
  })

  return (
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkTheme 
        ? 'bg-black text-white border-gray-800' 
        : 'bg-white text-gray-900 border-gray-200'
    }`}>
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header with enhanced contrast */}
        <div className={`relative overflow-hidden p-6 rounded-xl shadow-2xl mb-8 ${
          isDarkTheme 
            ? 'bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 border border-blue-800' 
            : 'bg-gradient-to-r from-blue-600 to-purple-600'
        }`}>
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-pulse"></div>
          <div className="relative flex justify-between items-center">
            <div>
              <h1 className={`text-4xl font-black mb-2 ${
                isDarkTheme ? 'text-white drop-shadow-2xl' : 'text-white'
              }`}>
                MCPVots Advanced AGI Platform
              </h1>
              <p className={`text-lg ${
                isDarkTheme ? 'text-blue-200' : 'text-blue-100'
              }`}>
                🤖 Next-Generation VoltAgent Integration with Full MCP Ecosystem
              </p>
              <div className="flex items-center space-x-4 mt-2">
                <Badge className="bg-green-500/20 text-green-300 border-green-500/50">
                  ⚡ Real-time AI
                </Badge>
                <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/50">
                  🧠 Multi-Model
                </Badge>
                <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/50">
                  🔗 MCP Protocol
                </Badge>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsDarkTheme(!isDarkTheme)}
                className={`p-3 rounded-full transition-all duration-300 transform hover:scale-110 ${
                  isDarkTheme 
                    ? 'bg-gray-800/80 hover:bg-gray-700/80 border border-gray-600' 
                    : 'bg-white/20 hover:bg-white/30'
                }`}
                title="Toggle Theme"
              >
                {isDarkTheme ? <Sun className="w-6 h-6 text-yellow-300" /> : <Moon className="w-6 h-6 text-white" />}
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
                <span className={`text-sm font-medium ${
                  isDarkTheme ? 'text-green-300' : 'text-white'
                }`}>System Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Model Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className={`transform hover:scale-105 transition-all duration-300 ${
            isDarkTheme 
              ? 'bg-gray-900 border-green-500/30 shadow-xl shadow-green-500/10' 
              : 'bg-white border-gray-200 shadow-lg'
          }`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-lg flex items-center ${
                isDarkTheme ? 'text-white' : 'text-gray-900'
              }`}>
                <Brain className="w-6 h-6 mr-3 text-blue-400" />
                Claude 3.5 Sonnet
                <Badge className="ml-auto bg-green-500/20 text-green-300 border-green-500/50">
                  ACTIVE
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                    <span className={`text-sm font-medium ${
                      isDarkTheme ? 'text-green-300' : 'text-green-600'
                    }`}>Active Processing</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Tokens Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
                      {claudeStatus.tokensUsed.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Last Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
                      {claudeStatus.lastUsed}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={`transform hover:scale-105 transition-all duration-300 ${
            isDarkTheme 
              ? 'bg-gray-900 border-purple-500/30 shadow-xl shadow-purple-500/10' 
              : 'bg-white border-gray-200 shadow-lg'
          }`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-lg flex items-center ${
                isDarkTheme ? 'text-white' : 'text-gray-900'
              }`}>
                <Zap className="w-6 h-6 mr-3 text-purple-400" />
                Gemini 2.5 Flash
                <Badge className="ml-auto bg-yellow-500/20 text-yellow-300 border-yellow-500/50">
                  READY
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-yellow-500 rounded-full animate-pulse shadow-lg shadow-yellow-500/50"></div>
                    <span className={`text-sm font-medium ${
                      isDarkTheme ? 'text-yellow-300' : 'text-yellow-600'
                    }`}>Standby Mode</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Tokens Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>0</div>
                  </div>
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Last Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>Never</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={`transform hover:scale-105 transition-all duration-300 ${
            isDarkTheme 
              ? 'bg-gray-900 border-orange-500/30 shadow-xl shadow-orange-500/10' 
              : 'bg-white border-gray-200 shadow-lg'
          }`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-lg flex items-center ${
                isDarkTheme ? 'text-white' : 'text-gray-900'
              }`}>
                <Sparkles className="w-6 h-6 mr-3 text-orange-400" />
                DeepSeek R1
                <Badge className="ml-auto bg-blue-500/20 text-blue-300 border-blue-500/50">
                  READY
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
                    <span className={`text-sm font-medium ${
                      isDarkTheme ? 'text-blue-300' : 'text-blue-600'
                    }`}>Reasoning Engine</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Tokens Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>0</div>
                  </div>
                  <div>
                    <div className={`font-medium ${isDarkTheme ? 'text-gray-300' : 'text-gray-600'}`}>Last Used</div>
                    <div className={`text-lg font-bold ${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>Never</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className={`grid w-full grid-cols-7 p-1 rounded-xl ${
            isDarkTheme 
              ? 'bg-gray-900 border border-gray-800' 
              : 'bg-gray-100 border border-gray-200'
          }`}>
            <TabsTrigger 
              value="chat" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'chat' 
                  ? isDarkTheme 
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' 
                    : 'bg-blue-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span className="font-medium">Chat</span>
            </TabsTrigger>
            <TabsTrigger 
              value="agents" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'agents' 
                  ? isDarkTheme 
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' 
                    : 'bg-purple-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Bot className="w-4 h-4" />
              <span className="font-medium">Agents</span>
            </TabsTrigger>
            <TabsTrigger 
              value="telemetry" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'telemetry' 
                  ? isDarkTheme 
                    ? 'bg-green-600 text-white shadow-lg shadow-green-600/30' 
                    : 'bg-green-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span className="font-medium">Telemetry</span>
            </TabsTrigger>
            <TabsTrigger 
              value="knowledge" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'knowledge' 
                  ? isDarkTheme 
                    ? 'bg-orange-600 text-white shadow-lg shadow-orange-600/30' 
                    : 'bg-orange-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Network className="w-4 h-4" />
              <span className="font-medium">Knowledge</span>
            </TabsTrigger>
            <TabsTrigger 
              value="3d" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === '3d' 
                  ? isDarkTheme 
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30' 
                    : 'bg-cyan-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Box className="w-4 h-4" />
              <span className="font-medium">3D View</span>
            </TabsTrigger>
            <TabsTrigger 
              value="n8n" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'n8n' 
                  ? isDarkTheme 
                    ? 'bg-pink-600 text-white shadow-lg shadow-pink-600/30' 
                    : 'bg-pink-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <Zap className="w-4 h-4" />
              <span className="font-medium">n8n</span>
            </TabsTrigger>
            <TabsTrigger 
              value="logs" 
              className={`flex items-center space-x-2 transition-all duration-300 rounded-lg ${
                activeTab === 'logs' 
                  ? isDarkTheme 
                    ? 'bg-gray-600 text-white shadow-lg shadow-gray-600/30' 
                    : 'bg-gray-600 text-white shadow-lg'
                  : isDarkTheme 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span className="font-medium">Logs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="mt-6">
            <VoltAgentChat isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="agents" className="mt-6">
            <AgentOrchestrator isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="telemetry" className="mt-6">
            <TelemetryDashboard isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="knowledge" className="mt-6">
            <KnowledgeGraphBrowser isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="3d" className="mt-6">
            <ThreeDVisualizer isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="n8n" className="mt-6">
            <N8nIntegration isDarkTheme={isDarkTheme} />
          </TabsContent>

          <TabsContent value="logs" className="mt-6">
            <Card className={`${
              isDarkTheme 
                ? 'bg-gray-900 border-gray-800 shadow-xl' 
                : 'bg-white border-gray-200 shadow-lg'
            }`}>
              <CardHeader>
                <CardTitle className={`flex items-center ${
                  isDarkTheme ? 'text-white' : 'text-gray-900'
                }`}>
                  <FileText className="w-5 h-5 mr-2" />
                  System Logs
                  <Badge className="ml-auto bg-green-500/20 text-green-300 border-green-500/50">
                    LIVE
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`p-4 rounded-xl font-mono text-sm max-h-96 overflow-y-auto ${
                  isDarkTheme 
                    ? 'bg-black border border-gray-800' 
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  <div className="space-y-1">
                    <div className={`${isDarkTheme ? 'text-green-400' : 'text-green-600'}`}>
                      [2024-01-20 14:30:15] INFO: VoltAgent system initialized
                    </div>
                    <div className={`${isDarkTheme ? 'text-blue-400' : 'text-blue-600'}`}>
                      [2024-01-20 14:30:16] INFO: MCP servers connected: 12
                    </div>
                    <div className={`${isDarkTheme ? 'text-purple-400' : 'text-purple-600'}`}>
                      [2024-01-20 14:30:17] INFO: Knowledge graph loaded: 1,245 nodes
                    </div>
                    <div className={`${isDarkTheme ? 'text-yellow-400' : 'text-yellow-600'}`}>
                      [2024-01-20 14:30:18] INFO: Agent orchestrator ready
                    </div>
                    <div className={`${isDarkTheme ? 'text-cyan-400' : 'text-cyan-600'}`}>
                      [2024-01-20 14:30:19] INFO: Telemetry dashboard active
                    </div>
                    <div className={`${isDarkTheme ? 'text-orange-400' : 'text-orange-600'}`}>
                      [2024-01-20 14:30:20] INFO: 3D visualization engine started
                    </div>
                    <div className={`${isDarkTheme ? 'text-white' : 'text-gray-900'}`}>
                      [2024-01-20 14:30:21] INFO: All systems operational
                    </div>
                    <div className={`${isDarkTheme ? 'text-green-400' : 'text-green-600'} font-bold`}>
                      [2024-01-20 14:30:22] SUCCESS: MCPVots platform ready
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className={isDarkTheme ? 'text-gray-400' : 'text-gray-600'}>
            MCPVots Advanced AGI Platform v3.0 - VoltAgent Enhanced with Full MCP Integration
          </p>
        </div>
      </div>
    </div>
  )
}
