/**
 * WebSocket Proxy Server for MCPVots
 * Handles WebSocket connections and proxying for real-time features
 */

import WebSocket from 'ws';
import http from 'http';
import url from 'url';

class WebSocketProxy {
    constructor(port = 8080) {
        this.port = port;
        this.clients = new Map();
        this.server = null;
        this.wss = null;
    }

    start() {
        // Create HTTP server for health checks
        this.server = http.createServer((req, res) => {
            const pathname = url.parse(req.url).pathname;
            
            if (pathname === '/health') {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    status: 'healthy',
                    uptime: process.uptime(),
                    connections: this.clients.size,
                    timestamp: new Date().toISOString()
                }));
                return;
            }
            
            res.writeHead(404);
            res.end('Not Found');
        });

        // Create WebSocket server
        this.wss = new WebSocket.Server({ server: this.server });

        this.wss.on('connection', (ws, req) => {
            const clientId = this.generateClientId();
            const clientInfo = {
                id: clientId,
                ws: ws,
                connected: Date.now(),
                ip: req.connection.remoteAddress
            };

            this.clients.set(clientId, clientInfo);
            console.log(`Client connected: ${clientId} from ${clientInfo.ip}`);

            // Send welcome message
            ws.send(JSON.stringify({
                type: 'welcome',
                clientId: clientId,
                timestamp: new Date().toISOString()
            }));

            // Handle messages
            ws.on('message', (message) => {
                try {
                    const data = JSON.parse(message);
                    this.handleMessage(clientId, data);
                } catch (error) {
                    console.error(`Invalid message from ${clientId}:`, error);
                }
            });

            // Handle disconnect
            ws.on('close', () => {
                this.clients.delete(clientId);
                console.log(`Client disconnected: ${clientId}`);
            });

            ws.on('error', (error) => {
                console.error(`WebSocket error for ${clientId}:`, error);
                this.clients.delete(clientId);
            });
        });

        this.server.listen(this.port, () => {
            console.log(`WebSocket Proxy Server running on port ${this.port}`);
            console.log(`Health check available at http://localhost:${this.port}/health`);
        });
    }

    handleMessage(clientId, data) {
        console.log(`Message from ${clientId}:`, data.type);

        switch (data.type) {
            case 'ping':
                this.sendToClient(clientId, { type: 'pong', timestamp: new Date().toISOString() });
                break;
                
            case 'broadcast':
                this.broadcast(data.payload, clientId);
                break;
                
            case 'subscribe':
                this.subscribe(clientId, data.channel);
                break;
                
            case 'unsubscribe':
                this.unsubscribe(clientId, data.channel);
                break;
                
            default:
                console.log(`Unknown message type: ${data.type}`);
        }
    }

    sendToClient(clientId, message) {
        const client = this.clients.get(clientId);
        if (client && client.ws.readyState === WebSocket.OPEN) {
            client.ws.send(JSON.stringify(message));
        }
    }

    broadcast(message, excludeClientId = null) {
        const broadcastMessage = {
            type: 'broadcast',
            payload: message,
            timestamp: new Date().toISOString()
        };

        this.clients.forEach((client, clientId) => {
            if (clientId !== excludeClientId && client.ws.readyState === WebSocket.OPEN) {
                client.ws.send(JSON.stringify(broadcastMessage));
            }
        });
    }

    subscribe(clientId, channel) {
        const client = this.clients.get(clientId);
        if (client) {
            if (!client.subscriptions) {
                client.subscriptions = new Set();
            }
            client.subscriptions.add(channel);
            console.log(`Client ${clientId} subscribed to ${channel}`);
        }
    }

    unsubscribe(clientId, channel) {
        const client = this.clients.get(clientId);
        if (client && client.subscriptions) {
            client.subscriptions.delete(channel);
            console.log(`Client ${clientId} unsubscribed from ${channel}`);
        }
    }

    generateClientId() {
        return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    stop() {
        if (this.wss) {
            this.wss.close();
        }
        if (this.server) {
            this.server.close();
        }
        console.log('WebSocket Proxy Server stopped');
    }
}

// Start the server if this file is run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const proxy = new WebSocketProxy();
    
    process.on('SIGINT', () => {
        console.log('\nShutting down WebSocket Proxy Server...');
        proxy.stop();
        process.exit(0);
    });
    
    proxy.start();
}

export default WebSocketProxy;
