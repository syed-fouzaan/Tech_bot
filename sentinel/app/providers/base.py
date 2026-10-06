"""Base definitions and protocols for AI Providers."""

from enum import Enum
from typing import Protocol, Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    DEDUPLICATION = "deduplication"
    SUMMARIZATION = "summarization"
    IMPORTANCE_SCORING = "importance_scoring"
    TECHNICAL_ANALYSIS = "technical_analysis"
    COMPARISON = "comparison"
    ROADMAP = "roadmap"
    LEARNING = "learning"
    CODING = "coding"
    FINAL_DIGEST = "final_digest"
    CHAT = "chat"


class AIResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    is_fallback: bool = False


class AIProvider(Protocol):
    provider_id: str
    cost_class: str  # Must be "free"

    async def is_available(self) -> bool:
        ...

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        task: TaskType = TaskType.CHAT,
        **kwargs: Any,
    ) -> AIResponse:
        ...
