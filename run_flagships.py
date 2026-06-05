import asyncio
import time
import logging
from mintuu_ai_ecosystem.core.orchestration.orchestration_manager import OrchestrationManager
from mintuu_ai_ecosystem.core.workflows.flagship_workflows import (
    get_github_pipeline_steps,
    get_product_launch_steps,
    get_incident_response_steps
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flagships")

def run_all():
    orch = OrchestrationManager()
    
    # Workflow 1
    logger.info("=== STARTING WORKFLOW 1: GitHub Autonomous Pipeline ===")
    gh_steps = get_github_pipeline_steps(
        issue_title="High Memory Usage in Analytics Engine",
        issue_body="The analytics engine is consuming 90% of available RAM during the nightly sync. Suspect memory leak in the data parser."
    )
    orch.execute_workflow(
        name="GitHub Incident: High Memory Usage",
        description="Autonomous response to GitHub Issue #42",
        steps=gh_steps
    )
    
    # Workflow 2
    logger.info("=== STARTING WORKFLOW 2: Product Launch Pipeline ===")
    launch_steps = get_product_launch_steps(
        goal="Launch Mintuu Pro by Q3 with 500 signups"
    )
    orch.execute_workflow(
        name="Product Launch: Mintuu Pro",
        description="Launch Mintuu Pro by Q3 with 500 signups",
        steps=launch_steps
    )
    
    # Workflow 3
    logger.info("=== STARTING WORKFLOW 3: Incident Response System ===")
    ir_steps = get_incident_response_steps(
        anomaly="CPU spikes on database cluster 3, suspected unauthorized query pattern."
    )
    orch.execute_workflow(
        name="Incident Response: DB Cluster 3",
        description="System Anomaly Detected: CPU spikes on database cluster 3",
        steps=ir_steps
    )
    
    # Workflow 4 (Report)
    logger.info("=== STARTING FINAL REPORT GENERATION ===")
    report_steps = [
        {
            "agent_type": "Research",
            "title": "Compile Workflow Data",
            "description": "Gather execution metrics, total time, tokens used, and agent handoffs from the recent flagship workflows.",
        },
        {
            "agent_type": "Marketing",
            "title": "Draft Report Content",
            "description": "Write a step-by-step walkthrough of the workflows in plain human language with no jargon, including actual LLM reasoning quotes.",
            "depends_on": [0]
        },
        {
            "agent_type": "Operations",
            "title": "Generate Final Artifacts",
            "description": "Format the gathered content and output the final report as HTML and PDF files using the file_write and terminal_execute tools.",
            "depends_on": [1]
        }
    ]
    orch.execute_workflow(
        name="Generate Flagship Report",
        description="Generate final HTML and PDF report of the execution",
        steps=report_steps
    )

if __name__ == "__main__":
    run_all()
