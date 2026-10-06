"""Hacker News source adapter via Algolia search API."""

from datetime import datetime, timezone
import httpx
from typing import List
from sentinel.app.sources.base import RawItem

HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"


class HackerNewsSourceAdapter:
    source_id: str = "hackernews"
    reliability_tier: int = 4  # Community discussion tier

    async def fetch(self, limit: int = 10) -> List[RawItem]:
        params = {
            "query": "LLM OR vLLM OR \"machine learning\" OR \"deep learning\"",
            "tags": "story",
            "hitsPerPage": str(limit),
        }

        items: List[RawItem] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(HN_ALGOLIA_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            for hit in data.get("hits", []):
                title = hit.get("title", "")
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                author = hit.get("author", "hn_user")
                points = hit.get("points", 0)
                comments = hit.get("num_comments", 0)

                items.append(
                    RawItem(
                        source_id=self.source_id,
                        external_id=str(hit.get("objectID")),
                        canonical_url=url,
                        title=f"HN: {title} ({points} pts, {comments} comments)",
                        author=author,
                        published_at=datetime.now(timezone.utc),
                        source_type="discussion",
                        reliability_tier=self.reliability_tier,
                        raw_content=f"Points: {points}. Comments: {comments}.",
                        metadata={"points": points, "num_comments": comments},
                    )
                )
        except Exception:
            pass

        return items
