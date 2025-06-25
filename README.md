# MCPVots - Advanced Dark Theme MCP Integration Platform

![MCPVots CI/CD](https://github.com/kabrony/MCPVots/workflows/MCPVots%20CI/CD%20Pipeline/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node Version](https://img.shields.io/badge/node-%3E%3D14.0.0-brightgreen.svg)

**Advanced Dark Theme MCP Integration Platform**

A cutting-edge web application featuring the most advanced dark theme implementation with seamless Model Context Protocol (MCP) server integration, complete with comprehensive CI/CD pipeline.

## Features

### 🎨 Advanced Dark Theme
- **Ultra High Contrast**: Optimized for accessibility and eye comfort
- **Seamless Theme Switching**: Instant light/dark mode toggle with smooth transitions
- **System Integration**: Automatically respects user's system theme preferences
- **Accessibility First**: Full support for high contrast mode and reduced motion
- **Custom Properties**: Dynamic CSS variables for real-time theme customization

### 🔌 MCP Integration
- **Multi-Server Support**: Connect to multiple MCP servers simultaneously
- **Real-time Monitoring**: Live status updates and health monitoring
- **Automatic Reconnection**: Robust connection handling with retry logic
- **Message Queue**: Reliable message delivery system
- **Event-Driven Architecture**: Reactive updates based on server events

### 📊 System Dashboard
- **Live Statistics**: Real-time system metrics and performance data
- **Server Status**: Visual indicators for all connected MCP servers
- **Connection Management**: Easy control over server connections
- **Console Output**: Live logging with color-coded severity levels
- **Quick Actions**: One-click access to common operations

### 🚀 Modern Architecture
- **Component-Based**: Modular JavaScript architecture
- **Event System**: Decoupled communication between components
- **Responsive Design**: Optimized for all screen sizes
- **Performance Optimized**: Efficient rendering and minimal resource usage
- **TypeScript Ready**: Easy migration path to TypeScript

## Technology Stack

- **Frontend**: Vanilla JavaScript ES6+, CSS3, HTML5
- **Styling**: Tailwind CSS with custom CSS variables
- **Architecture**: Event-driven, component-based
- **Theme System**: CSS custom properties with JavaScript control
- **MCP Protocol**: WebSocket-based communication

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/kabrony/MCPVots.git
   cd MCPVots
   ```

2. **Open in browser**
   ```bash
   # Simply open index.html in your browser
   open index.html
   ```

3. **For development server** (optional)
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   ```

## Configuration

### MCP Servers
The application automatically discovers and connects to configured MCP servers. Default configuration includes:

- **GitHub MCP**: Repository and issue management
- **Memory MCP**: Knowledge graph and storage
- **HuggingFace MCP**: AI model integration
- **SuperMemory MCP**: Advanced memory systems
- **Solana MCP**: Blockchain integration
- **Browser Tools MCP**: Web automation

### Theme Customization
Themes can be customized by modifying CSS custom properties in `css/style.css`:

```css
:root {
    --dark-bg: #0a0a0a;
    --dark-text: #ffffff;
    --accent-primary: #3b82f6;
    /* ... more properties */
}
```

## API Reference

### Theme Manager
```javascript
// Get current theme
const theme = window.themeManager.getTheme();

// Set theme programmatically
window.themeManager.setTheme('dark');

// Toggle between light and dark
window.themeManager.toggleTheme();

// Enable automatic theme switching
window.themeManager.enableAutoTheme();
```

### MCP Integration
```javascript
// Get all server statuses
const servers = window.mcpIntegration.getAllServersStatus();

// Send message to specific server
await window.mcpIntegration.sendMessage('github-mcp', {
    type: 'query',
    data: { repository: 'MCPVots' }
});

// Listen for server events
window.mcpIntegration.on('messageReceived', (data) => {
    console.log('Received:', data);
});
```

### Application Events
```javascript
// Listen for theme changes
window.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});

// MCP server connection events
window.mcpIntegration.on('serverConnected', (data) => {
    console.log('Server connected:', data.serverId);
});
```

## Keyboard Shortcuts

- **Ctrl+Shift+T**: Toggle theme
- **Ctrl+R**: Refresh system status
- **Ctrl+Shift+C**: Toggle console visibility

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Development

### Project Structure
```
MCPVots/
├── index.html              # Main application entry point
├── css/
│   ├── style.css          # Core styles and theme system
│   └── components.css     # Component-specific styles
├── src/
│   ├── app.js            # Main application logic
│   ├── theme-manager.js  # Theme system management
│   └── mcp-integration.js # MCP server integration
└── README.md
```

### Adding New MCP Servers
1. Add server configuration in `mcp-integration.js`
2. Update the discovery method with new server details
3. Implement any server-specific message handlers

### Custom Themes
1. Define new CSS custom properties
2. Add theme configuration to ThemeManager
3. Update theme switching logic if needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Model Context Protocol**: For the excellent MCP specification
- **Tailwind CSS**: For the utility-first CSS framework
- **Web Standards**: For modern browser APIs enabling this application

## Roadmap

- [ ] TypeScript migration
- [ ] PWA support with offline functionality
- [ ] Plugin system for custom MCP integrations
- [ ] Advanced analytics and monitoring
- [ ] Multi-language support
- [ ] Custom theme builder UI
- [ ] WebAssembly optimization for complex operations

## Support

For support, please open an issue on GitHub or contact the development team.

---

**MCPVots** - Where advanced theming meets powerful MCP integration. 🚀
