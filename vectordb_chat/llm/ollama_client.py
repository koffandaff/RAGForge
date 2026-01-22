"""
Ollama LLM client for local model inference
"""
import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "deepseek-coder:6.7b"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_url = f"{self.base_url}/api"
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                logger.info(f"Connected to Ollama. Using model: {self.model}")
                
                # Check if model exists
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                if self.model not in model_names:
                    logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
                    # Use first available model
                    if model_names:
                        self.model = model_names[0]
                        logger.info(f"Using model: {self.model}")
            else:
                logger.warning(f"Ollama connection failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Could not connect to Ollama: {e}")
            # Don't raise ConnectionError here to allow the app to start even if Ollama is down initially
            # raise ConnectionError(f"Ollama not running at {self.base_url}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                temperature: float = 0.7) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction (optional)
            temperature: Creativity control (0.0-1.0)
            
        Returns:
            Generated text
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=300  # Increased to 5 minutes to prevent local inference timeouts
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Ollama request failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def chat(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Chat with the LLM using the chat endpoint.
        
        Args:
            messages: List of message objects {"role": "user/assistant/system", "content": "..."}
            temperature: Creativity control
            
        Returns:
            Assistant response string
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Ollama chat failed: {str(e)}"
            logger.error(error_msg)
    def chat_stream(self, messages: List[Dict], temperature: float = 0.7):
        """
        Stream chat responses from the LLM.
        
        Args:
            messages: List of message objects
            temperature: Creativity control
            
        Yields:
            Tokens as they are generated
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=300,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk:
                            yield chunk['message'].get('content', '')
                        if chunk.get('done'):
                            break
            else:
                yield f"Error: Ollama API error {response.status_code}"
        except Exception as e:
            yield f"Error: {str(e)}"

    def chat_with_context(self, query: str, context: List[str], 
                         conversation_history: List[Dict] = None) -> str:
        """
        Generate response using RAG context and the chat endpoint.
        """
        context_str = "\n".join([f"- {c.strip()}" for c in context])
        
        system_msg = {
            "role": "system",
            "content": "You are a helpful assistant. Use the provided context to answer the user's question accurately. If the answer is not in the context, say you don't know."
        }
        
        user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
        
        messages = [system_msg]
        
        # Add history if available
        if conversation_history:
            messages.extend(conversation_history[-4:])
            
        # Add current query
        messages.append({"role": "user", "content": user_content})
        
        return self.chat(messages, temperature=0.1)
