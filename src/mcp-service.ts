/**
 * Advanced MCP Integration Service
 * Comprehensive Model Context Protocol integration with real-time capabilities
 */

export interface MCPMessage {
  jsonrpc: "2.0";
  method?: string;
  params?: any;
  id?: number | string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export interface MCPCapabilities {
  sampling?: boolean;
  logging?: boolean;
  prompts?: boolean;
  resources?: boolean;
  tools?: boolean;
  roots?: boolean;
}

export interface MCPServerInfo {
  name: string;
  version: string;
  capabilities: MCPCapabilities;
}

export interface MCPConnection {
  id: string;
  server: string;
  websocket: WebSocket | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastActivity: number;
  messageQueue: MCPMessage[];
  retryCount: number;
  maxRetries: number;
}

export class MCPIntegrationService {
  private connections: Map<string, MCPConnection> = new Map();
  private messageHandlers: Map<string, Function[]> = new Map();
  private globalHandlers: Function[] = [];
  private heartbeatInterval: number | null = null;
  private config: any;

  constructor(config: any) {
    this.config = config;
    this.initializeService();
  }

  private initializeService(): void {
    console.log('Initializing MCP Integration Service...');
    
    // Start heartbeat if configured
    if (this.config.advanced?.heartbeatInterval > 0) {
      this.startHeartbeat();
    }

    // Setup global error handler
    this.onGlobalMessage('error', (error: any) => {
      console.error('MCP Global Error:', error);
    });
  }

  /**
   * Initialize the MCP service
   */
  public async initialize(): Promise<void> {
    console.log('Initializing MCP Integration Service...');
    // Service is already initialized in constructor
    return Promise.resolve();
  }

  /**
   * Connect to MCP server
   */
  public async connect(serverConfig: any): Promise<boolean> {
    const connectionId = `${serverConfig.name}_${Date.now()}`;
    
    try {
      console.log(`Connecting to MCP server: ${serverConfig.name}`);
      
      const connection: MCPConnection = {
        id: connectionId,
        server: serverConfig.name,
        websocket: null,
        status: 'connecting',
        lastActivity: Date.now(),
        messageQueue: [],
        retryCount: 0,
        maxRetries: this.config.advanced?.maxReconnectAttempts || 5
      };

      this.connections.set(connectionId, connection);

      // Create WebSocket connection
      const ws = new WebSocket(serverConfig.url);
      connection.websocket = ws;

      return new Promise((resolve, reject) => {
        ws.onopen = () => {
          console.log(`Connected to ${serverConfig.name}`);
          connection.status = 'connected';
          connection.lastActivity = Date.now();
          
          // Send initialization
          this.sendInitialize(connection, serverConfig);
          
          this.emit('connection-established', { 
            connectionId, 
            server: serverConfig.name 
          });
          
          resolve(true);
        };

        ws.onmessage = (event) => {
          this.handleMessage(connection, event.data);
        };

        ws.onclose = (event) => {
          console.log(`Disconnected from ${serverConfig.name}:`, event.code, event.reason);
          connection.status = 'disconnected';
          
          this.emit('connection-closed', { 
            connectionId, 
            server: serverConfig.name,
            code: event.code,
            reason: event.reason
          });

          // Auto-reconnect if configured
          if (this.config.advanced?.autoReconnect && serverConfig.enabled) {
            this.scheduleReconnect(connection, serverConfig);
          }
        };

        ws.onerror = (error) => {
          console.error(`WebSocket error for ${serverConfig.name}:`, error);
          connection.status = 'error';
          
          this.emit('connection-error', { 
            connectionId, 
            server: serverConfig.name,
            error 
          });
          
          reject(error);
        };

        // Timeout for connection
        setTimeout(() => {
          if (connection.status === 'connecting') {
            ws.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);
      });

    } catch (error) {
      console.error(`Failed to connect to ${serverConfig.name}:`, error);
      this.connections.delete(connectionId);
      return false;
    }
  }

  /**
   * Send MCP initialization message
   */
  private sendInitialize(connection: MCPConnection, _serverConfig: MCPServerConfig): void {
    const initMessage: MCPMessage = {
      jsonrpc: "2.0",
      method: "initialize",
      params: {
        protocolVersion: "1.0",
        capabilities: {
          sampling: true,
          logging: true,
          prompts: true,
          resources: true,
          tools: true,
          roots: true
        },
        clientInfo: {
          name: "MCPVots",
          version: "1.0.0"
        }
      },
      id: Date.now()
    };

    this.sendMessage(connection, initMessage);
  }

  /**
   * Handle incoming MCP message
   */
  private handleMessage(connection: MCPConnection, data: string): void {
    try {
      const message: MCPMessage = JSON.parse(data);
      connection.lastActivity = Date.now();

      console.log(`Received from ${connection.server}:`, message.method || 'response');

      // Handle specific message types
      if (message.method === 'initialized') {
        this.handleInitialized(connection, message);
      } else if (message.method === 'notification') {
        this.handleNotification(connection, message);
      } else if (message.method === 'request') {
        this.handleRequest(connection, message);
      } else if (message.result !== undefined) {
        this.handleResponse(connection, message);
      } else if (message.error) {
        this.handleError(connection, message);
      }

      // Emit to registered handlers
      this.emitMessage(message.method || 'response', {
        connection: connection.id,
        server: connection.server,
        message
      });

      // Global handlers
      this.globalHandlers.forEach(handler => {
        try {
          handler({ connection: connection.id, server: connection.server, message });
        } catch (error) {
          console.error('Global handler error:', error);
        }
      });

    } catch (error) {
      console.error(`Failed to parse message from ${connection.server}:`, error);
      this.emit('parse-error', { connection: connection.id, server: connection.server, error });
    }
  }

  /**
   * Handle initialization response
   */
  private handleInitialized(connection: MCPConnection, message: MCPMessage): void {
    console.log(`${connection.server} initialized successfully`);
    
    // Process any queued messages
    this.processMessageQueue(connection);
    
    this.emit('server-initialized', {
      connection: connection.id,
      server: connection.server,
      capabilities: message.result?.capabilities
    });
  }

  /**
   * Handle notifications
   */
  private handleNotification(connection: MCPConnection, message: MCPMessage): void {
    console.log(`Notification from ${connection.server}:`, message.params);
    
    this.emit('notification', {
      connection: connection.id,
      server: connection.server,
      notification: message.params
    });
  }

  /**
   * Handle requests (server to client)
   */
  private handleRequest(connection: MCPConnection, message: MCPMessage): void {
    console.log(`Request from ${connection.server}:`, message.method, message.params);
    
    // Send acknowledgment or response as needed
    const response: MCPMessage = {
      jsonrpc: "2.0",
      result: { status: "acknowledged" },
      id: message.id
    };

    this.sendMessage(connection, response);

    this.emit('request', {
      connection: connection.id,
      server: connection.server,
      request: message
    });
  }

  /**
   * Handle responses
   */
  private handleResponse(connection: MCPConnection, message: MCPMessage): void {
    this.emit('response', {
      connection: connection.id,
      server: connection.server,
      response: message
    });
  }

  /**
   * Handle errors
   */
  private handleError(connection: MCPConnection, message: MCPMessage): void {
    console.error(`Error from ${connection.server}:`, message.error);
    
    this.emit('server-error', {
      connection: connection.id,
      server: connection.server,
      error: message.error
    });
  }

  /**
   * Send message to MCP server
   */
  public sendMessage(connection: MCPConnection, message: MCPMessage): boolean {
    try {
      if (!connection.websocket || connection.websocket.readyState !== WebSocket.OPEN) {
        // Queue message if not connected
        connection.messageQueue.push(message);
        console.log(`Queued message for ${connection.server}`);
        return false;
      }

      connection.websocket.send(JSON.stringify(message));
      connection.lastActivity = Date.now();
      
      this.emit('message-sent', {
        connection: connection.id,
        server: connection.server,
        message
      });

      return true;
    } catch (error) {
      console.error(`Failed to send message to ${connection.server}:`, error);
      return false;
    }
  }

  /**
   * Send message by server name
   */
  public sendToServer(serverName: string, message: MCPMessage): boolean {
    const connection = this.findConnectionByServer(serverName);
    if (!connection) {
      console.error(`No connection found for server: ${serverName}`);
      return false;
    }

    return this.sendMessage(connection, message);
  }

  /**
   * Process queued messages
   */
  private processMessageQueue(connection: MCPConnection): void {
    while (connection.messageQueue.length > 0) {
      const message = connection.messageQueue.shift();
      if (message) {
        this.sendMessage(connection, message);
      }
    }
  }

  /**
   * Find connection by server name
   */
  private findConnectionByServer(serverName: string): MCPConnection | null {
    for (const connection of this.connections.values()) {
      if (connection.server === serverName) {
        return connection;
      }
    }
    return null;
  }

  /**
   * Schedule reconnection
   */
  private scheduleReconnect(connection: MCPConnection, serverConfig: any): void {
    if (connection.retryCount >= connection.maxRetries) {
      console.log(`Max retries reached for ${connection.server}`);
      this.emit('max-retries-reached', { 
        connection: connection.id, 
        server: connection.server 
      });
      return;
    }

    connection.retryCount++;
    const delay = Math.min(1000 * Math.pow(2, connection.retryCount), 30000); // Exponential backoff

    console.log(`Scheduling reconnect for ${connection.server} in ${delay}ms (attempt ${connection.retryCount})`);

    setTimeout(() => {
      if (connection.status !== 'connected') {
        this.connect(serverConfig);
      }
    }, delay);
  }

  /**
   * Start heartbeat for all connections
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      this.connections.forEach((connection) => {
        if (connection.status === 'connected') {
          const pingMessage: MCPMessage = {
            jsonrpc: "2.0",
            method: "ping",
            params: { timestamp: Date.now() },
            id: Date.now()
          };
          this.sendMessage(connection, pingMessage);
        }
      });
    }, this.config.advanced.heartbeatInterval);
  }

  /**
   * Event handling
   */
  public on(event: string, handler: Function): void {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, []);
    }
    this.messageHandlers.get(event)!.push(handler);
  }

  public onGlobalMessage(_event: string, handler: Function): void {
    this.globalHandlers.push(handler);
  }

  private emit(event: string, data: any): void {
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Handler error for event ${event}:`, error);
        }
      });
    }
  }

  private emitMessage(method: string, data: any): void {
    this.emit(method, data);
    this.emit('message', data);
  }

  /**
   * Disconnect from server
   */
  public disconnect(serverName: string): boolean {
    const connection = this.findConnectionByServer(serverName);
    if (!connection) {
      return false;
    }

    if (connection.websocket) {
      connection.websocket.close();
    }

    this.connections.delete(connection.id);
    console.log(`Disconnected from ${serverName}`);
    
    this.emit('disconnected', { server: serverName });
    return true;
  }

  /**
   * Disconnect from all servers
   */
  public disconnectAll(): void {
    this.connections.forEach((connection) => {
      if (connection.websocket) {
        connection.websocket.close();
      }
    });
    
    this.connections.clear();
    console.log('Disconnected from all servers');
    
    this.emit('all-disconnected', {});
  }

  /**
   * Get connection status
   */
  public getConnectionStatus(): any {
    const status: {
      totalConnections: number;
      activeConnections: number;
      servers: Array<{
        id: string;
        server: string;
        status: string;
        lastActivity: number;
        queuedMessages: number;
        retryCount: number;
      }>;
    } = {
      totalConnections: this.connections.size,
      activeConnections: 0,
      servers: []
    };

    this.connections.forEach((connection) => {
      if (connection.status === 'connected') {
        status.activeConnections++;
      }

      status.servers.push({
        id: connection.id,
        server: connection.server,
        status: connection.status,
        lastActivity: connection.lastActivity,
        queuedMessages: connection.messageQueue.length,
        retryCount: connection.retryCount
      });
    });

    return status;
  }

  /**
   * Advanced MCP operations
   */
  public async callTool(serverName: string, toolName: string, parameters: any): Promise<any> {
    const message: MCPMessage = {
      jsonrpc: "2.0",
      method: "tools/call",
      params: {
        name: toolName,
        arguments: parameters
      },
      id: Date.now()
    };

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Tool call timeout'));
      }, 30000);

      const responseHandler = (data: any) => {
        if (data.message.id === message.id) {
          clearTimeout(timeout);
          this.off('response', responseHandler);
          
          if (data.message.error) {
            reject(new Error(data.message.error.message));
          } else {
            resolve(data.message.result);
          }
        }
      };

      this.on('response', responseHandler);
      
      if (!this.sendToServer(serverName, message)) {
        clearTimeout(timeout);
        this.off('response', responseHandler);
        reject(new Error('Failed to send message'));
      }
    });
  }

  public async getResources(serverName: string): Promise<any> {
    const message: MCPMessage = {
      jsonrpc: "2.0",
      method: "resources/list",
      params: {},
      id: Date.now()
    };

    return this.sendRequestWithResponse(serverName, message);
  }

  public async getPrompts(serverName: string): Promise<any> {
    const message: MCPMessage = {
      jsonrpc: "2.0",
      method: "prompts/list",
      params: {},
      id: Date.now()
    };

    return this.sendRequestWithResponse(serverName, message);
  }

  private async sendRequestWithResponse(serverName: string, message: MCPMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Request timeout'));
      }, 30000);

      const responseHandler = (data: any) => {
        if (data.message.id === message.id) {
          clearTimeout(timeout);
          this.off('response', responseHandler);
          
          if (data.message.error) {
            reject(new Error(data.message.error.message));
          } else {
            resolve(data.message.result);
          }
        }
      };

      this.on('response', responseHandler);
      
      if (!this.sendToServer(serverName, message)) {
        clearTimeout(timeout);
        this.off('response', responseHandler);
        reject(new Error('Failed to send message'));
      }
    });
  }

  private off(event: string, handler: Function): void {
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Cleanup
   */
  public destroy(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    this.disconnectAll();
    this.messageHandlers.clear();
    this.globalHandlers = [];
    
    console.log('MCP Integration Service destroyed');
  }
}

export default MCPIntegrationService;
