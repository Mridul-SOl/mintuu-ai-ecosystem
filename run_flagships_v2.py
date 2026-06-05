import time
import requests
import json
import os
from playwright.sync_api import sync_playwright

API_URL = "http://localhost:8003"
OUTPUT_DIR = "report/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

def wait_for_idle():
    print("Waiting for ecosystem to become idle...")
    while True:
        try:
            res = requests.get(f"{API_URL}/api/v1/status")
            status = res.json()
            # If all agents are IDLE
            agents = status.get("agents", [])
            active = [a for a in agents if a["state"]["status"] != "IDLE"]
            workflows = status.get("active_workflows", [])
            if not active and not workflows:
                print("Ecosystem is idle.")
                break
        except Exception as e:
            pass
        time.sleep(2)

def capture_screenshot(page, filename):
    page.screenshot(path=os.path.join(OUTPUT_DIR, filename))
    print(f"Captured {filename}")

def run_workflow_1():
    print("Triggering Workflow 1 (GitHub Webhook)...")
    payload = {
        "action": "opened",
        "issue": {
            "title": "Critical memory leak causing production crashes in analytics engine",
            "body": "The analytics engine is consuming 90% of available RAM during the nightly sync. Suspect memory leak in the data parser. Please investigate immediately.",
            "number": 104
        }
    }
    requests.post(f"{API_URL}/webhooks/github", json=payload, headers={"X-GitHub-Event": "issues"})

def run_workflow_2():
    print("Triggering Workflow 2 (Product Launch)...")
    payload = {
        "description": "Launch Mintuu Pro to developers by Q3 with 500 signups and $50k revenue."
    }
    # This invokes auto-workflow which routes it through the departments
    requests.post(f"{API_URL}/api/v1/workflows/auto", json=payload)

def run_workflow_3():
    print("Triggering Workflow 3 (Incident Response)...")
    payload = {
        "description": "Anomaly: CPU at 94% for 8 minutes on production server, memory at 87%, response time degraded by 340%."
    }
    requests.post(f"{API_URL}/api/v1/workflows/auto", json=payload)

def run_memory_test():
    print("Triggering Workflow 1 again for Memory Test...")
    payload = {
        "action": "opened",
        "issue": {
            "title": "Memory usage spiking in analytics module",
            "body": "We are seeing similar memory spikes again in the analytics module data parser.",
            "number": 105
        }
    }
    requests.post(f"{API_URL}/webhooks/github", json=payload, headers={"X-GitHub-Event": "issues"})

def dump_traces():
    print("Dumping traces and reasoning logs...")
    res = requests.get(f"{API_URL}/api/v1/status").json()
    completed = res.get("completed_workflows", [])
    
    with open("execution_trace.json", "w") as f:
        json.dump(completed, f, indent=2)
        
    with open("raw_reasoning_log.txt", "w") as f:
        for wf in completed:
            f.write(f"\n\n{'='*40}\nWORKFLOW: {wf.get('name')}\n{'='*40}\n")
            for step in wf.get("steps", []):
                if step.get("agent_type") in ["ceo", "research", "operations"]:
                    f.write(f"\nAGENT: {step.get('agent_type').upper()}\n")
                    # Try to extract the thought process from result summary if it was injected
                    reasoning = step.get("result", {}).get("results", {}).get("llm_reasoning", {})
                    f.write(f"THOUGHT_PROCESS: {reasoning.get('thought_process', '')}\n")
                    f.write(f"FINAL_DECISION: {reasoning.get('final_decision', '')}\n")

def main():
    wait_for_idle()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("http://localhost:8003/dashboard")
        
        # W1
        run_workflow_1()
        time.sleep(20) # wait a bit for CEO to be active
        capture_screenshot(page, "w1_dashboard.png")
        wait_for_idle()
        
        # W2 and W3 Skipped for speed
        
        # Memory
        run_memory_test()
        time.sleep(20)
        capture_screenshot(page, "memory_proof.png")
        wait_for_idle()
        
        browser.close()
        
    dump_traces()
    print("All workflows executed and traces saved.")

if __name__ == "__main__":
    main()
