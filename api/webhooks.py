from fastapi import APIRouter, Request, HTTPException
import logging
from typing import Optional

from mintuu_ai_ecosystem.core.events.event_types import Event, EventType
from mintuu_ai_ecosystem.core.events.event_bus import EventBus
from mintuu_ai_ecosystem.core.workflows.flagship_workflows import get_github_pipeline_steps

logger = logging.getLogger("mintuu.api.webhooks")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# Assume event_bus is injected or a global singleton
# For demonstration, we import a mock or create one
# Global reference to orchestrator
orchestrator_ref = None
global_event_bus = EventBus()

def set_orchestrator(orch):
    global orchestrator_ref
    orchestrator_ref = orch

@router.post("/github")
async def github_webhook(request: Request):
    """Receive GitHub webhooks."""
    try:
        payload = await request.json()
        event_name = request.headers.get("X-GitHub-Event", "unknown")
        
        event_type = EventType.EXTERNAL_WEBHOOK
        if event_name == "push":
            event_type = EventType.GITHUB_PUSH
        elif event_name == "pull_request":
            event_type = EventType.GITHUB_PR
        elif event_name == "issues":
            event_type = EventType.GITHUB_PR # Reusing or create GITHUB_ISSUE
            
        event = Event(
            type=event_type,
            source="github_webhook",
            payload=payload
        )
        
        await global_event_bus.publish(event)
        
        # Flagship Workflow 1 Trigger
        if event_name == "issues" and payload.get("action") == "opened":
            issue = payload.get("issue", {})
            title = issue.get("title", "Unknown Issue")
            body = issue.get("body", "")
            if orchestrator_ref:
                steps = get_github_pipeline_steps(title, body)
                orchestrator_ref.execute_workflow(
                    name=f"GitHub Incident: {title}",
                    description=f"Autonomous response to GitHub Issue #{issue.get('number', 0)}",
                    steps=steps
                )
                logger.info(f"Triggered GitHub Autonomous Pipeline for issue: {title}")
                
        return {"status": "accepted", "event_id": event.id}
        
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
