# Mintuu AI Ecosystem Complete Technical Snapshot

Generated from local workspace: `/Users/mridulsoliwal/Documents/All_Projects/AI_Agents/mintuu_ai_ecosystem`  
Generation date: 2026-05-28 Asia/Kolkata.  
Purpose: brief an external AI assistant for strategic planning, product direction, feature planning, and integration prompts.

## 1. Project Identity

| Field | Value |
|---|---|
| Repository folder | `AI_Agents/mintuu_ai_ecosystem` |
| Package name | `mintuu-ai-ecosystem` from `pyproject.toml` |
| Package version | `1.0.0` from `pyproject.toml` |
| Runtime/settings version | `3.0.0` from `config/settings.py` |
| FastAPI app title | `Mintuu AI Ecosystem v2` from `api/app.py` |
| README title | `Mintuu AI Ecosystem v3` |
| One-sentence description | An autonomous AI-native business operating system that coordinates specialized departmental AI agents through a central orchestration layer, workflow engine, memory system, tools, and a real-time dashboard. |
| Problem solved | It turns isolated AI agents into a coordinated digital workforce that can route work, execute multi-step workflows, remember results, collaborate, expose APIs, and present state through a dashboard. |
| Built for | Founders, builders, AI-agent developers, small teams, and operators who want a local/prototype autonomous business operations platform. |

Important identity note: the project has version naming drift. Packaging says `1.0.0`, settings say `3.0.0`, FastAPI title says `v2`, and README says `v3`. External planning should treat this as a v3 prototype with some v2 naming left in code.

## 2. Complete Tech Stack

| Technology | Exact observed version | Role | Files using it |
|---|---:|---|---|
| Python | `Python 3.14.4` | Backend language and runtime | All `.py` files |
| FastAPI | `0.136.1` | HTTP API, page routes, WebSocket/webhook routers | `api/app.py`, `api/auth_routes.py`, `api/webhooks.py`, `api/websocket.py` |
| Uvicorn | `0.46.0` | ASGI dev/production server | README, Makefile, Render start command |
| Pydantic | `2.13.4` | Request models and settings models | `api/app.py`, `api/auth_routes.py`, `config/settings.py`, `core/events/event_types.py` |
| Jinja2 | `3.1.6` | Declared template dependency; templates are currently read directly as files | `pyproject.toml`; dashboard templates |
| SQLite | `stdlib sqlite3 plus `.db` files` | Primary persistent relational storage | `database/models.py`, `database/mintuu_ecosystem.db` |
| ChromaDB | `1.5.9` | Persistent vector store for semantic organizational memory | `core/memory/vector_memory.py`, `database/chroma_db/` |
| OpenAI SDK | `2.36.0` | OpenAI LLM provider adapter | `core/llm/providers/openai_provider.py` |
| Anthropic SDK / HTTP API | `0.100.0` | Declared/installed; current Anthropic provider is mocked and uses `httpx` import | `core/llm/providers/anthropic_provider.py` |
| Ollama HTTP API | `local service, model configured by env` | Local LLM provider | `core/llm/providers/ollama_provider.py` |
| Groq API | `external API; package not required` | Cloud/free-tier LLM provider via aiohttp | `core/llm/providers/groq_provider.py` |
| aiohttp | `3.13.5` | Async HTTP client for Ollama/Groq and test script | `core/llm/providers/ollama_provider.py`, `core/llm/providers/groq_provider.py`, `test_ollama.py` |
| httpx | `0.28.1` | Imported by Anthropic provider | `core/llm/providers/anthropic_provider.py` |
| bcrypt | `5.0.0` | Password hashing and verification | `api/auth.py` |
| python-jose | `3.5.0` | JWT encode/decode | `api/auth.py` |
| python-multipart | `0.0.27` | FastAPI form/file upload support dependency | `pyproject.toml` |
| Redis | `7.4.0` | Declared production dependency and Docker service for Celery broker | `docker-compose.yml`, `core/distributed/celery_app.py` |
| Celery | `5.6.3` | Distributed worker task queue | `core/distributed/celery_app.py`, `core/distributed/tasks.py`, `docker-compose.yml` |
| Flower | `Docker image `mher/flower`` | Celery monitoring UI | `docker-compose.yml` |
| PyGithub | `2.9.1` | GitHub automation dependency; standalone implementation is partial | `requirements_v3.txt`, `tools/implementations/github_tool.py` |
| Playwright | `1.59.0` | Browser automation dependency; standalone implementation is partial | `requirements_v3.txt`, `tools/implementations/browser_tool.py` |
| python-dotenv | `1.2.2` | Loads `.env` at startup | `config/settings.py` |
| HTML/CSS/JavaScript | `browser-native` | Dashboard, landing page, auth pages | `dashboard/templates/*`, `dashboard/static/*` |
| Alpine.js | `CDN `3.x.x`` | Reactive dashboard controller | `dashboard/templates/dashboard.html`, `dashboard/static/js/app.js` |
| marked.js | `CDN latest from `marked/marked.min.js`` | Markdown rendering in dashboard if needed | `dashboard/templates/dashboard.html` |
| Three.js | `CDN r128` | Landing hero particle network | `dashboard/static/js/hero3d.js` |
| Docker Compose | `file format 3.8` | Local multi-service orchestration | `docker-compose.yml` |
| Render | `free web service config` | Backend deployment | `render.yaml` |
| Vercel | `static/proxy config` | Frontend deployment attempt | `vercel.json` |
| Kubernetes | `apps/v1 Deployment` | Production deployment sketch | `deployment/kubernetes/deployment.yaml` |
| Nginx | `reverse proxy config` | Load balancing and WebSocket proxying sketch | `deployment/nginx/nginx.conf` |
| Terraform | `AWS provider sketch` | EKS infrastructure sketch | `deployment/terraform/main.tf` |
| pytest | `9.0.3` | Test runner; no tests currently collected | `Makefile`, `tests/` |
| ruff | `0.15.12` | Declared dev linter | `pyproject.toml` |

## 3. Complete File Structure

```text
.
├── .DS_Store
├── .env
├── .env.example
├── .file_inventory.txt
├── .pytest_cache/
    └── .gitignore
    └── CACHEDIR.TAG
    └── README.md
    └── v/
        └── cache/
            └── nodeids
├── .section5_generated.md
├── Makefile
├── README.md
├── __init__.py
├── __pycache__/
    └── __init__.cpython-314.pyc
    └── run_flagships_v2.cpython-314.pyc
├── agents/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
    └── analytics_agent/
        └── __init__.py
        └── agent.py
    └── base_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── base.cpython-314.pyc
        └── base.py
    └── ceo_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
            └── system_prompt.cpython-314.pyc
        └── agent.py
        └── system_prompt.py
    └── finance_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
            └── system_prompt.cpython-314.pyc
        └── agent.py
        └── system_prompt.py
    └── hr_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
        └── agent.py
    └── infrastructure_agent/
        └── __pycache__/
            └── agent.cpython-314.pyc
        └── agent.py
    └── legal_agent/
        └── __init__.py
        └── agent.py
    └── marketing_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
            └── system_prompt.cpython-314.pyc
        └── agent.py
        └── system_prompt.py
    └── operations_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
        └── agent.py
    └── product_strategy_agent/
    └── production_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
        └── agent.py
    └── research_agent/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent.cpython-314.pyc
            └── system_prompt.cpython-314.pyc
        └── agent.py
        └── system_prompt.py
    └── security_agent/
        └── __pycache__/
            └── agent.cpython-314.pyc
        └── agent.py
    └── support_agent/
├── api/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── app.cpython-314.pyc
        └── auth.cpython-314.pyc
        └── auth_routes.cpython-314.pyc
        └── webhooks.cpython-314.pyc
        └── websocket.cpython-314.pyc
    └── app.py
    └── auth.py
    └── auth_routes.py
    └── webhooks.py
    └── websocket.py
├── automation/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── autonomous_engine.cpython-314.pyc
    └── autonomous_engine.py
├── build_report_workflow.py
├── cli/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── main.cpython-314.pyc
    └── main.py
├── config/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── settings.cpython-314.pyc
    └── settings.py
├── core/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
    └── adaptation/
        └── behavior_optimizer.py
        └── feedback_processor.py
        └── learning_engine.py
        └── strategy_evaluator.py
        └── workflow_optimizer.py
    └── approval/
        └── approval_engine.py
        └── escalation_manager.py
        └── human_review.py
        └── risk_analyzer.py
    └── communication/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── message_bus.cpython-314.pyc
        └── message_bus.py
    └── distributed/
        └── __init__.py
        └── celery_app.py
        └── tasks.py
    └── events/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── event_bus.cpython-314.pyc
            └── event_types.cpython-314.pyc
        └── event_bus.py
        └── event_types.py
    └── goals/
        └── __init__.py
        └── goal_engine.py
    └── llm/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── llm_manager.cpython-314.pyc
            └── provider_router.cpython-314.pyc
            └── reasoning_engine.cpython-314.pyc
            └── token_tracker.cpython-314.pyc
        └── context_builder.py
        └── llm_manager.py
        └── provider_router.py
        └── providers/
            └── __init__.py
            └── __pycache__/
                └── __init__.cpython-314.pyc
                └── anthropic_provider.cpython-314.pyc
                └── base_provider.cpython-314.pyc
                └── groq_provider.cpython-314.pyc
                └── ollama_provider.cpython-314.pyc
                └── openai_provider.cpython-314.pyc
            └── anthropic_provider.py
            └── base_provider.py
            └── groq_provider.py
            └── ollama_provider.py
            └── openai_provider.py
        └── reasoning_engine.py
        └── token_tracker.py
    └── memory/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── memory_manager.cpython-314.pyc
            └── vector_memory.cpython-314.pyc
        └── advanced/
            └── long_term_knowledge.py
            └── memory_ranker.py
            └── memory_summarizer.py
            └── organizational_brain.py
            └── semantic_learning.py
        └── memory_manager.py
        └── vector_memory.py
    └── multimodal/
        └── document_parser.py
        └── multimodal_router.py
        └── screenshot_reasoner.py
        └── vision_engine.py
    └── orchestration/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── agent_registry.cpython-314.pyc
            └── collaboration_engine.cpython-314.pyc
            └── orchestration_manager.cpython-314.pyc
            └── task_router.cpython-314.pyc
        └── agent_registry.py
        └── collaboration_engine.py
        └── orchestration_manager.py
        └── task_router.py
    └── planning/
        └── adaptive_planner.py
        └── dependency_graph.py
        └── execution_forecaster.py
        └── strategic_planner.py
        └── task_decomposer.py
    └── reflection/
        └── reflection_engine.py
    └── state/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── state_manager.cpython-314.pyc
        └── state_manager.py
    └── workflows/
        └── __init__.py
        └── __pycache__/
            └── __init__.cpython-314.pyc
            └── flagship_workflows.cpython-314.pyc
            └── workflow_engine.cpython-314.pyc
        └── flagship_workflows.py
        └── workflow_engine.py
├── dashboard/
    └── __init__.py
    └── static/
        └── assets/
        └── css/
            └── app.css
            └── base.css
            └── dashboard.css
            └── landing.css
            └── theme.css
        └── js/
            └── app.js
            └── auth.js
            └── dashboard.js
            └── hero3d.js
    └── templates/
        └── dashboard.html
        └── landing.html
        └── login.html
        └── logo.html
        └── signup.html
├── data/
    └── outputs/
├── database/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── models.cpython-314.pyc
    └── chroma_db/
        └── 909af621-9653-4797-be07-b16f020b8c87/
            └── data_level0.bin
            └── header.bin
            └── length.bin
            └── link_lists.bin
        └── chroma.sqlite3
    └── mintuu_ecosystem.db
    └── models.py
├── deployment/
    └── kubernetes/
        └── deployment.yaml
    └── nginx/
        └── nginx.conf
    └── production/
    └── terraform/
        └── main.tf
├── docker-compose.yml
├── docs/
├── execution_trace.json
├── generate_architecture.py
├── integrations/
    └── __init__.py
├── logs/
    └── workflow_1_execution.log
├── mintuu_ai_ecosystem.egg-info/
    └── PKG-INFO
    └── SOURCES.txt
    └── dependency_links.txt
    └── entry_points.txt
    └── requires.txt
    └── top_level.txt
├── mintuu_ecosystem.db
├── mintuu_flagship_report.html
├── mintuu_master_doc.md
├── mintuu_master_doc.pdf
├── mintuu_master_doc_final.md
├── mintuu_master_doc_final.pdf
├── monitoring/
    └── orchestration_metrics.py
    └── performance_monitor.py
    └── system_profiler.py
    └── tracing_engine.py
    └── workflow_analytics.py
├── pyproject.toml
├── raw_reasoning_log.txt
├── render.yaml
├── report/
    └── .DS_Store
    └── output/
        └── mintuu_flagship_report.html
        └── mintuu_flagship_report.md
        └── mintuu_flagship_report.pdf
        └── screenshots/
            └── chat_workflow.png
            └── dashboard_bottom.png
            └── dashboard_overview.png
            └── dashboard_top.png
            └── final_state.png
            └── workflow_completed.png
        └── w1_dashboard.png
├── requirements_v3.txt
├── run_flagships.py
├── run_flagships_v2.py
├── test_ollama.py
├── test_reasoning.py
├── test_workflow.py
├── tests/
    └── __init__.py
├── tools/
    └── __init__.py
    └── __pycache__/
        └── __init__.cpython-314.pyc
        └── execution_manager.cpython-314.pyc
        └── tool_registry.cpython-314.pyc
    └── execution_manager.py
    └── implementations/
        └── __init__.py
        └── browser_tool.py
        └── email_tool.py
        └── github_tool.py
    └── tool_registry.py
├── vercel.json
```

### File-by-File Purpose

| File | Purpose |
|---|---|
| `.DS_Store` | macOS Finder metadata file; not part of application logic. |
| `.env` | Local environment file containing API keys and runtime settings; values are intentionally not reproduced in this snapshot. |
| `.env.example` | Template showing expected environment variables for local and deployed environments. |
| `.file_inventory.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `.pytest_cache/.gitignore` | Project file or artifact used by the repository. |
| `.pytest_cache/CACHEDIR.TAG` | Project file or artifact used by the repository. |
| `.pytest_cache/README.md` | Markdown documentation or generated report artifact. |
| `.pytest_cache/v/cache/nodeids` | Project file or artifact used by the repository. |
| `.section5_generated.md` | Markdown documentation or generated report artifact. |
| `Makefile` | Convenience commands for installing, running the dev server, testing, and starting an ngrok tunnel. |
| `README.md` | Top-level project overview, architecture summary, stack notes, and basic run commands. |
| `__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `__pycache__/run_flagships_v2.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/analytics_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/analytics_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/base_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/base_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/base_agent/__pycache__/base.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/base_agent/base.py` | Abstract base class that implements shared agent lifecycle, messaging, tool use, memory use, logging, and task handling. |
| `agents/ceo_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/ceo_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/ceo_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/ceo_agent/__pycache__/system_prompt.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/ceo_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/ceo_agent/system_prompt.py` | Defines the system prompt used by the LLM reasoning layer for that agent. |
| `agents/finance_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/finance_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/finance_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/finance_agent/__pycache__/system_prompt.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/finance_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/finance_agent/system_prompt.py` | Defines the system prompt used by the LLM reasoning layer for that agent. |
| `agents/hr_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/hr_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/hr_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/hr_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/infrastructure_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/infrastructure_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/legal_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/legal_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/marketing_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/marketing_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/marketing_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/marketing_agent/__pycache__/system_prompt.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/marketing_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/marketing_agent/system_prompt.py` | Defines the system prompt used by the LLM reasoning layer for that agent. |
| `agents/operations_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/operations_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/operations_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/operations_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/production_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/production_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/production_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/production_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/research_agent/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `agents/research_agent/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/research_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/research_agent/__pycache__/system_prompt.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/research_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `agents/research_agent/system_prompt.py` | Defines the system prompt used by the LLM reasoning layer for that agent. |
| `agents/security_agent/__pycache__/agent.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `agents/security_agent/agent.py` | Defines a specialized Mintuu agent class, its identity, capabilities, planning logic, execution logic, and result summary behavior. |
| `api/__init__.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `api/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/__pycache__/app.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/__pycache__/auth.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/__pycache__/auth_routes.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/__pycache__/webhooks.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/__pycache__/websocket.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `api/app.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `api/auth.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `api/auth_routes.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `api/webhooks.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `api/websocket.py` | FastAPI API module for pages, REST endpoints, auth routes, webhooks, or WebSocket updates. |
| `automation/__init__.py` | Autonomous recurring task engine and package marker. |
| `automation/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `automation/__pycache__/autonomous_engine.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `automation/autonomous_engine.py` | Autonomous recurring task engine and package marker. |
| `build_report_workflow.py` | Python source module for project logic, scripts, tests, or utilities. |
| `cli/__init__.py` | Command-line package module and entry point placeholder for the mintuu console script. |
| `cli/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `cli/__pycache__/main.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `cli/main.py` | Command-line package module and entry point placeholder for the mintuu console script. |
| `config/__init__.py` | Centralized application settings loaded from environment variables and defaults. |
| `config/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `config/__pycache__/settings.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `config/settings.py` | Centralized application settings loaded from environment variables and defaults. |
| `core/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `core/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/adaptation/behavior_optimizer.py` | Placeholder or early-stage adaptation/learning component for future optimization features. |
| `core/adaptation/feedback_processor.py` | Placeholder or early-stage adaptation/learning component for future optimization features. |
| `core/adaptation/learning_engine.py` | Placeholder or early-stage adaptation/learning component for future optimization features. |
| `core/adaptation/strategy_evaluator.py` | Placeholder or early-stage adaptation/learning component for future optimization features. |
| `core/adaptation/workflow_optimizer.py` | Placeholder or early-stage adaptation/learning component for future optimization features. |
| `core/approval/approval_engine.py` | Approval, escalation, human review, or risk-analysis component, currently mostly skeletal. |
| `core/approval/escalation_manager.py` | Approval, escalation, human review, or risk-analysis component, currently mostly skeletal. |
| `core/approval/human_review.py` | Approval, escalation, human review, or risk-analysis component, currently mostly skeletal. |
| `core/approval/risk_analyzer.py` | Approval, escalation, human review, or risk-analysis component, currently mostly skeletal. |
| `core/communication/__init__.py` | Message bus implementation for agent-to-agent and orchestrator-to-agent communication. |
| `core/communication/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/communication/__pycache__/message_bus.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/communication/message_bus.py` | Message bus implementation for agent-to-agent and orchestrator-to-agent communication. |
| `core/distributed/__init__.py` | Celery distributed execution configuration and background task definitions. |
| `core/distributed/celery_app.py` | Celery distributed execution configuration and background task definitions. |
| `core/distributed/tasks.py` | Celery distributed execution configuration and background task definitions. |
| `core/events/__init__.py` | Async event bus and event type definitions used by webhook/event-driven flows. |
| `core/events/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/events/__pycache__/event_bus.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/events/__pycache__/event_types.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/events/event_bus.py` | Async event bus and event type definitions used by webhook/event-driven flows. |
| `core/events/event_types.py` | Async event bus and event type definitions used by webhook/event-driven flows. |
| `core/goals/__init__.py` | Goal engine stub for future long-running autonomous goal execution. |
| `core/goals/goal_engine.py` | Goal engine stub for future long-running autonomous goal execution. |
| `core/llm/__init__.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/llm/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/__pycache__/llm_manager.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/__pycache__/provider_router.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/__pycache__/reasoning_engine.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/__pycache__/token_tracker.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/context_builder.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/llm/llm_manager.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/llm/provider_router.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/llm/providers/__init__.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/providers/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/__pycache__/anthropic_provider.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/__pycache__/base_provider.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/__pycache__/groq_provider.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/__pycache__/ollama_provider.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/__pycache__/openai_provider.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/llm/providers/anthropic_provider.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/providers/base_provider.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/providers/groq_provider.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/providers/ollama_provider.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/providers/openai_provider.py` | LLM provider adapter implementing or stubbing provider-specific generation calls. |
| `core/llm/reasoning_engine.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/llm/token_tracker.py` | LLM routing, response generation, reasoning prompt construction, and token tracking logic. |
| `core/memory/__init__.py` | Memory manager or vector memory implementation backed by SQLite and ChromaDB. |
| `core/memory/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/memory/__pycache__/memory_manager.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/memory/__pycache__/vector_memory.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/memory/advanced/long_term_knowledge.py` | Placeholder or early-stage advanced memory component for future ranking, summarization, semantic learning, or organizational brain features. |
| `core/memory/advanced/memory_ranker.py` | Placeholder or early-stage advanced memory component for future ranking, summarization, semantic learning, or organizational brain features. |
| `core/memory/advanced/memory_summarizer.py` | Placeholder or early-stage advanced memory component for future ranking, summarization, semantic learning, or organizational brain features. |
| `core/memory/advanced/organizational_brain.py` | Placeholder or early-stage advanced memory component for future ranking, summarization, semantic learning, or organizational brain features. |
| `core/memory/advanced/semantic_learning.py` | Placeholder or early-stage advanced memory component for future ranking, summarization, semantic learning, or organizational brain features. |
| `core/memory/memory_manager.py` | Memory manager or vector memory implementation backed by SQLite and ChromaDB. |
| `core/memory/vector_memory.py` | Memory manager or vector memory implementation backed by SQLite and ChromaDB. |
| `core/multimodal/document_parser.py` | Placeholder multimodal component for document, screenshot, and vision routing features. |
| `core/multimodal/multimodal_router.py` | Placeholder multimodal component for document, screenshot, and vision routing features. |
| `core/multimodal/screenshot_reasoner.py` | Placeholder multimodal component for document, screenshot, and vision routing features. |
| `core/multimodal/vision_engine.py` | Placeholder multimodal component for document, screenshot, and vision routing features. |
| `core/orchestration/__init__.py` | Core orchestration layer for agents, routing, workflows, collaboration, and system status. |
| `core/orchestration/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/orchestration/__pycache__/agent_registry.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/orchestration/__pycache__/collaboration_engine.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/orchestration/__pycache__/orchestration_manager.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/orchestration/__pycache__/task_router.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/orchestration/agent_registry.py` | Core orchestration layer for agents, routing, workflows, collaboration, and system status. |
| `core/orchestration/collaboration_engine.py` | Core orchestration layer for agents, routing, workflows, collaboration, and system status. |
| `core/orchestration/orchestration_manager.py` | Core orchestration layer for agents, routing, workflows, collaboration, and system status. |
| `core/orchestration/task_router.py` | Core orchestration layer for agents, routing, workflows, collaboration, and system status. |
| `core/planning/adaptive_planner.py` | Planning-related placeholder or helper component for task decomposition, dependencies, forecasting, and strategy. |
| `core/planning/dependency_graph.py` | Planning-related placeholder or helper component for task decomposition, dependencies, forecasting, and strategy. |
| `core/planning/execution_forecaster.py` | Planning-related placeholder or helper component for task decomposition, dependencies, forecasting, and strategy. |
| `core/planning/strategic_planner.py` | Planning-related placeholder or helper component for task decomposition, dependencies, forecasting, and strategy. |
| `core/planning/task_decomposer.py` | Planning-related placeholder or helper component for task decomposition, dependencies, forecasting, and strategy. |
| `core/reflection/reflection_engine.py` | Reflection/cross-agent critique engine using the LLM manager. |
| `core/state/__init__.py` | In-memory state manager for agent status, workflow status, system health, and checkpoints. |
| `core/state/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/state/__pycache__/state_manager.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/state/state_manager.py` | In-memory state manager for agent status, workflow status, system health, and checkpoints. |
| `core/workflows/__init__.py` | Workflow engine and predefined flagship workflow step definitions. |
| `core/workflows/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/workflows/__pycache__/flagship_workflows.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/workflows/__pycache__/workflow_engine.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `core/workflows/flagship_workflows.py` | Workflow engine and predefined flagship workflow step definitions. |
| `core/workflows/workflow_engine.py` | Workflow engine and predefined flagship workflow step definitions. |
| `dashboard/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `dashboard/static/css/app.css` | CSS stylesheet for shared theme variables, base layout, landing page, dashboard, or app screens. |
| `dashboard/static/css/base.css` | CSS stylesheet for shared theme variables, base layout, landing page, dashboard, or app screens. |
| `dashboard/static/css/dashboard.css` | CSS stylesheet for shared theme variables, base layout, landing page, dashboard, or app screens. |
| `dashboard/static/css/landing.css` | CSS stylesheet for shared theme variables, base layout, landing page, dashboard, or app screens. |
| `dashboard/static/css/theme.css` | CSS stylesheet for shared theme variables, base layout, landing page, dashboard, or app screens. |
| `dashboard/static/js/app.js` | Browser-side JavaScript for auth, dashboard/app state, WebSocket updates, chat, onboarding, or hero animation. |
| `dashboard/static/js/auth.js` | Browser-side JavaScript for auth, dashboard/app state, WebSocket updates, chat, onboarding, or hero animation. |
| `dashboard/static/js/dashboard.js` | Browser-side JavaScript for auth, dashboard/app state, WebSocket updates, chat, onboarding, or hero animation. |
| `dashboard/static/js/hero3d.js` | Browser-side JavaScript for auth, dashboard/app state, WebSocket updates, chat, onboarding, or hero animation. |
| `dashboard/templates/dashboard.html` | HTML template served by FastAPI for a public page, auth page, dashboard, or logo. |
| `dashboard/templates/landing.html` | HTML template served by FastAPI for a public page, auth page, dashboard, or logo. |
| `dashboard/templates/login.html` | HTML template served by FastAPI for a public page, auth page, dashboard, or logo. |
| `dashboard/templates/logo.html` | HTML template served by FastAPI for a public page, auth page, dashboard, or logo. |
| `dashboard/templates/signup.html` | HTML template served by FastAPI for a public page, auth page, dashboard, or logo. |
| `database/__init__.py` | Python source module for project logic, scripts, tests, or utilities. |
| `database/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `database/__pycache__/models.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/data_level0.bin` | ChromaDB persistent vector-store storage file. |
| `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/header.bin` | ChromaDB persistent vector-store storage file. |
| `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/length.bin` | ChromaDB persistent vector-store storage file. |
| `database/chroma_db/909af621-9653-4797-be07-b16f020b8c87/link_lists.bin` | ChromaDB persistent vector-store storage file. |
| `database/chroma_db/chroma.sqlite3` | ChromaDB persistent vector-store storage file. |
| `database/mintuu_ecosystem.db` | SQLite database file containing project runtime state and/or ChromaDB metadata. |
| `database/models.py` | SQLite schema and DatabaseManager CRUD/logging/statistics operations. |
| `deployment/kubernetes/deployment.yaml` | Kubernetes deployment manifest for the orchestrator service. |
| `deployment/nginx/nginx.conf` | Nginx reverse proxy/load-balancing configuration with WebSocket headers. |
| `deployment/terraform/main.tf` | Terraform AWS/EKS infrastructure sketch. |
| `docker-compose.yml` | Docker Compose definition for API, Celery worker, Redis, and Flower monitoring. |
| `execution_trace.json` | JSON trace/configuration artifact. |
| `generate_architecture.py` | Python source module for project logic, scripts, tests, or utilities. |
| `integrations/__init__.py` | Integration package marker; no concrete integration code currently lives here. |
| `logs/workflow_1_execution.log` | Execution log artifact from prior workflow runs. |
| `mintuu_ai_ecosystem.egg-info/PKG-INFO` | Project file or artifact used by the repository. |
| `mintuu_ai_ecosystem.egg-info/SOURCES.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `mintuu_ai_ecosystem.egg-info/dependency_links.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `mintuu_ai_ecosystem.egg-info/entry_points.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `mintuu_ai_ecosystem.egg-info/requires.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `mintuu_ai_ecosystem.egg-info/top_level.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `mintuu_ecosystem.db` | SQLite database file containing project runtime state and/or ChromaDB metadata. |
| `mintuu_flagship_report.html` | Generated or served HTML report/page artifact. |
| `mintuu_master_doc.md` | Markdown documentation or generated report artifact. |
| `mintuu_master_doc.pdf` | Generated PDF documentation or report artifact. |
| `mintuu_master_doc_final.md` | Markdown documentation or generated report artifact. |
| `mintuu_master_doc_final.pdf` | Generated PDF documentation or report artifact. |
| `monitoring/orchestration_metrics.py` | Monitoring/profiling/analytics/tracing module for system or workflow telemetry. |
| `monitoring/performance_monitor.py` | Monitoring/profiling/analytics/tracing module for system or workflow telemetry. |
| `monitoring/system_profiler.py` | Monitoring/profiling/analytics/tracing module for system or workflow telemetry. |
| `monitoring/tracing_engine.py` | Monitoring/profiling/analytics/tracing module for system or workflow telemetry. |
| `monitoring/workflow_analytics.py` | Monitoring/profiling/analytics/tracing module for system or workflow telemetry. |
| `pyproject.toml` | Python package metadata, direct dependencies, optional dependency groups, entry point, and Ruff settings. |
| `raw_reasoning_log.txt` | Plain text inventory, generated section, or raw reasoning log artifact. |
| `render.yaml` | Render free-tier backend deployment configuration. |
| `report/.DS_Store` | macOS Finder metadata file; not part of application logic. |
| `report/output/mintuu_flagship_report.html` | Generated flagship report output artifact in HTML, Markdown, PDF, or image form. |
| `report/output/mintuu_flagship_report.md` | Generated flagship report output artifact in HTML, Markdown, PDF, or image form. |
| `report/output/mintuu_flagship_report.pdf` | Generated flagship report output artifact in HTML, Markdown, PDF, or image form. |
| `report/output/screenshots/chat_workflow.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/screenshots/dashboard_bottom.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/screenshots/dashboard_overview.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/screenshots/dashboard_top.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/screenshots/final_state.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/screenshots/workflow_completed.png` | Generated screenshot artifact from prior report/dashboard validation. |
| `report/output/w1_dashboard.png` | Generated flagship report output artifact in HTML, Markdown, PDF, or image form. |
| `requirements_v3.txt` | Additional v3 AI, vector-memory, distributed-worker, and automation dependencies not all present in pyproject dependencies. |
| `run_flagships.py` | Python source module for project logic, scripts, tests, or utilities. |
| `run_flagships_v2.py` | Python source module for project logic, scripts, tests, or utilities. |
| `test_ollama.py` | Python source module for project logic, scripts, tests, or utilities. |
| `test_reasoning.py` | Python source module for project logic, scripts, tests, or utilities. |
| `test_workflow.py` | Python source module for project logic, scripts, tests, or utilities. |
| `tests/__init__.py` | Pytest package marker; no test modules are currently present. |
| `tools/__init__.py` | Tool registry or execution manager used by agents to access file, terminal, reporting, metrics, calendar, email, git, and utility tools. |
| `tools/__pycache__/__init__.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `tools/__pycache__/execution_manager.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `tools/__pycache__/tool_registry.cpython-314.pyc` | Python bytecode cache generated from a source module; not source of truth. |
| `tools/execution_manager.py` | Tool registry or execution manager used by agents to access file, terminal, reporting, metrics, calendar, email, git, and utility tools. |
| `tools/implementations/__init__.py` | Standalone implementation for browser, email, or GitHub tool integration. |
| `tools/implementations/browser_tool.py` | Standalone implementation for browser, email, or GitHub tool integration. |
| `tools/implementations/email_tool.py` | Standalone implementation for browser, email, or GitHub tool integration. |
| `tools/implementations/github_tool.py` | Standalone implementation for browser, email, or GitHub tool integration. |
| `tools/tool_registry.py` | Tool registry or execution manager used by agents to access file, terminal, reporting, metrics, calendar, email, git, and utility tools. |
| `vercel.json` | Vercel frontend/static routing configuration that proxies API/auth/ws to the Render backend. |

## 4. Current Working State

| Area | Status | Evidence / Reason |
|---|---|---|
| FastAPI server | Working | Started successfully with `PYTHONPATH=/Users/mridulsoliwal/Documents/All_Projects/AI_Agents python3 -m uvicorn api.app:app --host 127.0.0.1 --port 8000`; `/api/v1/status` returned healthy runtime state. |
| Landing page | Working | `GET /` returns `dashboard/templates/landing.html`. |
| Auth pages | Working | `GET /login` and `GET /signup` serve HTML; client-side `auth.js` calls `/auth/login` and `/auth/signup`. |
| Dashboard shell | Working with auth dependency | `GET /app` serves HTML, but browser JS redirects to `/login` if no local access token exists. |
| REST API | Working | OpenAPI exposes all core routes; `/api/v1/status`, `/api/v1/tools`, `/api/v1/agents`, `/api/v1/memory`, `/api/v1/analytics` were probed. |
| WebSocket endpoint | Working/partial | `/ws` accepts clients and pushes state every 2 seconds when clients are connected; client-to-server messages are only logged. |
| SQLite persistence | Working | `database/mintuu_ecosystem.db` has tables, indexes, and real rows: {'agent_logs': 389, 'conversations': 18, 'events': 154, 'memories': 762, 'messages': 54, 'tasks': 326, 'tool_executions': 0, 'users': 1, 'workflow_states': 0, 'workflows': 15}. |
| Agent registry | Working | Runtime has 9 active registered agents: CEO, HR, Marketing, Finance, Production, Operations, Research, Security, Infrastructure. |
| Analytics and Legal source agents | Partial/stubbed | `agents/analytics_agent/agent.py` and `agents/legal_agent/agent.py` exist but are not instantiated in `OrchestrationManager._init_agents`. |
| Product Strategy and Support agent folders | Stubbed/broken-empty | Folders exist with no source files. |
| Agent execution | Working with simulated domain logic | Agents return structured outputs from deterministic Python logic; BaseAgent wraps planning/execution/memory/logging. |
| LLM reasoning | Partial/simulated depending provider | Provider router chooses env provider; current `.env` has `ANTHROPIC_API_KEY`, so router selected Anthropic during startup, but `AnthropicProvider.generate()` returns mocked canned JSON and does not call the real API. Ollama/OpenAI/Groq paths are real adapters if configured. |
| System prompts | Partial | CEO and Research use `SYSTEM_PROMPT`. Finance and Marketing define `FINANCE_SYSTEM_PROMPT` and `MARKETING_SYSTEM_PROMPT`, but dynamic import looks for `SYSTEM_PROMPT`, so those prompts are not actually used by BaseAgent without renaming or fallback logic. |
| ChromaDB vector memory | Working/partial | Persistent Chroma initializes; `org_knowledge` has 111 vectors. `workflows`, `decisions`, and `agent_memory` collections are created but empty. |
| Workflow engine | Working | 15 completed workflows exist in SQLite; dynamic workflow engine supports dependencies, auto approval, state changes, retries, completion history. |
| Approval gates | Stubbed/simulated | `_handle_approval()` always returns True and auto-approves via CEO collaboration response. |
| Autonomous engine | Working but stopped by default | Default scheduled tasks exist; status reports `is_running: false` unless `/api/v1/autonomous/start` is called. |
| Tool registry | Working but security-light | 11 tools registered; permissions default to EXECUTE, so READ/WRITE tools fail unless permissions are granted. Terminal tool uses `shell=True`, which is risky. |
| GitHub webhook | Partial | Endpoint accepts GitHub webhook JSON and triggers issue workflow, but no signature verification and event bus is an in-memory singleton. |
| Celery/Redis distributed layer | Partial/configured | Compose includes Redis/worker/Flower; Celery modules exist, but main API execution path is synchronous in-process. |
| Docker Compose | Partial/broken unless Dockerfile exists elsewhere | `docker-compose.yml` uses `build: .`, but no `Dockerfile` is present in this repo tree. |
| Render deployment | Partial | `render.yaml` exists; start command likely needs correct `PYTHONPATH`; free tier has sleep/persistence limitations. |
| Vercel deployment | Partial | `vercel.json` rewrites static routes to `/templates/$1.html`, but the actual root is `dashboard/templates`; WebSocket rewrite uses HTTPS destination rather than WSS semantics. |
| Tests | Broken/incomplete | `python3 -m pytest tests/ -v` collected 0 tests and exited code 5. Test scripts exist at root but are not pytest modules in `tests/`. |
| Local import ergonomics | Partial | Running `python3 -m uvicorn api.app:app` from repo root failed until `PYTHONPATH=/Users/mridulsoliwal/Documents/All_Projects/AI_Agents` was set. |

## 5. All APIs and Endpoints

| Method | URL | What it does | Parameters | Returns |
|---|---|---|---|---|
| GET | `/` | Serves landing page | none | HTML `landing.html` |
| GET | `/login` | Serves login page | none | HTML `login.html` |
| GET | `/signup` | Serves signup page | none | HTML `signup.html` |
| GET | `/app` | Serves authenticated dashboard shell | none server-side; client checks local token | HTML `dashboard.html` |
| POST | `/auth/signup` | Creates user and tokens | JSON: email, password, confirm_password, full_name | access token, refresh token, user |
| POST | `/auth/login` | Authenticates user | JSON: email, password | access token, refresh token, user |
| POST | `/auth/refresh` | Refreshes access token | Authorization: Bearer refresh_token | access_token, token_type |
| GET | `/auth/me` | Gets current profile | Authorization: Bearer access_token | profile object |
| PUT | `/auth/me` | Updates profile | Authorization plus JSON full_name/theme_preference | status updated |
| POST | `/auth/onboarding/complete` | Marks onboarding complete | Authorization | status |
| POST | `/auth/data/clear` | Deletes user conversations and scoped memories | Authorization | status |
| GET | `/auth/data/export` | Exports user profile/conversations/workflows | Authorization | JSON export |
| POST | `/api/v1/chat` | Main chat endpoint; routes to task or workflow | JSON: message, optional conversation_id, user_id | conversation_id, response, result, timestamp |
| POST | `/api/v1/execute` | Executes a single task | JSON: description, optional agent_type, priority | agent task result |
| GET | `/api/v1/tasks` | Lists tasks from SQLite | query status, limit | array of task rows |
| POST | `/api/v1/workflows` | Creates and executes explicit workflow | JSON: name, description, steps[] | workflow result |
| POST | `/api/v1/workflows/auto` | Creates agent order from router and executes workflow | JSON: description | workflow result |
| GET | `/api/v1/workflows` | Lists active and recent in-memory workflows | none | array |
| GET | `/api/v1/workflows/{workflow_id}` | Gets active in-memory or DB workflow | path workflow_id | workflow object/row |
| GET | `/api/v1/agents` | Lists registered agents | none | array of agent info |
| GET | `/api/v1/agents/{agent_type}` | Gets one agent by type | path agent_type | agent info |
| GET | `/api/v1/collaboration` | Gets collaboration feed | query limit | active requests, history, stats, message history |
| GET | `/api/v1/collaboration/messages` | Gets message bus history | query limit | array of messages |
| GET | `/api/v1/autonomous` | Gets autonomous engine status | none | tasks and running state |
| GET | `/api/v1/autonomous/events` | Gets autonomous execution events | query limit | array |
| POST | `/api/v1/autonomous/tasks` | Registers scheduled task | JSON: name, agent_type, description, interval_seconds | task_id, status |
| POST | `/api/v1/autonomous/{task_id}/trigger` | Runs scheduled task immediately | path task_id | event object or 404 |
| POST | `/api/v1/autonomous/start` | Starts recurring scheduler thread | none | status |
| POST | `/api/v1/autonomous/stop` | Stops recurring scheduler thread | none | status |
| GET | `/api/v1/status` | Full system status | none | ecosystem, agents, state, tools, memory, db stats, workflows, autonomous |
| GET | `/api/v1/logs` | Recent agent logs | query limit | array of agent_logs |
| GET | `/api/v1/events` | Recent system events | query limit | array of events |
| GET | `/api/v1/tools` | Lists registered tools | none | array of tool metadata |
| GET | `/api/v1/memory` | Memory cache stats | none | cache stats |
| GET | `/api/v1/analytics` | SQLite aggregate stats | none | counts by task/workflow status etc. |
| POST | `/webhooks/github` | Receives GitHub webhook and triggers issue workflow | JSON GitHub payload plus X-GitHub-Event header | status accepted, event_id |
| WS | `/ws` | Dashboard push stream | WebSocket connection; client messages ignored except logging | JSON events: state_update, collaboration_update, autonomous_update |

## 6. Database Schema

SQLite database path: `database/mintuu_ecosystem.db`.

#### `agent_logs` (389 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `agent_id` | `TEXT` | `True` | `None` | `False` | Agent ID or pseudo-agent namespace such as organization/workflow. |
| `action` | `TEXT` | `True` | `None` | `False` | Agent action name. |
| `input_data` | `TEXT` | `False` | `''` | `False` | Serialized action input. |
| `output_data` | `TEXT` | `False` | `''` | `False` | Serialized action output. |
| `status` | `TEXT` | `False` | `'SUCCESS'` | `False` | Current lifecycle status. |
| `duration_ms` | `INTEGER` | `False` | `0` | `False` | Execution duration in milliseconds. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |

#### `conversations` (18 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `user_id` | `TEXT` | `True` | `'default'` | `False` | Owning user identifier. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |
| `updated_at` | `TEXT` | `True` | `None` | `False` | UTC update timestamp. |

#### `events` (154 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `event_type` | `TEXT` | `True` | `None` | `False` | System event type. |
| `source` | `TEXT` | `True` | `None` | `False` | Event source. |
| `description` | `TEXT` | `True` | `None` | `False` | Human-readable work description. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |

#### `memories` (762 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `agent_id` | `TEXT` | `True` | `None` | `False` | Agent ID or pseudo-agent namespace such as organization/workflow. |
| `memory_type` | `TEXT` | `True` | `None` | `False` | Memory tier enum. |
| `key` | `TEXT` | `True` | `None` | `False` | Lookup key for memory item. |
| `content` | `TEXT` | `True` | `None` | `False` | Message or memory content. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `importance` | `REAL` | `False` | `0.5` | `False` | Memory importance score. |
| `access_count` | `INTEGER` | `False` | `0` | `False` | Number of times memory was accessed. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |
| `updated_at` | `TEXT` | `True` | `None` | `False` | UTC update timestamp. |
| `expires_at` | `TEXT` | `False` | `None` | `False` | Expiration timestamp for TTL memories. |

#### `messages` (54 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `conversation_id` | `TEXT` | `True` | `None` | `False` | Parent conversation ID. |
| `role` | `TEXT` | `True` | `None` | `False` | Message role, constrained to user/assistant/system/agent. |
| `content` | `TEXT` | `True` | `None` | `False` | Message or memory content. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |

#### `tasks` (326 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `title` | `TEXT` | `True` | `None` | `False` | Task or document title. |
| `description` | `TEXT` | `True` | `None` | `False` | Human-readable work description. |
| `status` | `TEXT` | `True` | `'PENDING'` | `False` | Current lifecycle status. |
| `assigned_agent` | `TEXT` | `True` | `None` | `False` | Agent ID assigned to execute the task. |
| `workflow_id` | `TEXT` | `False` | `None` | `False` | Related workflow ID. |
| `priority` | `INTEGER` | `False` | `5` | `False` | Task priority from low to high. |
| `dependencies` | `TEXT` | `False` | `'[]'` | `False` | JSON list of task/step dependencies. |
| `result` | `TEXT` | `False` | `None` | `False` | Serialized execution result. |
| `error_message` | `TEXT` | `False` | `None` | `False` | Failure reason if task failed. |
| `retry_count` | `INTEGER` | `False` | `0` | `False` | Retry counter. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |
| `updated_at` | `TEXT` | `True` | `None` | `False` | UTC update timestamp. |
| `started_at` | `TEXT` | `False` | `None` | `False` | UTC start timestamp. |
| `completed_at` | `TEXT` | `False` | `None` | `False` | UTC completion timestamp. |

#### `tool_executions` (0 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `agent_id` | `TEXT` | `True` | `None` | `False` | Agent ID or pseudo-agent namespace such as organization/workflow. |
| `tool_name` | `TEXT` | `True` | `None` | `False` | Executed tool name. |
| `input_params` | `TEXT` | `False` | `'{}'` | `False` | Serialized tool input parameters. |
| `output_data` | `TEXT` | `False` | `''` | `False` | Serialized action output. |
| `status` | `TEXT` | `False` | `'SUCCESS'` | `False` | Current lifecycle status. |
| `duration_ms` | `INTEGER` | `False` | `0` | `False` | Execution duration in milliseconds. |
| `error` | `TEXT` | `False` | `None` | `False` | Tool execution error. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |

#### `users` (1 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `email` | `TEXT` | `True` | `None` | `False` | User email. |
| `password_hash` | `TEXT` | `True` | `None` | `False` | bcrypt password hash. |
| `full_name` | `TEXT` | `True` | `None` | `False` | User display name. |
| `is_verified` | `INTEGER` | `False` | `0` | `False` | Boolean-ish integer verification flag. |
| `onboarding_complete` | `INTEGER` | `False` | `0` | `False` | Boolean-ish integer onboarding flag. |
| `theme_preference` | `TEXT` | `False` | `'dark'` | `False` | User UI theme preference. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |
| `updated_at` | `TEXT` | `True` | `None` | `False` | UTC update timestamp. |

#### `workflow_states` (0 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `workflow_id` | `TEXT` | `True` | `None` | `False` | Related workflow ID. |
| `step_index` | `INTEGER` | `True` | `None` | `False` | Workflow step index for state snapshots. |
| `state_data` | `TEXT` | `True` | `'{}'` | `False` | Serialized workflow state snapshot. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |

#### `workflows` (15 rows)
| Column | Type | Required | Default | Primary Key | Meaning |
|---|---:|---:|---|---:|---|
| `id` | `TEXT` | `False` | `None` | `True` | Unique row identifier. |
| `name` | `TEXT` | `True` | `None` | `False` | Workflow/user/tool name depending on table. |
| `description` | `TEXT` | `True` | `None` | `False` | Human-readable work description. |
| `status` | `TEXT` | `True` | `'PENDING'` | `False` | Current lifecycle status. |
| `steps` | `TEXT` | `True` | `'[]'` | `False` | Serialized workflow step definitions. |
| `current_step` | `INTEGER` | `False` | `0` | `False` | Current workflow step index. |
| `total_steps` | `INTEGER` | `False` | `0` | `False` | Total workflow step count. |
| `result` | `TEXT` | `False` | `None` | `False` | Serialized execution result. |
| `initiated_by` | `TEXT` | `False` | `'mintuu'` | `False` | User/system that initiated a workflow. |
| `metadata` | `TEXT` | `False` | `'{}'` | `False` | JSON metadata blob. |
| `created_at` | `TEXT` | `True` | `None` | `False` | UTC creation timestamp. |
| `updated_at` | `TEXT` | `True` | `None` | `False` | UTC update timestamp. |
| `started_at` | `TEXT` | `False` | `None` | `False` | UTC start timestamp. |
| `completed_at` | `TEXT` | `False` | `None` | `False` | UTC completion timestamp. |


### Relationships

| Relationship | Type | Defined by |
|---|---|---|
| `messages.conversation_id -> conversations.id` | Many messages per conversation | SQLite foreign key with cascade delete. |
| `tasks.workflow_id -> workflows.id` | Many tasks may belong to one workflow | SQLite foreign key with `ON DELETE SET NULL`. |
| `workflow_states.workflow_id -> workflows.id` | Many state snapshots per workflow | SQLite foreign key with cascade delete. |
| `memories.agent_id` | Logical relationship to agents, `organization`, or `workflow:<id>` | Not enforced by foreign key. |
| `agent_logs.agent_id` | Logical relationship to agents | Not enforced by foreign key. |
| `tool_executions.agent_id` | Logical relationship to agents | Not enforced by foreign key. |

### Current SQLite Contents

| Table | Row count |
|---|---:|
| `agent_logs` | 389 |
| `conversations` | 18 |
| `events` | 154 |
| `memories` | 762 |
| `messages` | 54 |
| `tasks` | 326 |
| `tool_executions` | 0 |
| `users` | 1 |
| `workflow_states` | 0 |
| `workflows` | 15 |

Recent workflow samples:

| ID | Name | Status | Current Step | Total Steps | Created At | Description |
|---|---|---|---:|---:|---|---|
| `56290520-72d7-481b-82d6-997dfcde5f3f` | Auto-Workflow: launh a new product with q3 | COMPLETED | 5 | 0 | 2026-05-27T19:13:23.464102+00:00 | launh a new product with q3 |
| `57ac8a21-16a0-4857-a1a6-7a6a912b9515` | Auto-Workflow: Launch a new product by Q3 with a $50k budget | COMPLETED | 5 | 0 | 2026-05-27T18:59:34.075147+00:00 | Launch a new product by Q3 with a $50k budget |
| `079a8d35-626e-4e40-9b86-b06ecfffff6e` | Auto-Workflow: Launch a new product by Q3 with a $50k budget | COMPLETED | 5 | 0 | 2026-05-24T10:46:44.938844+00:00 | Launch a new product by Q3 with a $50k budget |
| `8c57d6ba-afad-4cf8-99cc-e9f440ee572a` | Auto-Workflow: Run a system health check across all agents | COMPLETED | 5 | 0 | 2026-05-22T07:45:43.712154+00:00 | Run a system health check across all agents |
| `0c459a6e-8e67-4b0f-9cfd-844fc4fdcf1c` | Auto-Workflow: Run a system health check across all agents | COMPLETED | 5 | 0 | 2026-05-22T07:07:08.163408+00:00 | Run a system health check across all agents |
| `3ce636be-291b-4f69-a8e1-ebf9aaed6392` | Auto-Workflow: Run a comprehensive budget review | COMPLETED | 0 | 0 | 2026-05-22T07:06:34.861038+00:00 | Run a comprehensive budget review |
| `05763404-05fa-49c8-b85a-72c1814e9bce` | Auto-Workflow: Analyze our company KPIs and financial health | COMPLETED | 2 | 0 | 2026-05-08T14:57:19.426731+00:00 | Analyze our company KPIs and financial health |
| `4f0cecdb-6e16-4313-ba7a-45cfffc2fabc` | Auto-Workflow: Create a comprehensive company performance report | COMPLETED | 1 | 0 | 2026-05-08T14:50:07.832357+00:00 | Create a comprehensive company performance report |
| `d0435f42-3eb4-40dd-aee1-2af3e88de399` | Auto-Workflow: aunch a new product across all departments | COMPLETED | 5 | 0 | 2026-05-08T14:47:59.219949+00:00 | aunch a new product across all departments |
| `6a27b555-b625-493f-91ac-7da303ea139d` | Auto-Workflow: Now evolve Mintuu AI Ecosystem from a workflow dem | COMPLETED | 4 | 0 | 2026-05-08T14:47:15.436869+00:00 | Now evolve Mintuu AI Ecosystem from a workflow demo into a truly intelligent autonomous multi-agent  |

Recent task samples:

| ID | Agent | Status | Title | Created At |
|---|---|---|---|---|
| `fdccaa34-96d4-4012-8c0f-472614545abd` | `agent-research` | COMPLETED | Task: analyze our competitor startegies | 2026-05-27T19:14:43.317708+00:00 |
| `72a9eda8-ce69-404e-8238-8abe5742f78e` | `agent-finance` | COMPLETED | Task: Review monthly burn rate and budget | 2026-05-27T19:12:12.709566+00:00 |
| `e8d518d8-c52a-425c-9a9d-ccede01869c1` | `agent-production` | COMPLETED | Task: Audit our infrastructure security policies | 2026-05-24T10:49:17.705763+00:00 |
| `de2e5092-3575-41a4-8d6b-2461bf5ece24` | `agent-operations` | COMPLETED | Task: Find the absolute path of logo.html in this project workspace by searching the f | 2026-05-22T09:19:47.319316+00:00 |
| `0bec9315-ba8c-4e83-b6e9-34aa9ef094ac` | `agent-operations` | COMPLETED | Task: Find the absolute path of logo.html in this project workspace by searching the f | 2026-05-22T09:17:02.119676+00:00 |
| `6718ffe2-0f99-490b-a374-c57b427c0997` | `agent-operations` | COMPLETED | Task: Test workflow | 2026-05-22T09:08:38.943903+00:00 |
| `bd4214a2-3398-41a9-a54b-2b1fab711134` | `agent-research` | COMPLETED | Task: Run competitor analysis and market watch | 2026-05-22T07:06:57.105893+00:00 |
| `cca80d3d-7976-4fe9-b2dd-0ecf7b126c54` | `agent-operations` | COMPLETED | Task: Monitor system health, workflow efficiency, and automation status | 2026-05-09T07:17:44.464878+00:00 |
| `db6b21fd-3233-4bbe-813b-4f46fc3ee66d` | `agent-research` | COMPLETED | Task: Analyze competitor activities, market trends, and industry news | 2026-05-09T07:14:44.375260+00:00 |
| `6b993f5e-31a0-4699-9c52-1458bc074768` | `agent-operations` | COMPLETED | Task: Monitor system health, workflow efficiency, and automation status | 2026-05-09T07:14:44.369626+00:00 |

Recent memory samples:

| ID | Agent | Type | Key | Content Preview |
|---|---|---|---|---|
| `32c4ef60-5184-43f8-9227-b842e875ebf8` | `organization` | `ORGANIZATIONAL` | `task_result:fdccaa34-96d4-4012-8c0f-472614545abd` | 🔍 **Research Summary** / Task: Task: analyze our competitor startegies / Confirmed historical precedent. Similar memory leak in data parser previously caused Se |
| `7f3a341a-358a-46cb-b83d-0e94e8da04fd` | `organization` | `ORGANIZATIONAL` | `org_task:fdccaa34-96d4-4012-8c0f-472614545abd` | 🔍 **Research Summary** / Task: Task: analyze our competitor startegies / Confirmed historical precedent. Similar memory leak in data parser previously caused Se |
| `be79b963-6946-4f6f-a4de-efb42114c2b3` | `agent-research` | `SHORT_TERM` | `task_result:fdccaa34-96d4-4012-8c0f-472614545abd` | 🔍 **Research Summary** / Task: Task: analyze our competitor startegies / Confirmed historical precedent. Similar memory leak in data parser previously caused Se |
| `dd98bc92-1fa0-4597-a0a8-50643222709b` | `workflow:56290520-72d7-481b-82d6-997dfcde5f3f` | `WORKFLOW` | `final_result` | {"0": "\ud83d\udcca **CEO Executive Summary**\nTask: CEO Analysis\nStatus: COMPLETED\n\n**Decision:** Task processed successfully.\n\n**\ud83e\udd16 LLM Thought |
| `7660e7a4-0e63-4387-8a1f-3280e2af4ebe` | `organization` | `ORGANIZATIONAL` | `org_task:37870048-ae58-4c03-8008-29bad1bcc09b` | ⚙️ **Operations Summary** / Task: OPERATIONS Analysis / Response plan finalized: Isolate containers, revert commit f4a9b2, and deploy previous stable release.

 |
| `41346ef9-53cb-4552-a6db-489d2190f1a6` | `agent-operations` | `SHORT_TERM` | `task_result:37870048-ae58-4c03-8008-29bad1bcc09b` | ⚙️ **Operations Summary** / Task: OPERATIONS Analysis / Response plan finalized: Isolate containers, revert commit f4a9b2, and deploy previous stable release.

 |
| `a94f1858-8adc-4489-97c9-94cc3ebf6cd4` | `organization` | `ORGANIZATIONAL` | `org_task:3937610b-7918-41f6-96c8-2efffca0a42f` | 🚀 **Production Summary** / Task: PRODUCTION Analysis / Task processed successfully.

**🤖 LLM Thought Process:**
Analyzing the request. Proceeding with standard  |
| `85a9ae1e-734f-4985-b11c-1d4c7aa3c35c` | `agent-production` | `SHORT_TERM` | `task_result:3937610b-7918-41f6-96c8-2efffca0a42f` | 🚀 **Production Summary** / Task: PRODUCTION Analysis / Task processed successfully.

**🤖 LLM Thought Process:**
Analyzing the request. Proceeding with standard  |
| `426faaf2-6015-442c-a9cb-e43e50b6f624` | `organization` | `ORGANIZATIONAL` | `org_task:0ccb5939-914a-437c-80a3-bc18cf6b97e7` | 💰 **Finance Summary** / Task: FINANCE Analysis / Task processed successfully.

**🤖 LLM Thought Process:**
Analyzing the request. Proceeding with standard execut |
| `89436dfc-e21d-4127-ba6a-e325419cb19d` | `agent-finance` | `SHORT_TERM` | `task_result:0ccb5939-914a-437c-80a3-bc18cf6b97e7` | 💰 **Finance Summary** / Task: FINANCE Analysis / Task processed successfully.

**🤖 LLM Thought Process:**
Analyzing the request. Proceeding with standard execut |

### ChromaDB Collections

Persistent path: `database/chroma_db`.

| Collection | Count | Purpose |
|---|---:|---|
| `decisions` | `0` | Collection is created but currently empty/unused |
| `agent_memory` | `0` | Collection is created but currently empty/unused |
| `workflows` | `0` | Collection is created but currently empty/unused |
| `org_knowledge` | `111` | Stores shared task/workflow result embeddings |

## 7. Agent System Details

### Runtime Registered Agents

| Agent | ID | Responsibility | LLM model preference / prompt state | Outputs |
|---|---|---|---|---|
| CEO | `agent-ceo` | Strategic leadership, approvals, KPI analysis, goal management | llama3.1 preference through reasoning engine; provider selected by router | Strategic plans, approvals, executive summaries |
| HR | `agent-hr` | Hiring, onboarding, employee/team workflows, meetings | mistral preference through default BaseAgent path | HR reports, candidate/onboarding/team outputs |
| Marketing | `agent-marketing` | Campaigns, SEO, content, growth strategy | mistral preference; CMO prompt exists but dynamic import currently looks for `SYSTEM_PROMPT`, so default prompt is used unless fixed | Marketing strategy and campaign summaries |
| Finance | `agent-finance` | Budgets, expenses, revenue, forecasts | mistral preference; CFO prompt exists as `FINANCE_SYSTEM_PROMPT` but dynamic import expects `SYSTEM_PROMPT`, so default prompt is used unless fixed | Budget/financial summaries |
| Production | `agent-production` | Deployments, release, CI/CD simulation, health monitoring | mistral preference | Deployment and health summaries |
| Operations | `agent-operations` | Workflow coordination, automation scheduling, status reporting | llama3.1 preference | Operational plans and status summaries |
| Research | `agent-research` | Market research, competitor analysis, vector memory lookup | llama3.1 preference and Research system prompt | Research summaries with vector-memory context |
| Security | `agent-security` | Risk assessment, threat modeling, incident response | mistral preference | Risk rating and security summary |
| Infrastructure | `agent-infrastructure` | Infrastructure health/status/scaling | mistral preference | Infrastructure status and blast radius |
| Analytics | `agent-analytics` | Data processing/insights; source exists but not registered by orchestrator | not active | Basic metrics output if manually instantiated |
| Legal | `agent-legal` | Compliance/contract/risk; source exists but not registered by orchestrator | not active | Compliance recommendation if manually instantiated |

All runtime agents inherit `BaseAgent`, which provides `handle_task()`: set state to planning, call `plan()`, optionally call `ReasoningEngine.reason()`, call domain `execute()`, merge LLM final decision into outputs, summarize, broadcast reasoning trace, log activity, save short-term memory, save organizational vector memory, update state to idle, and return a result record.

### Tools Available to Agents

Runtime `/api/v1/tools` verified 11 tools: `file_read`, `file_write`, `terminal_execute`, `data_analysis`, `report_generator`, `git_status`, `system_info`, `document_generator`, `calendar_manager`, `email_send`, `metrics_collector`.

Permissions are present but underdeveloped. Default agent permissions are `[EXECUTE]`, so tools requiring `READ` or `WRITE` are blocked unless `ToolRegistry.grant_permission()` is called.

### System Prompts

CEO prompt in `agents/ceo_agent/system_prompt.py`:

```text
You are the Chief Executive Officer (CEO) of Mintuu AI.
Your role is to make high-level strategic decisions, review plans, and guide the overall direction of the company.

CRITICAL INSTRUCTION:
1. You MUST read the provided CONTEXT (Research/Production/Marketing outputs).
2. Your "thought_process" and "final_decision" MUST explicitly reference specific metrics, file names, risks, or past incidents.
3. FINANCIAL RIGOR: You are hyper-critical of marketing and business plans. 
   - If a plan assumes a conversion rate > 3% for new developer signups without a massive proven community, you MUST reject it as "mathematically optimistic".
   - You must require a REVISION if the numbers don't add up to the stated goals (e.g. 500 signups / 50k revenue).
   - If you reject a plan, start your final_decision with "REJECTED: [Reason]".
   - If you approve, start with "APPROVED: [Rationale]".

Be concise, authoritative, and strategically demanding.
```

Research prompt in `agents/research_agent/system_prompt.py`:

```text
You are the Research Agent of Mintuu AI.
Your role is to conduct market research, competitor analysis, and gather information from past incidents using vector memory.

CRITICAL INSTRUCTION:
You MUST read the provided CONTEXT, which will include `vector_memory_results`.
Your "thought_process" and "final_decision" MUST explicitly reference the specific details from these vector memory results. 
DO NOT invent generic findings. Extract the actual past incidents, metrics, and resolutions from the memory and present them specifically in your final decision.
```

Finance and Marketing prompts exist but are not automatically loaded because their variables are named `FINANCE_SYSTEM_PROMPT` and `MARKETING_SYSTEM_PROMPT`, while `BaseAgent` imports `SYSTEM_PROMPT`.

## 8. Workflow Definitions

### Dynamic Auto Workflow

Trigger: `/api/v1/chat` when message contains workflow keywords (`launch`, `full report`, `company`, `all departments`, `comprehensive`, `complete analysis`, `across all`, `new product`) or direct `/api/v1/workflows/auto`.

Router logic: `TaskRouter.suggest_workflow()` returns `['ceo', 'research', 'marketing', 'finance', 'production', 'operations']` for company-wide/new-product signals; otherwise it ranks agents by keyword rules and keeps CEO first and Operations last.

Step format:

| Field | Meaning |
|---|---|
| `agent_type` | Agent type to run. |
| `title` | Step title. |
| `description` | Department-specific task description. |
| `depends_on` | Previous step index by default. |
| `requires_approval` | True for first CEO step when CEO is in the workflow; approval is currently auto-approved. |

### Flagship Workflow: GitHub Incident Pipeline

Defined in `core/workflows/flagship_workflows.py`, triggered by `POST /webhooks/github` when `X-GitHub-Event: issues` and payload action is `opened`.

| Step | Agent | Title | Dependencies | Final output contribution |
|---:|---|---|---|---|
| 1 | Research | Analyze Issue against Memory | none | Past incident and resolution report from vector memory. |
| 2 | Production | Impact Analysis | step 1 | Affected files/recent commit impact report. |
| 3 | CEO | Severity Decision | steps 1 and 2 | Severity and immediate action decision. |
| 4 | Operations | Concrete Response Plan | step 3 | Concrete response plan. |
| 5 | Marketing | Final Summary & Update | step 4 | Final public/update summary and labels. |

### Flagship Workflow: Product Launch

Defined by `get_product_launch_steps(goal)`.

| Step | Agent | Title | Dependencies | Final output contribution |
|---:|---|---|---|---|
| 1 | CEO | Decompose Goal | none | Phases, budget range, success metrics. |
| 2 | Research | Market Retrieval | step 1 | Market/competitor/pricing retrieval. |
| 3 | Marketing | Campaign Plan | step 2 | Campaign plan based on research. |
| 4 | CEO | Plan Critique Loop | step 3 | Critique against original goal metrics. |
| 5 | Finance | Allocate Budget | step 4 | Budget allocation tied to constraints. |
| 6 | Operations | Execution Checklist & KPIs | step 5 | Sequenced execution checklist and KPI checkpoints. |

### Flagship Workflow: Incident Response

Defined by `get_incident_response_steps(anomaly)`.

| Step | Agent | Title | Dependencies | Final output contribution |
|---:|---|---|---|---|
| 1 | Infrastructure | Status Report | none | Factual affected-services and blast-radius report. |
| 2 | Security | Risk Assessment | step 1 | Exploit/risk rating. |
| 3 | Operations | Severity Scoring | steps 1 and 2 | Formula-based severity score and escalation need. |
| 4 | CEO | Escalation Decision | step 3 | Approval decision and conditions. |
| 5 | Operations | Post-Mortem Generation | step 4 | Plain-English post-mortem. |

### Approval Gates

Workflow steps support `requires_approval`. In current code, `_handle_approval()` creates a collaboration approval request to `agent-ceo`, auto-responds with approved data, logs an approval gate, and always returns `True`. This is simulation, not real human approval.

## 9. Memory System Details

Memory is implemented in `core/memory/memory_manager.py`, `core/memory/vector_memory.py`, and `database/models.py`.

End-to-end flow:

1. A task is executed by `OrchestrationManager.execute_task()` or `WorkflowEngine._execute_step()`.
2. Agent context is built by `MemoryManager.build_agent_context()` from short-term memory, long-term memory, optional conversation messages, optional workflow memory, and organizational memory.
3. `ResearchAgent.handle_task()` additionally queries `MemoryManager.query_vector_memory()` against Chroma collection `org_knowledge` and injects `vector_memory_results` into context.
4. `BaseAgent.handle_task()` executes the agent, summarizes output, logs the activity, saves short-term memory, and saves organizational memory.
5. `MemoryManager.store_organizational()` stores in SQLite `memories` and also writes an embedding document to Chroma `org_knowledge`.
6. Completed workflow final results are stored as workflow memory with agent ID `workflow:<workflow_id>` and key `final_result`.

Memory tiers:

| Tier | Stored in SQLite type | Agent namespace | TTL | Vectorized |
|---|---|---|---|---|
| Short-term | `SHORT_TERM` | concrete agent ID | 1 hour default | No |
| Long-term | `LONG_TERM` | concrete agent ID | none | No |
| Workflow | `WORKFLOW` | `workflow:<id>` | 72 hours | No |
| Conversation | `CONVERSATION` | `mintuu` | none | No |
| Organizational | `ORGANIZATIONAL` | `organization` | none | Yes, in `org_knowledge` |

Current memory distribution top rows:

| Memory Type | Agent Namespace | Count |
|---|---|---:|
| `ORGANIZATIONAL` | `organization` | 362 |
| `SHORT_TERM` | `agent-operations` | 111 |
| `SHORT_TERM` | `agent-finance` | 82 |
| `SHORT_TERM` | `agent-marketing` | 68 |
| `SHORT_TERM` | `agent-ceo` | 63 |
| `SHORT_TERM` | `agent-research` | 55 |
| `SHORT_TERM` | `agent-production` | 10 |
| `WORKFLOW` | `workflow:05763404-05fa-49c8-b85a-72c1814e9bce` | 1 |
| `WORKFLOW` | `workflow:079a8d35-626e-4e40-9b86-b06ecfffff6e` | 1 |
| `WORKFLOW` | `workflow:0c459a6e-8e67-4b0f-9cfd-844fc4fdcf1c` | 1 |
| `WORKFLOW` | `workflow:3ce636be-291b-4f69-a8e1-ebf9aaed6392` | 1 |
| `WORKFLOW` | `workflow:4f0cecdb-6e16-4313-ba7a-45cfffc2fabc` | 1 |
| `WORKFLOW` | `workflow:56290520-72d7-481b-82d6-997dfcde5f3f` | 1 |
| `WORKFLOW` | `workflow:57ac8a21-16a0-4857-a1a6-7a6a912b9515` | 1 |
| `WORKFLOW` | `workflow:6a27b555-b625-493f-91ac-7da303ea139d` | 1 |
| `WORKFLOW` | `workflow:8c57d6ba-afad-4cf8-99cc-e9f440ee572a` | 1 |
| `WORKFLOW` | `workflow:8d60bee7-13dd-4de3-aa8c-ba73fa26bbad` | 1 |
| `WORKFLOW` | `workflow:d0435f42-3eb4-40dd-aee1-2af3e88de399` | 1 |

## 10. Frontend Details

### HTML Pages

| Template | URL | Purpose |
|---|---|---|
| `dashboard/templates/landing.html` | `/` | Public marketing/landing page with nav, hero, demo, comparison, CTA, footer, hero animation. |
| `dashboard/templates/login.html` | `/login` | Login form wired to `handleLogin()` in `auth.js`. |
| `dashboard/templates/signup.html` | `/signup` | Signup form wired to `handleSignup()` in `auth.js`. |
| `dashboard/templates/dashboard.html` | `/app` | Main authenticated dashboard shell using Alpine.js controller from `app.js`. |
| `dashboard/templates/logo.html` | not directly routed | Standalone logo/design artifact. |

### JavaScript Files

| File | Purpose |
|---|---|
| `dashboard/static/js/auth.js` | Stores tokens in localStorage, signs up/logs in, refreshes tokens, wraps authenticated fetches, redirects authenticated users away from auth pages, and logs out. |
| `dashboard/static/js/app.js` | Main Alpine dashboard controller: auth gate, onboarding, tour, chat, state fetch, WebSocket connection, page navigation, workflow/agent data state, toasts, settings/history helpers. |
| `dashboard/static/js/dashboard.js` | Older/alternate dashboard controller: polling, WebSocket state handling, collaboration rendering, workflow graph/timeline rendering, logs, chat. |
| `dashboard/static/js/hero3d.js` | Landing hero Three.js particle network with mobile/reduced-motion SVG fallback, FPS degradation, mouse parallax, pulse edges. |

### CSS Files

| File | Purpose |
|---|---|
| `dashboard/static/css/theme.css` | Theme tokens/colors/design variables. |
| `dashboard/static/css/base.css` | Shared reset/base layout and reusable components. |
| `dashboard/static/css/landing.css` | Public landing page layout, hero, demo, sections, CTA, footer. |
| `dashboard/static/css/app.css` | Authenticated app/dashboard layout and components. |
| `dashboard/static/css/dashboard.css` | Older/alternate dashboard styling. |

Current UI state: the app has a polished dark AI dashboard aesthetic, onboarding overlay, guided tour spotlight, chat panel, agents/workflows/history/settings navigation, real-time status labels, toasts, and a landing hero animation. It still needs cleanup because `app.js` and `dashboard.js` overlap; dashboard auth is client-side only; some UI data depends on in-memory workflow history, so completed DB workflows do not all appear after restart.

Animations/interactions include rotating chat placeholders, welcome animation, guided tour spotlight/tooltip, toasts, page transitions, WebSocket-driven state refresh, Three.js node/edge animation, mobile/reduced-motion hero fallback, FPS-based hero degradation, and dashboard polling fallback.

## 11. Authentication System

Auth files: `api/auth.py`, `api/auth_routes.py`, `dashboard/static/js/auth.js`.

| Aspect | Implementation |
|---|---|
| Signup | `/auth/signup` validates matching passwords and minimum length 6, creates a SQLite user, returns tokens. |
| Login | `/auth/login` verifies bcrypt hash and returns tokens. |
| Password storage | Direct `bcrypt.hashpw()` with `gensalt(rounds=12)`. |
| Access token | JWT signed with `settings.auth.secret_key`, algorithm `HS256`, valid for 7 days. Payload: `sub`, `email`, `name`, `exp`, `iat`, `type: access`. |
| Refresh token | JWT signed with same secret and algorithm, valid for 30 days. Payload: `sub`, `exp`, `iat`, `type: refresh`. |
| Client storage | `localStorage` keys: `mintuu_access_token`, `mintuu_refresh_token`, `mintuu_user`. |
| Protected routes server-side | `/auth/me`, `/auth/me` PUT, `/auth/onboarding/complete`, `/auth/data/clear`, `/auth/data/export`. |
| Public API routes | All `/api/v1/*` routes, `/webhooks/github`, page routes, docs are public at server level. |
| Dashboard protection | Client-side only; `/app` HTML is public but JS redirects if no token exists. |
| Risk | `SECRET_KEY` defaults to a random process-local value if not configured, invalidating tokens after restart and making multi-instance deployment inconsistent. |

## 12. LLM Integration Details

Provider router logic in `core/llm/provider_router.py`:

1. If `DEFAULT_LLM_PROVIDER` is set and matches a provider, use it.
2. Else if `GROQ_API_KEY` exists, use Groq.
3. Else if `OPENAI_API_KEY` exists, use OpenAI.
4. Else if `ANTHROPIC_API_KEY` exists, use Anthropic.
5. Else use Ollama.

Current local `.env` key names detected: `ANTHROPIC_API_KEY=<redacted>` and `FISH_API_KEY=<redacted>`. Because Anthropic key exists and no Groq/OpenAI key was detected, startup selected `anthropic`.

Provider behavior:

| Provider | File | Model | Current behavior |
|---|---|---|---|
| OpenAI | `core/llm/providers/openai_provider.py` | `OPENAI_MODEL` or `gpt-4o-mini` | Real async OpenAI Chat Completions call. |
| Ollama | `core/llm/providers/ollama_provider.py` | `OLLAMA_MODEL`, mapped `llama3.1 -> llama3:latest`, `mistral -> mistral:latest` | Real local HTTP call to `/api/chat` after `/api/tags` health check. |
| Anthropic | `core/llm/providers/anthropic_provider.py` | `claude-3-haiku-20240307` | Mocked. It sleeps 2 seconds and returns canned JSON based on system prompt. |
| Groq | `core/llm/providers/groq_provider.py` | `GROQ_MODEL` or `llama-3.1-8b-instant` | Real OpenAI-compatible Groq HTTP call with optional JSON response format. |

Agent model preference in `BaseAgent.handle_task()`:

```python
pref = "llama3.1" if self.agent_type.lower() in ["ceo", "research", "operations"] else "mistral"
```

Important nuance: `model_preference` is also passed to `ProviderRouter.get_provider()`, which treats it as a provider name first. Because `llama3.1` and `mistral` are not provider names, the default provider is used, and the model preference only matters inside providers that inspect it, especially Ollama and Groq.

Reasoning output schema requested from LLM:

```json
{
  "thought_process": "Detailed step-by-step reasoning",
  "required_tools": ["tool1", "tool2"],
  "action_plan": [{"step": 1, "action": "...", "expected_outcome": "..."}],
  "confidence_score": 0.95,
  "final_decision": "Summary of what to do"
}
```

Parsing: `ReasoningEngine.reason()` strips markdown JSON fences if present, parses JSON, warns on confidence below 0.6, and returns fallback object with `raw` if JSON parsing fails.

## 13. Deployment Configuration

### Environment Variables

| Variable | Purpose | Required? |
|---|---|---|
| `MINTUU_DATA_DIR` | Data/database root; defaults to repo `database`. | No locally, yes for stable deploy storage. |
| `LOG_LEVEL` | Logging verbosity. | No. |
| `PORT` / `API_PORT` | API port; defaults to 8003 in settings. | Required by Render via `$PORT`. |
| `SECRET_KEY` | JWT signing key. | Strongly required in production. |
| `ENVIRONMENT` | `development`/`production` label. | No. |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins. | Required for deployed frontend. |
| `DEFAULT_LLM_PROVIDER` | Explicit provider selector. | No. |
| `OLLAMA_BASE_URL` | Local Ollama API base. | Needed for Ollama. |
| `OLLAMA_MODEL` | Default Ollama model. | No. |
| `OPENAI_API_KEY` | OpenAI provider credential. | Needed for OpenAI. |
| `ANTHROPIC_API_KEY` | Anthropic provider credential. | Needed only if real Anthropic implementation is restored. |
| `GROQ_API_KEY` | Groq provider credential; preferred for free Render deployment. | Needed for Groq. |
| `GROQ_MODEL` | Groq model override. | No. |
| `REDIS_URL` | Redis/Celery broker URL. | Needed for distributed worker. |
| `CHROMADB_PATH` | Configured Chroma path but current `VectorMemory()` uses its own default unless passed. | No/currently not fully wired. |
| `GITHUB_TOKEN` | GitHub tool token; missing means GitHub tool is simulated/limited. | Optional. |
| `MINTUU_FRONTEND_URL` | Frontend URL for CORS/email links. | Optional. |

### Local Run Commands

Known working command from this session:

```bash
cd /Users/mridulsoliwal/Documents/All_Projects/AI_Agents/mintuu_ai_ecosystem
PYTHONPATH=/Users/mridulsoliwal/Documents/All_Projects/AI_Agents python3 -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Makefile command:

```bash
make dev
# expands to: PYTHONPATH=$(dirname $(pwd)) uvicorn api.app:app --port 8003 --reload
```

README command:

```bash
docker-compose up -d
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Known deployment issues on free tier:

| Platform | Issue |
|---|---|
| Render free | Service sleeps, SQLite and Chroma persistence may be unstable unless persistent disk is configured, background threads stop during sleep, local Ollama unavailable, `SECRET_KEY` must be stable, and `PYTHONPATH`/package layout must be correct. |
| Vercel | Current config tries to route templates as static files under `/templates`, but repo structure is `dashboard/templates`; Vercel is not serving the FastAPI process. |
| Docker Compose | No Dockerfile exists, so `build: .` will fail unless a Dockerfile is added. |
| Kubernetes/Terraform | Manifests are sketches; missing service, ingress, secrets, Redis, persistent storage, Docker image build/push, IAM role definitions, subnets, and outputs. |

## 14. Known Issues and Limitations

| Issue | Why it exists | Fix |
|---|---|---|
| Version naming drift | README, app title, settings, and package metadata were updated independently. | Pick one version and update `pyproject.toml`, README, FastAPI title, logs, and settings. |
| Import requires parent `PYTHONPATH` | Code imports `mintuu_ai_ecosystem.*` while uvicorn target is `api.app:app` from inside package folder. | Run as installed package from parent, adjust package layout, or use `PYTHONPATH` consistently. |
| No tests collected | `tests/` only contains `__init__.py`; root scripts are not pytest tests. | Add pytest files under `tests/` for API, DB, workflow, memory, auth. |
| Anthropic provider is mocked | Provider returns canned JSON with comment `MOCK ANTHROPIC SINCE CREDITS ARE 0`. | Implement real Anthropic call or rename provider to mock in dev. |
| Marketing/Finance prompts not loaded | Variable names do not match BaseAgent dynamic import expectation. | Rename to `SYSTEM_PROMPT` or update BaseAgent to detect agent-specific prompt variable names. |
| Approval gates are fake | `_handle_approval()` always approves. | Add persistent approval requests, dashboard UI, protected approve/reject endpoints. |
| Tool permissions are incomplete | Defaults allow EXECUTE only; no robust per-agent policy setup. | Define default role permissions and enforce sandbox paths/command allowlists. |
| Terminal tool is dangerous | Uses `subprocess.run(..., shell=True)`. | Replace with argument-list execution, allowlist commands, no shell by default, timeouts, approvals, and audit logs. |
| File tools are unsandboxed | `file_read` and `file_write` accept arbitrary paths. | Restrict to configured workspace roots and block secrets/system paths. |
| GitHub webhook has no signature verification | Endpoint accepts arbitrary JSON. | Verify `X-Hub-Signature-256` with webhook secret. |
| Dashboard auth is client-side | `/app` route always serves HTML; JS redirects. | Add server-side auth or accept this for SPA but protect APIs. |
| Core APIs are public | `/api/v1/*` endpoints do not require JWT. | Add auth dependencies and user scoping for production. |
| Chroma path setting not fully wired | `MemoryManager` instantiates `VectorMemory()` without passing `settings.CHROMADB_PATH`. | Pass configured path to `VectorMemory(settings.CHROMADB_PATH)`. |
| Duplicate/old dashboard controllers | `app.js` and `dashboard.js` overlap. | Consolidate into one dashboard controller. |
| Docker Compose likely fails | `docker-compose.yml` references `build: .` but no Dockerfile found. | Add Dockerfile and correct worker import path/PYTHONPATH. |
| Celery not central to execution | Main flow executes synchronously in API process. | Move workflow/agent execution to Celery or remove distributed claims. |
| Some feature modules are placeholders | adaptation, planning, multimodal, advanced memory, approval components are skeletal. | Either implement or mark roadmap modules clearly. |
| Generated artifacts are committed with source | PDFs, PNGs, DBs, pyc, reports, `.DS_Store` exist in tree. | Add `.gitignore`, move artifacts to `artifacts/`, avoid committing DB/pycache. |
| SQLite user data deletion incomplete | `delete_user_data()` deletes conversations but not tasks/workflows by user comprehensively. | Add user scoping to tasks/workflows/memories and transactional cleanup. |

## 15. What Has Been Proven Working

| Capability | Proof |
|---|---|
| Server startup | Uvicorn started on `http://127.0.0.1:8000`; logs showed database, memory, state, message bus, tools, LLM manager, 9 agents, workflow engine, autonomous engine initialized. |
| Status API | `/api/v1/status` returned ecosystem name `Mintuu AI Ecosystem`, version `3.0.0`, environment `development`, 9 agents, 11 tools, and healthy state. |
| Tools API | `/api/v1/tools` returned all 11 tool metadata entries. |
| Agents API | `/api/v1/agents` returned 9 active runtime agents with states and capabilities. |
| Memory API | `/api/v1/memory` returned cache stats: cache capacity 500 and active cache entries. |
| Analytics API | `/api/v1/analytics` returned counts: 326 completed tasks, 15 completed workflows, 762 memories, no failed tasks/workflows. |
| SQLite schema | `.schema` inspection showed conversations, messages, tasks, workflows, workflow_states, memories, agent_logs, events, tool_executions, users, and indexes. |
| Existing workflow history | SQLite has 15 completed workflows including product launch, system health, budget review, KPI/financial health, and company performance report workflows. |
| Existing task history | SQLite has 326 completed tasks and 0 failed tasks. |
| Existing memory history | SQLite has 762 memories; Chroma `org_knowledge` has 111 embedded documents. |
| Frontend pages | `GET /`, `/app`, `/docs` returned HTML during verification. |
| Tests status | `python3 -m pytest tests/ -v` ran successfully as a command but collected 0 tests and exited code 5, proving test suite is missing rather than failing assertions. |

## Strategic Direction Notes for External AI

The best next architectural direction is to stabilize the core first: unify versions, fix import/package layout, protect APIs, replace mocked LLM/provider behavior with explicit dev/production modes, enforce tool sandboxing, add real tests, and separate source code from generated artifacts. After that, integrate `AI_Agents/Mac_Agent` as a separate local automation service exposed to Mintuu through a strict tool adapter and approval layer, rather than merging unsafe file/terminal capabilities directly into agent code.
