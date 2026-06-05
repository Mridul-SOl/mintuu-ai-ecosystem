import os
import json
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from .base_provider import BaseProvider

logger = logging.getLogger("mintuu.llm.openai")

class OpenAIProvider(BaseProvider):
    name = "openai"
    
    def __init__(self):
        # We'll instantiate the client dynamically to allow env vars to load
        self.client = None
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
    def _get_client(self):
        if not self.client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found. OpenAI provider will fail if invoked.")
            self.client = AsyncOpenAI(api_key=api_key)
        return self.client
        
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      json_mode: bool = False,
                      model_preference: Optional[str] = None) -> Dict[str, Any]:
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        try:
            response = await client.chat.completions.create(**kwargs)
            message = response.choices[0].message.content
            usage = response.usage
            
            return {
                "content": message,
                "model": response.model,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0
            }
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            raise
