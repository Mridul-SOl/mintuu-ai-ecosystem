"""
Mintuu AI Ecosystem — Collaboration Engine
===========================================
Structured inter-agent collaboration with request/response patterns,
subtask delegation, context sharing, and dependency-aware coordination.

This is the brain that makes agents actually TALK to each other.
"""

import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from mintuu_ai_ecosystem.core.communication.message_bus import (
    MessageBus, MessageType, MessagePriority, Message,
)

logger = logging.getLogger("mintuu.collaboration")


class CollaborationType(Enum):
    """Types of inter-agent collaboration."""
    INFO_REQUEST = "INFO_REQUEST"        # Agent needs info from another
    SUBTASK_DELEGATION = "SUBTASK_DELEGATION"  # Agent delegates work
    APPROVAL_GATE = "APPROVAL_GATE"      # Needs approval to continue
    DATA_HANDOFF = "DATA_HANDOFF"        # Passing results downstream
    CONSULTATION = "CONSULTATION"         # Advisory request
    BROADCAST_UPDATE = "BROADCAST_UPDATE" # System-wide announcement


@dataclass
class CollaborationRequest:
    """A structured collaboration request between agents."""
    id: str
    collab_type: CollaborationType
    requester_agent: str           # agent_id of requester
    target_agent: str              # agent_id of target (or "broadcast")
    workflow_id: Optional[str]
    payload: Dict[str, Any]        # The actual request data
    context: Dict[str, Any] = field(default_factory=dict)
    response: Optional[Dict[str, Any]] = None
    status: str = "PENDING"        # PENDING → SENT → RECEIVED → COMPLETED / FAILED
    created_at: str = ""
    completed_at: Optional[str] = None
    priority: int = 5

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "collab_type": self.collab_type.value,
            "requester_agent": self.requester_agent,
            "target_agent": self.target_agent,
            "workflow_id": self.workflow_id,
            "payload": self.payload,
            "status": self.status,
            "response": self.response,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "priority": self.priority,
        }


@dataclass
class CollaborationThread:
    """A thread of related collaboration exchanges within a workflow."""
    workflow_id: str
    exchanges: List[CollaborationRequest] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def add_exchange(self, request: CollaborationRequest):
        self.exchanges.append(request)
        self.timeline.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": request.collab_type.value,
            "from": request.requester_agent,
            "to": request.target_agent,
            "status": request.status,
            "summary": request.payload.get("summary", "")[:100],
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "total_exchanges": len(self.exchanges),
            "timeline": self.timeline[-20:],  # Last 20
        }


class CollaborationEngine:
    """
    Manages structured inter-agent collaboration.

    Key patterns:
    1. Request → Response: Agent A asks Agent B for data
    2. Delegation: Agent A assigns subtask to Agent B
    3. Approval: Agent needs CEO/authority approval
    4. Handoff: Step N passes results to Step N+1
    5. Broadcast: Agent shares update with all
    """

    def __init__(self, message_bus: MessageBus):
        self.bus = message_bus
        self._active_requests: Dict[str, CollaborationRequest] = {}
        self._threads: Dict[str, CollaborationThread] = {}
        self._collab_history: List[CollaborationRequest] = []
        self._max_history = 500
        logger.info("Collaboration Engine initialized")

    # ─────────────────────────────────────────────
    # Request / Response Patterns
    # ─────────────────────────────────────────────

    def request_info(
        self,
        requester: str,
        target: str,
        question: str,
        context: Optional[Dict] = None,
        workflow_id: Optional[str] = None,
        priority: int = 5,
    ) -> CollaborationRequest:
        """Agent requests information from another agent."""
        req = CollaborationRequest(
            id=str(uuid.uuid4()),
            collab_type=CollaborationType.INFO_REQUEST,
            requester_agent=requester,
            target_agent=target,
            workflow_id=workflow_id,
            payload={"question": question, "summary": question[:80]},
            context=context or {},
            priority=priority,
        )
        return self._send_request(req)

    def delegate_subtask(
        self,
        delegator: str,
        target: str,
        task_description: str,
        task_data: Optional[Dict] = None,
        workflow_id: Optional[str] = None,
        priority: int = 7,
    ) -> CollaborationRequest:
        """Agent delegates a subtask to another agent."""
        req = CollaborationRequest(
            id=str(uuid.uuid4()),
            collab_type=CollaborationType.SUBTASK_DELEGATION,
            requester_agent=delegator,
            target_agent=target,
            workflow_id=workflow_id,
            payload={
                "task_description": task_description,
                "task_data": task_data or {},
                "summary": f"Subtask: {task_description[:60]}",
            },
            priority=priority,
        )
        return self._send_request(req)

    def request_approval(
        self,
        requester: str,
        approver: str,
        proposal: str,
        details: Optional[Dict] = None,
        workflow_id: Optional[str] = None,
    ) -> CollaborationRequest:
        """Request approval from an authority agent (typically CEO)."""
        req = CollaborationRequest(
            id=str(uuid.uuid4()),
            collab_type=CollaborationType.APPROVAL_GATE,
            requester_agent=requester,
            target_agent=approver,
            workflow_id=workflow_id,
            payload={
                "proposal": proposal,
                "details": details or {},
                "summary": f"Approval: {proposal[:60]}",
            },
            priority=9,  # High priority for approvals
        )
        return self._send_request(req)

    def handoff_data(
        self,
        sender: str,
        receiver: str,
        data: Dict[str, Any],
        workflow_id: Optional[str] = None,
        description: str = "",
    ) -> CollaborationRequest:
        """Hand off workflow data from one agent to the next."""
        req = CollaborationRequest(
            id=str(uuid.uuid4()),
            collab_type=CollaborationType.DATA_HANDOFF,
            requester_agent=sender,
            target_agent=receiver,
            workflow_id=workflow_id,
            payload={
                "data": data,
                "description": description,
                "summary": f"Handoff: {description[:60]}",
            },
            priority=6,
        )
        # Handoffs are auto-completed (fire and forget)
        req.status = "COMPLETED"
        req.completed_at = datetime.now(timezone.utc).isoformat()
        return self._send_request(req)

    def broadcast_update(
        self,
        sender: str,
        update: str,
        data: Optional[Dict] = None,
        workflow_id: Optional[str] = None,
    ) -> str:
        """Broadcast an update to all agents."""
        msg_id = self.bus.broadcast(
            sender=sender,
            message_type=MessageType.BROADCAST,
            content={
                "update": update,
                "data": data or {},
            },
        )
        logger.info(f"Broadcast from {sender}: {update[:60]}")
        return msg_id

    # ─────────────────────────────────────────────
    # Response Handling
    # ─────────────────────────────────────────────

    def respond_to_request(
        self,
        request_id: str,
        responder: str,
        response_data: Dict[str, Any],
        approved: bool = True,
    ) -> bool:
        """Respond to a collaboration request."""
        req = self._active_requests.get(request_id)
        if not req:
            logger.warning(f"Collaboration request not found: {request_id}")
            return False

        req.response = {
            "responder": responder,
            "data": response_data,
            "approved": approved,
            "responded_at": datetime.now(timezone.utc).isoformat(),
        }
        req.status = "COMPLETED" if approved else "REJECTED"
        req.completed_at = datetime.now(timezone.utc).isoformat()

        # Send reply through message bus
        reply_type = (
            MessageType.APPROVAL_RESPONSE
            if req.collab_type == CollaborationType.APPROVAL_GATE
            else MessageType.QUERY_RESPONSE
        )
        self.bus.send(
            sender=responder,
            receiver=req.requester_agent,
            message_type=reply_type,
            content={
                "request_id": request_id,
                "response": response_data,
                "approved": approved,
            },
            workflow_id=req.workflow_id,
        )

        # Track in thread
        if req.workflow_id and req.workflow_id in self._threads:
            self._threads[req.workflow_id].add_exchange(req)

        # Move to history
        self._collab_history.append(req)
        del self._active_requests[request_id]

        logger.info(
            f"Collaboration {request_id} responded by {responder}: "
            f"{'APPROVED' if approved else 'REJECTED'}"
        )
        return True

    # ─────────────────────────────────────────────
    # Auto-respond (for simulated agents)
    # ─────────────────────────────────────────────

    def auto_resolve(self, request_id: str, agent_handle_fn) -> Dict[str, Any]:
        """
        Auto-resolve a collaboration request by invoking the target agent.
        Used when agents don't have async polling.
        """
        req = self._active_requests.get(request_id)
        if not req:
            return {"error": "Request not found"}

        # Execute via agent's handle_task
        response_data = agent_handle_fn(req.payload, req.context)
        self.respond_to_request(
            request_id=request_id,
            responder=req.target_agent,
            response_data=response_data,
            approved=True,
        )
        return response_data

    # ─────────────────────────────────────────────
    # Internal
    # ─────────────────────────────────────────────

    def _send_request(self, req: CollaborationRequest) -> CollaborationRequest:
        """Send a collaboration request through the message bus."""
        # Track active request
        self._active_requests[req.id] = req
        req.status = "SENT"

        # Determine message type
        msg_type_map = {
            CollaborationType.INFO_REQUEST: MessageType.QUERY,
            CollaborationType.SUBTASK_DELEGATION: MessageType.TASK_REQUEST,
            CollaborationType.APPROVAL_GATE: MessageType.APPROVAL_REQUEST,
            CollaborationType.DATA_HANDOFF: MessageType.DATA_SHARE,
            CollaborationType.CONSULTATION: MessageType.QUERY,
        }
        msg_type = msg_type_map.get(req.collab_type, MessageType.DATA_SHARE)

        # Send through bus
        priority_map = {1: MessagePriority.LOW, 5: MessagePriority.NORMAL,
                        7: MessagePriority.HIGH, 9: MessagePriority.CRITICAL}
        closest_priority = min(priority_map.keys(), key=lambda k: abs(k - req.priority))

        self.bus.send(
            sender=req.requester_agent,
            receiver=req.target_agent,
            message_type=msg_type,
            content={
                "collaboration_id": req.id,
                "type": req.collab_type.value,
                **req.payload,
            },
            priority=priority_map[closest_priority],
            workflow_id=req.workflow_id,
        )

        # Track in workflow thread
        if req.workflow_id:
            if req.workflow_id not in self._threads:
                self._threads[req.workflow_id] = CollaborationThread(
                    workflow_id=req.workflow_id
                )
            self._threads[req.workflow_id].add_exchange(req)

        logger.info(
            f"Collaboration {req.collab_type.value}: "
            f"{req.requester_agent} → {req.target_agent}"
        )
        return req

    # ─────────────────────────────────────────────
    # Query / Analytics
    # ─────────────────────────────────────────────

    def get_active_requests(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._active_requests.values()]

    def get_thread(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        thread = self._threads.get(workflow_id)
        return thread.to_dict() if thread else None

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._collab_history[-limit:]]

    def get_stats(self) -> Dict[str, Any]:
        type_counts = defaultdict(int)
        for r in self._collab_history:
            type_counts[r.collab_type.value] += 1
        return {
            "active_requests": len(self._active_requests),
            "active_threads": len(self._threads),
            "total_collaborations": len(self._collab_history),
            "by_type": dict(type_counts),
        }
