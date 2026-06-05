"""
Flagship Workflows Definitions for Mintuu AI Ecosystem
"""
from typing import Dict, Any, List

def get_github_pipeline_steps(issue_title: str, issue_body: str) -> List[Dict[str, Any]]:
    return [
        {
            "agent_type": "Research",
            "title": "Analyze Issue against Memory",
            "description": f"Query vector memory to find similar past issues for '{issue_title}'. Produce a report on past incidents and resolutions.",
        },
        {
            "agent_type": "Production",
            "title": "Impact Analysis",
            "description": f"Check affected files and recent commits related to: {issue_body}. Produce an impact report.",
            "depends_on": [0]
        },
        {
            "agent_type": "CEO",
            "title": "Severity Decision",
            "description": "Read Research and Production reports. Decide the severity of the issue with written reasoning. Decide if immediate action is needed.",
            "depends_on": [0, 1]
        },
        {
            "agent_type": "Operations",
            "title": "Concrete Response Plan",
            "description": "Build a concrete response plan based on CEO's severity decision.",
            "depends_on": [2]
        },
        {
            "agent_type": "Marketing",  # Re-purposed to handle external comms/dashboard updates
            "title": "Final Summary & Update",
            "description": "Write a final summary, define labels for the GitHub issue, and finalize the dashboard update.",
            "depends_on": [3]
        }
    ]

def get_product_launch_steps(goal: str) -> List[Dict[str, Any]]:
    return [
        {
            "agent_type": "CEO",
            "title": "Decompose Goal",
            "description": f"Decompose goal '{goal}' into phases, budget range, and success metrics.",
        },
        {
            "agent_type": "Research",
            "title": "Market Retrieval",
            "description": "Retrieve past market reports from vector memory and produce real numbers on competitors and pricing.",
            "depends_on": [0]
        },
        {
            "agent_type": "Marketing",
            "title": "Campaign Plan",
            "description": "Build a campaign plan using specific numbers from Research.",
            "depends_on": [1]
        },
        {
            "agent_type": "CEO",
            "title": "Plan Critique Loop",
            "description": f"Critique the marketing plan against the original goal metric ({goal}). Provide constructive feedback on the math.",
            "depends_on": [2]
        },
        {
            "agent_type": "Finance",
            "title": "Allocate Budget",
            "description": "Allocate budget with reasoning tied to the actual numbers Research produced and CEO's constraints.",
            "depends_on": [3]
        },
        {
            "agent_type": "Operations",
            "title": "Execution Checklist & KPIs",
            "description": "Produce a sequenced execution checklist. Set up real scheduled KPI checkpoints.",
            "depends_on": [4]
        }
    ]

def get_incident_response_steps(anomaly: str) -> List[Dict[str, Any]]:
    return [
        {
            "agent_type": "Infrastructure",
            "title": "Status Report",
            "description": f"Produce a factual status report on affected services and blast radius for anomaly: {anomaly}",
        },
        {
            "agent_type": "Security",
            "title": "Risk Assessment",
            "description": "Assess independently whether the anomaly carries exploit risk and produce a risk rating.",
            "depends_on": [0]
        },
        {
            "agent_type": "Operations",
            "title": "Severity Scoring",
            "description": "Combine both reports into a severity score using a defined formula. Decide if escalation is needed.",
            "depends_on": [0, 1]
        },
        {
            "agent_type": "CEO",
            "title": "Escalation Decision",
            "description": "Read the structured briefing and make an approval decision with conditions ONLY if escalated.",
            "depends_on": [2]
        },
        {
            "agent_type": "Operations",
            "title": "Post-Mortem Generation",
            "description": "Auto-generate a post-mortem written in plain English from the actual execution trace.",
            "depends_on": [3]
        }
    ]
