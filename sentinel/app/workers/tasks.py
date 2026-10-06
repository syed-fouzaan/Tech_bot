"""Background job tasks: ingestion cycle, daily digest, and SRS reviews."""

import logging
from sentinel.app.db.session import async_session_maker
from sentinel.app.services.ingestion.service import IngestionService

logger = logging.getLogger("sentinel.workers")
ingestion_service = IngestionService()


async def run_scheduled_ingestion():
    """Executes periodic source ingestion and clustering."""
    logger.info("Executing scheduled ingestion cycle...")
    async with async_session_maker() as session:
        try:
            stats = await ingestion_service.ingest_and_process(session, limit=10)
            logger.info("Scheduled ingestion complete: %s", stats)
        except Exception as e:
            logger.error("Error during scheduled ingestion: %s", e)
