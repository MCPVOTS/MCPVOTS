'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Bot, 
  Brain, 
  Send, 
  Copy, 
  Code2, 
  Sparkles, 
  MessageSquare,
  Cpu,
  Activity
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  model: 'deepseek-r1' | 'gemini-2.5'
  timestamp: Date
  tokens?: number
  executionTime?: number
  reasoning?: string[]
}

interface ModelConfig {
  name: string
  icon: React.ReactNode
  color: string
  bgColor: string
  status: 'online' | 'offline' | 'busy'
  capabilities: string[]
  performance: {
    latency: number
    accuracy: number
    contextWindow: string
  }
}

interface VoltAgentChatProps {
  isDarkTheme: boolean
}

export default function VoltAgentChat({ isDarkTheme }: VoltAgentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState<'deepseek-r1' | 'gemini-2.5'>('deepseek-r1')
  const [showReasoningChain, setShowReasoningChain] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const modelConfigs: Record<string, ModelConfig> = {
    'deepseek-r1': {
      name: 'DeepSeek R1',
      icon: <Brain className="w-4 h-4" />,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      status: 'online',
      capabilities: ['Chain of Thought', 'Math Reasoning', 'Code Analysis', 'Local Processing'],
      performance: {
        latency: 180,
        accuracy: 96.2,
        contextWindow: '128K tokens'
      }
    },
    'gemini-2.5': {
      name: 'Gemini 2.5 Flash',
      icon: <Sparkles className="w-4 h-4" />,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      status: 'online',
      capabilities: ['Multimodal', 'Code Generation', 'Research', '2M Context'],
      performance: {
        latency: 245,
        accuracy: 94.7,
        contextWindow: '2M tokens'
      }
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      model: selectedModel,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Simulate API call to VoltAgent backend
      const response = await simulateModelResponse(input, selectedModel)
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        role: 'assistant',
        model: selectedModel,
        timestamp: new Date(),
        tokens: response.tokens,
        executionTime: response.executionTime,
        reasoning: response.reasoning
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const simulateModelResponse = async (input: string, model: string) => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

    const responses = {
      'deepseek-r1': {
        content: `🧠 **DeepSeek R1 Analysis:**

I'll approach this step-by-step using chain-of-thought reasoning:

**Step 1: Understanding the Query**
- Analyzing the request: "${input}"
- Identifying key concepts and requirements
- Determining optimal reasoning approach

**Step 2: Knowledge Synthesis**
- Drawing from training data and contextual information
- Applying logical reasoning patterns
- Considering multiple perspectives

**Step 3: Solution Generation**
Based on my analysis, here's a comprehensive response that addresses your query with detailed reasoning and practical insights.

*Note: This is a simulated response. In the actual implementation, this would connect to the real DeepSeek R1 model via the VoltAgent bridge.*`,
        tokens: 180,
        executionTime: 1.8,
        reasoning: [
          'Parsed user input and identified intent',
          'Retrieved relevant context from knowledge base',
          'Applied logical reasoning framework',
          'Generated structured response with explanations'
        ]
      },
      'gemini-2.5': {
        content: `✨ **Gemini 2.5 Response:**

I can help you with that! Let me leverage my multimodal capabilities and extensive context window to provide a comprehensive answer.

**Key Points:**
• Analyzing your request: "${input}"
• Utilizing advanced reasoning and code generation
• Providing practical, actionable insights

**Enhanced Features:**
- 2M token context window for comprehensive understanding
- Multimodal processing capabilities
- Real-time information integration
- Code generation and analysis

*This is a simulated response showcasing Gemini 2.5's capabilities. The actual implementation would connect to the real Gemini model through the VoltAgent TypeScript bridge.*`,
        tokens: 220,
        executionTime: 2.1,
        reasoning: [
          'Processed multimodal input context',
          'Applied large context window analysis',
          'Generated contextually aware response',
          'Optimized for user engagement'
        ]
      }
    }

    return responses[model as keyof typeof responses] || responses['deepseek-r1']
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card className="border-2 border-gradient-to-r from-purple-200 to-blue-200">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-2xl bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  VoltAgent Chat
                </CardTitle>
                <p className="text-sm text-gray-600">
                  Interact with DeepSeek R1 & Gemini 2.5 through VoltAgent orchestration
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-green-50 text-green-700">
                <Activity className="w-3 h-3 mr-1" />
                Online
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Model Selection */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center">
            <Bot className="w-5 h-5 mr-2" />
            Select AI Model
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedModel} onValueChange={(value) => setSelectedModel(value as any)}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="deepseek-r1" className="flex items-center space-x-2">
                <Brain className="w-4 h-4" />
                <span>DeepSeek R1</span>
              </TabsTrigger>
              <TabsTrigger value="gemini-2.5" className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>Gemini 2.5</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="deepseek-r1" className="mt-4">
              <div className="p-4 bg-purple-50 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold flex items-center text-purple-800">
                    <Brain className="w-4 h-4 mr-2" />
                    DeepSeek R1 - Reasoning Specialist
                  </h3>
                  <Badge className="bg-purple-100 text-purple-800">Active</Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Latency: <span className="font-mono">180ms</span></p>
                    <p className="text-gray-600">Accuracy: <span className="font-mono">96.2%</span></p>
                  </div>
                  <div>
                    <p className="text-gray-600">Context: <span className="font-mono">128K tokens</span></p>
                    <p className="text-gray-600">Type: <span className="font-mono">Local Processing</span></p>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  {modelConfigs['deepseek-r1'].capabilities.map((cap, i) => (
                    <Badge key={i} variant="outline" className="text-xs bg-purple-50">
                      {cap}
                    </Badge>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="gemini-2.5" className="mt-4">
              <div className="p-4 bg-blue-50 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold flex items-center text-blue-800">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Gemini 2.5 Flash - Multimodal Expert
                  </h3>
                  <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Latency: <span className="font-mono">245ms</span></p>
                    <p className="text-gray-600">Accuracy: <span className="font-mono">94.7%</span></p>
                  </div>
                  <div>
                    <p className="text-gray-600">Context: <span className="font-mono">2M tokens</span></p>
                    <p className="text-gray-600">Type: <span className="font-mono">Cloud API</span></p>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  {modelConfigs['gemini-2.5'].capabilities.map((cap, i) => (
                    <Badge key={i} variant="outline" className="text-xs bg-blue-50">
                      {cap}
                    </Badge>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <Card className="h-96">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Conversation</CardTitle>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowReasoningChain(!showReasoningChain)}
              >
                <Code2 className="w-4 h-4 mr-1" />
                {showReasoningChain ? 'Hide' : 'Show'} Reasoning
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setMessages([])}
              >
                Clear
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-80 px-6">
            <div className="space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${
                      message.role === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : selectedModel === 'deepseek-r1' 
                          ? 'bg-purple-50 border border-purple-200' 
                          : 'bg-blue-50 border border-blue-200'
                    } rounded-lg p-3`}>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          {message.role === 'assistant' ? (
                            modelConfigs[message.model].icon
                          ) : (
                            <div className="w-4 h-4 bg-white rounded-full" />
                          )}
                          <span className="text-xs font-medium">
                            {message.role === 'user' ? 'You' : modelConfigs[message.model].name}
                          </span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(message.content)}
                        >
                          <Copy className="w-3 h-3" />
                        </Button>
                      </div>
                      <div className="prose prose-sm max-w-none">
                        {message.content.split('\n').map((line, i) => (
                          <p key={i} className="mb-1 last:mb-0">{line}</p>
                        ))}
                      </div>
                      {message.role === 'assistant' && (
                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-200">
                          <div className="flex items-center space-x-3 text-xs text-gray-500">
                            <span>⚡ {message.executionTime}s</span>
                            <span>🎯 {message.tokens} tokens</span>
                          </div>
                          {showReasoningChain && message.reasoning && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-6 text-xs"
                            >
                              <Cpu className="w-3 h-3 mr-1" />
                              Reasoning
                            </Button>
                          )}
                        </div>
                      )}
                      {showReasoningChain && message.reasoning && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-2 p-2 bg-gray-50 rounded text-xs"
                        >
                          <p className="font-medium mb-1">Reasoning Chain:</p>
                          <ol className="list-decimal list-inside space-y-1">
                            {message.reasoning.map((step, i) => (
                              <li key={i}>{step}</li>
                            ))}
                          </ol>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-100 rounded-lg p-3 flex items-center space-x-2">
                    <div className="animate-spin">
                      {modelConfigs[selectedModel].icon}
                    </div>
                    <span className="text-sm text-gray-600">
                      {modelConfigs[selectedModel].name} is thinking...
                    </span>
                  </div>
                </motion.div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </ScrollArea>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Ask ${modelConfigs[selectedModel].name} anything...`}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={isLoading}
                className="flex-1"
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={isLoading || !input.trim()}
                className="px-6"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <span>Using {modelConfigs[selectedModel].name} via VoltAgent</span>
              <span>{input.length}/2000 characters</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
