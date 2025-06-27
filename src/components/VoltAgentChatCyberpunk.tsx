'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Bot, 
  Brain, 
  Send, 
  Copy, 
  Sparkles, 
  MessageSquare,
  Activity,
  Terminal,
  Network
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { realAIService } from '@/services/RealAIService'

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

export default function VoltAgentChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: "🤖 **MCPVots AGI Command Center Initialized**\n\nWelcome to the advanced AI interface. I have access to multiple AI models and MCP tools. How can I assist you today?\n\n**Available Models:**\n• DeepSeek R1 - Advanced reasoning and chain-of-thought\n• Gemini 2.5 Flash - Multimodal processing and generation\n\n**MCP Tools Available:**\n• Knowledge Graph Memory\n• Vector Database Search\n• Semantic Reasoning Engine\n• Content Processing Pipeline",
      role: 'assistant',
      model: 'deepseek-r1',
      timestamp: new Date(),
      tokens: 89,
      executionTime: 0.2
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState<'deepseek-r1' | 'gemini-2.5'>('deepseek-r1')
  const [showReasoningChain, setShowReasoningChain] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const modelConfigs: Record<string, ModelConfig> = {
    'deepseek-r1': {
      name: 'DeepSeek R1',
      icon: <Brain className="w-5 h-5" />,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/20',
      status: 'online',
      capabilities: ['Chain of Thought', 'Math Reasoning', 'Code Analysis', 'MCP Tools'],
      performance: {
        latency: 180,
        accuracy: 96.2,
        contextWindow: '128K tokens'
      }
    },
    'gemini-2.5': {
      name: 'Gemini 2.5 Flash',
      icon: <Sparkles className="w-5 h-5" />,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/20',
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
      // Connect to real AI backend services
      const response = await getRealModelResponse(input, selectedModel)
      
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
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: `❌ **Error connecting to ${selectedModel}**\n\nFailed to get response from AI service. Please check if the backend services are running.\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'assistant',
        model: selectedModel,
        timestamp: new Date(),
        tokens: 0,
        executionTime: 0
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getRealModelResponse = async (input: string, model: string) => {
    if (model === 'gemini-2.5') {
      return await realAIService.sendToGemini(input)
    } else if (model === 'deepseek-r1') {
      return await realAIService.sendToDeepSeek(input)
    } else {
      throw new Error(`Unknown model: ${model}`)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="h-full flex flex-col">
      {/* Chat Header */}
      <div className="cyber-card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal className="w-6 h-6 text-orange-400" />
            <h2 className="cyber-card-title text-xl">AGI Command Interface</h2>
          </div>
          <div className="flex items-center gap-3">
            <div className="cyber-status online">
              <Activity className="w-4 h-4" />
              System Active
            </div>
            <div className="cyber-status online">
              <Network className="w-4 h-4" />
              MCP Connected
            </div>
          </div>
        </div>
      </div>

      {/* Model Selector */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">Active Model:</span>
          <div className="flex gap-2">
            {Object.entries(modelConfigs).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setSelectedModel(key as 'deepseek-r1' | 'gemini-2.5')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300 ${
                  selectedModel === key
                    ? 'bg-orange-500/20 border-orange-500 text-orange-400'
                    : 'bg-gray-800/50 border-gray-600 text-gray-400 hover:border-orange-500/50 hover:text-orange-400'
                }`}
              >
                {config.icon}
                <span className="font-medium">{config.name}</span>
                <div className={`cyber-status ${config.status}`}>
                  {config.status}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                      {modelConfigs[message.model]?.icon || <Bot className="w-5 h-5 text-white" />}
                    </div>
                  </div>
                )}
                
                <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : ''}`}>
                  <div className={`p-4 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-orange-500/20 border border-orange-500/50' 
                      : 'bg-gray-800/90 border border-gray-600'
                  }`}>
                    {/* Message Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${
                          message.role === 'user' ? 'text-orange-400' : 'text-cyan-400'
                        }`}>
                          {message.role === 'user' ? 'You' : modelConfigs[message.model]?.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(message.timestamp)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {message.tokens && (
                          <span className="text-xs text-gray-400">
                            {message.tokens} tokens
                          </span>
                        )}
                        {message.executionTime && (
                          <span className="text-xs text-gray-400">
                            {message.executionTime}s
                          </span>
                        )}
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="text-gray-400 hover:text-orange-400 transition-colors"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Message Content */}
                    <div className="prose prose-invert max-w-none">
                      <div className="whitespace-pre-wrap text-gray-200">
                        {message.content}
                      </div>
                    </div>

                    {/* Reasoning Chain */}
                    {message.reasoning && showReasoningChain && (
                      <div className="mt-3 p-3 bg-gray-900/50 rounded border border-gray-700">
                        <div className="text-sm text-gray-400 mb-2">Reasoning Chain:</div>
                        <ul className="space-y-1">
                          {message.reasoning.map((step, index) => (
                            <li key={index} className="text-xs text-gray-500">
                              {index + 1}. {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 order-1">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3 justify-start"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                {modelConfigs[selectedModel]?.icon}
              </div>
              <div className="bg-gray-800/90 border border-gray-600 p-4 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="cyber-loading"></div>
                  <span className="text-sm text-gray-400">
                    {modelConfigs[selectedModel]?.name} is thinking...
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              placeholder="Enter your message... (Shift+Enter for new line)"
              disabled={isLoading}
              className="cyber-input pr-20 min-h-[3rem] py-3"
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              <button
                onClick={() => setShowReasoningChain(!showReasoningChain)}
                className={`p-1 rounded transition-colors ${
                  showReasoningChain ? 'text-orange-400' : 'text-gray-400 hover:text-orange-400'
                }`}
                title="Toggle reasoning chain"
              >
                <Brain className="w-4 h-4" />
              </button>
            </div>
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="cyber-button px-6 py-3 min-h-[3rem]"
          >
            <Send className="w-4 h-4 mr-2" />
            Send
          </Button>
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>
            Using {modelConfigs[selectedModel]?.name} • {modelConfigs[selectedModel]?.performance?.contextWindow}
          </span>
          <span>
            Press Shift+Enter for new line, Enter to send
          </span>
        </div>
      </div>
    </div>
  )
}
