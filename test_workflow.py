import requests
import json
import time

API_URL = "http://localhost:8003/api/v1"

def test_workflow():
    print("Sending workflow trigger...")
    try:
        response = requests.post(f"{API_URL}/chat", json={
            "message": "We need to launch a new product. Can you do a complete analysis across all departments?",
            "user_id": "test_user_123"
        })
        response.raise_for_status()
        data = response.json()
        print("\nWorkflow triggered successfully!")
        print(f"Conversation ID: {data.get('conversation_id')}")
        print("\nResponse:")
        print(data.get('response'))
        
        # Now wait and poll workflow status
        time.sleep(2)
        print("\nFetching active workflows...")
        wf_resp = requests.get(f"{API_URL}/workflows")
        workflows = wf_resp.json()
        for wf in workflows:
            print(f"- {wf['name']} ({wf['status']})")
            for step in wf.get('steps', []):
                print(f"  [{step['status']}] {step['agent_type']}: {step['task_title']}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)

if __name__ == "__main__":
    test_workflow()
