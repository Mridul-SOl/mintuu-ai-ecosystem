import logging
from typing import Dict, Any
from core.memory.memory_manager import MemoryManager

logger = logging.getLogger("mintuu.llm.context")

class ContextBuilder:
    """Builds rich context for LLM prompts by querying memory and state."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    def build_task_context(self, agent_id: str, workflow_id: str = None) -> Dict[str, Any]:
        """Compile relevant context for a specific task."""
        context = {
            "agent_memory": self.memory.get_agent_memory(agent_id),
            "organizational_knowledge": self.memory.get_organizational_memory()[-5:] # Last 5 entries
        }
        
        if workflow_id:
            context["workflow_state"] = self.memory.get_workflow_memory(workflow_id)
            
        return context
