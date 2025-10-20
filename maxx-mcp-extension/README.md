# MAXX MCP Memory Integration for VSCode

This VSCode extension provides seamless integration with the MAXX Ecosystem MCP Memory Server, allowing you to manage vector-based memory for the MAXX trading system directly from VSCode.

## Features

- **Memory Storage**: Store memories with vector embeddings for semantic search
- **Semantic Search**: Find similar memories using vector similarity
- **Memory Management**: List, view, and manage stored memories
- **Statistics**: Get insights about your memory store
- **Server Integration**: Start and manage the MCP memory server

## Installation

1. **Install the Extension**:
   ```bash
   cd maxx-mcp-extension
   npm install
   npm run compile
   code --install-extension maxx-mcp-extension-0.0.1.vsix
   ```

2. **Dependencies**:
   - Python 3.8+
   - Required Python packages (install via pip):
     ```bash
     pip install mcp numpy
     ```

## Usage

### Starting the MCP Server

1. Open the MAXX Ecosystem workspace in VSCode
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run: `MAXX Memory: Start MCP Memory Server`

### Memory Operations

#### Store Memory
- Command: `MAXX Memory: Store Memory`
- Enter content and select category
- Memory is stored with vector embeddings

#### Search Memory
- Command: `MAXX Memory: Search Memory`
- Searches for semantically similar memories
- Results shown in output channel

#### List Memories
- Command: `MAXX Memory: List Memories`
- View all memories or filter by category
- Results shown in output channel

#### Memory Statistics
- Command: `MAXX Memory: Memory Statistics`
- Get overview of memory store contents

## MCP Server Configuration

The MCP server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "maxx-memory": {
      "command": "python",
      "args": ["maxx_memory_mcp_server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "MAXX_MEMORY_DB": "maxx_memory.db"
      }
    }
  }
}
```

## Memory Categories

- **trading**: Trading strategies, market analysis, trade records
- **system**: System status, configurations, technical details
- **analysis**: Market analysis, intelligence reports, patterns
- **general**: Miscellaneous memories and notes

## Architecture

```
VSCode Extension
    ↓
MCP Client (TypeScript)
    ↓
MCP Server (Python + FastMCP)
    ↓
Vector Memory Store (SQLite + NumPy)
```

## Development

### Building the Extension

```bash
cd maxx-mcp-extension
npm run compile
npm run watch  # For development
```

### Testing

```bash
npm test
```

## Integration with MAXX Ecosystem

This memory system integrates with:

- **MCP_MEMORY_CURRENT.md**: Current system state and status
- **Trading Bot**: Store and retrieve trading decisions
- **Intelligence Analyzer**: Cache analysis results
- **System Monitoring**: Track performance metrics

## API Reference

### MCP Tools Available

- `store_memory`: Store content with vector embeddings
- `search_memory`: Semantic search using vectors
- `retrieve_memory`: Get specific memory by ID
- `list_memories`: List memories with filtering
- `delete_memory`: Remove memory entries
- `get_memory_stats`: Statistics and analytics

## Troubleshooting

### Server Won't Start
- Ensure Python 3.8+ is installed
- Check that `maxx_memory_mcp_server.py` exists
- Verify MCP dependencies are installed

### Memory Operations Fail
- Ensure MCP server is running
- Check database file permissions
- Verify vector dimensions match

### Extension Not Loading
- Check VSCode version compatibility
- Ensure TypeScript compilation succeeded
- Check extension logs in Developer Console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

MIT License - see LICENSE file for details