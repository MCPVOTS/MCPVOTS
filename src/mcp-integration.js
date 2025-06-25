// MCPVots MCP Integration Module
class MCPIntegration {
    constructor() {
        this.servers = new Map();
        this.connections = new Map();
        this.messageQueue = [];
        this.isInitialized = false;
        this.eventHandlers = new Map();
        
        this.init();
    }

    async init() {
        console.log("Initializing MCP Integration system...");
        
        try {
            await this.discoverServers();
            await this.establishConnections();
            this.startHeartbeat();
            this.setupEventHandlers();
            
            this.isInitialized = true;
            this.emit('initialized', { timestamp: Date.now() });
            console.log("MCP Integration system initialized successfully");
        } catch (error) {
            console.error("Failed to initialize MCP Integration:", error);
            this.emit('error', { error: error.message });
        }
    }

    async discoverServers() {
        // Simulate MCP server discovery from configuration
        const serverConfigs = [
            {
                id: 'github-mcp',
                name: 'GitHub MCP Server',
                url: 'ws://localhost:3001',
                capabilities: ['repositories', 'issues', 'pull-requests'],
                status: 'discovering'
            },
            {
                id: 'memory-mcp',
                name: 'Memory MCP Server',
                url: 'ws://localhost:3002',
                capabilities: ['knowledge-graph', 'storage', 'retrieval'],
                status: 'discovering'
            },
            {
                id: 'huggingface-mcp',
                name: 'HuggingFace MCP Server',
                url: 'ws://localhost:3003',
                capabilities: ['models', 'inference', 'datasets'],
                status: 'discovering'
            },
            {
                id: 'supermemory-mcp',
                name: 'SuperMemory MCP Server',
                url: 'ws://localhost:3004',
                capabilities: ['memory', 'search', 'indexing'],
                status: 'discovering'
            },
            {
                id: 'solana-mcp',
                name: 'Solana MCP Server',
                url: 'ws://localhost:3005',
                capabilities: ['blockchain', 'transactions', 'wallets'],
                status: 'discovering'
            },
            {
                id: 'browser-mcp',
                name: 'Browser Tools MCP Server',
                url: 'ws://localhost:3006',
                capabilities: ['automation', 'scraping', 'interaction'],
                status: 'discovering'
            }
        ];

        for (const config of serverConfigs) {
            this.servers.set(config.id, {
                ...config,
                lastPing: null,
                connectionAttempts: 0,
                isConnected: false
            });
        }

        console.log(`Discovered ${serverConfigs.length} MCP servers`);
        this.emit('serversDiscovered', { count: serverConfigs.length });
    }

    async establishConnections() {
        const connectionPromises = Array.from(this.servers.values()).map(server => 
            this.connectToServer(server)
        );

        const results = await Promise.allSettled(connectionPromises);
        
        let successCount = 0;
        results.forEach((result, index) => {
            const server = Array.from(this.servers.values())[index];
            if (result.status === 'fulfilled') {
                successCount++;
                server.status = 'connected';
                server.isConnected = true;
            } else {
                server.status = 'failed';
                server.isConnected = false;
                console.warn(`Failed to connect to ${server.name}:`, result.reason);
            }
        });

        console.log(`Successfully connected to ${successCount}/${this.servers.size} MCP servers`);
        this.emit('connectionsEstablished', { 
            total: this.servers.size, 
            successful: successCount 
        });
    }

    async connectToServer(server) {
        return new Promise((resolve, reject) => {
            try {
                // Simulate WebSocket connection
                console.log(`Attempting to connect to ${server.name} at ${server.url}`);
                
                // Simulate connection delay
                setTimeout(() => {
                    // Simulate success/failure based on server ID
                    const shouldSucceed = this.shouldConnectionSucceed(server.id);
                    
                    if (shouldSucceed) {
                        const mockConnection = this.createMockConnection(server);
                        this.connections.set(server.id, mockConnection);
                        server.lastPing = Date.now();
                        server.connectionAttempts++;
                        
                        console.log(`Successfully connected to ${server.name}`);
                        resolve(mockConnection);
                    } else {
                        server.connectionAttempts++;
                        reject(new Error(`Connection timeout to ${server.name}`));
                    }
                }, Math.random() * 1000 + 500); // 500-1500ms delay
                
            } catch (error) {
                server.connectionAttempts++;
                reject(error);
            }
        });
    }

    shouldConnectionSucceed(serverId) {
        // Simulate different connection success rates for different servers
        const successRates = {
            'github-mcp': 0.9,
            'memory-mcp': 0.95,
            'huggingface-mcp': 0.7,
            'supermemory-mcp': 0.6,
            'solana-mcp': 0.85,
            'browser-mcp': 0.9
        };
        
        return Math.random() < (successRates[serverId] || 0.8);
    }

    createMockConnection(server) {
        return {
            id: server.id,
            server: server,
            readyState: 1, // WebSocket.OPEN
            send: (message) => {
                console.log(`Sending message to ${server.name}:`, message);
                this.handleMessage(server.id, message);
            },
            close: () => {
                console.log(`Closing connection to ${server.name}`);
                this.handleDisconnection(server.id);
            },
            addEventListener: (event, handler) => {
                // Mock event listener
                console.log(`Added event listener for ${event} on ${server.name}`);
            }
        };
    }

    async sendMessage(serverId, message) {
        const connection = this.connections.get(serverId);
        const server = this.servers.get(serverId);
        
        if (!connection || !server || !server.isConnected) {
            throw new Error(`No active connection to server: ${serverId}`);
        }

        try {
            const messageWithId = {
                id: this.generateMessageId(),
                timestamp: Date.now(),
                ...message
            };

            connection.send(JSON.stringify(messageWithId));
            
            this.emit('messageSent', { 
                serverId, 
                messageId: messageWithId.id,
                message: messageWithId 
            });
            
            return messageWithId.id;
        } catch (error) {
            console.error(`Failed to send message to ${serverId}:`, error);
            this.emit('messageError', { serverId, error: error.message });
            throw error;
        }
    }

    handleMessage(serverId, message) {
        try {
            const parsedMessage = typeof message === 'string' ? JSON.parse(message) : message;
            
            console.log(`Received message from ${serverId}:`, parsedMessage);
            
            this.emit('messageReceived', {
                serverId,
                message: parsedMessage,
                timestamp: Date.now()
            });
            
            // Update server last ping
            const server = this.servers.get(serverId);
            if (server) {
                server.lastPing = Date.now();
            }
            
        } catch (error) {
            console.error(`Failed to handle message from ${serverId}:`, error);
            this.emit('messageError', { serverId, error: error.message });
        }
    }

    handleDisconnection(serverId) {
        const server = this.servers.get(serverId);
        if (server) {
            server.isConnected = false;
            server.status = 'disconnected';
        }
        
        this.connections.delete(serverId);
        
        console.log(`Server ${serverId} disconnected`);
        this.emit('serverDisconnected', { serverId, timestamp: Date.now() });
        
        // Attempt to reconnect after a delay
        setTimeout(() => {
            this.reconnectToServer(serverId);
        }, 5000);
    }

    async reconnectToServer(serverId) {
        const server = this.servers.get(serverId);
        if (!server) return;
        
        console.log(`Attempting to reconnect to ${server.name}`);
        
        try {
            await this.connectToServer(server);
            console.log(`Successfully reconnected to ${server.name}`);
            this.emit('serverReconnected', { serverId, timestamp: Date.now() });
        } catch (error) {
            console.error(`Failed to reconnect to ${server.name}:`, error);
            
            // Schedule another reconnection attempt
            setTimeout(() => {
                this.reconnectToServer(serverId);
            }, 10000);
        }
    }

    startHeartbeat() {
        setInterval(() => {
            this.sendHeartbeats();
        }, 30000); // Every 30 seconds
    }

    async sendHeartbeats() {
        const heartbeatPromises = Array.from(this.connections.keys()).map(serverId => {
            return this.sendMessage(serverId, {
                type: 'heartbeat',
                timestamp: Date.now()
            }).catch(error => {
                console.warn(`Heartbeat failed for ${serverId}:`, error);
            });
        });

        await Promise.allSettled(heartbeatPromises);
    }

    // Event system
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, new Set());
        }
        this.eventHandlers.get(event).add(handler);
    }

    off(event, handler) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.delete(handler);
        }
    }

    emit(event, data) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    setupEventHandlers() {
        // Set up default event handlers
        this.on('serverDisconnected', (data) => {
            console.warn(`Server ${data.serverId} disconnected at ${new Date(data.timestamp)}`);
        });

        this.on('messageReceived', (data) => {
            // Handle different types of messages
            this.processIncomingMessage(data);
        });
    }

    processIncomingMessage(data) {
        const { message, serverId } = data;
        
        switch (message.type) {
            case 'heartbeat':
                // Heartbeat response received
                break;
            case 'capability_update':
                this.updateServerCapabilities(serverId, message.capabilities);
                break;
            case 'error':
                console.error(`Server ${serverId} reported error:`, message.error);
                break;
            default:
                // Forward to application handlers
                this.emit('applicationMessage', data);
        }
    }

    updateServerCapabilities(serverId, capabilities) {
        const server = this.servers.get(serverId);
        if (server) {
            server.capabilities = capabilities;
            this.emit('capabilitiesUpdated', { serverId, capabilities });
        }
    }

    // Utility methods
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getServerStatus(serverId) {
        const server = this.servers.get(serverId);
        return server ? {
            id: server.id,
            name: server.name,
            status: server.status,
            isConnected: server.isConnected,
            lastPing: server.lastPing,
            capabilities: server.capabilities,
            connectionAttempts: server.connectionAttempts
        } : null;
    }

    getAllServersStatus() {
        return Array.from(this.servers.values()).map(server => 
            this.getServerStatus(server.id)
        );
    }

    getConnectionCount() {
        return this.connections.size;
    }

    isServerConnected(serverId) {
        const server = this.servers.get(serverId);
        return server ? server.isConnected : false;
    }

    // Public API methods for external use
    async callServerMethod(serverId, method, params = {}) {
        return await this.sendMessage(serverId, {
            type: 'method_call',
            method: method,
            params: params
        });
    }

    async queryServer(serverId, query) {
        return await this.sendMessage(serverId, {
            type: 'query',
            query: query
        });
    }

    disconnectFromServer(serverId) {
        const connection = this.connections.get(serverId);
        if (connection) {
            connection.close();
        }
    }

    disconnectAll() {
        Array.from(this.connections.values()).forEach(connection => {
            connection.close();
        });
    }
}

// Initialize MCP Integration when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mcpIntegration = new MCPIntegration();
    
    // Bind to global app if available
    if (window.mcpVotsApp) {
        window.mcpIntegration.on('serversDiscovered', (data) => {
            window.mcpVotsApp.log('INFO', `Discovered ${data.count} MCP servers`);
        });
        
        window.mcpIntegration.on('connectionsEstablished', (data) => {
            window.mcpVotsApp.log('SUCCESS', `Connected to ${data.successful}/${data.total} MCP servers`);
        });
        
        window.mcpIntegration.on('serverDisconnected', (data) => {
            window.mcpVotsApp.log('WARNING', `Server ${data.serverId} disconnected`);
        });
        
        window.mcpIntegration.on('serverReconnected', (data) => {
            window.mcpVotsApp.log('SUCCESS', `Server ${data.serverId} reconnected`);
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MCPIntegration;
}
