"""Groq and OpenAI-compatible Free Tier Adapter."""

import time
import httpx
from typing import Any
from sentinel.app.providers.base import AIResponse, TaskType

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider:
    provider_id: str = "groq"
    cost_class: str = "free"

    def __init__(self, api_key: str, default_model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.default_model = default_model

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        task: TaskType = TaskType.CHAT,
        **kwargs: Any,
    ) -> AIResponse:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        model = kwargs.get("model", self.default_model)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start) * 1000.0

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("Groq returned empty choices")

        content = choices[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})

        return AIResponse(
            content=content,
            provider=self.provider_id,
            model=model,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
        )
