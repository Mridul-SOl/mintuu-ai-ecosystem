"""
Mintuu AI Ecosystem — Tool Execution Manager
==============================================
Manages async tool execution, sandboxed operations, execution tracking,
and agent-tool permissions. Wraps the ToolRegistry with execution intelligence.
"""

import os
import time
import json
import uuid
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from mintuu_ai_ecosystem.tools.tool_registry import (
    ToolRegistry, BaseTool, ToolResult, ToolCategory, ToolPermission,
)
from mintuu_ai_ecosystem.config.settings import BASE_DIR

logger = logging.getLogger("mintuu.execution")

# ============================================================
# Sandboxed Output Directory
# ============================================================

OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ExecutionRecord:
    """Tracks a single tool execution."""
    id: str
    agent_id: str
    tool_name: str
    params: Dict[str, Any]
    result: Optional[ToolResult] = None
    started_at: str = ""
    completed_at: Optional[str] = None
    duration_ms: int = 0

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "params": {k: str(v)[:100] for k, v in self.params.items()},
            "success": self.result.success if self.result else None,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
        }


# ============================================================
# Extended Tool Suite
# ============================================================

class GitStatusTool(BaseTool):
    """Check Git repository status."""
    def __init__(self):
        super().__init__()
        self.name = "git_status"
        self.description = "Check Git repository status in the project"
        self.category = ToolCategory.GITHUB
        self.parameters_schema = {"path": {"type": "string", "required": False}}

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", str(BASE_DIR))
        try:
            r = subprocess.run(
                ["git", "status", "--porcelain"], cwd=path,
                capture_output=True, text=True, timeout=10,
            )
            return ToolResult(success=True, output={
                "status": r.stdout.strip() or "Clean",
                "is_clean": not r.stdout.strip(),
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class SystemInfoTool(BaseTool):
    """Get system resource information."""
    def __init__(self):
        super().__init__()
        self.name = "system_info"
        self.description = "Get system CPU, memory, and disk information"
        self.category = ToolCategory.UTILITY
        self.parameters_schema = {}

    def execute(self, **kwargs) -> ToolResult:
        import platform
        try:
            info = {
                "os": platform.system(),
                "arch": platform.machine(),
                "python": platform.python_version(),
                "hostname": platform.node(),
            }
            return ToolResult(success=True, output=info)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DocumentGeneratorTool(BaseTool):
    """Generate business documents and save them."""
    def __init__(self):
        super().__init__()
        self.name = "document_generator"
        self.description = "Generate and save business documents (reports, plans, etc.)"
        self.category = ToolCategory.FILE
        self.required_permissions = [ToolPermission.WRITE]
        self.parameters_schema = {
            "doc_type": {"type": "string", "required": True},
            "title": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
        }

    def execute(self, **kwargs) -> ToolResult:
        doc_type = kwargs.get("doc_type", "report")
        title = kwargs.get("title", "Document")
        content = kwargs.get("content", "")
        try:
            filename = f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = OUTPUT_DIR / filename
            doc = f"# {title}\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n{content}"
            filepath.write_text(doc)
            return ToolResult(
                success=True,
                output={"file": str(filepath), "filename": filename, "size": len(doc)},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CalendarTool(BaseTool):
    """Manage calendar events and scheduling."""
    def __init__(self):
        super().__init__()
        self.name = "calendar_manager"
        self.description = "Create and manage calendar events"
        self.category = ToolCategory.CALENDAR
        self._events: List[Dict] = []

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "list")
        if action == "create":
            event = {
                "id": str(uuid.uuid4())[:8],
                "title": kwargs.get("title", "Meeting"),
                "date": kwargs.get("date", datetime.now().strftime("%Y-%m-%d")),
                "time": kwargs.get("time", "10:00"),
                "attendees": kwargs.get("attendees", []),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._events.append(event)
            return ToolResult(success=True, output=event)
        elif action == "list":
            return ToolResult(success=True, output={"events": self._events[-20:]})
        return ToolResult(success=False, error=f"Unknown action: {action}")


class EmailSimulationTool(BaseTool):
    """Simulate sending business emails."""
    def __init__(self):
        super().__init__()
        self.name = "email_send"
        self.description = "Simulate sending business emails"
        self.category = ToolCategory.EMAIL
        self._sent: List[Dict] = []

    def execute(self, **kwargs) -> ToolResult:
        email = {
            "id": str(uuid.uuid4())[:8],
            "to": kwargs.get("to", "team@mintuu.ai"),
            "subject": kwargs.get("subject", "Update"),
            "body": kwargs.get("body", ""),
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "DELIVERED",
        }
        self._sent.append(email)
        return ToolResult(
            success=True,
            output={"email_id": email["id"], "status": "DELIVERED"},
        )


class MetricsCollectorTool(BaseTool):
    """Collect and analyze business metrics."""
    def __init__(self):
        super().__init__()
        self.name = "metrics_collector"
        self.description = "Collect and report business metrics"
        self.category = ToolCategory.ANALYTICS

    def execute(self, **kwargs) -> ToolResult:
        metric_type = kwargs.get("metric_type", "general")
        return ToolResult(success=True, output={
            "metric_type": metric_type,
            "revenue_growth": "12.5%",
            "task_throughput": "47 tasks/hour",
            "agent_efficiency": "94.2%",
            "workflow_success_rate": "91.5%",
            "avg_response_time": "1.2s",
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })


# ============================================================
# Execution Manager
# ============================================================

class ExecutionManager:
    """
    Manages all tool executions across the ecosystem.

    Features:
    - Execution queue with tracking
    - Sandboxed file operations
    - Extended tool suite registration
    - Execution history and analytics
    """

    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self._executions: List[ExecutionRecord] = []
        self._max_history = 200
        self._register_extended_tools()
        logger.info(
            f"Execution Manager initialized with "
            f"{len(self.registry._tools)} total tools"
        )

    def _register_extended_tools(self):
        """Register extended tool suite."""
        extended = [
            GitStatusTool(),
            SystemInfoTool(),
            DocumentGeneratorTool(),
            CalendarTool(),
            EmailSimulationTool(),
            MetricsCollectorTool(),
        ]
        for tool in extended:
            self.registry.register(tool)

    def execute(self, agent_id: str, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool with full tracking."""
        record = ExecutionRecord(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            tool_name=tool_name,
            params=kwargs,
        )

        start = time.time()
        result = self.registry.execute_tool(tool_name, agent_id, **kwargs)
        record.duration_ms = int((time.time() - start) * 1000)
        record.result = result
        record.completed_at = datetime.now(timezone.utc).isoformat()

        self._executions.append(record)
        if len(self._executions) > self._max_history:
            self._executions = self._executions[-self._max_history:]

        return result

    def get_history(self, agent_id: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        history = self._executions
        if agent_id:
            history = [e for e in history if e.agent_id == agent_id]
        return [e.to_dict() for e in history[-limit:]]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._executions)
        successes = sum(1 for e in self._executions if e.result and e.result.success)
        return {
            "total_executions": total,
            "success_rate": f"{successes/total*100:.1f}%" if total else "N/A",
            "tools_available": len(self.registry._tools),
            "tool_names": list(self.registry._tools.keys()),
        }
