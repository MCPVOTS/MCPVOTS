import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { Line2 } from 'three/addons/lines/Line2.js';

class EthermaxDashboard {
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
        
        this.time = 0;
        
        this.dataConnector = null;
        
        this.init();
        this.setupEventListeners();
        this.setupDataConnector();
        this.animate();
    }
    
    setupDataConnector() {
        // Initialize data connector
        this.dataConnector = new (window.EthermaxDataConnector || class {
            constructor() {
                this.mockDataInterval = null;
            }
            
            connect() {
                // Start mock data updates if no real connector
                this.startMockDataUpdates();
            }
            
            startMockDataUpdates() {
                this.mockDataInterval = setInterval(() => {
                    // Simulate data updates
                    this.tokenData = {
                        price: 0.0012 + (Math.random() - 0.5) * 0.0002,
                        volume: 120000 + Math.random() * 10000,
                        liquidity: 500000 + Math.random() * 50000,
                        holders: 5200 + Math.floor(Math.random() * 100)
                    };
                    
                    this.swarmData = {
                        activeSwarms: Math.floor(Math.random() * 15),
                        botAddresses: Math.floor(Math.random() * 200) + 50,
                        confidenceScore: Math.floor(Math.random() * 40) + 60
                    };
                    
                    this.networkData = {
                        activeBots: Math.floor(Math.random() * 10) + 1,
                        txPerMin: Math.floor(Math.random() * 100) + 20,
                        networkLoad: Math.floor(Math.random() * 40) + 40
                    };
                    
                    // Update dashboard
                    this.updateUI();
                }, 3000);
            }
            
            subscribeToStream(streamName, callback) {
                // Handle subscription callbacks
                if (streamName === 'tokenData') this.onTokenDataUpdate = callback;
                if (streamName === 'swarmData') this.onSwarmDataUpdate = callback;
                if (streamName === 'networkData') this.onNetworkDataUpdate = callback;
                if (streamName === 'transactions') this.onTransactionUpdate = callback;
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
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0f);
        this.scene.fog = new THREE.Fog(0x0a0a0f, 10, 100);
        
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
        
        // Add orbit controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
    }
    
    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0x4facfe, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Back light for depth
        const backLight = new THREE.DirectionalLight(0x00f2fe, 0.5);
        backLight.position.set(-5, -5, -5);
        this.scene.add(backLight);
        
        // Hemisphere light for more natural illumination
        const hemisphereLight = new THREE.HemisphereLight(0x00f2fe, 0x11111b, 0.5);
        this.scene.add(hemisphereLight);
    }
    
    createGrid() {
        const gridHelper = new THREE.GridHelper(40, 20, 0x2a2a3a, 0x1a1a2a);
        gridHelper.position.y = -5;
        this.scene.add(gridHelper);
    }
    
    createParticleField() {
        const particleCount = 10000;
        const positions = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 80;     // x
            positions[i + 1] = (Math.random() - 0.5) * 20; // y
            positions[i + 2] = (Math.random() - 0.5) * 80; // z
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: 0x4facfe,
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
            color: 0x00f2fe,
            emissive: 0x0044ff,
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
        for (let i = 0; i < 12; i++) {
            const geometry = new THREE.IcosahedronGeometry(0.3, 1);
            const material = new THREE.MeshPhongMaterial({ 
                color: 0x4facfe,
                emissive: 0x0044ff,
                shininess: 100
            });
            
            const token = new THREE.Mesh(geometry, material);
            
            // Position in orbit
            const distance = 5 + Math.random() * 3;
            const angle = (i / 12) * Math.PI * 2;
            
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
        for (let i = 0; i < 8; i++) {
            const swarmGroup = new THREE.Group();
            
            // Create core
            const coreGeometry = new THREE.SphereGeometry(0.5, 16, 16);
            const coreMaterial = new THREE.MeshPhongMaterial({ 
                color: 0xff416c,
                emissive: 0x990000,
                shininess: 100
            });
            const core = new THREE.Mesh(coreGeometry, coreMaterial);
            core.scale.set(0.8, 0.8, 1);
            swarmGroup.add(core);
            
            // Create surrounding particles
            const particleCount = 20;
            for (let j = 0; j < particleCount; j++) {
                const particleGeometry = new THREE.SphereGeometry(0.1, 8, 8);
                const particleMaterial = new THREE.MeshPhongMaterial({ 
                    color: 0xff416c,
                    emissive: 0x660000,
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
        for (let i = 0; i < 15; i++) {
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
                color: 0x4facfe,
                linewidth: 0.005, // in pixels
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
    
    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
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
    }
    
    startDataSimulation() {
        // Simulate changing data
        setInterval(() => {
            // Update token data with realistic fluctuations
            this.tokenData.price += (Math.random() - 0.5) * 0.00005;
            this.tokenData.price = Math.max(0.0005, this.tokenData.price);
            this.tokenData.volume += (Math.random() - 0.5) * 2000;
            this.tokenData.volume = Math.max(100000, this.tokenData.volume);
            
            // Update swarm data
            this.swarmData.activeSwarms = Math.floor(Math.random() * 15);
            this.swarmData.botAddresses = Math.floor(Math.random() * 200) + 50;
            this.swarmData.confidenceScore = Math.floor(Math.random() * 40) + 60;
            
            // Update network data
            this.networkData.activeBots = Math.floor(Math.random() * 10) + 1;
            this.networkData.txPerMin = Math.floor(Math.random() * 100) + 20;
            this.networkData.networkLoad = Math.floor(Math.random() * 40) + 40;
            
            // Update UI
            this.updateUI();
        }, 3000); // Update every 3 seconds
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
        
        // Rotate particles
        if (this.particles) {
            this.particles.rotation.y = this.time * 0.05;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize dashboard when page loads
window.addEventListener('load', () => {
    new EthermaxDashboard();
});