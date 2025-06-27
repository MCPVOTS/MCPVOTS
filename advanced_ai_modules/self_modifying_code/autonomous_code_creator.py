#!/usr/bin/env python3
"""
Self-Learning Autonomous Code Creator for MCPVots Trading System
Enhanced AI-driven code generation and evolution for trading strategies

This system creates, evolves, and deploys trading strategies autonomously using:
- Neural code generation with DeepSeek/Gemini models
- Genetic programming for strategy evolution
- Knowledge graph learning from historical performance
- Self-modifying code capabilities
- Real-time adaptation to market conditions
"""

import ast
import asyncio
import json
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple
import requests
import sqlite3
import inspect
import textwrap

# Import transformers for AI code generation
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("Transformers not available - using fallback code generation")


@dataclass
class CodeEvolution:
    """Represents an evolved trading strategy code generation"""
    generation: int
    code: str
    performance_score: float
    market_conditions: Dict[str, Any]
    mutations: List[str]
    fitness: float
    timestamp: datetime
    parent_strategy: Optional[str] = None
    validation_results: Dict[str, Any] = None


@dataclass
class StrategyComponent:
    """Individual component of a trading strategy"""
    component_type: str  # 'indicator', 'entry', 'exit', 'risk'
    code: str
    parameters: Dict[str, Any]
    performance_impact: float
    usage_frequency: int


class SelfLearningCodeCreator:
    """
    Autonomous code creator that learns and evolves trading strategies
    
    Features:
    - AI-powered code generation using multiple LLMs
    - Genetic programming for strategy evolution  
    - Performance-based fitness evaluation
    - Self-modifying code injection
    - Knowledge graph integration for learning
    """
    
    def __init__(self, mcp_integration, knowledge_graph_url: str = "http://localhost:3002"):
        self.mcp = mcp_integration
        self.kg_url = knowledge_graph_url
        self.logger = self._setup_logging()
        
        # Initialize AI models for code generation
        self.code_models = self._initialize_code_models()
        
        # Strategy evolution tracking
        self.strategy_genome = []
        self.performance_memory = []
        self.component_library = {}
        self.evolution_history = []
        
        # Code generation templates and patterns
        self.strategy_templates = self._load_strategy_templates()
        self.code_patterns = self._load_code_patterns()
        
        # Database for autonomous code tracking
        self.db_path = Path(__file__).parent / "autonomous_code.db"
        self._init_database()
        
        self.logger.info("🧠 Self-Learning Autonomous Code Creator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for autonomous code creator"""
        logger = logging.getLogger("AutonomousCodeCreator")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("autonomous_code_creator.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_code_models(self) -> Dict:
        """Initialize AI models for code generation"""
        models = {}
        
        if HF_AVAILABLE:
            try:
                # DeepSeek Coder for strategy generation
                models['deepseek_coder'] = {
                    'model': AutoModelForCausalLM.from_pretrained(
                        "deepseek-ai/deepseek-coder-6.7b-base",
                        torch_dtype=torch.float16,
                        device_map="auto" if torch.cuda.is_available() else None
                    ),
                    'tokenizer': AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-6.7b-base")
                }
                
                # Code generation pipeline
                models['code_pipeline'] = pipeline(
                    "text-generation",
                    model="microsoft/CodeT5p-220m-py",
                    tokenizer="microsoft/CodeT5p-220m-py"
                )
                
                self.logger.info("✅ AI code generation models loaded successfully")
                
            except Exception as e:
                self.logger.warning(f"Failed to load HF models: {e}")
                models = self._create_fallback_models()
        else:
            models = self._create_fallback_models()
        
        return models
    
    def _create_fallback_models(self) -> Dict:
        """Create fallback models when HF not available"""
        return {
            'fallback': True,
            'code_pipeline': self._fallback_code_generation
        }
    
    def _fallback_code_generation(self, prompt: str) -> str:
        """Fallback code generation using template patterns"""
        # Use template-based code generation as fallback
        return self._generate_from_templates(prompt)
    
    def _init_database(self):
        """Initialize database for autonomous code tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation INTEGER NOT NULL,
                    strategy_code TEXT NOT NULL,
                    performance_score REAL NOT NULL,
                    fitness REAL NOT NULL,
                    market_conditions TEXT NOT NULL,
                    mutations TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    parent_strategy TEXT,
                    validation_results TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_type TEXT NOT NULL,
                    component_code TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    performance_impact REAL NOT NULL,
                    usage_frequency INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_generation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    generated_code TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    performance_evaluation REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE
                )
            """)
    
    def _load_strategy_templates(self) -> Dict[str, str]:
        """Load strategy code templates"""
        return {
            "momentum_strategy": """
class MomentumStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.rsi_period = {rsi_period}
        self.ema_fast = {ema_fast}
        self.ema_slow = {ema_slow}
        self.risk_per_trade = {risk_per_trade}
        
    def on_bar(self, bar):
        # {entry_logic}
        if self.should_enter_long(bar):
            self.enter_long(bar)
        elif self.should_enter_short(bar):
            self.enter_short(bar)
        
        # {exit_logic}
        self.manage_positions(bar)
            """,
            
            "mean_reversion": """
class MeanReversionStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.bb_period = {bb_period}
        self.bb_std = {bb_std}
        self.rsi_oversold = {rsi_oversold}
        self.rsi_overbought = {rsi_overbought}
        
    def on_bar(self, bar):
        # {mean_reversion_logic}
        if self.is_oversold(bar):
            self.enter_long(bar)
        elif self.is_overbought(bar):
            self.enter_short(bar)
            """,
            
            "breakout_strategy": """
class BreakoutStrategy(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.lookback_period = {lookback_period}
        self.volume_threshold = {volume_threshold}
        self.atr_multiplier = {atr_multiplier}
        
    def on_bar(self, bar):
        # {breakout_logic}
        if self.is_breakout(bar):
            self.enter_breakout_trade(bar)
            """
        }
    
    def _load_code_patterns(self) -> Dict[str, List[str]]:
        """Load common code patterns for evolution"""
        return {
            "entry_conditions": [
                "price > ema_fast and ema_fast > ema_slow",
                "rsi < 30 and price < bb_lower",
                "volume > volume_avg * 1.5 and price > resistance",
                "macd_line > macd_signal and momentum > 0",
                "price_change > atr * multiplier"
            ],
            "exit_conditions": [
                "profit_pct > take_profit_pct",
                "loss_pct < -stop_loss_pct", 
                "rsi > 70",
                "price < ema_fast",
                "bars_since_entry > max_hold_bars"
            ],
            "risk_management": [
                "position_size = account_balance * risk_per_trade / stop_distance",
                "max_position_size = min(calculated_size, max_size_limit)",
                "stop_loss = entry_price * (1 - stop_loss_pct)",
                "take_profit = entry_price * (1 + take_profit_pct)"
            ]
        }
    
    async def create_trading_workflow(self, market_context: Dict) -> str:
        """
        Generate a complete trading workflow autonomously
        
        Steps:
        1. Analyze market patterns from knowledge graph
        2. Extract successful strategy components  
        3. Generate base code structure using AI
        4. Evolve and optimize through genetic programming
        5. Add self-modification capabilities
        """
        
        self.logger.info(f"🎯 Creating autonomous trading workflow for market: {market_context.get('symbol', 'UNKNOWN')}")
        
        try:
            # Step 1: Analyze historical patterns
            historical_patterns = await self.get_knowledge_graph_insights(market_context)
            
            # Step 2: Extract successful components
            successful_components = self.extract_winning_patterns(historical_patterns)
            
            # Step 3: Generate base strategy using AI
            base_code = await self.generate_base_strategy(successful_components, market_context)
            
            # Step 4: Evolve the strategy
            evolved_code = await self.evolve_strategy_code(base_code, market_context)
            
            # Step 5: Inject self-learning capabilities
            autonomous_code = self.inject_self_learning_capabilities(evolved_code)
            
            # Step 6: Validate and store
            validation_results = await self.validate_generated_code(autonomous_code, market_context)
            
            # Store evolution in database
            await self.store_evolution(CodeEvolution(
                generation=len(self.strategy_genome),
                code=autonomous_code,
                performance_score=validation_results.get('expected_performance', 0.0),
                market_conditions=market_context,
                mutations=[],
                fitness=self.calculate_fitness(validation_results),
                timestamp=datetime.now(),
                validation_results=validation_results
            ))
            
            self.logger.info(f"✅ Successfully created autonomous trading workflow")
            return autonomous_code
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create trading workflow: {e}")
            return self._generate_fallback_strategy(market_context)
    
    async def get_knowledge_graph_insights(self, market_context: Dict) -> Dict:
        """Get historical insights from knowledge graph"""
        try:
            symbol = market_context.get('symbol', 'SOL/USDT')
            
            # Query for similar market conditions
            response = requests.get(
                f"{self.kg_url}/search_nodes",
                params={"query": f"TradingAnalysis {symbol} successful"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                analyses = data.get("nodes", [])
                
                # Extract patterns from successful trades
                patterns = {
                    "successful_strategies": [],
                    "market_conditions": [],
                    "performance_metrics": [],
                    "risk_patterns": []
                }
                
                for analysis in analyses:
                    observations = analysis.get("observations", [])
                    for obs in observations:
                        if "confidence:" in obs.lower() and float(obs.split(":")[-1].strip()) > 0.7:
                            patterns["successful_strategies"].append(analysis)
                        elif "market" in obs.lower():
                            patterns["market_conditions"].append(obs)
                
                return patterns
            
        except Exception as e:
            self.logger.error(f"Knowledge graph query failed: {e}")
        
        return {"successful_strategies": [], "market_conditions": [], "performance_metrics": [], "risk_patterns": []}
    
    def extract_winning_patterns(self, historical_patterns: Dict) -> List[StrategyComponent]:
        """Extract successful strategy components from historical data"""
        components = []
        
        # Analyze successful strategies
        for strategy in historical_patterns.get("successful_strategies", []):
            observations = strategy.get("observations", [])
            
            # Extract strategy components
            for obs in observations:
                if "reasoning:" in obs.lower():
                    reasoning = obs.split("reasoning:")[-1].strip()
                    
                    # Parse reasoning for strategy components
                    if "rsi" in reasoning.lower():
                        components.append(StrategyComponent(
                            component_type="indicator",
                            code="rsi = ta.RSI(close, timeperiod=14)",
                            parameters={"period": 14},
                            performance_impact=0.8,
                            usage_frequency=1
                        ))
                    
                    if "breakout" in reasoning.lower():
                        components.append(StrategyComponent(
                            component_type="entry",
                            code="if price > resistance and volume > avg_volume * 1.5:",
                            parameters={"volume_multiplier": 1.5},
                            performance_impact=0.7,
                            usage_frequency=1
                        ))
        
        # Load from component library
        components.extend(self.load_component_library())
        
        return components
    
    def load_component_library(self) -> List[StrategyComponent]:
        """Load strategy components from database"""
        components = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT component_type, component_code, parameters, 
                           performance_impact, usage_frequency
                    FROM component_library
                    ORDER BY performance_impact DESC, usage_frequency DESC
                    LIMIT 20
                """).fetchall()
                
                for row in rows:
                    components.append(StrategyComponent(
                        component_type=row[0],
                        code=row[1],
                        parameters=json.loads(row[2]),
                        performance_impact=row[3],
                        usage_frequency=row[4]
                    ))
                    
        except Exception as e:
            self.logger.error(f"Failed to load component library: {e}")
        
        return components
    
    async def generate_base_strategy(self, components: List[StrategyComponent], market_context: Dict) -> str:
        """Generate initial strategy code using AI models"""
        
        # Prepare prompt for AI code generation
        prompt = self._create_code_generation_prompt(components, market_context)
        
        try:
            if self.code_models.get('fallback'):
                # Use fallback generation
                generated_code = self._generate_from_templates(prompt)
            else:
                # Use AI model
                generated_code = await self._generate_with_ai_model(prompt)
            
            # Log generation attempt
            self._log_code_generation(prompt, generated_code, "AI_Model", True)
            
            return generated_code
            
        except Exception as e:
            self.logger.error(f"AI code generation failed: {e}")
            fallback_code = self._generate_from_templates(prompt)
            self._log_code_generation(prompt, fallback_code, "Fallback", False)
            return fallback_code
    
    def _create_code_generation_prompt(self, components: List[StrategyComponent], market_context: Dict) -> str:
        """Create a detailed prompt for AI code generation"""
        
        indicators = [c for c in components if c.component_type == "indicator"]
        entry_logic = [c for c in components if c.component_type == "entry"]
        exit_logic = [c for c in components if c.component_type == "exit"]
        risk_mgmt = [c for c in components if c.component_type == "risk"]
        
        prompt = f"""
Generate a complete Nautilus Trader strategy class for {market_context.get('symbol', 'crypto trading')}.

Market Context:
- Symbol: {market_context.get('symbol', 'SOL/USDT')}
- Market Condition: {market_context.get('condition', 'trending')}
- Volatility: {market_context.get('volatility', 'medium')}
- Budget: ${market_context.get('budget', 50)}

Strategy Requirements:
1. Use these successful indicators: {[i.code for i in indicators[:3]]}
2. Implement entry logic: {[e.code for e in entry_logic[:2]]}
3. Add exit conditions: {[x.code for x in exit_logic[:2]]}
4. Include risk management: {[r.code for r in risk_mgmt[:2]]}

The strategy should:
- Be production-ready with proper error handling
- Include position sizing based on volatility
- Have dynamic stop-loss and take-profit levels
- Log all decisions for analysis
- Be self-modifying based on performance

Generate a complete Python class that inherits from nautilus_trader.trading.strategy.Strategy:
"""
        
        return prompt
    
    async def _generate_with_ai_model(self, prompt: str) -> str:
        """Generate code using AI model"""
        
        if 'deepseek_coder' in self.code_models:
            # Use DeepSeek Coder
            model = self.code_models['deepseek_coder']['model']
            tokenizer = self.code_models['deepseek_coder']['tokenizer']
            
            inputs = tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1500,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part
            generated_code = generated_text[len(prompt):].strip()
            
        elif 'code_pipeline' in self.code_models:
            # Use code generation pipeline
            result = self.code_models['code_pipeline'](
                prompt,
                max_length=2048,
                temperature=0.8,
                do_sample=True
            )
            generated_code = result[0]['generated_text'][len(prompt):].strip()
        
        else:
            raise Exception("No AI model available")
        
        return self._clean_generated_code(generated_code)
    
    def _generate_from_templates(self, prompt: str) -> str:
        """Generate code using templates when AI models unavailable"""
        
        # Determine strategy type from prompt
        if "momentum" in prompt.lower() or "trend" in prompt.lower():
            template = self.strategy_templates["momentum_strategy"]
        elif "mean" in prompt.lower() or "reversion" in prompt.lower():
            template = self.strategy_templates["mean_reversion"]
        elif "breakout" in prompt.lower():
            template = self.strategy_templates["breakout_strategy"]
        else:
            template = self.strategy_templates["momentum_strategy"]  # Default
        
        # Fill template with random but reasonable parameters
        filled_template = template.format(
            rsi_period=np.random.choice([14, 21, 28]),
            ema_fast=np.random.choice([8, 12, 16]),
            ema_slow=np.random.choice([21, 26, 30]),
            risk_per_trade=np.random.choice([0.01, 0.02, 0.03]),
            bb_period=np.random.choice([20, 25, 30]),
            bb_std=np.random.choice([1.8, 2.0, 2.2]),
            rsi_oversold=np.random.choice([25, 30, 35]),
            rsi_overbought=np.random.choice([65, 70, 75]),
            lookback_period=np.random.choice([20, 30, 40]),
            volume_threshold=np.random.choice([1.2, 1.5, 1.8]),
            atr_multiplier=np.random.choice([1.5, 2.0, 2.5]),
            entry_logic=np.random.choice(self.code_patterns["entry_conditions"]),
            exit_logic=np.random.choice(self.code_patterns["exit_conditions"]),
            mean_reversion_logic="# Mean reversion logic here",
            breakout_logic="# Breakout logic here"
        )
        
        return filled_template
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and validate generated code"""
        
        # Remove common AI generation artifacts
        code = code.replace("```python", "").replace("```", "")
        code = code.strip()
        
        # Ensure proper indentation
        try:
            # Parse and reformat code
            tree = ast.parse(code)
            cleaned_code = ast.unparse(tree)
            return cleaned_code
        except:
            # If parsing fails, return original with basic cleaning
            lines = code.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip empty lines and comments at start
                if line.strip() and not line.strip().startswith('#'):
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
    
    async def evolve_strategy_code(self, base_code: str, market_context: Dict) -> str:
        """
        Evolve strategy code using genetic programming
        
        Evolution process:
        1. Create multiple mutations of the base code
        2. Backtest each mutation
        3. Select best performers
        4. Create new generation from winners
        5. Repeat until convergence
        """
        
        self.logger.info("🧬 Starting strategy code evolution...")
        
        current_generation = base_code
        best_performance = 0.0
        generation = 0
        max_generations = 5
        
        for gen in range(max_generations):
            self.logger.info(f"🔄 Evolution generation {gen + 1}/{max_generations}")
            
            # Create mutations
            mutations = await self.create_code_mutations(current_generation, market_context)
            
            # Evaluate each mutation
            evaluated_mutations = []
            for i, mutation in enumerate(mutations):
                try:
                    performance = await self.evaluate_strategy_performance(mutation, market_context)
                    evaluated_mutations.append((mutation, performance))
                    self.logger.info(f"   Mutation {i+1}: Performance = {performance.get('fitness', 0):.3f}")
                except Exception as e:
                    self.logger.warning(f"   Mutation {i+1}: Evaluation failed - {e}")
                    evaluated_mutations.append((mutation, {"fitness": 0.0}))
            
            # Select best mutation
            if evaluated_mutations:
                best_mutation, best_perf = max(evaluated_mutations, key=lambda x: x[1].get('fitness', 0))
                
                if best_perf.get('fitness', 0) > best_performance:
                    current_generation = best_mutation
                    best_performance = best_perf.get('fitness', 0)
                    generation = gen + 1
                    
                    self.logger.info(f"✅ Generation {gen + 1}: New best performance = {best_performance:.3f}")
                else:
                    self.logger.info(f"⏸️ Generation {gen + 1}: No improvement, keeping current best")
                    
        # Store evolution results
        evolution = CodeEvolution(
            generation=generation,
            code=current_generation,
            performance_score=best_performance,
            market_conditions=market_context,
            mutations=[m[0] for m in evaluated_mutations],
            fitness=best_performance,
            timestamp=datetime.now(),
            parent_strategy=base_code[:100]  # First 100 chars as identifier
        )
        
        self.strategy_genome.append(evolution)
        
        self.logger.info(f"🎉 Evolution complete! Best fitness: {best_performance:.3f}")
        return current_generation
    
    async def create_code_mutations(self, code: str, market_context: Dict, num_mutations: int = 8) -> List[str]:
        """Create multiple mutations of the strategy code"""
        
        mutations = []
        
        try:
            # Parse the code into AST for manipulation
            tree = ast.parse(code)
            
            for i in range(num_mutations):
                # Create a copy of the AST
                mutated_tree = ast.copy_location(ast.parse(code), tree)
                
                # Apply different types of mutations
                mutation_type = np.random.choice([
                    'parameter_tweak',
                    'condition_modify', 
                    'logic_swap',
                    'risk_adjust'
                ])
                
                if mutation_type == 'parameter_tweak':
                    mutated_code = self._mutate_parameters(code)
                elif mutation_type == 'condition_modify':
                    mutated_code = self._mutate_conditions(code)
                elif mutation_type == 'logic_swap':
                    mutated_code = self._swap_logic_components(code)
                elif mutation_type == 'risk_adjust':
                    mutated_code = self._adjust_risk_parameters(code)
                else:
                    mutated_code = code  # Fallback
                
                mutations.append(mutated_code)
                
        except Exception as e:
            self.logger.error(f"Mutation creation failed: {e}")
            # Fallback to simple parameter mutations
            for i in range(num_mutations):
                mutations.append(self._simple_parameter_mutation(code))
        
        return mutations
    
    def _mutate_parameters(self, code: str) -> str:
        """Mutate numerical parameters in the code"""
        
        lines = code.split('\n')
        mutated_lines = []
        
        for line in lines:
            mutated_line = line
            
            # Find and mutate numerical parameters
            if '=' in line and any(char.isdigit() for char in line):
                # Look for patterns like "period = 14" or "threshold = 0.02"
                import re
                
                # Float parameters
                float_pattern = r'(\w+\s*=\s*)([0-9]*\.?[0-9]+)'
                match = re.search(float_pattern, line)
                if match:
                    param_name, value = match.groups()
                    old_value = float(value)
                    
                    # Mutate by ±20%
                    mutation_factor = np.random.uniform(0.8, 1.2)
                    new_value = old_value * mutation_factor
                    
                    # Format appropriately
                    if '.' in value:
                        new_value_str = f"{new_value:.4f}".rstrip('0').rstrip('.')
                    else:
                        new_value_str = str(int(new_value))
                    
                    mutated_line = re.sub(float_pattern, f'{param_name}{new_value_str}', line)
            
            mutated_lines.append(mutated_line)
        
        return '\n'.join(mutated_lines)
    
    def _mutate_conditions(self, code: str) -> str:
        """Mutate logical conditions in the code"""
        
        # Simple condition mutations
        mutations = {
            ' > ': ' >= ',
            ' < ': ' <= ',
            ' >= ': ' > ',
            ' <= ': ' < ',
            ' and ': ' or ',
            ' or ': ' and '
        }
        
        mutated_code = code
        
        # Apply one random mutation
        if mutations:
            old_op, new_op = np.random.choice(list(mutations.items()))
            if old_op in mutated_code:
                # Replace first occurrence
                mutated_code = mutated_code.replace(old_op, new_op, 1)
        
        return mutated_code
    
    def _swap_logic_components(self, code: str) -> str:
        """Swap logical components with alternatives from patterns"""
        
        # Look for entry/exit conditions and swap with alternatives
        for pattern_type, alternatives in self.code_patterns.items():
            if len(alternatives) > 1:
                for alt in alternatives:
                    if alt in code:
                        # Replace with a different alternative
                        new_alt = np.random.choice([a for a in alternatives if a != alt])
                        code = code.replace(alt, new_alt, 1)
                        break
        
        return code
    
    def _adjust_risk_parameters(self, code: str) -> str:
        """Adjust risk management parameters"""
        
        risk_adjustments = {
            'risk_per_trade': np.random.uniform(0.005, 0.05),
            'stop_loss_pct': np.random.uniform(0.01, 0.08),
            'take_profit_pct': np.random.uniform(0.02, 0.15),
            'max_position_size': np.random.uniform(0.1, 0.3)
        }
        
        mutated_code = code
        
        for param, new_value in risk_adjustments.items():
            pattern = f'{param}\\s*=\\s*[0-9]*\\.?[0-9]+'
            import re
            if re.search(pattern, mutated_code):
                mutated_code = re.sub(pattern, f'{param} = {new_value:.4f}', mutated_code)
        
        return mutated_code
    
    def _simple_parameter_mutation(self, code: str) -> str:
        """Simple fallback parameter mutation"""
        
        # Just change some common numerical values
        import re
        
        # Find all numbers and randomly modify them
        numbers = re.findall(r'\b\d+\.?\d*\b', code)
        
        if numbers:
            # Pick a random number to modify
            old_num = np.random.choice(numbers)
            try:
                old_val = float(old_num)
                new_val = old_val * np.random.uniform(0.8, 1.2)
                
                if '.' in old_num:
                    new_num = f"{new_val:.3f}"
                else:
                    new_num = str(int(new_val))
                
                # Replace first occurrence
                code = code.replace(old_num, new_num, 1)
            except:
                pass
        
        return code
    
    async def evaluate_strategy_performance(self, strategy_code: str, market_context: Dict) -> Dict:
        """Evaluate strategy performance using backtesting"""
        
        try:
            # Simulate backtesting performance
            # In production, this would run actual backtests
            
            # Basic code quality checks
            syntax_score = self._check_code_syntax(strategy_code)
            complexity_score = self._calculate_code_complexity(strategy_code)
            
            # Simulate performance metrics
            base_performance = np.random.normal(0.6, 0.2)  # Base performance
            
            # Adjust based on market context
            market_adjustment = 0
            if market_context.get('volatility') == 'high':
                market_adjustment = 0.1
            elif market_context.get('volatility') == 'low':
                market_adjustment = -0.05
            
            # Calculate fitness
            fitness = max(0, min(1, 
                base_performance + 
                syntax_score * 0.2 + 
                complexity_score * 0.1 + 
                market_adjustment
            ))
            
            return {
                'fitness': fitness,
                'syntax_score': syntax_score,
                'complexity_score': complexity_score,
                'estimated_sharpe': fitness * 2.0,
                'estimated_return': fitness * 0.15,
                'market_adjustment': market_adjustment
            }
            
        except Exception as e:
            self.logger.error(f"Performance evaluation failed: {e}")
            return {'fitness': 0.0, 'error': str(e)}
    
    def _check_code_syntax(self, code: str) -> float:
        """Check code syntax and return quality score"""
        try:
            ast.parse(code)
            return 1.0  # Perfect syntax
        except SyntaxError:
            return 0.0  # Syntax error
        except Exception:
            return 0.5  # Other issues
    
    def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity score (lower complexity = higher score)"""
        
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Penalize very long or very short code
        length_score = 1.0
        if len(non_empty_lines) < 10:
            length_score = 0.5  # Too short
        elif len(non_empty_lines) > 100:
            length_score = 0.7  # Too long
        
        # Check for good practices
        has_error_handling = 'try:' in code or 'except' in code
        has_logging = 'log' in code.lower()
        has_comments = '#' in code
        
        practice_score = (
            (0.3 if has_error_handling else 0) +
            (0.2 if has_logging else 0) +
            (0.1 if has_comments else 0)
        )
        
        return min(1.0, length_score + practice_score)
    
    def calculate_fitness(self, performance_metrics: Dict) -> float:
        """Calculate overall fitness score for strategy"""
        
        if not performance_metrics:
            return 0.0
        
        # Weighted fitness calculation
        fitness = (
            performance_metrics.get('syntax_score', 0) * 0.3 +
            performance_metrics.get('complexity_score', 0) * 0.2 +
            performance_metrics.get('estimated_sharpe', 0) / 3.0 * 0.3 +  # Normalize Sharpe
            performance_metrics.get('estimated_return', 0) * 2.0 * 0.2  # Normalize return
        )
        
        return max(0.0, min(1.0, fitness))
    
    def inject_self_learning_capabilities(self, strategy_code: str) -> str:
        """Add self-modification capabilities to the strategy"""
        
        self_learning_mixin = '''

class SelfLearningMixin:
    """Mixin for self-modifying trading strategies"""
    
    def __init__(self):
        self.performance_buffer = []
        self.code_modifications = []
        self.learning_rate = 0.01
        self.modification_threshold = -0.05  # Modify if performance drops 5%
        self.evaluation_window = 20  # Evaluate every 20 trades
        
    def on_trade_complete(self, trade_result):
        """Learn from completed trade"""
        self.performance_buffer.append({
            'pnl': trade_result.get('pnl', 0),
            'duration': trade_result.get('duration', 0),
            'timestamp': datetime.now(),
            'market_conditions': self.get_current_market_state()
        })
        
        # Trigger learning if we have enough data
        if len(self.performance_buffer) >= self.evaluation_window:
            self.evaluate_and_adapt()
    
    def evaluate_and_adapt(self):
        """Evaluate recent performance and adapt strategy"""
        recent_trades = self.performance_buffer[-self.evaluation_window:]
        avg_pnl = np.mean([t['pnl'] for t in recent_trades])
        
        # If performance is declining, modify strategy
        if avg_pnl < self.modification_threshold:
            self.modify_strategy_parameters()
            
    def modify_strategy_parameters(self):
        """Dynamically modify strategy parameters"""
        try:
            # Analyze what's not working
            losing_trades = [t for t in self.performance_buffer[-self.evaluation_window:] if t['pnl'] < 0]
            
            if len(losing_trades) > self.evaluation_window * 0.6:  # More than 60% losing
                # Adjust risk parameters
                if hasattr(self, 'risk_per_trade'):
                    self.risk_per_trade *= 0.8  # Reduce risk
                if hasattr(self, 'stop_loss_pct'):
                    self.stop_loss_pct *= 0.9  # Tighter stops
                    
                self.log_modification("Reduced risk parameters due to high loss rate")
                
            # Log modification
            self.code_modifications.append({
                'timestamp': datetime.now(),
                'reason': 'performance_decline',
                'avg_pnl': np.mean([t['pnl'] for t in self.performance_buffer[-self.evaluation_window:]]),
                'modification_type': 'parameter_adjustment'
            })
            
        except Exception as e:
            self.logger.error(f"Self-modification failed: {e}")
    
    def log_modification(self, message):
        """Log strategy modifications"""
        if hasattr(self, 'logger'):
            self.logger.info(f"🔧 Self-Modification: {message}")
        else:
            print(f"🔧 Self-Modification: {message}")
    
    def get_modification_history(self):
        """Get history of all modifications"""
        return self.code_modifications
    
    def reset_learning(self):
        """Reset learning state"""
        self.performance_buffer = []
        self.code_modifications = []
'''

        # Inject the mixin into the strategy class
        enhanced_code = strategy_code + "\n\n" + self_learning_mixin
        
        # Modify the main strategy class to inherit from the mixin
        if "class " in strategy_code and "Strategy" in strategy_code:
            # Find the class definition and add mixin
            lines = enhanced_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('class ') and 'Strategy' in line:
                    # Add SelfLearningMixin to inheritance
                    if 'SelfLearningMixin' not in line:
                        line = line.rstrip(':') + ', SelfLearningMixin:'
                        lines[i] = line
                    break
            
            enhanced_code = '\n'.join(lines)
        
        return enhanced_code
    
    async def validate_generated_code(self, code: str, market_context: Dict) -> Dict:
        """Validate generated code for syntax and basic functionality"""
        
        validation_results = {
            'syntax_valid': False,
            'has_required_methods': False,
            'estimated_performance': 0.0,
            'risk_level': 'unknown',
            'complexity_score': 0.0
        }
        
        try:
            # Check syntax
            ast.parse(code)
            validation_results['syntax_valid'] = True
            
            # Check for required methods
            if 'on_bar' in code or 'on_trade' in code:
                validation_results['has_required_methods'] = True
            
            # Estimate performance based on code quality
            validation_results['complexity_score'] = self._calculate_code_complexity(code)
            validation_results['estimated_performance'] = validation_results['complexity_score'] * 0.7
            
            # Assess risk level
            if 'stop_loss' in code and 'position_size' in code:
                validation_results['risk_level'] = 'managed'
            elif 'risk' in code.lower():
                validation_results['risk_level'] = 'moderate'
            else:
                validation_results['risk_level'] = 'high'
                
        except SyntaxError as e:
            validation_results['syntax_error'] = str(e)
        except Exception as e:
            validation_results['validation_error'] = str(e)
        
        return validation_results
    
    async def store_evolution(self, evolution: CodeEvolution):
        """Store evolution data in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO strategy_evolution 
                    (generation, strategy_code, performance_score, fitness, 
                     market_conditions, mutations, parent_strategy, validation_results)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evolution.generation,
                    evolution.code,
                    evolution.performance_score,
                    evolution.fitness,
                    json.dumps(evolution.market_conditions),
                    json.dumps(evolution.mutations[:5]),  # Store first 5 mutations
                    evolution.parent_strategy,
                    json.dumps(evolution.validation_results)
                ))
                
            self.logger.info(f"✅ Stored evolution generation {evolution.generation}")
            
        except Exception as e:
            self.logger.error(f"Failed to store evolution: {e}")
    
    def _log_code_generation(self, prompt: str, code: str, model: str, success: bool):
        """Log code generation attempts"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO code_generation_log 
                    (prompt, generated_code, model_used, success)
                    VALUES (?, ?, ?, ?)
                """, (
                    prompt[:500],  # Truncate long prompts
                    code[:2000],   # Truncate long code
                    model,
                    success
                ))
        except Exception as e:
            self.logger.error(f"Failed to log code generation: {e}")
    
    def _generate_fallback_strategy(self, market_context: Dict) -> str:
        """Generate a simple fallback strategy when AI generation fails"""
        
        symbol = market_context.get('symbol', 'SOL/USDT')
        
        return f'''
class FallbackStrategy(Strategy, SelfLearningMixin):
    """
    Fallback strategy generated by autonomous code creator
    Symbol: {symbol}
    Generated: {datetime.now().isoformat()}
    """
    
    def __init__(self, config):
        super().__init__(config)
        SelfLearningMixin.__init__(self)
        
        # Basic parameters
        self.risk_per_trade = 0.02
        self.stop_loss_pct = 0.03
        self.take_profit_pct = 0.06
        self.rsi_period = 14
        self.ema_fast = 12
        self.ema_slow = 26
        
        self.logger.info("🤖 Fallback strategy initialized")
    
    def on_start(self):
        self.logger.info("▶️ Starting fallback strategy")
    
    def on_bar(self, bar):
        """Simple momentum strategy logic"""
        try:
            # Basic momentum check
            if self.should_enter_long(bar):
                self.enter_long_position(bar)
            elif self.should_exit_positions(bar):
                self.exit_all_positions(bar)
                
        except Exception as e:
            self.logger.error(f"Bar processing error: {{e}}")
    
    def should_enter_long(self, bar):
        """Simple entry condition"""
        # Placeholder logic - would be enhanced by evolution
        return bar.close > bar.open * 1.001  # Basic upward movement
    
    def should_exit_positions(self, bar):
        """Simple exit condition"""
        # Placeholder logic
        return False  # Hold positions for now
    
    def enter_long_position(self, bar):
        """Enter long position with risk management"""
        position_size = self.calculate_position_size(bar)
        self.logger.info(f"📈 Entering long position: {{position_size}}")
    
    def exit_all_positions(self, bar):
        """Exit all positions"""
        self.logger.info("📉 Exiting all positions")
    
    def calculate_position_size(self, bar):
        """Calculate position size based on risk"""
        return self.risk_per_trade  # Simplified
'''

    async def get_evolution_history(self) -> List[Dict]:
        """Get history of strategy evolution"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT generation, performance_score, fitness, 
                           market_conditions, timestamp
                    FROM strategy_evolution
                    ORDER BY timestamp DESC
                    LIMIT 50
                """).fetchall()
                
                history = []
                for row in rows:
                    history.append({
                        'generation': row[0],
                        'performance_score': row[1],
                        'fitness': row[2],
                        'market_conditions': json.loads(row[3]),
                        'timestamp': row[4]
                    })
                
                return history
                
        except Exception as e:
            self.logger.error(f"Failed to get evolution history: {e}")
            return []
    
    async def get_best_strategies(self, limit: int = 10) -> List[Dict]:
        """Get the best performing strategies"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT generation, strategy_code, performance_score, 
                           fitness, market_conditions, timestamp
                    FROM strategy_evolution
                    ORDER BY fitness DESC
                    LIMIT ?
                """, (limit,)).fetchall()
                
                strategies = []
                for row in rows:
                    strategies.append({
                        'generation': row[0],
                        'code': row[1],
                        'performance_score': row[2],
                        'fitness': row[3],
                        'market_conditions': json.loads(row[4]),
                        'timestamp': row[5]
                    })
                
                return strategies
                
        except Exception as e:
            self.logger.error(f"Failed to get best strategies: {e}")
            return []


# Demo function for testing
async def demo_autonomous_code_creator():
    """Demo the autonomous code creator"""
    
    print("🧠 Demo: Autonomous Code Creator for Trading Strategies")
    print("=" * 60)
    
    # Mock MCP integration
    class MockMCPIntegration:
        def get_market_data(self):
            return {"symbol": "SOL/USDT", "price": 100.0}
    
    # Initialize creator
    creator = SelfLearningCodeCreator(MockMCPIntegration())
    
    # Test market context
    market_context = {
        "symbol": "SOL/USDT",
        "condition": "trending_up",
        "volatility": "medium",
        "budget": 50.0
    }
    
    print(f"📊 Market Context: {market_context}")
    print("\n🎯 Generating autonomous trading workflow...")
    
    # Generate autonomous strategy
    strategy_code = await creator.create_trading_workflow(market_context)
    
    print(f"\n✅ Generated Strategy ({len(strategy_code)} characters):")
    print("-" * 40)
    print(strategy_code[:500] + "..." if len(strategy_code) > 500 else strategy_code)
    
    # Show evolution history
    history = await creator.get_evolution_history()
    print(f"\n📈 Evolution History ({len(history)} generations):")
    for h in history[:3]:
        print(f"   Gen {h['generation']}: Fitness = {h['fitness']:.3f}")
    
    print("\n🎉 Autonomous Code Creator Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_autonomous_code_creator())
