"""Multi-source fetcher."""

from typing import List
from sentinel.app.sources.base import RawItem, SourceAdapter
from sentinel.app.sources import (
    ArxivSourceAdapter,
    HuggingFaceSourceAdapter,
    GitHubReleasesSourceAdapter,
    RSSSourceAdapter,
    HackerNewsSourceAdapter,
)


class MultiSourceFetcher:
    def __init__(self, adapters: List[SourceAdapter] = None):
        self.adapters = adapters or [
            ArxivSourceAdapter(),
            HuggingFaceSourceAdapter(),
            GitHubReleasesSourceAdapter(),
            RSSSourceAdapter(),
            HackerNewsSourceAdapter(),
        ]

    async def fetch_all(self, limit_per_source: int = 10) -> List[RawItem]:
        items: List[RawItem] = []
        for adapter in self.adapters:
            try:
                fetched = await adapter.fetch(limit=limit_per_source)
                items.extend(fetched)
            except Exception:
                continue
        return items
