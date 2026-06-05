import os
import json
import aiohttp
import logging
from typing import Dict, Any, Optional
from .base_provider import BaseProvider

logger = logging.getLogger("mintuu.llm.ollama")

class OllamaProvider(BaseProvider):
    name = "ollama"
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.fallback_model = "mistral:latest" # Example fallback
        self._health_checked = False
        
    async def _check_health(self, session: aiohttp.ClientSession) -> bool:
        """Check if Ollama is running and the model is available."""
        if self._health_checked:
            return True
            
        try:
            # Check basic health
            async with session.get(f"{self.base_url}/api/tags") as resp:
                if resp.status != 200:
                    logger.error("Ollama health check failed.")
                    return False
                data = await resp.json()
                
            models = [m["name"] for m in data.get("models", [])]
            
            # Check if default model is available
            if self.default_model not in models:
                logger.warning(f"Ollama model '{self.default_model}' not found. Checking fallback...")
                if self.fallback_model in models:
                    logger.info(f"Using fallback model '{self.fallback_model}'.")
                    self.default_model = self.fallback_model
                else:
                    logger.warning(f"Neither '{self.default_model}' nor '{self.fallback_model}' found. Attempting to pull '{self.default_model}'...")
                    # We could try pulling it, but it takes time. Let's just use whatever is available if possible.
                    if models:
                        self.default_model = models[0]
                        logger.info(f"Using available model '{self.default_model}'.")
                    else:
                        logger.error("No models available in Ollama.")
                        return False
            
            self._health_checked = True
            return True
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return False
        
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, json_mode: bool = False, model_preference: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Determine exact model to use based on preference mapping
        target_model = self.default_model
        if model_preference == "llama3.1":
            target_model = "llama3:latest" # Use cached llama3 to save 10+ minutes of download time
        elif model_preference == "mistral":
            target_model = "mistral:latest"
            
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if json_mode:
            payload["format"] = "json"
            
        try:
            async with aiohttp.ClientSession() as session:
                # Run health check first
                if not await self._check_health(session):
                    raise Exception("Ollama health check failed or no models available.")
                    
                async with session.post(url, json=payload) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    
                    return {
                        "content": data.get("message", {}).get("content", ""),
                        "model": data.get("model", self.default_model),
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0)
                    }
        except Exception as e:
            logger.error(f"Ollama API Error: {e}")
            raise
