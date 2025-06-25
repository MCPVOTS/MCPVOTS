export interface MCPMetrics {
  totalRequests: number;
  successRate: number;
  averageResponseTime: number;
  activeConnections: number;
  lastUpdated: string;
}

export interface MCPMessage {
  jsonrpc: '2.0';
  method?: string;
  params?: any;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
  id?: string | number;
}

export class MCPClient {
  private ws: WebSocket | null = null;
  private connected = false;
  private messageId = 0;
  private pendingRequests = new Map<string | number, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }>();
  private listeners = new Set<(message: MCPMessage) => void>();
  private metrics: MCPMetrics = {
    totalRequests: 0,
    successRate: 0,
    averageResponseTime: 0,
    activeConnections: 0,
    lastUpdated: new Date().toISOString()
  };

  constructor(private url: string = 'ws://localhost:3001') {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          this.connected = true;
          this.metrics.activeConnections = 1;
          this.metrics.lastUpdated = new Date().toISOString();
          console.log('MCP Client connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: MCPMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse MCP message:', error);
          }
        };

        this.ws.onclose = () => {
          this.connected = false;
          this.metrics.activeConnections = 0;
          this.metrics.lastUpdated = new Date().toISOString();
          console.log('MCP Client disconnected');
        };

        this.ws.onerror = (error) => {
          console.error('MCP WebSocket error:', error);
          reject(new Error('Failed to connect to MCP server'));
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: MCPMessage) {
    // Handle responses to our requests
    if (message.id && this.pendingRequests.has(message.id)) {
      const request = this.pendingRequests.get(message.id)!;
      this.pendingRequests.delete(message.id);

      if (message.error) {
        request.reject(new Error(message.error.message));
      } else {
        request.resolve(message.result);
      }
      return;
    }

    // Notify listeners of incoming messages
    this.listeners.forEach(listener => listener(message));
  }

  async sendRequest(method: string, params?: any): Promise<any> {
    if (!this.connected || !this.ws) {
      throw new Error('MCP Client not connected');
    }

    const id = ++this.messageId;
    const message: MCPMessage = {
      jsonrpc: '2.0',
      method,
      params,
      id
    };

    const startTime = Date.now();
    this.metrics.totalRequests++;

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      
      try {
        this.ws!.send(JSON.stringify(message));
        
        // Timeout after 30 seconds
        setTimeout(() => {
          if (this.pendingRequests.has(id)) {
            this.pendingRequests.delete(id);
            reject(new Error('Request timeout'));
          }
        }, 30000);
        
      } catch (error) {
        this.pendingRequests.delete(id);
        reject(error);
      }
    }).finally(() => {
      const duration = Date.now() - startTime;
      this.updateMetrics(duration);
    });
  }

  private updateMetrics(responseTime: number) {
    // Update average response time
    const totalTime = this.metrics.averageResponseTime * (this.metrics.totalRequests - 1) + responseTime;
    this.metrics.averageResponseTime = Math.round(totalTime / this.metrics.totalRequests);
    
    // Calculate success rate (simplified - assumes successful completion)
    this.metrics.successRate = Math.round((this.metrics.totalRequests / this.metrics.totalRequests) * 100);
    
    this.metrics.lastUpdated = new Date().toISOString();
  }

  async initialize(): Promise<any> {
    return this.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {
        roots: { listChanged: true },
        sampling: {}
      },
      clientInfo: {
        name: 'MCPVots',
        version: '2.0.0'
      }
    });
  }

  async listResources(): Promise<any> {
    return this.sendRequest('resources/list');
  }

  async listTools(): Promise<any> {
    return this.sendRequest('tools/list');
  }

  async callTool(name: string, arguments_: any): Promise<any> {
    return this.sendRequest('tools/call', {
      name,
      arguments: arguments_
    });
  }

  getMetrics(): MCPMetrics {
    return { ...this.metrics };
  }

  addListener(listener: (message: MCPMessage) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
    this.pendingRequests.clear();
    this.listeners.clear();
  }

  isConnected(): boolean {
    return this.connected;
  }
}

export const mcpClient = new MCPClient();
