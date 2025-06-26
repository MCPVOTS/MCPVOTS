#!/usr/bin/env python3
"""
Autonomous AI Web Dashboard
Real-time monitoring and control interface for DeepSeek R1 & Gemini 2.5 coordination
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from autonomous_ai_coordinator import AutonomousAICoordinator, TaskType, Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Autonomous AI Dashboard", version="1.0.0")

# Global coordinator instance
coordinator: AutonomousAICoordinator = None
active_connections: List[WebSocket] = []

# Pydantic models for API
class TaskRequest(BaseModel):
    task_type: str
    description: str
    priority: int = 1
    input_data: Dict[str, Any] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the autonomous AI coordinator on startup"""
    global coordinator
    coordinator = AutonomousAICoordinator()
    logger.info("🚀 Autonomous AI Dashboard started")
    
    # Start coordinator in background
    asyncio.create_task(run_coordinator_with_updates())

async def run_coordinator_with_updates():
    """Run coordinator and broadcast updates"""
    global coordinator
    
    # Override the coordinator's task completion to broadcast updates
    original_execute_task = coordinator.execute_task
    
    async def execute_task_with_broadcast(task: Task):
        result = await original_execute_task(task)
        
        # Broadcast task update
        await manager.broadcast({
            "type": "task_update",
            "data": {
                "task_id": task.id,
                "status": task.status,
                "type": task.type.value,
                "description": task.description,
                "result": task.result,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        })
        
        return result
    
    coordinator.execute_task = execute_task_with_broadcast
    
    # Start the autonomous loop
    await coordinator.autonomous_loop()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard HTML"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous AI Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }

        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header h1 {
            color: white;
            font-size: 2rem;
            font-weight: 300;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .card h2 {
            color: #4a5568;
            margin-bottom: 1rem;
            font-size: 1.5rem;
            font-weight: 600;
        }

        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .status-item {
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .status-item.available {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }

        .status-item.unavailable {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #4a5568;
        }

        .form-group select,
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-group select:focus,
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .task-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .task-item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            transition: all 0.3s;
        }

        .task-item.executing {
            border-color: #fbbf24;
            background: #fffbeb;
        }

        .task-item.completed {
            border-color: #10b981;
            background: #ecfdf5;
        }

        .task-item.failed {
            border-color: #ef4444;
            background: #fef2f2;
        }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .task-status {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-pending { background: #fbbf24; color: white; }
        .status-executing { background: #3b82f6; color: white; }
        .status-completed { background: #10b981; color: white; }
        .status-failed { background: #ef4444; color: white; }

        .log-container {
            grid-column: span 2;
            max-height: 300px;
            overflow-y: auto;
            background: #1a202c;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }

        .log-entry {
            margin-bottom: 0.5rem;
            padding: 0.25rem;
            border-left: 3px solid #4a5568;
            padding-left: 0.75rem;
        }

        .log-info { border-color: #3b82f6; }
        .log-success { border-color: #10b981; }
        .log-error { border-color: #ef4444; }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .metric {
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
        }

        .metric-label {
            font-size: 0.875rem;
            opacity: 0.9;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .log-container {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Autonomous AI Dashboard - DeepSeek R1 & Gemini 2.5</h1>
    </div>

    <div class="container">
        <!-- System Status -->
        <div class="card">
            <h2>🔧 System Status</h2>
            <div class="status-grid">
                <div class="status-item" id="deepseek-status">
                    <h3>DeepSeek R1</h3>
                    <p id="deepseek-text">Checking...</p>
                </div>
                <div class="status-item" id="gemini-status">
                    <h3>Gemini 2.5</h3>
                    <p id="gemini-text">Checking...</p>
                </div>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="queue-count">0</div>
                    <div class="metric-label">Queue</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="completed-count">0</div>
                    <div class="metric-label">Completed</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="running-status">No</div>
                    <div class="metric-label">Running</div>
                </div>
            </div>
        </div>

        <!-- Task Management -->
        <div class="card">
            <h2>📝 Add New Task</h2>
            <form id="task-form">
                <div class="form-group">
                    <label for="task-type">Task Type:</label>
                    <select id="task-type" required>
                        <option value="reasoning">Reasoning</option>
                        <option value="analysis">Analysis</option>
                        <option value="code_generation">Code Generation</option>
                        <option value="problem_solving">Problem Solving</option>
                        <option value="research">Research</option>
                        <option value="planning">Planning</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="task-description">Description:</label>
                    <textarea id="task-description" rows="3" placeholder="Describe the task..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="task-priority">Priority (1-5):</label>
                    <input type="number" id="task-priority" min="1" max="5" value="1" required>
                </div>
                
                <button type="submit" class="btn">Add Task</button>
            </form>
        </div>

        <!-- Active Tasks -->
        <div class="card">
            <h2>⚡ Active Tasks</h2>
            <div class="task-list" id="task-list">
                <p style="text-align: center; color: #666;">No tasks in queue</p>
            </div>
        </div>

        <!-- Completed Tasks -->
        <div class="card">
            <h2>✅ Recent Completed Tasks</h2>
            <div class="task-list" id="completed-tasks">
                <p style="text-align: center; color: #666;">No completed tasks</p>
            </div>
        </div>

        <!-- Real-time Logs -->
        <div class="card log-container">
            <h2 style="color: #e2e8f0; margin-bottom: 1rem;">📋 Real-time Logs</h2>
            <div id="log-container">
                <div class="log-entry log-info">Dashboard initialized. Connecting to autonomous AI coordinator...</div>
            </div>
        </div>
    </div>

    <script>
        class AutonomousDashboard {
            constructor() {
                this.ws = null;
                this.activeTasks = new Map();
                this.completedTasks = [];
                this.init();
            }

            init() {
                this.connectWebSocket();
                this.setupEventListeners();
                this.fetchStatus();
            }

            connectWebSocket() {
                const wsUrl = `ws://${window.location.host}/ws`;
                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    this.addLog('WebSocket connected', 'success');
                };

                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                };

                this.ws.onclose = () => {
                    this.addLog('WebSocket disconnected. Reconnecting...', 'error');
                    setTimeout(() => this.connectWebSocket(), 3000);
                };

                this.ws.onerror = (error) => {
                    this.addLog(`WebSocket error: ${error}`, 'error');
                };
            }

            handleWebSocketMessage(message) {
                switch (message.type) {
                    case 'status_update':
                        this.updateStatus(message.data);
                        break;
                    case 'task_update':
                        this.updateTask(message.data);
                        break;
                    case 'log':
                        this.addLog(message.data.message, message.data.level);
                        break;
                }
            }

            setupEventListeners() {
                document.getElementById('task-form').addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.submitTask();
                });
            }

            async fetchStatus() {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    this.updateStatus(status);
                } catch (error) {
                    this.addLog(`Failed to fetch status: ${error}`, 'error');
                }
            }

            updateStatus(status) {
                // Update model status
                const deepseekEl = document.getElementById('deepseek-status');
                const geminiEl = document.getElementById('gemini-status');
                
                if (status.models_available.deepseek_r1) {
                    deepseekEl.className = 'status-item available';
                    document.getElementById('deepseek-text').textContent = 'Available';
                } else {
                    deepseekEl.className = 'status-item unavailable';
                    document.getElementById('deepseek-text').textContent = 'Unavailable';
                }

                if (status.models_available.gemini_2_5) {
                    geminiEl.className = 'status-item available';
                    document.getElementById('gemini-text').textContent = 'Available';
                } else {
                    geminiEl.className = 'status-item unavailable';
                    document.getElementById('gemini-text').textContent = 'Unavailable';
                }

                // Update metrics
                document.getElementById('queue-count').textContent = status.queue_length;
                document.getElementById('completed-count').textContent = status.completed_tasks;
                document.getElementById('running-status').textContent = status.running ? 'Yes' : 'No';
            }

            async submitTask() {
                const taskType = document.getElementById('task-type').value;
                const description = document.getElementById('task-description').value;
                const priority = parseInt(document.getElementById('task-priority').value);

                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            task_type: taskType,
                            description: description,
                            priority: priority
                        })
                    });

                    const result = await response.json();
                    
                    if (response.ok) {
                        this.addLog(`Task added: ${result.task_id}`, 'success');
                        document.getElementById('task-form').reset();
                        document.getElementById('task-priority').value = 1;
                    } else {
                        this.addLog(`Failed to add task: ${result.message}`, 'error');
                    }
                } catch (error) {
                    this.addLog(`Error adding task: ${error}`, 'error');
                }
            }

            updateTask(taskData) {
                if (taskData.status === 'completed' || taskData.status === 'failed') {
                    this.activeTasks.delete(taskData.task_id);
                    this.completedTasks.unshift(taskData);
                    this.updateCompletedTasksList();
                } else {
                    this.activeTasks.set(taskData.task_id, taskData);
                }
                this.updateActiveTasksList();
                
                this.addLog(`Task ${taskData.task_id}: ${taskData.status}`, 
                    taskData.status === 'completed' ? 'success' : 
                    taskData.status === 'failed' ? 'error' : 'info');
            }

            updateActiveTasksList() {
                const container = document.getElementById('task-list');
                if (this.activeTasks.size === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">No tasks in queue</p>';
                    return;
                }

                container.innerHTML = Array.from(this.activeTasks.values())
                    .map(task => this.createTaskElement(task))
                    .join('');
            }

            updateCompletedTasksList() {
                const container = document.getElementById('completed-tasks');
                if (this.completedTasks.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">No completed tasks</p>';
                    return;
                }

                container.innerHTML = this.completedTasks
                    .slice(0, 10) // Show only last 10
                    .map(task => this.createTaskElement(task))
                    .join('');
            }

            createTaskElement(task) {
                return `
                    <div class="task-item ${task.status}">
                        <div class="task-header">
                            <strong>${task.task_id}</strong>
                            <span class="task-status status-${task.status}">${task.status}</span>
                        </div>
                        <div><strong>Type:</strong> ${task.type}</div>
                        <div><strong>Description:</strong> ${task.description}</div>
                        ${task.completed_at ? `<div><strong>Completed:</strong> ${new Date(task.completed_at).toLocaleString()}</div>` : ''}
                    </div>
                `;
            }

            addLog(message, level = 'info') {
                const container = document.getElementById('log-container');
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${level}`;
                logEntry.textContent = `[${timestamp}] ${message}`;
                
                container.appendChild(logEntry);
                container.scrollTop = container.scrollHeight;

                // Keep only last 100 log entries
                while (container.children.length > 100) {
                    container.removeChild(container.firstChild);
                }
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new AutonomousDashboard();
        });
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic status updates
            if coordinator:
                status = coordinator.get_status()
                await websocket.send_text(json.dumps({
                    "type": "status_update",
                    "data": status
                }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Get current system status"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    return coordinator.get_status()

@app.post("/api/tasks", response_model=TaskResponse)
async def add_task(task_request: TaskRequest):
    """Add a new task to the queue"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    try:
        task_type = TaskType(task_request.task_type)
        task_id = coordinator.add_task(
            task_type=task_type,
            description=task_request.description,
            input_data=task_request.input_data,
            priority=task_request.priority
        )
        
        # Broadcast task addition
        await manager.broadcast({
            "type": "log",
            "data": {
                "message": f"New task added: {task_id}",
                "level": "info"
            }
        })
        
        return TaskResponse(
            task_id=task_id,
            status="added",
            message="Task successfully added to queue"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid task type: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add task: {e}")

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks (queue + completed)"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    return {
        "queue": [
            {
                "id": task.id,
                "type": task.type.value,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "created_at": task.created_at.isoformat()
            }
            for task in coordinator.tasks_queue
        ],
        "completed": [
            {
                "id": task.id,
                "type": task.type.value,
                "description": task.description,
                "status": task.status,
                "result": task.result,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in coordinator.completed_tasks[-20:]  # Last 20 completed tasks
        ]
    }

@app.post("/api/coordinator/start")
async def start_coordinator():
    """Start the autonomous coordinator"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    if coordinator.running:
        return {"message": "Coordinator is already running"}
    
    # Start coordinator in background
    asyncio.create_task(run_coordinator_with_updates())
    
    await manager.broadcast({
        "type": "log",
        "data": {
            "message": "Autonomous coordinator started",
            "level": "success"
        }
    })
    
    return {"message": "Coordinator started successfully"}

@app.post("/api/coordinator/stop")
async def stop_coordinator():
    """Stop the autonomous coordinator"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    coordinator.stop()
    
    await manager.broadcast({
        "type": "log",
        "data": {
            "message": "Autonomous coordinator stopped",
            "level": "info"
        }
    })
    
    return {"message": "Coordinator stopped successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "autonomous_ai_web_dashboard:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
