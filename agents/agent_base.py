"""
Base Agent Class
Provides common functionality for all agents
"""

import logging
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    def run(self, input_data):
        """
        Main method to be implemented by subclasses
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Processed result
        """
        raise NotImplementedError("Implement in subclass")
    
    def safe_run(self, input_data):
        """
        Safe wrapper for run method with error handling
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            dict: Result with success status and data/error
        """
        try:
            self.logger.info(f"Running {self.name} agent...")
            result = self.run(input_data)
            self.logger.info(f"{self.name} agent completed successfully")
            
            return {
                "success": True,
                "data": result,
                "error": None,
                "agent": self.name
            }
            
        except Exception as e:
            self.logger.error(f"Error in {self.name} agent: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "agent": self.name
            }
    
    def parse_input(self, input_data):
        """
        Parse input data safely
        
        Args:
            input_data: Raw input data
        
        Returns:
            Parsed data
        """
        try:
            if isinstance(input_data, str):
                try:
                    return json.loads(input_data)
                except json.JSONDecodeError:
                    return {"raw_input": input_data}
            elif isinstance(input_data, dict):
                return input_data
            else:
                return {"data": input_data}
        except Exception as e:
            self.logger.warning(f"Error parsing input: {e}")
            return {"raw_input": str(input_data)}
    
    def format_output(self, data):
        """
        Format output data consistently
        
        Args:
            data: Output data
        
        Returns:
            Formatted output
        """
        try:
            if isinstance(data, dict):
                return data
            elif isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return {"response": data}
            else:
                return {"result": data}
        except Exception as e:
            self.logger.warning(f"Error formatting output: {e}")
            return {"raw_output": str(data)}

class FallbackAgent(Agent):
    """Fallback agent for when specific agents are not available"""
    
    def __init__(self, agent_type="Generic"):
        super().__init__(f"Fallback{agent_type}")
        self.agent_type = agent_type
    
    def run(self, input_data):
        """
        Provide fallback response when real agent is not available
        
        Args:
            input_data: Input data
        
        Returns:
            Fallback response
        """
        self.logger.warning(f"Using fallback for {self.agent_type} agent")
        
        parsed_input = self.parse_input(input_data)
        
        return {
            "agent_type": self.agent_type,
            "status": "fallback_mode",
            "message": f"{self.agent_type} agent not available, using fallback",
            "input_received": bool(parsed_input),
            "recommendations": [
                f"Install required dependencies for {self.agent_type} agent",
                "Check configuration settings",
                "Verify API keys are properly set"
            ],
            "fallback_data": {
                "overall_score": 75,
                "parsed_data": parsed_input,
                "analysis_available": False
            }
        }