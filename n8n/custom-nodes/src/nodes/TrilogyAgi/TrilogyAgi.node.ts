
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
