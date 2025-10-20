import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { Line2 } from 'three/addons/lines/Line2.js';

class EnhancedEthermaxDashboard {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;

        // Scene objects
        this.particles = null;
        this.grid = null;
        this.tokens = [];
        this.swarms = [];
        this.connections = [];
        this.orbitingElements = [];
        this.ethPriceVisualization = null;

        // Data tracking
        this.tokenData = {
            price: 0.0012,
            volume: 120000,
            liquidity: 500000,
            holders: 5200
        };

        this.swarmData = {
            activeSwarms: 0,
            botAddresses: 0,
            confidenceScore: 0
        };

        this.networkData = {
            activeBots: 5,
            txPerMin: 45,
            networkLoad: 65
        };

        this.ethPriceData = {
            price: 0,
            change: 0
        };

        this.ethermaxData = {
            maxxBalance: 0,
            ethBalance: 0,
            totalValue: 0
        };

        this.time = 0;

        this.dataConnector = null;

        this.init();
        this.setupEventListeners();
        this.setupDataConnector();
        this.animate();
    }

    setupDataConnector() {
        // Initialize enhanced data connector
        this.dataConnector = new (window.EnhancedDataConnector || class {
            constructor() {
                this.ws = null;
                this.dataEndpoint = '/api/realtime';
                this.ethPriceEndpoint = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true';
                this.isConnected = false;
                this.reconnectInterval = 5000;
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

                // Callbacks
                this.onTokenDataUpdate = null;
                this.onSwarmDataUpdate = null;
                this.onNetworkDataUpdate = null;
                this.onTransactionUpdate = null;
                this.onEthPriceUpdate = null;
                this.onEthermaxUpdate = null;

                this.init();
            }

            init() {
                this.startEthPricePolling();
                this.startEthermaxSimulation();
            }

            async connect() {
                try {
                    await this.connectWebSocket();
                } catch (error) {
                    console.warn('WebSocket connection failed, falling back to REST API:', error);
                    this.startPolling();
                }
            }

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

            startPolling() {
                setInterval(async () => {
                    try {
                        await this.fetchData();
                    } catch (error) {
                        console.error('Error fetching data:', error);
                    }
                }, 5000);
            }

            async fetchData() {
                const response = await fetch(`${window.location.origin}/api/dashboard-data`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                this.handleDataUpdate(data);
            }

            startEthPricePolling() {
                this.fetchEthPrice();
                setInterval(() => {
                    this.fetchEthPrice();
                }, 30000);
            }

            async fetchEthPrice() {
                try {
                    const response = await fetch(this.ethPriceEndpoint);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    const newPrice = data.ethereum.usd;
                    const priceChange = data.ethereum.usd_24h_change;

                    if (this.ethPrice > 0) {
                        this.ethPrice = this.ethPrice * 0.9 + newPrice * 0.1;
                    } else {
                        this.ethPrice = newPrice;
                    }

                    this.ethPriceChange = priceChange;

                    if (this.onEthPriceUpdate) {
                        this.onEthPriceUpdate({
                            price: this.ethPrice,
                            change: this.ethPriceChange
                        });
                    }

                    if (this.ethermaxData.ethBalance > 0) {
                        this.ethermaxData.totalValue = this.ethermaxData.ethBalance * this.ethPrice +
                                                     (this.ethermaxData.maxxBalance * 0.0012);
                        if (this.onEthermaxUpdate) {
                            this.onEthermaxUpdate(this.ethermaxData);
                        }
                    }

                } catch (error) {
                    console.error('Error fetching ETH price:', error);
                }
            }

            startEthermaxSimulation() {
                setInterval(() => {
                    this.ethermaxData.maxxBalance += (Math.random() - 0.5) * 100;
                    this.ethermaxData.ethBalance += (Math.random() - 0.5) * 0.01;

                    this.ethermaxData.maxxBalance = Math.max(0, this.ethermaxData.maxxBalance);
                    this.ethermaxData.ethBalance = Math.max(0, this.ethermaxData.ethBalance);

                    this.ethermaxData.totalValue = this.ethermaxData.ethBalance * this.ethPrice +
                                                 (this.ethermaxData.maxxBalance * 0.0012);

                    if (this.onEthermaxUpdate) {
                        this.onEthermaxUpdate(this.ethermaxData);
                    }
                }, 5000);
            }

            handleDataUpdate(data) {
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

            subscribeToStream(streamName, callback) {
                this.sendCommand('subscribe', { stream: streamName });

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

            sendCommand(command, data = {}) {
                if (this.ws && this.isConnected) {
                    this.ws.send(JSON.stringify({ command, data }));
                } else {
                    console.warn('No WebSocket connection, command not sent:', command);
                }
            }
        })();

        // Connect to data source
        this.dataConnector.connect();

        // Subscribe to data streams
        this.dataConnector.subscribeToStream('tokenData', (data) => {
            this.tokenData = { ...this.tokenData, ...data };
            this.updateUI();
        });

        this.dataConnector.subscribeToStream('swarmData', (data) => {
            this.swarmData = { ...this.swarmData, ...data };
            this.updateUI();
        });

        this.dataConnector.subscribeToStream('networkData', (data) => {
            this.networkData = { ...this.networkData, ...data };
            this.updateUI();
        });

        this.dataConnector.subscribeToStream('ethPrice', (data) => {
            this.ethPriceData = data;
            this.updateUI();
            this.updateEthPriceVisualization();
        });

        this.dataConnector.subscribeToStream('ethermax', (data) => {
            this.ethermaxData = data;
            this.updateUI();
            this.updateEthermaxVisualization();
        });
    }

    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000000);
        this.scene.fog = new THREE.Fog(0x000000, 10, 100);

        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 5, 20);

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('container').appendChild(this.renderer.domElement);

        // Add lights
        this.addLights();

        // Create grid
        this.createGrid();

        // Create particle field
        this.createParticleField();

        // Create central token visualization
        this.createCentralToken();

        // Create orbiting elements
        this.createOrbitingElements();

        // Create swarm visualizations
        this.createSwarms();

        // Create connection lines
        this.createConnections();

        // Create ETH price visualization
        this.createEthPriceVisualization();

        // Add orbit controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;

        // Initialize anime.js animations
        this.initializeAnimeAnimations();
    }

    initializeAnimeAnimations() {
        // Animate title on load
        anime({
            targets: '.title',
            translateY: [-50, 0],
            opacity: [0, 1],
            duration: 1500,
            easing: 'easeOutExpo'
        });

        // Animate subtitle
        anime({
            targets: '.subtitle',
            translateY: [30, 0],
            opacity: [0, 1],
            duration: 1200,
            delay: 300,
            easing: 'easeOutExpo'
        });

        // Animate stat cards
        anime({
            targets: '.stat-card',
            translateY: [50, 0],
            opacity: [0, 1],
            duration: 1000,
            delay: anime.stagger(200),
            easing: 'easeOutExpo'
        });

        // Animate panels
        anime({
            targets: '.info-panel, .ethermax-panel, .price-ticker',
            scale: [0.8, 1],
            opacity: [0, 1],
            duration: 1000,
            delay: 800,
            easing: 'easeOutExpo'
        });
    }

    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
        this.scene.add(ambientLight);

        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0x00ff88, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // Back light for depth
        const backLight = new THREE.DirectionalLight(0xff00ff, 0.5);
        backLight.position.set(-5, -5, -5);
        this.scene.add(backLight);

        // Hemisphere light for more natural illumination
        const hemisphereLight = new THREE.HemisphereLight(0x00ffff, 0x000000, 0.5);
        this.scene.add(hemisphereLight);
    }

    createGrid() {
        const gridHelper = new THREE.GridHelper(40, 20, 0x00ff88, 0x004422);
        gridHelper.position.y = -5;
        this.scene.add(gridHelper);
    }

    createParticleField() {
        const particleCount = 15000;
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 80;     // x
            positions[i + 1] = (Math.random() - 0.5) * 20; // y
            positions[i + 2] = (Math.random() - 0.5) * 80; // z
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            color: 0x00ff88,
            size: 0.05,
            transparent: true,
            opacity: 0.6,
            sizeAttenuation: true
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    createCentralToken() {
        // Create a large central token representation
        const geometry = new THREE.IcosahedronGeometry(2, 3);
        const material = new THREE.MeshPhongMaterial({
            color: 0x00ff88,
            emissive: 0x00ff44,
            shininess: 100,
            flatShading: true,
            transparent: true,
            opacity: 0.9
        });

        this.centralToken = new THREE.Mesh(geometry, material);
        this.centralToken.position.y = 0;
        this.scene.add(this.centralToken);

        // Add a pulsing effect
        this.pulseEffect = { scale: 1, direction: 1 };
    }

    createOrbitingElements() {
        // Create smaller tokens orbiting the central one
        for (let i = 0; i < 16; i++) {
            const geometry = new THREE.IcosahedronGeometry(0.3, 1);
            const material = new THREE.MeshPhongMaterial({
                color: 0x00ffff,
                emissive: 0x0088ff,
                shininess: 100
            });

            const token = new THREE.Mesh(geometry, material);

            // Position in orbit
            const distance = 5 + Math.random() * 3;
            const angle = (i / 16) * Math.PI * 2;

            token.position.x = Math.cos(angle) * distance;
            token.position.z = Math.sin(angle) * distance;
            token.position.y = (Math.random() - 0.5) * 2;

            token.userData = {
                distance: distance,
                angle: angle,
                verticalOffset: (Math.random() - 0.5) * 2,
                speed: 0.002 + Math.random() * 0.003,
                verticalSpeed: 0.5 + Math.random() * 0.5
            };

            this.scene.add(token);
            this.orbitingElements.push(token);
        }
    }

    createSwarms() {
        // Create swarm representations
        for (let i = 0; i < 10; i++) {
            const swarmGroup = new THREE.Group();

            // Create core
            const coreGeometry = new THREE.SphereGeometry(0.5, 16, 16);
            const coreMaterial = new THREE.MeshPhongMaterial({
                color: 0xff00ff,
                emissive: 0xff0088,
                shininess: 100
            });
            const core = new THREE.Mesh(coreGeometry, coreMaterial);
            core.scale.set(0.8, 0.8, 1);
            swarmGroup.add(core);

            // Create surrounding particles
            const particleCount = 25;
            for (let j = 0; j < particleCount; j++) {
                const particleGeometry = new THREE.SphereGeometry(0.1, 8, 8);
                const particleMaterial = new THREE.MeshPhongMaterial({
                    color: 0xff00ff,
                    emissive: 0xff0088,
                    transparent: true,
                    opacity: 0.8
                });
                const particle = new THREE.Mesh(particleGeometry, particleMaterial);

                // Position particles in a spherical formation
                const radius = 1.5;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);

                particle.position.x = radius * Math.sin(phi) * Math.cos(theta);
                particle.position.y = radius * Math.sin(phi) * Math.sin(theta);
                particle.position.z = radius * Math.cos(phi);

                particle.userData = {
                    originalPos: particle.position.clone(),
                    orbitRadius: radius,
                    angle: Math.random() * Math.PI * 2,
                    speed: Math.random() * 0.02 + 0.01,
                    verticalSpeed: Math.random() * 0.01
                };

                swarmGroup.add(particle);
            }

            // Random position around the scene
            swarmGroup.position.x = (Math.random() - 0.5) * 30;
            swarmGroup.position.y = Math.random() * 5;
            swarmGroup.position.z = (Math.random() - 0.5) * 30;

            swarmGroup.userData = {
                originalPos: swarmGroup.position.clone(),
                floatSpeed: Math.random() * 0.002 + 0.001,
                floatOffset: Math.random() * Math.PI * 2
            };

            this.scene.add(swarmGroup);
            this.swarms.push(swarmGroup);
        }
    }

    createConnections() {
        // Create dynamic connections between elements
        for (let i = 0; i < 20; i++) {
            const start = new THREE.Vector3(
                (Math.random() - 0.5) * 20,
                Math.random() * 10,
                (Math.random() - 0.5) * 20
            );

            const end = new THREE.Vector3(
                (Math.random() - 0.5) * 20,
                Math.random() * 10,
                (Math.random() - 0.5) * 20
            );

            const points = [start, end];

            const lineGeometry = new LineGeometry();
            lineGeometry.setPositions([
                start.x, start.y, start.z,
                end.x, end.y, end.z
            ]);

            const lineMaterial = new LineMaterial({
                color: 0x00ffff,
                linewidth: 0.005,
                transparent: true,
                opacity: 0.3
            });

            const line = new Line2(lineGeometry, lineMaterial);
            line.userData = {
                start: start.clone(),
                end: end.clone(),
                pulse: Math.random() * Math.PI * 2
            };

            this.scene.add(line);
            this.connections.push(line);
        }
    }

    createEthPriceVisualization() {
        // Create a dynamic ETH price visualization
        const geometry = new THREE.TorusGeometry(3, 0.5, 16, 100);
        const material = new THREE.MeshPhongMaterial({
            color: 0xffd700,
            emissive: 0xffaa00,
            shininess: 100,
            transparent: true,
            opacity: 0.8
        });

        this.ethPriceVisualization = new THREE.Mesh(geometry, material);
        this.ethPriceVisualization.position.set(10, 5, 0);
        this.scene.add(this.ethPriceVisualization);

        // Add price text
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 128;

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(10, 8, 0);
        sprite.scale.set(4, 2, 1);

        this.ethPriceText = { sprite, canvas, context, texture };
        this.scene.add(sprite);
    }

    updateEthPriceVisualization() {
        if (!this.ethPriceText) return;

        const { canvas, context, texture } = this.ethPriceText;
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Draw price text
        context.fillStyle = '#ffd700';
        context.font = 'bold 24px Inter';
        context.textAlign = 'center';
        context.fillText(`$${this.ethPriceData.price.toFixed(2)}`, canvas.width / 2, 40);

        // Draw change indicator
        const changeColor = this.ethPriceData.change >= 0 ? '#00ff88' : '#ff4444';
        context.fillStyle = changeColor;
        context.font = 'bold 18px Inter';
        const changeText = `${this.ethPriceData.change >= 0 ? '+' : ''}${this.ethPriceData.change.toFixed(2)}%`;
        context.fillText(changeText, canvas.width / 2, 80);

        texture.needsUpdate = true;
    }

    updateEthermaxVisualization() {
        // Update Ethermax visualization based on balance data
        if (this.centralToken) {
            const scale = 1 + (this.ethermaxData.totalValue / 10000) * 0.1;
            anime({
                targets: this.centralToken.scale,
                x: scale,
                y: scale,
                z: scale,
                duration: 1000,
                easing: 'easeOutExpo'
            });
        }
    }

    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Handle connect wallet button
        document.querySelector('.cta-button').addEventListener('click', () => {
            this.connectWallet();
        });
    }

    connectWallet() {
        // Simulate wallet connection
        anime({
            targets: '.cta-button',
            scale: [1, 0.95, 1],
            duration: 300,
            easing: 'easeInOutQuad'
        });

        // Show connecting animation
        anime({
            targets: '.logo',
            color: ['#00ff88', '#ffffff', '#00ff88'],
            duration: 1000,
            easing: 'easeInOutQuad'
        });

        // Simulate connection success
        setTimeout(() => {
            anime({
                targets: '.cta-button',
                backgroundColor: ['#00ff88', '#00ffff'],
                color: ['#000000', '#000000'],
                duration: 500,
                easing: 'easeInOutQuad'
            });
        }, 1000);
    }

    updateUI() {
        // Update all UI elements with current data
        document.getElementById('price-value').textContent = `$${this.tokenData.price.toFixed(6)}`;
        document.getElementById('volume-value').textContent = `$${(this.tokenData.volume / 1000).toFixed(0)}K`;
        document.getElementById('swarms-value').textContent = this.swarmData.activeSwarms;
        document.getElementById('bots-value').textContent = this.swarmData.botAddresses;

        document.getElementById('network-load').textContent = `${this.swarmData.confidenceScore}%`;
        document.getElementById('active-bots').textContent = this.networkData.activeBots;
        document.getElementById('tx-per-min').textContent = this.networkData.txPerMin;
        document.getElementById('confidence-score').textContent = `${this.swarmData.confidenceScore}%`;

        // Update ETH price
        document.getElementById('eth-price').textContent = `$${this.ethPriceData.price.toFixed(2)}`;
        const priceChangeElement = document.getElementById('price-change');
        const changeText = `${this.ethPriceData.change >= 0 ? '+' : ''}${this.ethPriceData.change.toFixed(2)}%`;
        priceChangeElement.innerHTML = `<span class="${this.ethPriceData.change >= 0 ? 'price-up' : 'price-down'}">${changeText}</span>`;

        // Update Ethermax balances
        document.getElementById('maxx-balance').textContent = this.ethermaxData.maxxBalance.toFixed(2);
        document.getElementById('maxx-value').textContent = `$${(this.ethermaxData.maxxBalance * this.tokenData.price).toFixed(2)}`;
        document.getElementById('eth-balance').textContent = this.ethermaxData.ethBalance.toFixed(4);
        document.getElementById('total-value').textContent = `$${this.ethermaxData.totalValue.toFixed(2)}`;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        this.time += 0.01;

        // Update controls
        if (this.controls) {
            this.controls.update();
        }

        // Animate central token
        if (this.centralToken) {
            this.centralToken.rotation.x += 0.005;
            this.centralToken.rotation.y += 0.005;

            // Pulsing effect
            this.pulseEffect.scale = 1 + Math.sin(this.time * 2) * 0.05;
            this.centralToken.scale.set(this.pulseEffect.scale, this.pulseEffect.scale, this.pulseEffect.scale);
        }

        // Animate orbiting elements
        this.orbitingElements.forEach(element => {
            element.userData.angle += element.userData.speed;
            element.position.x = Math.cos(element.userData.angle) * element.userData.distance;
            element.position.z = Math.sin(element.userData.angle) * element.userData.distance;
            element.position.y = element.userData.verticalOffset + Math.sin(this.time * element.userData.verticalSpeed) * 0.5;

            element.rotation.x += 0.01;
            element.rotation.y += 0.01;
        });

        // Animate swarms
        this.swarms.forEach(swarm => {
            // Float up and down
            swarm.position.y = swarm.userData.originalPos.y + Math.sin(this.time * swarm.userData.floatSpeed + swarm.userData.floatOffset) * 0.5;

            // Rotate the entire swarm
            swarm.rotation.y += 0.005;

            // Animate individual particles
            swarm.children.forEach((child, index) => {
                if (index > 0) { // Skip the core (index 0)
                    child.userData.angle += child.userData.speed;
                    child.position.x = Math.cos(child.userData.angle) * child.userData.orbitRadius;
                    child.position.z = Math.sin(child.userData.angle) * child.userData.orbitRadius;
                    child.position.y = Math.sin(this.time * child.userData.verticalSpeed) * 0.2;

                    child.rotation.y += 0.02;
                }
            });
        });

        // Animate connections
        this.connections.forEach(conn => {
            conn.userData.pulse += 0.05;
            const pulseEffect = Math.sin(conn.userData.pulse) * 0.2 + 0.8;
            conn.material.opacity = 0.1 + pulseEffect * 0.3;
        });

        // Animate particles
        if (this.particles) {
            this.particles.rotation.y = this.time * 0.05;
        }

        // Animate ETH price visualization
        if (this.ethPriceVisualization) {
            this.ethPriceVisualization.rotation.x += 0.01;
            this.ethPriceVisualization.rotation.y += 0.02;

            // Scale based on price volatility
            const volatility = Math.abs(this.ethPriceData.change) / 100;
            const scale = 1 + volatility * 0.2;
            this.ethPriceVisualization.scale.set(scale, scale, scale);
        }

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize dashboard when page loads
window.addEventListener('load', () => {
    new EnhancedEthermaxDashboard();
});