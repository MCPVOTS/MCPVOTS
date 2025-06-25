#!/usr/bin/env python3
"""
DeerFlow Orchestrator MCP Server
Adaptive workflow management and data flow optimization system
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeerFlowServer:
    def __init__(self):
        self.workflows = {}
        self.executions = {}
        self.data_flows = {}
        self.optimizations = {}
        self.active_flows = {}
        self.performance_metrics = {}
        
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming MCP messages"""
        try:
            data = json.loads(message)
            method = data.get("method")
            params = data.get("params", {})
            msg_id = data.get("id")
            
            if method == "initialize":
                response = await self.initialize(params)
            elif method == "deerflow/create_workflow":
                response = await self.create_workflow(params)
            elif method == "deerflow/execute_workflow":
                response = await self.execute_workflow(params)
            elif method == "deerflow/optimize_flow":
                response = await self.optimize_flow(params)
            elif method == "deerflow/create_data_flow":
                response = await self.create_data_flow(params)
            elif method == "deerflow/monitor_execution":
                response = await self.monitor_execution(params)
            elif method == "deerflow/adaptive_scheduling":
                response = await self.adaptive_scheduling(params)
            elif method == "deerflow/get_performance":
                response = await self.get_performance_metrics(params)
            elif method == "deerflow/list_workflows":
                response = await self.list_workflows(params)
            elif method == "deerflow/pause_workflow":
                response = await self.pause_workflow(params)
            elif method == "deerflow/resume_workflow":
                response = await self.resume_workflow(params)
            elif method == "deerflow/stop_workflow":
                response = await self.stop_workflow(params)
            else:
                response = {"error": {"code": -32601, "message": "Method not found"}}
            
            if msg_id:
                response["id"] = msg_id
                
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": data.get("id") if 'data' in locals() else None
            }
            await websocket.send(json.dumps(error_response))

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize DeerFlow Orchestrator"""
        return {
            "jsonrpc": "2.0",
            "result": {
                "name": "DeerFlow Orchestrator",
                "version": "1.0.0",
                "capabilities": ["workflow-management", "data-flow", "optimization", "adaptive-execution"],
                "active_workflows": len(self.workflows),
                "running_executions": len([e for e in self.executions.values() if e.get("status") == "running"]),
                "total_optimizations": len(self.optimizations)
            }
        }

    async def create_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        workflow_name = params.get("name")
        workflow_steps = params.get("steps", [])
        workflow_config = params.get("config", {})
        
        if not workflow_name:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "workflow name is required"}
            }
        
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "name": workflow_name,
            "steps": workflow_steps,
            "config": workflow_config,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "version": 1,
            "executions": [],
            "optimization_score": 0.0,
            "estimated_duration": self.estimate_duration(workflow_steps),
            "dependencies": params.get("dependencies", []),
            "priority": params.get("priority", "medium")
        }
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow: {workflow_name} ({workflow_id})")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "workflow_id": workflow_id,
                "name": workflow_name,
                "steps": len(workflow_steps),
                "estimated_duration": workflow["estimated_duration"],
                "status": "created"
            }
        }

    async def execute_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow"""
        workflow_id = params.get("workflow_id")
        execution_params = params.get("execution_params", {})
        
        if not workflow_id or workflow_id not in self.workflows:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid workflow_id"}
            }
        
        workflow = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "current_step": 0,
            "total_steps": len(workflow["steps"]),
            "progress": 0.0,
            "execution_params": execution_params,
            "step_results": [],
            "metrics": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "io_operations": 0,
                "network_calls": 0
            }
        }
        
        self.executions[execution_id] = execution
        workflow["executions"].append(execution_id)
        
        # Start async execution
        asyncio.create_task(self.run_workflow_execution(execution_id))
        
        logger.info(f"Started execution: {execution_id} for workflow {workflow['name']}")
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "running",
                "estimated_completion": (datetime.now() + timedelta(seconds=workflow["estimated_duration"])).isoformat()
            }
        }

    async def run_workflow_execution(self, execution_id: str):
        """Run the actual workflow execution"""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution["workflow_id"]]
        
        try:
            for i, step in enumerate(workflow["steps"]):
                if execution["status"] != "running":
                    break
                
                execution["current_step"] = i
                execution["progress"] = (i / len(workflow["steps"])) * 100
                
                # Simulate step execution
                step_start = datetime.now()
                await self.execute_step(step, execution)
                step_duration = (datetime.now() - step_start).total_seconds()
                
                execution["step_results"].append({
                    "step_index": i,
                    "step_name": step.get("name", f"Step {i+1}"),
                    "status": "completed",
                    "duration": step_duration,
                    "completed_at": datetime.now().isoformat()
                })
                
                # Update metrics
                execution["metrics"]["cpu_usage"] += step.get("cpu_cost", 10)
                execution["metrics"]["memory_usage"] += step.get("memory_cost", 50)
                execution["metrics"]["io_operations"] += step.get("io_cost", 5)
                
                # Adaptive delay based on system load
                await asyncio.sleep(step.get("duration", 1))
            
            # Complete execution
            execution["status"] = "completed"
            execution["completed_at"] = datetime.now().isoformat()
            execution["progress"] = 100.0
            
            # Update workflow stats
            self.update_workflow_performance(workflow["id"], execution)
            
            logger.info(f"Completed execution: {execution_id}")
            
        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["failed_at"] = datetime.now().isoformat()
            logger.error(f"Execution {execution_id} failed: {e}")

    async def execute_step(self, step: Dict[str, Any], execution: Dict[str, Any]):
        """Execute a single workflow step"""
        step_type = step.get("type", "generic")
        
        if step_type == "data_processing":
            await self.process_data_step(step, execution)
        elif step_type == "api_call":
            await self.api_call_step(step, execution)
        elif step_type == "computation":
            await self.computation_step(step, execution)
        elif step_type == "file_operation":
            await self.file_operation_step(step, execution)
        else:
            # Generic step execution
            await asyncio.sleep(step.get("duration", 1))

    async def process_data_step(self, step: Dict[str, Any], execution: Dict[str, Any]):
        """Process a data processing step"""
        data_size = step.get("data_size", 1000)
        processing_time = data_size / 1000  # Simple simulation
        await asyncio.sleep(processing_time)
        execution["metrics"]["io_operations"] += data_size // 100

    async def api_call_step(self, step: Dict[str, Any], execution: Dict[str, Any]):
        """Process an API call step"""
        await asyncio.sleep(step.get("timeout", 2))
        execution["metrics"]["network_calls"] += 1

    async def computation_step(self, step: Dict[str, Any], execution: Dict[str, Any]):
        """Process a computation step"""
        complexity = step.get("complexity", "medium")
        compute_time = {"low": 0.5, "medium": 1.5, "high": 3.0}.get(complexity, 1.5)
        await asyncio.sleep(compute_time)
        execution["metrics"]["cpu_usage"] += compute_time * 20

    async def file_operation_step(self, step: Dict[str, Any], execution: Dict[str, Any]):
        """Process a file operation step"""
        operation = step.get("operation", "read")
        file_size = step.get("file_size", 1024)
        
        if operation == "write":
            await asyncio.sleep(file_size / 10000)  # Simulate write time
        else:
            await asyncio.sleep(file_size / 20000)  # Simulate read time
        
        execution["metrics"]["io_operations"] += file_size // 512

    async def optimize_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a workflow for better performance"""
        workflow_id = params.get("workflow_id")
        optimization_type = params.get("type", "performance")
        
        if not workflow_id or workflow_id not in self.workflows:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid workflow_id"}
            }
        
        workflow = self.workflows[workflow_id]
        optimization_id = str(uuid.uuid4())
        
        # Perform optimization analysis
        optimization_results = await self.analyze_and_optimize(workflow, optimization_type)
        
        optimization = {
            "id": optimization_id,
            "workflow_id": workflow_id,
            "type": optimization_type,
            "created_at": datetime.now().isoformat(),
            "results": optimization_results,
            "improvement_score": optimization_results.get("improvement_score", 0.0),
            "recommendations": optimization_results.get("recommendations", [])
        }
        
        self.optimizations[optimization_id] = optimization
        
        # Apply optimizations to workflow
        if optimization_results.get("apply_automatically", False):
            await self.apply_optimizations(workflow, optimization_results)
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "optimization_id": optimization_id,
                "workflow_id": workflow_id,
                "improvement_score": optimization_results.get("improvement_score", 0.0),
                "optimizations_found": len(optimization_results.get("recommendations", [])),
                "estimated_improvement": optimization_results.get("estimated_improvement", "0%")
            }
        }

    async def analyze_and_optimize(self, workflow: Dict[str, Any], optimization_type: str) -> Dict[str, Any]:
        """Analyze workflow and generate optimizations"""
        analysis = {
            "current_performance": workflow.get("optimization_score", 0.0),
            "bottlenecks": [],
            "recommendations": [],
            "improvement_score": 0.0,
            "estimated_improvement": "0%"
        }
        
        # Analyze workflow steps
        for i, step in enumerate(workflow["steps"]):
            step_duration = step.get("duration", 1)
            if step_duration > 5:  # Identify slow steps
                analysis["bottlenecks"].append({
                    "step_index": i,
                    "step_name": step.get("name", f"Step {i+1}"),
                    "issue": "slow_execution",
                    "current_duration": step_duration
                })
                
                analysis["recommendations"].append({
                    "step_index": i,
                    "recommendation": "optimize_algorithm",
                    "potential_improvement": "30-50%"
                })
        
        # Calculate improvement score
        if len(analysis["bottlenecks"]) > 0:
            analysis["improvement_score"] = min(len(analysis["bottlenecks"]) * 15, 75)
            analysis["estimated_improvement"] = f"{analysis['improvement_score']}%"
        
        return analysis

    async def apply_optimizations(self, workflow: Dict[str, Any], optimization_results: Dict[str, Any]):
        """Apply optimizations to a workflow"""
        for rec in optimization_results.get("recommendations", []):
            step_index = rec.get("step_index")
            if step_index < len(workflow["steps"]):
                step = workflow["steps"][step_index]
                
                if rec.get("recommendation") == "optimize_algorithm":
                    # Simulate optimization by reducing duration
                    original_duration = step.get("duration", 1)
                    step["duration"] = max(0.1, original_duration * 0.7)
        
        workflow["optimization_score"] = optimization_results.get("improvement_score", 0.0)
        workflow["version"] += 1

    async def create_data_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a data flow pipeline"""
        flow_name = params.get("name")
        sources = params.get("sources", [])
        transformations = params.get("transformations", [])
        destinations = params.get("destinations", [])
        
        if not flow_name:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "flow name is required"}
            }
        
        flow_id = str(uuid.uuid4())
        
        data_flow = {
            "id": flow_id,
            "name": flow_name,
            "sources": sources,
            "transformations": transformations,
            "destinations": destinations,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "throughput": 0.0,
            "error_rate": 0.0,
            "data_processed": 0
        }
        
        self.data_flows[flow_id] = data_flow
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "flow_id": flow_id,
                "name": flow_name,
                "sources": len(sources),
                "transformations": len(transformations),
                "destinations": len(destinations),
                "status": "created"
            }
        }

    async def monitor_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor workflow execution"""
        execution_id = params.get("execution_id")
        
        if not execution_id or execution_id not in self.executions:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid execution_id"}
            }
        
        execution = self.executions[execution_id]
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "execution_id": execution_id,
                "status": execution["status"],
                "progress": execution["progress"],
                "current_step": execution["current_step"],
                "total_steps": execution["total_steps"],
                "metrics": execution["metrics"],
                "started_at": execution["started_at"],
                "estimated_completion": self.estimate_completion(execution)
            }
        }

    async def adaptive_scheduling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implement adaptive scheduling for workflows"""
        strategy = params.get("strategy", "load_balanced")
        workflows = params.get("workflows", [])
        
        if not workflows:
            workflows = list(self.workflows.keys())
        
        schedule = {
            "strategy": strategy,
            "scheduled_workflows": [],
            "total_estimated_time": 0.0,
            "optimization_applied": False
        }
        
        # Simple scheduling algorithm
        sorted_workflows = sorted(
            [self.workflows[wid] for wid in workflows],
            key=lambda w: (w.get("priority", "medium"), w["estimated_duration"])
        )
        
        current_time = 0
        for workflow in sorted_workflows:
            schedule["scheduled_workflows"].append({
                "workflow_id": workflow["id"],
                "name": workflow["name"],
                "scheduled_start": current_time,
                "estimated_duration": workflow["estimated_duration"],
                "priority": workflow.get("priority", "medium")
            })
            current_time += workflow["estimated_duration"]
        
        schedule["total_estimated_time"] = current_time
        
        return {
            "jsonrpc": "2.0",
            "result": schedule
        }

    async def get_performance_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics"""
        time_range = params.get("time_range", "24h")
        
        metrics = {
            "time_range": time_range,
            "workflow_metrics": {
                "total_workflows": len(self.workflows),
                "completed_executions": len([e for e in self.executions.values() if e.get("status") == "completed"]),
                "failed_executions": len([e for e in self.executions.values() if e.get("status") == "failed"]),
                "running_executions": len([e for e in self.executions.values() if e.get("status") == "running"])
            },
            "performance": {
                "average_execution_time": self.calculate_average_execution_time(),
                "success_rate": self.calculate_success_rate(),
                "throughput": self.calculate_throughput(),
                "optimization_score": self.calculate_overall_optimization_score()
            },
            "resource_usage": {
                "avg_cpu_usage": 45.0,  # Simulated
                "avg_memory_usage": 60.0,
                "total_io_operations": sum(e.get("metrics", {}).get("io_operations", 0) for e in self.executions.values()),
                "total_network_calls": sum(e.get("metrics", {}).get("network_calls", 0) for e in self.executions.values())
            }
        }
        
        return {
            "jsonrpc": "2.0",
            "result": metrics
        }

    async def list_workflows(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all workflows"""
        status_filter = params.get("status")
        limit = params.get("limit", 50)
        
        workflows = list(self.workflows.values())
        
        if status_filter:
            workflows = [w for w in workflows if w.get("status") == status_filter]
        
        workflows = workflows[:limit]
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "workflows": workflows,
                "count": len(workflows),
                "total": len(self.workflows)
            }
        }

    async def pause_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a running workflow execution"""
        execution_id = params.get("execution_id")
        
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution["status"] == "running":
                execution["status"] = "paused"
                execution["paused_at"] = datetime.now().isoformat()
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"execution_id": execution_id, "status": "paused"}
                }
        
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid execution_id or execution not running"}
        }

    async def resume_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a paused workflow execution"""
        execution_id = params.get("execution_id")
        
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution["status"] == "paused":
                execution["status"] = "running"
                execution["resumed_at"] = datetime.now().isoformat()
                
                # Resume execution
                asyncio.create_task(self.run_workflow_execution(execution_id))
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"execution_id": execution_id, "status": "running"}
                }
        
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid execution_id or execution not paused"}
        }

    async def stop_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a workflow execution"""
        execution_id = params.get("execution_id")
        
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution["status"] in ["running", "paused"]:
                execution["status"] = "stopped"
                execution["stopped_at"] = datetime.now().isoformat()
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"execution_id": execution_id, "status": "stopped"}
                }
        
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid execution_id or execution already stopped"}
        }

    def estimate_duration(self, steps: List[Dict[str, Any]]) -> float:
        """Estimate workflow duration"""
        return sum(step.get("duration", 1) for step in steps)

    def estimate_completion(self, execution: Dict[str, Any]) -> str:
        """Estimate execution completion time"""
        if execution["status"] != "running":
            return execution.get("completed_at", "N/A")
        
        progress = execution["progress"] / 100.0
        if progress > 0:
            started = datetime.fromisoformat(execution["started_at"])
            elapsed = (datetime.now() - started).total_seconds()
            total_estimated = elapsed / progress
            completion_time = started + timedelta(seconds=total_estimated)
            return completion_time.isoformat()
        
        return "Unknown"

    def calculate_average_execution_time(self) -> float:
        """Calculate average execution time"""
        completed = [e for e in self.executions.values() if e.get("status") == "completed"]
        if not completed:
            return 0.0
        
        total_time = 0.0
        for execution in completed:
            started = datetime.fromisoformat(execution["started_at"])
            completed_time = datetime.fromisoformat(execution["completed_at"])
            total_time += (completed_time - started).total_seconds()
        
        return total_time / len(completed)

    def calculate_success_rate(self) -> float:
        """Calculate execution success rate"""
        if not self.executions:
            return 100.0
        
        completed = len([e for e in self.executions.values() if e.get("status") == "completed"])
        total_finished = len([e for e in self.executions.values() if e.get("status") in ["completed", "failed"]])
        
        if total_finished == 0:
            return 100.0
        
        return (completed / total_finished) * 100.0

    def calculate_throughput(self) -> float:
        """Calculate workflow throughput (executions per hour)"""
        # Simple calculation based on completed executions in last hour
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_completions = [
            e for e in self.executions.values()
            if e.get("status") == "completed" and
            datetime.fromisoformat(e.get("completed_at", "1970-01-01T00:00:00")) >= one_hour_ago
        ]
        
        return len(recent_completions)

    def calculate_overall_optimization_score(self) -> float:
        """Calculate overall optimization score"""
        if not self.workflows:
            return 0.0
        
        total_score = sum(w.get("optimization_score", 0.0) for w in self.workflows.values())
        return total_score / len(self.workflows)

    def update_workflow_performance(self, workflow_id: str, execution: Dict[str, Any]):
        """Update workflow performance metrics"""
        workflow = self.workflows[workflow_id]
        
        # Update estimated duration based on actual performance
        if execution["status"] == "completed":
            started = datetime.fromisoformat(execution["started_at"])
            completed = datetime.fromisoformat(execution["completed_at"])
            actual_duration = (completed - started).total_seconds()
            
            # Weighted average with previous estimates
            current_estimate = workflow["estimated_duration"]
            workflow["estimated_duration"] = (current_estimate * 0.7) + (actual_duration * 0.3)

async def handle_client(websocket: WebSocketServerProtocol, path: str):
    """Handle WebSocket connections"""
    server = DeerFlowServer()
    logger.info(f"New DeerFlow client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            await server.handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"DeerFlow client disconnected: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Error with DeerFlow client {websocket.remote_address}: {e}")

async def main():
    """Start the DeerFlow Orchestrator MCP server"""
    server = await websockets.serve(handle_client, "localhost", 8014)
    logger.info("DeerFlow Orchestrator MCP Server started on ws://localhost:8014")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("DeerFlow server shutting down...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
