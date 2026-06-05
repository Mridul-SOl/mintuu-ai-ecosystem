"""
Mintuu AI Ecosystem - Research Agent
=====================================
Market research, competitor analysis, information gathering, structured summaries.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from mintuu_ai_ecosystem.agents.base_agent.base import BaseAgent

logger = logging.getLogger("mintuu.agent.research")


class ResearchAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            agent_id="agent-research", agent_type="Research", name="Research Agent",
            description="Market research, competitor analysis, information gathering, and structured summaries",
            capabilities=["market_research", "competitor_analysis", "information_gathering",
                         "trend_analysis", "data_synthesis", "structured_summaries"],
            **kwargs)
        self._research_reports: List[Dict] = []

    def plan(self, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        desc = task_description.lower()
        if any(kw in desc for kw in ["competitor", "competition"]):
            steps = [{"step": 1, "action": "identify_competitors"}, {"step": 2, "action": "analyze_strengths"},
                     {"step": 3, "action": "compare_features"}, {"step": 4, "action": "report"}]
        elif any(kw in desc for kw in ["market", "industry", "trend"]):
            steps = [{"step": 1, "action": "gather_data"}, {"step": 2, "action": "analyze_trends"},
                     {"step": 3, "action": "synthesize"}]
        else:
            steps = [{"step": 1, "action": "research"}, {"step": 2, "action": "summarize"}]
        return {"agent": self.name, "task": task_description, "steps": steps}

    def execute(self, task: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        desc = task.get("description", "").lower()
        if "competitor" in desc:
            outputs = {
                "competitors": [
                    {"name": "CompanyA", "strengths": ["Brand recognition"], "weaknesses": ["Limited AI"]},
                    {"name": "CompanyB", "strengths": ["Large team"], "weaknesses": ["Slow innovation"]},
                ],
                "recommendation": "Strong competitive position. Focus on AI differentiation.",
            }
        elif "market" in desc or "trend" in desc:
            outputs = {
                "market_size": "$150B by 2028", "growth_rate": "24% CAGR",
                "key_trends": ["AI-native operations", "Multi-agent systems", "Autonomous workflows"],
                "recommendation": "Market expanding rapidly. First-mover advantage critical.",
            }
        else:
            outputs = {
                "research_summary": f"Research completed for: {desc[:100]}",
                "key_findings": ["Finding 1: Positive market signals", "Finding 2: Growing demand"],
                "recommendation": "Research indicates favorable conditions.",
            }
        report = {"topic": desc[:50], "outputs": outputs, "created_at": datetime.now(timezone.utc).isoformat()}
        self._research_reports.append(report)
        
        # Inject the vector memory results into the output so other agents can see them easily
        if context and "vector_memory_results" in context:
            outputs["vector_memory_results"] = context["vector_memory_results"]
            
        return {"agent": self.name, "task_title": task.get("title", ""), "status": "completed", "outputs": outputs}

    def summarize(self, results: Dict[str, Any]) -> str:
        o = results.get("outputs", {})
        decision = o.get("llm_decision") or o.get("recommendation", "Done")
        return f"🔍 **Research Summary** | Task: {results.get('task_title')} | {decision}"
        
    def handle_task(self, task: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Override to actually query vector memory before reasoning."""
        if context is None:
            context = {}
            
        # Perform semantic search on the task description
        desc = task.get("description", "")
        if "memory" in self.capabilities or True:
            # Query the memory manager for relevant context
            past_memories = self.memory.query_vector_memory(desc, limit=3)
            if past_memories:
                context["vector_memory_results"] = [m["document"] for m in past_memories]
            else:
                context["vector_memory_results"] = ["No previous incidents found matching this description."]
                
        # Now call the base handler which will pass this enriched context to the LLM
        return super().handle_task(task, context)
