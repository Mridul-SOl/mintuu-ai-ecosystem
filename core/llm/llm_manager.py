import logging
from typing import Dict, Any, Optional, List
from .provider_router import ProviderRouter
from .token_tracker import TokenTracker

logger = logging.getLogger("mintuu.llm.manager")

class LLMManager:
    """Central manager for LLM interactions across multiple providers."""
    
    def __init__(self):
        self.router = ProviderRouter()
        self.token_tracker = TokenTracker()
        logger.info("LLM Manager initialized.")
        
    async def generate_response(self, 
                              agent_id: str, 
                              prompt: str, 
                              system_prompt: Optional[str] = None,
                              model_preference: Optional[str] = None,
                              temperature: float = 0.7,
                              json_mode: bool = False) -> Dict[str, Any]:
        """Generate response using the best available provider."""
        provider = self.router.get_provider(model_preference)
        
        logger.debug(f"[{agent_id}] Routing request to {provider.name}")
        
        try:
            response = await provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                json_mode=json_mode,
                model_preference=model_preference
            )
            
            # Track tokens
            self.token_tracker.record_usage(
                agent_id=agent_id,
                provider=provider.name,
                model=response.get("model", "unknown"),
                prompt_tokens=response.get("prompt_tokens", 0),
                completion_tokens=response.get("completion_tokens", 0)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"[{agent_id}] LLM generation failed with {provider.name}: {e}")
            # Fallback logic could go here
            raise
