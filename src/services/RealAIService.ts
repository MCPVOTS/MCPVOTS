/**
 * Real AI Service API Client
 * Connects to actual backend services running on the system
 */

interface ChatResponse {
  content: string
  tokens: number
  executionTime: number
  reasoning?: string[]
  model: string
  status: 'success' | 'error'
  error?: string
}

interface ModelStatus {
  name: string
  status: 'online' | 'offline' | 'busy'
  port: number
  latency: number
}

class RealAIService {
  private baseUrl = 'http://localhost'
  private services = {
    'gemini-2.5': { port: 8025, endpoint: '/chat' },
    'deepseek-r1': { port: 8095, endpoint: '/generate' },
    'coordinator': { port: 8095, endpoint: '/health' }
  }

  /**
   * Send message to Gemini CLI server
   */
  async sendToGemini(message: string): Promise<ChatResponse> {
    const startTime = Date.now()
    
    try {
      // Connect to Gemini CLI MCP server via WebSocket
      const ws = new WebSocket('ws://localhost:8025')
      
      return new Promise((resolve, reject) => {
        ws.onopen = () => {
          // Send MCP request to Gemini
          const request = {
            jsonrpc: '2.0',
            id: Date.now(),
            method: 'gemini/chat',
            params: {
              message: message,
              model: 'gemini-2.5-flash'
            }
          }
          ws.send(JSON.stringify(request))
        }

        ws.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data)
            const executionTime = (Date.now() - startTime) / 1000

            if (response.result) {
              resolve({
                content: response.result.response || 'No response from Gemini',
                tokens: response.result.tokens || 0,
                executionTime,
                model: 'gemini-2.5',
                status: 'success'
              })
            } else {
              resolve({
                content: 'Error: ' + (response.error?.message || 'Unknown error'),
                tokens: 0,
                executionTime,
                model: 'gemini-2.5',
                status: 'error',
                error: response.error?.message
              })
            }
            ws.close()
          } catch (error) {
            reject(error)
          }
        }

        ws.onerror = (_error) => {
          reject(new Error('WebSocket connection failed'))
        }

        ws.onclose = () => {
          // Connection closed
        }

        // Timeout after 30 seconds
        setTimeout(() => {
          ws.close()
          reject(new Error('Request timeout'))
        }, 30000)
      })
    } catch (error) {
      return {
        content: `Error connecting to Gemini: ${error}`,
        tokens: 0,
        executionTime: (Date.now() - startTime) / 1000,
        model: 'gemini-2.5',
        status: 'error',
        error: String(error)
      }
    }
  }

  /**
   * Send message to DeepSeek R1 via Next.js API proxy
   */
  async sendToDeepSeek(message: string): Promise<ChatResponse> {
    const startTime = Date.now()
    
    try {
      console.log('🔄 Using Next.js API proxy for DeepSeek')
      console.log('📤 Sending message:', message)
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          model: 'deepseek-r1'
        })
      })

      console.log('📥 Response status:', response.status)
      console.log('📥 Response ok:', response.ok)

      const data = await response.json()
      console.log('📄 Response data:', data)
      const executionTime = (Date.now() - startTime) / 1000

      if (response.ok && data.response) {
        return {
          content: data.response,
          tokens: data.tokens || 0,
          executionTime,
          reasoning: data.reasoning || [],
          model: 'deepseek-r1',
          status: 'success'
        }
      } else {
        return {
          content: `Error: ${data.error || 'Unknown error'}`,
          tokens: 0,
          executionTime,
          model: 'deepseek-r1',
          status: 'error',
          error: data.error
        }
      }
    } catch (error) {
      console.error('❌ DeepSeek connection error:', error)
      console.error('❌ Error type:', typeof error)
      console.error('❌ Error details:', error instanceof Error ? error.message : error)
      
      return {
        content: `Error connecting to DeepSeek: ${error instanceof Error ? error.message : String(error)}\n\nThis could be due to:\n- Backend service not running\n- CORS policy blocking the request\n- Network connectivity issues\n\nPlease check the browser console for more details.`,
        tokens: 0,
        executionTime: (Date.now() - startTime) / 1000,
        model: 'deepseek-r1',
        status: 'error',
        error: String(error)
      }
    }
  }

  /**
   * Check service status
   */
  async checkServiceStatus(): Promise<ModelStatus[]> {
    const statusChecks = await Promise.allSettled([
      this.pingService('gemini-2.5', 8015),
      this.pingService('deepseek-r1', 8013),
      this.pingService('coordinator', 8091)
    ])

    return statusChecks.map((result, index) => {
      const serviceName = Object.keys(this.services)[index]
      const port = Object.values(this.services)[index].port
      
      if (result.status === 'fulfilled') {
        return {
          name: serviceName,
          status: 'online' as const,
          port,
          latency: result.value
        }
      } else {
        return {
          name: serviceName,
          status: 'offline' as const,
          port,
          latency: -1
        }
      }
    })
  }

  private async pingService(name: string, port: number): Promise<number> {
    const startTime = Date.now()
    
    try {
      if (name === 'gemini-2.5') {
        // Test WebSocket connection
        const ws = new WebSocket(`ws://localhost:${port}`)
        return new Promise((resolve, reject) => {
          ws.onopen = () => {
            const latency = Date.now() - startTime
            ws.close()
            resolve(latency)
          }
          ws.onerror = () => reject(new Error('Connection failed'))
          setTimeout(() => reject(new Error('Timeout')), 5000)
        })
      } else {
        // Test HTTP connection
        await fetch(`http://localhost:${port}/health`, {
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        })
        return Date.now() - startTime
      }
    } catch (error) {
      throw error
    }
  }

  /**
   * Main chat method that routes to appropriate service
   */
  async chat(message: string, model: 'deepseek-r1' | 'gemini-2.5'): Promise<ChatResponse> {
    switch (model) {
      case 'gemini-2.5':
        return this.sendToGemini(message)
      case 'deepseek-r1':
        return this.sendToDeepSeek(message)
      default:
        return {
          content: 'Unknown model selected',
          tokens: 0,
          executionTime: 0,
          model: model,
          status: 'error',
          error: 'Unknown model'
        }
    }
  }
}

export const realAIService = new RealAIService()
export default RealAIService
