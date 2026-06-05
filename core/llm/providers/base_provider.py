from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    name: str = "base"
    
    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      json_mode: bool = False,
                      model_preference: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response.
        Must return a dict containing at least:
        - content (str)
        - model (str)
        - prompt_tokens (int)
        - completion_tokens (int)
        """
        pass
