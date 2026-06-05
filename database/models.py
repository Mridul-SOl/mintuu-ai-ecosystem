"""
Mintuu AI Ecosystem - Database Models & Schema
===============================================
SQLite-backed persistent storage with full schema definitions.
Abstraction layer allows future migration to PostgreSQL / Redis / Vector DBs.
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from enum import Enum

from mintuu_ai_ecosystem.config.settings import settings

logger = logging.getLogger("mintuu.database")


# ============================================================
# Enums for database field types
# ============================================================

class TaskStatus(Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class WorkflowStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class MemoryType(Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    WORKFLOW = "WORKFLOW"
    CONVERSATION = "CONVERSATION"
    AGENT_SPECIFIC = "AGENT_SPECIFIC"
    ORGANIZATIONAL = "ORGANIZATIONAL"


class EventType(Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    WORKFLOW_CREATED = "WORKFLOW_CREATED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    AGENT_ACTIVATED = "AGENT_ACTIVATED"
    AGENT_DEACTIVATED = "AGENT_DEACTIVATED"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    MEMORY_STORED = "MEMORY_STORED"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    ERROR = "ERROR"


# ============================================================
# Database Manager
# ============================================================

class DatabaseManager:
    """
    Centralized database manager with connection pooling and schema management.
    Uses SQLite with WAL mode for concurrent access support.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database.sqlite_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
        logger.info(f"Database initialized at: {self.db_path}")

    def _initialize_database(self):
        """Create all tables if they don't exist."""
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

            conn.executescript(SCHEMA_SQL)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Thread-safe connection context manager."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    # --------------------------------------------------------
    # Conversation Operations
    # --------------------------------------------------------

    def create_conversation(self, user_id: str = "default", metadata: Optional[Dict] = None) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO conversations (id, user_id, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (conversation_id, user_id, json.dumps(metadata or {}),
                 _now(), _now())
            )
            conn.commit()
        logger.info(f"Created conversation: {conversation_id}")
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None) -> str:
        """Add a message to a conversation."""
        message_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO messages (id, conversation_id, role, content, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (message_id, conversation_id, role, content,
                 json.dumps(metadata or {}), _now())
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (_now(), conversation_id)
            )
            conn.commit()
        return message_id

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve messages for a conversation."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT id, role, content, metadata, created_at
                   FROM messages WHERE conversation_id = ?
                   ORDER BY created_at ASC LIMIT ?""",
                (conversation_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]

    # --------------------------------------------------------
    # Task Operations
    # --------------------------------------------------------

    def create_task(self, title: str, description: str, assigned_agent: str,
                    workflow_id: Optional[str] = None, priority: int = 5,
                    dependencies: Optional[List[str]] = None,
                    metadata: Optional[Dict] = None) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO tasks
                   (id, title, description, status, assigned_agent, workflow_id,
                    priority, dependencies, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, title, description, TaskStatus.PENDING.value,
                 assigned_agent, workflow_id, priority,
                 json.dumps(dependencies or []),
                 json.dumps(metadata or {}), _now(), _now())
            )
            conn.commit()
        logger.info(f"Created task: {task_id} → {assigned_agent}")
        return task_id

    def update_task_status(self, task_id: str, status: TaskStatus,
                           result: Optional[str] = None,
                           error: Optional[str] = None):
        """Update task status with optional result/error."""
        with self.get_connection() as conn:
            fields = ["status = ?", "updated_at = ?"]
            values: list = [status.value, _now()]

            if result is not None:
                fields.append("result = ?")
                values.append(result)
            if error is not None:
                fields.append("error_message = ?")
                values.append(error)
            if status == TaskStatus.RUNNING:
                fields.append("started_at = ?")
                values.append(_now())
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                fields.append("completed_at = ?")
                values.append(_now())

            values.append(task_id)
            conn.execute(
                f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
                values
            )
            conn.commit()
        logger.info(f"Task {task_id} → {status.value}")

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a task by ID."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_tasks_by_workflow(self, workflow_id: str) -> List[Dict]:
        """Get all tasks for a workflow."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE workflow_id = ? ORDER BY priority DESC, created_at ASC",
                (workflow_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def get_pending_tasks(self, agent_id: Optional[str] = None) -> List[Dict]:
        """Get pending tasks, optionally filtered by agent."""
        with self.get_connection() as conn:
            if agent_id:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? AND assigned_agent = ? ORDER BY priority DESC",
                    (TaskStatus.PENDING.value, agent_id)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY priority DESC",
                    (TaskStatus.PENDING.value,)
                ).fetchall()
            return [dict(row) for row in rows]

    # --------------------------------------------------------
    # Workflow Operations
    # --------------------------------------------------------

    def create_workflow(self, name: str, description: str,
                        steps: List[Dict], initiated_by: str = "mintuu",
                        metadata: Optional[Dict] = None) -> str:
        """Create a new workflow and return its ID."""
        workflow_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO workflows
                   (id, name, description, status, steps, current_step,
                    initiated_by, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (workflow_id, name, description,
                 WorkflowStatus.PENDING.value,
                 json.dumps(steps), 0, initiated_by,
                 json.dumps(metadata or {}), _now(), _now())
            )
            conn.commit()
        logger.info(f"Created workflow: {workflow_id} ({name})")
        return workflow_id

    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus,
                               current_step: Optional[int] = None,
                               result: Optional[str] = None):
        """Update workflow status."""
        with self.get_connection() as conn:
            fields = ["status = ?", "updated_at = ?"]
            values: list = [status.value, _now()]

            if current_step is not None:
                fields.append("current_step = ?")
                values.append(current_step)
            if result is not None:
                fields.append("result = ?")
                values.append(result)
            if status == WorkflowStatus.RUNNING:
                fields.append("started_at = ?")
                values.append(_now())
            if status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
                fields.append("completed_at = ?")
                values.append(_now())

            values.append(workflow_id)
            conn.execute(
                f"UPDATE workflows SET {', '.join(fields)} WHERE id = ?",
                values
            )
            conn.commit()

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get a workflow by ID."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM workflows WHERE id = ?", (workflow_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_active_workflows(self) -> List[Dict]:
        """Get all active (non-terminal) workflows."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM workflows
                   WHERE status IN (?, ?, ?)
                   ORDER BY created_at DESC""",
                (WorkflowStatus.PENDING.value,
                 WorkflowStatus.RUNNING.value,
                 WorkflowStatus.WAITING_APPROVAL.value)
            ).fetchall()
            return [dict(row) for row in rows]

    # --------------------------------------------------------
    # Memory Operations
    # --------------------------------------------------------

    def store_memory(self, agent_id: str, memory_type: MemoryType,
                     key: str, content: str, metadata: Optional[Dict] = None,
                     ttl_hours: Optional[int] = None) -> str:
        """Store a memory entry."""
        memory_id = str(uuid.uuid4())
        expires_at = None
        if ttl_hours:
            from datetime import timedelta
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat()

        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO memories
                   (id, agent_id, memory_type, key, content, metadata,
                    created_at, updated_at, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (memory_id, agent_id, memory_type.value, key, content,
                 json.dumps(metadata or {}), _now(), _now(), expires_at)
            )
            conn.commit()
        return memory_id

    def recall_memory(self, agent_id: str, memory_type: Optional[MemoryType] = None,
                      key: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Retrieve memory entries for an agent."""
        with self.get_connection() as conn:
            query = "SELECT * FROM memories WHERE agent_id = ?"
            params: list = [agent_id]

            if memory_type:
                query += " AND memory_type = ?"
                params.append(memory_type.value)
            if key:
                query += " AND key LIKE ?"
                params.append(f"%{key}%")

            query += " AND (expires_at IS NULL OR expires_at > ?) ORDER BY created_at DESC LIMIT ?"
            params.extend([_now(), limit])

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_shared_memory(self, key: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Retrieve shared organizational memory."""
        with self.get_connection() as conn:
            query = "SELECT * FROM memories WHERE memory_type = ?"
            params: list = [MemoryType.ORGANIZATIONAL.value]
            if key:
                query += " AND key LIKE ?"
                params.append(f"%{key}%")
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    # --------------------------------------------------------
    # Event & Logging Operations
    # --------------------------------------------------------

    def log_event(self, event_type: EventType, source: str,
                  description: str, metadata: Optional[Dict] = None) -> str:
        """Log a system event."""
        event_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO events (id, event_type, source, description, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (event_id, event_type.value, source, description,
                 json.dumps(metadata or {}), _now())
            )
            conn.commit()
        return event_id

    def log_agent_activity(self, agent_id: str, action: str,
                           input_data: str = "", output_data: str = "",
                           status: str = "SUCCESS", duration_ms: int = 0,
                           metadata: Optional[Dict] = None) -> str:
        """Log agent activity."""
        log_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO agent_logs
                   (id, agent_id, action, input_data, output_data, status,
                    duration_ms, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (log_id, agent_id, action, input_data, output_data, status,
                 duration_ms, json.dumps(metadata or {}), _now())
            )
            conn.commit()
        return log_id

    def log_tool_execution(self, agent_id: str, tool_name: str,
                           input_params: Dict, output_data: str = "",
                           status: str = "SUCCESS", duration_ms: int = 0,
                           error: Optional[str] = None) -> str:
        """Log tool execution."""
        exec_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO tool_executions
                   (id, agent_id, tool_name, input_params, output_data,
                    status, duration_ms, error, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (exec_id, agent_id, tool_name, json.dumps(input_params),
                 output_data, status, duration_ms, error, _now())
            )
            conn.commit()
        return exec_id

    # --------------------------------------------------------
    # Analytics & Aggregation
    # --------------------------------------------------------

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        with self.get_connection() as conn:
            stats = {}

            # Task stats
            for status in TaskStatus:
                count = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status = ?",
                    (status.value,)
                ).fetchone()[0]
                stats[f"tasks_{status.value.lower()}"] = count

            # Workflow stats
            for status in WorkflowStatus:
                count = conn.execute(
                    "SELECT COUNT(*) FROM workflows WHERE status = ?",
                    (status.value,)
                ).fetchone()[0]
                stats[f"workflows_{status.value.lower()}"] = count

            # Recent events
            stats["recent_events"] = conn.execute(
                "SELECT COUNT(*) FROM events WHERE created_at > datetime('now', '-1 hour')"
            ).fetchone()[0]

            # Active agents
            stats["active_agents"] = conn.execute(
                """SELECT COUNT(DISTINCT agent_id) FROM agent_logs
                   WHERE created_at > datetime('now', '-5 minutes')"""
            ).fetchone()[0]

            # Total memories
            stats["total_memories"] = conn.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]

            return stats

    def get_recent_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict]:
        """Get recent system events."""
        with self.get_connection() as conn:
            if event_type:
                rows = conn.execute(
                    "SELECT * FROM events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?",
                    (event_type, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM events ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            return [dict(row) for row in rows]

    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent agent logs."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]


def _now() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# SQL Schema
# ============================================================

SCHEMA_SQL = """
-- Conversations table: stores user chat sessions
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default',
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Messages table: individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system', 'agent')),
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Tasks table: individual work units assigned to agents
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    assigned_agent TEXT NOT NULL,
    workflow_id TEXT,
    priority INTEGER DEFAULT 5,
    dependencies TEXT DEFAULT '[]',
    result TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE SET NULL
);

-- Workflows table: multi-step execution pipelines
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    steps TEXT NOT NULL DEFAULT '[]',
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    result TEXT,
    initiated_by TEXT DEFAULT 'mintuu',
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT
);

-- Workflow state snapshots for recovery
CREATE TABLE IF NOT EXISTS workflow_states (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    state_data TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Memories table: agent memory storage
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    key TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    importance REAL DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT
);

-- Agent activity logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT DEFAULT '',
    output_data TEXT DEFAULT '',
    status TEXT DEFAULT 'SUCCESS',
    duration_ms INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

-- System events
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    description TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

-- Tool execution records
CREATE TABLE IF NOT EXISTS tool_executions (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input_params TEXT DEFAULT '{}',
    output_data TEXT DEFAULT '',
    status TEXT DEFAULT 'SUCCESS',
    duration_ms INTEGER DEFAULT 0,
    error TEXT,
    created_at TEXT NOT NULL
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_created ON agent_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_tool_exec_agent ON tool_executions(agent_id);
"""
