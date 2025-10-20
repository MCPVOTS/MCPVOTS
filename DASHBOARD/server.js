/**
 * Mock API Server for Ethermax Dashboard
 * Serves data to the 3D dashboard
 */

const express = require('express');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Serve static files
app.use(express.static('.'));

// API endpoints
app.get('/api/dashboard-data', (req, res) => {
    // Generate realistic mock data
    const data = {
        tokenData: {
            price: 0.0012 + (Math.random() - 0.5) * 0.0002,
            volume: 120000 + Math.random() * 10000,
            liquidity: 500000 + Math.random() * 50000,
            holders: 5200 + Math.floor(Math.random() * 100),
            priceChange24h: (Math.random() - 0.5) * 10, // -5% to +5%
            marketCap: 2500000 + Math.random() * 500000
        },
        swarmData: {
            activeSwarms: Math.floor(Math.random() * 15),
            botAddresses: Math.floor(Math.random() * 200) + 50,
            confidenceScore: Math.floor(Math.random() * 40) + 60,
            lastDetected: Date.now(),
            swarmAddresses: generateMockAddresses(Math.floor(Math.random() * 10) + 5)
        },
        networkData: {
            activeBots: Math.floor(Math.random() * 10) + 1,
            txPerMin: Math.floor(Math.random() * 100) + 20,
            networkLoad: Math.floor(Math.random() * 40) + 40,
            totalValueLocked: 1000000 + Math.random() * 500000
        },
        transactionData: {
            recentTransactions: generateMockTransactions(10),
            totalToday: Math.floor(Math.random() * 5000) + 1000
        }
    };
    
    res.json(data);
});

app.get('/api/historical', (req, res) => {
    const range = req.query.range || '24h';
    const metric = req.query.metric || 'price';
    
    // Generate historical data based on range
    const points = range === '1h' ? 60 : range === '24h' ? 24 : 7; // points for 1h, 24h, or 7d
    const data = [];
    
    let baseValue = metric === 'price' ? 0.0012 : 
                   metric === 'volume' ? 100000 : 
                   metric === 'swarms' ? 5 : 30;
    
    for (let i = points; i >= 0; i--) {
        const variation = (Math.random() - 0.5) * 0.1 * baseValue;
        data.push({
            timestamp: Date.now() - i * (range === '1h' ? 60000 : 3600000), // 1 min or 1 hour intervals
            value: baseValue + variation
        });
        
        // Adjust base value slightly for next point
        baseValue += (Math.random() - 0.5) * 0.01 * baseValue;
    }
    
    res.json(data);
});

app.get('/api/swarms', (req, res) => {
    const swarms = [];
    const count = Math.floor(Math.random() * 10) + 5;
    
    for (let i = 0; i < count; i++) {
        swarms.push({
            id: `swarm_${Date.now()}_${i}`,
            participants: Math.floor(Math.random() * 50) + 10,
            volume: Math.floor(Math.random() * 100000) + 10000,
            confidence: Math.floor(Math.random() * 40) + 60,
            detectedAt: Date.now() - Math.floor(Math.random() * 3600000), // Last hour
            addresses: generateMockAddresses(Math.floor(Math.random() * 20) + 5)
        });
    }
    
    res.json(swarms);
});

app.get('/api/transactions', (req, res) => {
    const transactions = generateMockTransactions(50);
    res.json(transactions);
});

app.get('/api/bots', (req, res) => {
    const botAddresses = generateMockAddresses(50);
    const bots = botAddresses.map(addr => ({
        address: addr,
        type: ['swarm', 'arbitrage', 'sniper', 'whale'][Math.floor(Math.random() * 4)],
        activityScore: Math.floor(Math.random() * 100),
        lastActive: Date.now() - Math.floor(Math.random() * 3600000)
    }));
    
    res.json(bots);
});

function generateMockAddresses(count) {
    const addresses = [];
    for (let i = 0; i < count; i++) {
        addresses.push(`0x${Array.from({length: 40}, () => 
            Math.floor(Math.random() * 16).toString(16)
        ).join('')}`);
    }
    return addresses;
}

function generateMockTransactions(count) {
    const transactions = [];
    for (let i = 0; i < count; i++) {
        transactions.push({
            hash: `0x${Array.from({length: 64}, () => 
                Math.floor(Math.random() * 16).toString(16)
            ).join('')}`,
            from: generateMockAddresses(1)[0],
            to: generateMockAddresses(1)[0],
            value: (Math.random() * 1000).toFixed(4),
            timestamp: Date.now() - Math.floor(Math.random() * 3600000),
            gasPrice: Math.floor(Math.random() * 50) + 10,
            success: Math.random() > 0.1 // 90% success rate
        });
    }
    return transactions;
}

// WebSocket for real-time updates
wss.on('connection', (ws) => {
    console.log('New client connected');
    
    // Send initial data
    ws.send(JSON.stringify({
        type: 'initial_data',
        data: {
            tokenData: {
                price: 0.0012 + (Math.random() - 0.5) * 0.0002,
                volume: 120000 + Math.random() * 10000,
                liquidity: 500000 + Math.random() * 50000,
                holders: 5200 + Math.floor(Math.random() * 100)
            },
            swarmData: {
                activeSwarms: Math.floor(Math.random() * 15),
                botAddresses: Math.floor(Math.random() * 200) + 50,
                confidenceScore: Math.floor(Math.random() * 40) + 60
            },
            networkData: {
                activeBots: Math.floor(Math.random() * 10) + 1,
                txPerMin: Math.floor(Math.random() * 100) + 20,
                networkLoad: Math.floor(Math.random() * 40) + 40
            }
        }
    }));
    
    // Send periodic updates
    const interval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'update',
                data: {
                    tokenData: {
                        price: 0.0012 + (Math.random() - 0.5) * 0.0002,
                        volume: 120000 + Math.random() * 10000,
                        liquidity: 500000 + Math.random() * 50000,
                        holders: 5200 + Math.floor(Math.random() * 100)
                    },
                    swarmData: {
                        activeSwarms: Math.floor(Math.random() * 15),
                        botAddresses: Math.floor(Math.random() * 200) + 50,
                        confidenceScore: Math.floor(Math.random() * 40) + 60
                    },
                    networkData: {
                        activeBots: Math.floor(Math.random() * 10) + 1,
                        txPerMin: Math.floor(Math.random() * 100) + 20,
                        networkLoad: Math.floor(Math.random() * 40) + 40
                    }
                }
            }));
        }
    }, 3000); // Update every 3 seconds
    
    ws.on('close', () => {
        console.log('Client disconnected');
        clearInterval(interval);
    });
    
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            if (data.command === 'subscribe') {
                console.log(`Client subscribed to ${data.data.stream}`);
                // In a real implementation, you would track subscriptions
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
    console.log(`Ethermax Dashboard Server running on http://localhost:${PORT}`);
    console.log(`WebSocket server running on ws://localhost:${PORT}/api/ws`);
});