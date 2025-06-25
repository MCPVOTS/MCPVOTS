import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mcpClient } from './mcp/client';

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Generic API fetch function
async function apiFetch(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// System Status Hook
export const useSystemStatus = () => {
  return useQuery({
    queryKey: ['systemStatus'],
    queryFn: async () => {
      try {
        return await apiFetch('/health');
      } catch {
        // Fallback for when backend isn't running
        return {
          status: 'offline',
          timestamp: new Date().toISOString(),
          services: {
            'mcp-gateway': 'offline',
            'trilogy-core': 'offline',
            'orchestrator': 'offline'
          }
        };
      }
    },
    refetchInterval: 5000,
    retry: 1,
  });
};

// MCP Metrics Hook
export const useMCPMetrics = () => {
  return useQuery({
    queryKey: ['mcpMetrics'],
    queryFn: async () => {
      if (mcpClient.isConnected()) {
        return mcpClient.getMetrics();
      } else {
        // Return default metrics if not connected
        return {
          totalRequests: 0,
          successRate: 0,
          averageResponseTime: 0,
          activeConnections: 0,
          lastUpdated: new Date().toISOString()
        };
      }
    },
    refetchInterval: 2000,
  });
};

// Trilogy Services Status Hook
export const useTrilogyServices = () => {
  return useQuery({
    queryKey: ['trilogyServices'],
    queryFn: async () => {
      const services = [];
      const ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007];
      
      for (const port of ports) {
        try {
          const response = await fetch(`http://localhost:${port}/health`, {
            signal: AbortSignal.timeout(2000)
          });
          
          if (response.ok) {
            const data = await response.json();
            services.push({
              name: `Service-${port}`,
              port,
              status: 'healthy',
              lastCheck: new Date().toISOString(),
              ...data
            });
          } else {
            services.push({
              name: `Service-${port}`,
              port,
              status: 'unhealthy',
              lastCheck: new Date().toISOString()
            });
          }
        } catch {
          services.push({
            name: `Service-${port}`,
            port,
            status: 'offline',
            lastCheck: new Date().toISOString()
          });
        }
      }
      
      return services;
    },
    refetchInterval: 10000,
    retry: 1,
  });
};

// MCP Connection Mutation
export const useMCPConnection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (action: 'connect' | 'disconnect') => {
      if (action === 'connect') {
        await mcpClient.connect();
        await mcpClient.initialize();
        return { status: 'connected' };
      } else {
        mcpClient.disconnect();
        return { status: 'disconnected' };
      }
    },
    onSuccess: () => {
      // Invalidate and refetch metrics after connection change
      queryClient.invalidateQueries({ queryKey: ['mcpMetrics'] });
    },
  });
};

// Execute MCP Tool Mutation
export const useExecuteTool = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ toolName, arguments: args }: { toolName: string; arguments: any }) => {
      if (!mcpClient.isConnected()) {
        throw new Error('MCP client not connected');
      }
      
      return await mcpClient.callTool(toolName, args);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mcpMetrics'] });
    },
  });
};

// Get Available Tools Hook
export const useAvailableTools = () => {
  return useQuery({
    queryKey: ['availableTools'],
    queryFn: async () => {
      if (mcpClient.isConnected()) {
        try {
          return await mcpClient.listTools();
        } catch {
          return { tools: [] };
        }
      }
      return { tools: [] };
    },
    enabled: mcpClient.isConnected(),
    refetchInterval: 30000,
  });
};

// Get Available Resources Hook
export const useAvailableResources = () => {
  return useQuery({
    queryKey: ['availableResources'],
    queryFn: async () => {
      if (mcpClient.isConnected()) {
        try {
          return await mcpClient.listResources();
        } catch {
          return { resources: [] };
        }
      }
      return { resources: [] };
    },
    enabled: mcpClient.isConnected(),
    refetchInterval: 30000,
  });
};

// Ecosystem Metrics Hook
export const useEcosystemMetrics = () => {
  return useQuery({
    queryKey: ['ecosystemMetrics'],
    queryFn: async () => {
      try {
        return await apiFetch('/api/metrics');
      } catch {
        // Return mock data when API is unavailable
        return {
          totalRequests: Math.floor(Math.random() * 1000),
          activeUsers: Math.floor(Math.random() * 50),
          uptime: '99.9%',
          responseTime: Math.floor(Math.random() * 100) + 'ms',
          lastUpdated: new Date().toISOString()
        };
      }
    },
    refetchInterval: 15000,
  });
};
