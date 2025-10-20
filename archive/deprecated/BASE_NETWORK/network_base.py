"""
Base network implementation for the network system.
"""
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import uuid


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class MessageProtocol:
    """
    Base message protocol for network communication.
    """
    
    def __init__(self, version: str = "1.0"):
        self.version = version
    
    def encode(self, data: Any) -> str:
        """
        Encode data for transmission.
        
        Args:
            data: Data to encode
            
        Returns:
            JSON-encoded string
        """
        return json.dumps(data)
    
    def decode(self, data: str) -> Any:
        """
        Decode received data.
        
        Args:
            data: JSON-encoded string
            
        Returns:
            Decoded data
        """
        return json.loads(data)


class BaseConnection(ABC):
    """
    Abstract base class for network connections.
    """
    
    def __init__(self, connection_id: Optional[str] = None, protocol: Optional[MessageProtocol] = None):
        self.connection_id = connection_id or str(uuid.uuid4())
        self.protocol = protocol or MessageProtocol()
        self.status = ConnectionStatus.DISCONNECTED
        self.metadata = {}
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish a connection.
        
        Returns:
            True if connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """
        Disconnect the connection.
        """
        pass
    
    @abstractmethod
    async def send(self, data: Any) -> bool:
        """
        Send data through the connection.
        
        Args:
            data: Data to send
            
        Returns:
            True if send was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def receive(self) -> Optional[Any]:
        """
        Receive data from the connection.
        
        Returns:
            Received data or None if no data available
        """
        pass
    
    async def set_metadata(self, key: str, value: Any):
        """
        Set metadata for the connection.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value


class NetworkManager:
    """
    Manages network connections and protocols.
    """
    
    def __init__(self, protocol: Optional[MessageProtocol] = None):
        self.protocol = protocol or MessageProtocol()
        self.connections: Dict[str, BaseConnection] = {}
        self.message_handlers: List[Callable] = []
    
    async def register_connection(self, connection: BaseConnection) -> str:
        """
        Register a connection with the network manager.
        
        Args:
            connection: Connection to register
            
        Returns:
            Connection ID
        """
        self.connections[connection.connection_id] = connection
        return connection.connection_id
    
    async def get_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """
        Get a connection by ID.
        
        Args:
            connection_id: ID of the connection to retrieve
            
        Returns:
            Connection instance or None if not found
        """
        return self.connections.get(connection_id)
    
    async def remove_connection(self, connection_id: str):
        """
        Remove a connection from management.
        
        Args:
            connection_id: ID of the connection to remove
        """
        if connection_id in self.connections:
            conn = self.connections[connection_id]
            if conn.status == ConnectionStatus.CONNECTED:
                await conn.disconnect()
            del self.connections[connection_id]
    
    async def broadcast_message(self, message: Any, exclude_connection_ids: Optional[List[str]] = None):
        """
        Broadcast a message to all connected connections.
        
        Args:
            message: Message to broadcast
            exclude_connection_ids: List of connection IDs to exclude from broadcast
        """
        exclude_ids = exclude_connection_ids or []
        tasks = []
        
        for conn_id, connection in self.connections.items():
            if conn_id not in exclude_ids and connection.status == ConnectionStatus.CONNECTED:
                tasks.append(connection.send(message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def add_message_handler(self, handler: Callable[[Any, str], None]):
        """
        Add a message handler to process incoming messages.
        
        Args:
            handler: Function to handle messages with signature handler(message, connection_id)
        """
        self.message_handlers.append(handler)
    
    async def process_message(self, message: Any, connection_id: str):
        """
        Process an incoming message with registered handlers.
        
        Args:
            message: Message to process
            connection_id: ID of the connection that received the message
        """
        for handler in self.message_handlers:
            try:
                await handler(message, connection_id)
            except Exception as e:
                print(f"Error in message handler: {e}")