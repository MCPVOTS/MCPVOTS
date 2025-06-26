'use client'

import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Sphere, Line, Html } from '@react-three/drei'
import { Vector3, Color } from 'three'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Maximize2, 
  Minimize2, 
  Play, 
  Pause, 
  RotateCcw,
  Settings,
  Eye,
  Layers,
  Zap
} from 'lucide-react'

interface Node {
  id: string
  position: Vector3
  type: 'agent' | 'model' | 'tool' | 'memory' | 'data'
  status: 'active' | 'idle' | 'error' | 'offline'
  connections: string[]
  metadata: {
    name: string
    performance: number
    load: number
    lastActivity: Date
  }
}

interface Connection {
  from: string
  to: string
  type: 'data' | 'command' | 'response' | 'memory'
  strength: number
  animated: boolean
}

interface VisualizationData {
  nodes: Node[]
  connections: Connection[]
  stats: {
    totalNodes: number
    activeConnections: number
    dataFlow: number
    systemHealth: number
  }
}

// Enhanced 3D Node Component
function Node3D({ node, isSelected, onSelect, isDarkTheme }: { 
  node: Node, 
  isSelected: boolean, 
  onSelect: (id: string) => void,
  isDarkTheme: boolean
}) {
  const meshRef = useRef<any>()
  
  const getNodeColor = () => {
    const baseColors = {
      active: isDarkTheme ? '#10b981' : '#059669',
      idle: isDarkTheme ? '#6b7280' : '#4b5563',
      error: isDarkTheme ? '#ef4444' : '#dc2626',
      offline: isDarkTheme ? '#374151' : '#1f2937'
    }
    return baseColors[node.status] || baseColors.idle
  }

  const getTypeColor = () => {
    const typeColors = {
      agent: isDarkTheme ? '#3b82f6' : '#1d4ed8',
      model: isDarkTheme ? '#8b5cf6' : '#7c3aed',
      tool: isDarkTheme ? '#f59e0b' : '#d97706',
      memory: isDarkTheme ? '#06b6d4' : '#0891b2',
      data: isDarkTheme ? '#f97316' : '#ea580c'
    }
    return typeColors[node.type] || getNodeColor()
  }

  const getNodeSize = () => {
    const sizes = { agent: 0.9, model: 1.1, tool: 0.7, memory: 0.8, data: 0.6 }
    return sizes[node.type] || 0.7
  }

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01
      if (isSelected) {
        meshRef.current.scale.setScalar(1.3 + Math.sin(state.clock.elapsedTime * 4) * 0.1)
      } else {
        meshRef.current.scale.setScalar(1.0)
      }
    }
  })

  return (
    <group position={node.position}>
      <Sphere
        ref={meshRef}
        args={[getNodeSize(), 32, 32]}
        onClick={() => onSelect(node.id)}
        onPointerOver={() => document.body.style.cursor = 'pointer'}
        onPointerOut={() => document.body.style.cursor = 'default'}
      >
        <meshStandardMaterial 
          color={getTypeColor()} 
          emissive={isSelected ? getTypeColor() : getNodeColor()}
          emissiveIntensity={isSelected ? 0.5 : node.status === 'active' ? 0.3 : 0.1}
          metalness={0.2}
          roughness={0.3}
        />
      </Sphere>
      
      {/* Pulsing Ring for Active Nodes */}
      {node.status === 'active' && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[getNodeSize() + 0.2, getNodeSize() + 0.4, 16]} />
          <meshBasicMaterial 
            color={getTypeColor()} 
            transparent 
            opacity={0.6}
          />
        </mesh>
      )}
      
      <Html distanceFactor={15} position={[0, getNodeSize() + 0.8, 0]}>
        <div className={`px-3 py-2 rounded-lg text-xs whitespace-nowrap font-medium border shadow-lg backdrop-blur-sm ${
          isDarkTheme 
            ? 'bg-gray-900/90 text-white border-gray-700' 
            : 'bg-white/90 text-gray-900 border-gray-200'
        }`}>
          <div className="font-semibold">{node.metadata.name}</div>
          <div className={`text-xs mt-1 flex items-center space-x-2 ${
            isDarkTheme ? 'text-gray-400' : 'text-gray-600'
          }`}>
            <span>{node.type}</span>
            <span>•</span>
            <span className={`inline-block w-2 h-2 rounded-full ${
              node.status === 'active' ? 'bg-green-400' :
              node.status === 'error' ? 'bg-red-400' :
              node.status === 'idle' ? 'bg-yellow-400' : 'bg-gray-400'
            }`}></span>
            <span>{node.status}</span>
          </div>
        </div>
      </Html>
    </group>
  )
}

// Enhanced 3D Connection Component
function Connection3D({ connection, nodes, isDarkTheme }: { 
  connection: Connection, 
  nodes: Node[],
  isDarkTheme: boolean
}) {
  const fromNode = nodes.find(n => n.id === connection.from)
  const toNode = nodes.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return null

  const getConnectionColor = () => {
    const colors = {
      data: isDarkTheme ? '#3b82f6' : '#1d4ed8',
      command: isDarkTheme ? '#f59e0b' : '#d97706',
      response: isDarkTheme ? '#10b981' : '#059669',
      memory: isDarkTheme ? '#8b5cf6' : '#7c3aed'
    }
    return colors[connection.type] || (isDarkTheme ? '#6b7280' : '#4b5563')
  }

  const points = [fromNode.position, toNode.position]

  return (
    <Line
      points={points}
      color={getConnectionColor()}
      lineWidth={connection.strength * 3}
      transparent
      opacity={isDarkTheme ? 0.8 : 0.6}
    />
  )
}

// Main 3D Scene Component with Enhanced Contrast
function Scene3D({ data, selectedNode, onNodeSelect, isDarkTheme }: {
  data: VisualizationData,
  selectedNode: string | null,
  onNodeSelect: (id: string) => void,
  isDarkTheme: boolean
}) {
  const meshRef = useRef<any>()
  
  // Animate the scene
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01
    }
  })

  return (
    <>
      {/* Enhanced Lighting for High Contrast */}
      <ambientLight intensity={isDarkTheme ? 0.3 : 0.6} />
      <pointLight 
        position={[10, 10, 10]} 
        intensity={isDarkTheme ? 1.2 : 0.8}
        color={isDarkTheme ? "#ffffff" : "#fbbf24"}
      />
      <pointLight 
        position={[-10, -10, -10]} 
        color={isDarkTheme ? "#3b82f6" : "#8b5cf6"} 
        intensity={isDarkTheme ? 0.8 : 0.4} 
      />
      <spotLight
        position={[0, 10, 0]}
        angle={0.3}
        penumbra={1}
        intensity={isDarkTheme ? 0.5 : 0.3}
        color={isDarkTheme ? "#10b981" : "#06b6d4"}
        castShadow
      />
      
      {/* Central Grid/Wireframe */}
      <group ref={meshRef}>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[8, 16, 16]} />
          <meshBasicMaterial 
            color={isDarkTheme ? "#1f2937" : "#e5e7eb"} 
            wireframe 
            transparent 
            opacity={0.1}
          />
        </mesh>
      </group>
      
      {/* Render Enhanced Nodes */}
      {data.nodes.map(node => (
        <Node3D
          key={node.id}
          node={node}
          isSelected={selectedNode === node.id}
          onSelect={onNodeSelect}
          isDarkTheme={isDarkTheme}
        />
      ))}
      
      {/* Render Enhanced Connections */}
      {data.connections.map((connection, index) => (
        <Connection3D
          key={index}
          connection={connection}
          nodes={data.nodes}
          isDarkTheme={isDarkTheme}
        />
      ))}
      
      <OrbitControls 
        enablePan={true} 
        enableZoom={true} 
        enableRotate={true}
        maxDistance={50}
        minDistance={5}
      />
    </>
  )
}

interface ThreeDVisualizerProps {
  isDarkTheme: boolean
}

export default function ThreeDVisualizer({ isDarkTheme }: ThreeDVisualizerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isPlaying, setIsPlaying] = useState(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [activeView, setActiveView] = useState('network')
  const [showStats, setShowStats] = useState(true)
  
  // Mock data - in real app, this would come from your VoltAgent/MCP system
  const [visualizationData, setVisualizationData] = useState<VisualizationData>({
    nodes: [
      {
        id: 'agent-1',
        position: new Vector3(0, 0, 0),
        type: 'agent',
        status: 'active',
        connections: ['model-1', 'tool-1'],
        metadata: {
          name: 'VoltAgent-1',
          performance: 95,
          load: 60,
          lastActivity: new Date()
        }
      },
      {
        id: 'model-1',
        position: new Vector3(3, 1, 0),
        type: 'model',
        status: 'active',
        connections: ['agent-1', 'memory-1'],
        metadata: {
          name: 'Gemini 2.5',
          performance: 98,
          load: 45,
          lastActivity: new Date()
        }
      },
      {
        id: 'model-2',
        position: new Vector3(-3, 1, 0),
        type: 'model',
        status: 'active',
        connections: ['agent-1'],
        metadata: {
          name: 'DeepSeek R1',
          performance: 92,
          load: 30,
          lastActivity: new Date()
        }
      },
      {
        id: 'tool-1',
        position: new Vector3(0, -2, 2),
        type: 'tool',
        status: 'active',
        connections: ['agent-1'],
        metadata: {
          name: 'MCP Tools',
          performance: 85,
          load: 25,
          lastActivity: new Date()
        }
      },
      {
        id: 'memory-1',
        position: new Vector3(0, 2, -2),
        type: 'memory',
        status: 'active',
        connections: ['model-1', 'agent-1'],
        metadata: {
          name: 'Knowledge Graph',
          performance: 90,
          load: 40,
          lastActivity: new Date()
        }
      }
    ],
    connections: [
      { from: 'agent-1', to: 'model-1', type: 'data', strength: 0.8, animated: true },
      { from: 'agent-1', to: 'model-2', type: 'data', strength: 0.6, animated: true },
      { from: 'agent-1', to: 'tool-1', type: 'command', strength: 0.7, animated: false },
      { from: 'model-1', to: 'memory-1', type: 'memory', strength: 0.9, animated: true },
      { from: 'agent-1', to: 'memory-1', type: 'memory', strength: 0.5, animated: false }
    ],
    stats: {
      totalNodes: 5,
      activeConnections: 5,
      dataFlow: 85,
      systemHealth: 94
    }
  })

  const selectedNodeData = visualizationData.nodes.find(n => n.id === selectedNode)

  const handleReset = () => {
    setSelectedNode(null)
    // Reset camera position would go here
  }

  return (
    <Card className={`${isFullscreen ? 'fixed inset-0 z-50' : ''} bg-gray-900 border-gray-700`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-400" />
            3D Network Visualization
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsPlaying(!isPlaying)}
              className="text-gray-400 hover:text-white"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="text-gray-400 hover:text-white"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowStats(!showStats)}
              className="text-gray-400 hover:text-white"
            >
              <Eye className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="text-gray-400 hover:text-white"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="flex">
          {/* 3D Canvas */}
          <div className={`${isFullscreen ? 'w-full h-screen' : 'w-2/3 h-96'} relative`}>
            <Canvas
              camera={{ position: [8, 8, 8], fov: 50 }}
              style={{ 
                width: '100%', 
                height: '100%',
                background: isDarkTheme 
                  ? 'linear-gradient(135deg, #0f1419 0%, #1a202c 50%, #2d3748 100%)' 
                  : 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 50%, #e2e8f0 100%)'
              }}
              shadows
            >
              <Scene3D
                data={visualizationData}
                selectedNode={selectedNode}
                onNodeSelect={setSelectedNode}
                isDarkTheme={isDarkTheme}
              />
            </Canvas>
          </div>
          
          {/* Info Panel */}
          <div className={`${isFullscreen ? 'w-80' : 'w-1/3'} bg-gray-800 border-l border-gray-700 p-4`}>
            <Tabs value={activeView} onValueChange={setActiveView}>
              <TabsList className="grid w-full grid-cols-2 bg-gray-700">
                <TabsTrigger value="network" className="text-gray-300 data-[state=active]:text-white">
                  Network
                </TabsTrigger>
                <TabsTrigger value="stats" className="text-gray-300 data-[state=active]:text-white">
                  Stats
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="network" className="space-y-4 mt-4">
                {selectedNodeData ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-white border-gray-600">
                        {selectedNodeData.type}
                      </Badge>
                      <Badge 
                        variant="outline" 
                        className={`${
                          selectedNodeData.status === 'active' ? 'text-green-400 border-green-400' : 
                          selectedNodeData.status === 'error' ? 'text-red-400 border-red-400' : 
                          'text-gray-400 border-gray-400'
                        }`}
                      >
                        {selectedNodeData.status}
                      </Badge>
                    </div>
                    
                    <h3 className="text-white font-semibold">
                      {selectedNodeData.metadata.name}
                    </h3>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between text-gray-300">
                        <span>Performance:</span>
                        <span className="text-green-400">{selectedNodeData.metadata.performance}%</span>
                      </div>
                      <div className="flex justify-between text-gray-300">
                        <span>Load:</span>
                        <span className="text-yellow-400">{selectedNodeData.metadata.load}%</span>
                      </div>
                      <div className="flex justify-between text-gray-300">
                        <span>Connections:</span>
                        <span className="text-blue-400">{selectedNodeData.connections.length}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-400 text-center py-8">
                    Click on a node to view details
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="stats" className="space-y-4 mt-4">
                <div className="space-y-3">
                  <div className="flex justify-between text-gray-300">
                    <span>Total Nodes:</span>
                    <span className="text-white">{visualizationData.stats.totalNodes}</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>Active Connections:</span>
                    <span className="text-green-400">{visualizationData.stats.activeConnections}</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>Data Flow:</span>
                    <span className="text-blue-400">{visualizationData.stats.dataFlow}%</span>
                  </div>
                  <div className="flex justify-between text-gray-300">
                    <span>System Health:</span>
                    <span className="text-green-400">{visualizationData.stats.systemHealth}%</span>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="text-white font-medium mb-2">Node Types</h4>
                  <div className="space-y-2">
                    {['agent', 'model', 'tool', 'memory', 'data'].map(type => {
                      const count = visualizationData.nodes.filter(n => n.type === type).length
                      return (
                        <div key={type} className="flex justify-between text-sm">
                          <span className="text-gray-300 capitalize">{type}s:</span>
                          <span className="text-white">{count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
