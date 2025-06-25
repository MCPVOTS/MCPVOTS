/**
 * Trilogy AGI Dashboard Component
 * Main dashboard showcasing the complete AGI ecosystem and its value to MCP
 */

import React, { useState, useEffect } from 'react';
import { trilogyService } from '../services/trilogy-mcp-service';
import { MCP_VALUE_PROPOSITION, BLOCKCHAIN_FEATURES } from '../services/trilogy-overview';

interface DashboardProps {
  className?: string;
}

export const TrilogyAGIDashboard: React.FC<DashboardProps> = ({ className = '' }) => {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Subscribe to system updates
    const unsubscribe = trilogyService.subscribe((status: any) => {
      setSystemStatus(status);
      setIsLoading(false);
    });

    return unsubscribe;
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400';
      case 'offline': return 'text-red-400';
      case 'starting': return 'text-yellow-400';
      case 'error': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusEmoji = (status: string) => {
    switch (status) {
      case 'online': return '🟢';
      case 'offline': return '🔴';
      case 'starting': return '🟡';
      case 'error': return '🟠';
      default: return '⚪';
    }
  };

  if (isLoading) {
    return (
      <div className={`bg-dark-secondary-bg rounded-xl border border-dark-border p-8 ${className}`}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
          <span className="ml-4 text-dark-text">Loading Trilogy AGI System...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-dark-secondary-bg rounded-xl border border-dark-border ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-dark-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-dark-text flex items-center">
              🧠 Trilogy AGI System
              <span className="ml-3 px-3 py-1 bg-gradient-to-r from-accent-primary to-accent-purple text-white text-sm rounded-full">
                Live
              </span>
            </h2>
            <p className="text-dark-secondary-text mt-1">
              Advanced AGI ecosystem with Darwin Gödel Machine evolution
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-accent-secondary font-mono text-xl">
                {systemStatus?.metrics.online_services || 0}/{systemStatus?.metrics.total_services || 8}
              </div>
              <div className="text-dark-secondary-text text-sm">Services Online</div>
            </div>
            
            <div className="text-right">
              <div className="text-accent-primary font-mono text-xl">
                {Math.round(systemStatus?.health_overview.overall_health || 0)}%
              </div>
              <div className="text-dark-secondary-text text-sm">System Health</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mt-6 bg-dark-bg rounded-lg p-1">
          {[
            { id: 'overview', label: '🏠 Overview', icon: '🏠' },
            { id: 'services', label: '🔧 Services', icon: '🔧' },
            { id: 'blockchain', label: '⛓️ Blockchain', icon: '⛓️' },
            { id: 'value', label: '💎 Value Prop', icon: '💎' },
            { id: 'demo', label: '🚀 Demo', icon: '🚀' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-accent-primary text-white'
                  : 'text-dark-secondary-text hover:text-dark-text hover:bg-dark-hover-bg'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-accent-primary text-2xl font-mono">
                  {systemStatus?.metrics.success_rate.toFixed(1) || '0.0'}%
                </div>
                <div className="text-dark-secondary-text text-sm">Success Rate</div>
              </div>
              
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-accent-secondary text-2xl font-mono">
                  {systemStatus?.metrics.average_response_time.toFixed(0) || '0'}ms
                </div>
                <div className="text-dark-secondary-text text-sm">Avg Response</div>
              </div>
              
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-accent-warning text-2xl font-mono">
                  ${systemStatus?.metrics.cost_savings.toFixed(2) || '0.00'}
                </div>
                <div className="text-dark-secondary-text text-sm">Cost Savings</div>
              </div>
              
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-accent-cyan text-2xl font-mono">
                  {systemStatus?.metrics.ai_improvements || 0}
                </div>
                <div className="text-dark-secondary-text text-sm">AI Improvements</div>
              </div>
            </div>

            {/* Architecture Overview */}
            <div className="bg-dark-bg rounded-lg p-6">
              <h3 className="text-lg font-semibold text-dark-text mb-4">🏗️ Architecture Overview</h3>
              <div className="text-dark-secondary-text space-y-2">
                <div>🧠 <strong>DeepSeek R1 + DGM:</strong> Advanced reasoning with evolutionary code optimization</div>
                <div>🔄 <strong>DSPy Autonomous:</strong> Self-improving prompt engineering and optimization</div>
                <div>💾 <strong>RL Memory:</strong> Reinforcement learning with episodic memory storage</div>
                <div>🎭 <strong>Jenova Orchestrator:</strong> Multi-agent coordination and resource allocation</div>
                <div>⛓️ <strong>Blockchain Integration:</strong> Solana + Base L2 for decentralized compute</div>
                <div>🔧 <strong>Autonomous Ops:</strong> Self-healing and adaptive system management</div>
              </div>
            </div>

            {/* Value Proposition Preview */}
            <div className="bg-gradient-to-r from-accent-primary/20 to-accent-purple/20 rounded-lg p-6 border border-accent-primary/30">
              <h3 className="text-lg font-semibold text-dark-text mb-3">💎 Value for MCP Ecosystem</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-accent-primary font-medium">For Developers:</div>
                  <div className="text-dark-secondary-text">Advanced AGI capabilities at fractional cost</div>
                </div>
                <div>
                  <div className="text-accent-secondary font-medium">For Enterprises:</div>
                  <div className="text-dark-secondary-text">Scalable AI infrastructure without massive costs</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-dark-text">🔧 Core Services Status</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {systemStatus?.services.map((service: any) => (
                <div
                  key={service.service_name}
                  className={`bg-dark-bg rounded-lg p-4 border cursor-pointer transition-colors ${
                    selectedService === service.service_name
                      ? 'border-accent-primary'
                      : 'border-dark-border hover:border-dark-hover-border'
                  }`}
                  onClick={() => setSelectedService(
                    selectedService === service.service_name ? null : service.service_name
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <span className="mr-2">{getStatusEmoji(service.status)}</span>
                      <span className="font-medium text-dark-text">
                        {service.service_name.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <span className="text-dark-secondary-text text-sm">:{service.port}</span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
                      {service.status.toUpperCase()}
                    </span>
                    <span className="text-dark-secondary-text text-sm">
                      {service.response_time}ms
                    </span>
                  </div>
                  
                  <div className="w-full bg-dark-border rounded-full h-1">
                    <div
                      className="bg-accent-primary h-1 rounded-full transition-all"
                      style={{ width: `${service.health_score}%` }}
                    ></div>
                  </div>
                  
                  {selectedService === service.service_name && (
                    <div className="mt-4 pt-4 border-t border-dark-border">
                      <div className="text-sm text-dark-secondary-text space-y-1">
                        <div><strong>Capabilities:</strong></div>
                        {service.capabilities.slice(0, 3).map((cap: string, i: number) => (
                          <div key={i} className="ml-2">• {cap}</div>
                        ))}
                        {service.capabilities.length > 3 && (
                          <div className="ml-2 text-accent-primary">
                            +{service.capabilities.length - 3} more...
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'blockchain' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-dark-text">⛓️ Blockchain Integration</h3>
            
            {/* Solana Integration */}
            <div className="bg-dark-bg rounded-lg p-6">
              <h4 className="text-accent-purple font-semibold mb-4 flex items-center">
                <span className="mr-2">🔮</span> Solana Network
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(BLOCKCHAIN_FEATURES.solana_integration).map(([key, feature]) => (
                  <div key={key} className="border border-dark-border rounded-lg p-4">
                    <h5 className="font-medium text-dark-text mb-2">
                      {feature.description}
                    </h5>
                    <div className="text-sm text-dark-secondary-text space-y-1">
                      {feature.features.map((f: string, i: number) => (
                        <div key={i}>• {f}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Base L2 Integration */}
            <div className="bg-dark-bg rounded-lg p-6">
              <h4 className="text-accent-cyan font-semibold mb-4 flex items-center">
                <span className="mr-2">🌊</span> Base Layer 2
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(BLOCKCHAIN_FEATURES.base_l2_integration).map(([key, feature]) => (
                  <div key={key} className="border border-dark-border rounded-lg p-4">
                    <h5 className="font-medium text-dark-text mb-2">
                      {feature.description}
                    </h5>
                    <div className="text-sm text-dark-secondary-text space-y-1">
                      {feature.features.map((f: string, i: number) => (
                        <div key={i}>• {f}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Live Metrics */}
            <div className="bg-gradient-to-r from-accent-primary/10 to-accent-purple/10 rounded-lg p-6 border border-accent-primary/20">
              <h4 className="text-dark-text font-semibold mb-4">📊 Live Blockchain Metrics</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-mono text-accent-primary">
                    {systemStatus?.metrics.blockchain_transactions || 0}
                  </div>
                  <div className="text-dark-secondary-text text-sm">Transactions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-mono text-accent-secondary">
                    $0.001
                  </div>
                  <div className="text-dark-secondary-text text-sm">Avg Gas Cost</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-mono text-accent-warning">
                    99.9%
                  </div>
                  <div className="text-dark-secondary-text text-sm">Uptime</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'value' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-dark-text">💎 Value Proposition for MCP Ecosystem</h3>
            
            {Object.entries(MCP_VALUE_PROPOSITION).map(([category, benefits]) => (
              <div key={category} className="bg-dark-bg rounded-lg p-6">
                <h4 className="text-accent-primary font-semibold mb-4 capitalize flex items-center">
                  <span className="mr-2">
                    {category === 'for_developers' ? '👨‍💻' : 
                     category === 'for_enterprises' ? '🏢' : 
                     category === 'for_researchers' ? '🔬' : '⚡'}
                  </span>
                  {category.replace('_', ' ')}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {(benefits as string[]).map((benefit: string, i: number) => (
                    <div key={i} className="flex items-start">
                      <span className="text-accent-secondary mr-2 mt-1">•</span>
                      <span className="text-dark-secondary-text text-sm">{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'demo' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-dark-text">🚀 Live Demo & Interaction</h3>
            
            <div className="bg-dark-bg rounded-lg p-6">
              <h4 className="text-accent-primary font-semibold mb-4">Try Trilogy AGI Capabilities</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <button className="bg-gradient-to-r from-accent-primary to-accent-secondary text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">🧠 Advanced Reasoning</div>
                  <div className="text-sm opacity-90">Test DeepSeek R1 reasoning</div>
                </button>
                
                <button className="bg-gradient-to-r from-accent-secondary to-accent-purple text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">💾 Memory Storage</div>
                  <div className="text-sm opacity-90">Store and retrieve memories</div>
                </button>
                
                <button className="bg-gradient-to-r from-accent-purple to-accent-cyan text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">🎭 Multi-Agent</div>
                  <div className="text-sm opacity-90">Orchestrated query processing</div>
                </button>
                
                <button className="bg-gradient-to-r from-accent-cyan to-accent-warning text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">🧬 Code Evolution</div>
                  <div className="text-sm opacity-90">DGM code optimization</div>
                </button>
                
                <button className="bg-gradient-to-r from-accent-warning to-accent-danger text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">⚡ System Optimization</div>
                  <div className="text-sm opacity-90">Autonomous system tuning</div>
                </button>
                
                <button className="bg-gradient-to-r from-accent-danger to-accent-primary text-white p-4 rounded-lg hover:opacity-90 transition-opacity">
                  <div className="text-lg font-semibold mb-2">⛓️ Blockchain Verify</div>
                  <div className="text-sm opacity-90">On-chain verification</div>
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-gradient-to-r from-accent-primary/10 to-accent-purple/10 rounded-lg p-6 border border-accent-primary/20">
              <h4 className="text-dark-text font-semibold mb-4">📈 Real-time Performance</h4>
              <div className="text-center">
                <div className="text-4xl font-mono text-accent-primary mb-2">
                  {systemStatus?.metrics.total_requests || 0}
                </div>
                <div className="text-dark-secondary-text">Total Requests Processed</div>
                <div className="text-accent-secondary mt-2">
                  Saving developers ${(systemStatus?.metrics.cost_savings || 0).toFixed(2)} compared to cloud AI services
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrilogyAGIDashboard;
