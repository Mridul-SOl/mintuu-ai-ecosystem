"""
Mintuu AI Ecosystem — Dynamic Workflow Engine v2
==================================================
Intelligent workflow execution with conditional branching, approval gates,
dynamic path modification, inter-agent collaboration, and real-time state
transitions. Replaces the static linear engine.
"""
import uuid
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field

from mintuu_ai_ecosystem.database.models import (
    DatabaseManager, WorkflowStatus, TaskStatus, EventType
)
from mintuu_ai_ecosystem.core.state.state_manager import StateManager
from mintuu_ai_ecosystem.core.orchestration.agent_registry import AgentRegistry

logger = logging.getLogger("mintuu.workflow")


# ============================================================
# Workflow State Machine
# ============================================================

class StepState(Enum):
    PENDING = "PENDING"
    WAITING = "WAITING"      # Waiting for dependencies
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"      # Blocked on approval/resource
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class WorkflowStep:
    """A single step within a workflow with full state tracking."""
    index: int
    agent_type: str
    task_title: str
    task_description: str
    depends_on: List[int] = field(default_factory=list)
    state: StepState = StepState.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    requires_approval: bool = False
    approval_status: Optional[str] = None
    condition: Optional[str] = None      # "previous_success", "budget_approved", etc.
    collaboration_ids: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "agent_type": self.agent_type,
            "task_title": self.task_title,
            "task_description": self.task_description,
            "depends_on": self.depends_on,
            "state": self.state.value,
            "status": self.state.value,  # alias for JS compat
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "requires_approval": self.requires_approval,
            "approval_status": self.approval_status,
            "condition": self.condition,
            "collaboration_ids": self.collaboration_ids,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
        }


@dataclass
class DynamicWorkflow:
    """Full workflow with dynamic execution capabilities."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: str = "PENDING"
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    initiated_by: str = "mintuu"
    results: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    collaboration_log: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "results": {
                str(k): v.get("summary", "") if isinstance(v, dict) else str(v)
                for k, v in self.results.items()
            },
            "collaboration_log": self.collaboration_log[-10:],
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class WorkflowEngine:
    """
    Dynamic Workflow Engine v2.

    Capabilities:
    - Dynamic workflow generation and modification
    - Conditional branching (skip steps based on conditions)
    - Approval checkpoints (CEO/authority gates)
    - Dependency graph resolution
    - Inter-step collaboration via message bus
    - Retry with exponential backoff
    - Step-level state transitions with timestamps
    - Real-time status reporting for dashboard
    - Workflow memory (agents share context through steps)
    """

    def __init__(self, db: DatabaseManager, state: StateManager,
                 registry: AgentRegistry, collaboration_engine=None):
        self.db = db
        self.state = state
        self.registry = registry
        self.collab = collaboration_engine   # Set post-init
        self._active_workflows: Dict[str, DynamicWorkflow] = {}
        self._completed_workflows: List[Dict[str, Any]] = []
        logger.info("Workflow Engine initialized")

    def set_collaboration_engine(self, collab):
        """Set the collaboration engine (resolves circular dependency)."""
        self.collab = collab

    # ============================================================
    # Workflow Creation
    # ============================================================

    def create_workflow(self, name: str, description: str,
                        steps: List[Dict[str, Any]],
                        initiated_by: str = "mintuu") -> str:
        """Create a new dynamic workflow from step definitions."""
        workflow_steps = []
        for i, step_def in enumerate(steps):
            ws = WorkflowStep(
                index=i,
                agent_type=step_def.get("agent_type", "operations"),
                task_title=step_def.get("title", f"Step {i+1}"),
                task_description=step_def.get("description", ""),
                depends_on=step_def.get("depends_on", [i-1] if i > 0 else []),
                max_retries=step_def.get("max_retries", 3),
                requires_approval=step_def.get("requires_approval", False),
                condition=step_def.get("condition"),
            )
            workflow_steps.append(ws)

        workflow_id = self.db.create_workflow(
            name=name, description=description,
            steps=[s.to_dict() for s in workflow_steps],
            initiated_by=initiated_by,
        )

        wf = DynamicWorkflow(
            id=workflow_id, name=name, description=description,
            steps=workflow_steps, initiated_by=initiated_by,
        )
        self._active_workflows[workflow_id] = wf

        self.db.log_event(EventType.WORKFLOW_CREATED, "workflow_engine",
                          f"Workflow created: {name}", {"workflow_id": workflow_id})
        logger.info(f"Workflow created: {name} ({workflow_id}) with {len(workflow_steps)} steps")
        return workflow_id

    # ============================================================
    # Dynamic Execution
    # ============================================================

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow with dynamic routing and collaboration."""
        wf = self._active_workflows.get(workflow_id)
        if not wf:
            return {"status": "ERROR", "error": "Workflow not found"}

        wf.status = "RUNNING"
        wf.started_at = datetime.now(timezone.utc).isoformat()
        self.db.update_workflow_status(workflow_id, WorkflowStatus.RUNNING)
        self.db.log_event(EventType.WORKFLOW_STARTED, "workflow_engine",
                          f"Workflow started: {wf.name}")
        self.state.set_workflow_state(workflow_id, {
            "status": "RUNNING", "name": wf.name,
            "total_steps": len(wf.steps),
        })

        # Execute steps respecting dependencies
        for step in wf.steps:
            step_result = self._execute_step(wf, step)
            if step.state == StepState.FAILED:
                # Check if we can continue (non-critical step)
                if not self._can_continue_after_failure(wf, step):
                    break

        # Finalize
        return self._finalize_workflow(wf)

    def _execute_step(self, wf: DynamicWorkflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step with full lifecycle management."""

        # 1. Check dependencies
        if not self._deps_met(wf, step):
            step.state = StepState.SKIPPED
            step.error = "Dependencies not met"
            logger.warning(f"Step {step.index} skipped: deps not met")
            return {"status": "SKIPPED"}

        # 2. Check conditions
        if step.condition and not self._evaluate_condition(wf, step):
            step.state = StepState.SKIPPED
            step.error = f"Condition not met: {step.condition}"
            logger.info(f"Step {step.index} skipped: condition '{step.condition}' not met")
            return {"status": "SKIPPED"}

        # 3. Approval gate
        if step.requires_approval:
            approval = self._handle_approval(wf, step)
            if not approval:
                step.state = StepState.BLOCKED
                step.approval_status = "DENIED"
                return {"status": "BLOCKED"}
            step.approval_status = "APPROVED"

        # 4. Inter-agent collaboration: share previous results as context
        previous_context = self._build_step_context(wf, step)

        # 5. Collaboration: request info from upstream if needed
        if self.collab and step.index > 0:
            prev_step = wf.steps[step.index - 1]
            if prev_step.state == StepState.COMPLETED and prev_step.result:
                collab_req = self.collab.handoff_data(
                    sender=f"agent-{prev_step.agent_type.lower()}",
                    receiver=f"agent-{step.agent_type.lower()}",
                    data=prev_step.result.get("results", prev_step.result),
                    workflow_id=wf.id,
                    description=f"Results from {prev_step.task_title}",
                )
                step.collaboration_ids.append(collab_req.id)
                wf.collaboration_log.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "DATA_HANDOFF",
                    "from": prev_step.agent_type,
                    "to": step.agent_type,
                    "step": step.index,
                })

        # 6. Execute with retry
        step.state = StepState.RUNNING
        step.started_at = datetime.now(timezone.utc).isoformat()
        self.db.update_workflow_status(wf.id, WorkflowStatus.RUNNING,
                                       current_step=step.index)

        success = False
        while step.retry_count <= step.max_retries and not success:
            try:
                agent = self.registry.get_agent_by_type(step.agent_type)
                if not agent:
                    step.state = StepState.FAILED
                    step.error = f"Agent not found: {step.agent_type}"
                    logger.error(step.error)
                    break

                task = {
                    "id": str(uuid.uuid4()),
                    "title": step.task_title,
                    "description": step.task_description,
                    "workflow_id": wf.id,
                    "step_index": step.index,
                }

                result = agent.handle_task(task, previous_context)

                if result.get("status") == "SUCCESS":
                    step.state = StepState.COMPLETED
                    step.result = result
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    step.duration_ms = result.get("duration_ms", 0)
                    wf.results[step.index] = result
                    success = True

                    # Log collaboration
                    wf.collaboration_log.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "STEP_COMPLETED",
                        "agent": step.agent_type,
                        "step": step.index,
                        "duration_ms": step.duration_ms,
                    })
                    logger.info(f"Step {step.index} completed by {step.agent_type}")
                else:
                    step.retry_count += 1
                    if step.retry_count > step.max_retries:
                        step.state = StepState.FAILED
                        step.error = result.get("error", "Unknown error")
                    else:
                        logger.warning(
                            f"Step {step.index} retry {step.retry_count}/{step.max_retries}"
                        )
                        time.sleep(0.1 * step.retry_count)

            except Exception as e:
                step.retry_count += 1
                step.error = str(e)
                if step.retry_count > step.max_retries:
                    step.state = StepState.FAILED
                    logger.error(f"Step {step.index} failed permanently: {e}")
                else:
                    logger.warning(f"Step {step.index} error, retrying: {e}")

        return step.result or {"status": step.state.value}

    # ============================================================
    # Dynamic Workflow Modification
    # ============================================================

    def add_step(self, workflow_id: str, step_def: Dict[str, Any],
                 insert_after: Optional[int] = None) -> bool:
        """Dynamically add a step to a running workflow."""
        wf = self._active_workflows.get(workflow_id)
        if not wf:
            return False

        idx = insert_after + 1 if insert_after is not None else len(wf.steps)
        new_step = WorkflowStep(
            index=idx,
            agent_type=step_def.get("agent_type", "operations"),
            task_title=step_def.get("title", f"Dynamic Step {idx}"),
            task_description=step_def.get("description", ""),
            depends_on=step_def.get("depends_on", [idx - 1] if idx > 0 else []),
        )

        # Re-index
        for s in wf.steps[idx:]:
            s.index += 1
            s.depends_on = [d + 1 if d >= idx else d for d in s.depends_on]

        wf.steps.insert(idx, new_step)
        logger.info(f"Dynamic step added to workflow {workflow_id}: {new_step.task_title}")
        return True

    def skip_step(self, workflow_id: str, step_index: int, reason: str = "") -> bool:
        """Dynamically skip a pending step."""
        wf = self._active_workflows.get(workflow_id)
        if not wf or step_index >= len(wf.steps):
            return False
        step = wf.steps[step_index]
        if step.state == StepState.PENDING:
            step.state = StepState.SKIPPED
            step.error = reason or "Skipped by orchestrator"
            logger.info(f"Step {step_index} skipped: {reason}")
            return True
        return False

    def reroute_step(self, workflow_id: str, step_index: int,
                     new_agent_type: str) -> bool:
        """Reroute a pending step to a different agent."""
        wf = self._active_workflows.get(workflow_id)
        if not wf or step_index >= len(wf.steps):
            return False
        step = wf.steps[step_index]
        if step.state == StepState.PENDING:
            old = step.agent_type
            step.agent_type = new_agent_type
            logger.info(f"Step {step_index} rerouted: {old} → {new_agent_type}")
            return True
        return False

    # ============================================================
    # Internal Helpers
    # ============================================================

    def _deps_met(self, wf: DynamicWorkflow, step: WorkflowStep) -> bool:
        """Check if all dependencies are met."""
        return all(
            wf.steps[d].state in (StepState.COMPLETED, StepState.SKIPPED)
            for d in step.depends_on
            if 0 <= d < len(wf.steps)
        )

    def _evaluate_condition(self, wf: DynamicWorkflow, step: WorkflowStep) -> bool:
        """Evaluate a step condition against workflow state."""
        cond = step.condition
        if not cond:
            return True
        if cond == "previous_success":
            prev = step.depends_on[-1] if step.depends_on else step.index - 1
            return (0 <= prev < len(wf.steps) and
                    wf.steps[prev].state == StepState.COMPLETED)
        if cond == "all_previous_success":
            return all(
                wf.steps[d].state == StepState.COMPLETED
                for d in step.depends_on if 0 <= d < len(wf.steps)
            )
        # Default: pass
        return True

    def _handle_approval(self, wf: DynamicWorkflow, step: WorkflowStep) -> bool:
        """Handle approval gate — auto-approve via CEO agent."""
        if self.collab:
            collab_req = self.collab.request_approval(
                requester=f"agent-{step.agent_type.lower()}",
                approver="agent-ceo",
                proposal=step.task_title,
                details={"step_index": step.index, "workflow": wf.name},
                workflow_id=wf.id,
            )
            step.collaboration_ids.append(collab_req.id)

            # Auto-resolve via CEO agent
            ceo = self.registry.get_agent_by_type("CEO")
            if ceo:
                self.collab.respond_to_request(
                    request_id=collab_req.id,
                    responder="agent-ceo",
                    response_data={"decision": "APPROVED", "reason": "Aligned with goals"},
                    approved=True,
                )

            wf.collaboration_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "APPROVAL_GATE",
                "step": step.index,
                "agent": step.agent_type,
                "status": "APPROVED",
            })

        return True  # Auto-approve for simulation

    def _build_step_context(self, wf: DynamicWorkflow, step: WorkflowStep) -> Dict[str, Any]:
        """Build context from all previous step results."""
        context = {
            "workflow_id": wf.id,
            "workflow_name": wf.name,
            "step_index": step.index,
            "total_steps": len(wf.steps),
            "previous_results": {},
            "collaboration_log": wf.collaboration_log[-5:],
        }
        for i, prev in enumerate(wf.steps[:step.index]):
            if prev.state == StepState.COMPLETED and prev.result:
                context["previous_results"][i] = {
                    "agent": prev.agent_type,
                    "summary": prev.result.get("summary", ""),
                    "status": prev.state.value,
                }
        return context

    def _can_continue_after_failure(self, wf: DynamicWorkflow,
                                     failed_step: WorkflowStep) -> bool:
        """Determine if workflow can continue despite a step failure."""
        # Check if any remaining steps depend on the failed one
        for step in wf.steps[failed_step.index + 1:]:
            if failed_step.index in step.depends_on:
                step.state = StepState.SKIPPED
                step.error = f"Dependency step {failed_step.index} failed"
        return True  # Always try to continue

    def _finalize_workflow(self, wf: DynamicWorkflow) -> Dict[str, Any]:
        """Finalize workflow and determine status."""
        completed = all(s.state in (StepState.COMPLETED, StepState.SKIPPED) for s in wf.steps)
        has_failures = any(s.state == StepState.FAILED for s in wf.steps)
        completed_count = sum(1 for s in wf.steps if s.state == StepState.COMPLETED)

        if completed and not has_failures:
            wf.status = "COMPLETED"
            self.db.update_workflow_status(wf.id, WorkflowStatus.COMPLETED,
                                           result=json.dumps({"steps_completed": completed_count}))
            self.db.log_event(EventType.WORKFLOW_COMPLETED, "workflow_engine",
                              f"Workflow completed: {wf.name}")
        elif has_failures:
            wf.status = "PARTIAL" if completed_count > 0 else "FAILED"
            final_status = WorkflowStatus.COMPLETED if completed_count > 0 else WorkflowStatus.FAILED
            self.db.update_workflow_status(wf.id, final_status)
            self.db.log_event(EventType.WORKFLOW_FAILED, "workflow_engine",
                              f"Workflow {'partial' if completed_count > 0 else 'failed'}: {wf.name}")
        else:
            wf.status = "PAUSED"

        wf.completed_at = datetime.now(timezone.utc).isoformat()
        self.state.clear_workflow_state(wf.id)

        # Move to completed history
        self._completed_workflows.append(wf.to_dict())
        if workflow_id := wf.id:
            self._active_workflows.pop(workflow_id, None)
            
        if len(self._completed_workflows) > 100:
            self._completed_workflows = self._completed_workflows[-100:]

        return wf.to_dict()

    # ============================================================
    # Status & History
    # ============================================================

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        wf = self._active_workflows.get(workflow_id)
        if wf:
            return wf.to_dict()
        return self.db.get_workflow(workflow_id)

    def list_active_workflows(self) -> List[Dict[str, Any]]:
        return [
            {"workflow_id": wid, "name": wf.name, "status": wf.status,
             "steps_count": len(wf.steps),
             "completed_steps": sum(1 for s in wf.steps if s.state == StepState.COMPLETED)}
            for wid, wf in self._active_workflows.items()
        ]

    def list_completed_workflows(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._completed_workflows[-limit:]

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        active = self.list_active_workflows()
        completed = self._completed_workflows[-10:]
        return active + completed
