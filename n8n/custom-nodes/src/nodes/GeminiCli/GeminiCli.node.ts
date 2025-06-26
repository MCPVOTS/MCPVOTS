
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
