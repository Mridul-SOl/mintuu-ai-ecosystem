import logging
import os
from typing import Dict, Optional
from .providers.base_provider import BaseProvider
from .providers.openai_provider import OpenAIProvider
from .providers.ollama_provider import OllamaProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.groq_provider import GroqProvider

logger = logging.getLogger("mintuu.llm.router")

class ProviderRouter:
    """Routes requests to the appropriate LLM provider.
    
    Auto-selection logic for deployment:
    - If GROQ_API_KEY is set → use Groq (free cloud, ideal for Render deployment)
    - If OPENAI_API_KEY is set → use OpenAI
    - Otherwise → use Ollama (local development)
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {
            "openai": OpenAIProvider(),
            "ollama": OllamaProvider(),
            "anthropic": AnthropicProvider(),
            "groq": GroqProvider(),
        }
        self.default_provider = self._detect_default_provider()
        logger.info(f"LLM Provider auto-selected: {self.default_provider}")
        
    def _detect_default_provider(self) -> str:
        """Auto-detect the best available provider based on environment."""
        explicit = os.getenv("DEFAULT_LLM_PROVIDER")
        if explicit and explicit in self.providers:
            return explicit
        
        # Auto-select: Groq (free cloud) > OpenAI (paid cloud) > Ollama (local)
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        return "ollama"
        
    def get_provider(self, preference: Optional[str] = None) -> BaseProvider:
        """Get requested provider, fallback to default."""
        if preference and preference in self.providers:
            return self.providers[preference]
        
        if self.default_provider in self.providers:
            return self.providers[self.default_provider]
            
        # Absolute fallback
        return list(self.providers.values())[0]
