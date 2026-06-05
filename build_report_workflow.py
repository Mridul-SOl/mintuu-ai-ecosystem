import requests
import json
import os

API_URL = "http://localhost:8003"
OUTPUT_DIR = "report/output"

def execute_task(agent, description):
    print(f"Requesting {agent.upper()} to perform task...")
    res = requests.post(f"{API_URL}/api/v1/execute", json={
        "description": description,
        "agent_type": agent,
        "priority": 10
    })
    return res.json().get("summary", "")

def main():
    print("Building the Mintuu Flagship Report via Agent Workflow...")
    
    with open("execution_trace.json", "r") as f:
        trace = f.read()
        
    with open("raw_reasoning_log.txt", "r") as f:
        reasoning = f.read()
        
    # Research Agent Task
    research_prompt = f"""
    You are the Research Agent. I need you to extract the real stats from the following execution trace.
    Return ONLY a factual, bulleted summary containing:
    1. Total time per workflow.
    2. Total tokens used across all workflows.
    3. Number of agent handoffs.
    4. Memory retrieval confirmation (did we retrieve context in the memory test run?).
    
    Trace Data:
    {trace}
    """
    research_stats = execute_task("research", research_prompt)
    
    # CEO Agent Task
    ceo_prompt = f"""
    You are the CEO. I need you to write the plain-English narrative for our Flagship Demonstration Report. 
    Write two sections:
    1. Workflow 1 (GitHub Pipeline): Describe what the workflow accomplished step-by-step. Focus on the business value. Use completely plain language. No jargon, no variable names, no code references. Write as if you are explaining this to a non-technical smart friend.
    2. Autonomous Operations: Describe how the Operations and Finance agents ran their health and budget checks in the background asynchronously without interrupting the main workflow.
    
    Please ensure the writing is warm, human, and professional. DO NOT write an 'executive analysis' template. Write a real narrative.
    
    Source Material to summarize:
    {reasoning}
    """
    ceo_narrative = execute_task("ceo", ceo_prompt)
    
    # Operations Agent Task
    ops_prompt = f"""
    You are the Operations Director. Your task is to compile the CEO's narrative and the Research metrics into a SINGLE, BEAUTIFUL HTML file.
    
    Requirements:
    1. It must be a complete HTML file with <html>, <head>, and <body> tags.
    2. Include CSS in a <style> tag to make it look incredibly modern, premium, and clean (like a Stripe or Apple webpage).
    3. Include a Cover Page section titled 'Mintuu AI Ecosystem - Flagship Workflow Demonstration' and today's date.
    4. Insert the Research Stats.
    5. Insert the CEO Narrative.
    6. DO NOT output your thought process. ONLY output the raw HTML code. Do NOT wrap it in markdown block quotes.
    
    Research Stats: {research_stats}
    CEO Narrative: {ceo_narrative}
    """
    html_content = execute_task("operations", ops_prompt)
    
    # Clean up HTML response
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
        html_content = html_content.split("```")[1].strip()
        
    out_html = os.path.join(OUTPUT_DIR, "mintuu_flagship_report.html")
    with open(out_html, "w") as f:
        f.write(html_content)
        
    print(f"Report successfully compiled and saved to {out_html}.")

if __name__ == "__main__":
    main()
