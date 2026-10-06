"""Admin maintenance and ingestion triggers."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.db.session import get_db
from sentinel.app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/admin", tags=["Admin"])
ingestion_service = IngestionService()


@router.post("/ingest")
async def trigger_admin_ingest(session: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    stats = await ingestion_service.ingest_and_process(session, limit=10)
    return {"status": "success", "stats": stats}


@router.get("/health")
async def admin_health_status() -> Dict[str, Any]:
    return {
        "status": "operational",
        "budget": 0.0,
        "mode": "free_tier_only",
    }
