"""
Groq LLM Provider — Free tier API for deployed environments.
Uses the Groq Cloud API (OpenAI-compatible) with llama-3.1-8b-instant.
Free at console.groq.com — no credit card required.
"""
import os
import logging
import aiohttp
from typing import Dict, Any, Optional
from .base_provider import BaseProvider

logger = logging.getLogger("mintuu.llm.groq")


class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.default_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        model_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise Exception("GROQ_API_KEY not set. Get a free key at console.groq.com")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model_preference or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, json=payload, headers=headers
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"Groq API error {resp.status}: {error_text}")

                    data = await resp.json()
                    choice = data.get("choices", [{}])[0]
                    usage = data.get("usage", {})

                    return {
                        "content": choice.get("message", {}).get("content", ""),
                        "model": data.get("model", self.default_model),
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                    }
        except aiohttp.ClientError as e:
            logger.error(f"Groq connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
