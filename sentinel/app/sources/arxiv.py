"""arXiv source adapter using export API and stdlib XML parsing."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import httpx
from typing import List
from sentinel.app.sources.base import RawItem

ARXIV_API_URL = "https://export.arxiv.org/api/query"


class ArxivSourceAdapter:
    source_id: str = "arxiv"
    reliability_tier: int = 9  # Research paper tier

    async def fetch(self, limit: int = 10) -> List[RawItem]:
        params = {
            "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(limit),
        }
        
        items: List[RawItem] = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(ARXIV_API_URL, params=params)
                resp.raise_for_status()
                xml_data = resp.text

            root = ET.fromstring(xml_data)
            # Atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                id_elem = entry.find("atom:id", ns)
                published_elem = entry.find("atom:published", ns)
                
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "Untitled Paper"
                summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""
                paper_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
                external_id = paper_url.split("/abs/")[-1] if "/abs/" in paper_url else paper_url

                author_elem = entry.find("atom:author/atom:name", ns)
                author = author_elem.text.strip() if author_elem is not None and author_elem.text else None

                published_at = datetime.now(timezone.utc)
                if published_elem is not None and published_elem.text:
                    try:
                        published_at = datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
                    except Exception:
                        pass

                items.append(
                    RawItem(
                        source_id=self.source_id,
                        external_id=external_id,
                        canonical_url=paper_url,
                        title=title,
                        author=author,
                        published_at=published_at,
                        source_type="paper",
                        reliability_tier=self.reliability_tier,
                        raw_content=summary,
                        metadata={"category": "research"},
                    )
                )
        except Exception as e:
            # ponytail: resilient failure returns empty list; network drops won't crash the bot
            pass

        return items
