"""
Base agent implementation for the agentic system.
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: str = "BaseAgent", **kwargs):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.created_at = asyncio.get_event_loop().time()
        self.active = True
        self.metadata = kwargs
        self.skills = []
        self.memory = {}
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a given task.
        
        Args:
            task: Dictionary containing task information
            
        Returns:
            Dictionary containing task results
        """
        pass
    
    @abstractmethod
    async def process_input(self, input_data: Any) -> Any:
        """
        Process input data and return a response.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed response
        """
        pass
    
    async def add_skill(self, skill: Any):
        """
        Add a skill to the agent's skill set.
        
        Args:
            skill: A callable or skill object to add
        """
        self.skills.append(skill)
    
    async def store_memory(self, key: str, value: Any):
        """
        Store a value in the agent's memory.
        
        Args:
            key: Memory key
            value: Memory value
        """
        self.memory[key] = value
    
    async def retrieve_memory(self, key: str) -> Any:
        """
        Retrieve a value from the agent's memory.
        
        Args:
            key: Memory key
            
        Returns:
            Memory value or None if not found
        """
        return self.memory.get(key)
    
    async def deactivate(self):
        """
        Deactivate the agent.
        """
        self.active = False

class AgentManager:
    """
    Manages multiple agents, their lifecycle and coordination.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    async def register_agent(self, agent: BaseAgent) -> str:
        """
        Register an agent with the manager.
        
        Args:
            agent: Agent to register
            
        Returns:
            Agent ID
        """
        self.agents[agent.agent_id] = agent
        return agent.agent_id
    
    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    async def remove_agent(self, agent_id: str):
        """
        Remove an agent from management.
        
        Args:
            agent_id: ID of the agent to remove
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    async def execute_task_for_agents(self, task: Dict[str, Any], agent_ids: Optional[List[str]] = None):
        """
        Execute a task across multiple agents.
        
        Args:
            task: Task to execute
            agent_ids: List of agent IDs to execute task for. If None, all agents will execute the task.
        """
        target_agents = [self.agents[aid] for aid in agent_ids if aid in self.agents] if agent_ids else self.agents.values()
        
        results = []
        for agent in target_agents:
            if agent.active:
                result = await agent.execute_task(task)
                results.append(result)
        
        return results