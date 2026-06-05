import json
import logging
from typing import Dict, Any, List, Optional
from .llm_manager import LLMManager

logger = logging.getLogger("mintuu.llm.reasoning")

class ReasoningEngine:
    """Engine for chain-of-thought reasoning and structured output generation."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        
    async def reason(self, 
                    agent_id: str, 
                    task: str, 
                    context: Dict[str, Any],
                    system_prompt: str,
                    model_preference: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a reasoning chain.
        1. Build prompt with context
        2. Ask LLM to reason (Chain of Thought) and output JSON
        3. Parse and validate
        """
        prompt = self._build_reasoning_prompt(task, context)
        
        logger.info(f"[{agent_id}] Starting reasoning chain for task: {task[:50]}...")
        
        # Enforce JSON output for structured reasoning
        response = await self.llm.generate_response(
            agent_id=agent_id,
            prompt=prompt,
            system_prompt=system_prompt,
            model_preference=model_preference,
            temperature=0.4,
            json_mode=True
        )
        
        content = response.get("content", "{}")
        try:
            # Handle potential markdown code blocks around JSON
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            parsed_output = json.loads(content)
            
            # Self-critique / validation could be injected here
            confidence = parsed_output.get("confidence_score", 1.0)
            if confidence < 0.6:
                logger.warning(f"[{agent_id}] Low confidence reasoning ({confidence}).")
                
            return parsed_output
            
        except json.JSONDecodeError as e:
            logger.error(f"[{agent_id}] Failed to parse reasoning output as JSON: {e}")
            logger.debug(f"Raw output: {content}")
            return {
                "thought_process": "Failed to generate structured reasoning.",
                "action_plan": [],
                "error": str(e),
                "raw": content
            }
            
    def _build_reasoning_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Construct a structured prompt forcing Chain of Thought."""
        return f"""
TASK:
{task}

CONTEXT:
{json.dumps(context, indent=2)}

INSTRUCTIONS:
You must reason through this task step-by-step. 
Provide your response strictly as a JSON object with the following schema:
{{
    "thought_process": "Detailed step-by-step reasoning",
    "required_tools": ["tool1", "tool2"],
    "action_plan": [
        {{"step": 1, "action": "...", "expected_outcome": "..."}}
    ],
    "confidence_score": 0.95,
    "final_decision": "Summary of what to do"
}}
"""
