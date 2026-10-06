"""Normalization service for ingested data."""

from sentinel.app.pipeline.deduplication import canonicalize_url

__all__ = ["canonicalize_url"]
