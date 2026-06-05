"""
Mintuu AI Ecosystem - Centralized Memory Architecture
=====================================================
Multi-tier memory system supporting short-term, long-term, workflow,
conversation, agent-specific, and shared organizational memory.
Future-ready for vector databases and semantic retrieval.
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from collections import OrderedDict

from mintuu_ai_ecosystem.database.models import (
    DatabaseManager, MemoryType
)
from mintuu_ai_ecosystem.config.settings import settings
from mintuu_ai_ecosystem.core.memory.vector_memory import VectorMemory

logger = logging.getLogger("mintuu.memory")


class MemoryStore:
    """
    In-memory LRU cache layer on top of persistent SQLite storage.
    Provides fast access patterns for frequently used memories.
    """

    def __init__(self, capacity: int = 500):
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._capacity = capacity

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: Dict[str, Any]):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)

    def invalidate(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


class MemoryManager:
    """
    Centralized memory manager for the Mintuu AI Ecosystem.
    Handles all memory operations across agents, workflows, and the system.

    Memory Tiers:
    1. Short-term: Recent context (auto-expires)
    2. Long-term: Persistent knowledge
    3. Workflow: Execution context for active workflows
    4. Conversation: Chat history and context
    5. Agent-specific: Individual agent knowledge bases
    6. Organizational: Shared company-wide knowledge
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._cache = MemoryStore(capacity=settings.memory.short_term_capacity)
        self._conversation_cache: Dict[str, List[Dict]] = {}
        self.vector_store = VectorMemory()
        logger.info("Memory Manager initialized")

    # --------------------------------------------------------
    # Short-Term Memory (auto-expires, high-frequency access)
    # --------------------------------------------------------

    def store_short_term(self, agent_id: str, key: str, content: str,
                         metadata: Optional[Dict] = None, ttl_hours: int = 1) -> str:
        """Store a short-term memory entry with automatic expiration."""
        memory_id = self.db.store_memory(
            agent_id=agent_id,
            memory_type=MemoryType.SHORT_TERM,
            key=key,
            content=content,
            metadata=metadata,
            ttl_hours=ttl_hours,
        )
        cache_key = f"st:{agent_id}:{key}"
        self._cache.put(cache_key, {
            "id": memory_id, "content": content,
            "metadata": metadata or {}, "agent_id": agent_id,
        })
        logger.debug(f"Short-term memory stored: {agent_id}/{key}")
        return memory_id

    def recall_short_term(self, agent_id: str, key: Optional[str] = None,
                          limit: int = 10) -> List[Dict]:
        """Recall short-term memories, checking cache first."""
        if key:
            cache_key = f"st:{agent_id}:{key}"
            cached = self._cache.get(cache_key)
            if cached:
                return [cached]
        return self.db.recall_memory(agent_id, MemoryType.SHORT_TERM, key, limit)

    # --------------------------------------------------------
    # Long-Term Memory (persistent, important information)
    # --------------------------------------------------------

    def store_long_term(self, agent_id: str, key: str, content: str,
                        metadata: Optional[Dict] = None) -> str:
        """Store a long-term memory entry (no expiration)."""
        memory_id = self.db.store_memory(
            agent_id=agent_id,
            memory_type=MemoryType.LONG_TERM,
            key=key,
            content=content,
            metadata=metadata,
        )
        logger.info(f"Long-term memory stored: {agent_id}/{key}")
        return memory_id

    def recall_long_term(self, agent_id: str, key: Optional[str] = None,
                         limit: int = 20) -> List[Dict]:
        """Recall long-term memories."""
        return self.db.recall_memory(agent_id, MemoryType.LONG_TERM, key, limit)

    # --------------------------------------------------------
    # Workflow Memory (execution context)
    # --------------------------------------------------------

    def store_workflow_memory(self, workflow_id: str, key: str, content: str,
                              metadata: Optional[Dict] = None) -> str:
        """Store workflow execution context."""
        return self.db.store_memory(
            agent_id=f"workflow:{workflow_id}",
            memory_type=MemoryType.WORKFLOW,
            key=key,
            content=content,
            metadata=metadata,
            ttl_hours=72,  # Workflow memories expire after 3 days
        )

    def recall_workflow_memory(self, workflow_id: str,
                               key: Optional[str] = None) -> List[Dict]:
        """Recall workflow execution context."""
        return self.db.recall_memory(
            f"workflow:{workflow_id}", MemoryType.WORKFLOW, key
        )

    # --------------------------------------------------------
    # Conversation Memory
    # --------------------------------------------------------

    def store_conversation_context(self, conversation_id: str,
                                   summary: str, metadata: Optional[Dict] = None) -> str:
        """Store a conversation context summary."""
        return self.db.store_memory(
            agent_id="mintuu",
            memory_type=MemoryType.CONVERSATION,
            key=f"conv:{conversation_id}",
            content=summary,
            metadata=metadata,
        )

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get full conversation message history."""
        if conversation_id in self._conversation_cache:
            return self._conversation_cache[conversation_id][-limit:]
        messages = self.db.get_conversation_messages(conversation_id, limit)
        self._conversation_cache[conversation_id] = messages
        return messages

    def add_to_conversation(self, conversation_id: str, role: str, content: str,
                            metadata: Optional[Dict] = None) -> str:
        """Add a message and update cache."""
        message_id = self.db.add_message(conversation_id, role, content, metadata)
        if conversation_id in self._conversation_cache:
            self._conversation_cache[conversation_id].append({
                "id": message_id, "role": role, "content": content,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        return message_id

    # --------------------------------------------------------
    # Shared Organizational Memory
    # --------------------------------------------------------

    def store_organizational(self, key: str, content: str,
                             source_agent: str = "system",
                             metadata: Optional[Dict] = None) -> str:
        """Store shared organizational knowledge accessible to all agents."""
        meta = metadata or {}
        meta["source_agent"] = source_agent
        memory_id = self.db.store_memory(
            agent_id="organization",
            memory_type=MemoryType.ORGANIZATIONAL,
            key=key,
            content=content,
            metadata=meta,
        )
        if self.vector_store:
            self.vector_store.store_memory("org_knowledge", content, meta, memory_id)
        return memory_id

    def recall_organizational(self, key: Optional[str] = None,
                              limit: int = 50) -> List[Dict]:
        """Recall shared organizational memories."""
        return self.db.get_shared_memory(key, limit)
        
    def query_vector_memory(self, query: str, limit: int = 3) -> List[Dict]:
        """Semantic search in organizational knowledge."""
        if not self.vector_store:
            return []
        return self.vector_store.search_memory("org_knowledge", query, limit)

    # --------------------------------------------------------
    # Agent Context Builder
    # --------------------------------------------------------

    def build_agent_context(self, agent_id: str, conversation_id: Optional[str] = None,
                            workflow_id: Optional[str] = None,
                            include_organizational: bool = True) -> Dict[str, Any]:
        """
        Build a comprehensive context package for an agent.
        Combines short-term, long-term, workflow, and organizational memories.
        """
        context: Dict[str, Any] = {
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "short_term": self.recall_short_term(agent_id, limit=10),
            "long_term": self.recall_long_term(agent_id, limit=5),
        }

        if conversation_id:
            context["conversation"] = self.get_conversation_history(
                conversation_id, limit=settings.memory.conversation_history_limit
            )

        if workflow_id:
            context["workflow"] = self.recall_workflow_memory(workflow_id)

        if include_organizational:
            context["organizational"] = self.recall_organizational(limit=10)

        logger.debug(f"Built context for agent {agent_id}: "
                     f"{sum(len(v) if isinstance(v, list) else 1 for v in context.values())} items")
        return context

    # --------------------------------------------------------
    # Memory Analytics
    # --------------------------------------------------------

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "cache_size": self._cache.size,
            "conversation_cache_size": len(self._conversation_cache),
            "cache_capacity": self._cache._capacity,
        }

    def cleanup_expired(self):
        """Cleanup expired memory entries (run periodically)."""
        logger.info("Running memory cleanup...")
        self._cache.clear()
        self._conversation_cache.clear()
