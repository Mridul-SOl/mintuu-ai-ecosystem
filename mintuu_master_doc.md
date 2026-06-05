# Mintuu Master Documentation
## Table of Contents
- [Section 1 — Project Introduction](#section-1--project-introduction)
- [Section 2 — Who is this for and what is the benefit](#section-2--who-is-this-for-and-what-is-the-benefit)
  - [Startup founders](#startup-founders)
  - [Engineering teams](#engineering-teams)
  - [Product managers](#product-managers)
  - [Operations teams](#operations-teams)
  - [Investors and evaluators](#investors-and-evaluators)
- [Section 3 — Tech stack with explanation of every choice](#section-3--tech-stack-with-explanation-of-every-choice)
- [Section 4 — Complete project architecture](#section-4--complete-project-architecture)
  - [4.1 Component-by-component explanation](#41-component-by-component-explanation)
  - [4.2 Full system ASCII architecture flowchart](#42-full-system-ascii-architecture-flowchart)
  - [4.3 Flagship workflow execution flowcharts](#43-flagship-workflow-execution-flowcharts)
- [Section 5 — Complete project structure](#section-5--complete-project-structure)
- [Section 6 — The three flagship workflows explained completely](#section-6--the-three-flagship-workflows-explained-completely)
  - [Workflow 1 — GitHub autonomous incident pipeline](#workflow-1--github-autonomous-incident-pipeline)
  - [Workflow 2 — Product launch and critique loop](#workflow-2--product-launch-and-critique-loop)
  - [Workflow 3 — Critical infrastructure anomaly response](#workflow-3--critical-infrastructure-anomaly-response)
- [Section 7 — How to use Mintuu — what tasks to give the agents](#section-7--how-to-use-mintuu--what-tasks-to-give-the-agents)
- [Section 8 — API documentation](#section-8--api-documentation)
- [Section 9 — Observability and dashboard guide](#section-9--observability-and-dashboard-guide)
- [Section 10 — Memory system explained](#section-10--memory-system-explained)
- [Section 11 — Pros and cons](#section-11--pros-and-cons)
- [Section 12 — Setup and execution guide](#section-12--setup-and-execution-guide)
- [Section 13 — Agent personalities and reasoning behavior](#section-13--agent-personalities-and-reasoning-behavior)
- [Section 14 — How agents talk to each other](#section-14--how-agents-talk-to-each-other)
- [Section 15 — Failure handling and what happens when things go wrong](#section-15--failure-handling-and-what-happens-when-things-go-wrong)
- [Section 16 — Security and permissions](#section-16--security-and-permissions)
- [Section 17 — Extending Mintuu — how to add your own agent or workflow](#section-17--extending-mintuu--how-to-add-your-own-agent-or-workflow)
- [Section 18 — Real business scenarios with expected outputs](#section-18--real-business-scenarios-with-expected-outputs)
- [Section 19 — Comparison with similar tools](#section-19--comparison-with-similar-tools)
- [Section 20 — Glossary](#section-20--glossary)
- [Section 21 — Version history and changelog (v1 to v3)](#section-21--version-history-and-changelog-v1-to-v3)
- [Section 22 — Known issues and honest component status](#section-22--known-issues-and-honest-component-status)
- [Section 23 — 10-minute live demo script](#section-23--10-minute-live-demo-script)
- [Executive Summary (one page)](#executive-summary-one-page)

## Section 1 — Project Introduction
Mintuu starts from a painfully common business reality: teams spend enormous energy coordinating each other instead of moving work forward. People chase updates between departments, ask the same questions repeatedly, re-explain context, and re-decide things that were already decided last week. That works at a small scale, but as complexity grows, coordination itself becomes the bottleneck.

Mintuu is built as an AI operating system that treats this bottleneck as a systems problem, not a chat problem. Instead of one general-purpose assistant, it runs a structured company of specialized agents: strategy, research, production, operations, finance, and more. These agents collaborate through explicit handoffs, shared context, and workflow state. They reason step-by-step, write decisions to memory, and continue execution without waiting for human intervention between every step.

This is fundamentally different from a chatbot. A chatbot is usually request-response and ephemeral. Mintuu is workflow-driven and cumulative. It executes multi-step plans across multiple agents, uses organizational memory (SQLite + ChromaDB vector retrieval), and makes future decisions based on prior runs.

A typical session looks like this: a GitHub issue is opened for a production incident; Mintuu automatically triggers an incident workflow; Research checks historical context, Production analyzes impact, the CEO agent decides severity, Operations produces a response plan, and Marketing publishes the final summary for communication surfaces. The dashboard updates live over WebSocket while the workflow runs. The user can walk away and return to a completed, reasoned, documented outcome.

## Section 2 — Who is this for and what is the benefit
### Startup founders
Before Mintuu, founders often spend their day switching contexts: strategy in the morning, metrics in the afternoon, coordination all day. Mintuu gives founders a structured AI team that can run research, planning, and cross-functional execution with a single goal-level prompt. Instead of asking five people for updates, they review one coherent output with reasoning and traceability. After adoption, the founder’s role shifts from manual coordinator to decision-maker.

### Engineering teams
Before Mintuu, incident response often means waking someone up, digging through context, and reconstructing what happened under pressure. Mintuu can run autonomous response flows that investigate, classify severity, produce action plans, and leave machine-readable logs. Teams get faster triage with less context loss and better post-incident artifacts. It does not replace engineers; it reduces the repetitive coordination overhead around engineering response.

### Product managers
Before Mintuu, PMs convert high-level goals into fragmented documents, then manually align marketing, engineering, and operations. Mintuu can take one-line business intent and orchestrate a department-by-department launch workflow with dependencies. PMs move from “document chasing” to “constraint setting and validation.” The output is not just ideas; it is execution sequencing with handoffs.

### Operations teams
Before Mintuu, operations work is continuous but scattered across dashboards, alerts, tickets, and status updates. Mintuu adds autonomous health checks, escalation logic, and structured post-mortem generation. Ops teams get a system that can run recurring checks in the background and produce consistent operational narratives. After implementation, operations become more proactive and less interrupt-driven.

### Investors and evaluators
Before Mintuu, many AI demos stop at polished chat outputs without operational depth. Mintuu demonstrates real multi-agent execution, workflow state transitions, memory retrieval, and reasoned decisions with traces. Evaluators can inspect architecture, logs, and outputs to verify behavior. The project is useful as both a product candidate and a proof-of-capability platform.

## Section 3 — Tech stack with explanation of every choice
- **FastAPI (API gateway)**
  - **What it is:** An async-first Python web framework.
  - **Why chosen over Flask:** Flask is minimal and excellent, but async support is less native and requires more add-ons for comparable real-time behavior.
  - **Why chosen over Django:** Django is powerful but heavier than needed for this API-first orchestration runtime.
  - **Mintuu role:** Serves REST endpoints (`/api/v1/*`), dashboard HTML, WebSocket endpoint `/ws`, and GitHub webhook ingestion.
- **Ollama (local model runtime)**
  - **What it is:** Local LLM serving infrastructure.
  - **Why local models instead of cloud-only APIs:** Lower marginal cost per iteration, offline-capable development, and full control of experimentation.
  - **Mintuu role:** Default provider through `OllamaProvider`, including model routing and fallback behavior.
- **ChromaDB (vector memory)**
  - **What it is:** Persistent vector database for semantic retrieval.
  - **Why vector search instead of SQL-only memory:** Keyword lookups miss semantically similar past incidents; vector retrieval enables context matching by meaning.
  - **Mintuu role:** Stores organizational memories in collections like `org_knowledge`, retrieves similar incidents for agent context.
- **SQLite (transactional persistence)**
  - **What it is:** Embedded relational database.
  - **Why alongside ChromaDB:** ChromaDB handles semantic retrieval; SQLite handles canonical workflow/task/event/log state with ACID consistency.
  - **Mintuu role:** Stores tasks, workflows, messages, memories metadata, events, agent logs, tool logs.
- **Celery + Redis (distributed task queue)**
  - **What it is:** Background execution framework and broker/backend.
  - **Why distributed queues matter:** Concurrent workflows and background reflection require decoupled execution for scale.
  - **Mintuu role:** Present and configured (`core/distributed/*`), currently partially integrated with mock task execution in local workflow path.
- **Playwright (browser automation/screenshots)**
  - **What it is:** Browser automation framework.
  - **Why chosen:** Stable headless execution and reliable screenshot automation for evidence artifacts.
  - **Mintuu role:** Used in demo orchestration (`run_flagships_v2.py`) and available via browser tool implementation.
- **WebSocket streaming (replacing polling)**
  - **What it is:** Persistent duplex channel between server and dashboard clients.
  - **Why replaced polling:** Lower latency state updates, fewer redundant HTTP requests, cleaner real-time UX.
  - **Mintuu role:** `/ws` pushes `state_update`, `collaboration_update`, `autonomous_update` at 2-second cadence.
- **Model routing: `llama3` and `mistral` families**
  - **What it is:** Preference-based model selection in `BaseAgent.handle_task` and `OllamaProvider`.
  - **Why these pairings:** Strategic/reasoning-heavy roles (`CEO`, `Research`, `Operations`) route to llama-family preference; other roles route to mistral-family preference for faster operational throughput.
  - **Mintuu role:** Practical division of model workload by agent role and decision criticality.

## Section 4 — Complete project architecture
### 4.1 Component-by-component explanation
- **Orchestration Manager (`core/orchestration/orchestration_manager.py`)**: System kernel; composes all subsystems and coordinates task/workflow execution. Remove it and the ecosystem has no central control plane.
- **Collaboration Engine (`core/orchestration/collaboration_engine.py`)**: Implements structured patterns (`INFO_REQUEST`, `SUBTASK_DELEGATION`, `APPROVAL_GATE`, `DATA_HANDOFF`, `BROADCAST_UPDATE`). Remove it and agent handoffs become ad hoc.
- **Workflow Engine (`core/workflows/workflow_engine.py`)**: Executes step graphs with dependencies, approvals, retry, and status transitions. Remove it and multi-step autonomy collapses.
- **Task Router (`core/orchestration/task_router.py`)**: Maps intent to agent(s) and suggests workflow orders. Remove it and routing must be manually specified.
- **Execution Manager (`tools/execution_manager.py`)**: Wraps tools with execution records and extended tool registration. Remove it and tool usage loses observability and structure.
- **Autonomous Engine (`automation/autonomous_engine.py`)**: Runs scheduled recurring tasks and background simulation cycles. Remove it and no autonomous recurrence exists.
- **Memory Manager (`core/memory/memory_manager.py`)**: Multi-tier memory (short/long/workflow/conversation/organizational) with context assembly. Remove it and agents lose continuity.
- **Message Bus (`core/communication/message_bus.py`)**: Inter-agent communication fabric with mailboxes and priorities. Remove it and no systematic messaging exists.
- **State Manager (`core/state/state_manager.py`)**: Tracks agent runtime state, system health, workflow state, and checkpoints. Remove it and operational introspection is weak.
- **Agent Registry (`core/orchestration/agent_registry.py`)**: Agent discovery and lifecycle registration. Remove it and orchestrator cannot resolve target agents.
- **LLM Manager (`core/llm/llm_manager.py`)**: Provider-agnostic LLM request handling and token tracking hooks. Remove it and agents cannot reason through shared interface.
- **Reasoning Engine (`core/llm/reasoning_engine.py`)**: Builds structured reasoning prompts and enforces JSON parsing/fallback. Remove it and outputs become less structured and harder to validate.
- **Vector Memory Store (`core/memory/vector_memory.py`)**: ChromaDB-backed semantic retrieval layer. Remove it and memory retrieval degrades to lexical/non-semantic behavior.
- **Event Bus (`core/events/event_bus.py`)**: Async pub/sub queue for external and internal events. Remove it and webhook/event decoupling is reduced.

### 4.2 Full system ASCII architecture flowchart
```text
[User/API Client] or [External Trigger: GitHub Webhook]
                |
                v
         [FastAPI Gateway]
   (/chat, /execute, /workflows, /webhooks, /ws)
                |
                v
      [Orchestration Manager Kernel]
      |        |         |        |
      |        |         |        +--> [Autonomous Engine] --scheduled--> [Task Execution]
      |        |         |
      |        |         +--> [Workflow Engine] --deps/retries/approval--> [Step Runner]
      |        |
      |        +--> [Task Router] --agent selection--> [Agent Registry]
      |
      +--> [Collaboration Engine] <--> [Message Bus] <--> [Agents]
                                         |                     |
                                         |                     +--> [Reasoning Engine] --> [LLM Manager]
                                         |                                             |--> [Provider Router]
                                         |                                             |--> [Ollama/OpenAI/Anthropic]
                                         |
                                         +--> [Event Bus]

[Agents] --> [Execution Manager] --> [Tool Registry] --> [Tools (file/terminal/github/browser/email/...)]

[Agents/Orchestrator] --> [Memory Manager]
                         |--> [SQLite (tasks/workflows/messages/events/logs)]
                         |--> [Vector Memory Store: ChromaDB]

[State Manager] <--- runtime statuses/workflow snapshots from orchestrator+agents

[WebSocket State Pusher] <-- status/collaboration/autonomous data -- [Orchestration Manager]
                |
                v
          [Live Dashboard]

Final outputs:
- Completed workflow state
- Stored organizational memory
- Reasoning traces and logs
- Dashboard/event updates
```

### 4.3 Flagship workflow execution flowcharts
#### Workflow 1 — GitHub incident pipeline
```text
GitHub Issue Opened
   |
   v
Webhook /webhooks/github
   |
   v
Create Workflow (5 steps)
   |
   +--> Step 1: Research (query vector memory)
   |        |-- if retrieval empty --> continue with fallback context
   |        +-- success --> handoff to Production
   |
   +--> Step 2: Production (impact analysis)
   |        |-- on failure --> retry up to max_retries (3)
   |        +-- success --> handoff to CEO
   |
   +--> Step 3: CEO (severity decision)
   |        |-- may deny approval gate (if configured)
   |        +-- success --> handoff to Operations
   |
   +--> Step 4: Operations (response plan)
   |        +-- success --> handoff to Marketing
   |
   +--> Step 5: Marketing (final summary/dashboard update)
            |
            v
       Workflow COMPLETE
            |
            v
   Store result in workflow + org memory
```

#### Workflow 2 — Product launch with critique loop
```text
Goal Triggered: "Launch Mintuu Pro ... 500 signups ..."
   |
   v
Step 1 Marketing draft plan
   |
   v
Step 2 CEO review
   |-- if plan mathematically optimistic --> REJECT --> Revision Workflow
   |                                          |
   |                                          v
   |                                  Marketing revises plan
   |                                          |
   |                                          v
   |                                   CEO re-reviews
   |-- if approved ----------------------------+
   v
Approved launch plan persisted
   |
   v
Memory updated with conversion assumptions + rationale
```

#### Workflow 3 — Critical infrastructure anomaly response
```text
Anomaly Trigger (CPU 94%, latency degradation)
   |
   v
Step 1 Infrastructure/Research root-cause analysis
   |
   v
Step 2 Security/Production risk-impact assessment
   |
   v
Step 3 Operations severity scoring + mitigation path
   |-- if severity >= escalation threshold --> CEO escalation decision
   |-- else --> direct operations mitigation
   v
Step 4 Operations incident resolution + post-mortem draft
   |
   v
Workflow COMPLETE -> memory + logs + dashboard timeline
```

## Section 5 — Complete project structure
```text
mintuu_ai_ecosystem/
├── .DS_Store
├── .env
├── .env.example
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-314.pyc
│   └── run_flagships_v2.cpython-314.pyc
├── agents
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-314.pyc
│   ├── analytics_agent
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── base_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── base.cpython-314.pyc
│   │   └── base.py
│   ├── ceo_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── agent.cpython-314.pyc
│   │   │   └── system_prompt.cpython-314.pyc
│   │   ├── agent.py
│   │   └── system_prompt.py
│   ├── finance_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── agent.cpython-314.pyc
│   │   │   └── system_prompt.cpython-314.pyc
│   │   ├── agent.py
│   │   └── system_prompt.py
│   ├── hr_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── agent.cpython-314.pyc
│   │   └── agent.py
│   ├── infrastructure_agent
│   │   ├── __pycache__
│   │   │   └── agent.cpython-314.pyc
│   │   └── agent.py
│   ├── legal_agent
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── marketing_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── agent.cpython-314.pyc
│   │   │   └── system_prompt.cpython-314.pyc
│   │   ├── agent.py
│   │   └── system_prompt.py
│   ├── operations_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── agent.cpython-314.pyc
│   │   └── agent.py
│   ├── production_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── agent.cpython-314.pyc
│   │   └── agent.py
│   ├── research_agent
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── agent.cpython-314.pyc
│   │   │   └── system_prompt.cpython-314.pyc
│   │   ├── agent.py
│   │   └── system_prompt.py
│   └── security_agent
│       ├── __pycache__
│       │   └── agent.cpython-314.pyc
│       └── agent.py
├── api
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   ├── app.cpython-314.pyc
│   │   ├── webhooks.cpython-314.pyc
│   │   └── websocket.cpython-314.pyc
│   ├── app.py
│   ├── webhooks.py
│   └── websocket.py
├── automation
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   └── autonomous_engine.cpython-314.pyc
│   └── autonomous_engine.py
├── build_report_workflow.py
├── cli
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   └── main.cpython-314.pyc
│   └── main.py
├── config
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   └── settings.cpython-314.pyc
│   └── settings.py
├── core
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-314.pyc
│   ├── adaptation
│   │   ├── behavior_optimizer.py
│   │   ├── feedback_processor.py
│   │   ├── learning_engine.py
│   │   ├── strategy_evaluator.py
│   │   └── workflow_optimizer.py
│   ├── approval
│   │   ├── approval_engine.py
│   │   ├── escalation_manager.py
│   │   ├── human_review.py
│   │   └── risk_analyzer.py
│   ├── communication
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── message_bus.cpython-314.pyc
│   │   └── message_bus.py
│   ├── distributed
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks.py
│   ├── events
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── event_bus.cpython-314.pyc
│   │   │   └── event_types.cpython-314.pyc
│   │   ├── event_bus.py
│   │   └── event_types.py
│   ├── goals
│   │   ├── __init__.py
│   │   └── goal_engine.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── llm_manager.cpython-314.pyc
│   │   │   ├── provider_router.cpython-314.pyc
│   │   │   ├── reasoning_engine.cpython-314.pyc
│   │   │   └── token_tracker.cpython-314.pyc
│   │   ├── context_builder.py
│   │   ├── llm_manager.py
│   │   ├── provider_router.py
│   │   ├── providers
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-314.pyc
│   │   │   │   ├── anthropic_provider.cpython-314.pyc
│   │   │   │   ├── base_provider.cpython-314.pyc
│   │   │   │   ├── ollama_provider.cpython-314.pyc
│   │   │   │   └── openai_provider.cpython-314.pyc
│   │   │   ├── anthropic_provider.py
│   │   │   ├── base_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   └── openai_provider.py
│   │   ├── reasoning_engine.py
│   │   └── token_tracker.py
│   ├── memory
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── memory_manager.cpython-314.pyc
│   │   │   └── vector_memory.cpython-314.pyc
│   │   ├── advanced
│   │   │   ├── long_term_knowledge.py
│   │   │   ├── memory_ranker.py
│   │   │   ├── memory_summarizer.py
│   │   │   ├── organizational_brain.py
│   │   │   └── semantic_learning.py
│   │   ├── memory_manager.py
│   │   └── vector_memory.py
│   ├── multimodal
│   │   ├── document_parser.py
│   │   ├── multimodal_router.py
│   │   ├── screenshot_reasoner.py
│   │   └── vision_engine.py
│   ├── orchestration
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   ├── agent_registry.cpython-314.pyc
│   │   │   ├── collaboration_engine.cpython-314.pyc
│   │   │   ├── orchestration_manager.cpython-314.pyc
│   │   │   └── task_router.cpython-314.pyc
│   │   ├── agent_registry.py
│   │   ├── collaboration_engine.py
│   │   ├── orchestration_manager.py
│   │   └── task_router.py
│   ├── planning
│   │   ├── adaptive_planner.py
│   │   ├── dependency_graph.py
│   │   ├── execution_forecaster.py
│   │   ├── strategic_planner.py
│   │   └── task_decomposer.py
│   ├── reflection
│   │   └── reflection_engine.py
│   ├── state
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-314.pyc
│   │   │   └── state_manager.cpython-314.pyc
│   │   └── state_manager.py
│   └── workflows
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-314.pyc
│       │   ├── flagship_workflows.cpython-314.pyc
│       │   └── workflow_engine.cpython-314.pyc
│       ├── flagship_workflows.py
│       └── workflow_engine.py
├── dashboard
│   ├── __init__.py
│   ├── static
│   │   ├── css
│   │   │   └── dashboard.css
│   │   └── js
│   │       └── dashboard.js
│   └── templates
│       └── dashboard.html
├── database
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   └── models.cpython-314.pyc
│   ├── chroma_db
│   │   ├── 909af621-9653-4797-be07-b16f020b8c87
│   │   │   ├── data_level0.bin
│   │   │   ├── header.bin
│   │   │   ├── length.bin
│   │   │   └── link_lists.bin
│   │   └── chroma.sqlite3
│   ├── mintuu_ecosystem.db
│   └── models.py
├── deployment
│   ├── kubernetes
│   │   └── deployment.yaml
│   ├── nginx
│   │   └── nginx.conf
│   └── terraform
│       └── main.tf
├── docker-compose.yml
├── execution_trace.json
├── generate_architecture.py
├── integrations
│   └── __init__.py
├── logs
│   └── workflow_1_execution.log
├── mintuu_ai_ecosystem.egg-info
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── PKG-INFO
│   ├── requires.txt
│   ├── SOURCES.txt
│   └── top_level.txt
├── mintuu_ecosystem.db
├── mintuu_flagship_report.html
├── mintuu_master_doc.md
├── mintuu_master_doc.pdf
├── monitoring
│   ├── orchestration_metrics.py
│   ├── performance_monitor.py
│   ├── system_profiler.py
│   ├── tracing_engine.py
│   └── workflow_analytics.py
├── pyproject.toml
├── raw_reasoning_log.txt
├── README.md
├── report
│   ├── .DS_Store
│   └── output
│       ├── mintuu_flagship_report.html
│       ├── mintuu_flagship_report.md
│       ├── mintuu_flagship_report.pdf
│       └── w1_dashboard.png
├── requirements_v3.txt
├── run_flagships.py
├── run_flagships_v2.py
├── test_ollama.py
├── test_reasoning.py
├── test_workflow.py
├── tests
│   └── __init__.py
└── tools
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-314.pyc
    │   ├── execution_manager.cpython-314.pyc
    │   └── tool_registry.cpython-314.pyc
    ├── execution_manager.py
    ├── implementations
    │   ├── __init__.py
    │   ├── browser_tool.py
    │   ├── email_tool.py
    │   └── github_tool.py
    └── tool_registry.py
```


- `.DS_Store` — macOS Finder metadata file; not required for application runtime.
- `.env` — Local environment variable file containing machine-specific secrets and runtime configuration.
- `.env.example` — Template environment file documenting required configuration keys for new setups.
- `README.md` — Top-level project overview and quick-start instructions for running Mintuu.
- `__init__.py` — Package marker enabling Python module imports for this directory.
- `__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `__pycache__/run_flagships_v2.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/analytics_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/analytics_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/base_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/base_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/base_agent/__pycache__/base.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/base_agent/base.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/ceo_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/ceo_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/ceo_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/ceo_agent/__pycache__/system_prompt.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/ceo_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/ceo_agent/system_prompt.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/finance_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/finance_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/finance_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/finance_agent/__pycache__/system_prompt.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/finance_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/finance_agent/system_prompt.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/hr_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/hr_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/hr_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/hr_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/infrastructure_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/infrastructure_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/legal_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/legal_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/marketing_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/marketing_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/marketing_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/marketing_agent/__pycache__/system_prompt.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/marketing_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/marketing_agent/system_prompt.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/operations_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/operations_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/operations_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/operations_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/production_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/production_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/production_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/production_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/research_agent/__init__.py` — Package marker enabling Python module imports for this directory.
- `agents/research_agent/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/research_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/research_agent/__pycache__/system_prompt.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/research_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/research_agent/system_prompt.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `agents/security_agent/__pycache__/agent.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `agents/security_agent/agent.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `api/__init__.py` — Package marker enabling Python module imports for this directory.
- `api/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `api/__pycache__/app.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `api/__pycache__/webhooks.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `api/__pycache__/websocket.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `api/app.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `api/webhooks.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `api/websocket.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `automation/__init__.py` — Package marker enabling Python module imports for this directory.
- `automation/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `automation/__pycache__/autonomous_engine.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `automation/autonomous_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `build_report_workflow.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `cli/__init__.py` — Package marker enabling Python module imports for this directory.
- `cli/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `cli/__pycache__/main.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `cli/main.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `config/__init__.py` — Package marker enabling Python module imports for this directory.
- `config/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `config/__pycache__/settings.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `config/settings.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/adaptation/behavior_optimizer.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/adaptation/feedback_processor.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/adaptation/learning_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/adaptation/strategy_evaluator.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/adaptation/workflow_optimizer.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/approval/approval_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/approval/escalation_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/approval/human_review.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/approval/risk_analyzer.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/communication/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/communication/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/communication/__pycache__/message_bus.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/communication/message_bus.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/distributed/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/distributed/celery_app.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/distributed/tasks.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/events/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/events/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/events/__pycache__/event_bus.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/events/__pycache__/event_types.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/events/event_bus.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/events/event_types.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/goals/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/goals/goal_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/llm/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/__pycache__/llm_manager.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/__pycache__/provider_router.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/__pycache__/reasoning_engine.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/__pycache__/token_tracker.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/context_builder.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/llm_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/provider_router.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/providers/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/llm/providers/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/providers/__pycache__/anthropic_provider.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/providers/__pycache__/base_provider.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/providers/__pycache__/ollama_provider.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/providers/__pycache__/openai_provider.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/llm/providers/anthropic_provider.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/providers/base_provider.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/providers/ollama_provider.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/providers/openai_provider.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/reasoning_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/llm/token_tracker.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/memory/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/memory/__pycache__/memory_manager.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/memory/__pycache__/vector_memory.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/memory/advanced/long_term_knowledge.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/advanced/memory_ranker.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/advanced/memory_summarizer.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/advanced/organizational_brain.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/advanced/semantic_learning.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/memory_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/memory/vector_memory.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/multimodal/document_parser.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/multimodal/multimodal_router.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/multimodal/screenshot_reasoner.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/multimodal/vision_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/orchestration/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/orchestration/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/orchestration/__pycache__/agent_registry.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/orchestration/__pycache__/collaboration_engine.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/orchestration/__pycache__/orchestration_manager.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/orchestration/__pycache__/task_router.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/orchestration/agent_registry.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/orchestration/collaboration_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/orchestration/orchestration_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/orchestration/task_router.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/planning/adaptive_planner.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/planning/dependency_graph.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/planning/execution_forecaster.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/planning/strategic_planner.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/planning/task_decomposer.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/reflection/reflection_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/state/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/state/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/state/__pycache__/state_manager.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/state/state_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/workflows/__init__.py` — Package marker enabling Python module imports for this directory.
- `core/workflows/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/workflows/__pycache__/flagship_workflows.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/workflows/__pycache__/workflow_engine.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `core/workflows/flagship_workflows.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `core/workflows/workflow_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `dashboard/__init__.py` — Package marker enabling Python module imports for this directory.
- `dashboard/static/css/dashboard.css` — Stylesheet defining dashboard visual design and UI theming.
- `dashboard/static/js/dashboard.js` — Client-side dashboard logic for live updates, rendering, and interactions.
- `dashboard/templates/dashboard.html` — Rendered report or dashboard template used for browser-based presentation.
- `database/__init__.py` — Package marker enabling Python module imports for this directory.
- `database/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `database/__pycache__/models.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/data_level0.bin` — ChromaDB binary index shard used for vector storage/search internals.
- `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/header.bin` — ChromaDB binary index shard used for vector storage/search internals.
- `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/length.bin` — ChromaDB binary index shard used for vector storage/search internals.
- `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/link_lists.bin` — ChromaDB binary index shard used for vector storage/search internals.
- `database/chroma_db/chroma.sqlite3` — ChromaDB internal SQLite persistence file for vector index metadata.
- `database/mintuu_ecosystem.db` — SQLite database file storing runtime entities like tasks, workflows, memories, and logs.
- `database/models.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `deployment/kubernetes/deployment.yaml` — Deployment/environment configuration in YAML format.
- `deployment/nginx/nginx.conf` — Service configuration for reverse proxy/network behavior.
- `deployment/terraform/main.tf` — Terraform infrastructure-as-code definition file.
- `docker-compose.yml` — Container orchestration configuration file.
- `execution_trace.json` — Structured runtime artifact (trace, data dump, or config) captured from executions.
- `generate_architecture.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `integrations/__init__.py` — Package marker enabling Python module imports for this directory.
- `logs/workflow_1_execution.log` — Execution log capturing runtime events, initialization, and workflow progress.
- `mintuu_ai_ecosystem.egg-info/PKG-INFO` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ai_ecosystem.egg-info/SOURCES.txt` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ai_ecosystem.egg-info/dependency_links.txt` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ai_ecosystem.egg-info/entry_points.txt` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ai_ecosystem.egg-info/requires.txt` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ai_ecosystem.egg-info/top_level.txt` — Python packaging metadata generated during installation/build of the project package.
- `mintuu_ecosystem.db` — SQLite database file storing runtime entities like tasks, workflows, memories, and logs.
- `mintuu_flagship_report.html` — Rendered report or dashboard template used for browser-based presentation.
- `mintuu_master_doc.md` — Markdown documentation artifact explaining project behavior or reports.
- `mintuu_master_doc.pdf` — Exported document artifact generated from markdown/html reports for sharing or review.
- `monitoring/orchestration_metrics.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `monitoring/performance_monitor.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `monitoring/system_profiler.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `monitoring/tracing_engine.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `monitoring/workflow_analytics.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `pyproject.toml` — Project/build configuration in TOML format.
- `raw_reasoning_log.txt` — Plain-text artifact containing logs, traces, or generated reference outputs.
- `report/.DS_Store` — macOS Finder metadata file; not required for application runtime.
- `report/output/mintuu_flagship_report.html` — Rendered report or dashboard template used for browser-based presentation.
- `report/output/mintuu_flagship_report.md` — Markdown documentation artifact explaining project behavior or reports.
- `report/output/mintuu_flagship_report.pdf` — Exported document artifact generated from markdown/html reports for sharing or review.
- `report/output/w1_dashboard.png` — Screenshot artifact used as visual evidence during workflow/dashboard demonstrations.
- `requirements_v3.txt` — Plain-text artifact containing logs, traces, or generated reference outputs.
- `run_flagships.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `run_flagships_v2.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `test_ollama.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `test_reasoning.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `test_workflow.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `tests/__init__.py` — Package marker enabling Python module imports for this directory.
- `tools/__init__.py` — Package marker enabling Python module imports for this directory.
- `tools/__pycache__/__init__.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `tools/__pycache__/execution_manager.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `tools/__pycache__/tool_registry.cpython-314.pyc` — Compiled Python bytecode cache generated by the interpreter for faster imports.
- `tools/execution_manager.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `tools/implementations/__init__.py` — Package marker enabling Python module imports for this directory.
- `tools/implementations/browser_tool.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `tools/implementations/email_tool.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `tools/implementations/github_tool.py` — Python source module implementing application logic, APIs, agents, or tooling.
- `tools/tool_registry.py` — Python source module implementing application logic, APIs, agents, or tooling.

## Section 6 — The three flagship workflows explained completely
### Workflow 1 — GitHub autonomous incident pipeline
**What it does (plain English):** It takes a newly opened GitHub issue, investigates likely causes, determines severity, writes an action plan, and publishes a final coordinated summary.

**How to trigger it:** Send a GitHub `issues` webhook with action `opened` to `POST /webhooks/github`.

**Step-by-step narrative (one paragraph per agent step):**
1. **Research** starts by searching organizational memory for similar incidents so the team does not repeat old mistakes. It tries to anchor the current issue in historical evidence and returns findings that can guide downstream decisions.
2. **Production** reads the incident text and estimates technical impact, including affected components and urgency. It proposes concrete investigative actions and what to test first.
3. **CEO** reads both perspectives, weighs business impact, and decides whether immediate action is required. This is where strategic accountability appears: not just “what happened,” but “what do we do now.”
4. **Operations** converts the CEO direction into an actionable response plan with sequencing and coordination expectations. The output is operationally practical instead of abstract.
5. **Marketing/Comms** produces a final narrative suitable for stakeholder-facing surfaces (labels, summary updates, status communication).

**Workflow 1 flowchart with failure/retry paths:**
```text
[Webhook Received]
   -> [Research]
      -> if LLM JSON parse fails: fallback output + continue
      -> [Production]
         -> if execution fails: retry #1/#2/#3 then mark FAILED
         -> [CEO]
            -> if decision blocked (approval denied): mark BLOCKED
            -> [Operations]
               -> if step fails after retries: workflow PARTIAL
               -> [Marketing]
                  -> complete -> persist memory + logs
```

**Screenshot reference (exact state):**
- **Filename:** `report/output/w1_dashboard.png`
- **Caption:** “Captured at the moment CEO step finished and Operations step started; reasoning panel open on the right; workflow graph shows steps 1–3 green and step 4 active; execution timeline shows Research 29.0s and Production 41.2s bars; collaboration feed includes handoff `Production → CEO`.”

![Workflow 1 dashboard state](report/output/w1_dashboard.png)

**Direct reasoning quote:**
> “Given the severity of the issue and the potential impact on production, I conclude that immediate action is necessary to resolve the memory leak and prevent future crashes.”

**Real execution numbers (from `execution_trace.json`):**
- Total runtime: **299.60s** (07:04:26.479 → 07:09:26.080 UTC)
- Step runtimes: **Research 29.029s**, **Production 41.248s**, **CEO 66.411s**, **Operations 76.666s**, **Marketing 86.190s**
- Agent handoffs recorded: **4 data handoffs**
- Models used: **llama-family** for Research/CEO/Operations; **mistral-family** for Production/Marketing
- Persisted token telemetry in trace artifact: **0 fields recorded** (token tracker not persisted to this artifact)
- Memory retrieval fired: **Yes** (Research agent always queries vector memory before reasoning)
- Critique loop: **No** (single-pass incident pipeline)

**What gets stored in memory and why next run is smarter:**
- Workflow final result stored via `store_workflow_memory(..., key="final_result")`.
- Agent summaries stored in short-term + organizational memory.
- ChromaDB receives organizational entries, making semantically similar incidents easier to retrieve later.

## Section 8 — API documentation
Base URL (local default): `http://localhost:8000`

### Chat
- **POST** `/api/v1/chat`
- **Purpose:** Conversational entry point; routes either to single task or auto-workflow.
- **Parameters:**
  - `message` (string, required): user intent.
  - `conversation_id` (string, optional): existing thread id.
  - `user_id` (string, optional; default `default`).

```bash
curl -X POST http://localhost:8000/api/v1/chat   -H 'Content-Type: application/json'   -d '{"message":"Launch Mintuu Pro by Q3 with 500 signups","user_id":"demo"}'
```

```json
{
  "conversation_id": "b7f...",
  "response": "📋 Auto-Workflow...",
  "result": {"status": "COMPLETED", "steps": [...] },
  "timestamp": "2026-05-09T..."
}
```

## Section 22 — Known issues and honest component status
1. **Email tool** — Partially stubbed/simulated when SMTP credentials missing. **Plan:** add provider adapters + integration tests. **Effort:** 1–2 days.
2. **Browser automation** — Integrated, but mainly utility-level; not deeply wired into production workflows. **Plan:** workflow-native browser actions + robust error handling. **Effort:** 2–4 days.
3. **Redis/Celery integration** — Configured but primary workflow path still synchronous/local in current run path. **Plan:** route workflow execution through distributed task orchestration. **Effort:** 4–7 days.
4. **Token observability** — token tracker exists but run artifacts do not persist per-workflow token totals. **Plan:** persist token usage per step/workflow in SQLite. **Effort:** 1–2 days.
5. **Permission matrix enforcement** — framework exists, role-specific grants incomplete. **Plan:** define + enforce agent permission policy at startup. **Effort:** 2–3 days.
6. **Model prompt variable mismatch** — some system prompt modules use non-`SYSTEM_PROMPT` names, causing generic fallback prompts. **Plan:** normalize prompt constants and tests. **Effort:** <1 day.
7. **`settings.memory.conversation_history_limit` missing** — referenced but not defined; can break context assembly in some paths. **Plan:** add config field + defaults. **Effort:** <1 day.
8. **Infrastructure/Security `summarize` method signature mismatch** — potential runtime bug under direct usage. **Plan:** align method signatures with `BaseAgent`. **Effort:** <1 day.

## Executive Summary (one page)
Mintuu is an AI operating system that organizes specialized agents into a company-like execution model. Instead of handling one prompt at a time, it runs full workflows: routing tasks, coordinating handoffs, making decisions, and persisting memory for future runs. The platform combines FastAPI orchestration, WebSocket observability, SQLite system state, and ChromaDB semantic memory retrieval.
