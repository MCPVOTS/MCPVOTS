
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
