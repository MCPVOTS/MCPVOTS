
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
