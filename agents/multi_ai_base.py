"""
Multi AI Base Agent
Supports multiple AI providers with fallback handling
"""

from agents.agent_base import Agent
import time
import logging
from typing import Callable, List, Optional, Dict, Any
import asyncio
from threading import Lock

# Import configuration with error handling
try:
    from utils.config import GEMINI_API_KEY, MISTRAL_API_KEY, GEMINI_AVAILABLE, MISTRAL_AVAILABLE
except ImportError:
    GEMINI_API_KEY = None
    MISTRAL_API_KEY = None
    GEMINI_AVAILABLE = False
    MISTRAL_AVAILABLE = False
    logging.warning("Configuration not available, using fallback mode")

import importlib.util

# Import AI libraries based on availability
if importlib.util.find_spec("google.generativeai") is not None and GEMINI_AVAILABLE:
    try:
        import google.generativeai as genai
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        GENAI_AVAILABLE = True
    except Exception as e:
        GENAI_AVAILABLE = False
        logging.warning(f"Gemini AI not available: {e}")
else:
    GENAI_AVAILABLE = False

# Mistral import with error handling
if importlib.util.find_spec("mistralai") is not None and MISTRAL_AVAILABLE:
    try:
        from mistralai.client import MistralClient
        if MISTRAL_API_KEY:
            mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
        MISTRAL_CLIENT_AVAILABLE = True
    except Exception as e:
        MISTRAL_CLIENT_AVAILABLE = False
        logging.warning(f"Mistral AI not available: {e}")
else:
    MISTRAL_CLIENT_AVAILABLE = False

class MultiAIAgent(Agent):
    """Base class for agents that support multiple AI providers simultaneously, with advanced features"""

    def __init__(
        self,
        name,
        use_gemini=True,
        use_mistral=True,
        return_mode="aggregate",
        verbose=False,
        fallback_to_fallback=True,
        prompt_template: Optional[str] = None,
        provider_priority: Optional[List[str]] = None,
        max_retries: int = 1,
        postprocess_hook: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        cache_enabled: bool = False,
        provider_settings: Optional[Dict[str, dict]] = None,
        rate_limit_per_minute: int = 0,
        user_context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize MultiAI Agent with comprehensive configuration
        
        Args:
            name: Agent name
            use_gemini: Whether to use Gemini AI
            use_mistral: Whether to use Mistral AI
            return_mode: How to return results ('aggregate', 'compare', 'dict')
            verbose: Enable verbose logging
            fallback_to_fallback: Use fallback when all providers fail
            prompt_template: Template for prompts
            provider_priority: Order of provider usage
            max_retries: Number of retries per provider
            postprocess_hook: Function to postprocess responses
            cache_enabled: Enable response caching
            provider_settings: Provider-specific settings
            rate_limit_per_minute: Rate limiting
            user_context: User context for personalization
        """
        super().__init__(name)
        
        self.use_gemini = use_gemini and GENAI_AVAILABLE
        self.use_mistral = use_mistral and MISTRAL_CLIENT_AVAILABLE
        self.return_mode = return_mode
        self.verbose = verbose
        self.fallback_to_fallback = fallback_to_fallback
        self.prompt_template = prompt_template
        self.provider_priority = provider_priority or ["gemini", "mistral"]
        self.max_retries = max_retries
        self.postprocess_hook = postprocess_hook
        self.cache_enabled = cache_enabled
        self.provider_settings = provider_settings or {}
        self.rate_limit_per_minute = rate_limit_per_minute
        self.user_context = user_context or {}
        
        # Internal state
        self.cache = {} if cache_enabled else None
        self.rate_limit_lock = Lock()
        self.last_request_times = []
        
        # Setup AI clients
        self.setup_ai_clients()
        
        if self.verbose:
            self.logger.info(f"MultiAI Agent '{name}' initialized")
            self.logger.info(f"Gemini available: {self.use_gemini}")
            self.logger.info(f"Mistral available: {self.use_mistral}")

    def setup_ai_clients(self):
        """Setup AI clients with error handling"""
        self.gemini_model = None
        self.mistral_client = None
        
        # Setup Gemini
        if self.use_gemini:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                if self.verbose:
                    self.logger.info("Gemini client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.use_gemini = False
        
        # Setup Mistral
        if self.use_mistral:
            try:
                self.mistral_client = mistral_client
                if self.verbose:
                    self.logger.info("Mistral client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Mistral: {e}")
                self.use_mistral = False

    def run(self, input_data):
        """
        Main method to run the multi-AI agent
        
        Args:
            input_data: Input data for processing
        
        Returns:
            Processed result based on return_mode
        """
        try:
            parsed_input = self.parse_input(input_data)
            
            # Check cache if enabled
            if self.cache_enabled:
                cache_key = str(hash(str(parsed_input)))
                if cache_key in self.cache:
                    if self.verbose:
                        self.logger.info("Returning cached result")
                    return self.cache[cache_key]
            
            # Rate limiting
            if self.rate_limit_per_minute > 0:
                self._enforce_rate_limit()
            
            # Get responses from available providers
            responses = self._get_provider_responses(parsed_input)
            
            # Process responses based on return mode
            result = self._process_responses(responses, parsed_input)
            
            # Apply postprocessing hook if provided
            if self.postprocess_hook:
                result = self.postprocess_hook(result)
            
            # Cache result if enabled
            if self.cache_enabled and cache_key:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in MultiAI agent run: {e}")
            return self._get_fallback_response(input_data, str(e))

    def _get_provider_responses(self, parsed_input):
        """Get responses from available AI providers"""
        responses = {}
        
        for provider in self.provider_priority:
            if provider == "gemini" and self.use_gemini:
                responses["gemini"] = self._call_gemini(parsed_input)
            elif provider == "mistral" and self.use_mistral:
                responses["mistral"] = self._call_mistral(parsed_input)
        
        return responses

    def _call_gemini(self, parsed_input):
        """Call Gemini AI with error handling"""
        try:
            if not self.gemini_model:
                raise Exception("Gemini model not available")
            
            prompt = self._format_prompt(parsed_input, "gemini")
            
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.gemini_model.generate_content(prompt)
                    
                    if response and response.text:
                        return {
                            "success": True,
                            "response": response.text,
                            "provider": "gemini",
                            "attempt": attempt + 1
                        }
                    else:
                        raise Exception("Empty response from Gemini")
                        
                except Exception as e:
                    if attempt < self.max_retries:
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            self.logger.error(f"Gemini call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "gemini"
            }

    def _call_mistral(self, parsed_input):
        """Call Mistral AI with error handling"""
        try:
            if not self.mistral_client:
                raise Exception("Mistral client not available")
            
            prompt = self._format_prompt(parsed_input, "mistral")
            
            for attempt in range(self.max_retries + 1):
                try:
                    from mistralai.models.chat_completion import ChatMessage
                    
                    messages = [ChatMessage(role="user", content=prompt)]
                    response = self.mistral_client.chat(
                        model="mistral-tiny",
                        messages=messages
                    )
                    
                    if response and response.choices:
                        return {
                            "success": True,
                            "response": response.choices[0].message.content,
                            "provider": "mistral",
                            "attempt": attempt + 1
                        }
                    else:
                        raise Exception("Empty response from Mistral")
                        
                except Exception as e:
                    if attempt < self.max_retries:
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            self.logger.error(f"Mistral call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "mistral"
            }

    def _format_prompt(self, parsed_input, provider):
        """Format prompt for specific provider"""
        if self.prompt_template:
            return self.prompt_template.format(
                input=parsed_input,
                provider=provider,
                context=self.user_context
            )
        else:
            return str(parsed_input)

    def _process_responses(self, responses, parsed_input):
        """Process responses based on return mode"""
        if not responses:
            return self._get_fallback_response(parsed_input, "No providers available")
        
        successful_responses = {k: v for k, v in responses.items() if v.get("success")}
        
        if not successful_responses and self.fallback_to_fallback:
            return self._get_fallback_response(parsed_input, "All providers failed")
        
        if self.return_mode == "aggregate":
            return self._aggregate_responses(successful_responses)
        elif self.return_mode == "compare":
            return self._compare_responses(successful_responses)
        else:  # dict mode
            return successful_responses

    def _aggregate_responses(self, responses):
        """Aggregate multiple responses into a single result"""
        if not responses:
            return self._get_fallback_response({}, "No successful responses")
        
        # Use the first successful response as base
        primary_response = list(responses.values())[0]
        
        return {
            "success": True,
            "response": primary_response.get("response", ""),
            "providers_used": list(responses.keys()),
            "primary_provider": primary_response.get("provider"),
            "aggregated": True
        }

    def _compare_responses(self, responses):
        """Compare responses from different providers"""
        return {
            "success": True,
            "responses": responses,
            "comparison_mode": True,
            "providers_count": len(responses)
        }

    def _get_fallback_response(self, input_data, error_msg):
        """Generate fallback response when AI providers fail"""
        return {
            "success": False,
            "fallback": True,
            "error": error_msg,
            "message": f"AI providers not available for {self.name}",
            "input_received": bool(input_data),
            "recommendations": [
                "Check API keys configuration",
                "Verify internet connection",
                "Install required AI libraries"
            ]
        }

    def _enforce_rate_limit(self):
        """Enforce rate limiting"""
        with self.rate_limit_lock:
            current_time = time.time()
            
            # Remove old timestamps
            self.last_request_times = [
                t for t in self.last_request_times 
                if current_time - t < 60
            ]
            
            # Check if we're within rate limit
            if len(self.last_request_times) >= self.rate_limit_per_minute:
                sleep_time = 60 - (current_time - self.last_request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            self.last_request_times.append(current_time)