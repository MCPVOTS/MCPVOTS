'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Bot, 
  Play, 
  Pause, 
  Settings, 
  Plus, 
  Activity, 
  Zap,
  Brain,
  Cpu,
  CheckCircle,
  Clock
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  type: 'voltagent' | 'autonomous' | 'specialized'
  status: 'running' | 'idle' | 'stopped' | 'error'
  model: 'gemini-2.5' | 'deepseek-r1' | 'both'
  capabilities: string[]
  metrics: {
    tasksCompleted: number
    averageExecutionTime: number
    successRate: number
    memoryUsage: number
  }
  currentTask?: {
    id: string
    description: string
    progress: number
    startTime: Date
  }
  logs: LogEntry[]
  config: {
    maxConcurrentTasks: number
    timeoutMinutes: number
    retryAttempts: number
    mcpTools: string[]
  }
}

interface LogEntry {
  timestamp: Date
  level: 'info' | 'warning' | 'error' | 'debug'
  message: string
  details?: any
}

interface Task {
  id: string
  title: string
  description: string
  agentId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  priority: 'high' | 'medium' | 'low'
  createdAt: Date
  startedAt?: Date
  completedAt?: Date
  result?: any
  error?: string
}

interface AgentOrchestratorProps {
  isDarkTheme: boolean
}

export default function AgentOrchestrator({ isDarkTheme: _isDarkTheme }: AgentOrchestratorProps) {
  const [agents, setAgents] = useState<Agent[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('agents')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [isOrchestratorRunning, setIsOrchestratorRunning] = useState(true)

  // Initialize with mock data
  useEffect(() => {
    const mockAgents: Agent[] = [
      {
        id: 'va-001',
        name: 'VoltAgent Primary',
        type: 'voltagent',
        status: 'running',
        model: 'both',
        capabilities: ['reasoning', 'code-generation', 'mcp-tools', 'memory-access'],
        metrics: {
          tasksCompleted: 47,
          averageExecutionTime: 2.3,
          successRate: 96.8,
          memoryUsage: 45.2
        },
        currentTask: {
          id: 'task-001',
          description: 'Analyzing system performance metrics',
          progress: 75,
          startTime: new Date(Date.now() - 300000)
        },
        logs: [
          {
            timestamp: new Date(Date.now() - 60000),
            level: 'info',
            message: 'Task progress: 75% - Analyzing telemetry data'
          },
          {
            timestamp: new Date(Date.now() - 120000),
            level: 'info',
            message: 'MCP tools accessed: filesystem, memory'
          }
        ],
        config: {
          maxConcurrentTasks: 3,
          timeoutMinutes: 30,
          retryAttempts: 3,
          mcpTools: ['filesystem', 'memory', 'github', 'huggingface']
        }
      },
      {
        id: 'va-002',
        name: 'Code Specialist',
        type: 'specialized',
        status: 'idle',
        model: 'gemini-2.5',
        capabilities: ['code-analysis', 'refactoring', 'documentation', 'testing'],
        metrics: {
          tasksCompleted: 23,
          averageExecutionTime: 4.1,
          successRate: 91.3,
          memoryUsage: 28.7
        },
        logs: [
          {
            timestamp: new Date(Date.now() - 300000),
            level: 'info',
            message: 'Agent initialized and ready for tasks'
          }
        ],
        config: {
          maxConcurrentTasks: 2,
          timeoutMinutes: 45,
          retryAttempts: 2,
          mcpTools: ['filesystem', 'github']
        }
      },
      {
        id: 'va-003',
        name: 'Memory Manager',
        type: 'specialized',
        status: 'running',
        model: 'deepseek-r1',
        capabilities: ['knowledge-graph', 'memory-optimization', 'data-analysis'],
        metrics: {
          tasksCompleted: 31,
          averageExecutionTime: 1.8,
          successRate: 98.7,
          memoryUsage: 67.3
        },
        currentTask: {
          id: 'task-002',
          description: 'Optimizing knowledge graph structure',
          progress: 45,
          startTime: new Date(Date.now() - 180000)
        },
        logs: [
          {
            timestamp: new Date(Date.now() - 30000),
            level: 'info',
            message: 'Knowledge graph optimization in progress'
          },
          {
            timestamp: new Date(Date.now() - 90000),
            level: 'warning',
            message: 'High memory usage detected, implementing cleanup'
          }
        ],
        config: {
          maxConcurrentTasks: 1,
          timeoutMinutes: 60,
          retryAttempts: 5,
          mcpTools: ['memory', 'memory2']
        }
      }
    ]

    const mockTasks: Task[] = [
      {
        id: 'task-001',
        title: 'System Performance Analysis',
        description: 'Analyze current system performance and provide optimization recommendations',
        agentId: 'va-001',
        status: 'running',
        priority: 'high',
        createdAt: new Date(Date.now() - 400000),
        startedAt: new Date(Date.now() - 300000)
      },
      {
        id: 'task-002',
        title: 'Knowledge Graph Optimization',
        description: 'Optimize knowledge graph structure for better query performance',
        agentId: 'va-003',
        status: 'running',
        priority: 'medium',
        createdAt: new Date(Date.now() - 300000),
        startedAt: new Date(Date.now() - 180000)
      },
      {
        id: 'task-003',
        title: 'Code Review Assistant',
        description: 'Review recent code changes and suggest improvements',
        agentId: 'va-002',
        status: 'pending',
        priority: 'low',
        createdAt: new Date(Date.now() - 120000)
      }
    ]

    setAgents(mockAgents)
    setTasks(mockTasks)
  }, [])

  const selectedAgentData = agents.find(a => a.id === selectedAgent)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400'
      case 'idle': return 'text-yellow-400'
      case 'stopped': return 'text-gray-400'
      case 'error': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-900 text-green-300 border-green-600'
      case 'idle': return 'bg-yellow-900 text-yellow-300 border-yellow-600'
      case 'stopped': return 'bg-gray-900 text-gray-300 border-gray-600'
      case 'error': return 'bg-red-900 text-red-300 border-red-600'
      default: return 'bg-gray-900 text-gray-300 border-gray-600'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400'
      case 'medium': return 'text-yellow-400'
      case 'low': return 'text-green-400'
      default: return 'text-gray-400'
    }
  }

  const handleStartAgent = (agentId: string) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status: 'running' } : agent
    ))
  }

  const handleStopAgent = (agentId: string) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status: 'stopped', currentTask: undefined } : agent
    ))
  }

  const handleCreateTask = () => {
    if (!newTaskDescription.trim()) return

    const newTask: Task = {
      id: `task-${Date.now()}`,
      title: newTaskDescription.split('.')[0] || 'New Task',
      description: newTaskDescription,
      agentId: '',
      status: 'pending',
      priority: 'medium',
      createdAt: new Date()
    }

    setTasks(prev => [...prev, newTask])
    setNewTaskDescription('')
  }

  const handleAssignTask = (taskId: string, agentId: string) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, agentId, status: 'running', startedAt: new Date() } : task
    ))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Bot className="w-6 h-6 text-blue-400" />
            Agent Orchestrator
          </h2>
          <Badge variant="outline" className={isOrchestratorRunning ? 'text-green-400 border-green-400' : 'text-red-400 border-red-400'}>
            {isOrchestratorRunning ? 'Active' : 'Stopped'}
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOrchestratorRunning(!isOrchestratorRunning)}
            className={isOrchestratorRunning ? 'text-red-400 hover:text-red-300' : 'text-green-400 hover:text-green-300'}
          >
            {isOrchestratorRunning ? (
              <>
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-1" />
                Start
              </>
            )}
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Agents</p>
                <p className="text-2xl font-bold text-white">{agents.filter(a => a.status === 'running').length}</p>
              </div>
              <Activity className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Running Tasks</p>
                <p className="text-2xl font-bold text-white">{tasks.filter(t => t.status === 'running').length}</p>
              </div>
              <Zap className="w-8 h-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Pending Tasks</p>
                <p className="text-2xl font-bold text-white">{tasks.filter(t => t.status === 'pending').length}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Success Rate</p>
                <p className="text-2xl font-bold text-white">
                  {agents.length > 0 ? Math.round(agents.reduce((acc, a) => acc + a.metrics.successRate, 0) / agents.length) : 0}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 bg-gray-800">
          <TabsTrigger value="agents" className="text-gray-300 data-[state=active]:text-white">
            Agents
          </TabsTrigger>
          <TabsTrigger value="tasks" className="text-gray-300 data-[state=active]:text-white">
            Tasks
          </TabsTrigger>
          <TabsTrigger value="logs" className="text-gray-300 data-[state=active]:text-white">
            Logs
          </TabsTrigger>
        </TabsList>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Agents ({agents.length})</h3>
                <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4 mr-1" />
                  Add Agent
                </Button>
              </div>
              
              <div className="space-y-3">
                {agents.map(agent => (
                  <Card 
                    key={agent.id} 
                    className={`bg-gray-800 border-gray-700 cursor-pointer transition-colors ${
                      selectedAgent === agent.id ? 'ring-2 ring-blue-500' : 'hover:bg-gray-750'
                    }`}
                    onClick={() => setSelectedAgent(agent.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-white font-medium">{agent.name}</h4>
                        <Badge className={getStatusBadge(agent.status)}>
                          {agent.status}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400 mb-2">
                        <span className="flex items-center gap-1">
                          <Brain className="w-3 h-3" />
                          {agent.model}
                        </span>
                        <span className="flex items-center gap-1">
                          <Cpu className="w-3 h-3" />
                          {agent.metrics.memoryUsage.toFixed(1)}% RAM
                        </span>
                      </div>
                      
                      {agent.currentTask && (
                        <div className="text-sm text-blue-400">
                          Current: {agent.currentTask.description}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-3">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation()
                              agent.status === 'running' ? handleStopAgent(agent.id) : handleStartAgent(agent.id)
                            }}
                            className={agent.status === 'running' ? 'text-red-400 hover:text-red-300' : 'text-green-400 hover:text-green-300'}
                          >
                            {agent.status === 'running' ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                          </Button>
                        </div>
                        <div className="text-sm text-gray-400">
                          {agent.metrics.tasksCompleted} tasks completed
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Agent Details */}
            <div>
              {selectedAgentData ? (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      {selectedAgentData.name}
                      <Badge className={getStatusBadge(selectedAgentData.status)}>
                        {selectedAgentData.status}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm">Success Rate</p>
                        <p className="text-xl font-bold text-green-400">{selectedAgentData.metrics.successRate}%</p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Avg Time</p>
                        <p className="text-xl font-bold text-blue-400">{selectedAgentData.metrics.averageExecutionTime}s</p>
                      </div>
                    </div>

                    {/* Current Task */}
                    {selectedAgentData.currentTask && (
                      <div className="bg-gray-700 p-3 rounded">
                        <h4 className="text-white font-medium mb-2">Current Task</h4>
                        <p className="text-gray-300 text-sm mb-2">{selectedAgentData.currentTask.description}</p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-400">Progress:</span>
                          <span className="text-blue-400">{selectedAgentData.currentTask.progress}%</span>
                        </div>
                      </div>
                    )}

                    {/* Capabilities */}
                    <div>
                      <h4 className="text-white font-medium mb-2">Capabilities</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgentData.capabilities.map(cap => (
                          <Badge key={cap} variant="outline" className="text-gray-300 border-gray-600">
                            {cap}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* MCP Tools */}
                    <div>
                      <h4 className="text-white font-medium mb-2">MCP Tools</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgentData.config.mcpTools.map(tool => (
                          <Badge key={tool} variant="outline" className="text-blue-300 border-blue-600">
                            {tool}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Recent Logs */}
                    <div>
                      <h4 className="text-white font-medium mb-2">Recent Logs</h4>
                      <ScrollArea className="h-24">
                        <div className="space-y-1">
                          {selectedAgentData.logs.slice(-3).map((log, index) => (
                            <div key={index} className="text-sm">
                              <span className="text-gray-400">{log.timestamp.toLocaleTimeString()}</span>
                              <span className={`ml-2 ${
                                log.level === 'error' ? 'text-red-400' : 
                                log.level === 'warning' ? 'text-yellow-400' : 'text-gray-300'
                              }`}>
                                {log.message}
                              </span>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-8 text-center">
                    <Bot className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">Select an agent to view details</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-4">
          {/* Create Task */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Create New Task</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Describe the task you want to create..."
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  className="bg-gray-700 border-gray-600 text-white"
                  onKeyPress={(e) => e.key === 'Enter' && handleCreateTask()}
                />
                <Button onClick={handleCreateTask} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Task List */}
          <div className="space-y-3">
            {tasks.map(task => (
              <Card key={task.id} className="bg-gray-800 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-white font-medium">{task.title}</h4>
                    <div className="flex items-center gap-2">
                      <Badge className={`${
                        task.priority === 'high' ? 'bg-red-900 text-red-300 border-red-600' :
                        task.priority === 'medium' ? 'bg-yellow-900 text-yellow-300 border-yellow-600' :
                        'bg-green-900 text-green-300 border-green-600'
                      }`}>
                        {task.priority}
                      </Badge>
                      <Badge className={getStatusBadge(task.status)}>
                        {task.status}
                      </Badge>
                    </div>
                  </div>
                  
                  <p className="text-gray-300 text-sm mb-3">{task.description}</p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <span>Created: {task.createdAt.toLocaleString()}</span>
                    {task.agentId && (
                      <span>Agent: {agents.find(a => a.id === task.agentId)?.name || 'Unknown'}</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">System Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-2">
                  {agents.flatMap(agent => 
                    agent.logs.map((log, index) => (
                      <div key={`${agent.id}-${index}`} className="flex items-start gap-3 p-2 rounded bg-gray-700">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          log.level === 'error' ? 'bg-red-400' : 
                          log.level === 'warning' ? 'bg-yellow-400' : 
                          log.level === 'info' ? 'bg-blue-400' : 'bg-gray-400'
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-gray-400 text-xs">{log.timestamp.toLocaleString()}</span>
                            <Badge variant="outline" className="text-xs text-gray-400 border-gray-600">
                              {agent.name}
                            </Badge>
                            <Badge variant="outline" className={`text-xs ${
                              log.level === 'error' ? 'text-red-400 border-red-600' : 
                              log.level === 'warning' ? 'text-yellow-400 border-yellow-600' : 
                              'text-blue-400 border-blue-600'
                            }`}>
                              {log.level.toUpperCase()}
                            </Badge>
                          </div>
                          <p className="text-gray-300 text-sm">{log.message}</p>
                        </div>
                      </div>
                    ))
                  ).sort((a, b) => new Date(b.key.split('-')[2]).getTime() - new Date(a.key.split('-')[2]).getTime()).slice(0, 20)}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
