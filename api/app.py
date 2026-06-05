"""
Mintuu AI Ecosystem — FastAPI Application v2
==============================================
Production-grade REST API with collaboration feeds,
autonomous controls, workflow management, and real-time dashboard.
"""
import logging
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from mintuu_ai_ecosystem.config.settings import settings
from mintuu_ai_ecosystem.core.orchestration.orchestration_manager import OrchestrationManager
from mintuu_ai_ecosystem.api.websocket import router as websocket_router, state_pusher_loop
from mintuu_ai_ecosystem.api.webhooks import router as webhook_router, set_orchestrator
from mintuu_ai_ecosystem.api.auth import UserManager
from mintuu_ai_ecosystem.api.auth_routes import router as auth_router, set_user_manager

# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format=settings.logging.format,
    datefmt=settings.logging.date_format,
)
logger = logging.getLogger("mintuu.api")

# ============================================================
# Global
# ============================================================

orchestrator: Optional[OrchestrationManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    logger.info("Starting Mintuu AI Ecosystem v2...")
    orchestrator = OrchestrationManager()
    
    # Inject orchestrator to webhooks
    set_orchestrator(orchestrator)
    
    # Initialize auth system
    user_mgr = UserManager(orchestrator.db)
    set_user_manager(user_mgr)
    logger.info("Auth system initialized.")
    
    # Start autonomous simulation
    # orchestrator.start_autonomous()
    
    # Start websocket pusher
    pusher_task = asyncio.create_task(state_pusher_loop(orchestrator))
    
    logger.info("Ecosystem v2 fully operational. Autonomous engine running.")
    yield
    logger.info("Shutting down...")
    pusher_task.cancel()
    orchestrator.stop_autonomous()

# ============================================================
# App
# ============================================================

app = FastAPI(
    title="Mintuu AI Ecosystem v2",
    description="AI-Powered Business Operating System — Autonomous Multi-Agent Orchestration",
    version=settings.version,
    docs_url="/docs", redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(websocket_router)
app.include_router(webhook_router)
app.include_router(auth_router)

# Static files
from pathlib import Path as _Path
import os
_pkg_dir = _Path(__file__).resolve().parent.parent
_static = str(_pkg_dir / "dashboard" / "static")
_templates = str(_pkg_dir / "dashboard" / "templates")
if os.path.exists(_static):
    app.mount("/static", StaticFiles(directory=_static), name="static")

# ============================================================
# Models
# ============================================================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to Mintuu")
    conversation_id: Optional[str] = Field(None)
    user_id: str = Field("default")

class TaskRequest(BaseModel):
    description: str = Field(...)
    agent_type: Optional[str] = Field(None)
    priority: int = Field(5, ge=1, le=10)

class WorkflowRequest(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    steps: List[Dict[str, Any]] = Field(...)

class AutoWorkflowRequest(BaseModel):
    description: str = Field(...)

class AutonomousTaskRequest(BaseModel):
    name: str = Field(...)
    agent_type: str = Field(...)
    description: str = Field(...)
    interval_seconds: int = Field(300)

# ============================================================
# Page Routes
# ============================================================

def _serve_template(name: str) -> HTMLResponse:
    """Serve an HTML template file."""
    tpl = os.path.join(_templates, name)
    if os.path.exists(tpl):
        with open(tpl, "r") as f:
            return HTMLResponse(f.read())
    return HTMLResponse(f"<h1>Mintuu AI</h1><p>Template '{name}' not found.</p>", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return _serve_template("landing.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return _serve_template("login.html")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return _serve_template("signup.html")

@app.get("/app", response_class=HTMLResponse)
async def app_dashboard(request: Request):
    return _serve_template("dashboard.html")

# ============================================================
# Chat (Mintuu Interface)
# ============================================================

@app.post("/api/v1/chat")
def chat(req: ChatRequest):
    if not orchestrator:
        raise HTTPException(503, "Not initialized")

    conv_id = req.conversation_id or orchestrator.db.create_conversation(req.user_id)
    orchestrator.memory.add_to_conversation(conv_id, "user", req.message)

    message = req.message.lower()
    workflow_keywords = [
        "launch", "full report", "company", "all departments",
        "comprehensive", "complete analysis", "across all", "new product",
    ]
    is_workflow = any(kw in message for kw in workflow_keywords)

    if is_workflow:
        result = orchestrator.execute_auto_workflow(req.message)
        response_text = _format_workflow_response(result)
    else:
        result = orchestrator.execute_task(req.message, conversation_id=conv_id)
        response_text = _format_task_response(result)

    orchestrator.memory.add_to_conversation(conv_id, "assistant", response_text)

    return {
        "conversation_id": conv_id,
        "response": response_text,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# ============================================================
# Tasks
# ============================================================

@app.post("/api/v1/execute")
def execute_task(req: TaskRequest):
    if not orchestrator: raise HTTPException(503)
    return orchestrator.execute_task(req.description, req.agent_type)

@app.get("/api/v1/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    if not orchestrator: raise HTTPException(503)
    with orchestrator.db.get_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

# ============================================================
# Workflows
# ============================================================

@app.post("/api/v1/workflows")
def create_workflow(req: WorkflowRequest):
    if not orchestrator: raise HTTPException(503)
    return orchestrator.execute_workflow(req.name, req.description, req.steps)

@app.post("/api/v1/workflows/auto")
def auto_workflow(req: AutoWorkflowRequest):
    if not orchestrator: raise HTTPException(503)
    return orchestrator.execute_auto_workflow(req.description)

@app.get("/api/v1/workflows")
async def list_workflows():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.workflow_engine.get_all_workflows()

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    if not orchestrator: raise HTTPException(503)
    wf = orchestrator.workflow_engine.get_workflow_status(workflow_id)
    if not wf: raise HTTPException(404)
    return wf

# ============================================================
# Agents
# ============================================================

@app.get("/api/v1/agents")
async def list_agents():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.get_agents()

@app.get("/api/v1/agents/{agent_type}")
async def get_agent(agent_type: str):
    if not orchestrator: raise HTTPException(503)
    info = orchestrator.get_agent_info(agent_type)
    if not info: raise HTTPException(404)
    return info

# ============================================================
# Collaboration Feed (NEW — Phase 1)
# ============================================================

@app.get("/api/v1/collaboration")
async def get_collaboration_feed(limit: int = 50):
    """Get inter-agent collaboration activity feed."""
    if not orchestrator: raise HTTPException(503)
    return orchestrator.get_collaboration_feed(limit)

@app.get("/api/v1/collaboration/messages")
async def get_message_history(limit: int = 100):
    """Get raw message bus history."""
    if not orchestrator: raise HTTPException(503)
    return orchestrator.message_bus.get_history(limit=limit)

# ============================================================
# Autonomous Operations (NEW — Phase 6)
# ============================================================

@app.get("/api/v1/autonomous")
async def get_autonomous_status():
    """Get autonomous engine status and tasks."""
    if not orchestrator: raise HTTPException(503)
    return orchestrator.autonomous.get_stats()

@app.get("/api/v1/autonomous/events")
async def get_autonomous_events(limit: int = 50):
    """Get autonomous execution event log."""
    if not orchestrator: raise HTTPException(503)
    return orchestrator.autonomous.get_event_log(limit)

@app.post("/api/v1/autonomous/tasks")
async def add_autonomous_task(req: AutonomousTaskRequest):
    """Register a new autonomous task."""
    if not orchestrator: raise HTTPException(503)
    task_id = orchestrator.autonomous.add_task(
        name=req.name, agent_type=req.agent_type,
        description=req.description, interval_seconds=req.interval_seconds,
    )
    return {"task_id": task_id, "status": "registered"}

@app.post("/api/v1/autonomous/{task_id}/trigger")
async def trigger_autonomous_task(task_id: str):
    """Manually trigger an autonomous task."""
    if not orchestrator: raise HTTPException(503)
    result = orchestrator.autonomous.trigger_now(task_id)
    if not result: raise HTTPException(404)
    return result

@app.post("/api/v1/autonomous/start")
async def start_autonomous():
    if not orchestrator: raise HTTPException(503)
    orchestrator.start_autonomous()
    return {"status": "started"}

@app.post("/api/v1/autonomous/stop")
async def stop_autonomous():
    if not orchestrator: raise HTTPException(503)
    orchestrator.stop_autonomous()
    return {"status": "stopped"}

# ============================================================
# System Status & Monitoring
# ============================================================

@app.get("/api/v1/status")
async def system_status():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.get_system_status()

@app.get("/api/v1/logs")
async def get_logs(limit: int = 100):
    if not orchestrator: raise HTTPException(503)
    return orchestrator.get_recent_logs(limit)

@app.get("/api/v1/events")
async def get_events(limit: int = 50):
    if not orchestrator: raise HTTPException(503)
    return orchestrator.get_recent_events(limit)

@app.get("/api/v1/tools")
async def list_tools():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.tool_registry.list_tools()

@app.get("/api/v1/memory")
async def get_memory_stats():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.memory.get_memory_stats()

@app.get("/api/v1/analytics")
async def get_analytics():
    if not orchestrator: raise HTTPException(503)
    return orchestrator.db.get_system_stats()

# ============================================================
# Helpers
# ============================================================

def _format_task_response(result: Dict[str, Any]) -> str:
    if result.get("status") == "ERROR":
        return f"❌ Error: {result.get('error', 'Unknown error')}"
    summary = result.get("summary", "")
    agent = result.get("agent_type", "Unknown")
    return f"✅ **{agent.upper()} Agent** completed the task.\n\n{summary}"

def _format_workflow_response(result: Dict[str, Any]) -> str:
    if result.get("status") == "ERROR":
        return f"❌ Workflow Error: {result.get('error', 'Unknown error')}"
    name = result.get("name", "Workflow")
    status = result.get("status", "UNKNOWN")
    steps = result.get("steps", [])
    collabs = result.get("collaboration_log", [])
    lines = [f"📋 **{name}** — {status}", ""]
    for s in steps:
        icon = "✅" if s["status"] == "COMPLETED" else "❌" if s["status"] == "FAILED" else "⏳"
        lines.append(f"  {icon} Step {s['index']+1}: {s['task_title']} ({s['agent_type']})")
    if collabs:
        lines.append("")
        lines.append(f"🤝 {len(collabs)} inter-agent collaborations")
    return "\n".join(lines)
