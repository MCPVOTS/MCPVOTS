/**
 * Enhanced Data Connector for Ethermax Dashboard
 * Connects the 3D dashboard to backend data sources with real-time ETH price streaming
 */

class EnhancedDataConnector {
    constructor() {
        this.ws = null;
        this.dataEndpoint = '/api/realtime';
        this.ethPriceEndpoint = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true';
        this.isConnected = false;
        this.reconnectInterval = 5000; // 5 seconds
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;

        // ETH price data
        this.ethPrice = 0;
        this.ethPriceChange = 0;

        // Ethermax balance data
        this.ethermaxData = {
            maxxBalance: 0,
            ethBalance: 0,
            totalValue: 0
        };

        // Callbacks for different data types
        this.onTokenDataUpdate = null;
        this.onSwarmDataUpdate = null;
        this.onNetworkDataUpdate = null;
        this.onTransactionUpdate = null;
        this.onEthPriceUpdate = null;
        this.onEthermaxUpdate = null;

        // Initialize
        this.init();
    }

    init() {
        // Start ETH price polling
        this.startEthPricePolling();

        // Start Ethermax balance simulation
        this.startEthermaxSimulation();
    }

    /**
     * Initialize connection to data source
     */
    async connect() {
        try {
            // Try WebSocket first
            await this.connectWebSocket();
        } catch (error) {
            console.warn('WebSocket connection failed, falling back to REST API:', error);
            // Fallback to REST polling
            this.startPolling();
        }
    }

    /**
     * Connect via WebSocket for real-time updates
     */
    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            const wsUrl = `ws://${window.location.host}/api/ws`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('Connected to data stream');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.setupWebSocketHandlers();
                resolve();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                reject(error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket connection closed');
                this.isConnected = false;

                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                    setTimeout(() => {
                        this.connectWebSocket().catch(console.error);
                    }, this.reconnectInterval);
                }
            };
        });
    }

    /**
     * Set up WebSocket message handlers
     */
    setupWebSocketHandlers() {
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleDataUpdate(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
    }

    /**
     * Start polling REST API as fallback
     */
    startPolling() {
        setInterval(async () => {
            try {
                await this.fetchData();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }, 5000); // Poll every 5 seconds
    }

    /**
     * Fetch data from REST API
     */
    async fetchData() {
        const response = await fetch(`${window.location.origin}/api/dashboard-data`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.handleDataUpdate(data);
    }

    /**
     * Start ETH price polling from CoinGecko
     */
    startEthPricePolling() {
        // Initial fetch
        this.fetchEthPrice();

        // Update every 30 seconds
        setInterval(() => {
            this.fetchEthPrice();
        }, 30000);
    }

    /**
     * Fetch ETH price from CoinGecko API
     */
    async fetchEthPrice() {
        try {
            const response = await fetch(this.ethPriceEndpoint);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const newPrice = data.ethereum.usd;
            const priceChange = data.ethereum.usd_24h_change;

            // Update price with smoothing
            if (this.ethPrice > 0) {
                this.ethPrice = this.ethPrice * 0.9 + newPrice * 0.1;
            } else {
                this.ethPrice = newPrice;
            }

            this.ethPriceChange = priceChange;

            // Trigger callback
            if (this.onEthPriceUpdate) {
                this.onEthPriceUpdate({
                    price: this.ethPrice,
                    change: this.ethPriceChange
                });
            }

            // Update Ethermax total value if we have balance data
            if (this.ethermaxData.ethBalance > 0) {
                this.ethermaxData.totalValue = this.ethermaxData.ethBalance * this.ethPrice +
                                             (this.ethermaxData.maxxBalance * 0.0012); // Using current MAXX price
                if (this.onEthermaxUpdate) {
                    this.onEthermaxUpdate(this.ethermaxData);
                }
            }

        } catch (error) {
            console.error('Error fetching ETH price:', error);
        }
    }

    /**
     * Start Ethermax balance simulation
     */
    startEthermaxSimulation() {
        // Simulate changing balances
        setInterval(() => {
            // Simulate small balance changes
            this.ethermaxData.maxxBalance += (Math.random() - 0.5) * 100;
            this.ethermaxData.ethBalance += (Math.random() - 0.5) * 0.01;

            // Ensure positive balances
            this.ethermaxData.maxxBalance = Math.max(0, this.ethermaxData.maxxBalance);
            this.ethermaxData.ethBalance = Math.max(0, this.ethermaxData.ethBalance);

            // Update total value
            this.ethermaxData.totalValue = this.ethermaxData.ethBalance * this.ethPrice +
                                         (this.ethermaxData.maxxBalance * 0.0012);

            // Trigger callback
            if (this.onEthermaxUpdate) {
                this.onEthermaxUpdate(this.ethermaxData);
            }
        }, 5000); // Update every 5 seconds
    }

    /**
     * Handle incoming data updates
     */
    handleDataUpdate(data) {
        // Process different data types
        if (data.tokenData) {
            this.onTokenDataUpdate && this.onTokenDataUpdate(data.tokenData);
        }

        if (data.swarmData) {
            this.onSwarmDataUpdate && this.onSwarmDataUpdate(data.swarmData);
        }

        if (data.networkData) {
            this.onNetworkDataUpdate && this.onNetworkDataUpdate(data.networkData);
        }

        if (data.transactionData) {
            this.onTransactionUpdate && this.onTransactionUpdate(data.transactionData);
        }
    }

    /**
     * Get historical data for charting
     */
    async getHistoricalData(range = '24h', metric = 'price') {
        const response = await fetch(`${window.location.origin}/api/historical?range=${range}&metric=${metric}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Get swarm detection data
     */
    async getSwarmData() {
        const response = await fetch(`${window.location.origin}/api/swarms`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Get transaction data
     */
    async getTransactionData() {
        const response = await fetch(`${window.location.origin}/api/transactions`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Get bot addresses
     */
    async getBotAddresses() {
        const response = await fetch(`${window.location.origin}/api/bots`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Send command to backend
     */
    sendCommand(command, data = {}) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify({ command, data }));
        } else {
            console.warn('No WebSocket connection, command not sent:', command);
        }
    }

    /**
     * Subscribe to specific data streams
     */
    subscribeToStream(streamName, callback) {
        this.sendCommand('subscribe', { stream: streamName });

        // Store callback for the stream
        switch(streamName) {
            case 'tokenData':
                this.onTokenDataUpdate = callback;
                break;
            case 'swarmData':
                this.onSwarmDataUpdate = callback;
                break;
            case 'networkData':
                this.onNetworkDataUpdate = callback;
                break;
            case 'transactions':
                this.onTransactionUpdate = callback;
                break;
            case 'ethPrice':
                this.onEthPriceUpdate = callback;
                break;
            case 'ethermax':
                this.onEthermaxUpdate = callback;
                break;
        }
    }

    /**
     * Get current ETH price
     */
    getEthPrice() {
        return this.ethPrice;
    }

    /**
     * Get current Ethermax data
     */
    getEthermaxData() {
        return this.ethermaxData;
    }
}

// Export for use in dashboard
export { EnhancedDataConnector };

// Create global instance for easy access
const enhancedDataConnector = new EnhancedDataConnector();

// Initialize the connector when page loads
window.addEventListener('load', () => {
    enhancedDataConnector.connect().catch(console.error);
});

// Make it globally available
window.EnhancedDataConnector = enhancedDataConnector;