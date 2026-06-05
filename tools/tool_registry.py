"""
Mintuu AI Ecosystem - Tool Registry & Execution Layer
======================================================
Pluggable tool architecture with registration, permission handling,
execution logging, and async support.
"""

import time
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger("mintuu.tools")


class ToolCategory(Enum):
    FILE = "FILE"
    TERMINAL = "TERMINAL"
    BROWSER = "BROWSER"
    EMAIL = "EMAIL"
    CALENDAR = "CALENDAR"
    GITHUB = "GITHUB"
    NOTION = "NOTION"
    SLACK = "SLACK"
    ANALYTICS = "ANALYTICS"
    DATABASE = "DATABASE"
    AI = "AI"
    UTILITY = "UTILITY"


class ToolPermission(Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    ADMIN = "ADMIN"


@dataclass
class ToolResult:
    """Standardized tool execution result."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class BaseTool(ABC):
    """
    Abstract base class for all ecosystem tools.
    Every tool must implement execute() and provide metadata.
    """

    def __init__(self):
        self.name: str = self.__class__.__name__
        self.description: str = ""
        self.category: ToolCategory = ToolCategory.UTILITY
        self.required_permissions: List[ToolPermission] = [ToolPermission.EXECUTE]
        self.parameters_schema: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def validate_params(self, **kwargs) -> bool:
        """Validate input parameters against schema."""
        for param, spec in self.parameters_schema.items():
            if spec.get("required", False) and param not in kwargs:
                return False
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "required_permissions": [p.value for p in self.required_permissions],
            "parameters": self.parameters_schema,
        }


# ============================================================
# Built-in Tools
# ============================================================

class FileReadTool(BaseTool):
    """Read contents of a file."""

    def __init__(self):
        super().__init__()
        self.name = "file_read"
        self.description = "Read the contents of a file from the filesystem"
        self.category = ToolCategory.FILE
        self.required_permissions = [ToolPermission.READ]
        self.parameters_schema = {
            "path": {"type": "string", "required": True, "description": "File path to read"},
        }

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", "")
        try:
            with open(path, "r") as f:
                content = f.read()
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileWriteTool(BaseTool):
    """Write contents to a file."""

    def __init__(self):
        super().__init__()
        self.name = "file_write"
        self.description = "Write content to a file on the filesystem"
        self.category = ToolCategory.FILE
        self.required_permissions = [ToolPermission.WRITE]
        self.parameters_schema = {
            "path": {"type": "string", "required": True, "description": "File path to write"},
            "content": {"type": "string", "required": True, "description": "Content to write"},
        }

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        try:
            from pathlib import Path
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return ToolResult(success=True, output=f"Written to {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class TerminalTool(BaseTool):
    """Execute terminal commands."""

    def __init__(self):
        super().__init__()
        self.name = "terminal_execute"
        self.description = "Execute a shell command and return output"
        self.category = ToolCategory.TERMINAL
        self.required_permissions = [ToolPermission.EXECUTE]
        self.parameters_schema = {
            "command": {"type": "string", "required": True, "description": "Shell command to execute"},
            "timeout": {"type": "integer", "required": False, "description": "Timeout in seconds"},
        }

    def execute(self, **kwargs) -> ToolResult:
        import subprocess
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", 30)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DataAnalysisTool(BaseTool):
    """Analyze structured data and produce summaries."""

    def __init__(self):
        super().__init__()
        self.name = "data_analysis"
        self.description = "Analyze structured data and return insights"
        self.category = ToolCategory.ANALYTICS
        self.parameters_schema = {
            "data": {"type": "object", "required": True, "description": "Data to analyze"},
            "analysis_type": {"type": "string", "required": False, "description": "Type of analysis"},
        }

    def execute(self, **kwargs) -> ToolResult:
        data = kwargs.get("data", {})
        analysis_type = kwargs.get("analysis_type", "summary")
        try:
            if isinstance(data, dict):
                summary = {
                    "keys": list(data.keys()),
                    "total_fields": len(data),
                    "analysis_type": analysis_type,
                }
            elif isinstance(data, list):
                summary = {
                    "total_items": len(data),
                    "analysis_type": analysis_type,
                }
            else:
                summary = {"data_type": type(data).__name__}
            return ToolResult(success=True, output=summary)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ReportGeneratorTool(BaseTool):
    """Generate formatted reports from structured data."""

    def __init__(self):
        super().__init__()
        self.name = "report_generator"
        self.description = "Generate formatted business reports"
        self.category = ToolCategory.UTILITY
        self.parameters_schema = {
            "title": {"type": "string", "required": True},
            "sections": {"type": "array", "required": True},
            "format": {"type": "string", "required": False},
        }

    def execute(self, **kwargs) -> ToolResult:
        title = kwargs.get("title", "Report")
        sections = kwargs.get("sections", [])
        fmt = kwargs.get("format", "markdown")
        try:
            lines = [f"# {title}", f"Generated: {datetime.now(timezone.utc).isoformat()}", ""]
            for section in sections:
                if isinstance(section, dict):
                    lines.append(f"## {section.get('heading', 'Section')}")
                    lines.append(section.get('content', ''))
                    lines.append("")
                else:
                    lines.append(str(section))
                    lines.append("")
            report = "\n".join(lines)
            return ToolResult(success=True, output=report)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


# ============================================================
# Tool Registry
# ============================================================

class ToolRegistry:
    """
    Central registry for all ecosystem tools.

    Features:
    - Tool registration and discovery
    - Permission-based access control
    - Execution logging
    - Usage statistics
    """

    def __init__(self, db=None):
        self._tools: Dict[str, BaseTool] = {}
        self._agent_permissions: Dict[str, List[ToolPermission]] = {}
        self._execution_log: List[Dict[str, Any]] = []
        self._db = db
        self._register_builtin_tools()
        logger.info(f"Tool Registry initialized with {len(self._tools)} tools")

    def _register_builtin_tools(self):
        """Register built-in ecosystem tools."""
        builtins = [
            FileReadTool(),
            FileWriteTool(),
            TerminalTool(),
            DataAnalysisTool(),
            ReportGeneratorTool(),
        ]
        for tool in builtins:
            self.register(tool)

    def register(self, tool: BaseTool):
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name} [{tool.category.value}]")

    def unregister(self, tool_name: str):
        """Remove a tool from the registry."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Tool unregistered: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """List all registered tools, optionally filtered by category."""
        tools = self._tools.values()
        if category:
            tools = [t for t in tools if t.category == category]
        return [t.get_info() for t in tools]

    def grant_permission(self, agent_id: str, permissions: List[ToolPermission]):
        """Grant tool permissions to an agent."""
        self._agent_permissions[agent_id] = permissions

    def check_permission(self, agent_id: str, tool: BaseTool) -> bool:
        """Check if an agent has permission to use a tool."""
        agent_perms = self._agent_permissions.get(agent_id, [ToolPermission.EXECUTE])
        return all(perm in agent_perms for perm in tool.required_permissions)

    def execute_tool(self, tool_name: str, agent_id: str, **kwargs) -> ToolResult:
        """
        Execute a tool with permission checking and logging.
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool not found: {tool_name}")

        # Permission check
        if not self.check_permission(agent_id, tool):
            return ToolResult(
                success=False,
                error=f"Agent {agent_id} lacks permission for {tool_name}"
            )

        # Parameter validation
        if not tool.validate_params(**kwargs):
            return ToolResult(success=False, error="Invalid parameters")

        # Execute with timing
        start_time = time.time()
        try:
            result = tool.execute(**kwargs)
            result.duration_ms = int((time.time() - start_time) * 1000)
        except Exception as e:
            result = ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        # Log execution
        log_entry = {
            "id": str(uuid.uuid4()),
            "tool_name": tool_name,
            "agent_id": agent_id,
            "params": {k: str(v)[:200] for k, v in kwargs.items()},
            "success": result.success,
            "duration_ms": result.duration_ms,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._execution_log.append(log_entry)

        # Persist to database if available
        if self._db:
            self._db.log_tool_execution(
                agent_id=agent_id,
                tool_name=tool_name,
                input_params=kwargs,
                output_data=str(result.output)[:500] if result.output else "",
                status="SUCCESS" if result.success else "FAILED",
                duration_ms=result.duration_ms,
                error=result.error,
            )

        if result.success:
            logger.debug(f"Tool executed: {tool_name} by {agent_id} ({result.duration_ms}ms)")
        else:
            logger.warning(f"Tool failed: {tool_name} by {agent_id}: {result.error}")

        return result

    def get_execution_history(self, agent_id: Optional[str] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get tool execution history."""
        history = self._execution_log
        if agent_id:
            history = [e for e in history if e["agent_id"] == agent_id]
        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get tool registry statistics."""
        return {
            "total_tools": len(self._tools),
            "categories": list(set(t.category.value for t in self._tools.values())),
            "total_executions": len(self._execution_log),
            "tools": list(self._tools.keys()),
        }
