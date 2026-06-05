"""
Mintuu AI Ecosystem — CLI Entry Point
"""
import argparse
import sys
import uvicorn


def main():
    parser = argparse.ArgumentParser(
        prog="mintuu",
        description="Mintuu AI Ecosystem — AI-Powered Business Operating System",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Server command
    srv = sub.add_parser("serve", help="Start the ecosystem server")
    srv.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    srv.add_argument("--port", type=int, default=8000, help="Port to bind to")
    srv.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Status command
    sub.add_parser("status", help="Check system status")

    # Task command
    task = sub.add_parser("task", help="Execute a task")
    task.add_argument("description", help="Task description")
    task.add_argument("--agent", help="Target agent type")

    args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        host = getattr(args, "host", "0.0.0.0")
        port = getattr(args, "port", 8000)
        reload = getattr(args, "reload", False)
        print(f"\n🚀 Starting Mintuu AI Ecosystem on http://{host}:{port}\n")
        uvicorn.run(
            "mintuu_ai_ecosystem.api.app:app",
            host=host, port=port, reload=reload,
            log_level="info",
        )

    elif args.command == "status":
        import httpx
        try:
            r = httpx.get("http://localhost:8000/api/v1/status", timeout=5)
            import json
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print("❌ Ecosystem not running. Start with: mintuu serve")

    elif args.command == "task":
        import httpx
        try:
            r = httpx.post("http://localhost:8000/api/v1/execute", json={
                "description": args.description,
                "agent_type": args.agent,
            }, timeout=30)
            import json
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print("❌ Ecosystem not running. Start with: mintuu serve")


if __name__ == "__main__":
    main()
