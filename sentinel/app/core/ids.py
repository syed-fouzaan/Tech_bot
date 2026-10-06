"""ID and content hash generation utilities."""

import hashlib
import uuid
import re


def generate_uuid() -> str:
    return str(uuid.uuid4())


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
