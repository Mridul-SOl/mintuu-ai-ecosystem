"""
Mintuu AI Ecosystem - Task Router
===================================
Intelligent task routing engine that determines which agents
should handle specific tasks based on content analysis.
"""
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from mintuu_ai_ecosystem.core.orchestration.agent_registry import AgentRegistry

logger = logging.getLogger("mintuu.orchestration.router")


class TaskRouter:
    """Routes tasks to appropriate agents based on intent analysis."""

    # Weighted keyword mappings: agent_type -> [(keyword, weight)]
    ROUTING_RULES: Dict[str, List[Tuple[str, float]]] = {
        "ceo": [("strategy", 1.0), ("strategic", 1.0), ("decision", 0.9), ("kpi", 0.9),
                ("approve", 0.9), ("goal", 0.8), ("vision", 0.8), ("leadership", 0.7),
                ("executive", 0.7), ("priority", 0.6), ("business plan", 1.0)],
        "hr": [("hire", 1.0), ("hiring", 1.0), ("recruit", 1.0), ("onboard", 0.9),
               ("employee", 0.8), ("meeting", 0.6), ("interview", 0.9), ("resume", 0.9),
               ("team", 0.5), ("candidate", 0.9), ("talent", 0.8)],
        "marketing": [("campaign", 1.0), ("marketing", 1.0), ("seo", 0.9), ("content", 0.7),
                      ("social media", 0.9), ("brand", 0.8), ("growth", 0.6), ("promotion", 0.8),
                      ("audience", 0.7), ("advertising", 0.9)],
        "finance": [("budget", 1.0), ("expense", 1.0), ("revenue", 0.9), ("financial", 0.9),
                    ("cost", 0.7), ("invoice", 0.9), ("profit", 0.8), ("accounting", 0.9),
                    ("forecast", 0.8), ("payment", 0.7)],
        "production": [("deploy", 1.0), ("deployment", 1.0), ("release", 0.9), ("build", 0.7),
                       ("infrastructure", 0.8), ("monitor", 0.6), ("ci/cd", 1.0), ("server", 0.7),
                       ("production", 0.5), ("pipeline", 0.7)],
        "operations": [("automate", 0.9), ("automation", 0.9), ("coordinate", 0.8),
                       ("workflow", 0.6), ("schedule", 0.6), ("process", 0.5),
                       ("operational", 0.7), ("efficiency", 0.6)],
        "research": [("research", 1.0), ("competitor", 0.9), ("market analysis", 1.0),
                     ("analyze", 0.5), ("investigate", 0.8), ("report", 0.4),
                     ("trend", 0.7), ("study", 0.7), ("data", 0.4)],
    }

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def route(self, task_description: str) -> Optional[str]:
        """
        Determine the best agent type for a task description.
        Returns agent_type string or None.
        """
        scores = self._score_agents(task_description)
        if not scores:
            return None
        best = max(scores, key=scores.get)
        if scores[best] < 0.3:
            logger.info(f"No confident routing for: {task_description[:60]} (best: {best}={scores[best]:.2f})")
            return None
        logger.info(f"Routed to {best} (score: {scores[best]:.2f})")
        return best

    def route_multi(self, task_description: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Route to multiple agents, returning ranked list."""
        scores = self._score_agents(task_description)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(t, s) for t, s in ranked[:top_n] if s > 0.2]

    def _score_agents(self, text: str) -> Dict[str, float]:
        """Score each agent type based on keyword matching."""
        text_lower = text.lower()
        scores: Dict[str, float] = {}
        for agent_type, keywords in self.ROUTING_RULES.items():
            score = 0.0
            for keyword, weight in keywords:
                if keyword in text_lower:
                    score += weight
            if score > 0:
                scores[agent_type] = min(score / 2.0, 1.0)  # Normalize
        return scores

    def suggest_workflow(self, task_description: str) -> List[str]:
        """Suggest a multi-agent workflow order for complex tasks."""
        desc_lower = task_description.lower()

        # If the request is company-wide or mentions all departments, use all agents
        all_dept_signals = ["all departments", "company-wide", "every department",
                           "full company", "entire organization", "across all",
                           "new product", "product launch"]
        if any(signal in desc_lower for signal in all_dept_signals):
            return ["ceo", "research", "marketing", "finance", "production", "operations"]

        agents = self.route_multi(task_description, top_n=5)
        # Always start with CEO for strategic tasks, end with operations
        order = [t for t, _ in agents]

        # Ensure at least one agent
        if not order:
            order = ["ceo", "operations"]

        if "ceo" in order:
            order.remove("ceo")
            order.insert(0, "ceo")
        if "operations" in order:
            order.remove("operations")
            order.append("operations")
        return order

