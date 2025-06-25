/**
 * Gemini CLI Integration Component for MCPVots
 */

import * as React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

interface GeminiModel {
  name: string;
  capabilities: string[];
  context_window: number;
  description: string;
}

export function GeminiCLIDashboard() {
  const [isConnected, setIsConnected] = React.useState(false);
  const [models, setModels] = React.useState<Record<string, GeminiModel>>({});
  const [selectedModel, setSelectedModel] = React.useState<string>('gemini-1.5-flash');
  const [prompt, setPrompt] = React.useState<string>('');
  const [response, setResponse] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [conversationId, setConversationId] = React.useState<string>('');
  const [healthStatus, setHealthStatus] = React.useState<'healthy' | 'unhealthy' | 'unknown'>('unknown');
  const { toast } = useToast();

  // WebSocket connection
  const [ws, setWs] = React.useState<WebSocket | null>(null);

  React.useEffect(() => {
    connectToGemini();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const connectToGemini = async () => {
    try {
      const websocket = new WebSocket('ws://localhost:8015');
      
      websocket.onopen = () => {
        console.log('Connected to Gemini CLI MCP Server');
        setIsConnected(true);
        setWs(websocket);
        
        // Initialize the service
        sendMessage('initialize', {});
        
        // Load available models
        sendMessage('gemini/list_models', {});
        
        // Check health
        sendMessage('gemini/health', {});
        
        toast({
          title: 'Gemini CLI Connected',
          description: 'Successfully connected to Google Gemini AI',
          variant: 'success'
        });
      };
      
      websocket.onmessage = (event) => {
        handleMessage(JSON.parse(event.data));
      };
      
      websocket.onclose = () => {
        console.log('Disconnected from Gemini CLI MCP Server');
        setIsConnected(false);
        setWs(null);
        
        toast({
          title: 'Gemini CLI Disconnected',
          description: 'Connection to Gemini AI lost',
          variant: 'destructive'
        });
      };
      
      websocket.onerror = (error) => {
        console.error('Gemini CLI WebSocket error:', error);
        toast({
          title: 'Connection Error',
          description: 'Failed to connect to Gemini CLI service',
          variant: 'destructive'
        });
      };
      
    } catch (error) {
      console.error('Failed to connect to Gemini CLI:', error);
      toast({
        title: 'Connection Failed',
        description: 'Could not establish connection to Gemini CLI',
        variant: 'destructive'
      });
    }
  };

  const sendMessage = (method: string, params: any) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    const message = {
      jsonrpc: '2.0',
      id: Date.now().toString(),
      method,
      params
    };

    ws.send(JSON.stringify(message));
  };

  const handleMessage = (data: any) => {
    if (data.error) {
      console.error('Gemini CLI error:', data.error);
      toast({
        title: 'Gemini Error',
        description: data.error.message,
        variant: 'destructive'
      });
      setIsLoading(false);
      return;
    }

    if (!data.result) return;

    const result = data.result;

    // Handle different response types
    if (result.models) {
      setModels(result.models);
    }
    
    if (result.response) {
      setResponse(result.response);
      setIsLoading(false);
    }
    
    if (result.generated_text) {
      setResponse(result.generated_text);
      setIsLoading(false);
    }
    
    if (result.analysis) {
      setResponse(result.analysis);
      setIsLoading(false);
    }
    
    if (result.status) {
      setHealthStatus(result.status);
    }
    
    if (result.session_id) {
      setConversationId(result.session_id);
    }
    
    if (result.assistant_response) {
      setResponse(result.assistant_response);
      setIsLoading(false);
    }
  };

  const handleChat = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    setResponse('');
    
    if (conversationId) {
      // Continue existing conversation
      sendMessage('gemini/continue_conversation', {
        session_id: conversationId,
        message: prompt
      });
    } else {
      // Simple chat
      sendMessage('gemini/chat', {
        message: prompt,
        model: selectedModel
      });
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    setResponse('');
    
    sendMessage('gemini/generate', {
      prompt: prompt,
      model: selectedModel,
      max_tokens: 1000,
      temperature: 0.7
    });
  };

  const startConversation = () => {
    sendMessage('gemini/start_conversation', {
      model: selectedModel,
      system_prompt: 'You are a helpful AI assistant integrated into the MCPVots ecosystem.'
    });
    
    toast({
      title: 'Conversation Started',
      description: 'New conversation session created with Gemini',
      variant: 'success'
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            Google Gemini CLI Integration
            <Badge variant={healthStatus === 'healthy' ? 'default' : 'destructive'}>
              {healthStatus}
            </Badge>
          </CardTitle>
          <CardDescription>
            Access Google's Gemini AI models through the official CLI integration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Button
              onClick={connectToGemini}
              disabled={isConnected}
              variant="outline"
            >
              {isConnected ? 'Connected' : 'Connect'}
            </Button>
            <Button
              onClick={startConversation}
              disabled={!isConnected}
              variant="outline"
            >
              Start Conversation
            </Button>
            {conversationId && (
              <Badge variant="outline">
                Session: {conversationId.slice(-8)}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available Models</CardTitle>
          <CardDescription>
            Choose from Google's latest Gemini models
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(models).map(([modelId, model]) => (
              <Card 
                key={modelId}
                className={`cursor-pointer transition-colors ${
                  selectedModel === modelId ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedModel(modelId)}
              >
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">{model.name}</CardTitle>
                  <CardDescription className="text-xs">
                    {model.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex flex-wrap gap-1 mb-2">
                    {model.capabilities.map((cap) => (
                      <Badge key={cap} variant="secondary" className="text-xs">
                        {cap}
                      </Badge>
                    ))}
                  </div>
                  <div className="text-xs text-gray-600">
                    Context: {model.context_window.toLocaleString()} tokens
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Chat with Gemini</CardTitle>
          <CardDescription>
            Send messages to {models[selectedModel]?.name || selectedModel}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your message or prompt..."
              className="w-full h-32 p-3 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={!isConnected}
            />
            
            <div className="flex gap-2">
              <Button
                onClick={handleChat}
                disabled={!isConnected || isLoading || !prompt.trim()}
                className="flex-1"
              >
                {isLoading ? 'Sending...' : 'Chat'}
              </Button>
              <Button
                onClick={handleGenerate}
                disabled={!isConnected || isLoading || !prompt.trim()}
                variant="outline"
                className="flex-1"
              >
                {isLoading ? 'Generating...' : 'Generate'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {response && (
        <Card>
          <CardHeader>
            <CardTitle>Gemini Response</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-md">
              <pre className="whitespace-pre-wrap text-sm">{response}</pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
