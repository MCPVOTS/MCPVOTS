// Simple MCP test server for integration testing
const WebSocket = require('ws');

const port = 8080;
const wss = new WebSocket.Server({ port });

console.log(`MCP Test Server running on port ${port}`);

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('Received:', data);
      
      // Echo back with MCP response format
      ws.send(JSON.stringify({
        id: data.id,
        result: {
          status: 'success',
          message: 'Test response from MCP server'
        }
      }));
    } catch (error) {
      console.error('Error processing message:', error);
      ws.send(JSON.stringify({
        error: {
          code: -1,
          message: 'Invalid JSON'
        }
      }));
    }
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down MCP test server...');
  wss.close(() => {
    process.exit(0);
  });
});
