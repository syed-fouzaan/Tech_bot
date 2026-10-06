from sentinel.app.services.ingestion.fetcher import MultiSourceFetcher
from sentinel.app.services.ingestion.normalization import canonicalize_url
from sentinel.app.services.ingestion.deduplication import compute_content_hash, title_similarity, cluster_items
from sentinel.app.services.ingestion.service import IngestionService

__all__ = [
    "MultiSourceFetcher",
    "canonicalize_url",
    "compute_content_hash",
    "title_similarity",
    "cluster_items",
    "IngestionService",
]
