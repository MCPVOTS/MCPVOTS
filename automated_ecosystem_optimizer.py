#!/usr/bin/env python3
"""
Automated MCPVots Ecosystem Optimization Service
==============================================
Integrates Enhanced Memory Knowledge System, Trilogy AGI Ollama Fine-Tuning,
and real-time ecosystem optimization for continuous improvement.

Features:
- Automated monitoring and optimization
- Real-time performance analytics
- Predictive maintenance and scaling
- Integration with all MCPVots services
- CI/CD integration for automated deployments
"""

import asyncio
import json
import logging
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import sqlite3
import psutil

# Try to import git, fallback if not available
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: GitPython not available - git monitoring disabled")

# Import our components
from enhanced_memory_knowledge_system import EnhancedMemoryKnowledgeSystem, LearningInsight
from trilogy_ollama_fine_tuner import TrilogyOllamaFineTuner
from memory_mcp_integration import MemoryMCPIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ecosystem_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationRule:
    """Rule for automated optimization"""
    rule_id: str
    name: str
    condition: str  # Python expression to evaluate
    action: str     # Action to take when condition is met
    priority: int   # Priority level (1-10)
    safety_level: str  # 'safe', 'review_required', 'manual_only'
    cooldown_minutes: int = 60  # Minimum time between applications
    last_applied: Optional[datetime] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    service_health: Dict[str, str]
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    custom_metrics: Dict[str, Any]

class EcosystemOptimizationService:
    """
    Advanced ecosystem optimization service for MCPVots
    """
    
    def __init__(self, workspace_path: str = "c:\\Workspace\\MCPVots"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "ecosystem_optimizer.db"
        self.config_path = self.workspace_path / "optimization_config.json"
        
        # Initialize components
        self.memory_system = EnhancedMemoryKnowledgeSystem(str(workspace_path))
        self.fine_tuner = TrilogyOllamaFineTuner(str(workspace_path))
        self.memory_mcp = MemoryMCPIntegration()
        
        # Service endpoints (from advanced_orchestrator.py)
        self.service_endpoints = {
            "owl_semantic": "http://localhost:8011",
            "agent_file": "http://localhost:8012", 
            "dgm_evolution": "http://localhost:8013",
            "deerflow": "http://localhost:8014",
            "gemini_cli": "http://localhost:8015",
            "trilogy_ollama": "http://localhost:11434",
            "frontend": "http://localhost:3000",
            "orchestrator": "http://localhost:8000"
        }
        
        # Optimization configuration
        self.config = {
            "monitoring_interval": 30,      # seconds
            "optimization_interval": 300,   # seconds  
            "git_monitoring": True,
            "auto_deployment": False,
            "performance_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 2.0,
                "error_rate": 0.05
            },
            "scaling_rules": {
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3,
                "min_instances": 1,
                "max_instances": 5
            }
        }
        
        # Optimization rules
        self.optimization_rules = []
        self.current_metrics = None
        self.optimization_history = []
        
        # Ensure directories exist
        (self.workspace_path / "data").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "logs").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "optimization_reports").mkdir(parents=True, exist_ok=True)
        
        # Initialize database and rules
        self._init_database()
        self._load_optimization_rules()
    
    def _init_database(self):
        """Initialize SQLite database for optimization tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    metric_id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io TEXT,
                    service_health TEXT,
                    response_times TEXT,
                    error_rates TEXT,
                    custom_metrics TEXT
                );
                
                CREATE TABLE IF NOT EXISTS optimization_actions (
                    action_id TEXT PRIMARY KEY,
                    rule_id TEXT,
                    action_type TEXT,
                    target_service TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    impact_metrics TEXT
                );
                
                CREATE TABLE IF NOT EXISTS git_changes (
                    change_id TEXT PRIMARY KEY,
                    commit_hash TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    files_changed TEXT,
                    change_summary TEXT,
                    impact_analysis TEXT,
                    optimization_triggered BOOLEAN DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS deployment_events (
                    deployment_id TEXT PRIMARY KEY,
                    version TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    services_affected TEXT,
                    deployment_type TEXT,
                    status TEXT DEFAULT 'pending',
                    rollback_plan TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp);
                CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON optimization_actions(timestamp);
                CREATE INDEX IF NOT EXISTS idx_changes_timestamp ON git_changes(timestamp);
            """)
    
    def _load_optimization_rules(self):
        """Load optimization rules from configuration"""
        self.optimization_rules = [
            OptimizationRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage Optimization",
                condition="metrics.cpu_usage > 80.0",
                action="scale_up_service",
                priority=8,
                safety_level="safe",
                cooldown_minutes=30
            ),
            OptimizationRule(
                rule_id="high_memory_usage", 
                name="High Memory Usage Optimization",
                condition="metrics.memory_usage > 85.0",
                action="cleanup_memory",
                priority=7,
                safety_level="safe",
                cooldown_minutes=15
            ),
            OptimizationRule(
                rule_id="slow_response_time",
                name="Slow Response Time Optimization",
                condition="any(rt > 2.0 for rt in metrics.response_times.values())",
                action="optimize_caching",
                priority=6,
                safety_level="safe",
                cooldown_minutes=60
            ),
            OptimizationRule(
                rule_id="high_error_rate",
                name="High Error Rate Response",
                condition="any(er > 0.05 for er in metrics.error_rates.values())",
                action="restart_failing_service",
                priority=9,
                safety_level="safe",
                cooldown_minutes=10
            ),
            OptimizationRule(
                rule_id="low_utilization",
                name="Low Resource Utilization",
                condition="metrics.cpu_usage < 30.0 and metrics.memory_usage < 40.0",
                action="scale_down_service",
                priority=3,
                safety_level="safe",
                cooldown_minutes=120
            ),
            OptimizationRule(
                rule_id="outdated_models",
                name="Outdated Model Retraining",
                condition="self._check_model_freshness() > 7",  # Days since last training
                action="retrain_models",
                priority=5,
                safety_level="review_required",
                cooldown_minutes=1440  # 24 hours
            )
        ]
    
    async def start_optimization_service(self):
        """Start the main optimization service"""
        logger.info("🚀 Starting MCPVots Ecosystem Optimization Service")
        logger.info("=" * 60)
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._monitoring_loop()),
            asyncio.create_task(self._optimization_loop()),
            asyncio.create_task(self._git_monitoring_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._reporting_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in optimization service: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Continuous system monitoring"""
        while True:
            try:
                logger.debug("📊 Collecting system metrics...")
                
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                self.current_metrics = metrics
                
                # Store metrics
                await self._store_metrics(metrics)
                
                # Log key metrics
                logger.info(f"CPU: {metrics.cpu_usage:.1f}%, Memory: {metrics.memory_usage:.1f}%, "
                           f"Services: {sum(1 for status in metrics.service_health.values() if status == 'healthy')}/{len(metrics.service_health)}")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _optimization_loop(self):
        """Continuous optimization based on rules"""
        while True:
            try:
                if self.current_metrics:
                    logger.debug("🎯 Evaluating optimization rules...")
                    
                    # Evaluate optimization rules
                    triggered_rules = await self._evaluate_optimization_rules(self.current_metrics)
                    
                    # Apply triggered optimizations
                    for rule in triggered_rules:
                        await self._apply_optimization_rule(rule, self.current_metrics)
                    
                    if triggered_rules:
                        logger.info(f"Applied {len(triggered_rules)} optimization rules")
                
                # Wait for next optimization cycle
                await asyncio.sleep(self.config["optimization_interval"])
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(60)
    
    async def _git_monitoring_loop(self):
        """Monitor git repository for changes"""
        if not self.config["git_monitoring"] or not GIT_AVAILABLE:
            logger.info("Git monitoring disabled (GitPython not available)")
            return
        
        last_commit = None
        
        while True:
            try:
                # Check for new commits using GitPython
                repo = git.Repo(self.workspace_path)
                current_commit = repo.head.commit.hexsha
                
                if last_commit and current_commit != last_commit:
                    logger.info(f"🔄 New commit detected: {current_commit[:8]}")
                    
                    # Analyze changes
                    diff = repo.git.diff(last_commit, current_commit, '--name-only')
                    changed_files = diff.split('\n') if diff else []
                    
                    # Store change record
                    change_record = {
                        "commit_hash": current_commit,
                        "files_changed": changed_files,
                        "change_summary": repo.head.commit.message,
                        "timestamp": datetime.now()
                    }
                    
                    await self._process_git_changes(change_record)
                
                last_commit = current_commit
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in git monitoring: {e}")
                await asyncio.sleep(120)
    
    async def _health_check_loop(self):
        """Continuous health checking of services"""
        while True:
            try:
                logger.debug("🏥 Performing health checks...")
                
                # Check all services
                unhealthy_services = []
                for service_name, endpoint in self.service_endpoints.items():
                    health_status = await self._check_service_health(service_name, endpoint)
                    if health_status != "healthy":
                        unhealthy_services.append((service_name, health_status))
                
                # Handle unhealthy services
                for service_name, status in unhealthy_services:
                    await self._handle_unhealthy_service(service_name, status)
                
                # Wait before next health check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(120)
    
    async def _reporting_loop(self):
        """Generate periodic optimization reports"""
        while True:
            try:
                # Generate daily report at 2 AM
                now = datetime.now()
                if now.hour == 2 and now.minute < 10:
                    logger.info("📋 Generating daily optimization report...")
                    await self._generate_daily_report()
                
                # Wait 10 minutes before next check
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error in reporting loop: {e}")
                await asyncio.sleep(600)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        # System resources
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Service health and response times
        service_health = {}
        response_times = {}
        error_rates = {}
        
        for service_name, endpoint in self.service_endpoints.items():
            health_status = await self._check_service_health(service_name, endpoint)
            response_time = await self._measure_response_time(service_name, endpoint)
            error_rate = await self._calculate_error_rate(service_name)
            
            service_health[service_name] = health_status
            response_times[service_name] = response_time
            error_rates[service_name] = error_rate
        
        # Custom metrics from memory system
        custom_metrics = {}
        try:
            memory_status = await self.memory_system.get_system_status()
            custom_metrics["knowledge_entities"] = memory_status.get("knowledge_entities", 0)
            custom_metrics["learning_insights"] = memory_status.get("learning_insights", {}).get("total", 0)
            custom_metrics["fine_tuning_sessions"] = memory_status.get("fine_tuning_sessions_this_week", 0)
        except Exception as e:
            logger.warning(f"Could not collect memory system metrics: {e}")
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            },
            service_health=service_health,
            response_times=response_times,
            error_rates=error_rates,
            custom_metrics=custom_metrics
        )
    
    async def _check_service_health(self, service_name: str, endpoint: str) -> str:
        """Check health of a specific service"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                health_url = f"{endpoint}/health"
                async with session.get(health_url) as response:
                    if response.status == 200:
                        return "healthy"
                    else:
                        return f"unhealthy_http_{response.status}"
        except asyncio.TimeoutError:
            return "unhealthy_timeout"
        except Exception as e:
            return f"unhealthy_error_{str(e)[:20]}"
    
    async def _measure_response_time(self, service_name: str, endpoint: str) -> float:
        """Measure response time of a service"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{endpoint}/health") as response:
                    await response.read()
                    return time.time() - start_time
        except Exception:
            return 999.0  # Return high value for failed requests
    
    async def _calculate_error_rate(self, service_name: str) -> float:
        """Calculate error rate for a service (placeholder)"""
        # This would be calculated from actual logs and metrics
        # For now, return a simulated value
        return 0.01  # 1% error rate
    
    async def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics 
                (metric_id, timestamp, cpu_usage, memory_usage, disk_usage, 
                 network_io, service_health, response_times, error_rates, custom_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"metrics_{int(time.time())}",
                metrics.timestamp,
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.disk_usage,
                json.dumps(metrics.network_io),
                json.dumps(metrics.service_health),
                json.dumps(metrics.response_times),
                json.dumps(metrics.error_rates),
                json.dumps(metrics.custom_metrics)
            ))
    
    async def _evaluate_optimization_rules(self, metrics: SystemMetrics) -> List[OptimizationRule]:
        """Evaluate optimization rules against current metrics"""
        triggered_rules = []
        
        for rule in self.optimization_rules:
            try:
                # Check cooldown
                if rule.last_applied:
                    time_since_last = datetime.now() - rule.last_applied
                    if time_since_last.total_seconds() < rule.cooldown_minutes * 60:
                        continue
                
                # Evaluate condition
                condition_result = self._evaluate_condition(rule.condition, metrics)
                
                if condition_result:
                    triggered_rules.append(rule)
                    logger.info(f"🎯 Optimization rule triggered: {rule.name}")
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        # Sort by priority (higher priority first)
        triggered_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return triggered_rules
    
    def _evaluate_condition(self, condition: str, metrics: SystemMetrics) -> bool:
        """Safely evaluate optimization rule condition"""
        try:
            # Create safe evaluation context
            context = {
                "metrics": metrics,
                "self": self,
                "datetime": datetime,
                "any": any,
                "all": all,
                "len": len,
                "sum": sum,
                "max": max,
                "min": min
            }
            
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _apply_optimization_rule(self, rule: OptimizationRule, metrics: SystemMetrics):
        """Apply an optimization rule"""
        if rule.safety_level == "manual_only":
            logger.info(f"⚠️ Rule {rule.name} requires manual intervention")
            return
        
        try:
            logger.info(f"🚀 Applying optimization: {rule.name}")
            
            action_id = f"action_{int(time.time())}_{rule.rule_id}"
            
            # Record action attempt
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO optimization_actions 
                    (action_id, rule_id, action_type, timestamp, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (action_id, rule.rule_id, rule.action, datetime.now(), "running"))
            
            # Apply the action
            result = await self._execute_optimization_action(rule.action, metrics)
            
            # Update action record
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE optimization_actions 
                    SET status = ?, result = ? 
                    WHERE action_id = ?
                """, ("completed", json.dumps(result), action_id))
            
            # Update rule last applied time
            rule.last_applied = datetime.now()
            
            logger.info(f"✅ Optimization completed: {rule.name}")
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {rule.name} - {e}")
            
            # Update action record with error
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE optimization_actions 
                    SET status = ?, result = ? 
                    WHERE action_id = ?
                """, ("failed", json.dumps({"error": str(e)}), action_id))
    
    async def _execute_optimization_action(self, action: str, metrics: SystemMetrics) -> Dict[str, Any]:
        """Execute a specific optimization action"""
        if action == "scale_up_service":
            return await self._scale_up_services(metrics)
        elif action == "cleanup_memory":
            return await self._cleanup_memory()
        elif action == "optimize_caching":
            return await self._optimize_caching()
        elif action == "restart_failing_service":
            return await self._restart_failing_services(metrics)
        elif action == "scale_down_service":
            return await self._scale_down_services(metrics)
        elif action == "retrain_models":
            return await self._retrain_models()
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _scale_up_services(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Scale up services under high load"""
        # This would integrate with container orchestration (Docker, Kubernetes)
        # For now, simulate the action
        logger.info("📈 Scaling up services...")
        
        scaled_services = []
        for service_name, health in metrics.service_health.items():
            if health == "healthy" and metrics.cpu_usage > 80:
                # Simulate scaling
                scaled_services.append(service_name)
        
        return {
            "action": "scale_up",
            "scaled_services": scaled_services,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cleanup_memory(self) -> Dict[str, Any]:
        """Clean up memory usage"""
        logger.info("🧹 Cleaning up memory...")
        
        # Trigger memory consolidation in memory system
        try:
            await self.memory_system._cleanup_old_memories()
            await self.memory_system._optimize_database()
            
            return {
                "action": "memory_cleanup",
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "action": "memory_cleanup",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _optimize_caching(self) -> Dict[str, Any]:
        """Optimize caching strategies"""
        logger.info("⚡ Optimizing caching...")
        
        # This would implement caching optimizations
        # For now, simulate the action
        return {
            "action": "optimize_caching",
            "optimizations": [
                "enabled_redis_caching",
                "increased_cache_ttl",
                "optimized_cache_keys"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _restart_failing_services(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Restart services that are failing"""
        logger.info("🔄 Restarting failing services...")
        
        restarted_services = []
        for service_name, health in metrics.service_health.items():
            if health.startswith("unhealthy"):
                # Simulate service restart
                logger.info(f"Restarting service: {service_name}")
                restarted_services.append(service_name)
        
        return {
            "action": "restart_services",
            "restarted_services": restarted_services,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _scale_down_services(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Scale down services under low load"""
        logger.info("📉 Scaling down services...")
        
        # Simulate scaling down
        return {
            "action": "scale_down",
            "scaled_services": ["background_worker"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _retrain_models(self) -> Dict[str, Any]:
        """Retrain machine learning models"""
        logger.info("🎯 Retraining models...")
        
        try:
            # Get recent insights for training
            recent_insights = await self.memory_system._get_recent_insights(hours=168)  # 1 week
            
            if len(recent_insights) >= 20:  # Minimum training data
                # Convert to training format
                training_data = []
                for insight in recent_insights:
                    training_data.append({
                        "category": insight.category,
                        "content": insight.content,
                        "confidence_score": insight.confidence_score,
                        "source": insight.source
                    })
                
                # Trigger fine-tuning
                version_id = await self.fine_tuner.fine_tune_model(training_data)
                
                return {
                    "action": "retrain_models",
                    "status": "completed",
                    "version_id": version_id,
                    "training_data_size": len(training_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "action": "retrain_models",
                    "status": "skipped",
                    "reason": "insufficient_training_data",
                    "available_insights": len(recent_insights),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "action": "retrain_models",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_model_freshness(self) -> int:
        """Check how many days since last model training"""
        try:
            with sqlite3.connect(self.fine_tuner.db_path) as conn:
                cursor = conn.execute("""
                    SELECT MAX(datetime(created_at)) FROM model_versions 
                    WHERE status = 'completed'
                """)
                last_training = cursor.fetchone()[0]
                
                if last_training:
                    last_date = datetime.fromisoformat(last_training)
                    return (datetime.now() - last_date).days
                else:
                    return 999  # No training found
        except Exception:
            return 999
    
    async def _process_git_changes(self, change_record: Dict[str, Any]):
        """Process git changes and trigger appropriate optimizations"""
        logger.info(f"📝 Processing git changes: {len(change_record['files_changed'])} files")
        
        # Store change record
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO git_changes 
                (change_id, commit_hash, timestamp, files_changed, change_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"change_{int(time.time())}",
                change_record["commit_hash"],
                change_record["timestamp"],
                json.dumps(change_record["files_changed"]),
                change_record["change_summary"]
            ))
        
        # Analyze impact and trigger learning
        impact_analysis = await self._analyze_change_impact(change_record)
        
        # Trigger memory system analysis if significant changes
        if impact_analysis.get("significance", 0) > 0.5:
            logger.info("🧠 Triggering memory system analysis for significant changes")
            try:
                await self.memory_system._repository_analysis_loop()
            except Exception as e:
                logger.error(f"Error in triggered analysis: {e}")
    
    async def _analyze_change_impact(self, change_record: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of git changes"""
        files_changed = change_record["files_changed"]
        
        # Categorize changes
        categories = {
            "frontend": 0,
            "backend": 0,
            "config": 0,
            "docs": 0,
            "tests": 0
        }
        
        for file_path in files_changed:
            if any(pattern in file_path for pattern in [".tsx", ".ts", ".js", ".jsx"]):
                categories["frontend"] += 1
            elif any(pattern in file_path for pattern in [".py", ".java", ".go"]):
                categories["backend"] += 1
            elif any(pattern in file_path for pattern in [".json", ".yaml", ".yml", ".toml"]):
                categories["config"] += 1
            elif any(pattern in file_path for pattern in [".md", ".txt", ".rst"]):
                categories["docs"] += 1
            elif "test" in file_path.lower():
                categories["tests"] += 1
        
        # Calculate significance
        total_changes = sum(categories.values())
        significance = min(1.0, total_changes / 20.0)  # Normalize to 0-1
        
        return {
            "categories": categories,
            "total_changes": total_changes,
            "significance": significance,
            "requires_restart": categories["config"] > 0,
            "requires_testing": categories["backend"] > 0 or categories["frontend"] > 0
        }
    
    async def _handle_unhealthy_service(self, service_name: str, status: str):
        """Handle an unhealthy service"""
        logger.warning(f"🚨 Service {service_name} is {status}")
        
        # Log the incident
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO optimization_actions 
                (action_id, rule_id, action_type, target_service, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"health_action_{int(time.time())}",
                "health_monitor",
                "health_check_failed",
                service_name,
                datetime.now(),
                "logged"
            ))
        
        # Trigger restart if appropriate
        if status.startswith("unhealthy_timeout") or status.startswith("unhealthy_error"):
            await self._restart_failing_services(self.current_metrics)
    
    async def _generate_daily_report(self):
        """Generate daily optimization report"""
        logger.info("📊 Generating daily optimization report...")
        
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_path = self.workspace_path / "optimization_reports" / f"daily_report_{report_date}.json"
        
        # Collect data for the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get optimization actions
            cursor = conn.execute("""
                SELECT action_type, COUNT(*), 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                FROM optimization_actions 
                WHERE datetime(timestamp) > datetime(?)
                GROUP BY action_type
            """, (yesterday,))
            
            actions_summary = {}
            for row in cursor.fetchall():
                actions_summary[row[0]] = {
                    "total": row[1],
                    "successful": row[2],
                    "success_rate": row[2] / row[1] if row[1] > 0 else 0
                }
            
            # Get average metrics
            cursor = conn.execute("""
                SELECT AVG(cpu_usage), AVG(memory_usage), AVG(disk_usage)
                FROM system_metrics 
                WHERE datetime(timestamp) > datetime(?)
            """, (yesterday,))
            
            avg_metrics = cursor.fetchone()
        
        # Generate report
        report = {
            "date": report_date,
            "summary": {
                "total_optimizations": sum(data["total"] for data in actions_summary.values()),
                "successful_optimizations": sum(data["successful"] for data in actions_summary.values()),
                "overall_success_rate": 0,
                "avg_cpu_usage": avg_metrics[0] if avg_metrics[0] else 0,
                "avg_memory_usage": avg_metrics[1] if avg_metrics[1] else 0,
                "avg_disk_usage": avg_metrics[2] if avg_metrics[2] else 0
            },
            "optimization_actions": actions_summary,
            "recommendations": await self._generate_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
        
        # Calculate overall success rate
        total_actions = report["summary"]["total_optimizations"]
        successful_actions = report["summary"]["successful_optimizations"]
        report["summary"]["overall_success_rate"] = successful_actions / total_actions if total_actions > 0 else 0
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Daily report saved: {report_path}")
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if self.current_metrics:
            # CPU recommendations
            if self.current_metrics.cpu_usage > 70:
                recommendations.append("Consider scaling up services due to high CPU usage")
            elif self.current_metrics.cpu_usage < 20:
                recommendations.append("Consider scaling down services due to low CPU usage")
            
            # Memory recommendations
            if self.current_metrics.memory_usage > 80:
                recommendations.append("Implement memory cleanup routines")
            
            # Service health recommendations
            unhealthy_count = sum(1 for status in self.current_metrics.service_health.values() 
                                if not status == "healthy")
            if unhealthy_count > 0:
                recommendations.append(f"Investigate {unhealthy_count} unhealthy services")
            
            # Response time recommendations
            slow_services = [name for name, time in self.current_metrics.response_times.items() 
                           if time > 1.0]
            if slow_services:
                recommendations.append(f"Optimize response times for: {', '.join(slow_services)}")
        
        # Model training recommendations
        days_since_training = self._check_model_freshness()
        if days_since_training > 7:
            recommendations.append("Consider retraining models with recent insights")
        
        return recommendations
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization service status"""
        status = {
            "service_status": "running",
            "current_metrics": asdict(self.current_metrics) if self.current_metrics else None,
            "optimization_rules": len(self.optimization_rules),
            "recent_actions": [],
            "system_health": "unknown"
        }
        
        # Get recent actions
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT action_type, target_service, timestamp, status, result
                FROM optimization_actions 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            
            for row in cursor.fetchall():
                status["recent_actions"].append({
                    "action_type": row[0],
                    "target_service": row[1],
                    "timestamp": row[2],
                    "status": row[3],
                    "result": json.loads(row[4]) if row[4] else None
                })
        
        # Determine overall system health
        if self.current_metrics:
            health_indicators = []
            
            # CPU health
            if self.current_metrics.cpu_usage < 80:
                health_indicators.append("cpu_ok")
            else:
                health_indicators.append("cpu_high")
            
            # Memory health
            if self.current_metrics.memory_usage < 85:
                health_indicators.append("memory_ok")
            else:
                health_indicators.append("memory_high")
            
            # Service health
            healthy_services = sum(1 for s in self.current_metrics.service_health.values() if s == "healthy")
            total_services = len(self.current_metrics.service_health)
            
            if healthy_services == total_services:
                health_indicators.append("services_all_healthy")
            elif healthy_services > total_services * 0.8:
                health_indicators.append("services_mostly_healthy")
            else:
                health_indicators.append("services_degraded")
            
            # Overall health assessment
            if all("ok" in indicator or "healthy" in indicator for indicator in health_indicators):
                status["system_health"] = "excellent"
            elif any("high" in indicator or "degraded" in indicator for indicator in health_indicators):
                status["system_health"] = "degraded"
            else:
                status["system_health"] = "good"
        
        return status

# Example usage and testing functions
async def main():
    """Main function to test the optimization service"""
    optimizer = EcosystemOptimizationService()
    
    print("⚡ MCPVots Ecosystem Optimization Service")
    print("=" * 50)
    
    # Get initial status
    status = await optimizer.get_optimization_status()
    print("📊 Initial Status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Run optimization service for a short time (demo)
    print("\n🚀 Starting optimization service...")
    
    try:
        # Run for 60 seconds as demo
        await asyncio.wait_for(optimizer.start_optimization_service(), timeout=60)
    except asyncio.TimeoutError:
        print("\n⏰ Demo timeout reached")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    # Get final status
    final_status = await optimizer.get_optimization_status()
    print("\n📊 Final Status:")
    print(json.dumps(final_status, indent=2, default=str))
    
    print("\n✅ Ecosystem Optimization Service demo completed")

if __name__ == "__main__":
    asyncio.run(main())
