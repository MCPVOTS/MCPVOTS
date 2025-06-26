#!/usr/bin/env python3
"""
Autonomous AI Web Dashboard
Real-time monitoring and control interface for the AI coordination system
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import asyncio
import time
from datetime import datetime
from autonomous_ai_coordinator import AutonomousAICoordinator, TaskType

app = Flask(__name__)
app.config['SECRET_KEY'] = 'autonomous_ai_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global coordinator instance
coordinator = None
coordinator_thread = None

class WebDashboard:
    """Web dashboard for monitoring autonomous AI operations"""
    
    def __init__(self):
        self.coordinator = AutonomousAICoordinator()
        self.running = False
    
    async def start_coordinator(self):
        """Start the autonomous coordinator"""
        self.running = True
        await self.coordinator.autonomous_loop()
    
    def run_coordinator_thread(self):
        """Run coordinator in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_coordinator())
    
    def start_autonomous_system(self):
        """Start the autonomous AI system"""
        if not self.running:
            self.coordinator_thread = threading.Thread(target=self.run_coordinator_thread)
            self.coordinator_thread.daemon = True
            self.coordinator_thread.start()
            return True
        return False
    
    def stop_autonomous_system(self):
        """Stop the autonomous AI system"""
        if self.running:
            self.coordinator.stop()
            self.running = False
            return True
        return False

# Global dashboard instance
dashboard = WebDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('autonomous_ai_dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    status = dashboard.coordinator.get_status()
    return jsonify(status)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks (pending and completed)"""
    pending_tasks = []
    for task in dashboard.coordinator.tasks_queue:
        pending_tasks.append({
            'id': task.id,
            'type': task.type.value,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'created_at': task.created_at.isoformat()
        })
    
    completed_tasks = []
    for task in dashboard.coordinator.completed_tasks[-10:]:  # Last 10 completed tasks
        completed_tasks.append({
            'id': task.id,
            'type': task.type.value,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'assigned_model': task.assigned_model.value if task.assigned_model else None,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
    
    return jsonify({
        'pending': pending_tasks,
        'completed': completed_tasks
    })

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    data = request.json
    
    try:
        task_type = TaskType(data['type'])
        description = data['description']
        priority = data.get('priority', 1)
        
        task_id = dashboard.coordinator.add_task(task_type, description, priority=priority)
        
        # Emit real-time update
        socketio.emit('task_added', {
            'task_id': task_id,
            'type': task_type.value,
            'description': description,
            'priority': priority
        })
        
        return jsonify({'success': True, 'task_id': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/task/<task_id>')
def get_task_result(task_id):
    """Get specific task result"""
    # Find task in completed tasks
    for task in dashboard.coordinator.completed_tasks:
        if task.id == task_id:
            return jsonify({
                'id': task.id,
                'type': task.type.value,
                'description': task.description,
                'status': task.status,
                'result': task.result,
                'assigned_model': task.assigned_model.value if task.assigned_model else None,
                'created_at': task.created_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            })
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/start', methods=['POST'])
def start_system():
    """Start the autonomous AI system"""
    success = dashboard.start_autonomous_system()
    
    if success:
        socketio.emit('system_status', {'running': True})
        return jsonify({'success': True, 'message': 'Autonomous AI system started'})
    else:
        return jsonify({'success': False, 'message': 'System already running'})

@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Stop the autonomous AI system"""
    success = dashboard.stop_autonomous_system()
    
    if success:
        socketio.emit('system_status', {'running': False})
        return jsonify({'success': True, 'message': 'Autonomous AI system stopped'})
    else:
        return jsonify({'success': False, 'message': 'System not running'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('system_status', {'running': dashboard.running})

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    status = dashboard.coordinator.get_status()
    emit('status_update', status)

# Background task to emit real-time updates
def background_thread():
    """Send periodic updates to connected clients"""
    while True:
        time.sleep(5)  # Update every 5 seconds
        if dashboard.coordinator:
            status = dashboard.coordinator.get_status()
            socketio.emit('status_update', status)

# Start background thread
thread = threading.Thread(target=background_thread)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    print("🚀 Starting Autonomous AI Web Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
