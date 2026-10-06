"""Ingestion Pipeline Runner: orchestrates sources, deduplication, scoring, and storage."""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.sources import (
    RawItem,
    ArxivSourceAdapter,
    HuggingFaceSourceAdapter,
    GitHubReleasesSourceAdapter,
    RSSSourceAdapter,
    HackerNewsSourceAdapter,
)
from sentinel.app.pipeline.deduplication import canonicalize_url, compute_content_hash, cluster_items
from sentinel.app.pipeline.scoring import score_item
from sentinel.app.pipeline.trust import evaluate_epistemic_level, detect_hype
from sentinel.app.models import ItemModel, ClaimModel


class IngestionPipeline:
    def __init__(self):
        self.adapters = [
            ArxivSourceAdapter(),
            HuggingFaceSourceAdapter(),
            GitHubReleasesSourceAdapter(),
            RSSSourceAdapter(),
            HackerNewsSourceAdapter(),
        ]

    async def run(self, session: AsyncSession, limit_per_source: int = 10) -> Dict[str, Any]:
        """
        Executes full ingestion pipeline funnel:
        1. Fetch raw items
        2. Canonicalize URLs and compute hashes
        3. Deduplicate and cluster
        4. Score importance and personal relevance
        5. Assign epistemic labels and hype flags
        6. Store new items idempotently
        """
        raw_items: List[RawItem] = []
        for adapter in self.adapters:
            try:
                items = await adapter.fetch(limit=limit_per_source)
                raw_items.extend(items)
            except Exception:
                continue

        scanned_count = len(raw_items)
        if not raw_items:
            return {"scanned": 0, "accepted": 0, "funnel": "Empty source fetch"}

        # Canonicalize and hash
        for item in raw_items:
            item.canonical_url = canonicalize_url(item.canonical_url)

        # Deduplicate & cluster
        clusters = cluster_items(raw_items, threshold=0.65)
        clustered_count = len(clusters)

        accepted_count = 0
        must_know_count = 0
        should_know_count = 0

        for cluster in clusters:
            primary = cluster[0]
            content_hash = compute_content_hash(primary.canonical_url, primary.title)

            # Check if already present in DB
            stmt = select(ItemModel).where(
                (ItemModel.source_id == primary.source_id) &
                (ItemModel.external_id == primary.external_id)
            )
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                continue

            importance, personal, priority, reasoning, action = score_item(primary)
            marker, confidence_label = evaluate_epistemic_level(primary)
            hype_flag, hype_reason = detect_hype(primary)

            if priority == "MUST_KNOW":
                must_know_count += 1
            elif priority == "SHOULD_KNOW":
                should_know_count += 1

            new_item = ItemModel(
                source_id=primary.source_id,
                external_id=primary.external_id,
                canonical_url=primary.canonical_url,
                title=primary.title,
                author=primary.author,
                published_at=primary.published_at,
                retrieved_at=datetime.now(timezone.utc),
                source_type=primary.source_type,
                reliability_tier=primary.reliability_tier,
                content_hash=content_hash,
                excerpt=primary.raw_content[:1500],
                category=primary.metadata.get("category", "general"),
                importance_score=importance,
                personal_relevance_score=personal,
                priority=priority,
                status="new",
                summary=primary.raw_content[:300] if primary.raw_content else primary.title,
                why_it_matters=reasoning,
                what_changed="Updated version/architecture released",
                practical_action=action,
                epistemic_marker=marker,
                hype_flag=hype_flag,
            )

            # Create claim
            claim = ClaimModel(
                item=new_item,
                claim_type="capability",
                text=primary.title,
                verification_level=2 if len(cluster) > 1 else (1 if primary.reliability_tier >= 9 else 0),
                epistemic_label=confidence_label,
                evidence_url=primary.canonical_url,
            )
            session.add(new_item)
            session.add(claim)
            accepted_count += 1

        await session.commit()

        funnel_stats = {
            "scanned": scanned_count,
            "clusters": clustered_count,
            "accepted": accepted_count,
            "must_know": must_know_count,
            "should_know": should_know_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return funnel_stats
