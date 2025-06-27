"""
Advanced AI Modules for MCPVots Trading System
============================================

This package contains advanced AI components for the MCPVots trading system:

- quantum_strategy: Quantum-inspired trading strategy evolution
- neural_meta_learning: Meta-learning for strategy optimization  
- distributed_swarm: Distributed trading swarm coordination
- temporal_knowledge_graph: Temporal knowledge graph with causal reasoning
- self_modifying_code: Self-evolving code generation and optimization
- autonomous_orchestrator: Autonomous trading workflow orchestration
"""

__version__ = "1.0.0"
__author__ = "MCPVots Development Team"

# Import main components
from .quantum_strategy import quantum_strategy_evolution
from .neural_meta_learning import neural_meta_learning, neural_strategy_architect  
from .distributed_swarm import distributed_trading_swarm
from .temporal_knowledge_graph import temporal_knowledge_graph
from .self_modifying_code import self_modifying_code_generator, autonomous_code_creator
from .autonomous_orchestrator import autonomous_trading_orchestrator, autonomous_workflow_engine

__all__ = [
    'quantum_strategy_evolution',
    'neural_meta_learning', 
    'neural_strategy_architect',
    'distributed_trading_swarm',
    'temporal_knowledge_graph', 
    'self_modifying_code_generator',
    'autonomous_code_creator',
    'autonomous_trading_orchestrator',
    'autonomous_workflow_engine'
]
