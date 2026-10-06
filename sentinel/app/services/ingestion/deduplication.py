"""Deduplication and clustering service."""

from sentinel.app.pipeline.deduplication import compute_content_hash, title_similarity, cluster_items

__all__ = ["compute_content_hash", "title_similarity", "cluster_items"]
