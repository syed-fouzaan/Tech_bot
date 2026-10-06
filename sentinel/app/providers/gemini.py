"""Google Gemini Free Tier Adapter using direct REST API."""

import time
import httpx
from typing import Any
from sentinel.app.providers.base import AIResponse, TaskType

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider:
    provider_id: str = "gemini"
    cost_class: str = "free"

    def __init__(self, api_key: str, default_model: str = "gemini-2.5-flash"):
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
            raise ValueError("GEMINI_API_KEY is not configured")

        model = kwargs.get("model", self.default_model)
        url = GEMINI_API_URL.format(model=model) + f"?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. Proceeding strictly under instructions."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.2),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            },
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start) * 1000.0

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned empty candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        content = parts[0].get("text", "") if parts else ""

        usage = data.get("usageMetadata", {})
        tokens_in = usage.get("promptTokenCount", 0)
        tokens_out = usage.get("candidatesTokenCount", 0)

        return AIResponse(
            content=content,
            provider=self.provider_id,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
        )
