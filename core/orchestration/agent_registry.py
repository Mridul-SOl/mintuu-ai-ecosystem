"""
Mintuu AI Ecosystem - Agent Registry
=====================================
Central registry for discovering, managing, and accessing all agents.
"""
import logging
from typing import Dict, Any, Optional, List
from mintuu_ai_ecosystem.agents.base_agent.base import BaseAgent

logger = logging.getLogger("mintuu.orchestration.registry")


class AgentRegistry:
    """Central registry for all ecosystem agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, str] = {}  # agent_type -> agent_id mapping
        logger.info("Agent Registry initialized")

    def register(self, agent: BaseAgent):
        """Register an agent."""
        self._agents[agent.agent_id] = agent
        self._agent_types[agent.agent_type.lower()] = agent.agent_id
        agent.activate()
        logger.info(f"Registered: {agent.name} ({agent.agent_id})")

    def unregister(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            agent.deactivate()
            self._agent_types.pop(agent.agent_type.lower(), None)
            del self._agents[agent_id]
            logger.info(f"Unregistered: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_agent_by_type(self, agent_type: str) -> Optional[BaseAgent]:
        """Get agent by type (e.g., 'CEO', 'HR')."""
        agent_id = self._agent_types.get(agent_type.lower())
        return self._agents.get(agent_id) if agent_id else None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [agent.get_info() for agent in self._agents.values()]

    def get_active_agents(self) -> List[BaseAgent]:
        """Get all active agents."""
        return [a for a in self._agents.values() if a.is_active]

    def get_agent_for_task(self, task_keywords: List[str]) -> Optional[BaseAgent]:
        """Route a task to the best-suited agent based on keywords."""
        keyword_map = {
            "strategy": "ceo", "decision": "ceo", "kpi": "ceo", "approve": "ceo", "goal": "ceo",
            "hire": "hr", "recruit": "hr", "onboard": "hr", "meeting": "hr", "employee": "hr",
            "campaign": "marketing", "seo": "marketing", "content": "marketing", "social": "marketing",
            "budget": "finance", "expense": "finance", "revenue": "finance", "cost": "finance",
            "deploy": "production", "release": "production", "monitor": "production", "health": "production",
            "automate": "operations", "coordinate": "operations", "workflow": "operations", "schedule": "operations",
            "research": "research", "competitor": "research", "market": "research", "analyze": "research",
        }
        for kw in task_keywords:
            agent_type = keyword_map.get(kw.lower())
            if agent_type:
                agent = self.get_agent_by_type(agent_type)
                if agent:
                    return agent
        return None

    @property
    def count(self) -> int:
        return len(self._agents)
