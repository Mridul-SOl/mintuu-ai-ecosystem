"""
Mintuu AI Ecosystem - State Manager
====================================
Global state management with checkpointing and recovery.
Tracks system-wide state including agent statuses, workflow progress,
and operational metrics.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger("mintuu.state")


class AgentStatus(Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    COMMUNICATING = "COMMUNICATING"
    WAITING = "WAITING"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"


@dataclass
class AgentState:
    """Runtime state for a single agent."""
    agent_id: str
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    current_workflow_id: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time_ms: int = 0
    last_active: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "current_task_id": self.current_task_id,
            "current_workflow_id": self.current_workflow_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_execution_time_ms": self.total_execution_time_ms,
            "last_active": self.last_active,
            "metadata": self.metadata,
        }


@dataclass
class SystemState:
    """Global system state snapshot."""
    active_workflows: int = 0
    active_tasks: int = 0
    total_agents: int = 0
    active_agents: int = 0
    uptime_seconds: float = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_workflows_completed: int = 0
    system_health: str = "HEALTHY"
    last_checkpoint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_workflows": self.active_workflows,
            "active_tasks": self.active_tasks,
            "total_agents": self.total_agents,
            "active_agents": self.active_agents,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "total_workflows_completed": self.total_workflows_completed,
            "system_health": self.system_health,
            "last_checkpoint": self.last_checkpoint,
        }


class StateManager:
    """
    Centralized state manager for the Mintuu AI Ecosystem.

    Tracks:
    - Individual agent states
    - System-wide operational state
    - Workflow execution states
    - Checkpoints for recovery
    """

    def __init__(self):
        self._agent_states: Dict[str, AgentState] = {}
        self._system_state = SystemState()
        self._workflow_states: Dict[str, Dict[str, Any]] = {}
        self._start_time = time.time()
        self._checkpoints: List[Dict[str, Any]] = []
        logger.info("State Manager initialized")

    # --------------------------------------------------------
    # Agent State Management
    # --------------------------------------------------------

    def register_agent(self, agent_id: str, agent_type: str):
        """Register an agent in the state tracker."""
        self._agent_states[agent_id] = AgentState(
            agent_id=agent_id,
            agent_type=agent_type,
        )
        self._system_state.total_agents = len(self._agent_states)
        logger.info(f"Agent registered: {agent_id} ({agent_type})")

    def update_agent_status(self, agent_id: str, status: AgentStatus,
                            task_id: Optional[str] = None,
                            workflow_id: Optional[str] = None):
        """Update an agent's operational status."""
        if agent_id not in self._agent_states:
            logger.warning(f"Agent {agent_id} not registered")
            return

        state = self._agent_states[agent_id]
        state.status = status
        state.last_active = datetime.now(timezone.utc).isoformat()

        if task_id is not None:
            state.current_task_id = task_id
        if workflow_id is not None:
            state.current_workflow_id = workflow_id

        # Update active agent count
        self._system_state.active_agents = sum(
            1 for s in self._agent_states.values()
            if s.status not in (AgentStatus.IDLE, AgentStatus.OFFLINE)
        )
        logger.debug(f"Agent {agent_id} → {status.value}")

    def record_task_completion(self, agent_id: str, duration_ms: int, success: bool):
        """Record a task completion for an agent."""
        if agent_id in self._agent_states:
            state = self._agent_states[agent_id]
            if success:
                state.tasks_completed += 1
                self._system_state.total_tasks_completed += 1
            else:
                state.tasks_failed += 1
                self._system_state.total_tasks_failed += 1
            state.total_execution_time_ms += duration_ms
            state.current_task_id = None

    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of an agent."""
        if agent_id in self._agent_states:
            return self._agent_states[agent_id].to_dict()
        return None

    def get_all_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states for all registered agents."""
        return {
            aid: state.to_dict()
            for aid, state in self._agent_states.items()
        }

    # --------------------------------------------------------
    # Workflow State Management
    # --------------------------------------------------------

    def set_workflow_state(self, workflow_id: str, state_data: Dict[str, Any]):
        """Set the execution state for a workflow."""
        self._workflow_states[workflow_id] = {
            **state_data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._system_state.active_workflows = len(self._workflow_states)

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the execution state for a workflow."""
        return self._workflow_states.get(workflow_id)

    def clear_workflow_state(self, workflow_id: str):
        """Remove a completed workflow's state."""
        self._workflow_states.pop(workflow_id, None)
        self._system_state.active_workflows = len(self._workflow_states)
        self._system_state.total_workflows_completed += 1

    # --------------------------------------------------------
    # System State
    # --------------------------------------------------------

    def get_system_state(self) -> Dict[str, Any]:
        """Get the current system-wide state."""
        self._system_state.uptime_seconds = time.time() - self._start_time
        return self._system_state.to_dict()

    def update_system_health(self, health: str):
        """Update overall system health status."""
        self._system_state.system_health = health

    # --------------------------------------------------------
    # Checkpoints
    # --------------------------------------------------------

    def create_checkpoint(self) -> Dict[str, Any]:
        """Create a full state checkpoint for recovery."""
        checkpoint = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_state": self._system_state.to_dict(),
            "agent_states": self.get_all_agent_states(),
            "workflow_states": dict(self._workflow_states),
        }
        self._checkpoints.append(checkpoint)
        self._system_state.last_checkpoint = checkpoint["timestamp"]

        # Keep only last 100 checkpoints
        if len(self._checkpoints) > 100:
            self._checkpoints = self._checkpoints[-100:]

        logger.info(f"Checkpoint created at {checkpoint['timestamp']}")
        return checkpoint

    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the most recent checkpoint."""
        return self._checkpoints[-1] if self._checkpoints else None

    def restore_from_checkpoint(self, checkpoint: Dict[str, Any]):
        """Restore system state from a checkpoint."""
        logger.info(f"Restoring from checkpoint: {checkpoint.get('timestamp')}")
        self._workflow_states = checkpoint.get("workflow_states", {})
        # Agent states would need re-registration; this restores metadata only
