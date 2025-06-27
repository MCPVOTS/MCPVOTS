#!/usr/bin/env python3
"""
Neural Meta-Learning System for MCPVots Trading
Advanced neural architecture that learns how to learn from market patterns

This system provides:
- Meta-learning algorithms for strategy adaptation
- Neural architecture search for optimal models
- Continual learning without catastrophic forgetting
- Memory-augmented neural networks
- Integration with quantum strategies and knowledge graph
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple, Union
import sqlite3
import random
from enum import Enum
import hashlib
import pickle
import copy
from collections import deque, defaultdict


@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning system"""
    inner_lr: float = 0.01
    outer_lr: float = 0.001
    num_inner_steps: int = 5
    num_outer_steps: int = 100
    meta_batch_size: int = 16
    support_shots: int = 5
    query_shots: int = 15
    memory_size: int = 10000
    architecture_search_steps: int = 50


@dataclass
class MetaLearningResult:
    """Result of meta-learning process"""
    adapted_parameters: Dict[str, torch.Tensor]
    meta_loss: float
    adaptation_accuracy: float
    memory_usage: float
    architecture_score: float
    learning_time: float
    convergence_steps: int


class MetaLearningMemory:
    """Memory system for meta-learning with experience replay"""
    
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.memory = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        
    def add(self, experience: Dict, priority: float = 1.0):
        """Add experience to memory"""
        self.memory.append(experience)
        self.priorities.append(priority)
    
    def sample(self, batch_size: int) -> List[Dict]:
        """Sample experiences with priority weighting"""
        if len(self.memory) < batch_size:
            return list(self.memory)
        
        # Convert priorities to probabilities
        priorities = np.array(self.priorities)
        probabilities = priorities / np.sum(priorities)
        
        # Sample indices based on priorities
        indices = np.random.choice(len(self.memory), size=batch_size, 
                                 replace=False, p=probabilities)
        
        return [self.memory[i] for i in indices]
    
    def update_priority(self, index: int, priority: float):
        """Update priority of experience"""
        if 0 <= index < len(self.priorities):
            self.priorities[index] = priority


class NeuralArchitectureCell(nn.Module):
    """Learnable neural architecture cell for NAS"""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        # Candidate operations
        self.operations = nn.ModuleDict({
            'linear': nn.Linear(input_dim, hidden_dim),
            'conv1d': nn.Conv1d(1, hidden_dim//8, kernel_size=3, padding=1),
            'lstm': nn.LSTM(input_dim, hidden_dim//2, batch_first=True),
            'attention': nn.MultiheadAttention(input_dim, num_heads=4, batch_first=True),
            'residual': nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, input_dim)
            )
        })
        
        # Architecture weights (learnable)
        self.arch_weights = nn.Parameter(torch.randn(len(self.operations)))
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, hidden_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with weighted combination of operations"""
        
        # Apply softmax to architecture weights
        arch_probs = F.softmax(self.arch_weights, dim=0)
        
        outputs = []
        
        for i, (op_name, operation) in enumerate(self.operations.items()):
            try:
                if op_name == 'conv1d':
                    # Reshape for conv1d
                    x_conv = x.unsqueeze(1)  # Add channel dimension
                    out = operation(x_conv)
                    out = out.squeeze(1)  # Remove channel dimension
                    # Pad or truncate to match hidden_dim
                    if out.size(-1) < self.hidden_dim:
                        pad_size = self.hidden_dim - out.size(-1)
                        out = F.pad(out, (0, pad_size))
                    else:
                        out = out[:, :self.hidden_dim]
                        
                elif op_name == 'lstm':
                    if len(x.shape) == 2:
                        x_lstm = x.unsqueeze(1)  # Add sequence dimension
                    else:
                        x_lstm = x
                    out, _ = operation(x_lstm)
                    out = out.squeeze(1) if out.size(1) == 1 else out.mean(dim=1)
                    # Ensure output dimension matches
                    if out.size(-1) != self.hidden_dim:
                        out = F.linear(out, torch.randn(out.size(-1), self.hidden_dim).to(out.device))
                        
                elif op_name == 'attention':
                    if len(x.shape) == 2:
                        x_att = x.unsqueeze(1)  # Add sequence dimension
                    else:
                        x_att = x
                    out, _ = operation(x_att, x_att, x_att)
                    out = out.squeeze(1) if out.size(1) == 1 else out.mean(dim=1)
                    
                elif op_name == 'residual':
                    out = operation(x)
                    # Residual connection
                    if out.size(-1) == x.size(-1):
                        out = out + x
                    # Project to hidden_dim
                    if out.size(-1) != self.hidden_dim:
                        out = F.linear(out, torch.randn(out.size(-1), self.hidden_dim).to(out.device))
                        
                else:  # linear
                    out = operation(x)
                
                # Weight by architecture probability
                weighted_out = arch_probs[i] * out
                outputs.append(weighted_out)
                
            except Exception as e:
                # Fallback to linear operation
                out = self.operations['linear'](x)
                weighted_out = arch_probs[i] * out
                outputs.append(weighted_out)
        
        # Combine all weighted outputs
        combined = torch.stack(outputs).sum(dim=0)
        
        # Final output projection
        output = self.output_proj(combined)
        
        return output


class MetaLearningNetwork(nn.Module):
    """Meta-learning neural network with adaptive architecture"""
    
    def __init__(self, input_dim: int, hidden_dim: int = 256, output_dim: int = 3, num_layers: int = 3):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        
        # Input normalization
        self.input_norm = nn.LayerNorm(input_dim)
        
        # Learnable architecture cells
        self.cells = nn.ModuleList([
            NeuralArchitectureCell(input_dim if i == 0 else hidden_dim, hidden_dim)
            for i in range(num_layers)
        ])
        
        # Meta-learning specific components
        self.meta_embedding = nn.Linear(input_dim, hidden_dim)
        self.task_embedding = nn.Linear(hidden_dim, hidden_dim)
        
        # Memory-augmented components
        self.memory_controller = nn.LSTMCell(hidden_dim, hidden_dim)
        self.memory_bank = nn.Parameter(torch.randn(100, hidden_dim))  # External memory
        
        # Output layers
        self.output_layers = nn.ModuleDict({
            'prediction': nn.Linear(hidden_dim, output_dim),
            'confidence': nn.Linear(hidden_dim, 1),
            'uncertainty': nn.Linear(hidden_dim, 1)
        })
        
        # Architecture search components
        self.architecture_controller = nn.Linear(hidden_dim, num_layers)
        
        # Initialize meta-learning parameters
        self.meta_parameters = {}
        for name, param in self.named_parameters():
            if param.requires_grad:
                self.meta_parameters[name] = param.clone()
    
    def forward(self, x: torch.Tensor, task_context: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """Forward pass with meta-learning and memory augmentation"""
        
        batch_size = x.size(0)
        
        # Input normalization
        x = self.input_norm(x)
        
        # Create task embedding
        if task_context is not None:
            task_emb = self.task_embedding(task_context)
        else:
            task_emb = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        
        # Meta embedding
        meta_emb = self.meta_embedding(x)
        
        # Combine with task context
        hidden = meta_emb + task_emb
        
        # Memory-augmented processing
        memory_state = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        memory_cell = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        
        # Pass through learnable architecture cells
        for i, cell in enumerate(self.cells):
            # Memory controller update
            memory_state, memory_cell = self.memory_controller(hidden, (memory_state, memory_cell))
            
            # Memory bank attention
            memory_attention = torch.softmax(torch.matmul(memory_state, self.memory_bank.T), dim=-1)
            memory_read = torch.matmul(memory_attention, self.memory_bank)
            
            # Combine with cell output
            cell_output = cell(hidden)
            hidden = cell_output + memory_read
            
            # Apply residual connection if dimensions match
            if i > 0 and hidden.size(-1) == meta_emb.size(-1):
                hidden = hidden + meta_emb
        
        # Generate outputs
        outputs = {}
        for output_name, output_layer in self.output_layers.items():
            outputs[output_name] = output_layer(hidden)
        
        # Architecture controller output
        outputs['architecture_logits'] = self.architecture_controller(hidden)
        
        return outputs
    
    def adapt_to_task(self, support_data: torch.Tensor, support_labels: torch.Tensor, 
                     num_steps: int = 5, lr: float = 0.01) -> Dict[str, torch.Tensor]:
        """Adapt network parameters to new task using gradient descent"""
        
        # Store original parameters
        original_params = {}
        for name, param in self.named_parameters():
            original_params[name] = param.clone()
        
        # Inner loop adaptation
        optimizer = optim.SGD(self.parameters(), lr=lr)
        
        for step in range(num_steps):
            # Forward pass
            outputs = self.forward(support_data)
            
            # Calculate adaptation loss
            pred_loss = F.cross_entropy(outputs['prediction'], support_labels)
            confidence_loss = -torch.mean(torch.log(torch.sigmoid(outputs['confidence'])))
            uncertainty_loss = torch.mean(outputs['uncertainty'])
            
            total_loss = pred_loss + 0.1 * confidence_loss + 0.05 * uncertainty_loss
            
            # Backward pass
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
        
        # Return adapted parameters
        adapted_params = {}
        for name, param in self.named_parameters():
            adapted_params[name] = param.clone()
        
        # Restore original parameters
        for name, param in self.named_parameters():
            param.data = original_params[name].data
        
        return adapted_params
    
    def get_architecture_description(self) -> Dict[str, Any]:
        """Get current architecture description"""
        
        architecture = {
            'num_layers': self.num_layers,
            'hidden_dim': self.hidden_dim,
            'cell_architectures': []
        }
        
        for i, cell in enumerate(self.cells):
            cell_arch = {
                'layer': i,
                'operation_weights': F.softmax(cell.arch_weights, dim=0).detach().cpu().numpy().tolist(),
                'dominant_operation': list(cell.operations.keys())[torch.argmax(cell.arch_weights).item()]
            }
            architecture['cell_architectures'].append(cell_arch)
        
        return architecture


class NeuralMetaLearningSystem:
    """Neural meta-learning system for trading strategy adaptation"""
    
    def __init__(self, input_dim: int = 50, hidden_dim: int = 256, config: Optional[MetaLearningConfig] = None):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.config = config or MetaLearningConfig()
        self.logger = self._setup_logging()
        
        # Initialize neural network
        self.network = MetaLearningNetwork(input_dim, hidden_dim)
        self.meta_optimizer = optim.Adam(self.network.parameters(), lr=self.config.outer_lr)
        
        # Memory system
        self.memory = MetaLearningMemory(capacity=self.config.memory_size)
        
        # Task and adaptation tracking
        self.task_history = []
        self.adaptation_history = []
        
        # Architecture search components
        self.architecture_scores = []
        self.best_architecture = None
        
        # Database for tracking
        self.db_path = Path(__file__).parent / "neural_meta_learning.db"
        self._init_database()
        
        self.logger.info("🧠 Neural Meta-Learning System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for meta-learning system"""
        logger = logging.getLogger("NeuralMetaLearning")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("neural_meta_learning.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize database for meta-learning tracking"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meta_learning_sessions (
                    session_id TEXT PRIMARY KEY,
                    task_description TEXT NOT NULL,
                    input_dim INTEGER NOT NULL,
                    meta_loss REAL NOT NULL,
                    adaptation_accuracy REAL NOT NULL,
                    architecture_score REAL NOT NULL,
                    learning_time REAL NOT NULL,
                    convergence_steps INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS architecture_evolution (
                    evolution_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    architecture_description TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    operation_weights TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS adaptation_history (
                    adaptation_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    original_params TEXT NOT NULL,
                    adapted_params TEXT NOT NULL,
                    adaptation_loss REAL NOT NULL,
                    task_similarity REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def meta_learn_from_tasks(self, tasks: List[Dict]) -> MetaLearningResult:
        """Meta-learn from multiple tasks using MAML-style algorithm"""
        
        self.logger.info(f"🎯 Starting meta-learning from {len(tasks)} tasks...")
        start_time = datetime.now()
        
        total_meta_loss = 0.0
        total_accuracy = 0.0
        convergence_steps = 0
        
        for outer_step in range(self.config.num_outer_steps):
            # Sample batch of tasks
            task_batch = random.sample(tasks, min(self.config.meta_batch_size, len(tasks)))
            
            meta_gradients = defaultdict(list)
            batch_loss = 0.0
            batch_accuracy = 0.0
            
            for task in task_batch:
                # Prepare task data
                support_data, support_labels, query_data, query_labels = self._prepare_task_data(task)
                
                # Inner loop adaptation
                adapted_params = self.network.adapt_to_task(
                    support_data, support_labels,
                    num_steps=self.config.num_inner_steps,
                    lr=self.config.inner_lr
                )
                
                # Evaluate on query set with adapted parameters
                with torch.no_grad():
                    # Temporarily update network parameters
                    original_params = {}
                    for name, param in self.network.named_parameters():
                        original_params[name] = param.clone()
                        param.data = adapted_params[name].data
                    
                    # Forward pass on query set
                    query_outputs = self.network.forward(query_data)
                    query_loss = F.cross_entropy(query_outputs['prediction'], query_labels)
                    
                    # Calculate accuracy
                    predictions = torch.argmax(query_outputs['prediction'], dim=1)
                    accuracy = (predictions == query_labels).float().mean()
                    
                    batch_loss += query_loss.item()
                    batch_accuracy += accuracy.item()
                    
                    # Restore original parameters
                    for name, param in self.network.named_parameters():
                        param.data = original_params[name].data
                
                # Calculate meta-gradients (second-order derivatives)
                # For simplicity, using first-order approximation here
                task_gradients = torch.autograd.grad(
                    query_loss, self.network.parameters(),
                    create_graph=True, retain_graph=True
                )
                
                for i, (name, param) in enumerate(self.network.named_parameters()):
                    meta_gradients[name].append(task_gradients[i])
            
            # Update meta-parameters
            self.meta_optimizer.zero_grad()
            
            for name, param in self.network.named_parameters():
                if name in meta_gradients:
                    # Average gradients across tasks
                    avg_gradient = torch.stack(meta_gradients[name]).mean(dim=0)
                    param.grad = avg_gradient
            
            self.meta_optimizer.step()
            
            # Track progress
            epoch_meta_loss = batch_loss / len(task_batch)
            epoch_accuracy = batch_accuracy / len(task_batch)
            
            total_meta_loss += epoch_meta_loss
            total_accuracy += epoch_accuracy
            
            if outer_step % 10 == 0:
                self.logger.info(f"   Epoch {outer_step}: Meta-loss={epoch_meta_loss:.4f}, Accuracy={epoch_accuracy:.4f}")
            
            # Check convergence
            if epoch_meta_loss < 0.01:
                convergence_steps = outer_step
                break
        
        # Final adapted parameters
        final_task = random.choice(tasks)
        support_data, support_labels, _, _ = self._prepare_task_data(final_task)
        adapted_parameters = self.network.adapt_to_task(support_data, support_labels)
        
        # Architecture evaluation
        architecture_score = await self._evaluate_architecture()
        
        # Memory usage calculation
        memory_usage = len(self.memory.memory) / self.memory.capacity
        
        learning_time = (datetime.now() - start_time).total_seconds()
        
        result = MetaLearningResult(
            adapted_parameters=adapted_parameters,
            meta_loss=total_meta_loss / max(1, self.config.num_outer_steps),
            adaptation_accuracy=total_accuracy / max(1, self.config.num_outer_steps),
            memory_usage=memory_usage,
            architecture_score=architecture_score,
            learning_time=learning_time,
            convergence_steps=convergence_steps if convergence_steps > 0 else self.config.num_outer_steps
        )
        
        # Store session in database
        await self._store_meta_learning_session(result, tasks)
        
        self.logger.info(f"🎉 Meta-learning complete. Final accuracy: {result.adaptation_accuracy:.4f}")
        
        return result
    
    def _prepare_task_data(self, task: Dict) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Prepare support and query data for a task"""
        
        # Extract market data and labels from task
        market_data = np.array(task.get('market_data', []))
        labels = np.array(task.get('labels', []))
        
        # Pad or truncate to match input dimension
        if market_data.shape[-1] < self.input_dim:
            padding = np.zeros((market_data.shape[0], self.input_dim - market_data.shape[-1]))
            market_data = np.concatenate([market_data, padding], axis=1)
        elif market_data.shape[-1] > self.input_dim:
            market_data = market_data[:, :self.input_dim]
        
        # Convert to tensors
        data_tensor = torch.FloatTensor(market_data)
        label_tensor = torch.LongTensor(labels)
        
        # Split into support and query sets
        total_shots = self.config.support_shots + self.config.query_shots
        if len(data_tensor) < total_shots:
            # Duplicate data if insufficient
            repeat_factor = (total_shots // len(data_tensor)) + 1
            data_tensor = data_tensor.repeat(repeat_factor, 1)[:total_shots]
            label_tensor = label_tensor.repeat(repeat_factor)[:total_shots]
        
        # Random split
        indices = torch.randperm(len(data_tensor))
        support_indices = indices[:self.config.support_shots]
        query_indices = indices[self.config.support_shots:self.config.support_shots + self.config.query_shots]
        
        support_data = data_tensor[support_indices]
        support_labels = label_tensor[support_indices]
        query_data = data_tensor[query_indices]
        query_labels = label_tensor[query_indices]
        
        return support_data, support_labels, query_data, query_labels
    
    async def neural_architecture_search(self) -> Dict[str, Any]:
        """Perform neural architecture search to optimize network structure"""
        
        self.logger.info("🔍 Starting Neural Architecture Search...")
        
        best_score = -float('inf')
        best_architecture = None
        search_results = []
        
        for step in range(self.config.architecture_search_steps):
            # Generate random architecture modifications
            self._mutate_architecture()
            
            # Evaluate architecture
            score = await self._evaluate_architecture()
            
            search_results.append({
                'step': step,
                'architecture': self.network.get_architecture_description(),
                'score': score
            })
            
            if score > best_score:
                best_score = score
                best_architecture = copy.deepcopy(self.network.get_architecture_description())
                
                self.logger.info(f"   New best architecture found: Score={score:.4f}")
            
            if step % 10 == 0:
                self.logger.info(f"   NAS Step {step}: Current Score={score:.4f}, Best={best_score:.4f}")
        
        self.best_architecture = best_architecture
        self.architecture_scores.append(best_score)
        
        # Store architecture evolution
        await self._store_architecture_evolution(search_results)
        
        return {
            'best_architecture': best_architecture,
            'best_score': best_score,
            'search_history': search_results,
            'improvement': best_score - (self.architecture_scores[-2] if len(self.architecture_scores) > 1 else 0)
        }
    
    def _mutate_architecture(self):
        """Mutate current architecture for search"""
        
        for cell in self.network.cells:
            # Add noise to architecture weights
            mutation_strength = 0.1
            noise = torch.randn_like(cell.arch_weights) * mutation_strength
            cell.arch_weights.data += noise
            
            # Ensure weights remain learnable
            cell.arch_weights.data = torch.clamp(cell.arch_weights.data, -5, 5)
    
    async def _evaluate_architecture(self) -> float:
        """Evaluate current architecture performance"""
        
        # Generate synthetic evaluation task
        eval_data = torch.randn(100, self.input_dim)
        eval_labels = torch.randint(0, 3, (100,))
        
        # Split into support and query
        support_data = eval_data[:50]
        support_labels = eval_labels[:50]
        query_data = eval_data[50:]
        query_labels = eval_labels[50:]
        
        # Test adaptation capability
        adapted_params = self.network.adapt_to_task(support_data, support_labels)
        
        # Evaluate adapted network
        with torch.no_grad():
            # Temporarily update parameters
            original_params = {}
            for name, param in self.network.named_parameters():
                original_params[name] = param.clone()
                param.data = adapted_params[name].data
            
            # Forward pass
            outputs = self.network.forward(query_data)
            predictions = torch.argmax(outputs['prediction'], dim=1)
            accuracy = (predictions == query_labels).float().mean().item()
            
            # Confidence and uncertainty evaluation
            confidence = torch.sigmoid(outputs['confidence']).mean().item()
            uncertainty = outputs['uncertainty'].mean().item()
            
            # Architecture complexity penalty
            total_params = sum(p.numel() for p in self.network.parameters())
            complexity_penalty = np.log(total_params) / 1000
            
            # Restore parameters
            for name, param in self.network.named_parameters():
                param.data = original_params[name].data
        
        # Combine metrics
        score = accuracy + 0.1 * confidence - 0.05 * uncertainty - 0.01 * complexity_penalty
        
        return score
    
    async def continual_learning_update(self, new_task: Dict) -> Dict[str, float]:
        """Update system with new task while preventing catastrophic forgetting"""
        
        self.logger.info("📚 Performing continual learning update...")
        
        # Store current performance on old tasks
        old_performance = await self._evaluate_memory_tasks()
        
        # Learn new task
        new_task_data = self._prepare_task_data(new_task)
        support_data, support_labels, query_data, query_labels = new_task_data
        
        # Elastic Weight Consolidation (EWC) for catastrophic forgetting prevention
        fisher_information = self._compute_fisher_information()
        
        # Adapt to new task with EWC regularization
        adapted_params = await self._ewc_adaptation(
            support_data, support_labels, query_data, query_labels, fisher_information
        )
        
        # Update network parameters
        for name, param in self.network.named_parameters():
            if name in adapted_params:
                param.data = adapted_params[name].data
        
        # Evaluate performance after update
        new_performance = await self._evaluate_memory_tasks()
        
        # Add to memory with priority based on performance difference
        priority = max(0.1, abs(new_performance - old_performance))
        self.memory.add(new_task, priority)
        
        # Calculate forgetting measure
        forgetting = max(0, old_performance - new_performance)
        
        self.logger.info(f"   Continual learning complete. Forgetting: {forgetting:.4f}")
        
        return {
            'old_performance': old_performance,
            'new_performance': new_performance,
            'forgetting': forgetting,
            'memory_size': len(self.memory.memory)
        }
    
    def _compute_fisher_information(self) -> Dict[str, torch.Tensor]:
        """Compute Fisher Information Matrix for EWC"""
        
        fisher_info = {}
        
        # Sample data from memory for Fisher computation
        if len(self.memory.memory) == 0:
            return fisher_info
        
        memory_samples = self.memory.sample(min(100, len(self.memory.memory)))
        
        # Accumulate gradients for Fisher information
        for sample in memory_samples:
            # Prepare sample data
            sample_data, sample_labels, _, _ = self._prepare_task_data(sample)
            
            # Forward pass
            outputs = self.network.forward(sample_data)
            loss = F.cross_entropy(outputs['prediction'], sample_labels)
            
            # Compute gradients
            gradients = torch.autograd.grad(loss, self.network.parameters(), retain_graph=True)
            
            # Accumulate squared gradients (Fisher information)
            for i, (name, param) in enumerate(self.network.named_parameters()):
                if name not in fisher_info:
                    fisher_info[name] = torch.zeros_like(param)
                fisher_info[name] += gradients[i] ** 2
        
        # Normalize by number of samples
        for name in fisher_info:
            fisher_info[name] /= len(memory_samples)
        
        return fisher_info
    
    async def _ewc_adaptation(self, support_data: torch.Tensor, support_labels: torch.Tensor,
                             query_data: torch.Tensor, query_labels: torch.Tensor,
                             fisher_info: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Perform EWC-regularized adaptation"""
        
        # Store original parameters for EWC regularization
        original_params = {}
        for name, param in self.network.named_parameters():
            original_params[name] = param.clone()
        
        # EWC optimizer
        ewc_optimizer = optim.SGD(self.network.parameters(), lr=self.config.inner_lr)
        
        for step in range(self.config.num_inner_steps):
            # Forward pass
            outputs = self.network.forward(support_data)
            
            # Task loss
            task_loss = F.cross_entropy(outputs['prediction'], support_labels)
            
            # EWC regularization loss
            ewc_loss = 0.0
            ewc_lambda = 1000.0  # EWC strength
            
            for name, param in self.network.named_parameters():
                if name in fisher_info and name in original_params:
                    ewc_loss += (fisher_info[name] * (param - original_params[name]) ** 2).sum()
            
            # Total loss
            total_loss = task_loss + ewc_lambda * ewc_loss
            
            # Backward pass
            ewc_optimizer.zero_grad()
            total_loss.backward()
            ewc_optimizer.step()
        
        # Return adapted parameters
        adapted_params = {}
        for name, param in self.network.named_parameters():
            adapted_params[name] = param.clone()
        
        return adapted_params
    
    async def _evaluate_memory_tasks(self) -> float:
        """Evaluate performance on tasks stored in memory"""
        
        if len(self.memory.memory) == 0:
            return 0.0
        
        total_accuracy = 0.0
        num_tasks = min(10, len(self.memory.memory))
        
        memory_samples = self.memory.sample(num_tasks)
        
        for sample in memory_samples:
            # Prepare task data
            _, _, query_data, query_labels = self._prepare_task_data(sample)
            
            # Evaluate
            with torch.no_grad():
                outputs = self.network.forward(query_data)
                predictions = torch.argmax(outputs['prediction'], dim=1)
                accuracy = (predictions == query_labels).float().mean().item()
                total_accuracy += accuracy
        
        return total_accuracy / num_tasks
    
    async def _store_meta_learning_session(self, result: MetaLearningResult, tasks: List[Dict]):
        """Store meta-learning session in database"""
        
        try:
            session_id = hashlib.sha256(f"{datetime.now()}_{len(tasks)}".encode()).hexdigest()[:16]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO meta_learning_sessions 
                    (session_id, task_description, input_dim, meta_loss, adaptation_accuracy,
                     architecture_score, learning_time, convergence_steps)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    f"Meta-learning on {len(tasks)} tasks",
                    self.input_dim,
                    result.meta_loss,
                    result.adaptation_accuracy,
                    result.architecture_score,
                    result.learning_time,
                    result.convergence_steps
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store meta-learning session: {e}")
    
    async def _store_architecture_evolution(self, search_results: List[Dict]):
        """Store architecture evolution history"""
        
        try:
            session_id = hashlib.sha256(f"nas_{datetime.now()}".encode()).hexdigest()[:16]
            
            with sqlite3.connect(self.db_path) as conn:
                for result in search_results:
                    evolution_id = hashlib.sha256(f"{session_id}_{result['step']}".encode()).hexdigest()[:16]
                    
                    conn.execute("""
                        INSERT INTO architecture_evolution 
                        (evolution_id, session_id, architecture_description, 
                         performance_score, operation_weights)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        evolution_id,
                        session_id,
                        json.dumps(result['architecture']),
                        result['score'],
                        json.dumps(result['architecture'].get('cell_architectures', []))
                    ))
                    
        except Exception as e:
            self.logger.error(f"Failed to store architecture evolution: {e}")
    
    async def get_meta_learning_statistics(self) -> Dict[str, Any]:
        """Get meta-learning system statistics"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Recent sessions
                recent_sessions = conn.execute("""
                    SELECT adaptation_accuracy, architecture_score, learning_time, convergence_steps
                    FROM meta_learning_sessions
                    ORDER BY created_at DESC
                    LIMIT 10
                """).fetchall()
                
                # Architecture evolution stats
                arch_stats = conn.execute("""
                    SELECT AVG(performance_score), MAX(performance_score), MIN(performance_score)
                    FROM architecture_evolution
                """).fetchone()
                
                stats = {
                    'recent_sessions': len(recent_sessions),
                    'avg_adaptation_accuracy': np.mean([s[0] for s in recent_sessions]) if recent_sessions else 0,
                    'avg_architecture_score': np.mean([s[1] for s in recent_sessions]) if recent_sessions else 0,
                    'avg_learning_time': np.mean([s[2] for s in recent_sessions]) if recent_sessions else 0,
                    'avg_convergence_steps': np.mean([s[3] for s in recent_sessions]) if recent_sessions else 0,
                    'architecture_evolution': {
                        'avg_score': arch_stats[0] if arch_stats[0] else 0,
                        'best_score': arch_stats[1] if arch_stats[1] else 0,
                        'worst_score': arch_stats[2] if arch_stats[2] else 0
                    },
                    'memory_utilization': len(self.memory.memory) / self.memory.capacity,
                    'current_architecture': self.network.get_architecture_description()
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get meta-learning statistics: {e}")
            return {'error': str(e)}


# Demo function for testing
async def demo_neural_meta_learning():
    """Demo the neural meta-learning system"""
    
    print("🧠 Demo: Neural Meta-Learning System")
    print("=" * 60)
    
    # Initialize meta-learning system
    meta_learning = NeuralMetaLearningSystem(input_dim=20, hidden_dim=128)
    
    # Generate synthetic trading tasks
    tasks = []
    for i in range(10):
        # Generate random market data
        market_data = np.random.randn(50, 20)  # 50 samples, 20 features
        
        # Generate labels based on simple rule (for demo)
        labels = []
        for sample in market_data:
            if np.mean(sample[:5]) > 0.5:
                labels.append(2)  # Buy
            elif np.mean(sample[:5]) < -0.5:
                labels.append(0)  # Sell
            else:
                labels.append(1)  # Hold
        
        task = {
            'task_id': f"trading_task_{i}",
            'market_data': market_data.tolist(),
            'labels': labels,
            'market_regime': random.choice(['trending', 'ranging', 'volatile'])
        }
        tasks.append(task)
    
    print(f"📊 Generated {len(tasks)} synthetic trading tasks")
    
    # Meta-learning phase
    print(f"\n🎯 Starting Meta-Learning...")
    meta_result = await meta_learning.meta_learn_from_tasks(tasks)
    
    print(f"✨ Meta-Learning Results:")
    print(f"   Meta Loss: {meta_result.meta_loss:.4f}")
    print(f"   Adaptation Accuracy: {meta_result.adaptation_accuracy:.4f}")
    print(f"   Architecture Score: {meta_result.architecture_score:.4f}")
    print(f"   Learning Time: {meta_result.learning_time:.2f}s")
    print(f"   Convergence Steps: {meta_result.convergence_steps}")
    print(f"   Memory Usage: {meta_result.memory_usage:.2%}")
    
    # Neural Architecture Search
    print(f"\n🔍 Starting Neural Architecture Search...")
    nas_result = await meta_learning.neural_architecture_search()
    
    print(f"🏗️ NAS Results:")
    print(f"   Best Score: {nas_result['best_score']:.4f}")
    print(f"   Improvement: {nas_result['improvement']:.4f}")
    print(f"   Search Steps: {len(nas_result['search_history'])}")
    
    # Show best architecture
    best_arch = nas_result['best_architecture']
    print(f"   Best Architecture:")
    for i, cell_arch in enumerate(best_arch['cell_architectures']):
        dominant_op = cell_arch['dominant_operation']
        weight = max(cell_arch['operation_weights'])
        print(f"     Layer {i}: {dominant_op} (weight: {weight:.3f})")
    
    # Continual Learning Test
    print(f"\n📚 Testing Continual Learning...")
    new_task = {
        'task_id': "new_trading_task",
        'market_data': np.random.randn(30, 20).tolist(),
        'labels': [random.randint(0, 2) for _ in range(30)],
        'market_regime': 'volatile'
    }
    
    cl_result = await meta_learning.continual_learning_update(new_task)
    
    print(f"🔄 Continual Learning Results:")
    print(f"   Old Performance: {cl_result['old_performance']:.4f}")
    print(f"   New Performance: {cl_result['new_performance']:.4f}")
    print(f"   Forgetting: {cl_result['forgetting']:.4f}")
    print(f"   Memory Size: {cl_result['memory_size']}")
    
    # Get system statistics
    stats = await meta_learning.get_meta_learning_statistics()
    
    print(f"\n📈 System Statistics:")
    print(f"   Average Adaptation Accuracy: {stats['avg_adaptation_accuracy']:.4f}")
    print(f"   Average Architecture Score: {stats['avg_architecture_score']:.4f}")
    print(f"   Average Learning Time: {stats['avg_learning_time']:.2f}s")
    print(f"   Memory Utilization: {stats['memory_utilization']:.2%}")
    
    print(f"\n🎉 Neural Meta-Learning Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_neural_meta_learning())
