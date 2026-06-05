import asyncio
import aiohttp
import json

async def main():
    payload = {
        "model": "llama3:latest",
        "messages": [{"role": "user", "content": "hi"}],
        "stream": False,
        "format": "json"
    }
    url = "http://localhost:11434/api/chat"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            print(resp.status)
            print(await resp.text())

asyncio.run(main())
