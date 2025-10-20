import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';

interface MCPServer {
    process: any;
    isRunning: boolean;
}

let mcpServer: MCPServer | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('MCP Memory Manager extension is now active!');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('mcp-memory.updateMemory', updateMemory),
        vscode.commands.registerCommand('mcp-memory.addEntry', addEntry),
        vscode.commands.registerCommand('mcp-memory.refreshMemory', refreshMemory),
        vscode.commands.registerCommand('mcp-memory.viewMemory', viewMemory),
        vscode.commands.registerCommand('mcp-memory.startServer', startMCPServer),
        vscode.commands.registerCommand('mcp-memory.stopServer', stopMCPServer),
        vscode.commands.registerCommand('mcp-memory.storeMemory', storeMemory),
        vscode.commands.registerCommand('mcp-memory.searchMemory', searchMemory),
        vscode.commands.registerCommand('mcp-memory.listMemories', listMemories),
        vscode.commands.registerCommand('mcp-memory.showStats', showMemoryStats)
    );
}

export function deactivate() {
    stopMCPServer();
}

async function updateMemory() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const memoryFile = path.join(workspaceFolder.uri.fsPath, 'MCP_MEMORY_CURRENT.md');
    if (!fs.existsSync(memoryFile)) {
        vscode.window.showErrorMessage('MCP_MEMORY_CURRENT.md not found in workspace');
        return;
    }

    // Read current memory
    const content = fs.readFileSync(memoryFile, 'utf8');

    // Show quick pick for what to update
    const updateType = await vscode.window.showQuickPick([
        'System Status',
        'Component Status',
        'Network Information',
        'Trading Strategy',
        'Add Custom Entry'
    ], { placeHolder: 'What would you like to update?' });

    if (!updateType) return;

    let newContent = '';
    switch (updateType) {
        case 'System Status':
            newContent = await updateSystemStatus(content);
            break;
        case 'Component Status':
            newContent = await updateComponentStatus(content);
            break;
        case 'Network Information':
            newContent = await updateNetworkInfo(content);
            break;
        case 'Trading Strategy':
            newContent = await updateTradingStrategy(content);
            break;
        case 'Add Custom Entry':
            newContent = await addCustomEntry(content);
            break;
    }

    if (newContent) {
        fs.writeFileSync(memoryFile, newContent);
        vscode.window.showInformationMessage('MCP Memory updated successfully!');
        // Refresh the file in editor if open
        const document = vscode.workspace.textDocuments.find(doc => doc.fileName === memoryFile);
        if (document) {
            await document.save();
        }
    }
}

async function updateSystemStatus(content: string): Promise<string> {
    const status = await vscode.window.showQuickPick([
        '✅ OPERATIONAL',
        '⚠️ DEGRADED',
        '❌ DOWN',
        '🔄 MAINTENANCE'
    ], { placeHolder: 'Select new system status' });

    if (!status) return content;

    // Update the status line
    const statusRegex = /- Status: .*/;
    return content.replace(statusRegex, `- Status: ${status}`);
}

async function updateComponentStatus(content: string): Promise<string> {
    const component = await vscode.window.showInputBox({
        prompt: 'Enter component name (e.g., master_trading_system.py)',
        placeHolder: 'Component name'
    });

    if (!component) return content;

    const status = await vscode.window.showQuickPick([
        '✅ PASS',
        '⚠️ PARTIAL',
        '❌ FAIL',
        '🔄 UPDATING'
    ], { placeHolder: 'Select component status' });

    if (!status) return content;

    // Find and update component status
    const componentRegex = new RegExp(`(${component}[^\\n]*)(?=\\n\\n|$)`, 's');
    const match = content.match(componentRegex);

    if (match) {
        const updatedComponent = match[1].replace(/(- Status: ).*/, `$1${status}`);
        return content.replace(match[1], updatedComponent);
    }

    return content;
}

async function updateNetworkInfo(content: string): Promise<string> {
    const networkInfo = await vscode.window.showInputBox({
        prompt: 'Enter network information update',
        placeHolder: 'e.g., Chain: Base (8453) - Updated RPC endpoint'
    });

    if (!networkInfo) return content;

    // Find network section and update
    const networkRegex = /- Chain: .*/;
    return content.replace(networkRegex, `- Chain: ${networkInfo}`);
}

async function updateTradingStrategy(content: string): Promise<string> {
    const strategyUpdate = await vscode.window.showInputBox({
        prompt: 'Enter trading strategy update',
        placeHolder: 'e.g., Reactive thresholds changed to +15%/-8%'
    });

    if (!strategyUpdate) return content;

    // Find strategies section and add update
    const strategiesSection = content.indexOf('## 🧠 Strategies');
    if (strategiesSection !== -1) {
        const insertPoint = content.indexOf('\n\n', strategiesSection);
        if (insertPoint !== -1) {
            return content.slice(0, insertPoint) + `\n- **Update:** ${strategyUpdate}` + content.slice(insertPoint);
        }
    }

    return content;
}

async function addCustomEntry(content: string): Promise<string> {
    const section = await vscode.window.showQuickPick([
        'System Overview',
        'Current Status',
        'Core Components',
        'Strategies',
        'Intelligence',
        'Operations',
        'Health',
        'Insights',
        'Notes'
    ], { placeHolder: 'Select section to add entry to' });

    if (!section) return content;

    const entry = await vscode.window.showInputBox({
        prompt: `Enter new entry for ${section}`,
        placeHolder: 'Entry content'
    });

    if (!entry) return content;

    // Find section and add entry
    const sectionHeader = `## ${section === 'System Overview' ? '🔥 System Overview' :
                          section === 'Current Status' ? '📊 Current Status' :
                          section === 'Core Components' ? '🎯 Core Components' :
                          section === 'Strategies' ? '🧠 Strategies' :
                          section === 'Intelligence' ? '🔍 Intelligence' :
                          section === 'Operations' ? '⚙️ Ops' :
                          section === 'Health' ? '✅ Current Health' :
                          section === 'Insights' ? '💡 Key Insights' :
                          '⚠️ Notes'}`;

    const sectionIndex = content.indexOf(sectionHeader);
    if (sectionIndex !== -1) {
        const nextSectionIndex = content.indexOf('\n##', sectionIndex + 1);
        const insertPoint = nextSectionIndex !== -1 ? nextSectionIndex : content.length;
        const beforeInsert = content.slice(0, insertPoint);
        const afterInsert = content.slice(insertPoint);

        // Add bullet point
        const bulletEntry = entry.startsWith('- ') ? entry : `- ${entry}`;
        return beforeInsert + `\n${bulletEntry}` + afterInsert;
    }

    return content;
}

async function refreshMemory() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const memoryFile = path.join(workspaceFolder.uri.fsPath, 'MCP_MEMORY_CURRENT.md');
    if (!fs.existsSync(memoryFile)) {
        vscode.window.showErrorMessage('MCP_MEMORY_CURRENT.md not found in workspace');
        return;
    }

    // Read and parse memory file
    const content = fs.readFileSync(memoryFile, 'utf8');

    // Extract key information
    const statusMatch = content.match(/- Status: (.*)/);
    const chainMatch = content.match(/- Chain: (.*)/);
    const tokenMatch = content.match(/- Token: (.*)/);

    const status = statusMatch ? statusMatch[1] : 'Unknown';
    const chain = chainMatch ? chainMatch[1] : 'Unknown';
    const token = tokenMatch ? tokenMatch[1] : 'Unknown';

    // Show status summary
    vscode.window.showInformationMessage(
        `MCP Memory Status: ${status} | Chain: ${chain} | Token: ${token}`
    );
}

async function addEntry() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const memoryFile = path.join(workspaceFolder.uri.fsPath, 'MCP_MEMORY_CURRENT.md');
    if (!fs.existsSync(memoryFile)) {
        vscode.window.showErrorMessage('MCP_MEMORY_CURRENT.md not found in workspace');
        return;
    }

    // Read current memory
    const content = fs.readFileSync(memoryFile, 'utf8');

    const section = await vscode.window.showQuickPick([
        'System Overview',
        'Current Status',
        'Core Components',
        'Strategies',
        'Intelligence',
        'Operations',
        'Health',
        'Insights',
        'Notes'
    ], { placeHolder: 'Select section to add entry to' });

    if (!section) return;

    const entry = await vscode.window.showInputBox({
        prompt: `Enter new entry for ${section}`,
        placeHolder: 'Entry content'
    });

    if (!entry) return;

    // Find section and add entry
    const sectionHeader = `## ${section === 'System Overview' ? '🔥 System Overview' :
                          section === 'Current Status' ? '📊 Current Status' :
                          section === 'Core Components' ? '🎯 Core Components' :
                          section === 'Strategies' ? '🧠 Strategies' :
                          section === 'Intelligence' ? '🔍 Intelligence' :
                          section === 'Operations' ? '⚙️ Ops' :
                          section === 'Health' ? '✅ Current Health' :
                          section === 'Insights' ? '💡 Key Insights' :
                          '⚠️ Notes'}`;

    const sectionIndex = content.indexOf(sectionHeader);
    if (sectionIndex !== -1) {
        const nextSectionIndex = content.indexOf('\n##', sectionIndex + 1);
        const insertPoint = nextSectionIndex !== -1 ? nextSectionIndex : content.length;
        const beforeInsert = content.slice(0, insertPoint);
        const afterInsert = content.slice(insertPoint);

        // Add bullet point
        const bulletEntry = entry.startsWith('- ') ? entry : `- ${entry}`;
        const newContent = beforeInsert + `\n${bulletEntry}` + afterInsert;
        fs.writeFileSync(memoryFile, newContent);
        vscode.window.showInformationMessage('Entry added to MCP Memory!');
    }
}

async function viewMemory() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const memoryFile = path.join(workspaceFolder.uri.fsPath, 'MCP_MEMORY_CURRENT.md');
    if (!fs.existsSync(memoryFile)) {
        vscode.window.showErrorMessage('MCP_MEMORY_CURRENT.md not found in workspace');
        return;
    }

    // Open the memory file
    const document = await vscode.workspace.openTextDocument(memoryFile);
    await vscode.window.showTextDocument(document);
}

async function startMCPServer() {
    if (mcpServer?.isRunning) {
        vscode.window.showInformationMessage('MCP Memory Server is already running');
        return;
    }

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    const serverPath = path.join(workspaceFolder.uri.fsPath, 'maxx_memory_mcp_server.py');

    if (!fs.existsSync(serverPath)) {
        vscode.window.showErrorMessage('maxx_memory_mcp_server.py not found in workspace root');
        return;
    }

    try {
        // Start the Python MCP server
        const pythonProcess = spawn('python', [serverPath], {
            cwd: workspaceFolder.uri.fsPath,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        mcpServer = {
            process: pythonProcess,
            isRunning: true
        };

        // Handle process events
        pythonProcess.on('exit', (code) => {
            console.log(`MCP Server exited with code ${code}`);
            if (mcpServer) {
                mcpServer.isRunning = false;
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('MCP Server error:', error);
            vscode.window.showErrorMessage(`MCP Server error: ${error.message}`);
            if (mcpServer) {
                mcpServer.isRunning = false;
            }
        });

        // Log stdout for debugging
        pythonProcess.stdout?.on('data', (data) => {
            console.log('MCP Server stdout:', data.toString());
        });

        pythonProcess.stderr?.on('data', (data) => {
            console.error('MCP Server stderr:', data.toString());
        });

        vscode.window.showInformationMessage('MCP Memory Server started successfully');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start MCP Server: ${error}`);
    }
}

async function storeMemory() {
    if (!mcpServer?.isRunning) {
        vscode.window.showErrorMessage('MCP Memory Server is not running. Start it first.');
        return;
    }

    const content = await vscode.window.showInputBox({
        prompt: 'Enter memory content to store',
        placeHolder: 'Memory content'
    });

    if (!content) return;

    const category = await vscode.window.showQuickPick([
        'system',
        'trading',
        'analysis',
        'general'
    ], { placeHolder: 'Select memory category' });

    if (!category) return;

    // For demo purposes, create a simple vector (in real usage, you'd generate embeddings)
    const vector = Array.from({ length: 384 }, () => Math.random());

    try {
        // Send store_memory request to MCP server
        const request = {
            jsonrpc: '2.0',
            id: Date.now(),
            method: 'tools/call',
            params: {
                name: 'store_memory',
                arguments: {
                    content: content,
                    vector: vector,
                    category: category
                }
            }
        };

        const response = await sendMCPRequest(request);
        vscode.window.showInformationMessage(`Memory stored: ${response.result}`);
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to store memory: ${error}`);
    }
}

async function searchMemory() {
    if (!mcpServer?.isRunning) {
        vscode.window.showErrorMessage('MCP Memory Server is not running. Start it first.');
        return;
    }

    const query = await vscode.window.showInputBox({
        prompt: 'Enter search query',
        placeHolder: 'Search for memories'
    });

    if (!query) return;

    // For demo, create a simple query vector
    const queryVector = Array.from({ length: 384 }, () => Math.random());

    try {
        const request = {
            jsonrpc: '2.0',
            id: Date.now(),
            method: 'tools/call',
            params: {
                name: 'search_memory',
                arguments: {
                    query_vector: queryVector,
                    limit: 5
                }
            }
        };

        const response = await sendMCPRequest(request);
        const panel = vscode.window.createWebviewPanel(
            'memorySearch',
            'Memory Search Results',
            vscode.ViewColumn.One,
            {}
        );
        panel.webview.html = `<pre>${response.result}</pre>`;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to search memory: ${error}`);
    }
}

async function listMemories() {
    if (!mcpServer?.isRunning) {
        vscode.window.showErrorMessage('MCP Memory Server is not running. Start it first.');
        return;
    }

    try {
        const request = {
            jsonrpc: '2.0',
            id: Date.now(),
            method: 'tools/call',
            params: {
                name: 'list_memories',
                arguments: {
                    limit: 20
                }
            }
        };

        const response = await sendMCPRequest(request);
        const panel = vscode.window.createWebviewPanel(
            'memoryList',
            'Memory List',
            vscode.ViewColumn.One,
            {}
        );
        panel.webview.html = `<pre>${response.result}</pre>`;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to list memories: ${error}`);
    }
}

async function sendMCPRequest(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
        if (!mcpServer?.process) {
            reject(new Error('MCP Server not running'));
            return;
        }

        const requestJson = JSON.stringify(request) + '\n';
        mcpServer.process.stdin?.write(requestJson);

        let responseData = '';
        const timeout = setTimeout(() => {
            reject(new Error('MCP request timeout'));
        }, 10000);

        const onData = (data: Buffer) => {
            responseData += data.toString();
            try {
                const response = JSON.parse(responseData);
                clearTimeout(timeout);
                mcpServer?.process?.stdout?.removeListener('data', onData);
                resolve(response);
            } catch (e) {
                // Wait for more data
            }
        };

        mcpServer.process.stdout?.on('data', onData);
    });
}

async function stopMCPServer() {
    if (!mcpServer?.isRunning) {
        vscode.window.showInformationMessage('MCP Memory Server is not running');
        return;
    }

    try {
        mcpServer.process.kill();
        mcpServer.isRunning = false;
        vscode.window.showInformationMessage('MCP Memory Server stopped');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to stop MCP Server: ${error}`);
    }
}

async function showMemoryStats() {
    if (!mcpServer?.isRunning) {
        vscode.window.showErrorMessage('MCP Memory Server is not running. Start it first.');
        return;
    }

    try {
        const request = {
            jsonrpc: '2.0',
            id: Date.now(),
            method: 'tools/call',
            params: {
                name: 'get_memory_stats',
                arguments: {}
            }
        };

        const response = await sendMCPRequest(request);
        const stats = response.result;

        // Create a formatted stats display
        const panel = vscode.window.createWebviewPanel(
            'memoryStats',
            'MAXX Memory Statistics',
            vscode.ViewColumn.One,
            {}
        );

        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>MAXX Memory Statistics</title>
                <style>
                    body { font-family: var(--vscode-font-family); padding: 20px; }
                    .stat-card { background: var(--vscode-editor-background); border: 1px solid var(--vscode-panel-border); padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .stat-title { font-weight: bold; color: var(--vscode-textLink-foreground); margin-bottom: 10px; }
                    .stat-value { font-size: 24px; color: var(--vscode-textPreformat-foreground); }
                    .category-list { margin-top: 15px; }
                    .category-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--vscode-panel-border); }
                </style>
            </head>
            <body>
                <h2>🧠 MAXX Memory System Statistics</h2>
                <div class="stat-card">
                    <div class="stat-title">Total Memories Stored</div>
                    <div class="stat-value">${stats.match(/Total memories: (\d+)/)?.[1] || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Category Breakdown</div>
                    <div class="category-list">
                        ${stats.split('Memories by category:')[1]?.split('\n').filter(line => line.trim()).map(line => {
                            const match = line.trim().match(/^(\w+): (\d+)/);
                            return match ? `<div class="category-item"><span>${match[1]}</span><span>${match[2]}</span></div>` : '';
                        }).join('') || 'No category data available'}
                    </div>
                </div>
                <p><em>Last updated: ${new Date().toLocaleString()}</em></p>
            </body>
            </html>
        `;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to get memory stats: ${error}`);
    }
}