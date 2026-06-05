"""
Mintuu AI Ecosystem - Inter-Agent Communication System
=======================================================
Message bus and communication protocol for agent-to-agent
and agent-to-orchestrator communication.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger("mintuu.communication")


class MessageType(Enum):
    """Types of inter-agent messages."""
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESPONSE = "TASK_RESPONSE"
    STATUS_UPDATE = "STATUS_UPDATE"
    DATA_SHARE = "DATA_SHARE"
    QUERY = "QUERY"
    QUERY_RESPONSE = "QUERY_RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    APPROVAL_RESPONSE = "APPROVAL_RESPONSE"
    BROADCAST = "BROADCAST"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Message:
    """Structured inter-agent message."""
    id: str
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    reply_to: Optional[str] = None
    workflow_id: Optional[str] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "reply_to": self.reply_to,
            "workflow_id": self.workflow_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            id=data["id"],
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            priority=MessagePriority(data.get("priority", 5)),
            reply_to=data.get("reply_to"),
            workflow_id=data.get("workflow_id"),
            timestamp=data.get("timestamp", ""),
            metadata=data.get("metadata", {}),
        )


class MessageBus:
    """
    Central message bus for inter-agent communication.

    Features:
    - Point-to-point messaging
    - Broadcast messaging
    - Topic-based subscriptions
    - Message history
    - Priority-based delivery
    """

    def __init__(self):
        self._mailboxes: Dict[str, List[Message]] = defaultdict(list)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._broadcast_subscribers: List[Callable] = []
        self._message_history: List[Message] = []
        self._max_history = 1000
        logger.info("Message Bus initialized")

    def send(self, sender: str, receiver: str, message_type: MessageType,
             content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
             reply_to: Optional[str] = None,
             workflow_id: Optional[str] = None) -> str:
        """Send a message from one agent to another."""
        message = Message(
            id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority,
            reply_to=reply_to,
            workflow_id=workflow_id,
        )

        # Deliver to mailbox
        self._mailboxes[receiver].append(message)
        # Sort by priority (highest first)
        self._mailboxes[receiver].sort(key=lambda m: m.priority.value, reverse=True)

        # Notify subscribers
        for callback in self._subscribers.get(receiver, []):
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Subscriber callback error: {e}")

        # Store in history
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]

        logger.debug(f"Message sent: {sender} → {receiver} [{message_type.value}]")
        return message.id

    def broadcast(self, sender: str, message_type: MessageType,
                  content: Dict[str, Any], exclude: Optional[List[str]] = None) -> str:
        """Broadcast a message to all registered agents."""
        message = Message(
            id=str(uuid.uuid4()),
            sender=sender,
            receiver="*",
            message_type=message_type,
            content=content,
        )

        exclude = exclude or []
        for agent_id in list(self._mailboxes.keys()):
            if agent_id not in exclude and agent_id != sender:
                self._mailboxes[agent_id].append(message)

        for callback in self._broadcast_subscribers:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Broadcast subscriber error: {e}")

        self._message_history.append(message)
        logger.info(f"Broadcast from {sender}: {message_type.value}")
        return message.id

    def receive(self, agent_id: str, limit: int = 10) -> List[Message]:
        """Receive pending messages for an agent (non-destructive peek)."""
        return self._mailboxes.get(agent_id, [])[:limit]

    def consume(self, agent_id: str, limit: int = 10) -> List[Message]:
        """Consume (remove) pending messages for an agent."""
        mailbox = self._mailboxes.get(agent_id, [])
        consumed = mailbox[:limit]
        self._mailboxes[agent_id] = mailbox[limit:]
        return consumed

    def consume_one(self, agent_id: str) -> Optional[Message]:
        """Consume the highest priority message."""
        mailbox = self._mailboxes.get(agent_id, [])
        if mailbox:
            return mailbox.pop(0)
        return None

    def reply(self, original_message: Message, sender: str,
              content: Dict[str, Any], message_type: Optional[MessageType] = None) -> str:
        """Reply to a message."""
        reply_type = message_type or MessageType.TASK_RESPONSE
        return self.send(
            sender=sender,
            receiver=original_message.sender,
            message_type=reply_type,
            content=content,
            reply_to=original_message.id,
            workflow_id=original_message.workflow_id,
        )

    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe to messages for a specific agent."""
        self._subscribers[agent_id].append(callback)
        # Ensure mailbox exists
        if agent_id not in self._mailboxes:
            self._mailboxes[agent_id] = []

    def subscribe_broadcast(self, callback: Callable):
        """Subscribe to broadcast messages."""
        self._broadcast_subscribers.append(callback)

    def get_pending_count(self, agent_id: str) -> int:
        """Get count of pending messages for an agent."""
        return len(self._mailboxes.get(agent_id, []))

    def get_history(self, agent_id: Optional[str] = None,
                    message_type: Optional[MessageType] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get message history with optional filters."""
        history = self._message_history
        if agent_id:
            history = [
                m for m in history
                if m.sender == agent_id or m.receiver == agent_id
            ]
        if message_type:
            history = [m for m in history if m.message_type == message_type]
        return [m.to_dict() for m in history[-limit:]]

    def clear_mailbox(self, agent_id: str):
        """Clear all messages for an agent."""
        self._mailboxes[agent_id] = []

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        total_pending = sum(len(mb) for mb in self._mailboxes.values())
        return {
            "registered_agents": len(self._mailboxes),
            "total_pending_messages": total_pending,
            "message_history_size": len(self._message_history),
            "mailbox_sizes": {
                aid: len(msgs) for aid, msgs in self._mailboxes.items() if msgs
            },
        }
