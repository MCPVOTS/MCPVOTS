/**
 * MCP Context Provider
 * Manages MCP connections, servers, and protocol state across the React application
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { MCPIntegrationService } from '../mcp-service';
import type { MCPServer, SystemStats, PerformanceMetrics, LogEntry } from '../components';

export interface MCPState {
  servers: MCPServer[];
  systemStats: SystemStats;
  performanceMetrics: PerformanceMetrics;
  logs: LogEntry[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  activeConnections: number;
}

export type MCPAction =
  | { type: 'SET_SERVERS'; payload: MCPServer[] }
  | { type: 'UPDATE_SERVER'; payload: { index: number; server: Partial<MCPServer> } }
  | { type: 'SET_SYSTEM_STATS'; payload: SystemStats }
  | { type: 'SET_PERFORMANCE_METRICS'; payload: PerformanceMetrics }
  | { type: 'ADD_LOG'; payload: LogEntry }
  | { type: 'CLEAR_LOGS' }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_ACTIVE_CONNECTIONS'; payload: number };

const initialState: MCPState = {
  servers: [],
  systemStats: {
    activeConnections: 0,
    memoryUsage: 0,
    uptime: 0,
    messagesProcessed: 0,
    errorCount: 0,
    lastActivity: Date.now(),
  },
  performanceMetrics: {
    responseTime: [],
    throughput: 0,
    errorRate: 0,
    latency: 0,
    bandwidth: 0,
  },
  logs: [],
  isConnected: false,
  isLoading: false,
  error: null,
  activeConnections: 0,
};

function mcpReducer(state: MCPState, action: MCPAction): MCPState {
  switch (action.type) {
    case 'SET_SERVERS':
      return { ...state, servers: action.payload };
    case 'UPDATE_SERVER':
      return {
        ...state,
        servers: state.servers.map((server, index) =>
          index === action.payload.index ? { ...server, ...action.payload.server } : server
        ),
      };
    case 'SET_SYSTEM_STATS':
      return { ...state, systemStats: action.payload };
    case 'SET_PERFORMANCE_METRICS':
      return { ...state, performanceMetrics: action.payload };
    case 'ADD_LOG':
      return {
        ...state,
        logs: [action.payload, ...state.logs].slice(0, 1000), // Keep last 1000 logs
      };
    case 'CLEAR_LOGS':
      return { ...state, logs: [] };
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_ACTIVE_CONNECTIONS':
      return { ...state, activeConnections: action.payload };
    default:
      return state;
  }
}

export interface MCPContextType {
  state: MCPState;
  dispatch: React.Dispatch<MCPAction>;
  mcpService: MCPIntegrationService | null;
  connectServer: (serverConfig: Partial<MCPServer>) => Promise<void>;
  disconnectServer: (serverIndex: number) => Promise<void>;
  sendMessage: (serverIndex: number, message: any) => Promise<any>;
  refreshServers: () => Promise<void>;
  toggleServer: (serverIndex: number) => Promise<void>;
  clearLogs: () => void;
  exportMetrics: () => void;
}

const MCPContext = createContext<MCPContextType | undefined>(undefined);

export interface MCPProviderProps {
  children: ReactNode;
}

export function MCPProvider({ children }: MCPProviderProps) {
  const [state, dispatch] = useReducer(mcpReducer, initialState);
  const [mcpService, setMcpService] = React.useState<MCPIntegrationService | null>(null);

  // Initialize MCP Service
  useEffect(() => {
    const service = new MCPIntegrationService({
      advanced: {
        heartbeatInterval: 30000,
        maxReconnectAttempts: 5,
        connectionTimeout: 10000
      }
    });
    setMcpService(service);

    // Set up event listeners
    service.on('serverUpdate', (servers: MCPServer[]) => {
      dispatch({ type: 'SET_SERVERS', payload: servers });
    });

    service.on('statsUpdate', (stats: SystemStats) => {
      dispatch({ type: 'SET_SYSTEM_STATS', payload: stats });
    });

    service.on('logEntry', (log: LogEntry) => {
      dispatch({ type: 'ADD_LOG', payload: log });
    });

    service.on('connectionChange', (connected: boolean) => {
      dispatch({ type: 'SET_CONNECTED', payload: connected });
    });

    service.on('error', (error: string) => {
      dispatch({ type: 'SET_ERROR', payload: error });
    });

    // Initialize service
    service.initialize().catch((error) => {
      console.error('Failed to initialize MCP service:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    });

    return () => {
      service.destroy();
    };
  }, []);

  const connectServer = async (serverConfig: Partial<MCPServer>) => {
    if (!mcpService) return;
    
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      await mcpService.connectServer(serverConfig);
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: (error as Error).message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const disconnectServer = async (serverIndex: number) => {
    if (!mcpService) return;
    
    try {
      await mcpService.disconnectServer(serverIndex);
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: (error as Error).message });
    }
  };

  const sendMessage = async (serverIndex: number, message: any) => {
    if (!mcpService) throw new Error('MCP service not initialized');
    
    return await mcpService.sendMessage(serverIndex, message);
  };

  const refreshServers = async () => {
    if (!mcpService) return;
    
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      await mcpService.refreshServers();
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: (error as Error).message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const toggleServer = async (serverIndex: number) => {
    if (!mcpService) return;
    
    try {
      await mcpService.toggleServer(serverIndex);
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: (error as Error).message });
    }
  };

  const clearLogs = () => {
    dispatch({ type: 'CLEAR_LOGS' });
  };

  const exportMetrics = () => {
    if (!mcpService) return;
    
    const data = {
      timestamp: new Date().toISOString(),
      systemStats: state.systemStats,
      performanceMetrics: state.performanceMetrics,
      servers: state.servers,
      logs: state.logs.slice(0, 100), // Export last 100 logs
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mcpvots-metrics-${new Date().toISOString().slice(0, 19)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const value: MCPContextType = {
    state,
    dispatch,
    mcpService,
    connectServer,
    disconnectServer,
    sendMessage,
    refreshServers,
    toggleServer,
    clearLogs,
    exportMetrics,
  };

  return <MCPContext.Provider value={value}>{children}</MCPContext.Provider>;
}

export function useMCP() {
  const context = useContext(MCPContext);
  if (context === undefined) {
    throw new Error('useMCP must be used within a MCPProvider');
  }
  return context;
}
