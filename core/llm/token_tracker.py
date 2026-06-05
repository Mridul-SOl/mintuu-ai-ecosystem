import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger("mintuu.llm.tokens")

class TokenTracker:
    """Tracks token usage and estimates cost per agent and provider."""
    
    def __init__(self):
        self.usage: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls": 0
        })
        
    def record_usage(self, agent_id: str, provider: str, model: str, prompt_tokens: int, completion_tokens: int):
        key = f"{agent_id}:{provider}:{model}"
        self.usage[key]["prompt_tokens"] += prompt_tokens
        self.usage[key]["completion_tokens"] += completion_tokens
        self.usage[key]["total_tokens"] += (prompt_tokens + completion_tokens)
        self.usage[key]["calls"] += 1
        
        logger.debug(f"Token usage updated for {key}: {prompt_tokens} prompt, {completion_tokens} comp")
        
    def get_stats(self) -> Dict[str, Any]:
        return dict(self.usage)
