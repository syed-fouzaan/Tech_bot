"""Ingestion application service orchestrating fetch, normalization, deduplication, and persistence."""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.pipeline.ingestion import IngestionPipeline


class IngestionService:
    def __init__(self):
        self.pipeline = IngestionPipeline()

    async def ingest_and_process(self, session: AsyncSession, limit: int = 10) -> Dict[str, Any]:
        return await self.pipeline.run(session, limit_per_source=limit)
