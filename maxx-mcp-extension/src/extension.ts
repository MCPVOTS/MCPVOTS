import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

interface MCPMemoryResult {
    content: string;
    similarity?: number;
    metadata?: any;
    category?: string;
    timestamp?: number;
}

class MCPMemoryClient {
    private serverProcess: any = null;
    private isServerRunning = false;

    async startServer(): Promise<boolean> {
        if (this.isServerRunning) {
            return true;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        const serverPath = path.join(workspaceFolder.uri.fsPath, 'maxx_memory_mcp_server.py');
        if (!fs.existsSync(serverPath)) {
            throw new Error('MCP server file not found: maxx_memory_mcp_server.py');
        }

        return new Promise((resolve, reject) => {
            try {
                // Start the MCP server
                this.serverProcess = spawn('python', [serverPath], {
                    cwd: workspaceFolder.uri.fsPath,
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                this.serverProcess.on('error', (error: any) => {
                    console.error('MCP Server error:', error);
                    this.isServerRunning = false;
                    reject(error);
                });

                this.serverProcess.on('exit', (code: number) => {
                    console.log('MCP Server exited with code:', code);
                    this.isServerRunning = false;
                });

                // Wait a bit for server to start
                setTimeout(() => {
                    this.isServerRunning = true;
                    resolve(true);
                }, 2000);

            } catch (error) {
                reject(error);
            }
        });
    }

    async callTool(toolName: string, args: any = {}): Promise<string> {
        // For now, we'll simulate MCP calls since we need proper MCP client implementation
        // In a real implementation, you'd use the MCP SDK to communicate with the server

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        // Simulate different tool calls
        switch (toolName) {
            case 'store_memory':
                return this.simulateStoreMemory(args);
            case 'search_memory':
                return this.simulateSearchMemory(args);
            case 'list_memories':
                return this.simulateListMemories(args);
            case 'get_memory_stats':
                return this.simulateGetStats();
            default:
                throw new Error(`Unknown tool: ${toolName}`);
        }
    }

    private async simulateStoreMemory(args: any): Promise<string> {
        // Simulate storing memory
        const content = args.content || 'Sample memory content';
        const vector = args.vector || [0.1, 0.2, 0.3];
        const category = args.category || 'general';

        // In real implementation, this would call the MCP server
        return `Successfully stored memory: "${content.substring(0, 50)}..." in category "${category}"`;
    }

    private async simulateSearchMemory(args: any): Promise<string> {
        // Simulate searching memory
        const queryVector = args.query_vector || [0.1, 0.2, 0.3];
        const limit = args.limit || 5;

        // In real implementation, this would call the MCP server
        return `Found ${limit} similar memories for query vector [${queryVector.slice(0, 3).join(', ')}...]`;
    }

    private async simulateListMemories(args: any): Promise<string> {
        // Simulate listing memories
        const category = args.category || 'all';
        const limit = args.limit || 10;

        // In real implementation, this would call the MCP server
        return `Found ${limit} memories${category !== 'all' ? ` in category "${category}"` : ''}`;
    }

    private async simulateGetStats(): Promise<string> {
        // Simulate getting memory statistics
        return `MAXX Memory Statistics:
Total memories: 42
Categories:
  trading: 15
  system: 12
  analysis: 10
  general: 5`;
    }

    stopServer() {
        if (this.serverProcess) {
            this.serverProcess.kill();
            this.serverProcess = null;
            this.isServerRunning = false;
        }
    }
}

// Global MCP client instance
let mcpClient: MCPMemoryClient | null = null;

function getMCPClient(): MCPMemoryClient {
    if (!mcpClient) {
        mcpClient = new MCPMemoryClient();
    }
    return mcpClient;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('MAXX MCP Memory extension is now active!');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('maxx-mcp-memory.storeMemory', storeMemory),
        vscode.commands.registerCommand('maxx-mcp-memory.searchMemory', searchMemory),
        vscode.commands.registerCommand('maxx-mcp-memory.listMemories', listMemories),
        vscode.commands.registerCommand('maxx-mcp-memory.getStats', getStats),
        vscode.commands.registerCommand('maxx-mcp-memory.startServer', startServer)
    );

    // Clean up on deactivation
    context.subscriptions.push({
        dispose: () => {
            if (mcpClient) {
                mcpClient.stopServer();
            }
        }
    });
}

export function deactivate() {
    if (mcpClient) {
        mcpClient.stopServer();
    }
}

async function startServer() {
    const client = getMCPClient();
    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Starting MAXX MCP Memory Server...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Initializing server..." });
            const success = await client.startServer();
            progress.report({ increment: 100, message: "Server started successfully!" });

            if (success) {
                vscode.window.showInformationMessage('MAXX MCP Memory Server started successfully!');
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to start MCP server: ${error.message}`);
    }
}

async function storeMemory() {
    const client = getMCPClient();

    // Get user input
    const content = await vscode.window.showInputBox({
        prompt: 'Enter memory content',
        placeHolder: 'What would you like to remember?'
    });

    if (!content) return;

    const category = await vscode.window.showQuickPick([
        'trading',
        'system',
        'analysis',
        'general'
    ], {
        placeHolder: 'Select memory category'
    });

    if (!category) return;

    // Generate a simple vector (in real implementation, you'd use embeddings)
    const vector = Array.from({ length: 128 }, () => Math.random() - 0.5);

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Storing memory...",
            cancellable: false
        }, async (progress) => {
            const result = await client.callTool('store_memory', {
                content,
                vector,
                category
            });
            vscode.window.showInformationMessage(result);
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to store memory: ${error.message}`);
    }
}

async function searchMemory() {
    const client = getMCPClient();

    // For demo purposes, use a random vector
    // In real implementation, you'd get user input or use current context
    const queryVector = Array.from({ length: 128 }, () => Math.random() - 0.5);

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Searching memories...",
            cancellable: false
        }, async (progress) => {
            const result = await client.callTool('search_memory', {
                query_vector: queryVector,
                limit: 5
            });

            // Show results in output channel
            const channel = vscode.window.createOutputChannel('MAXX Memory Search');
            channel.clear();
            channel.appendLine('MAXX Memory Search Results:');
            channel.appendLine('=' .repeat(50));
            channel.appendLine(result);
            channel.show();
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to search memory: ${error.message}`);
    }
}

async function listMemories() {
    const client = getMCPClient();

    const category = await vscode.window.showQuickPick([
        'all',
        'trading',
        'system',
        'analysis',
        'general'
    ], {
        placeHolder: 'Select category to list (or "all")'
    });

    if (!category) return;

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Listing memories...",
            cancellable: false
        }, async (progress) => {
            const result = await client.callTool('list_memories', {
                category: category === 'all' ? null : category,
                limit: 20
            });

            // Show results in output channel
            const channel = vscode.window.createOutputChannel('MAXX Memory List');
            channel.clear();
            channel.appendLine('MAXX Memory List:');
            channel.appendLine('=' .repeat(50));
            channel.appendLine(result);
            channel.show();
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list memories: ${error.message}`);
    }
}

async function getStats() {
    const client = getMCPClient();

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Getting memory statistics...",
            cancellable: false
        }, async (progress) => {
            const result = await client.callTool('get_memory_stats');

            // Show results in information message
            vscode.window.showInformationMessage('Memory Statistics Retrieved', 'View Details')
                .then(selection => {
                    if (selection === 'View Details') {
                        const channel = vscode.window.createOutputChannel('MAXX Memory Stats');
                        channel.clear();
                        channel.appendLine('MAXX Memory Statistics:');
                        channel.appendLine('=' .repeat(50));
                        channel.appendLine(result);
                        channel.show();
                    }
                });
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to get memory stats: ${error.message}`);
    }
}