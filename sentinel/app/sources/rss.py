"""AI Lab Blogs and Engineering publications RSS adapter."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import httpx
from typing import List
from sentinel.app.sources.base import RawItem

RSS_FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml", "tier": 10},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "tier": 10},
    {"name": "AWS Machine Learning", "url": "https://aws.amazon.com/blogs/machine-learning/feed/", "tier": 8},
    {"name": "Databricks Engineering", "url": "https://www.databricks.com/blog/feed", "tier": 8},
]


class RSSSourceAdapter:
    source_id: str = "rss_blogs"
    reliability_tier: int = 9

    async def fetch(self, limit: int = 10) -> List[RawItem]:
        items: List[RawItem] = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for feed in RSS_FEEDS:
                try:
                    resp = await client.get(feed["url"])
                    if resp.status_code != 200:
                        continue
                    
                    root = ET.fromstring(resp.text)
                    # Check for RSS 2.0 channel/item or Atom feed
                    channel = root.find("channel")
                    entries = channel.findall("item") if channel is not None else root.findall("{http://www.w3.org/2005/Atom}entry")
                    
                    for item in entries[:2]:
                        title = (item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "Blog Post").strip()
                        link = (item.findtext("link") or "").strip()
                        if not link:
                            link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                            if link_elem is not None:
                                link = link_elem.attrib.get("href", "")
                                
                        desc = (item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
                        ext_id = link or title

                        items.append(
                            RawItem(
                                source_id=self.source_id,
                                external_id=ext_id,
                                canonical_url=link,
                                title=f"[{feed['name']}] {title}",
                                author=feed["name"],
                                published_at=datetime.now(timezone.utc),
                                source_type="blog",
                                reliability_tier=feed["tier"],
                                raw_content=desc[:2000],
                                metadata={"feed": feed["name"]},
                            )
                        )
                except Exception:
                    continue

        return items[:limit]
