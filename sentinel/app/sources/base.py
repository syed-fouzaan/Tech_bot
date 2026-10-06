"""Base protocol and models for source adapters."""

from datetime import datetime, timezone
from typing import Protocol, List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RawItem(BaseModel):
    source_id: str
    external_id: str
    canonical_url: str
    title: str
    author: Optional[str] = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: str  # paper, model, release, blog, discussion
    reliability_tier: int = 5  # 1-10 scale
    raw_content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SourceAdapter(Protocol):
    source_id: str
    reliability_tier: int

    async def fetch(self, limit: int = 15) -> List[RawItem]:
        ...
