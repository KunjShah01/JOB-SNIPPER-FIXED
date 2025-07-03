"""
Message Protocol for Agent Communication
Handles message passing between agents
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AgentMessage:
    """Message class for agent communication"""
    
    def __init__(self, sender: str, receiver: str, data: Any, message_type: str = "data", metadata: Optional[Dict] = None):
        """
        Initialize agent message
        
        Args:
            sender: Name of sending agent
            receiver: Name of receiving agent
            data: Message data
            message_type: Type of message
            metadata: Additional metadata
        """
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.message_id = f"{sender}_{receiver}_{int(datetime.now().timestamp())}"
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        try:
            message_dict = {
                "message_id": self.message_id,
                "sender": self.sender,
                "receiver": self.receiver,
                "data": self.data,
                "message_type": self.message_type,
                "metadata": self.metadata,
                "timestamp": self.timestamp
            }
            return json.dumps(message_dict)
        except Exception as e:
            logger.error(f"Error converting message to JSON: {e}")
            return json.dumps({
                "error": str(e),
                "sender": self.sender,
                "receiver": self.receiver,
                "timestamp": self.timestamp
            })
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "data": self.data,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create message from JSON string"""
        try:
            if isinstance(json_str, dict):
                data = json_str
            else:
                data = json.loads(json_str)
            
            message = cls(
                sender=data.get("sender", "unknown"),
                receiver=data.get("receiver", "unknown"),
                data=data.get("data", {}),
                message_type=data.get("message_type", "data"),
                metadata=data.get("metadata", {})
            )
            
            # Restore timestamp and ID if available
            if "timestamp" in data:
                message.timestamp = data["timestamp"]
            if "message_id" in data:
                message.message_id = data["message_id"]
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating message from JSON: {e}")
            # Return error message
            return cls(
                sender="system",
                receiver="error_handler",
                data={"error": str(e), "original_data": json_str},
                message_type="error"
            )
    
    @classmethod
    def from_dict(cls, data_dict: Dict) -> 'AgentMessage':
        """Create message from dictionary"""
        try:
            message = cls(
                sender=data_dict.get("sender", "unknown"),
                receiver=data_dict.get("receiver", "unknown"),
                data=data_dict.get("data", {}),
                message_type=data_dict.get("message_type", "data"),
                metadata=data_dict.get("metadata", {})
            )
            
            # Restore timestamp and ID if available
            if "timestamp" in data_dict:
                message.timestamp = data_dict["timestamp"]
            if "message_id" in data_dict:
                message.message_id = data_dict["message_id"]
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating message from dict: {e}")
            return cls(
                sender="system",
                receiver="error_handler",
                data={"error": str(e), "original_data": data_dict},
                message_type="error"
            )
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to message"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None):
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def is_error(self) -> bool:
        """Check if message is an error message"""
        return self.message_type == "error"
    
    def __str__(self) -> str:
        """String representation of message"""
        return f"AgentMessage({self.sender} -> {self.receiver}: {self.message_type})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"AgentMessage(id={self.message_id}, {self.sender} -> {self.receiver}, type={self.message_type}, timestamp={self.timestamp})"

class MessageBus:
    """Message bus for handling agent communication"""
    
    def __init__(self):
        self.messages = []
        self.subscribers = {}
        self.logger = logging.getLogger("MessageBus")
    
    def send_message(self, message: AgentMessage) -> bool:
        """Send message through the bus"""
        try:
            self.messages.append(message)
            self.logger.debug(f"Message sent: {message}")
            
            # Notify subscribers
            if message.receiver in self.subscribers:
                for callback in self.subscribers[message.receiver]:
                    try:
                        callback(message)
                    except Exception as e:
                        self.logger.error(f"Error in subscriber callback: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def subscribe(self, agent_name: str, callback):
        """Subscribe agent to receive messages"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
        self.logger.debug(f"Agent {agent_name} subscribed to message bus")
    
    def get_messages_for(self, agent_name: str) -> list:
        """Get all messages for specific agent"""
        return [msg for msg in self.messages if msg.receiver == agent_name]
    
    def get_conversation(self, agent1: str, agent2: str) -> list:
        """Get conversation between two agents"""
        return [
            msg for msg in self.messages 
            if (msg.sender == agent1 and msg.receiver == agent2) or 
               (msg.sender == agent2 and msg.receiver == agent1)
        ]
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()
        self.logger.debug("Message bus cleared")

# Global message bus instance
message_bus = MessageBus()