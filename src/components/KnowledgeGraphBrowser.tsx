'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Network, 
  Search, 
  Filter, 
  Plus, 
  Trash2, 
  Eye, 
  Edit3, 
  Download, 
  Upload,
  Database,
  GitBranch,
  Users,
  FileText,
  Tag,
  Clock,
  Activity,
  Zap,
  Brain,
  Settings,
  RefreshCw,
  Maximize2,
  Minimize2
} from 'lucide-react'

// Simple SVG-based graph visualization component
const SimpleForceGraph = ({ graphData, onNodeClick }: { 
  graphData: { nodes: any[], links: any[] }, 
  onNodeClick?: (node: any) => void 
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  
  useEffect(() => {
    if (!svgRef.current || !graphData) return
    
    const svg = svgRef.current
    const width = 800
    const height = 600
    
    // Clear previous content
    svg.innerHTML = ''
    
    // Create simple force simulation manually
    const nodes = graphData.nodes.map((node, i) => ({
      ...node,
      x: Math.random() * width,
      y: Math.random() * height,
      fx: null,
      fy: null
    }))
    
    const links = graphData.links.map(link => ({
      ...link,
      source: nodes.find(n => n.id === link.source),
      target: nodes.find(n => n.id === link.target)
    })).filter(link => link.source && link.target)
    
    // Draw links
    links.forEach(link => {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
      line.setAttribute('x1', link.source.x.toString())
      line.setAttribute('y1', link.source.y.toString())
      line.setAttribute('x2', link.target.x.toString())
      line.setAttribute('y2', link.target.y.toString())
      line.setAttribute('stroke', '#666')
      line.setAttribute('stroke-width', '2')
      svg.appendChild(line)
    })
    
    // Draw nodes
    nodes.forEach(node => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
      circle.setAttribute('cx', node.x.toString())
      circle.setAttribute('cy', node.y.toString())
      circle.setAttribute('r', '8')
      circle.setAttribute('fill', node.color || '#3b82f6')
      circle.setAttribute('stroke', '#fff')
      circle.setAttribute('stroke-width', '2')
      circle.style.cursor = 'pointer'
      
      if (onNodeClick) {
        circle.addEventListener('click', () => onNodeClick(node))
      }
      
      svg.appendChild(circle)
      
      // Add label
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      text.setAttribute('x', (node.x + 12).toString())
      text.setAttribute('y', (node.y + 4).toString())
      text.setAttribute('font-size', '12')
      text.setAttribute('fill', '#333')
      text.textContent = node.name || node.id
      svg.appendChild(text)
    })
  }, [graphData, onNodeClick])
  
  return (
    <svg 
      ref={svgRef} 
      width="800" 
      height="600" 
      viewBox="0 0 800 600"
      className="border rounded-lg bg-white dark:bg-gray-900"
    />
  )
}

interface KnowledgeNode {
  id: string
  name: string
  type: 'entity' | 'concept' | 'relation' | 'memory' | 'tool' | 'agent'
  category: string
  properties: Record<string, any>
  observations: string[]
  connections: string[]
  metadata: {
    created: Date
    lastModified: Date
    accessCount: number
    relevanceScore: number
  }
}

interface KnowledgeEdge {
  id: string
  source: string
  target: string
  type: string
  weight: number
  properties: Record<string, any>
  metadata: {
    created: Date
    strength: number
  }
}

interface GraphData {
  nodes: KnowledgeNode[]
  links: KnowledgeEdge[]
}

interface SearchResult {
  node: KnowledgeNode
  relevance: number
  path: string[]
}

interface KnowledgeGraphBrowserProps {
  isDarkTheme: boolean
}

export default function KnowledgeGraphBrowser({ isDarkTheme }: KnowledgeGraphBrowserProps) {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] })
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [activeTab, setActiveTab] = useState('graph')
  const [filterType, setFilterType] = useState<string>('all')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isGraphLoading, setIsGraphLoading] = useState(false)

  // Mock data initialization
  useEffect(() => {
    const mockNodes: KnowledgeNode[] = [
      {
        id: 'agent-voltagent',
        name: 'VoltAgent System',
        type: 'agent',
        category: 'AI System',
        properties: {
          version: '2.0',
          capabilities: ['reasoning', 'code-generation', 'multi-modal'],
          status: 'active'
        },
        observations: [
          'High-performance autonomous agent system',
          'Integrates multiple AI models',
          'Supports reinforcement learning'
        ],
        connections: ['model-gemini', 'model-deepseek', 'tool-mcp'],
        metadata: {
          created: new Date('2024-01-15'),
          lastModified: new Date(),
          accessCount: 247,
          relevanceScore: 0.95
        }
      },
      {
        id: 'model-gemini',
        name: 'Gemini 2.5 Flash',
        type: 'entity',
        category: 'AI Model',
        properties: {
          provider: 'Google',
          type: 'multimodal',
          contextWindow: '2M tokens',
          capabilities: ['text', 'vision', 'code']
        },
        observations: [
          'Advanced multimodal language model',
          'Excellent reasoning capabilities',
          'Fast inference speed'
        ],
        connections: ['agent-voltagent', 'concept-reasoning', 'memory-system'],
        metadata: {
          created: new Date('2024-01-10'),
          lastModified: new Date(),
          accessCount: 189,
          relevanceScore: 0.92
        }
      },
      {
        id: 'model-deepseek',
        name: 'DeepSeek R1',
        type: 'entity',
        category: 'AI Model',
        properties: {
          provider: 'DeepSeek',
          type: 'reasoning',
          specialty: 'chain-of-thought',
          localProcessing: true
        },
        observations: [
          'Specialized in mathematical reasoning',
          'Chain-of-thought processing',
          'Local deployment capability'
        ],
        connections: ['agent-voltagent', 'concept-reasoning', 'concept-mathematics'],
        metadata: {
          created: new Date('2024-01-12'),
          lastModified: new Date(),
          accessCount: 156,
          relevanceScore: 0.88
        }
      },
      {
        id: 'tool-mcp',
        name: 'Model Context Protocol',
        type: 'tool',
        category: 'Integration',
        properties: {
          version: '1.0',
          functions: ['filesystem', 'memory', 'github', 'huggingface'],
          status: 'active'
        },
        observations: [
          'Standardized protocol for AI tool integration',
          'Enables seamless tool access',
          'Supports multiple tool categories'
        ],
        connections: ['agent-voltagent', 'memory-system', 'concept-integration'],
        metadata: {
          created: new Date('2024-01-08'),
          lastModified: new Date(),
          accessCount: 312,
          relevanceScore: 0.90
        }
      },
      {
        id: 'concept-reasoning',
        name: 'AI Reasoning',
        type: 'concept',
        category: 'AI Capability',
        properties: {
          definition: 'Ability to draw logical conclusions',
          importance: 'critical',
          applications: ['problem-solving', 'decision-making', 'analysis']
        },
        observations: [
          'Fundamental capability for AI systems',
          'Enables complex problem solving',
          'Critical for autonomous operation'
        ],
        connections: ['model-gemini', 'model-deepseek', 'concept-intelligence'],
        metadata: {
          created: new Date('2024-01-05'),
          lastModified: new Date(),
          accessCount: 98,
          relevanceScore: 0.85
        }
      },
      {
        id: 'memory-system',
        name: 'Knowledge Memory System',
        type: 'memory',
        category: 'Data Storage',
        properties: {
          type: 'graph-based',
          size: '10k+ nodes',
          queryPerformance: 'high'
        },
        observations: [
          'Persistent knowledge storage',
          'Graph-based relationships',
          'Fast query performance'
        ],
        connections: ['agent-voltagent', 'tool-mcp', 'concept-knowledge'],
        metadata: {
          created: new Date('2024-01-01'),
          lastModified: new Date(),
          accessCount: 445,
          relevanceScore: 0.93
        }
      }
    ]

    const mockLinks: KnowledgeEdge[] = [
      {
        id: 'link-1',
        source: 'agent-voltagent',
        target: 'model-gemini',
        type: 'uses',
        weight: 5,
        properties: { frequency: 'high', performance: 'excellent' },
        metadata: { created: new Date(), strength: 0.9 }
      },
      {
        id: 'link-2',
        source: 'agent-voltagent',
        target: 'model-deepseek',
        type: 'uses',
        weight: 4,
        properties: { frequency: 'medium', performance: 'good' },
        metadata: { created: new Date(), strength: 0.7 }
      },
      {
        id: 'link-3',
        source: 'agent-voltagent',
        target: 'tool-mcp',
        type: 'integrates',
        weight: 5,
        properties: { dependency: 'critical' },
        metadata: { created: new Date(), strength: 0.95 }
      },
      {
        id: 'link-4',
        source: 'model-gemini',
        target: 'concept-reasoning',
        type: 'implements',
        weight: 4,
        properties: { capability: 'advanced' },
        metadata: { created: new Date(), strength: 0.8 }
      },
      {
        id: 'link-5',
        source: 'model-deepseek',
        target: 'concept-reasoning',
        type: 'specializes',
        weight: 5,
        properties: { specialty: 'mathematical' },
        metadata: { created: new Date(), strength: 0.9 }
      },
      {
        id: 'link-6',
        source: 'tool-mcp',
        target: 'memory-system',
        type: 'accesses',
        weight: 4,
        properties: { operations: ['read', 'write', 'query'] },
        metadata: { created: new Date(), strength: 0.85 }
      }
    ]

    setGraphData({ nodes: mockNodes, links: mockLinks })
  }, [])

  // Search functionality
  useEffect(() => {
    if (searchQuery.trim()) {
      const results = graphData.nodes
        .filter(node => 
          node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          node.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
          node.observations.some(obs => obs.toLowerCase().includes(searchQuery.toLowerCase()))
        )
        .map(node => ({
          node,
          relevance: calculateRelevance(node, searchQuery),
          path: findShortestPath(node.id, graphData)
        }))
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 10)

      setSearchResults(results)
    } else {
      setSearchResults([])
    }
  }, [searchQuery, graphData])

  const calculateRelevance = (node: KnowledgeNode, query: string): number => {
    const queryLower = query.toLowerCase()
    let score = 0
    
    if (node.name.toLowerCase().includes(queryLower)) score += 0.5
    if (node.category.toLowerCase().includes(queryLower)) score += 0.3
    
    node.observations.forEach(obs => {
      if (obs.toLowerCase().includes(queryLower)) score += 0.2
    })
    
    return Math.min(score + node.metadata.relevanceScore * 0.1, 1.0)
  }

  const findShortestPath = (nodeId: string, graph: GraphData): string[] => {
    // Simplified path finding - in real implementation, use proper graph algorithms
    return [nodeId]
  }

  const getNodeColor = (node: KnowledgeNode) => {
    switch (node.type) {
      case 'agent': return '#3b82f6'
      case 'entity': return '#10b981'
      case 'concept': return '#f59e0b'
      case 'memory': return '#8b5cf6'
      case 'tool': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getNodeSize = (node: KnowledgeNode) => {
    return Math.max(5, Math.min(15, node.metadata.relevanceScore * 15))
  }

  const filteredNodes = filterType === 'all' 
    ? graphData.nodes 
    : graphData.nodes.filter(node => node.type === filterType)

  const filteredLinks = graphData.links.filter(link => 
    filteredNodes.some(n => n.id === link.source) && 
    filteredNodes.some(n => n.id === link.target)
  )

  const graphDataFiltered = {
    nodes: filteredNodes.map(node => ({
      id: node.id,
      name: node.name,
      color: getNodeColor(node),
      size: getNodeSize(node),
      type: node.type,
      ...node
    })),
    links: filteredLinks.map(link => ({
      source: link.source,
      target: link.target,
      color: '#64748b',
      width: link.weight,
      ...link
    }))
  }

  return (
    <div className={`space-y-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-gray-900 p-6' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="w-6 h-6 text-purple-400" />
            Knowledge Graph
          </h2>
          <Badge variant="outline" className="text-purple-400 border-purple-400">
            {graphData.nodes.length} nodes • {graphData.links.length} edges
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsGraphLoading(true)}
            className="text-gray-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${isGraphLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Download className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Upload className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="text-gray-400 hover:text-white"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Search knowledge graph..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-gray-800 border-gray-600 text-white"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-gray-800 border border-gray-600 text-white rounded px-3 py-2"
          >
            <option value="all">All Types</option>
            <option value="agent">Agents</option>
            <option value="entity">Entities</option>
            <option value="concept">Concepts</option>
            <option value="memory">Memory</option>
            <option value="tool">Tools</option>
          </select>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 bg-gray-800">
          <TabsTrigger value="graph" className="text-gray-300 data-[state=active]:text-white">
            Graph View
          </TabsTrigger>
          <TabsTrigger value="list" className="text-gray-300 data-[state=active]:text-white">
            Node List
          </TabsTrigger>
          <TabsTrigger value="search" className="text-gray-300 data-[state=active]:text-white">
            Search Results
          </TabsTrigger>
          <TabsTrigger value="analytics" className="text-gray-300 data-[state=active]:text-white">
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Graph View */}
        <TabsContent value="graph" className="space-y-4">
          <div className="flex gap-6">
            {/* Graph Visualization */}
            <div className={`${isFullscreen ? 'w-full' : 'w-2/3'} bg-gray-800 border border-gray-700 rounded-lg overflow-hidden`}>
              <div className={`${isFullscreen ? 'h-screen' : 'h-96'} relative flex items-center justify-center`}>
                <SimpleForceGraph
                  graphData={graphDataFiltered}
                  onNodeClick={(node: any) => setSelectedNode(node)}
                />
              </div>
            </div>

            {/* Node Details Panel */}
            {!isFullscreen && (
              <div className="w-1/3">
                {selectedNode ? (
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center justify-between">
                        {selectedNode.name}
                        <Badge 
                          variant="outline" 
                          className="text-white border-gray-600"
                          style={{ color: getNodeColor(selectedNode) }}
                        >
                          {selectedNode.type}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="text-gray-300 font-medium mb-2">Category</h4>
                        <p className="text-white">{selectedNode.category}</p>
                      </div>

                      <div>
                        <h4 className="text-gray-300 font-medium mb-2">Properties</h4>
                        <div className="space-y-1">
                          {Object.entries(selectedNode.properties).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-sm">
                              <span className="text-gray-400">{key}:</span>
                              <span className="text-white">{JSON.stringify(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-gray-300 font-medium mb-2">Observations</h4>
                        <ScrollArea className="h-24">
                          <div className="space-y-1">
                            {selectedNode.observations.map((obs, index) => (
                              <p key={index} className="text-sm text-gray-300">
                                • {obs}
                              </p>
                            ))}
                          </div>
                        </ScrollArea>
                      </div>

                      <div>
                        <h4 className="text-gray-300 font-medium mb-2">Connections</h4>
                        <p className="text-white">{selectedNode.connections.length} connections</p>
                      </div>

                      <div>
                        <h4 className="text-gray-300 font-medium mb-2">Metadata</h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Created:</span>
                            <span className="text-white">{selectedNode.metadata.created.toLocaleDateString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Access Count:</span>
                            <span className="text-white">{selectedNode.metadata.accessCount}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Relevance:</span>
                            <span className="text-green-400">{(selectedNode.metadata.relevanceScore * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="bg-gray-800 border-gray-700">
                    <CardContent className="p-8 text-center">
                      <Network className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">Click on a node to view details</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        </TabsContent>

        {/* List View */}
        <TabsContent value="list" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {graphData.nodes.map(node => (
              <Card 
                key={node.id} 
                className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
                onClick={() => setSelectedNode(node)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-white font-medium">{node.name}</h4>
                    <Badge 
                      variant="outline" 
                      className="text-white border-gray-600 text-xs"
                      style={{ color: getNodeColor(node) }}
                    >
                      {node.type}
                    </Badge>
                  </div>
                  
                  <p className="text-gray-400 text-sm mb-2">{node.category}</p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{node.connections.length} connections</span>
                    <span>{node.observations.length} observations</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Search Results */}
        <TabsContent value="search" className="space-y-4">
          {searchResults.length > 0 ? (
            <div className="space-y-3">
              {searchResults.map((result, index) => (
                <Card 
                  key={index} 
                  className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
                  onClick={() => setSelectedNode(result.node)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{result.node.name}</h4>
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant="outline" 
                          className="text-white border-gray-600 text-xs"
                          style={{ color: getNodeColor(result.node) }}
                        >
                          {result.node.type}
                        </Badge>
                        <Badge variant="outline" className="text-green-400 border-green-600 text-xs">
                          {(result.relevance * 100).toFixed(0)}% match
                        </Badge>
                      </div>
                    </div>
                    
                    <p className="text-gray-400 text-sm mb-2">{result.node.category}</p>
                    
                    <div className="text-xs text-gray-500">
                      Observations: {result.node.observations.length} • 
                      Connections: {result.node.connections.length}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : searchQuery ? (
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-8 text-center">
                <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No results found for "{searchQuery}"</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-8 text-center">
                <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Enter a search query to find nodes</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Nodes</p>
                    <p className="text-2xl font-bold text-white">{graphData.nodes.length}</p>
                  </div>
                  <Database className="w-8 h-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Edges</p>
                    <p className="text-2xl font-bold text-white">{graphData.links.length}</p>
                  </div>
                  <GitBranch className="w-8 h-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Node Types</p>
                    <p className="text-2xl font-bold text-white">
                      {new Set(graphData.nodes.map(n => n.type)).size}
                    </p>
                  </div>
                  <Tag className="w-8 h-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Avg Connections</p>
                    <p className="text-2xl font-bold text-white">
                      {(graphData.nodes.reduce((acc, n) => acc + n.connections.length, 0) / graphData.nodes.length).toFixed(1)}
                    </p>
                  </div>
                  <Activity className="w-8 h-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Node Type Distribution */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Node Type Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(
                  graphData.nodes.reduce((acc, node) => {
                    acc[node.type] = (acc[node.type] || 0) + 1
                    return acc
                  }, {} as Record<string, number>)
                ).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getNodeColor({ type } as KnowledgeNode) }}
                      />
                      <span className="text-gray-300 capitalize">{type}</span>
                    </div>
                    <Badge variant="outline" className="text-white border-gray-600">
                      {count}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
