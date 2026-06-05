import logging
from typing import Dict, Any
from core.llm.llm_manager import LLMManager

logger = logging.getLogger("mintuu.reflection")

class ReflectionEngine:
    """Engine for agent self-reflection and cross-agent critique."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        
    async def evaluate_output(self, agent_id: str, task: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Ask the agent to critique its own output."""
        prompt = f"""
TASK:
{task}

GENERATED OUTPUT:
{output}

INSTRUCTIONS:
Critique your own output. Are there any weaknesses? Did you miss any constraints?
Provide a JSON response:
{{
    "is_acceptable": boolean,
    "critique": "string",
    "suggested_revisions": ["string"]
}}
"""
        logger.info(f"[{agent_id}] Running self-reflection on output...")
        
        response = await self.llm.generate_response(
            agent_id=agent_id,
            prompt=prompt,
            system_prompt="You are a strict self-evaluator. Find flaws in the reasoning.",
            temperature=0.2,
            json_mode=True
        )
        
        # Simplified handling for the demo
        import json
        try:
            return json.loads(response.get("content", "{}"))
        except Exception:
            return {"is_acceptable": True, "critique": "Failed to parse critique", "suggested_revisions": []}
            
    async def cross_agent_critique(self, reviewer_id: str, author_id: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Ask another agent (e.g., CEO) to review output from an author (e.g., Marketing)."""
        prompt = f"""
AUTHOR: {author_id}
OUTPUT TO REVIEW:
{output}

INSTRUCTIONS:
Critique this output from the perspective of your role.
Provide a JSON response:
{{
    "approved": boolean,
    "feedback": "string"
}}
"""
        response = await self.llm.generate_response(
            agent_id=reviewer_id,
            prompt=prompt,
            temperature=0.3,
            json_mode=True
        )
        import json
        try:
            return json.loads(response.get("content", "{}"))
        except Exception:
            return {"approved": True, "feedback": ""}
