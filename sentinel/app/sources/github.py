"""GitHub releases adapter tracking key AI & Data Engineering repositories via Atom feeds."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import httpx
from typing import List
from sentinel.app.sources.base import RawItem

TRACKED_REPOS = [
    "vllm-project/vllm",
    "huggingface/transformers",
    "ollama/ollama",
    "langchain-ai/langgraph",
    "dbt-labs/dbt-core",
    "apache/airflow",
]


class GitHubReleasesSourceAdapter:
    source_id: str = "github"
    reliability_tier: int = 9  # Official release notes tier

    async def fetch(self, limit: int = 10) -> List[RawItem]:
        items: List[RawItem] = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            for repo in TRACKED_REPOS:
                atom_url = f"https://github.com/{repo}/releases.atom"
                try:
                    resp = await client.get(atom_url)
                    if resp.status_code != 200:
                        continue
                    root = ET.fromstring(resp.text)
                    
                    entries = root.findall("atom:entry", ns)[:2]  # top 2 per repo
                    for entry in entries:
                        id_elem = entry.find("atom:id", ns)
                        title_elem = entry.find("atom:title", ns)
                        content_elem = entry.find("atom:content", ns)
                        updated_elem = entry.find("atom:updated", ns)
                        link_elem = entry.find("atom:link", ns)

                        ext_id = id_elem.text.strip() if id_elem is not None and id_elem.text else f"{repo}-release"
                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else f"{repo} Release"
                        release_url = link_elem.attrib.get("href", f"https://github.com/{repo}/releases") if link_elem is not None else ""
                        content = content_elem.text.strip() if content_elem is not None and content_elem.text else ""

                        pub_at = datetime.now(timezone.utc)
                        if updated_elem is not None and updated_elem.text:
                            try:
                                pub_at = datetime.fromisoformat(updated_elem.text.replace("Z", "+00:00"))
                            except Exception:
                                pass

                        items.append(
                            RawItem(
                                source_id=self.source_id,
                                external_id=ext_id,
                                canonical_url=release_url,
                                title=f"GitHub: {repo} {title}",
                                author=repo.split("/")[0],
                                published_at=pub_at,
                                source_type="release",
                                reliability_tier=self.reliability_tier,
                                raw_content=content[:2000],
                                metadata={"repo": repo},
                            )
                        )
                except Exception:
                    continue

        return items[:limit]
