#!/usr/bin/env python3
"""
n8n Configuration and Integration Manager
========================================
Manages n8n installation, configuration, and integration with the MCPVots AGI ecosystem.
Provides automated setup, custom node creation, and workflow synchronization.
"""

import asyncio
import json
import logging
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiohttp
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8NManager:
    def __init__(self, base_dir: str = "n8n"):
        self.base_dir = Path(base_dir)
        self.n8n_data_dir = self.base_dir / "data"
        self.n8n_config_dir = self.base_dir / "config"
        self.custom_nodes_dir = self.base_dir / "custom-nodes"
        self.workflows_dir = self.base_dir / "workflows"
        self.n8n_port = 5678
        self.n8n_process = None
        
        # AGI Integration endpoints
        self.agi_endpoints = {
            "gemini": "http://localhost:8015",
            "trilogy": "http://localhost:8000",
            "memory": "http://localhost:3002",
            "n8n_integration": "http://localhost:8020"
        }
        
    async def setup_n8n_environment(self) -> bool:
        """Set up n8n environment and configuration"""
        try:
            logger.info("🔧 Setting up n8n environment...")
            
            # Create directories
            self._create_directories()
            
            # Check if n8n is installed
            if not await self._check_n8n_installation():
                logger.info("📦 Installing n8n...")
                await self._install_n8n()
            
            # Create configuration files
            await self._create_n8n_config()
            
            # Create custom AGI nodes
            await self._create_custom_agi_nodes()
            
            # Set up environment variables
            await self._setup_environment_variables()
            
            logger.info("✅ n8n environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup n8n environment: {e}")
            return False
            
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.n8n_data_dir,
            self.n8n_config_dir,
            self.custom_nodes_dir,
            self.workflows_dir,
            self.custom_nodes_dir / "agi-nodes",
            self.workflows_dir / "templates"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
            
    async def _check_n8n_installation(self) -> bool:
        """Check if n8n is installed"""
        try:
            result = subprocess.run(
                ["n8n", "--version"], 
                capture_output=True, 
                text=True,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"✅ n8n is installed: {result.stdout.strip()}")
                return True
            return False
        except:
            return False
            
    async def _install_n8n(self):
        """Install n8n via npm"""
        try:
            # Install n8n globally
            logger.info("Installing n8n globally via npm...")
            result = subprocess.run(
                ["npm", "install", "-g", "n8n"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                raise Exception(f"npm install failed: {result.stderr}")
                
            logger.info("✅ n8n installed successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to install n8n: {e}")
            # Try alternative installation
            await self._install_n8n_alternative()
            
    async def _install_n8n_alternative(self):
        """Alternative n8n installation via Docker"""
        try:
            logger.info("Trying Docker installation...")
            
            # Create Docker Compose file
            docker_compose = {
                "version": "3.8",
                "services": {
                    "n8n": {
                        "image": "n8nio/n8n:latest",
                        "container_name": "n8n",
                        "ports": [f"{self.n8n_port}:5678"],
                        "environment": [
                            "N8N_BASIC_AUTH_ACTIVE=false",
                            "N8N_HOST=localhost",
                            f"N8N_PORT={self.n8n_port}",
                            "N8N_PROTOCOL=http",
                            "WEBHOOK_URL=http://localhost:5678/",
                            "GENERIC_TIMEZONE=UTC"
                        ],
                        "volumes": [
                            f"{self.n8n_data_dir.absolute()}:/home/node/n8n",
                            f"{self.custom_nodes_dir.absolute()}:/home/node/n8n/custom-nodes"
                        ],
                        "restart": "unless-stopped"
                    }
                }
            }
            
            docker_compose_file = self.base_dir / "docker-compose.yml"
            with open(docker_compose_file, 'w') as f:
                yaml.dump(docker_compose, f, default_flow_style=False)
                
            logger.info("✅ Docker Compose file created")
            
        except Exception as e:
            logger.error(f"❌ Docker installation also failed: {e}")
            
    async def _create_n8n_config(self):
        """Create n8n configuration"""
        try:
            config = {
                "host": "localhost",
                "port": self.n8n_port,
                "protocol": "http",
                "basicAuth": {
                    "active": False
                },
                "endpoints": {
                    "webhook": "webhook",
                    "webhookTest": "webhook-test"
                },
                "externalHookFiles": [],
                "nodes": {
                    "communityPackages": {
                        "enabled": True,
                        "registry": "https://www.npmjs.com/"
                    }
                },
                "credentials": {
                    "overwrite": {
                        "data": "{}"
                    }
                },
                "workflows": {
                    "defaultName": "My Workflow"
                }
            }
            
            config_file = self.n8n_config_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("✅ n8n configuration created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create n8n config: {e}")
            
    async def _create_custom_agi_nodes(self):
        """Create custom AGI nodes for n8n"""
        try:
            logger.info("🧩 Creating custom AGI nodes...")
            
            # Create package.json for custom nodes
            package_json = {
                "name": "n8n-nodes-agi-mcpvots",
                "version": "1.0.0",
                "description": "Custom n8n nodes for MCPVots AGI ecosystem",
                "main": "index.js",
                "scripts": {
                    "build": "tsc",
                    "dev": "tsc --watch"
                },
                "keywords": ["n8n", "n8n-community-node-package", "agi", "mcpvots"],
                "license": "MIT",
                "homepage": "https://github.com/mcpvots/n8n-nodes-agi",
                "author": "MCPVots Team",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/mcpvots/n8n-nodes-agi.git"
                },
                "n8n": {
                    "n8nNodesApiVersion": 1,
                    "nodes": [
                        "dist/nodes/GeminiCli/GeminiCli.node.js",
                        "dist/nodes/TrilogyAgi/TrilogyAgi.node.js",
                        "dist/nodes/MemoryMcp/MemoryMcp.node.js",
                        "dist/nodes/OllamaLocal/OllamaLocal.node.js",
                        "dist/nodes/DeerFlow/DeerFlow.node.js"
                    ]
                },
                "devDependencies": {
                    "n8n-workflow": "^1.0.0",
                    "typescript": "^4.9.0",
                    "@types/node": "^18.0.0"
                },
                "dependencies": {
                    "axios": "^1.4.0"
                }
            }
            
            package_file = self.custom_nodes_dir / "package.json"
            with open(package_file, 'w') as f:
                json.dump(package_json, f, indent=2)
                
            # Create TypeScript configuration
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "lib": ["ES2020"],
                    "declaration": True,
                    "outDir": "./dist",
                    "rootDir": "./src",
                    "strict": True,
                    "noImplicitAny": True,
                    "strictNullChecks": True,
                    "strictFunctionTypes": True,
                    "noImplicitReturns": True,
                    "noImplicitThis": True,
                    "alwaysStrict": True,
                    "noUnusedLocals": True,
                    "noUnusedParameters": True,
                    "exactOptionalPropertyTypes": True,
                    "noImplicitOverride": True,
                    "noPropertyAccessFromIndexSignature": True,
                    "moduleResolution": "node",
                    "allowSyntheticDefaultImports": True,
                    "esModuleInterop": True,
                    "experimentalDecorators": True,
                    "emitDecoratorMetadata": True,
                    "skipLibCheck": True,
                    "forceConsistentCasingInFileNames": True
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules", "dist"]
            }
            
            tsconfig_file = self.custom_nodes_dir / "tsconfig.json"
            with open(tsconfig_file, 'w') as f:
                json.dump(tsconfig, f, indent=2)
                
            # Create individual AGI nodes
            await self._create_gemini_node()
            await self._create_trilogy_node()
            await self._create_memory_node()
            await self._create_ollama_node()
            await self._create_deerflow_node()
            
            logger.info("✅ Custom AGI nodes created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create custom AGI nodes: {e}")
            
    async def _create_gemini_node(self):
        """Create Gemini CLI n8n node"""
        node_dir = self.custom_nodes_dir / "src" / "nodes" / "GeminiCli"
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # Node definition
        node_code = '''
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';
import axios from 'axios';

export class GeminiCli implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Gemini CLI',
        name: 'geminiCli',
        icon: 'file:gemini.svg',
        group: ['ai'],
        version: 1,
        description: 'Interact with Gemini CLI AGI service',
        defaults: {
            name: 'Gemini CLI',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                noDataExpression: true,
                options: [
                    {
                        name: 'Chat',
                        value: 'chat',
                        description: 'Send chat message to Gemini',
                    },
                    {
                        name: 'Analyze',
                        value: 'analyze',
                        description: 'Analyze content with Gemini',
                    },
                    {
                        name: 'Generate',
                        value: 'generate',
                        description: 'Generate content with Gemini',
                    },
                ],
                default: 'chat',
            },
            {
                displayName: 'Prompt',
                name: 'prompt',
                type: 'string',
                typeOptions: {
                    rows: 4,
                },
                default: '',
                description: 'The prompt to send to Gemini',
                required: true,
            },
            {
                displayName: 'Model',
                name: 'model',
                type: 'options',
                options: [
                    {
                        name: 'Gemini Pro',
                        value: 'gemini-pro',
                    },
                    {
                        name: 'Gemini Pro Vision',
                        value: 'gemini-pro-vision',
                    },
                ],
                default: 'gemini-pro',
            },
            {
                displayName: 'Temperature',
                name: 'temperature',
                type: 'number',
                typeOptions: {
                    minValue: 0,
                    maxValue: 2,
                    numberStepSize: 0.1,
                },
                default: 0.7,
                description: 'Controls randomness in the response',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            const operation = this.getNodeParameter('operation', i) as string;
            const prompt = this.getNodeParameter('prompt', i) as string;
            const model = this.getNodeParameter('model', i) as string;
            const temperature = this.getNodeParameter('temperature', i) as number;

            try {
                const response = await axios.post('http://localhost:8015/chat', {
                    prompt,
                    model,
                    temperature,
                    operation,
                });

                returnData.push({
                    json: {
                        operation,
                        prompt,
                        model,
                        temperature,
                        response: response.data,
                        timestamp: new Date().toISOString(),
                    },
                });
            } catch (error) {
                throw new NodeOperationError(this.getNode(), `Gemini CLI request failed: ${error.message}`);
            }
        }

        return [returnData];
    }
}
'''
        
        with open(node_dir / "GeminiCli.node.ts", 'w') as f:
            f.write(node_code)
            
    async def _create_trilogy_node(self):
        """Create Trilogy AGI n8n node"""
        node_dir = self.custom_nodes_dir / "src" / "nodes" / "TrilogyAgi"
        node_dir.mkdir(parents=True, exist_ok=True)
        
        node_code = '''
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';
import axios from 'axios';

export class TrilogyAgi implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Trilogy AGI',
        name: 'trilogyAgi',
        icon: 'file:trilogy.svg',
        group: ['ai'],
        version: 1,
        description: 'Advanced AGI reasoning and autonomous agents',
        defaults: {
            name: 'Trilogy AGI',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Task Type',
                name: 'taskType',
                type: 'options',
                options: [
                    {
                        name: 'Reasoning',
                        value: 'reasoning',
                    },
                    {
                        name: 'Planning',
                        value: 'planning',
                    },
                    {
                        name: 'Execution',
                        value: 'execution',
                    },
                    {
                        name: 'Analysis',
                        value: 'analysis',
                    },
                ],
                default: 'reasoning',
            },
            {
                displayName: 'Input Data',
                name: 'inputData',
                type: 'json',
                default: '{}',
                description: 'Data to process with Trilogy AGI',
            },
            {
                displayName: 'Complexity Level',
                name: 'complexity',
                type: 'options',
                options: [
                    {
                        name: 'Simple',
                        value: 'simple',
                    },
                    {
                        name: 'Medium',
                        value: 'medium',
                    },
                    {
                        name: 'Complex',
                        value: 'complex',
                    },
                    {
                        name: 'Expert',
                        value: 'expert',
                    },
                ],
                default: 'medium',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            const taskType = this.getNodeParameter('taskType', i) as string;
            const inputData = this.getNodeParameter('inputData', i) as object;
            const complexity = this.getNodeParameter('complexity', i) as string;

            try {
                const response = await axios.post('http://localhost:8000/process', {
                    task_type: taskType,
                    input_data: inputData,
                    complexity,
                });

                returnData.push({
                    json: {
                        task_type: taskType,
                        complexity,
                        input_data: inputData,
                        result: response.data,
                        timestamp: new Date().toISOString(),
                    },
                });
            } catch (error) {
                throw new NodeOperationError(this.getNode(), `Trilogy AGI request failed: ${error.message}`);
            }
        }

        return [returnData];
    }
}
'''
        
        with open(node_dir / "TrilogyAgi.node.ts", 'w') as f:
            f.write(node_code)
            
    async def _create_memory_node(self):
        """Create Memory MCP n8n node"""
        node_dir = self.custom_nodes_dir / "src" / "nodes" / "MemoryMcp"
        node_dir.mkdir(parents=True, exist_ok=True)
        
        node_code = '''
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';
import axios from 'axios';

export class MemoryMcp implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Memory MCP',
        name: 'memoryMcp',
        icon: 'file:memory.svg',
        group: ['database'],
        version: 1,
        description: 'Knowledge graph and persistent memory operations',
        defaults: {
            name: 'Memory MCP',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                options: [
                    {
                        name: 'Store',
                        value: 'store',
                    },
                    {
                        name: 'Retrieve',
                        value: 'retrieve',
                    },
                    {
                        name: 'Search',
                        value: 'search',
                    },
                    {
                        name: 'Update',
                        value: 'update',
                    },
                ],
                default: 'store',
            },
            {
                displayName: 'Content',
                name: 'content',
                type: 'json',
                default: '{}',
                description: 'Content to store or update',
                displayOptions: {
                    show: {
                        operation: ['store', 'update'],
                    },
                },
            },
            {
                displayName: 'Query',
                name: 'query',
                type: 'string',
                default: '',
                description: 'Search query',
                displayOptions: {
                    show: {
                        operation: ['retrieve', 'search'],
                    },
                },
            },
            {
                displayName: 'Memory Type',
                name: 'memoryType',
                type: 'options',
                options: [
                    {
                        name: 'Knowledge Graph',
                        value: 'knowledge_graph',
                    },
                    {
                        name: 'Episodic',
                        value: 'episodic',
                    },
                    {
                        name: 'Semantic',
                        value: 'semantic',
                    },
                    {
                        name: 'Working',
                        value: 'working',
                    },
                ],
                default: 'knowledge_graph',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            const operation = this.getNodeParameter('operation', i) as string;
            const memoryType = this.getNodeParameter('memoryType', i) as string;
            
            let requestData: any = {
                operation,
                memory_type: memoryType,
            };
            
            if (operation === 'store' || operation === 'update') {
                requestData.content = this.getNodeParameter('content', i);
            } else if (operation === 'retrieve' || operation === 'search') {
                requestData.query = this.getNodeParameter('query', i);
            }

            try {
                const response = await axios.post(`http://localhost:3002/memory/${operation}`, requestData);

                returnData.push({
                    json: {
                        operation,
                        memory_type: memoryType,
                        request: requestData,
                        result: response.data,
                        timestamp: new Date().toISOString(),
                    },
                });
            } catch (error) {
                throw new NodeOperationError(this.getNode(), `Memory MCP request failed: ${error.message}`);
            }
        }

        return [returnData];
    }
}
'''
        
        with open(node_dir / "MemoryMcp.node.ts", 'w') as f:
            f.write(node_code)
            
    async def _create_ollama_node(self):
        """Create Ollama Local LLM n8n node"""
        node_dir = self.custom_nodes_dir / "src" / "nodes" / "OllamaLocal"
        node_dir.mkdir(parents=True, exist_ok=True)
        
        node_code = '''
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';
import axios from 'axios';

export class OllamaLocal implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Ollama Local',
        name: 'ollamaLocal',
        icon: 'file:ollama.svg',
        group: ['ai'],
        version: 1,
        description: 'Local language model processing with Ollama',
        defaults: {
            name: 'Ollama Local',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Model',
                name: 'model',
                type: 'string',
                default: 'llama2',
                description: 'Ollama model to use',
                required: true,
            },
            {
                displayName: 'Prompt',
                name: 'prompt',
                type: 'string',
                typeOptions: {
                    rows: 4,
                },
                default: '',
                description: 'The prompt to send to the model',
                required: true,
            },
            {
                displayName: 'Temperature',
                name: 'temperature',
                type: 'number',
                typeOptions: {
                    minValue: 0,
                    maxValue: 2,
                    numberStepSize: 0.1,
                },
                default: 0.7,
            },
            {
                displayName: 'Max Tokens',
                name: 'maxTokens',
                type: 'number',
                typeOptions: {
                    minValue: 1,
                    maxValue: 4096,
                },
                default: 256,
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            const model = this.getNodeParameter('model', i) as string;
            const prompt = this.getNodeParameter('prompt', i) as string;
            const temperature = this.getNodeParameter('temperature', i) as number;
            const maxTokens = this.getNodeParameter('maxTokens', i) as number;

            try {
                const response = await axios.post('http://localhost:11434/api/generate', {
                    model,
                    prompt,
                    stream: false,
                    options: {
                        temperature,
                        num_predict: maxTokens,
                    },
                });

                returnData.push({
                    json: {
                        model,
                        prompt,
                        temperature,
                        max_tokens: maxTokens,
                        response: response.data.response,
                        context: response.data.context,
                        timestamp: new Date().toISOString(),
                    },
                });
            } catch (error) {
                throw new NodeOperationError(this.getNode(), `Ollama request failed: ${error.message}`);
            }
        }

        return [returnData];
    }
}
'''
        
        with open(node_dir / "OllamaLocal.node.ts", 'w') as f:
            f.write(node_code)
            
    async def _create_deerflow_node(self):
        """Create DeerFlow orchestration n8n node"""
        node_dir = self.custom_nodes_dir / "src" / "nodes" / "DeerFlow"
        node_dir.mkdir(parents=True, exist_ok=True)
        
        node_code = '''
import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';
import axios from 'axios';

export class DeerFlow implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'DeerFlow',
        name: 'deerFlow',
        icon: 'file:deerflow.svg',
        group: ['workflow'],
        version: 1,
        description: 'Adaptive workflow management and optimization',
        defaults: {
            name: 'DeerFlow',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            {
                displayName: 'Action',
                name: 'action',
                type: 'options',
                options: [
                    {
                        name: 'Create Workflow',
                        value: 'create_workflow',
                    },
                    {
                        name: 'Execute Workflow',
                        value: 'execute_workflow',
                    },
                    {
                        name: 'Optimize',
                        value: 'optimize',
                    },
                    {
                        name: 'Monitor',
                        value: 'monitor',
                    },
                ],
                default: 'optimize',
            },
            {
                displayName: 'Workflow Data',
                name: 'workflowData',
                type: 'json',
                default: '{}',
                description: 'Workflow configuration or data',
            },
            {
                displayName: 'Optimization Target',
                name: 'optimizationTarget',
                type: 'options',
                options: [
                    {
                        name: 'Performance',
                        value: 'performance',
                    },
                    {
                        name: 'Efficiency',
                        value: 'efficiency',
                    },
                    {
                        name: 'Quality',
                        value: 'quality',
                    },
                    {
                        name: 'Resource Usage',
                        value: 'resource_usage',
                    },
                ],
                default: 'performance',
                displayOptions: {
                    show: {
                        action: ['optimize'],
                    },
                },
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        for (let i = 0; i < items.length; i++) {
            const action = this.getNodeParameter('action', i) as string;
            const workflowData = this.getNodeParameter('workflowData', i) as object;
            
            let requestData: any = {
                action,
                workflow_data: workflowData,
            };
            
            if (action === 'optimize') {
                requestData.optimization_target = this.getNodeParameter('optimizationTarget', i);
            }

            try {
                const response = await axios.post(`http://localhost:8014/deerflow/${action}`, requestData);

                returnData.push({
                    json: {
                        action,
                        workflow_data: workflowData,
                        result: response.data,
                        timestamp: new Date().toISOString(),
                    },
                });
            } catch (error) {
                throw new NodeOperationError(this.getNode(), `DeerFlow request failed: ${error.message}`);
            }
        }

        return [returnData];
    }
}
'''
        
        with open(node_dir / "DeerFlow.node.ts", 'w') as f:
            f.write(node_code)
            
    async def _setup_environment_variables(self):
        """Set up environment variables for n8n"""
        env_vars = {
            "N8N_BASIC_AUTH_ACTIVE": "false",
            "N8N_HOST": "localhost",
            "N8N_PORT": str(self.n8n_port),
            "N8N_PROTOCOL": "http",
            "WEBHOOK_URL": f"http://localhost:{self.n8n_port}/",
            "GENERIC_TIMEZONE": "UTC",
            "N8N_CUSTOM_EXTENSIONS": str(self.custom_nodes_dir.absolute()),
            "N8N_USER_FOLDER": str(self.n8n_data_dir.absolute())
        }
        
        # Write environment file
        env_file = self.base_dir / ".env"
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
                
        logger.info("✅ Environment variables configured")
        
    async def start_n8n(self) -> bool:
        """Start n8n server"""
        try:
            logger.info("🚀 Starting n8n server...")
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "N8N_BASIC_AUTH_ACTIVE": "false",
                "N8N_HOST": "localhost",
                "N8N_PORT": str(self.n8n_port),
                "N8N_PROTOCOL": "http",
                "WEBHOOK_URL": f"http://localhost:{self.n8n_port}/",
                "N8N_USER_FOLDER": str(self.n8n_data_dir.absolute())
            })
            
            # Try direct n8n start
            try:
                self.n8n_process = subprocess.Popen(
                    ["n8n", "start"],
                    env=env,
                    cwd=str(self.base_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait a bit to see if it starts successfully
                await asyncio.sleep(3)
                
                if self.n8n_process.poll() is None:
                    logger.info(f"✅ n8n started successfully on port {self.n8n_port}")
                    return True
                else:
                    raise Exception("n8n process terminated")
                    
            except Exception as e:
                logger.warning(f"Direct n8n start failed: {e}")
                return await self._start_n8n_docker()
                
        except Exception as e:
            logger.error(f"❌ Failed to start n8n: {e}")
            return False
            
    async def _start_n8n_docker(self) -> bool:
        """Start n8n using Docker"""
        try:
            logger.info("🐳 Starting n8n with Docker...")
            
            docker_compose_file = self.base_dir / "docker-compose.yml"
            if not docker_compose_file.exists():
                logger.error("Docker Compose file not found")
                return False
                
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ n8n started with Docker")
                return True
            else:
                logger.error(f"Docker Compose failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Docker start failed: {e}")
            return False
            
    async def stop_n8n(self):
        """Stop n8n server"""
        try:
            if self.n8n_process:
                self.n8n_process.terminate()
                await asyncio.sleep(2)
                if self.n8n_process.poll() is None:
                    self.n8n_process.kill()
                logger.info("✅ n8n process stopped")
                
            # Also try to stop Docker if running
            try:
                subprocess.run(
                    ["docker-compose", "down"],
                    cwd=str(self.base_dir),
                    capture_output=True
                )
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Failed to stop n8n: {e}")
            
    async def create_agi_workflow_templates(self):
        """Create AGI workflow templates"""
        try:
            logger.info("📋 Creating AGI workflow templates...")
            
            templates = [
                {
                    "name": "AGI Code Analysis Pipeline",
                    "description": "Automated code analysis using Gemini and Memory MCP",
                    "workflow": {
                        "nodes": [
                            {
                                "name": "Webhook Trigger",
                                "type": "n8n-nodes-base.webhook",
                                "position": [250, 300],
                                "parameters": {
                                    "httpMethod": "POST",
                                    "path": "code-analysis"
                                }
                            },
                            {
                                "name": "Gemini Analysis",
                                "type": "geminiCli",
                                "position": [450, 300],
                                "parameters": {
                                    "operation": "analyze",
                                    "prompt": "Analyze this code for quality, security, and optimization opportunities: {{$json['code']}}",
                                    "model": "gemini-pro"
                                }
                            },
                            {
                                "name": "Store Results",
                                "type": "memoryMcp",
                                "position": [650, 300],
                                "parameters": {
                                    "operation": "store",
                                    "content": "{{$json}}",
                                    "memoryType": "knowledge_graph"
                                }
                            }
                        ],
                        "connections": {
                            "Webhook Trigger": {
                                "main": [["Gemini Analysis"]]
                            },
                            "Gemini Analysis": {
                                "main": [["Store Results"]]
                            }
                        }
                    }
                },
                {
                    "name": "Multi-Modal AGI Processing",
                    "description": "Complex multi-modal processing using full AGI stack",
                    "workflow": {
                        "nodes": [
                            {
                                "name": "Manual Trigger",
                                "type": "n8n-nodes-base.manualTrigger",
                                "position": [250, 300]
                            },
                            {
                                "name": "Trilogy AGI Reasoning",
                                "type": "trilogyAgi",
                                "position": [450, 200],
                                "parameters": {
                                    "taskType": "reasoning",
                                    "complexity": "complex"
                                }
                            },
                            {
                                "name": "DeerFlow Optimization",
                                "type": "deerFlow",
                                "position": [450, 400],
                                "parameters": {
                                    "action": "optimize",
                                    "optimizationTarget": "performance"
                                }
                            },
                            {
                                "name": "Ollama Processing",
                                "type": "ollamaLocal",
                                "position": [650, 300],
                                "parameters": {
                                    "model": "llama2",
                                    "prompt": "Synthesize insights from: {{$json}}"
                                }
                            },
                            {
                                "name": "Memory Storage",
                                "type": "memoryMcp",
                                "position": [850, 300],
                                "parameters": {
                                    "operation": "store",
                                    "memoryType": "semantic"
                                }
                            }
                        ],
                        "connections": {
                            "Manual Trigger": {
                                "main": [["Trilogy AGI Reasoning", "DeerFlow Optimization"]]
                            },
                            "Trilogy AGI Reasoning": {
                                "main": [["Ollama Processing"]]
                            },
                            "DeerFlow Optimization": {
                                "main": [["Ollama Processing"]]
                            },
                            "Ollama Processing": {
                                "main": [["Memory Storage"]]
                            }
                        }
                    }
                }
            ]
            
            for template in templates:
                template_file = self.workflows_dir / "templates" / f"{template['name'].lower().replace(' ', '_')}.json"
                with open(template_file, 'w') as f:
                    json.dump(template, f, indent=2)
                    
            logger.info(f"✅ Created {len(templates)} workflow templates")
            
        except Exception as e:
            logger.error(f"❌ Failed to create workflow templates: {e}")
            
    async def install_custom_nodes(self):
        """Install custom AGI nodes"""
        try:
            logger.info("📦 Installing custom AGI nodes...")
            
            # Build TypeScript nodes
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(self.custom_nodes_dir),
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                logger.warning(f"npm install warning: {result.stderr}")
                
            # Build TypeScript
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(self.custom_nodes_dir),
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Custom AGI nodes built successfully")
            else:
                logger.warning(f"Build warning: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Failed to install custom nodes: {e}")
            
    async def check_n8n_health(self) -> bool:
        """Check if n8n is running and healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{self.n8n_port}/api/v1/health") as response:
                    if response.status == 200:
                        logger.info("✅ n8n is healthy")
                        return True
                    else:
                        logger.warning(f"n8n health check failed: {response.status}")
                        return False
        except Exception as e:
            logger.warning(f"n8n health check failed: {e}")
            return False
            
    async def get_status(self) -> Dict[str, Any]:
        """Get n8n integration status"""
        is_healthy = await self.check_n8n_health()
        
        return {
            "n8n_running": is_healthy,
            "n8n_port": self.n8n_port,
            "n8n_url": f"http://localhost:{self.n8n_port}",
            "custom_nodes_installed": (self.custom_nodes_dir / "dist").exists(),
            "workflow_templates": len(list((self.workflows_dir / "templates").glob("*.json"))),
            "agi_endpoints": self.agi_endpoints,
            "directories": {
                "base": str(self.base_dir),
                "data": str(self.n8n_data_dir),
                "config": str(self.n8n_config_dir),
                "custom_nodes": str(self.custom_nodes_dir),
                "workflows": str(self.workflows_dir)
            }
        }


async def main():
    """Main function to setup and start n8n integration"""
    manager = N8NManager()
    
    # Setup environment
    if await manager.setup_n8n_environment():
        logger.info("✅ n8n environment setup complete")
        
        # Install custom nodes
        await manager.install_custom_nodes()
        
        # Create workflow templates
        await manager.create_agi_workflow_templates()
        
        # Start n8n
        if await manager.start_n8n():
            logger.info("✅ n8n started successfully")
            
            # Wait a bit for n8n to fully start
            await asyncio.sleep(5)
            
            # Check health
            await manager.check_n8n_health()
            
            # Print status
            status = await manager.get_status()
            print(f"\n📊 n8n Integration Status:")
            print(f"   n8n URL: {status['n8n_url']}")
            print(f"   Custom Nodes: {status['custom_nodes_installed']}")
            print(f"   Templates: {status['workflow_templates']}")
            print(f"   AGI Services: {len(status['agi_endpoints'])}")
            
        else:
            logger.error("❌ Failed to start n8n")
    else:
        logger.error("❌ Failed to setup n8n environment")


if __name__ == "__main__":
    asyncio.run(main())
