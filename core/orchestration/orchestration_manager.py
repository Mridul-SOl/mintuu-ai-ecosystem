"""
Mintuu AI Ecosystem — Central Orchestration Manager v2
=======================================================
The OS kernel of the ecosystem. Coordinates all agents, workflows,
tasks, collaboration, tool execution, autonomous operations,
and system-wide intelligence.
"""
import uuid
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from mintuu_ai_ecosystem.config.settings import settings
from mintuu_ai_ecosystem.database.models import (
    DatabaseManager, TaskStatus, WorkflowStatus, EventType
)
from mintuu_ai_ecosystem.core.memory.memory_manager import MemoryManager
from mintuu_ai_ecosystem.core.state.state_manager import StateManager
from mintuu_ai_ecosystem.core.communication.message_bus import MessageBus, MessageType
from mintuu_ai_ecosystem.core.orchestration.agent_registry import AgentRegistry
from mintuu_ai_ecosystem.core.orchestration.task_router import TaskRouter
from mintuu_ai_ecosystem.core.orchestration.collaboration_engine import CollaborationEngine
from mintuu_ai_ecosystem.core.workflows.workflow_engine import WorkflowEngine
from mintuu_ai_ecosystem.tools.tool_registry import ToolRegistry
from mintuu_ai_ecosystem.tools.execution_manager import ExecutionManager
from mintuu_ai_ecosystem.automation.autonomous_engine import AutonomousEngine
from mintuu_ai_ecosystem.core.llm.llm_manager import LLMManager
from mintuu_ai_ecosystem.core.llm.reasoning_engine import ReasoningEngine

# Agents
from mintuu_ai_ecosystem.agents.ceo_agent.agent import CEOAgent
from mintuu_ai_ecosystem.agents.hr_agent.agent import HRAgent
from mintuu_ai_ecosystem.agents.marketing_agent.agent import MarketingAgent
from mintuu_ai_ecosystem.agents.finance_agent.agent import FinanceAgent
from mintuu_ai_ecosystem.agents.production_agent.agent import ProductionAgent
from mintuu_ai_ecosystem.agents.operations_agent.agent import OperationsAgent
from mintuu_ai_ecosystem.agents.research_agent.agent import ResearchAgent
from mintuu_ai_ecosystem.agents.security_agent.agent import SecurityAgent
from mintuu_ai_ecosystem.agents.infrastructure_agent.agent import InfrastructureAgent

logger = logging.getLogger("mintuu.orchestrator")


class OrchestrationManager:
    """
    Central Orchestration Manager v2 — the core kernel of Mintuu AI Ecosystem.

    Integrations:
    - Agent Registry + Task Router           (routing)
    - Collaboration Engine                   (inter-agent comms)
    - Dynamic Workflow Engine                (multi-step pipelines)
    - Execution Manager + Tool Registry      (tool usage)
    - Autonomous Engine                      (scheduled operations)
    - Memory Manager                         (contextual intelligence)
    - State Manager                          (system health)
    - Message Bus                            (communication backbone)
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("  MINTUU AI ECOSYSTEM v2 — INITIALIZING")
        logger.info("=" * 60)

        # ── Core Infrastructure ──────────────────────────
        self.db = DatabaseManager()
        self.memory = MemoryManager(self.db)
        self.state = StateManager()
        self.message_bus = MessageBus()
        self.tool_registry = ToolRegistry(self.db)
        self.agent_registry = AgentRegistry()

        # ── Phase 1: Collaboration Engine ────────────────
        self.collaboration = CollaborationEngine(self.message_bus)

        # ── Phase 3: Execution Manager ───────────────────
        self.execution = ExecutionManager(self.tool_registry)

        # ── Phase 1/2: LLM & Reasoning ───────────────────
        self.llm_manager = LLMManager()
        self.reasoning_engine = ReasoningEngine(self.llm_manager)

        # ── Initialize Agents ────────────────────────────
        self._init_agents()

        # ── Routing & Workflow ───────────────────────────
        self.task_router = TaskRouter(self.agent_registry)
        self.workflow_engine = WorkflowEngine(
            self.db, self.state, self.agent_registry,
            collaboration_engine=self.collaboration,
        )

        # ── Phase 6: Autonomous Engine ───────────────────
        self.autonomous = AutonomousEngine()
        self.autonomous.set_executor(self.execute_task)

        # ── System Metadata ──────────────────────────────
        self._start_time = time.time()

        logger.info("=" * 60)
        logger.info(f"  ECOSYSTEM v2 ONLINE — {self.agent_registry.count} agents active")
        logger.info(f"  Tools: {len(self.tool_registry._tools)} | Autonomous tasks: {len(self.autonomous._tasks)}")
        logger.info("=" * 60)

    def _init_agents(self):
        """Initialize and register all specialized agents."""
        agent_kwargs = {
            "db": self.db, "memory": self.memory, "state": self.state,
            "message_bus": self.message_bus, "tool_registry": self.tool_registry,
            "llm": self.llm_manager, "reasoning": self.reasoning_engine
        }

        agents = [
            CEOAgent(**agent_kwargs),
            HRAgent(**agent_kwargs),
            MarketingAgent(**agent_kwargs),
            FinanceAgent(**agent_kwargs),
            ProductionAgent(**agent_kwargs),
            OperationsAgent(**agent_kwargs),
            ResearchAgent(**agent_kwargs),
            SecurityAgent(**agent_kwargs),
            InfrastructureAgent(**agent_kwargs),
        ]

        for agent in agents:
            self.agent_registry.register(agent)

    # ============================================================
    # Task Execution (with collaboration + memory)
    # ============================================================

    def execute_task(self, description: str, agent_type: Optional[str] = None,
                     conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a single task with intelligent routing and memory."""
        # Route to agent
        target_type = agent_type or self.task_router.route(description)
        if not target_type:
            return {"status": "ERROR", "error": "Could not determine appropriate agent"}

        agent = self.agent_registry.get_agent_by_type(target_type)
        if not agent:
            return {"status": "ERROR", "error": f"Agent not found: {target_type}"}

        # Create task in DB
        task_id = self.db.create_task(
            title=f"Task: {description[:80]}",
            description=description,
            assigned_agent=agent.agent_id,
        )

        task = {
            "id": task_id, "title": f"Task: {description[:80]}",
            "description": description, "type": "general",
        }

        # Build rich context (Phase 4: includes memory + workflow history)
        context = self.memory.build_agent_context(
            agent.agent_id, conversation_id=conversation_id
        )

        # Execute
        self.db.update_task_status(task_id, TaskStatus.RUNNING)

        # Broadcast task start through message bus
        self.message_bus.broadcast(
            sender="orchestrator",
            message_type=MessageType.STATUS_UPDATE,
            content={
                "event": "task_started",
                "task_id": task_id,
                "agent": target_type,
                "description": description[:100],
            },
        )

        result = agent.handle_task(task, context)

        # Update status
        if result.get("status") == "SUCCESS":
            self.db.update_task_status(task_id, TaskStatus.COMPLETED,
                                       result=result.get("summary", ""))

            # Store result in organizational memory
            self.memory.store_organizational(
                key=f"task_result:{task_id}",
                content=result.get("summary", ""),
                source_agent=agent.agent_id,
                metadata={"task_id": task_id, "agent_type": target_type},
            )
        else:
            self.db.update_task_status(task_id, TaskStatus.FAILED,
                                       error=result.get("error", ""))

        # Broadcast completion
        self.message_bus.broadcast(
            sender="orchestrator",
            message_type=MessageType.STATUS_UPDATE,
            content={
                "event": "task_completed",
                "task_id": task_id,
                "agent": target_type,
                "status": result.get("status", "UNKNOWN"),
            },
        )

        result["task_id"] = task_id
        result["agent_type"] = target_type
        return result

    # ============================================================
    # Workflow Execution (with collaboration)
    # ============================================================

    def execute_workflow(self, name: str, description: str,
                         steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create and execute a collaborative multi-agent workflow."""
        workflow_id = self.workflow_engine.create_workflow(name, description, steps)

        # Broadcast workflow start
        self.collaboration.broadcast_update(
            sender="orchestrator",
            update=f"Workflow started: {name}",
            data={"workflow_id": workflow_id, "steps": len(steps)},
            workflow_id=workflow_id,
        )

        result = self.workflow_engine.execute_workflow(workflow_id)

        # Store workflow results in memory
        self.memory.store_workflow_memory(
            workflow_id=workflow_id,
            key="final_result",
            content=json.dumps(result.get("results", {})),
            metadata={"name": name, "status": result.get("status")},
        )

        return result

    def execute_auto_workflow(self, description: str) -> Dict[str, Any]:
        """Auto-detect required agents and create a dynamic workflow."""
        agent_order = self.task_router.suggest_workflow(description)
        if not agent_order:
            return {"status": "ERROR", "error": "Could not determine workflow agents"}

        steps = []
        for i, agent_type in enumerate(agent_order):
            steps.append({
                "agent_type": agent_type,
                "title": f"{agent_type.upper()} Analysis",
                "description": f"{description} — {agent_type} department perspective",
                "depends_on": [i-1] if i > 0 else [],
                "requires_approval": (i == 0 and "CEO" in [a.upper() for a in agent_order]),
            })

        return self.execute_workflow(
            name=f"Auto-Workflow: {description[:50]}",
            description=description,
            steps=steps,
        )

    # ============================================================
    # Autonomous Operations
    # ============================================================

    def start_autonomous(self):
        """Start the autonomous business simulation."""
        self.autonomous.start()
        logger.info("Autonomous operations STARTED")

    def stop_autonomous(self):
        """Stop autonomous operations."""
        self.autonomous.stop()
        logger.info("Autonomous operations STOPPED")

    # ============================================================
    # System Status & Analytics (comprehensive v2)
    # ============================================================

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status v2."""
        return {
            "ecosystem": {
                "name": settings.project_name,
                "version": settings.version,
                "environment": settings.environment.value,
                "uptime_seconds": round(time.time() - self._start_time, 2),
            },
            "agents": self.agent_registry.list_agents(),
            "system_state": self.state.get_system_state(),
            "message_bus": self.message_bus.get_stats(),
            "tools": self.execution.get_stats(),
            "memory": self.memory.get_memory_stats(),
            "db_stats": self.db.get_system_stats(),
            "active_workflows": self.workflow_engine.list_active_workflows(),
            "completed_workflows": self.workflow_engine.list_completed_workflows(5),
            "collaboration": self.collaboration.get_stats(),
            "autonomous": self.autonomous.get_stats(),
        }

    def get_agents(self) -> List[Dict[str, Any]]:
        return self.agent_registry.list_agents()

    def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        agent = self.agent_registry.get_agent_by_type(agent_type)
        return agent.get_info() if agent else None

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        return self.db.get_recent_events(limit)

    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        return self.db.get_recent_logs(limit)

    def get_collaboration_feed(self, limit: int = 50) -> Dict[str, Any]:
        """Get inter-agent collaboration activity."""
        return {
            "active_requests": self.collaboration.get_active_requests(),
            "recent_history": self.collaboration.get_history(limit),
            "stats": self.collaboration.get_stats(),
            "message_history": self.message_bus.get_history(limit=limit),
        }
