import asyncio
import json
from mintuu_ai_ecosystem.core.llm.llm_manager import LLMManager
from mintuu_ai_ecosystem.core.llm.reasoning_engine import ReasoningEngine
from mintuu_ai_ecosystem.agents.research_agent.system_prompt import SYSTEM_PROMPT as RES_SYS_PROMPT
from mintuu_ai_ecosystem.agents.ceo_agent.system_prompt import SYSTEM_PROMPT as CEO_SYS_PROMPT

async def main():
    llm = LLMManager()
    engine = ReasoningEngine(llm)
    
    # 1. Research Agent
    res_task = "Query vector memory to find similar past issues for 'Critical memory leak causing production crashes in analytics engine'. Produce a report on past incidents and resolutions."
    res_context = {
        "vector_memory_results": [
            "Incident #104: Analytics module data parser memory leak. Resolution: Patched the buffer allocation loop in data_parser.py"
        ]
    }
    
    print("--- RESEARCH AGENT ---")
    res_output = await engine.reason("agent-research", res_task, res_context, RES_SYS_PROMPT, "llama3.1")
    print(json.dumps(res_output, indent=2))
    
    # 2. CEO Agent
    ceo_task = "Read Research and Production reports. Decide the severity of the issue with written reasoning. Decide if immediate action is needed."
    ceo_context = {
        "workflow_context": {
            "0": res_output.get("final_decision", "Research found nothing."),
            "1": "Production Agent: Investigated and found memory leak in data_parser.py. Critical impact."
        }
    }
    
    print("\n--- CEO AGENT ---")
    ceo_output = await engine.reason("agent-ceo", ceo_task, ceo_context, CEO_SYS_PROMPT, "llama3.1")
    print(json.dumps(ceo_output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
