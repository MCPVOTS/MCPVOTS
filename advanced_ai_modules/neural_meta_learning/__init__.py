"""
Neural Meta-Learning Module
===========================

Advanced neural meta-learning system for trading strategy optimization
using few-shot learning and adaptive neural architectures.

Main Components:
- NeuralMetaLearning: Core meta-learning system
- NeuralStrategyArchitect: Neural architecture search for trading strategies
- Adaptive learning algorithms for market regime changes
- Multi-task learning across different trading instruments
"""

from .neural_meta_learning import NeuralMetaLearning
from .neural_strategy_architect import NeuralStrategyArchitect

__all__ = ['NeuralMetaLearning', 'NeuralStrategyArchitect']
