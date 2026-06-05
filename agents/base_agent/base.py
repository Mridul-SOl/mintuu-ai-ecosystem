"""
Mintuu AI Ecosystem - Base Agent
=================================
Abstract base class for all specialized AI agents in the ecosystem.
Provides a standardized interface for planning, execution, communication,
tool usage, memory management, and logging.
"""

import time
import json
import logging
import uuid
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from mintuu_ai_ecosystem.core.memory.memory_manager import MemoryManager
from mintuu_ai_ecosystem.core.state.state_manager import StateManager, AgentStatus
from mintuu_ai_ecosystem.core.communication.message_bus import (
    MessageBus, MessageType, MessagePriority
)
from mintuu_ai_ecosystem.tools.tool_registry import ToolRegistry, ToolResult
from mintuu_ai_ecosystem.database.models import DatabaseManager, EventType

logger = logging.getLogger("mintuu.agent")


class BaseAgent(ABC):
    """
    Abstract base class for all Mintuu AI Ecosystem agents.

    Every agent inherits this class and implements domain-specific logic
    while getting standardized support for:
    - Planning & execution lifecycle
    - Inter-agent communication
    - Tool invocation
    - Memory read/write
    - Logging & monitoring
    - Workflow participation

    Subclasses MUST implement:
    - plan()       → Create execution plan from task description
    - execute()    → Execute a task and return results
    - summarize()  → Generate a summary of completed work
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        description: str,
        db: DatabaseManager,
        memory: MemoryManager,
        state: StateManager,
        message_bus: MessageBus,
        tool_registry: ToolRegistry,
        capabilities: Optional[List[str]] = None,
        llm: Optional[Any] = None,
        reasoning: Optional[Any] = None,
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description

        # Core system references
        self.db = db
        self.memory = memory
        self.state = state
        self.message_bus = message_bus
        self.tool_registry = tool_registry
        
        # LLM Reasoning
        self.llm = llm
        self.reasoning = reasoning

        # Agent metadata
        self.capabilities = capabilities or []
        self.is_active = False
        self._task_history: List[Dict[str, Any]] = []

        # Register with state manager and message bus
        self.state.register_agent(self.agent_id, self.agent_type)
        self.message_bus.subscribe(self.agent_id, self._on_message)

        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")

    # ============================================================
    # Core Lifecycle Methods (must be implemented by subclasses)
    # ============================================================

    @abstractmethod
    def plan(self, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create an execution plan for a given task.

        Args:
            task_description: Natural language description of the task
            context: Optional context from orchestrator/memory

        Returns:
            Dict containing execution plan with steps, tools needed, etc.
        """
        pass

    @abstractmethod
    def execute(self, task: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a task according to a plan.

        Args:
            task: Task definition with title, description, parameters
            context: Execution context from memory/orchestrator

        Returns:
            Dict containing execution results
        """
        pass

    @abstractmethod
    def summarize(self, results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of task results.

        Args:
            results: Task execution results

        Returns:
            Formatted summary string
        """
        pass

    # ============================================================
    # Communication Methods
    # ============================================================

    def communicate(self, receiver: str, message_type: MessageType,
                    content: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.NORMAL,
                    workflow_id: Optional[str] = None) -> str:
        """Send a message to another agent."""
        msg_id = self.message_bus.send(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority,
            workflow_id=workflow_id,
        )
        logger.debug(f"{self.name} → {receiver}: {message_type.value}")
        return msg_id

    def broadcast(self, message_type: MessageType, content: Dict[str, Any]):
        """Broadcast a message to all other agents."""
        self.message_bus.broadcast(
            sender=self.agent_id,
            message_type=message_type,
            content=content,
        )

    def check_messages(self, limit: int = 10):
        """Check for incoming messages."""
        return self.message_bus.consume(self.agent_id, limit)

    def _on_message(self, message):
        """Default message handler (can be overridden)."""
        logger.debug(f"{self.name} received message: {message.message_type.value} from {message.sender}")

    # ============================================================
    # Tool Usage Methods
    # ============================================================

    def use_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Use a registered tool."""
        self.state.update_agent_status(self.agent_id, AgentStatus.EXECUTING)
        result = self.tool_registry.execute_tool(tool_name, self.agent_id, **kwargs)

        if result.success:
            logger.debug(f"{self.name} used tool '{tool_name}' successfully")
        else:
            logger.warning(f"{self.name} tool '{tool_name}' failed: {result.error}")

        return result

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List tools available to this agent."""
        return self.tool_registry.list_tools()

    # ============================================================
    # Memory Methods
    # ============================================================

    def save_memory(self, key: str, content: str, memory_type: str = "long_term",
                    metadata: Optional[Dict] = None):
        """Save information to the agent's memory."""
        if memory_type == "short_term":
            self.memory.store_short_term(self.agent_id, key, content, metadata)
        elif memory_type == "long_term":
            self.memory.store_long_term(self.agent_id, key, content, metadata)
        elif memory_type == "organizational":
            self.memory.store_organizational(key, content, self.agent_id, metadata)
        logger.debug(f"{self.name} saved {memory_type} memory: {key}")

    def recall(self, key: Optional[str] = None, memory_type: str = "long_term",
               limit: int = 10) -> List[Dict]:
        """Recall memories."""
        if memory_type == "short_term":
            return self.memory.recall_short_term(self.agent_id, key, limit)
        elif memory_type == "long_term":
            return self.memory.recall_long_term(self.agent_id, key, limit)
        elif memory_type == "organizational":
            return self.memory.recall_organizational(key, limit)
        return []

    def get_context(self, conversation_id: Optional[str] = None,
                    workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Build a full context package for this agent."""
        return self.memory.build_agent_context(
            self.agent_id, conversation_id, workflow_id
        )

    # ============================================================
    # Logging Methods
    # ============================================================

    def log_activity(self, action: str, input_data: str = "",
                     output_data: str = "", status: str = "SUCCESS",
                     duration_ms: int = 0):
        """Log agent activity to the database."""
        self.db.log_agent_activity(
            agent_id=self.agent_id,
            action=action,
            input_data=input_data,
            output_data=output_data,
            status=status,
            duration_ms=duration_ms,
        )

    def log_event(self, event_type: EventType, description: str,
                  metadata: Optional[Dict] = None):
        """Log a system event."""
        self.db.log_event(
            event_type=event_type,
            source=self.agent_id,
            description=description,
            metadata=metadata,
        )

    # ============================================================
    # Lifecycle Management
    # ============================================================

    def activate(self):
        """Activate the agent."""
        self.is_active = True
        self.state.update_agent_status(self.agent_id, AgentStatus.IDLE)
        self.log_event(EventType.AGENT_ACTIVATED, f"{self.name} activated")
        logger.info(f"Agent activated: {self.name}")

    def deactivate(self):
        """Deactivate the agent."""
        self.is_active = False
        self.state.update_agent_status(self.agent_id, AgentStatus.OFFLINE)
        self.log_event(EventType.AGENT_DEACTIVATED, f"{self.name} deactivated")
        logger.info(f"Agent deactivated: {self.name}")

    # ============================================================
    # Task Execution Wrapper (used by orchestrator)
    # ============================================================

    def handle_task(self, task: Dict[str, Any],
                    context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Full task handling pipeline:
        1. Update state to PLANNING
        2. Create execution plan
        3. Update state to EXECUTING
        4. Execute the plan
        5. Generate summary
        6. Log results
        7. Return to IDLE

        This is the primary entry point used by the orchestrator.
        """
        task_id = task.get("id", str(uuid.uuid4()))
        start_time = time.time()

        self.state.update_agent_status(
            self.agent_id, AgentStatus.PLANNING, task_id=task_id
        )

        try:
            # 1. Plan
            logger.info(f"{self.name} planning task: {task.get('title', 'Unknown')}")
            plan = self.plan(task.get("description", ""), context)

            # If reasoning engine is available, let's use it for the execution!
            if getattr(self, "reasoning", None):
                import asyncio
                import logging
                logging.getLogger("mintuu.agent").info(f"Using LLM Reasoning Engine for {self.agent_type}...")
                
                try:
                    # Import agent specific prompt dynamically
                    try:
                        sys_prompt_module = __import__(f"mintuu_ai_ecosystem.agents.{self.agent_type.lower()}_agent.system_prompt", fromlist=["SYSTEM_PROMPT"])
                        sys_prompt = getattr(sys_prompt_module, "SYSTEM_PROMPT", f"You are the {self.name}.")
                    except ModuleNotFoundError:
                        sys_prompt = f"You are the {self.name}. Your role is {self.description}. Please process the task based on your capabilities."
                        
                    # Run the LLM reasoning (synchronously using asyncio.run since we're in a thread)
                    pref = "llama3.1" if self.agent_type.lower() in ["ceo", "research", "operations"] else "mistral"
                    coro = self.reasoning.reason(
                        agent_id=self.agent_id,
                        task=task.get("description", ""),
                        context=context or {},
                        system_prompt=sys_prompt,
                        model_preference=pref
                    )
                    
                    try:
                        asyncio.get_running_loop()
                        # Event loop is running, run in a separate thread
                        import concurrent.futures
                        def run_coroutine(coro):
                            new_loop = asyncio.new_event_loop()
                            try:
                                return new_loop.run_until_complete(coro)
                            finally:
                                new_loop.close()
                                
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            future = pool.submit(run_coroutine, coro)
                            llm_result = future.result()
                    except RuntimeError:
                        # No event loop running
                        llm_result = asyncio.run(coro)
                    
                    # Merge LLM output into results
                    results = self.execute(task, context)
                    results["llm_reasoning"] = llm_result
                    results["outputs"]["llm_decision"] = llm_result.get("final_decision", "")
                    if "recommendation" in results["outputs"]:
                        results["outputs"]["recommendation"] = llm_result.get("final_decision", results["outputs"]["recommendation"])
                except Exception as e:
                    logging.getLogger("mintuu.agent").error(f"LLM reasoning failed, falling back to dummy execute: {e}")
                    results = self.execute(task, context)
            else:
                # 2. Execute natively
                self.state.update_agent_status(self.agent_id, AgentStatus.EXECUTING)
                logger.info(f"{self.name} executing task: {task.get('title', 'Unknown')}")
                results = self.execute(task, context)

            # 3. Summarize
            summary = self.summarize(results)
            thought_process = ""
            if getattr(self, "reasoning", None) and results.get("llm_reasoning"):
                thought_process = results['llm_reasoning'].get('thought_process', '')
                summary += f"\n\n**🤖 LLM Thought Process:**\n{thought_process}"
                
            # Broadcast reasoning for dashboard
            if thought_process:
                self.message_bus.broadcast(
                    sender=self.agent_id,
                    message_type=MessageType.STATUS_UPDATE,
                    content={
                        "event": "reasoning_trace",
                        "agent": self.agent_type,
                        "thought_process": thought_process
                    }
                )

            # 4. Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # 5. Log
            self.log_activity(
                action=f"task:{task.get('title', 'Unknown')}",
                input_data=json.dumps(task)[:500],
                output_data=summary[:500],
                status="SUCCESS",
                duration_ms=duration_ms,
            )
            self.state.record_task_completion(self.agent_id, duration_ms, True)

            # 6. Store in memory
            self.save_memory(
                key=f"task_result:{task_id}",
                content=summary,
                memory_type="short_term",
                metadata={"task_id": task_id, "status": "completed"},
            )
            # Save to organizational vector memory so the memory test works
            self.save_memory(
                key=f"org_task:{task_id}",
                content=summary,
                memory_type="organizational",
                metadata={"task_id": task_id, "agent": self.agent_type, "workflow": True},
            )

            # 7. Record in history
            result_record = {
                "task_id": task_id,
                "task": task,
                "plan": plan,
                "results": results,
                "summary": summary,
                "duration_ms": duration_ms,
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._task_history.append(result_record)

            # 8. Return to idle
            self.state.update_agent_status(self.agent_id, AgentStatus.IDLE)

            return result_record

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"{self.name} task failed: {e}")

            self.log_activity(
                action=f"task:{task.get('title', 'Unknown')}",
                input_data=json.dumps(task)[:500],
                output_data="",
                status="FAILED",
                duration_ms=duration_ms,
            )
            self.state.record_task_completion(self.agent_id, duration_ms, False)
            self.state.update_agent_status(self.agent_id, AgentStatus.ERROR)

            return {
                "task_id": task_id,
                "status": "FAILED",
                "error": str(e),
                "duration_ms": duration_ms,
            }

    # ============================================================
    # Agent Info
    # ============================================================

    def get_info(self) -> Dict[str, Any]:
        """Get complete agent information."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "state": self.state.get_agent_state(self.agent_id),
            "tasks_completed": len([t for t in self._task_history if t["status"] == "SUCCESS"]),
            "tasks_failed": len([t for t in self._task_history if t["status"] == "FAILED"]),
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name})>"
