# Ethermax Dashboard

An advanced 3D visualization dashboard for the Ethermax ecosystem, featuring real-time transaction tracking, swarm detection, and market analytics.

## Features

- **3D Visualization**: Interactive Three.js-based dashboard with real-time data
- **Swarm Detection**: Visual identification of coordinated bot activity
- **Real-time Analytics**: Live updates of token metrics and network activity
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Inspired by ethermax.tech with gradient colors and glass-morphism

## Technologies Used

- **Three.js**: 3D graphics and visualization
- **WebGL**: Hardware-accelerated rendering
- **WebSocket**: Real-time data streaming
- **Express.js**: Backend API server
- **HTML5/CSS3**: Modern web technologies

## Installation

1. Make sure you have Node.js installed
2. Navigate to the DASHBOARD directory:
   ```bash
   cd C:\PumpFun_Ecosystem\ECOSYSTEM_UNIFIED\DASHBOARD
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Open your browser to `http://localhost:8080`

## Project Structure

```
DASHBOARD/
├── index.html          # Main HTML page
├── main.js             # Main Three.js application
├── data-connector.js   # Data connection utilities
├── server.js           # Backend API server
├── package.json        # Project configuration
└── README.md           # This file
```

## Dashboard Components

1. **Central Token Visualization**: Large animated token in the center
2. **Orbiting Elements**: Smaller tokens orbiting the central token
3. **Swarm Representations**: Visual clusters of bot activity
4. **Particle Field**: Background particles for depth
5. **Real-time Metrics**: Live updating statistics panels
6. **Connection Lines**: Dynamic links showing relationships

## API Endpoints

- `GET /api/dashboard-data` - All dashboard data
- `GET /api/historical?range=24h&metric=price` - Historical data
- `GET /api/swarms` - Swarm detection data
- `GET /api/transactions` - Transaction data
- `GET /api/bots` - Bot address data
- `WS /api/ws` - WebSocket real-time updates

## Data Simulation

The dashboard includes sophisticated data simulation that generates realistic:
- Price fluctuations
- Volume changes
- Swarm detection
- Network activity
- Transaction patterns

## License

MIT License - see the LICENSE file for details.

---
Built with ❤️ for the Ethermax ecosystem