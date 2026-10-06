"""Claims extraction and management service."""

from typing import List, Dict, Any
from sentinel.app.models import ClaimModel, ItemModel


def build_claim(item: ItemModel, claim_type: str, text: str, confidence_label: str) -> ClaimModel:
    return ClaimModel(
        item_id=item.id,
        claim_type=claim_type,
        text=text,
        epistemic_label=confidence_label,
        evidence_url=item.canonical_url,
    )
