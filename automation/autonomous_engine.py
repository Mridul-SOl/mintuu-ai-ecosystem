"""
Mintuu AI Ecosystem — Autonomous Engine
=========================================
Event-driven autonomous business simulation. Agents operate continuously
with scheduled tasks, recurring workflows, and self-triggered activities.
"""

import time
import uuid
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("mintuu.autonomous")


class TriggerType(Enum):
    SCHEDULED = "SCHEDULED"        # Runs at intervals
    EVENT_DRIVEN = "EVENT_DRIVEN"  # Triggered by events
    ONE_SHOT = "ONE_SHOT"          # Runs once


@dataclass
class AutonomousTask:
    """A recurring or event-driven autonomous task."""
    id: str
    name: str
    agent_type: str
    description: str
    trigger_type: TriggerType
    interval_seconds: int = 300     # Default: every 5 minutes
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    is_active: bool = True
    max_runs: Optional[int] = None  # None = infinite
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.next_run and self.trigger_type == TriggerType.SCHEDULED:
            self.next_run = (
                datetime.now(timezone.utc) + timedelta(seconds=self.interval_seconds)
            ).isoformat()

    def should_run(self) -> bool:
        if not self.is_active:
            return False
        if self.max_runs and self.run_count >= self.max_runs:
            return False
        if self.trigger_type == TriggerType.SCHEDULED:
            if self.next_run:
                return datetime.now(timezone.utc).isoformat() >= self.next_run
        return False

    def mark_run(self):
        self.last_run = datetime.now(timezone.utc).isoformat()
        self.run_count += 1
        if self.trigger_type == TriggerType.SCHEDULED:
            self.next_run = (
                datetime.now(timezone.utc) + timedelta(seconds=self.interval_seconds)
            ).isoformat()
        if self.max_runs and self.run_count >= self.max_runs:
            self.is_active = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agent_type": self.agent_type,
            "description": self.description,
            "trigger_type": self.trigger_type.value,
            "interval_seconds": self.interval_seconds,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "is_active": self.is_active,
        }


@dataclass
class SimulationEvent:
    """Record of an autonomous execution."""
    timestamp: str
    task_id: str
    task_name: str
    agent_type: str
    status: str
    summary: str = ""
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "agent_type": self.agent_type,
            "status": self.status,
            "summary": self.summary[:100],
            "duration_ms": self.duration_ms,
        }


class AutonomousEngine:
    """
    Autonomous business simulation engine.

    Pre-configured business operations:
    - CEO: Quarterly goal reviews
    - Finance: Budget monitoring
    - Marketing: Campaign performance tracking
    - Operations: System health checks
    - Research: Competitor monitoring
    - HR: Team capacity analysis
    - Production: Infrastructure health

    Can be extended with custom scheduled tasks.
    """

    def __init__(self):
        self._tasks: Dict[str, AutonomousTask] = {}
        self._event_log: List[SimulationEvent] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._execute_fn: Optional[Callable] = None
        self._tick_interval = 10  # Check every 10 seconds
        self._register_default_tasks()
        logger.info("Autonomous Engine initialized")

    def set_executor(self, execute_fn: Callable):
        """Set the task executor (usually orchestrator.execute_task)."""
        self._execute_fn = execute_fn

    # ─────────────────────────────────────────────
    # Default Business Operations
    # ─────────────────────────────────────────────

    def _register_default_tasks(self):
        """Register default autonomous business operations."""
        defaults = [
            AutonomousTask(
                id="auto-ceo-review",
                name="CEO Quarterly Review",
                agent_type="CEO",
                description="Review company KPIs, agent performance, and strategic goals",
                trigger_type=TriggerType.SCHEDULED,
                interval_seconds=600,  # Every 10 min in simulation
            ),
            AutonomousTask(
                id="auto-finance-budget",
                name="Finance Budget Check",
                agent_type="Finance",
                description="Monitor budget allocation, expenses, and revenue forecasts",
                trigger_type=TriggerType.SCHEDULED,
                interval_seconds=300,
            ),
            AutonomousTask(
                id="auto-marketing-metrics",
                name="Marketing Campaign Metrics",
                agent_type="Marketing",
                description="Track campaign performance, SEO rankings, and content engagement",
                trigger_type=TriggerType.SCHEDULED,
                interval_seconds=450,
            ),
            AutonomousTask(
                id="auto-ops-health",
                name="Operations Health Check",
                agent_type="Operations",
                description="Monitor system health, workflow efficiency, and automation status",
                trigger_type=TriggerType.SCHEDULED,
                interval_seconds=180,
            ),
            AutonomousTask(
                id="auto-research-competitors",
                name="Research Competitor Watch",
                agent_type="Research",
                description="Analyze competitor activities, market trends, and industry news",
                trigger_type=TriggerType.SCHEDULED,
                interval_seconds=900,
            ),
        ]
        for task in defaults:
            self._tasks[task.id] = task

    # ─────────────────────────────────────────────
    # Task Management
    # ─────────────────────────────────────────────

    def add_task(self, name: str, agent_type: str, description: str,
                 interval_seconds: int = 300,
                 trigger_type: TriggerType = TriggerType.SCHEDULED,
                 max_runs: Optional[int] = None) -> str:
        """Register a new autonomous task."""
        task = AutonomousTask(
            id=f"auto-{uuid.uuid4().hex[:8]}",
            name=name,
            agent_type=agent_type,
            description=description,
            trigger_type=trigger_type,
            interval_seconds=interval_seconds,
            max_runs=max_runs,
        )
        self._tasks[task.id] = task
        logger.info(f"Autonomous task registered: {name} ({task.id})")
        return task.id

    def pause_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            self._tasks[task_id].is_active = False
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            self._tasks[task_id].is_active = True
            return True
        return False

    def remove_task(self, task_id: str) -> bool:
        return bool(self._tasks.pop(task_id, None))

    # ─────────────────────────────────────────────
    # Engine Control
    # ─────────────────────────────────────────────

    def start(self):
        """Start the autonomous engine loop."""
        if self._is_running:
            return
        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Autonomous engine STARTED")

    def stop(self):
        """Stop the autonomous engine."""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=15)
        logger.info("Autonomous engine STOPPED")

    def _run_loop(self):
        """Main engine loop — checks and executes scheduled tasks."""
        while self._is_running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Autonomous engine tick error: {e}")
            time.sleep(self._tick_interval)

    def _tick(self):
        """Single tick: check all tasks and execute if due."""
        for task in list(self._tasks.values()):
            if task.should_run() and self._execute_fn:
                try:
                    start = time.time()
                    result = self._execute_fn(task.description, task.agent_type)
                    duration = int((time.time() - start) * 1000)

                    task.mark_run()
                    event = SimulationEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        task_id=task.id,
                        task_name=task.name,
                        agent_type=task.agent_type,
                        status="SUCCESS" if result.get("status") == "SUCCESS" else "PARTIAL",
                        summary=result.get("summary", "")[:100],
                        duration_ms=duration,
                    )
                    self._event_log.append(event)

                    # Keep log bounded
                    if len(self._event_log) > 500:
                        self._event_log = self._event_log[-500:]

                    logger.info(
                        f"Autonomous: {task.name} → {event.status} ({duration}ms)"
                    )
                except Exception as e:
                    logger.error(f"Autonomous task {task.name} failed: {e}")
                    self._event_log.append(SimulationEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        task_id=task.id,
                        task_name=task.name,
                        agent_type=task.agent_type,
                        status="ERROR",
                        summary=str(e)[:100],
                    ))

    # ─────────────────────────────────────────────
    # Trigger Manually
    # ─────────────────────────────────────────────

    def trigger_now(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Manually trigger a task immediately."""
        task = self._tasks.get(task_id)
        if not task or not self._execute_fn:
            return None
        start = time.time()
        result = self._execute_fn(task.description, task.agent_type)
        duration = int((time.time() - start) * 1000)
        task.mark_run()
        event = SimulationEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task.id,
            task_name=task.name,
            agent_type=task.agent_type,
            status="SUCCESS" if result.get("status") == "SUCCESS" else "PARTIAL",
            summary=result.get("summary", "")[:100],
            duration_ms=duration,
        )
        self._event_log.append(event)
        return event.to_dict()

    # ─────────────────────────────────────────────
    # Status
    # ─────────────────────────────────────────────

    def get_tasks(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._tasks.values()]

    def get_event_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._event_log[-limit:]]

    def get_stats(self) -> Dict[str, Any]:
        active = sum(1 for t in self._tasks.values() if t.is_active)
        return {
            "is_running": self._is_running,
            "total_tasks": len(self._tasks),
            "active_tasks": active,
            "total_executions": len(self._event_log),
            "tasks": [t.to_dict() for t in self._tasks.values()],
        }
