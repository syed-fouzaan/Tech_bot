"""Hugging Face Hub source adapter for trending models and model cards."""

from datetime import datetime, timezone
import httpx
from typing import List
from sentinel.app.sources.base import RawItem

HF_MODELS_API = "https://huggingface.co/api/models"


class HuggingFaceSourceAdapter:
    source_id: str = "hf_hub"
    reliability_tier: int = 10  # Model cards / direct weights tier

    async def fetch(self, limit: int = 10) -> List[RawItem]:
        params = {
            "sort": "likes",
            "direction": "-1",
            "limit": str(limit),
            "full": "false",
        }
        
        items: List[RawItem] = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(HF_MODELS_API, params=params)
                resp.raise_for_status()
                data = resp.json()

            for m in data:
                model_id = m.get("id", "")
                if not model_id:
                    continue
                url = f"https://huggingface.co/{model_id}"
                pipeline_tag = m.get("pipeline_tag", "unknown")
                likes = m.get("likes", 0)
                downloads = m.get("downloads", 0)

                items.append(
                    RawItem(
                        source_id=self.source_id,
                        external_id=model_id,
                        canonical_url=url,
                        title=f"HuggingFace Model: {model_id} ({pipeline_tag})",
                        author=model_id.split("/")[0] if "/" in model_id else "Community",
                        published_at=datetime.now(timezone.utc),
                        source_type="model",
                        reliability_tier=self.reliability_tier,
                        raw_content=f"Pipeline tag: {pipeline_tag}. Likes: {likes}. Downloads: {downloads}.",
                        metadata={"pipeline_tag": pipeline_tag, "likes": likes, "downloads": downloads},
                    )
                )
        except Exception:
            pass

        return items
