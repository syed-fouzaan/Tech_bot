"""URL canonicalization, hash calculation, and title clustering deduplication."""

import hashlib
import re
import urllib.parse
from typing import Set, Tuple, List, Dict
from sentinel.app.sources.base import RawItem

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "_ga", "feature",
}


def canonicalize_url(url: str) -> str:
    """Normalizes URL by stripping query tracking parameters, anchors, and standardizing host and path."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url)
        # Filter query params
        q_params = urllib.parse.parse_qsl(parsed.query)
        clean_q = [(k, v) for k, v in q_params if k.lower() not in TRACKING_PARAMS]
        new_query = urllib.parse.urlencode(clean_q)
        
        # Standardize path
        path = parsed.path.lower().rstrip("/") if parsed.path != "/" else "/"
        return urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            new_query,
            "",
        ))
    except Exception:
        return url.strip()


def compute_content_hash(canonical_url: str, title: str) -> str:
    """Computes SHA-256 fingerprint from canonical URL and normalized title."""
    clean_title = re.sub(r"\W+", " ", title.lower()).strip()
    data = f"{canonical_url}|{clean_title}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def title_similarity(t1: str, t2: str) -> float:
    """Calculates Jaccard token similarity with suffix normalization."""
    stop = {"with", "and", "the", "for", "from", "in", "on", "at"}

    def normalize(w: str) -> str:
        # strip inflection suffixes: ed, ing, es, s, d
        return re.sub(r"(?:ing|ed|es|d|s)$", "", w)

    words1 = {normalize(w) for w in re.findall(r"[a-zA-Z0-9]{3,}", t1.lower()) if w not in stop}
    words2 = {normalize(w) for w in re.findall(r"[a-zA-Z0-9]{3,}", t2.lower()) if w not in stop}
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


def cluster_items(items: List[RawItem], threshold: float = 0.65) -> List[List[RawItem]]:
    """
    Groups raw items covering the same story based on URL equivalence or high title similarity.
    Returns clusters where each cluster's first element is the highest reliability source.
    """
    clusters: List[List[RawItem]] = []

    for item in items:
        matched = False
        for cluster in clusters:
            primary = cluster[0]
            # Match if canonical URLs match or title similarity exceeds threshold
            if (item.canonical_url and item.canonical_url == primary.canonical_url) or \
               (title_similarity(item.title, primary.title) >= threshold):
                cluster.append(item)
                matched = True
                break
        if not matched:
            clusters.append([item])

    # Sort each cluster so the highest reliability tier is the primary item
    for cluster in clusters:
        cluster.sort(key=lambda x: x.reliability_tier, reverse=True)

    return clusters
