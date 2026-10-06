"""Multi-Provider AI Gateway with hard $0 budget guard, circuit breaker, and task router."""

import time
import asyncio
from typing import Dict, List, Optional, Any
from sentinel.app.config import Settings, get_settings
from sentinel.app.providers.base import AIProvider, AIResponse, TaskType
from sentinel.app.providers.gemini import GeminiProvider
from sentinel.app.providers.groq import GroqProvider
from sentinel.app.providers.ollama import OllamaProvider
from sentinel.app.providers.mock import MockProvider


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time_s: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_time_s = recovery_time_s
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_attempt(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_time_s:
                self.state = "HALF_OPEN"
                return True
            return False
        # HALF_OPEN allows single probe
        return True


class QuotaLedger:
    def __init__(self):
        self.minute_calls: Dict[str, List[float]] = {}
        self.daily_calls: Dict[str, int] = {}
        self.current_day: str = time.strftime("%Y-%m-%d")

    def _clean(self, provider_id: str) -> None:
        now = time.time()
        calls = self.minute_calls.get(provider_id, [])
        self.minute_calls[provider_id] = [t for t in calls if now - t < 60.0]

        today = time.strftime("%Y-%m-%d")
        if today != self.current_day:
            self.daily_calls.clear()
            self.current_day = today

    def can_call(self, provider_id: str, rpm_limit: int = 15, rpd_limit: int = 1500) -> bool:
        self._clean(provider_id)
        if len(self.minute_calls.get(provider_id, [])) >= rpm_limit:
            return False
        if self.daily_calls.get(provider_id, 0) >= rpd_limit:
            return False
        return True

    def record_call(self, provider_id: str) -> None:
        self._clean(provider_id)
        self.minute_calls.setdefault(provider_id, []).append(time.time())
        self.daily_calls[provider_id] = self.daily_calls.get(provider_id, 0) + 1


class AIGateway:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.quota = QuotaLedger()
        self.providers: Dict[str, AIProvider] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        # Gemini Free Adapter
        if self.settings.GEMINI_API_KEY:
            self.providers["gemini"] = GeminiProvider(
                api_key=self.settings.GEMINI_API_KEY,
                default_model=self.settings.GEMINI_MODEL,
            )
        # Groq Free Adapter
        if self.settings.GROQ_API_KEY:
            self.providers["groq"] = GroqProvider(
                api_key=self.settings.GROQ_API_KEY,
                default_model=self.settings.GROQ_MODEL,
            )
        # Ollama local Adapter
        self.providers["ollama"] = OllamaProvider(
            base_url=self.settings.OLLAMA_BASE_URL,
            default_model=self.settings.OLLAMA_MODEL,
        )
        # Mock / Deterministic Fallback Adapter
        self.providers["mock"] = MockProvider()

        for pid in self.providers:
            self.breakers[pid] = CircuitBreaker()

    def _get_task_provider_chain(self, task: TaskType) -> List[str]:
        """Configurable task-to-provider routing priorities."""
        if task in (TaskType.TECHNICAL_ANALYSIS, TaskType.COMPARISON, TaskType.FINAL_DIGEST):
            return ["gemini", "groq", "ollama", "mock"]
        elif task in (TaskType.CLASSIFICATION, TaskType.SUMMARIZATION, TaskType.IMPORTANCE_SCORING):
            return ["groq", "gemini", "ollama", "mock"]
        elif task in (TaskType.ROADMAP, TaskType.LEARNING, TaskType.CODING):
            return ["gemini", "groq", "ollama", "mock"]
        return ["gemini", "groq", "ollama", "mock"]

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        task: TaskType = TaskType.CHAT,
        preferred_provider: Optional[str] = None,
        **kwargs: Any,
    ) -> AIResponse:
        """
        Unified AI generation with hard $0 budget guard and graceful fallback.
        """
        # Hard $0 guard
        if self.settings.DAILY_AI_BUDGET > 0.0 and not self.settings.ALLOW_PAID_PROVIDERS:
            raise PermissionError("Hard $0 Guard: Non-zero budget detected without paid provider authorization.")

        chain = [preferred_provider] if preferred_provider else self._get_task_provider_chain(task)
        # Always ensure fallback is present
        if "mock" not in chain:
            chain.append("mock")

        last_error = None
        for pid in chain:
            provider = self.providers.get(pid)
            if not provider:
                continue

            # Ensure provider is tagged free
            if provider.cost_class != "free" and not self.settings.ALLOW_PAID_PROVIDERS:
                continue

            breaker = self.breakers.get(pid)
            if breaker and not breaker.can_attempt():
                continue

            if not self.quota.can_call(pid):
                continue

            try:
                if not await provider.is_available():
                    continue

                response = await provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    task=task,
                    **kwargs,
                )
                self.quota.record_call(pid)
                if breaker:
                    breaker.record_success()
                return response
            except Exception as e:
                last_error = e
                if breaker:
                    breaker.record_failure()
                continue

        # If everything failed, call mock provider as ultimate deterministic fallback
        mock_provider = self.providers["mock"]
        response = await mock_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=task,
            **kwargs,
        )
        return response
