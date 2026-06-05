from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from typing import List, Dict, Any
import json
import asyncio

logger = logging.getLogger("mintuu.api.websocket")
router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect much client->server over WS right now, mostly server push
            data = await websocket.receive_text()
            logger.debug(f"Received WS data: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
async def push_event_to_dashboard(event_type: str, payload: Dict[str, Any]):
    """Helper function to push events to all connected clients."""
    await manager.broadcast({
        "type": event_type,
        "data": payload
    })

# ── State Pusher loop ───────────────────────────────────────────
async def state_pusher_loop(orchestrator):
    """Background task to push state to clients instead of UI polling."""
    while True:
        if manager.active_connections and orchestrator:
            try:
                # Push status
                status = orchestrator.get_system_status()
                await push_event_to_dashboard("state_update", status)
                
                # Push collaboration
                collab = orchestrator.get_collaboration_feed(50)
                await push_event_to_dashboard("collaboration_update", collab)
                
                # Push autonomous
                auto = orchestrator.autonomous.get_stats()
                await push_event_to_dashboard("autonomous_update", auto)
            except Exception as e:
                logger.error(f"Error in state pusher: {e}")
        
        await asyncio.sleep(2)
