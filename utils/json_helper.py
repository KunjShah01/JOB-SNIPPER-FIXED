"""
JSON Helper Utility
Handles mixed data types (dict, str, JSON) safely
"""

import json
import logging

logger = logging.getLogger(__name__)

def safe_json_loads(data, default=None):
    """
    Safely parse JSON data that might be a string, dict, or other type
    
    Args:
        data: Input data (could be str, dict, list, etc.)
        default: Default value to return if parsing fails
    
    Returns:
        Parsed data or default value
    """
    if default is None:
        default = {}
    
    try:
        # If it's already a dict or list, return as-is
        if isinstance(data, (dict, list)):
            return data
        
        # If it's a string, try to parse as JSON
        if isinstance(data, str):
            # Check if it's empty or whitespace
            if not data.strip():
                return default
            
            # Try to parse as JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # If JSON parsing fails, return the string wrapped in a dict
                logger.warning(f"Failed to parse JSON, returning string as-is: {data[:100]}...")
                return {"raw_response": data}
        
        # For other types, try to convert to dict
        if hasattr(data, '__dict__'):
            return data.__dict__
        
        # Last resort: return as-is wrapped in a dict
        return {"data": data}
        
    except Exception as e:
        logger.error(f"Error in safe_json_loads: {e}")
        return default

def safe_json_dumps(data, default=None):
    """
    Safely convert data to JSON string
    
    Args:
        data: Input data to convert
        default: Default value if conversion fails
    
    Returns:
        JSON string or default value
    """
    if default is None:
        default = "{}"
    
    try:
        # If it's already a string, check if it's valid JSON
        if isinstance(data, str):
            try:
                # Try to parse and re-dump to ensure valid JSON
                parsed = json.loads(data)
                return json.dumps(parsed)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in quotes
                return json.dumps(data)
        
        # For other types, convert to JSON
        return json.dumps(data, default=str)
        
    except Exception as e:
        logger.error(f"Error in safe_json_dumps: {e}")
        return default

def extract_data_safely(response, key, default=None):
    """
    Safely extract data from agent response
    
    Args:
        response: Agent response (could be dict, JSON string, etc.)
        key: Key to extract
        default: Default value if key not found
    
    Returns:
        Extracted value or default
    """
    if default is None:
        default = {}
    
    try:
        # Parse the response safely
        data = safe_json_loads(response, {})
        
        # Extract the key
        if isinstance(data, dict):
            return data.get(key, default)
        
        # If data is not a dict, return default
        return default
        
    except Exception as e:
        logger.error(f"Error extracting key '{key}': {e}")
        return default

def normalize_agent_response(response):
    """
    Normalize agent response to a consistent format
    
    Args:
        response: Raw agent response
    
    Returns:
        Normalized dict with standard keys
    """
    try:
        data = safe_json_loads(response, {})
        
        # Ensure we have a dict
        if not isinstance(data, dict):
            data = {"raw_response": data}
        
        # Add standard keys if missing
        normalized = {
            "success": True,
            "data": data,
            "overall_score": data.get("overall_score", 0),
            "parsed_data": data.get("parsed_data", {}),
            "recommendations": data.get("recommendations", []),
            "error": None
        }
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing response: {e}")
        return {
            "success": False,
            "data": {},
            "overall_score": 0,
            "parsed_data": {},
            "recommendations": [],
            "error": str(e)
        }