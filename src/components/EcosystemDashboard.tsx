/**
 * Comprehensive Ecosystem Dashboard
 * Showcases the complete value proposition of MCPVots for agents and humans
 */

"use client";

import React, { useState, useEffect } from 'react';
import { 
  AGENT_VALUE_PROPOSITION, 
  HUMAN_VALUE_PROPOSITION, 
  ECOSYSTEM_METRICS,
  COMPETITIVE_ADVANTAGES,
  USE_CASE_SCENARIOS
} from '../services/ecosystem-value-analysis';
import { TRILOGY_AGI_OVERVIEW } from '../services/trilogy-overview';

interface EcosystemDashboardProps {
  className?: string;
}

export const EcosystemDashboard: React.FC<EcosystemDashboardProps> = ({ className = '' }) => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedValueProp, setSelectedValueProp] = useState<string | null>(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState(ECOSYSTEM_METRICS);

  useEffect(() => {
    // Simulate real-time metrics updates
    const interval = setInterval(() => {
      setRealTimeMetrics(prev => ({
        ...prev,
        performance: {
          ...prev.performance,
          response_time_ms: Math.floor(Math.random() * 50) + 125,
          throughput_requests_per_second: Math.floor(Math.random() * 200) + 900,
          availability_percentage: 99.8 + Math.random() * 0.2
        }
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const TabButton: React.FC<{ id: string; label: string; emoji: string }> = ({ id, label, emoji }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
        activeTab === id
          ? 'bg-blue-600 text-white shadow-lg'
          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
      }`}
    >
      <span className="text-lg">{emoji}</span>
      {label}
    </button>
  );

  const MetricCard: React.FC<{ title: string; value: string | number; unit?: string; trend?: string; emoji: string }> = 
    ({ title, value, unit, trend, emoji }) => (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm font-medium">{title}</span>
        <span className="text-xl">{emoji}</span>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-white">{value}</span>
        {unit && <span className="text-gray-400 text-sm">{unit}</span>}
      </div>
      {trend && (
        <div className="mt-1 text-xs text-green-400">
          ↗ {trend}
        </div>
      )}
    </div>
  );

  const ValuePropCard: React.FC<{ 
    title: string; 
    description: string; 
    benefits: string[]; 
    roi: string[];
    emoji: string;
    id: string;
  }> = ({ title, description, benefits, roi, emoji, id }) => (
    <div 
      className={`bg-gray-800 rounded-xl p-6 border transition-all duration-200 cursor-pointer ${
        selectedValueProp === id 
          ? 'border-blue-500 bg-gray-750' 
          : 'border-gray-700 hover:border-gray-600'
      }`}
      onClick={() => setSelectedValueProp(selectedValueProp === id ? null : id)}
    >
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">{emoji}</span>
        <h3 className="text-xl font-bold text-white">{title}</h3>
      </div>
      <p className="text-gray-300 mb-4">{description}</p>
      
      {selectedValueProp === id && (
        <div className="space-y-4">
          <div>
            <h4 className="text-lg font-semibold text-blue-400 mb-2">Key Benefits</h4>
            <ul className="space-y-1">
              {benefits.slice(0, 3).map((benefit, index) => (
                <li key={index} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-green-400 mt-1">•</span>
                  {benefit}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-green-400 mb-2">ROI Metrics</h4>
            <ul className="space-y-1">
              {roi.slice(0, 3).map((metric, index) => (
                <li key={index} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-blue-400 mt-1">▲</span>
                  {metric}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold text-white mb-4">
          🚀 MCPVots Ecosystem
        </h1>
        <p className="text-xl text-gray-300 max-w-4xl mx-auto">
          A comprehensive AGI-powered platform that brings unprecedented value to both AI agents and humans 
          through advanced reasoning, memory, and autonomous capabilities.
        </p>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="Response Time"
          value={realTimeMetrics.performance.response_time_ms}
          unit="ms"
          trend="+15% faster"
          emoji="⚡"
        />
        <MetricCard
          title="Throughput"
          value={realTimeMetrics.performance.throughput_requests_per_second}
          unit="req/s"
          trend="+25% higher"
          emoji="🚄"
        />
        <MetricCard
          title="Availability"
          value={realTimeMetrics.performance.availability_percentage.toFixed(1)}
          unit="%"
          trend="99.9% uptime"
          emoji="🛡️"
        />
        <MetricCard
          title="Cost Efficiency"
          value="85"
          unit="% savings"
          trend="+12% this month"
          emoji="💰"
        />
      </div>

      {/* Core Services Status */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          🏗️ Core AGI Services
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(TRILOGY_AGI_OVERVIEW.core_services).map(([key, service]) => (
            <div key={key} className="bg-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-green-400 text-sm">🟢 ONLINE</span>
                <span className="text-gray-400 text-xs">Port {service.port}</span>
              </div>
              <h3 className="text-white font-medium text-sm">{key.replace(/_/g, ' ').toUpperCase()}</h3>
              <p className="text-gray-400 text-xs mt-1">{service.capabilities[0]}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAgentValue = () => (
    <div className="space-y-8">
      <div className="text-center py-6">
        <h2 className="text-3xl font-bold text-white mb-4">
          🤖 Value for AI Agents
        </h2>
        <p className="text-lg text-gray-300 max-w-3xl mx-auto">
          Advanced capabilities that enhance AI agent performance, autonomy, and collaboration
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ValuePropCard
          id="reasoning"
          title="Enhanced Reasoning"
          description={AGENT_VALUE_PROPOSITION.reasoning_enhancement.description}
          benefits={AGENT_VALUE_PROPOSITION.reasoning_enhancement.benefits}
          roi={AGENT_VALUE_PROPOSITION.reasoning_enhancement.roi_metrics}
          emoji="🧠"
        />
        <ValuePropCard
          id="memory"
          title="Memory Augmentation"
          description={AGENT_VALUE_PROPOSITION.memory_augmentation.description}
          benefits={AGENT_VALUE_PROPOSITION.memory_augmentation.benefits}
          roi={AGENT_VALUE_PROPOSITION.memory_augmentation.roi_metrics}
          emoji="🧮"
        />
        <ValuePropCard
          id="autonomous"
          title="Autonomous Capabilities"
          description={AGENT_VALUE_PROPOSITION.autonomous_capabilities.description}
          benefits={AGENT_VALUE_PROPOSITION.autonomous_capabilities.benefits}
          roi={AGENT_VALUE_PROPOSITION.autonomous_capabilities.roi_metrics}
          emoji="🔄"
        />
        <ValuePropCard
          id="collaboration"
          title="Collaboration Tools"
          description={AGENT_VALUE_PROPOSITION.collaboration_tools.description}
          benefits={AGENT_VALUE_PROPOSITION.collaboration_tools.benefits}
          roi={AGENT_VALUE_PROPOSITION.collaboration_tools.roi_metrics}
          emoji="🤝"
        />
      </div>
    </div>
  );

  const renderHumanValue = () => (
    <div className="space-y-8">
      <div className="text-center py-6">
        <h2 className="text-3xl font-bold text-white mb-4">
          👥 Value for Humans
        </h2>
        <p className="text-lg text-gray-300 max-w-3xl mx-auto">
          AI-powered tools that amplify human capabilities and transform productivity
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ValuePropCard
          id="productivity"
          title="Productivity Enhancement"
          description={HUMAN_VALUE_PROPOSITION.productivity_enhancement.description}
          benefits={HUMAN_VALUE_PROPOSITION.productivity_enhancement.benefits}
          roi={HUMAN_VALUE_PROPOSITION.productivity_enhancement.roi_metrics}
          emoji="📈"
        />
        <ValuePropCard
          id="decision"
          title="Decision Support"
          description={HUMAN_VALUE_PROPOSITION.decision_support.description}
          benefits={HUMAN_VALUE_PROPOSITION.decision_support.benefits}
          roi={HUMAN_VALUE_PROPOSITION.decision_support.roi_metrics}
          emoji="🎯"
        />
        <ValuePropCard
          id="knowledge"
          title="Knowledge Amplification"
          description={HUMAN_VALUE_PROPOSITION.knowledge_amplification.description}
          benefits={HUMAN_VALUE_PROPOSITION.knowledge_amplification.benefits}
          roi={HUMAN_VALUE_PROPOSITION.knowledge_amplification.roi_metrics}
          emoji="🎓"
        />
        <ValuePropCard
          id="automation"
          title="Automation Assistance"
          description={HUMAN_VALUE_PROPOSITION.automation_assistance.description}
          benefits={HUMAN_VALUE_PROPOSITION.automation_assistance.benefits}
          roi={HUMAN_VALUE_PROPOSITION.automation_assistance.roi_metrics}
          emoji="⚙️"
        />
      </div>
    </div>
  );

  const renderUseCases = () => (
    <div className="space-y-8">
      <div className="text-center py-6">
        <h2 className="text-3xl font-bold text-white mb-4">
          🎯 Real-World Use Cases
        </h2>
        <p className="text-lg text-gray-300 max-w-3xl mx-auto">
          See how MCPVots transforms industries and workflows
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(USE_CASE_SCENARIOS).map(([key, useCase]) => (
          <div key={key} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-3">{useCase.title}</h3>
            <p className="text-gray-300 mb-4">{useCase.description}</p>
            
            <div className="mb-4">
              <h4 className="text-lg font-semibold text-blue-400 mb-2">Value Chain</h4>
              <ul className="space-y-1">
                {useCase.value_chain.slice(0, 3).map((step, index) => (
                  <li key={index} className="text-gray-300 text-sm flex items-start gap-2">
                    <span className="text-blue-400 mt-1">{index + 1}.</span>
                    {step}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-green-900/20 rounded-lg p-3 border border-green-500/30">
              <span className="text-green-400 font-semibold">Impact: </span>
              <span className="text-gray-300">{useCase.impact}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCompetitive = () => (
    <div className="space-y-8">
      <div className="text-center py-6">
        <h2 className="text-3xl font-bold text-white mb-4">
          🏆 Competitive Advantages
        </h2>
        <p className="text-lg text-gray-300 max-w-3xl mx-auto">
          Why MCPVots stands out in the AI ecosystem
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(COMPETITIVE_ADVANTAGES).map(([key, advantage]) => (
          <div key={key} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-3 capitalize">
              {advantage.description}
            </h3>
            <ul className="space-y-2">
              {advantage.advantages.map((adv, index) => (
                <li key={index} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  {adv}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className={`min-h-screen bg-gray-900 text-white ${className}`}>
      <div className="container mx-auto px-6 py-8">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-4 mb-8 justify-center">
          <TabButton id="overview" label="System Overview" emoji="🌟" />
          <TabButton id="agents" label="Agent Value" emoji="🤖" />
          <TabButton id="humans" label="Human Value" emoji="👥" />
          <TabButton id="use-cases" label="Use Cases" emoji="🎯" />
          <TabButton id="competitive" label="Advantages" emoji="🏆" />
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'agents' && renderAgentValue()}
          {activeTab === 'humans' && renderHumanValue()}
          {activeTab === 'use-cases' && renderUseCases()}
          {activeTab === 'competitive' && renderCompetitive()}
        </div>
      </div>
    </div>
  );
};

export default EcosystemDashboard;
