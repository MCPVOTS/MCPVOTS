
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
