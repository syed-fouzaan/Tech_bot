"""Local Ollama Adapter for offline and fallback inference."""

import time
import httpx
from typing import Any
from sentinel.app.providers.base import AIResponse, TaskType


class OllamaProvider:
    provider_id: str = "ollama"
    cost_class: str = "free"

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen2.5:7b"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        task: TaskType = TaskType.CHAT,
        **kwargs: Any,
    ) -> AIResponse:
        model = kwargs.get("model", self.default_model)
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.2),
            },
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start) * 1000.0

        content = data.get("response", "")
        tokens_in = data.get("prompt_eval_count", 0)
        tokens_out = data.get("eval_count", 0)

        return AIResponse(
            content=content,
            provider=self.provider_id,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
        )
